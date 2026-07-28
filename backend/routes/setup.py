import logging
import re

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from db import get_db, is_app_initialized


setup_bp = Blueprint("setup", __name__)
logger = logging.getLogger("finance.setup")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def _collect_setup_form_state():
    return {
        "owner_username": (request.form.get("owner_username") or "").strip(),
        "owner_email": (request.form.get("owner_email") or "").strip(),
    }


def _upsert_initialized(conn, value: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO settings (key, value)
            VALUES ('app_initialized', %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """,
            (value,),
        )


def _is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(ch.isupper() for ch in password)
        and any(ch.islower() for ch in password)
        and any(ch.isdigit() for ch in password)
    )


def _database_status():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT current_database(), COALESCE(inet_server_addr()::text, '')"
                )
                row = cur.fetchone()
        return {
            "connected": True,
            "database": row[0] if row else "unknown",
            "server": row[1] if row and row[1] else "local",
        }
    except Exception as exc:
        logger.warning("setup_database_check_failed error=%s", exc)
        return {"connected": False, "database": "", "server": ""}


@setup_bp.route("/setup", methods=["GET"])
def setup_page():
    if is_app_initialized():
        return redirect(url_for("auth.login"))
    return render_template(
        "setup.html",
        error=session.pop("setup_err", ""),
        message=session.pop("setup_msg", ""),
        setup_form=session.get("setup_form", {}),
        database_status=_database_status(),
        current_page="setup",
    )


@setup_bp.route("/setup/test-connection", methods=["POST"])
def setup_test_connection():
    if is_app_initialized():
        return redirect(url_for("auth.login"))
    status = _database_status()
    if status["connected"]:
        session["setup_msg"] = (
            f"Connection test OK (db={status['database']}, server={status['server']})."
        )
    else:
        session["setup_err"] = "Connection test failed. Check DATABASE_URL and container logs."
    return redirect(url_for("setup.setup_page"))


@setup_bp.route("/setup/initialize", methods=["POST"])
def setup_initialize():
    if is_app_initialized():
        return redirect(url_for("auth.login"))

    session["setup_form"] = _collect_setup_form_state()
    username = (request.form.get("owner_username") or "").strip()
    email = (request.form.get("owner_email") or "").strip().lower()
    password = request.form.get("owner_password") or ""
    password_confirm = request.form.get("owner_password_confirm") or ""

    if not username or not email or not password:
        session["setup_err"] = "Admin username, email and password are required."
        return redirect(url_for("setup.setup_page"))
    if not USERNAME_RE.fullmatch(username):
        session["setup_err"] = (
            "Invalid username. Use 3-30 chars: letters, numbers, dot, underscore or dash."
        )
        return redirect(url_for("setup.setup_page"))
    if not EMAIL_RE.fullmatch(email):
        session["setup_err"] = "Invalid email format."
        return redirect(url_for("setup.setup_page"))
    if password != password_confirm:
        session["setup_err"] = "Passwords do not match."
        return redirect(url_for("setup.setup_page"))
    if not _is_strong_password(password):
        session["setup_err"] = (
            "Password must be at least 8 chars and include uppercase, lowercase and number."
        )
        return redirect(url_for("setup.setup_page"))

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(username)=LOWER(%s) OR LOWER(email)=LOWER(%s)
                    """,
                    (username, email),
                )
                if cur.fetchone():
                    session["setup_err"] = "Username or email already exists."
                    return redirect(url_for("setup.setup_page"))
                cur.execute(
                    """
                    INSERT INTO users
                        (email, username, password_hash, role, is_admin, is_active)
                    VALUES (%s, %s, %s, 'admin', TRUE, TRUE)
                    """,
                    (email, username, generate_password_hash(password)),
                )
            _upsert_initialized(conn, 1)
            conn.commit()
        session.pop("setup_form", None)
        session["setup_msg"] = "Setup completed. You can sign in now."
        return redirect(url_for("auth.login"))
    except Exception as exc:
        logger.warning("setup_initialize_failed error=%s", exc)
        session["setup_err"] = "Initialization failed. Check DATABASE_URL and container logs."
        return redirect(url_for("setup.setup_page"))
