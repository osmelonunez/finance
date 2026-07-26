from datetime import datetime

import pytest

import email_service
import report_service


pytestmark = [pytest.mark.integration]


class _FakeSMTP:
    instances = []
    fail = False

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.tls = False
        self.login_args = None
        self.message = None
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def starttls(self):
        self.tls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        if self.fail:
            raise RuntimeError("smtp unavailable")
        self.message = message


def _smtp_config(use_tls=True):
    return {
        "host": "smtp.example.test",
        "port": 587,
        "username": "finance",
        "password": "secret",
        "from_name": "Finance",
        "from_email": "finance@example.test",
        "use_tls": use_tls,
    }


def test_send_email_builds_html_message_and_handles_failures(monkeypatch):
    _FakeSMTP.instances.clear()
    _FakeSMTP.fail = False
    monkeypatch.setattr(email_service, "_load_enabled_smtp", lambda: _smtp_config())
    monkeypatch.setattr(email_service.smtplib, "SMTP", _FakeSMTP)

    assert email_service.send_email(
        "user@example.test", "Subject", "Plain body", "<b>HTML body</b>"
    )
    smtp = _FakeSMTP.instances[-1]
    assert smtp.tls is True
    assert smtp.login_args == ("finance", "secret")
    assert smtp.message["To"] == "user@example.test"
    assert smtp.message.is_multipart()

    _FakeSMTP.fail = True
    assert not email_service.send_email(["user@example.test"], "Subject", "Body")
    monkeypatch.setattr(email_service, "_load_enabled_smtp", lambda: None)
    assert not email_service.send_email(["user@example.test"], "Subject", "Body")
    monkeypatch.setattr(email_service, "_load_enabled_smtp", lambda: _smtp_config(False))
    assert not email_service.send_email([], "Subject", "Body")


def test_smtp_cipher_encrypts_and_decrypts(monkeypatch):
    monkeypatch.setenv("SMTP_ENCRYPTION_KEY", "test-key")
    cipher = email_service._smtp_cipher()
    token = cipher.encrypt(b"password")
    assert cipher.decrypt(token) == b"password"
    monkeypatch.delenv("SMTP_ENCRYPTION_KEY")
    assert email_service._smtp_cipher() is None


def test_user_notification_helpers_respect_available_recipients(monkeypatch, db_query):
    calls = []
    monkeypatch.setattr(
        email_service,
        "send_email",
        lambda recipients, subject, body, **_kwargs: calls.append(
            (recipients, subject, body)
        )
        or True,
    )

    assert email_service.notify_admins_pending_user("new_user", "new@example.test")
    assert calls[-1][0] == ["admin@example.test"]
    assert "new_user" in calls[-1][2]
    assert email_service.notify_user_approved("editor_test", "EDITOR@example.test")
    assert calls[-1][0] == "editor@example.test"

    db_query(
        "UPDATE users SET email_notifications=FALSE WHERE role='admin'",
        fetch="none",
    )
    assert not email_service.notify_admins_pending_user("nobody", "none@example.test")
    assert not email_service.notify_user_approved("missing", "missing@example.test")


def test_monthly_report_groups_languages_and_records_failed_delivery(
    monkeypatch, db_query
):
    sent = []
    monkeypatch.setenv("APP_PUBLIC_URL", "https://devfinance.home")
    monkeypatch.setattr(
        report_service,
        "send_email",
        lambda recipients, subject, body, html_body=None: sent.append(
            (recipients, subject, body, html_body)
        )
        or (len(sent) == 1),
    )

    ok, message = report_service.send_monthly_report(
        test=True,
        recipients_override=[
            "admin@example.test",
            "ADMIN@example.test",
            "outside@example.test",
        ],
    )

    assert not ok
    assert message == "send failed"
    assert len(sent) == 2
    assert any("Balance mensual" in item[1] for item in sent)
    assert any("Finance monthly balance" in item[1] for item in sent)
    assert all("https://devfinance.home" in item[2] for item in sent)
    assert all("data-finance-branding" in item[3] for item in sent)
    assert db_query(
        """
        SELECT status, message FROM email_report_runs
        WHERE report_type='test_monthly'
        ORDER BY id DESC LIMIT 1
        """
    ) == ("failed", "send failed")


def test_report_no_recipient_already_sent_and_scheduler_branches(
    monkeypatch, db_query
):
    assert report_service.send_yearly_report(
        test=True, recipients_override=[""]
    ) == (False, "No test recipient")

    db_query(
        """
        INSERT INTO email_report_runs (report_type, period_key, status, message)
        VALUES ('monthly', '2026-06', 'success', 'fixture')
        """,
        fetch="none",
    )
    assert report_service.send_monthly_report(test=False) == (True, "already_sent")

    calls = []
    monkeypatch.setattr(
        report_service,
        "send_monthly_report",
        lambda test=False: calls.append(("monthly", test)) or (True, "sent"),
    )
    monkeypatch.setattr(
        report_service,
        "send_yearly_report",
        lambda test=False: calls.append(("yearly", test)) or (True, "sent"),
    )

    class _JanuaryFirst:
        @classmethod
        def now(cls):
            return datetime(2026, 1, 1, 0, 1)

    monkeypatch.setattr(report_service, "datetime", _JanuaryFirst)
    report_service.maybe_run_scheduled_reports()
    assert calls == [("monthly", False), ("yearly", False)]

    class _NotFirstDay:
        @classmethod
        def now(cls):
            return datetime(2026, 1, 2, 0, 1)

    monkeypatch.setattr(report_service, "datetime", _NotFirstDay)
    report_service.maybe_run_scheduled_reports()
    assert len(calls) == 2

