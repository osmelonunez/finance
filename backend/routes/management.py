from flask import Blueprint, render_template, request, redirect, url_for, session
import logging
import os
import base64
import smtplib
from urllib.parse import urlparse, quote_plus

import psycopg2
from db import get_db, get_database_url, get_previous_database_url, set_database_url
from dashboard_cache import invalidate_dashboard_cache
from i18n import format_number, t
from email_service import notify_user_approved
from report_service import send_monthly_report, send_yearly_report
from validators import (
    MAX_BANK_NAME_LENGTH,
    MAX_PAYMENT_METHOD_NAME_LENGTH,
    validate_text_length,
)


management_bp = Blueprint("management", __name__)
logger = logging.getLogger("finance.management")
DEMO_SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "demo_data_management.sql")
DEMO_TAG = "[DEMO_SEED_MANAGEMENT]"
DEMO_BANK_NAMES = ("ING", "Santander", "CaixaBank", "BBVA")
DEMO_PAYMENT_METHOD_NAMES = (
    "Demo - ING Card - Person 1",
    "Demo - ING Card - Person 2",
    "Demo - ING Shared Card 1",
    "Demo - ING Shared Card 2",
    "Demo - ING Account - Person 1",
    "Demo - ING Account - Person 2",
    "Demo - ING Shared Account",
    "Demo - Shared Card",
    "Demo - Santander Account",
    "Demo - BBVA Card",
    "Demo - BBVA Account",
)


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


def _demo_data_counts(cur):
    cur.execute("SELECT COUNT(*) FROM banks WHERE name = ANY(%s)", (list(DEMO_BANK_NAMES),))
    banks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM payment_methods WHERE name = ANY(%s)", (list(DEMO_PAYMENT_METHOD_NAMES),))
    payment_methods = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM loans WHERE description LIKE %s", (f"{DEMO_TAG}%",))
    loans = cur.fetchone()[0]
    cur.execute(
        """
        SELECT
            COUNT(*) FILTER (WHERE is_loan_payment = TRUE),
            COUNT(*) FILTER (WHERE COALESCE(is_loan_payment, FALSE) = FALSE),
            COUNT(*) FILTER (WHERE type = 'income'),
            COUNT(*) FILTER (WHERE type = 'expense'),
            COUNT(*) FILTER (WHERE type = 'saving')
        FROM records
        WHERE comment = %s
        """,
        (DEMO_TAG,),
    )
    loan_payments, regular_records, incomes, expenses, savings = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM loan_usages WHERE comment LIKE %s", (f"{DEMO_TAG}%",))
    loan_usages = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM settings WHERE key='initial_saving'")
    initial_saving = cur.fetchone()[0]
    return {
        "banks": banks,
        "payment_methods": payment_methods,
        "loans": loans,
        "regular_records": regular_records,
        "loan_payments": loan_payments,
        "loan_usages": loan_usages,
        "incomes": incomes,
        "expenses": expenses,
        "savings": savings,
        "initial_saving": initial_saving,
    }


def _log_demo_data_actions(action, counts, total=None):
    for entity, count in counts.items():
        logger.info("[DEMO DATA] action=%s entity=%s count=%s", action, entity, count)
    if total is not None:
        logger.info("[DEMO DATA] action=%s entity=total count=%s", action, total)


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
                       pm.bank_id, COALESCE(b.name, pm.bank_name) AS bank_display,
                       pm.parent_account_id, parent.name AS parent_account_name
                FROM payment_methods pm
                LEFT JOIN banks b ON pm.bank_id = b.id
                LEFT JOIN payment_methods parent ON parent.id=pm.parent_account_id
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


def _load_bank_summaries(selected_year):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH method_totals AS (
                    SELECT
                        pm.bank_id,
                        COUNT(*) FILTER (WHERE pm.kind='bank_account') AS account_count,
                        COUNT(*) FILTER (WHERE pm.kind='card') AS card_count,
                        COUNT(*) FILTER (WHERE pm.is_active=TRUE) AS active_method_count
                    FROM payment_methods pm
                    GROUP BY pm.bank_id
                ),
                method_spending AS (
                    SELECT
                        pm.bank_id,
                        COALESCE(SUM(r.amount), 0) AS total_spent,
                        COALESCE(SUM(r.amount) FILTER (WHERE r.date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0) AS month_spent,
                        COALESCE(SUM(r.amount) FILTER (WHERE LEFT(r.date, 4)=%s), 0) AS year_spent
                    FROM payment_methods pm
                    JOIN records r ON r.payment_method_id=pm.id
                        AND r.type='expense'
                        AND COALESCE(r.is_loan_payment, FALSE)=FALSE
                    GROUP BY pm.bank_id
                ),
                loan_payment_spending AS (
                    SELECT
                        l.bank_id,
                        COALESCE(SUM(r.amount), 0) AS total_spent,
                        COALESCE(SUM(r.amount) FILTER (WHERE r.date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0) AS month_spent,
                        COALESCE(SUM(r.amount) FILTER (WHERE LEFT(r.date, 4)=%s), 0) AS year_spent
                    FROM loans l
                    JOIN records r ON r.loan_id=l.id
                        AND r.type='expense'
                        AND r.is_loan_payment=TRUE
                    WHERE l.bank_id IS NOT NULL
                    GROUP BY l.bank_id
                )
                SELECT
                    b.id,
                    b.name,
                    b.is_active,
                    COALESCE(mt.account_count, 0),
                    COALESCE(mt.card_count, 0),
                    COALESCE(mt.active_method_count, 0),
                    COALESCE(ms.total_spent, 0) + COALESCE(lps.total_spent, 0) AS total_spent,
                    COALESCE(ms.month_spent, 0) + COALESCE(lps.month_spent, 0) AS month_spent,
                    COALESCE(ms.year_spent, 0) + COALESCE(lps.year_spent, 0) AS year_spent
                FROM banks b
                LEFT JOIN method_totals mt ON mt.bank_id=b.id
                LEFT JOIN method_spending ms ON ms.bank_id=b.id
                LEFT JOIN loan_payment_spending lps ON lps.bank_id=b.id
                ORDER BY b.name
                """,
                (str(selected_year), str(selected_year)),
            )
            return cur.fetchall()


def _load_payment_method_summaries(selected_year):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    pm.id,
                    pm.name,
                    pm.kind,
                    COALESCE(SUM(r.amount), 0) AS total_spent,
                    COALESCE(SUM(r.amount) FILTER (WHERE r.date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0) AS month_spent,
                    COALESCE(SUM(r.amount) FILTER (WHERE LEFT(r.date, 4)=%s), 0) AS year_spent
                FROM payment_methods pm
                LEFT JOIN records r ON r.payment_method_id=pm.id AND r.type='expense'
                GROUP BY pm.id
                ORDER BY pm.name
                """,
                (str(selected_year),),
            )
            return cur.fetchall()


def _load_expense_years():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT year_value
                FROM (
                    SELECT DISTINCT LEFT(date, 4) AS year_value
                    FROM records
                    WHERE type='expense' AND date ~ '^[0-9]{4}-[0-9]{2}$'
                    UNION
                    SELECT TO_CHAR(CURRENT_DATE, 'YYYY')
                ) years
                WHERE year_value <= TO_CHAR(CURRENT_DATE, 'YYYY')
                ORDER BY year_value DESC
                """
            )
            return [row[0] for row in cur.fetchall()]


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

@management_bp.route("/payment-methods")
def management_payment_methods():
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    return redirect(url_for("management.payment_methods_section", section="kpi"))


@management_bp.route("/payment-methods/<section>")
def payment_methods_section(section):
    if section == "summary":
        return redirect(url_for("management.payment_methods_section", section="kpi"))
    if section == "dependencies":
        return redirect(url_for("management.payment_methods_section", section="relationships"))
    if section not in {"kpi", "relationships", "banks", "accounts", "cards"}:
        return redirect(url_for("management.management_payment_methods"))
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    available_years = _load_expense_years()
    requested_year = (request.args.get("year") or "").strip()
    selected_year = requested_year if requested_year in available_years else available_years[0]
    requested_scope = (request.args.get("scope") or "banks").strip()
    selected_scope = requested_scope if requested_scope in {"banks", "accounts", "cards"} else "banks"
    payment_methods = _load_payment_methods()
    banks = _load_banks(include_inactive=True)
    bank_summaries = _load_bank_summaries(selected_year)
    method_summaries = _load_payment_method_summaries(selected_year)
    if section == "relationships":
        relationship_count_by_bank = {}
        for method in payment_methods:
            relationship_count_by_bank[method[6]] = relationship_count_by_bank.get(method[6], 0) + 1
        banks.sort(key=lambda bank: (-relationship_count_by_bank.get(bank[0], 0), bank[1].lower()))
    return render_template(
        "management_payment_methods.html",
        payment_methods=payment_methods,
        banks=banks,
        bank_summaries=bank_summaries,
        payment_method_kpis={
            "active_banks": sum(1 for bank in banks if bank[2]),
            "total_banks": len(banks),
            "active_accounts": sum(1 for method in payment_methods if method[2] == "bank_account" and method[5]),
            "total_accounts": sum(1 for method in payment_methods if method[2] == "bank_account"),
            "active_cards": sum(1 for method in payment_methods if method[2] == "card" and method[5]),
            "total_cards": sum(1 for method in payment_methods if method[2] == "card"),
            "month_spent": sum((bank[7] for bank in bank_summaries), 0),
        },
        chart_scopes={
            "banks": {
                "labels": [bank[1] for bank in bank_summaries],
                "month_spent": [float(bank[7]) for bank in bank_summaries],
                "year_spent": [float(bank[8]) for bank in bank_summaries],
                "total_spent": [float(bank[6]) for bank in bank_summaries],
                "urls": [f"/payment-methods/banks/{bank[0]}" for bank in bank_summaries],
            },
            "accounts": {
                "labels": [method[1] for method in method_summaries if method[2] == "bank_account"],
                "month_spent": [float(method[4]) for method in method_summaries if method[2] == "bank_account"],
                "year_spent": [float(method[5]) for method in method_summaries if method[2] == "bank_account"],
                "total_spent": [float(method[3]) for method in method_summaries if method[2] == "bank_account"],
                "urls": [f"/payment-methods/{method[0]}" for method in method_summaries if method[2] == "bank_account"],
            },
            "cards": {
                "labels": [method[1] for method in method_summaries if method[2] == "card"],
                "month_spent": [float(method[4]) for method in method_summaries if method[2] == "card"],
                "year_spent": [float(method[5]) for method in method_summaries if method[2] == "card"],
                "total_spent": [float(method[3]) for method in method_summaries if method[2] == "card"],
                "urls": [f"/payment-methods/{method[0]}" for method in method_summaries if method[2] == "card"],
            },
        },
        payment_methods_section=section,
        available_years=available_years,
        selected_year=selected_year,
        selected_scope=selected_scope,
        is_admin=(session.get("role") == "admin"),
        **_flash_payload(),
        current_page="payment_methods",
        management_section="payment_methods",
    )


@management_bp.route("/payment-methods/<int:method_id>")
def payment_method_detail(method_id):
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT pm.id, pm.name, pm.kind, pm.account_ref, pm.is_active,
                       pm.created_at, pm.updated_at, pm.bank_id,
                       COALESCE(b.name, pm.bank_name) AS bank_name,
                       COALESCE(b.is_active, FALSE) AS bank_is_active,
                       pm.parent_account_id, parent.name AS parent_account_name
                FROM payment_methods pm
                LEFT JOIN banks b ON b.id=pm.bank_id
                LEFT JOIN payment_methods parent ON parent.id=pm.parent_account_id
                WHERE pm.id=%s
                """,
                (method_id,),
            )
            payment_method = cur.fetchone()
            if not payment_method:
                return redirect(url_for("management.management_payment_methods"))
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(amount), 0),
                    COALESCE(SUM(amount) FILTER (WHERE date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0),
                    COUNT(*)
                FROM records
                WHERE payment_method_id=%s AND type='expense'
                """,
                (method_id,),
            )
            totals = cur.fetchone()
            per_page = 10
            total_pages = max(1, (totals[2] + per_page - 1) // per_page)
            page = request.args.get("page", 1, type=int) or 1
            page = min(max(page, 1), total_pages)
            cur.execute(
                """
                SELECT r.id, r.concept, r.amount, r.date, r.source, c.name, r.comment
                FROM records r
                LEFT JOIN categories c ON c.id=r.category_id
                WHERE r.payment_method_id=%s AND r.type='expense'
                ORDER BY r.date DESC, r.id DESC
                LIMIT %s OFFSET %s
                """,
                (method_id, per_page, (page - 1) * per_page),
            )
            recent_records = cur.fetchall()
    return render_template(
        "payment_method_detail.html",
        payment_method=payment_method,
        total_spent=totals[0],
        month_spent=totals[1],
        movement_count=totals[2],
        recent_records=recent_records,
        page=page,
        total_pages=total_pages,
        payment_methods_section="accounts" if payment_method[2] == "bank_account" else "cards",
        current_page="payment_methods",
        management_section="payment_methods",
    )


@management_bp.route("/payment-methods/banks/<int:bank_id>")
def bank_detail(bank_id):
    denied = _require_roles("admin", "editor")
    if denied:
        return denied
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, is_active, created_at, updated_at FROM banks WHERE id=%s",
                (bank_id,),
            )
            bank = cur.fetchone()
            if not bank:
                return redirect(url_for("management.payment_methods_section", section="banks"))
            cur.execute(
                """
                SELECT pm.id, pm.name, pm.kind, pm.account_ref, pm.is_active, parent.name
                FROM payment_methods pm
                LEFT JOIN payment_methods parent ON parent.id=pm.parent_account_id
                WHERE pm.bank_id=%s
                ORDER BY pm.kind, pm.name
                """,
                (bank_id,),
            )
            linked_methods = cur.fetchall()
            cur.execute(
                """
                SELECT id, name, status, principal_amount, monthly_payment,
                       COALESCE(total_repayment_amount, principal_amount)
                FROM loans
                WHERE bank_id=%s
                ORDER BY status, name
                """,
                (bank_id,),
            )
            linked_loans = cur.fetchall()
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(r.amount), 0),
                    COALESCE(SUM(r.amount) FILTER (WHERE r.date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0),
                    COALESCE(SUM(r.amount) FILTER (WHERE LEFT(r.date, 4)=TO_CHAR(CURRENT_DATE, 'YYYY')), 0),
                    COUNT(r.id)
                FROM records r
                JOIN payment_methods pm ON pm.id=r.payment_method_id
                WHERE pm.bank_id=%s
                  AND r.type='expense'
                  AND COALESCE(r.is_loan_payment, FALSE)=FALSE
                """,
                (bank_id,),
            )
            totals = cur.fetchone()
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(r.amount), 0),
                    COALESCE(SUM(r.amount) FILTER (WHERE r.date=TO_CHAR(CURRENT_DATE, 'YYYY-MM')), 0),
                    COALESCE(SUM(r.amount) FILTER (WHERE LEFT(r.date, 4)=TO_CHAR(CURRENT_DATE, 'YYYY')), 0),
                    COUNT(r.id)
                FROM records r
                JOIN loans l ON l.id=r.loan_id
                WHERE l.bank_id=%s
                  AND r.type='expense'
                  AND r.is_loan_payment=TRUE
                """,
                (bank_id,),
            )
            loan_payment_spending = cur.fetchone()
            per_page = 10
            total_pages = max(1, (totals[3] + per_page - 1) // per_page)
            page = request.args.get("page", 1, type=int) or 1
            page = min(max(page, 1), total_pages)
            cur.execute(
                """
                SELECT r.id, r.concept, r.amount, r.date, r.source, c.name, pm.name
                FROM records r
                JOIN payment_methods pm ON pm.id=r.payment_method_id
                LEFT JOIN categories c ON c.id=r.category_id
                WHERE pm.bank_id=%s AND r.type='expense'
                ORDER BY r.date DESC, r.id DESC
                LIMIT %s OFFSET %s
                """,
                (bank_id, per_page, (page - 1) * per_page),
            )
            recent_records = cur.fetchall()
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(l.principal_amount), 0),
                    COALESCE(SUM(paid.paid_amount), 0),
                    COALESCE(SUM(CASE WHEN l.status='active' THEN l.monthly_payment ELSE 0 END), 0),
                    COALESCE(SUM(COALESCE(l.total_repayment_amount, l.principal_amount)), 0)
                FROM loans l
                LEFT JOIN (
                    SELECT loan_id, SUM(amount) AS paid_amount
                    FROM records
                    WHERE type='expense' AND is_loan_payment=TRUE
                    GROUP BY loan_id
                ) paid ON paid.loan_id=l.id
                WHERE l.bank_id=%s AND l.status <> 'cancelled'
                """,
                (bank_id,),
            )
            loan_totals = cur.fetchone()
    return render_template(
        "bank_detail.html",
        bank=bank,
        accounts=[method for method in linked_methods if method[2] == "bank_account"],
        cards=[method for method in linked_methods if method[2] == "card"],
        loans=linked_loans,
        active_method_count=sum(1 for method in linked_methods if method[4]),
        total_spent=totals[0] + loan_payment_spending[0],
        month_spent=totals[1] + loan_payment_spending[1],
        year_spent=totals[2] + loan_payment_spending[2],
        movement_count=totals[3] + loan_payment_spending[3],
        recent_records=recent_records,
        page=page,
        total_pages=total_pages,
        loan_principal=loan_totals[0],
        loan_amortized=loan_totals[1],
        loan_monthly_payment=loan_totals[2],
        loan_pending=max(loan_totals[3] - loan_totals[1], 0),
        payment_methods_section="banks",
        current_page="payment_methods",
        management_section="payment_methods",
    )


@management_bp.route("/management/payment-methods")
def legacy_management_payment_methods():
    return redirect(url_for("management.management_payment_methods"))


@management_bp.route("/management/payment-methods/<int:method_id>")
def legacy_payment_method_detail(method_id):
    return redirect(url_for("management.payment_method_detail", method_id=method_id))


@management_bp.route("/management/payment-methods/add", methods=["POST"])
@management_bp.route("/payment-methods/add", methods=["POST"])
def add_payment_method():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Name",
        MAX_PAYMENT_METHOD_NAME_LENGTH,
        required=True,
    )
    kind = (request.form.get("kind") or "card").strip()
    bank_id = _parse_int_or_none(request.form.get("bank_id"))
    parent_account_id = _parse_int_or_none(request.form.get("parent_account_id"))
    account_ref = (request.form.get("account_ref") or "").strip()
    is_active = (request.form.get("is_active") or "1") == "1"
    if kind not in {"card", "bank_account"}:
        kind = "card"
    if name_error:
        session["management_err"] = t(name_error)
        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
    if kind == "card" and parent_account_id is None:
        session["management_err"] = t("Select an active account.")
        return redirect(url_for("management.payment_methods_section", section="cards"))
    if kind == "bank_account" and bank_id is None:
        session["management_err"] = t("Select an active bank.")
        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                if kind == "card":
                    cur.execute(
                        "SELECT bank_id FROM payment_methods WHERE id=%s AND kind='bank_account' AND is_active=TRUE",
                        (parent_account_id,),
                    )
                    account_row = cur.fetchone()
                    if not account_row:
                        session["management_err"] = t("Select an active account.")
                        return redirect(url_for("management.payment_methods_section", section="cards"))
                    bank_id = account_row[0]
                cur.execute("SELECT 1 FROM banks WHERE id=%s AND is_active=TRUE", (bank_id,))
                if not cur.fetchone():
                    session["management_err"] = t("Select an active bank.")
                    return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
                cur.execute(
                    """
                    INSERT INTO payment_methods (name, kind, bank_id, bank_name, account_ref, is_active, parent_account_id, updated_at)
                    VALUES (%s, %s, %s, (SELECT name FROM banks WHERE id=%s), %s, %s, %s, NOW())
                    RETURNING id
                    """,
                    (name, kind, bank_id, bank_id, account_ref or None, is_active, parent_account_id if kind == "card" else None),
                )
                method_id = cur.fetchone()[0]
                conn.commit()
        logger.info(
            "payment_method_create user=%s id=%s name=%s kind=%s bank_id=%s active=%s",
            session.get("user_name"),
            method_id,
            name,
            kind,
            bank_id,
            is_active,
        )
        session["management_msg"] = t("Payment method created.")
    except Exception:
        session["management_err"] = t("Name already exists.")
    return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))


@management_bp.route("/management/payment-methods/<int:method_id>/update", methods=["POST"])
@management_bp.route("/payment-methods/<int:method_id>/update", methods=["POST"])
def update_payment_method(method_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Name",
        MAX_PAYMENT_METHOD_NAME_LENGTH,
        required=True,
    )
    kind = (request.form.get("kind") or "card").strip()
    bank_id = _parse_int_or_none(request.form.get("bank_id"))
    parent_account_id = _parse_int_or_none(request.form.get("parent_account_id"))
    account_ref = (request.form.get("account_ref") or "").strip()
    is_active = (request.form.get("is_active") or "0") == "1"
    if kind not in {"card", "bank_account"}:
        kind = "card"
    if name_error:
        session["management_err"] = t(name_error)
        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
    if kind == "card" and parent_account_id is None:
        session["management_err"] = t("Select an active account.")
        return redirect(url_for("management.payment_methods_section", section="cards"))
    if kind == "bank_account" and bank_id is None:
        session["management_err"] = t("Select an active bank.")
        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                if kind == "card":
                    cur.execute(
                        "SELECT bank_id FROM payment_methods WHERE id=%s AND kind='bank_account' AND is_active=TRUE",
                        (parent_account_id,),
                    )
                    account_row = cur.fetchone()
                    if not account_row:
                        session["management_err"] = t("Select an active account.")
                        return redirect(url_for("management.payment_methods_section", section="cards"))
                    bank_id = account_row[0]
                cur.execute("SELECT bank_id FROM payment_methods WHERE id=%s", (method_id,))
                current_row = cur.fetchone()
                if not current_row:
                    return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
                current_bank_id = current_row[0]
                if bank_id is not None and bank_id != current_bank_id:
                    cur.execute("SELECT 1 FROM banks WHERE id=%s AND is_active=TRUE", (bank_id,))
                    if not cur.fetchone():
                        session["management_err"] = t("Select an active bank.")
                        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
                if is_active and bank_id is not None:
                    cur.execute("SELECT 1 FROM banks WHERE id=%s AND is_active=TRUE", (bank_id,))
                    if not cur.fetchone():
                        session["management_err"] = t("An account or card cannot be active when its bank is inactive.")
                        return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))
                cur.execute(
                    """
                    UPDATE payment_methods
                    SET name=%s,
                        kind=%s,
                        bank_id=%s,
                        bank_name=(SELECT name FROM banks WHERE id=%s),
                        account_ref=%s,
                        parent_account_id=%s,
                        is_active=%s,
                        updated_at=NOW()
                    WHERE id=%s
                    """,
                    (name, kind, bank_id, bank_id, account_ref or None, parent_account_id if kind == "card" else None, is_active, method_id),
                )
                updated = cur.rowcount
                if kind == "bank_account" and not is_active:
                    cur.execute(
                        "UPDATE payment_methods SET is_active=FALSE, updated_at=NOW() WHERE parent_account_id=%s",
                        (method_id,),
                    )
                conn.commit()
        logger.info(
            "payment_method_update user=%s id=%s name=%s kind=%s bank_id=%s active=%s updated=%s",
            session.get("user_name"),
            method_id,
            name,
            kind,
            bank_id,
            is_active,
            updated,
        )
        session["management_msg"] = t("Payment method updated.")
    except Exception:
        session["management_err"] = t("Name already exists.")
    return redirect(url_for("management.payment_methods_section", section="accounts" if kind == "bank_account" else "cards"))


def _parse_int_or_none(raw_value):
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None


@management_bp.route("/management/banks/add", methods=["POST"])
@management_bp.route("/payment-methods/banks/add", methods=["POST"])
def add_bank():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Bank name",
        MAX_BANK_NAME_LENGTH,
        required=True,
    )
    is_active = (request.form.get("is_active") or "1") == "1"
    if name_error:
        session["management_err"] = t(name_error)
        return redirect(url_for("management.payment_methods_section", section="banks"))
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO banks (name, is_active, updated_at)
                    VALUES (%s, %s, NOW())
                    RETURNING id
                    """,
                    (name, is_active),
                )
                bank_id = cur.fetchone()[0]
                conn.commit()
        logger.info(
            "bank_create user=%s id=%s name=%s active=%s",
            session.get("user_name"),
            bank_id,
            name,
            is_active,
        )
        session["management_msg"] = t("Bank created.")
    except Exception:
        session["management_err"] = t("Bank already exists.")
    return redirect(url_for("management.payment_methods_section", section="banks"))


@management_bp.route("/management/banks/<int:bank_id>/update", methods=["POST"])
@management_bp.route("/payment-methods/banks/<int:bank_id>/update", methods=["POST"])
def update_bank(bank_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Bank name",
        MAX_BANK_NAME_LENGTH,
        required=True,
    )
    is_active = (request.form.get("is_active") or "0") == "1"
    if name_error:
        session["management_err"] = t(name_error)
        return redirect(url_for("management.payment_methods_section", section="banks"))
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
                updated = cur.rowcount
                cur.execute(
                    """
                    UPDATE payment_methods
                    SET bank_name=%s,
                        is_active=CASE WHEN %s THEN is_active ELSE FALSE END,
                        updated_at=NOW()
                    WHERE bank_id=%s
                    """,
                    (name, is_active, bank_id),
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
        logger.info(
            "bank_update user=%s id=%s name=%s active=%s updated=%s",
            session.get("user_name"),
            bank_id,
            name,
            is_active,
            updated,
        )
        session["management_msg"] = t("Bank updated.")
    except Exception:
        session["management_err"] = t("Bank already exists.")
    return redirect(url_for("management.payment_methods_section", section="banks"))


@management_bp.route("/management/banks/<int:bank_id>/delete", methods=["POST"])
@management_bp.route("/payment-methods/banks/<int:bank_id>/delete", methods=["POST"])
def delete_bank(bank_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM payment_methods WHERE bank_id=%s LIMIT 1", (bank_id,))
            if cur.fetchone():
                logger.info(
                    "bank_delete_blocked user=%s id=%s reason=payment_methods_in_use",
                    session.get("user_name"),
                    bank_id,
                )
                session["management_err"] = t("Cannot delete bank. It is used by accounts or cards.")
                return redirect(url_for("management.payment_methods_section", section="banks"))
            cur.execute("SELECT 1 FROM loans WHERE bank_id=%s LIMIT 1", (bank_id,))
            if cur.fetchone():
                logger.info(
                    "bank_delete_blocked user=%s id=%s reason=loans_in_use",
                    session.get("user_name"),
                    bank_id,
                )
                session["management_err"] = t("Cannot delete bank. It is used by loans.")
                return redirect(url_for("management.payment_methods_section", section="banks"))
            cur.execute("DELETE FROM banks WHERE id=%s", (bank_id,))
            deleted = cur.rowcount
            conn.commit()
    logger.info(
        "bank_delete user=%s id=%s deleted=%s",
        session.get("user_name"),
        bank_id,
        deleted,
    )
    session["management_msg"] = t("Bank deleted.")
    return redirect(url_for("management.payment_methods_section", section="banks"))


@management_bp.route("/management/payment-methods/<int:method_id>/delete", methods=["POST"])
@management_bp.route("/payment-methods/<int:method_id>/delete", methods=["POST"])
def delete_payment_method(method_id):
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT kind FROM payment_methods WHERE id=%s", (method_id,))
            method_row = cur.fetchone()
            section = "accounts" if method_row and method_row[0] == "bank_account" else "cards"
            cur.execute("SELECT 1 FROM records WHERE payment_method_id=%s LIMIT 1", (method_id,))
            if cur.fetchone():
                logger.info(
                    "payment_method_delete_blocked user=%s id=%s reason=records_in_use",
                    session.get("user_name"),
                    method_id,
                )
                session["management_err"] = t("Cannot delete payment method. It is used by expenses.")
                return redirect(url_for("management.payment_methods_section", section=section))
            cur.execute("SELECT 1 FROM payment_methods WHERE parent_account_id=%s LIMIT 1", (method_id,))
            if cur.fetchone():
                session["management_err"] = t("Cannot delete account. It has linked cards.")
                return redirect(url_for("management.payment_methods_section", section=section))
            cur.execute("DELETE FROM payment_methods WHERE id=%s", (method_id,))
            deleted = cur.rowcount
            conn.commit()
    logger.info(
        "payment_method_delete user=%s id=%s deleted=%s",
        session.get("user_name"),
        method_id,
        deleted,
    )
    session["management_msg"] = t("Payment method deleted.")
    return redirect(url_for("management.payment_methods_section", section=section))


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
    session["management_msg"] = f"{t('Database reset')}: {format_number(deleted)} {t('records deleted')}"

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
            demo_counts = _demo_data_counts(cur)
            conn.commit()
    invalidate_dashboard_cache()
    _log_demo_data_actions("seed", demo_counts, inserted)
    logger.info("demo_data_seed user=%s inserted=%s initial_saving=300", session.get("user_name"), inserted)
    session["management_msg"] = f"{t('Demo data inserted')}: {format_number(inserted)} {t('records')}"

    return redirect(url_for("management.management_system"))


@management_bp.route("/management/demo-data/clear", methods=["POST"])
def clear_demo_data():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))

    with get_db() as conn:
        with conn.cursor() as cur:
            _ensure_demo_functions(cur)
            demo_counts = _demo_data_counts(cur)
            cur.execute("SELECT management_clear_demo_data()")
            deleted = cur.fetchone()[0]
            conn.commit()
    invalidate_dashboard_cache()
    _log_demo_data_actions("clear", demo_counts, deleted)
    logger.info("demo_data_clear user=%s deleted=%s initial_saving_removed=true", session.get("user_name"), deleted)
    session["management_msg"] = f"{t('Demo data deleted')}: {format_number(deleted)} {t('records')}"

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
