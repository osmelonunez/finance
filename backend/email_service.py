import logging
import os
import smtplib
from email.utils import formataddr
from email.message import EmailMessage

from db import get_db


logger = logging.getLogger("finance.email")


def _env_bool(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _load_enabled_smtp():
    if not _env_bool("SMTP_ENABLED"):
        return None
    host = (os.environ.get("SMTP_HOST") or "").strip()
    username = (os.environ.get("SMTP_USER") or "").strip()
    password = os.environ.get("SMTP_PASSWORD") or ""
    from_email = (os.environ.get("SMTP_FROM_EMAIL") or "").strip()
    try:
        port = int((os.environ.get("SMTP_PORT") or "587").strip())
    except ValueError:
        return None
    if not host or not username or not password or not from_email or not 1 <= port <= 65535:
        return None
    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "from_name": (os.environ.get("SMTP_SENDER_NAME") or "").strip(),
        "from_email": from_email,
        "use_tls": _env_bool("SMTP_USE_TLS", True),
    }


def smtp_status():
    enabled = _env_bool("SMTP_ENABLED")
    configured = _load_enabled_smtp() is not None
    return {
        "enabled": enabled,
        "configured": configured,
        "host": (os.environ.get("SMTP_HOST") or "").strip() if configured else "",
        "from_email": (os.environ.get("SMTP_FROM_EMAIL") or "").strip() if configured else "",
    }


def send_email(recipients, subject, body, html_body=None):
    smtp = _load_enabled_smtp()
    if not smtp:
        logger.info("email_skipped reason=smtp_not_configured recipients=%s", recipients)
        return False
    if not recipients:
        return False
    if isinstance(recipients, str):
        recipients = [recipients]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((smtp["from_name"], smtp["from_email"])) if smtp.get("from_name") else smtp["from_email"]
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp["host"], smtp["port"], timeout=20) as server:
            if smtp["use_tls"]:
                server.starttls()
            server.login(smtp["username"], smtp["password"])
            server.send_message(msg)
        logger.info("email_sent recipients=%s subject=%s", recipients, subject)
        return True
    except Exception as exc:
        logger.warning("email_send_failed recipients=%s subject=%s error=%s", recipients, subject, exc)
        return False


def notify_admins_pending_user(username, email):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT email
                FROM users
                WHERE role='admin' AND is_active=TRUE AND COALESCE(email_notifications, TRUE)=TRUE
                """
            )
            recipients = [r[0] for r in cur.fetchall() if r and r[0]]
    if not recipients:
        return False
    subject = "Finance: user pending approval"
    body = (
        "A new user is waiting for approval.\n\n"
        f"Username: {username}\n"
        f"Email: {email}\n"
    )
    return send_email(recipients, subject, body)


def notify_user_approved(username, email):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT email
                FROM users
                WHERE LOWER(email)=LOWER(%s)
                  AND is_active=TRUE
                  AND COALESCE(email_notifications, TRUE)=TRUE
                LIMIT 1
                """,
                (email,),
            )
            row = cur.fetchone()
    if not row or not row[0]:
        return False
    subject = "Finance: account approved"
    body = (
        "Your Finance account has been approved.\n\n"
        f"Username: {username}\n"
        "You can now log in."
    )
    return send_email(row[0], subject, body)
