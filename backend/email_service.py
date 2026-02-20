import base64
import logging
import os
import smtplib
from email.utils import formataddr
from email.message import EmailMessage

from db import get_db


logger = logging.getLogger("finance.email")


def _smtp_cipher():
    key = (os.environ.get("SMTP_ENCRYPTION_KEY") or "").strip()
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet
    except Exception:
        return None

    candidate = key.encode("utf-8")
    if len(candidate) != 44:
        candidate = base64.urlsafe_b64encode(candidate[:32].ljust(32, b"0"))
    return Fernet(candidate)


def _load_enabled_smtp():
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
                return None
            host, port, username, password_encrypted, from_name, from_email, use_tls, enabled = row
            if not enabled:
                return None
            if not host or not username or not from_email or not password_encrypted:
                return None
            cipher = _smtp_cipher()
            if not cipher:
                return None
            try:
                password = cipher.decrypt(password_encrypted.encode("utf-8")).decode("utf-8")
            except Exception:
                return None
            return {
                "host": host,
                "port": int(port or 587),
                "username": username,
                "password": password,
                "from_name": from_name or "",
                "from_email": from_email,
                "use_tls": bool(use_tls),
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
