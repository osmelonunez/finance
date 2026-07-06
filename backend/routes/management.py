from flask import Blueprint, render_template, request, redirect, url_for, session
import logging
import os
import base64
import smtplib
from urllib.parse import urlparse, quote_plus

import psycopg2
from psycopg2.errors import ForeignKeyViolation

from db import get_db, get_database_url, get_previous_database_url, set_database_url
from dashboard_cache import invalidate_dashboard_cache
from i18n import t
from email_service import notify_user_approved
from report_service import send_monthly_report, send_yearly_report


management_bp = Blueprint("management", __name__)
logger = logging.getLogger("finance.management")
DEMO_SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "demo_data_management.sql")


def _build_db_url_from_form(prefix: str = ""):
    host = (request.form.get(f"{prefix}db_host") or "").strip()
    port = (request.form.get(f"{prefix}db_port") or "").strip()
    db_name = (request.form.get(f"{prefix}db_name") or "").strip()
    db_user = (request.form.get(f"{prefix}db_user") or "").strip()
    db_password = request.form.get(f"{prefix}db_password") or ""
    if not host or not port or not db_name or not db_user:
        return ""
    return f"postgresql://{db_user}:{quote_plus(db_password)}@{host}:{port}/{db_name}"


def _db_form_defaults_from_url(db_url: str):
    parsed = urlparse(db_url or "")
    return {
        "db_host": parsed.hostname or "",
        "db_port": str(parsed.port or 5432),
        "db_name": (parsed.path or "").lstrip("/"),
        "db_user": parsed.username or "",
        "db_password": "",
    }


def _require_roles(*roles):
    if session.get("role") not in roles:
        return redirect(url_for("dashboard.dashboard"))
    return None


def _load_system_settings():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(value,0) FROM settings WHERE key='initial_saving'")
            row = cur.fetchone()
            initial_saving = row[0] if row else 0
            cur.execute("SELECT COALESCE(value,1) FROM settings WHERE key='records_years'")
            row = cur.fetchone()
            records_years = int(row[0]) if row else 1
    return initial_saving, records_years


def _load_users():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, is_active, is_admin, created_at, username, role FROM users ORDER BY created_at DESC")
            users = cur.fetchall()
    return users


def _flash_payload():
    return {
        "message": session.pop("management_msg", ""),
        "error": session.pop("management_err", ""),
    }


def _ensure_demo_functions(cur):
    with open(DEMO_SQL_PATH, "r", encoding="utf-8") as f:
        cur.execute(f.read())


def _smtp_cipher():
    key = (os.environ.get("SMTP_ENCRYPTION_KEY") or "").strip()
    if not key:
        raise RuntimeError("SMTP_ENCRYPTION_KEY is not configured.")
    app_env = (os.environ.get("APP_ENV") or "").strip().lower()
    strict = app_env == "production" or (os.environ.get("FINANCE_STRICT_SECRETS", "").strip().lower() in {"1", "true", "yes", "on"})
    if strict and key == "change-this-smtp-key":
        raise RuntimeError("SMTP_ENCRYPTION_KEY cannot use the default value in production.")
    try:
        from cryptography.fernet import Fernet
    except Exception as exc:
        raise RuntimeError(f"cryptography package is required: {exc}") from exc

    candidate = key.encode("utf-8")
    if len(candidate) != 44:
        candidate = base64.urlsafe_b64encode(candidate[:32].ljust(32, b"0"))
    return Fernet(candidate)


def _load_smtp_settings():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT host, port, username, password_encrypted, from_name, from_email, use_tls, enabled
                FROM smtp_settings
                WHERE id=1
                """
            )
            row = cur.fetchone()
            if not row:
                return {
                    "host": "",
                    "port": 587,
                    "username": "",
                    "password_encrypted": None,
                    "from_name": "",
                    "from_email": "",
                    "use_tls": True,
                    "enabled": False,
                }
            return {
                "host": row[0] or "",
                "port": int(row[1] or 587),
                "username": row[2] or "",
                "password_encrypted": row[3],
                "from_name": row[4] or "",
                "from_email": row[5] or "",
                "use_tls": bool(row[6]),
                "enabled": bool(row[7]),
            }


def _load_email_report_config():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version
                FROM email_report_config
                WHERE id=1
                """
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    """
                    INSERT INTO email_report_config (
                        id, monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version, updated_at
                    )
                    VALUES (1, TRUE, TRUE, 'v1', 'v1', NOW())
                    """
                )
                conn.commit()
                return {
                    "monthly_enabled": True,
                    "yearly_enabled": True,
                    "monthly_template_version": "v1",
                    "yearly_template_version": "v1",
                }
            return {
                "monthly_enabled": bool(row[0]),
                "yearly_enabled": bool(row[1]),
                "monthly_template_version": "v1" if (row[2] or "v1") != "v1" else "v1",
                "yearly_template_version": "v1" if (row[3] or "v1") != "v1" else "v1",
            }


def _decrypt_smtp_password(enc_value):
    if not enc_value:
        return ""
    return _smtp_cipher().decrypt(enc_value.encode("utf-8")).decode("utf-8")


def _encrypt_smtp_password(raw_value):
    if not raw_value:
        return None
    return _smtp_cipher().encrypt(raw_value.encode("utf-8")).decode("utf-8")

def _load_payment_methods():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT pm.id, pm.name, pm.kind, pm.bank_name, pm.account_ref, pm.is_active,
                       pm.bank_id, COALESCE(b.name, pm.bank_name) AS bank_display
                FROM payment_methods pm
                LEFT JOIN banks b ON pm.bank_id = b.id
                ORDER BY pm.name ASC
                """
            )
            return cur.fetchall()


def _load_banks(include_inactive=False):
    with get_db() as conn:
        with conn.cursor() as cur:
            where = "" if include_inactive else "WHERE is_active=TRUE"
            cur.execute(
                f"""
                SELECT id, name, is_active
                FROM banks
                {where}
                ORDER BY name ASC
                """
            )
            return cur.fetchall()


@management_bp.route("/management")
def management():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    initial_saving, records_years = _load_system_settings()
    return render_template(
        "management_hub.html",
        initial_saving=initial_saving,
        records_years=records_years,
        is_admin=(session.get("role") == "admin"),
        **_flash_payload(),
        current_page="management"
    )


@management_bp.route("/management/users")
def management_users():
    denied = _require_roles("admin")
    if denied:
        return denied
    return render_template(
        "management_users.html",
        users=_load_users(),
        **_flash_payload(),
        current_page="management",
        management_section="users",
    )


@management_bp.route("/management/database")
def management_database():
    denied = _require_roles("admin")
    if denied:
        return denied
    current_db_form = _db_form_defaults_from_url(get_database_url())
    tested_db_form = session.get("db_conn_form", {})
    db_form = {**current_db_form, **tested_db_form}
    return render_template(
        "management_database.html",
        db_form=db_form,
        using_env_database_url=bool(os.environ.get("DATABASE_URL", "").strip()),
        has_previous_database_url=bool(get_previous_database_url()),
        **_flash_payload(),
        current_page="management",
        management_section="database",
    )


@management_bp.route("/management/smtp")
def management_smtp():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    smtp = _load_smtp_settings()
    report_cfg = _load_email_report_config()
    return render_template(
        "management_smtp.html",
        smtp=smtp,
        report_cfg=report_cfg,
        has_password=bool(smtp["password_encrypted"]),
        is_admin=(session.get("role") == "admin"),
        **_flash_payload(),
        current_page="management",
        management_section="smtp",
    )


@management_bp.route("/management/smtp/save", methods=["POST"])
def save_smtp():
    denied = _require_roles("admin")
    if denied:
        return denied

    current = _load_smtp_settings()
    host = (request.form.get("smtp_host") or "").strip()
    username = (request.form.get("smtp_user") or "").strip()
    from_name = (request.form.get("smtp_from_name") or "").strip()
    from_email = (request.form.get("smtp_from") or "").strip()
    raw_password = request.form.get("smtp_password") or ""
    enabled = (request.form.get("smtp_enabled") == "1")
    use_tls = (request.form.get("smtp_use_tls") == "1")
    try:
        port = int((request.form.get("smtp_port") or "587").strip())
    except ValueError:
        port = 587
    port = min(max(port, 1), 65535)

    if enabled and (not host or not username or not from_email):
        session["management_err"] = t("SMTP host, user and from email are required when enabled.")
        return redirect(url_for("management.management_smtp"))

    try:
        if raw_password.strip():
            encrypted = _encrypt_smtp_password(raw_password.strip())
        else:
            encrypted = current["password_encrypted"]
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO smtp_settings (id, host, port, username, password_encrypted, from_name, from_email, use_tls, enabled, updated_at)
                    VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        host=EXCLUDED.host,
                        port=EXCLUDED.port,
                        username=EXCLUDED.username,
                        password_encrypted=EXCLUDED.password_encrypted,
                        from_name=EXCLUDED.from_name,
                        from_email=EXCLUDED.from_email,
                        use_tls=EXCLUDED.use_tls,
                        enabled=EXCLUDED.enabled,
                        updated_at=NOW()
                    """,
                    (host, port, username, encrypted, from_name or None, from_email, use_tls, enabled),
                )
                conn.commit()
        session["management_msg"] = t("SMTP settings saved.")
    except Exception as exc:
        logger.warning("smtp_save_failed user=%s error=%s", session.get("user_name"), exc)
        session["management_err"] = t("SMTP save failed")

    return redirect(url_for("management.management_smtp"))


@management_bp.route("/management/smtp/test", methods=["POST"])
def test_smtp():
    denied = _require_roles("admin")
    if denied:
        return denied

    current = _load_smtp_settings()
    host = (request.form.get("smtp_host") or "").strip()
    username = (request.form.get("smtp_user") or "").strip()
    from_email = (request.form.get("smtp_from") or "").strip()
    test_to = (request.form.get("smtp_test_to") or "").strip() or (session.get("user_email") or "")
    raw_password = request.form.get("smtp_password") or ""
    use_tls = (request.form.get("smtp_use_tls") == "1")
    try:
        port = int((request.form.get("smtp_port") or "587").strip())
    except ValueError:
        port = 587
    port = min(max(port, 1), 65535)

    if not host or not username or not from_email or not test_to:
        session["management_err"] = t("SMTP host, user, from and test email are required.")
        return redirect(url_for("management.management_smtp"))

    try:
        smtp_password = raw_password.strip() or _decrypt_smtp_password(current["password_encrypted"])
        if not smtp_password:
            session["management_err"] = t("SMTP password is required for test.")
            return redirect(url_for("management.management_smtp"))

        with smtplib.SMTP(host, port, timeout=15) as server:
            if use_tls:
                server.starttls()
            server.login(username, smtp_password)
            body = "Subject: Finance SMTP test\n\nSMTP test message from Finance."
            server.sendmail(from_email, [test_to], body)

        session["management_msg"] = t("SMTP test email sent.")
    except Exception as exc:
        logger.warning("smtp_test_failed user=%s error=%s", session.get("user_name"), exc)
        session["management_err"] = t("SMTP test failed")

    return redirect(url_for("management.management_smtp"))


@management_bp.route("/management/email-reports/save", methods=["POST"])
def save_email_reports():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    monthly_enabled = (request.form.get("monthly_enabled") == "1")
    yearly_enabled = (request.form.get("yearly_enabled") == "1")
    monthly_template_version = (request.form.get("monthly_template_version") or "v1").strip().lower()
    yearly_template_version = (request.form.get("yearly_template_version") or "v1").strip().lower()
    if monthly_template_version != "v1":
        monthly_template_version = "v1"
    if yearly_template_version != "v1":
        yearly_template_version = "v1"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO email_report_config (
                    id, monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version, updated_at
                )
                VALUES (1, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    monthly_enabled=EXCLUDED.monthly_enabled,
                    yearly_enabled=EXCLUDED.yearly_enabled,
                    monthly_template_version=EXCLUDED.monthly_template_version,
                    yearly_template_version=EXCLUDED.yearly_template_version,
                    updated_at=NOW()
                """,
                (monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version),
            )
            conn.commit()
    session["management_msg"] = t("Email report settings saved.")
    return redirect(url_for("management.management_smtp"))


@management_bp.route("/management/email-reports/test-monthly", methods=["POST"])
def test_monthly_report():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    recipient = (session.get("user_email") or "").strip()
    ok, msg = send_monthly_report(test=True, recipients_override=[recipient] if recipient else [])
    session["management_msg" if ok else "management_err"] = (
        t("Monthly report test sent.") if ok else f"{t('Monthly report test failed')}: {msg}"
    )
    return redirect(url_for("management.management_smtp"))


@management_bp.route("/management/email-reports/test-yearly", methods=["POST"])
def test_yearly_report():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    recipient = (session.get("user_email") or "").strip()
    ok, msg = send_yearly_report(test=True, recipients_override=[recipient] if recipient else [])
    session["management_msg" if ok else "management_err"] = (
        t("Yearly report test sent.") if ok else f"{t('Yearly report test failed')}: {msg}"
    )
    return redirect(url_for("management.management_smtp"))


@management_bp.route("/management/system")
def management_system():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    initial_saving, records_years = _load_system_settings()
    return render_template(
        "management_system.html",
        initial_saving=initial_saving,
        records_years=records_years,
        is_admin=(session.get("role") == "admin"),
        **_flash_payload(),
        current_page="management",
        management_section="system",
    )

@management_bp.route("/management/payment-methods")
def management_payment_methods():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    return render_template(
        "management_payment_methods.html",
        payment_methods=_load_payment_methods(),
        banks=_load_banks(include_inactive=True),
        is_admin=(session.get("role") == "admin"),
        **_flash_payload(),
        current_page="management",
        management_section="payment_methods",
    )


@management_bp.route("/management/payment-methods/add", methods=["POST"])
def add_payment_method():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name = (request.form.get("name") or "").strip()
    kind = (request.form.get("kind") or "card").strip()
    bank_id = _parse_int_or_none(request.form.get("bank_id"))
    account_ref = (request.form.get("account_ref") or "").strip()
    is_active = (request.form.get("is_active") or "1") == "1"
    if kind not in {"card", "bank_account"}:
        kind = "card"
    if not name:
        session["management_err"] = t("Name is required.")
        return redirect(url_for("management.management_payment_methods"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO payment_methods (name, kind, bank_id, bank_name, account_ref, is_active, updated_at)
                    VALUES (%s, %s, %s, (SELECT name FROM banks WHERE id=%s), %s, %s, NOW())
                    """,
                    (name, kind, bank_id, bank_id, account_ref or None, is_active),
                )
                conn.commit()
        session["management_msg"] = t("Payment method created.")
    except Exception:
        session["management_err"] = t("Name already exists.")
    return redirect(url_for("management.management_payment_methods"))


@management_bp.route("/management/payment-methods/<int:method_id>/update", methods=["POST"])
def update_payment_method(method_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name = (request.form.get("name") or "").strip()
    kind = (request.form.get("kind") or "card").strip()
    bank_id = _parse_int_or_none(request.form.get("bank_id"))
    account_ref = (request.form.get("account_ref") or "").strip()
    is_active = (request.form.get("is_active") or "0") == "1"
    if kind not in {"card", "bank_account"}:
        kind = "card"
    if not name:
        session["management_err"] = t("Name is required.")
        return redirect(url_for("management.management_payment_methods"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE payment_methods
                    SET name=%s,
                        kind=%s,
                        bank_id=%s,
                        bank_name=(SELECT name FROM banks WHERE id=%s),
                        account_ref=%s,
                        is_active=%s,
                        updated_at=NOW()
                    WHERE id=%s
                    """,
                    (name, kind, bank_id, bank_id, account_ref or None, is_active, method_id),
                )
                conn.commit()
        session["management_msg"] = t("Payment method updated.")
    except Exception:
        session["management_err"] = t("Name already exists.")
    return redirect(url_for("management.management_payment_methods"))


def _parse_int_or_none(raw_value):
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None


@management_bp.route("/management/banks/add", methods=["POST"])
def add_bank():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name = (request.form.get("name") or "").strip()
    is_active = (request.form.get("is_active") or "1") == "1"
    if not name:
        session["management_err"] = t("Bank name is required.")
        return redirect(url_for("management.management_payment_methods"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO banks (name, is_active, updated_at)
                    VALUES (%s, %s, NOW())
                    """,
                    (name, is_active),
                )
                conn.commit()
        session["management_msg"] = t("Bank created.")
    except Exception:
        session["management_err"] = t("Bank already exists.")
    return redirect(url_for("management.management_payment_methods"))


@management_bp.route("/management/banks/<int:bank_id>/update", methods=["POST"])
def update_bank(bank_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name = (request.form.get("name") or "").strip()
    is_active = (request.form.get("is_active") or "0") == "1"
    if not name:
        session["management_err"] = t("Bank name is required.")
        return redirect(url_for("management.management_payment_methods"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE banks
                    SET name=%s, is_active=%s, updated_at=NOW()
                    WHERE id=%s
                    """,
                    (name, is_active, bank_id),
                )
                cur.execute(
                    """
                    UPDATE payment_methods
                    SET bank_name=%s, updated_at=NOW()
                    WHERE bank_id=%s
                    """,
                    (name, bank_id),
                )
                cur.execute(
                    """
                    UPDATE loans
                    SET bank_name=%s, updated_at=NOW()
                    WHERE bank_id=%s
                    """,
                    (name, bank_id),
                )
                conn.commit()
        session["management_msg"] = t("Bank updated.")
    except Exception:
        session["management_err"] = t("Bank already exists.")
    return redirect(url_for("management.management_payment_methods"))


@management_bp.route("/management/payment-methods/<int:method_id>/delete", methods=["POST"])
def delete_payment_method(method_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM payment_methods WHERE id=%s", (method_id,))
                conn.commit()
        session["management_msg"] = t("Payment method deleted.")
    except ForeignKeyViolation:
        session["management_err"] = t("Cannot delete payment method. It is used by expenses.")
    return redirect(url_for("management.management_payment_methods"))


@management_bp.route("/management/initial-saving", methods=["POST"])
def update_initial_saving():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    raw = (request.form.get("initial_saving") or "0").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 0

    if value < 0:
        value = 0

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO settings (key, value)
                VALUES ('initial_saving', %s)
                ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
            """, (value,))
            conn.commit()
    invalidate_dashboard_cache()

    session["management_msg"] = t("Initial saving updated")
    return redirect(url_for("management.management_system"))


@management_bp.route("/management/records-years", methods=["POST"])
def update_records_years():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    raw = (request.form.get("records_years") or "1").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 1

    if value < 1:
        value = 1
    if value > 10:
        value = 10

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO settings (key, value)
                VALUES ('records_years', %s)
                ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
                """,
                (value,),
            )
            conn.commit()

    session["management_msg"] = t("Records years window updated")
    return redirect(url_for("management.management_system"))


@management_bp.route("/management/db-connection/test", methods=["POST"])
def test_db_connection():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if os.environ.get("DATABASE_URL", "").strip():
        session["management_err"] = t("DATABASE_URL env is active. Update it there to change DB connection.")
        return redirect(url_for("management.management_database"))

    db_url = _build_db_url_from_form()
    form_values = {
        "db_host": (request.form.get("db_host") or "").strip(),
        "db_port": (request.form.get("db_port") or "").strip(),
        "db_name": (request.form.get("db_name") or "").strip(),
        "db_user": (request.form.get("db_user") or "").strip(),
        "db_password": request.form.get("db_password") or "",
    }
    session["db_conn_form"] = form_values

    if not db_url:
        session["management_err"] = t("Database host, port, name and user are required.")
        return redirect(url_for("management.management_database"))

    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), COALESCE(inet_server_addr()::text, '')")
                row = cur.fetchone()
        db_name = row[0] if row else "unknown"
        db_ip = row[1] if row and row[1] else "unknown"
        session["db_conn_tested_url"] = db_url
        logger.info("db_connection_test_ok user=%s db=%s ip=%s", session.get("user_name"), db_name, db_ip)
        session["management_msg"] = f"{t('Connection test OK')} (db={db_name}, ip={db_ip})."
    except Exception as exc:
        session.pop("db_conn_tested_url", None)
        logger.warning("db_connection_test_fail user=%s error=%s", session.get("user_name"), exc)
        session["management_err"] = t("Connection test failed")
    return redirect(url_for("management.management_database"))


@management_bp.route("/management/db-connection/save", methods=["POST"])
def save_db_connection():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if os.environ.get("DATABASE_URL", "").strip():
        session["management_err"] = t("DATABASE_URL env is active. Update it there to change DB connection.")
        return redirect(url_for("management.management_database"))

    db_url = _build_db_url_from_form()
    tested_url = session.get("db_conn_tested_url", "")

    if not db_url:
        session["management_err"] = t("Database host, port, name and user are required.")
        return redirect(url_for("management.management_database"))
    if not tested_url or tested_url != db_url:
        session["management_err"] = t("Run a successful test for this exact connection before saving.")
        return redirect(url_for("management.management_database"))

    previous = get_database_url()
    set_database_url(db_url, previous_database_url=previous)
    session.pop("db_conn_tested_url", None)
    session.pop("db_conn_form", None)
    logger.info("db_connection_save user=%s", session.get("user_name"))
    session["management_msg"] = t("Database connection updated.")
    return redirect(url_for("management.management_database"))


@management_bp.route("/management/db-connection/rollback", methods=["POST"])
def rollback_db_connection():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if os.environ.get("DATABASE_URL", "").strip():
        session["management_err"] = t("DATABASE_URL env is active. Update it there to change DB connection.")
        return redirect(url_for("management.management_database"))

    previous = get_previous_database_url()
    if not previous:
        session["management_err"] = t("No previous database connection available.")
        return redirect(url_for("management.management_database"))

    try:
        with psycopg2.connect(previous) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        current = get_database_url()
        set_database_url(previous, previous_database_url=current)
        session.pop("db_conn_tested_url", None)
        session.pop("db_conn_form", None)
        logger.info("db_connection_rollback user=%s", session.get("user_name"))
        session["management_msg"] = t("Database connection rollback applied.")
    except Exception as exc:
        logger.warning("db_connection_rollback_fail user=%s error=%s", session.get("user_name"), exc)
        session["management_err"] = t("Rollback failed")
    return redirect(url_for("management.management_database"))


@management_bp.route("/management/reset-db", methods=["POST"])
def reset_db():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM records")
            deleted = cur.rowcount
            conn.commit()
    invalidate_dashboard_cache()
    logger.info("reset_db user=%s deleted=%s", session.get("user_name"), deleted)
    session["management_msg"] = f"{t('Database reset')}: {deleted} {t('records deleted')}"

    return redirect(url_for("management.management_system"))


@management_bp.route("/management/demo-data/seed", methods=["POST"])
def seed_demo_data():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))

    with get_db() as conn:
        with conn.cursor() as cur:
            _ensure_demo_functions(cur)
            cur.execute("SELECT management_seed_demo_data()")
            inserted = cur.fetchone()[0]
            conn.commit()
    invalidate_dashboard_cache()
    logger.info("demo_data_seed user=%s inserted=%s initial_saving=300", session.get("user_name"), inserted)
    session["management_msg"] = f"{t('Demo data inserted')}: {inserted} {t('records')}"

    return redirect(url_for("management.management_system"))


@management_bp.route("/management/demo-data/clear", methods=["POST"])
def clear_demo_data():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))

    with get_db() as conn:
        with conn.cursor() as cur:
            _ensure_demo_functions(cur)
            cur.execute("SELECT management_clear_demo_data()")
            deleted = cur.fetchone()[0]
            conn.commit()
    invalidate_dashboard_cache()
    logger.info("demo_data_clear user=%s deleted=%s initial_saving_removed=true", session.get("user_name"), deleted)
    session["management_msg"] = f"{t('Demo data deleted')}: {deleted} {t('records')}"

    return redirect(url_for("management.management_system"))


@management_bp.route("/management/users/<int:user_id>/toggle", methods=["POST"])
def toggle_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if session.get("user_id") == user_id:
        return redirect(url_for("management.management_users"))

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT is_active, role, email, username FROM users WHERE id=%s", (user_id,))
            row = cur.fetchone()
            if row:
                is_active = row[0]
                role = row[1]
                target_email = row[2]
                target_username = row[3] or target_email
                # Prevent deactivating the last active admin.
                if is_active and role == "admin":
                    cur.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=TRUE")
                    active_admins = cur.fetchone()[0]
                    if active_admins <= 1:
                        session["management_err"] = t("At least one active admin must remain")
                        return redirect(url_for("management.management_users"))
                cur.execute(
                    "UPDATE users SET is_active=%s WHERE id=%s",
                    (not is_active, user_id)
                )
                conn.commit()
                session["management_msg"] = t("User status updated")
                if (not is_active):
                    notify_user_approved(target_username, target_email)
                    logger.info("user_approved_notification user_id=%s email=%s", user_id, target_email)

    return redirect(url_for("management.management_users"))


@management_bp.route("/management/users/<int:user_id>/role", methods=["POST"])
def update_role(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))

    role = (request.form.get("role") or "user").strip().lower()
    if role not in {"user", "admin", "editor"}:
        role = "user"
    desired_is_admin = role == "admin"
    current_user_id = session.get("user_id")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT is_admin, role FROM users WHERE id=%s", (user_id,))
            row = cur.fetchone()
            if not row:
                session["management_err"] = t("User not found")
                return redirect(url_for("management.management_users"))

            # Prevent self-demotion to avoid lockout.
            if current_user_id == user_id and not desired_is_admin:
                session["management_err"] = t("You cannot remove your own admin role")
                return redirect(url_for("management.management_users"))

            if not desired_is_admin:
                # Ensure at least one admin remains.
                cur.execute("SELECT COUNT(*) FROM users WHERE is_admin=TRUE")
                admin_count = cur.fetchone()[0]
                if admin_count <= 1 and row[0]:
                    session["management_err"] = t("At least one admin must remain active")
                    return redirect(url_for("management.management_users"))

            cur.execute("UPDATE users SET is_admin=%s, role=%s WHERE id=%s", (desired_is_admin, role, user_id))
            conn.commit()
            session["management_msg"] = t("User role updated")

    return redirect(url_for("management.management_users"))
