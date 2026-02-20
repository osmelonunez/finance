import logging
import psycopg2
import re
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from db import get_db, is_app_initialized, set_database_url
from migrations import apply_migrations


setup_bp = Blueprint("setup", __name__)
logger = logging.getLogger("finance.setup")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def _build_db_url_from_form(prefix: str = ""):
    host = (request.form.get(f"{prefix}db_host") or "").strip()
    port = (request.form.get(f"{prefix}db_port") or "").strip()
    db_name = (request.form.get(f"{prefix}db_name") or "").strip()
    db_user = (request.form.get(f"{prefix}db_user") or "").strip()
    db_password = request.form.get(f"{prefix}db_password") or ""
    if not host or not port or not db_name or not db_user:
        return ""
    return f"postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}"


def _collect_setup_form_state():
    return {
        "setup_mode": (request.form.get("setup_mode") or "").strip(),
        "db_host": (request.form.get("db_host") or "").strip(),
        "db_port": (request.form.get("db_port") or "5432").strip(),
        "db_name": (request.form.get("db_name") or "").strip(),
        "db_user": (request.form.get("db_user") or "").strip(),
        "db_password": request.form.get("db_password") or "",
        "owner_username_new": (request.form.get("owner_username_new") or "").strip(),
        "owner_email_new": (request.form.get("owner_email_new") or "").strip(),
        "owner_password_new": request.form.get("owner_password_new") or "",
        "owner_password_confirm_new": request.form.get("owner_password_confirm_new") or "",
        "target_db_host": (request.form.get("target_db_host") or "").strip(),
        "target_db_port": (request.form.get("target_db_port") or "5432").strip(),
        "target_db_name": (request.form.get("target_db_name") or "").strip(),
        "target_db_user": (request.form.get("target_db_user") or "").strip(),
        "target_db_password": request.form.get("target_db_password") or "",
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
    conn.commit()


def _is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    return has_upper and has_lower and has_digit


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.fullmatch((email or "").strip()))


def _is_valid_username(username: str) -> bool:
    return bool(USERNAME_RE.fullmatch((username or "").strip()))


def _ensure_owner_user(conn, username: str, email: str, password: str):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    if not username or not email or not password:
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM users WHERE LOWER(username)=LOWER(%s) OR LOWER(email)=LOWER(%s)",
            (username, email),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE users
                SET email=%s, username=%s, password_hash=%s, role='admin', is_admin=TRUE, is_active=TRUE
                WHERE id=%s
                """,
                (email, username, generate_password_hash(password), row[0]),
            )
        else:
            cur.execute(
                """
                INSERT INTO users (email, username, password_hash, role, is_admin, is_active)
                VALUES (%s, %s, %s, 'admin', TRUE, TRUE)
                """,
                (email, username, generate_password_hash(password)),
            )
    conn.commit()


@setup_bp.route("/setup", methods=["GET"])
def setup_page():
    if is_app_initialized():
        return redirect(url_for("auth.login"))
    return render_template(
        "setup.html",
        error=session.pop("setup_err", ""),
        message=session.pop("setup_msg", ""),
        setup_form=session.get("setup_form", {}),
        current_page="setup",
    )


@setup_bp.route("/setup/use-existing", methods=["POST"])
def setup_use_existing():
    if is_app_initialized():
        return redirect(url_for("auth.login"))

    session["setup_form"] = _collect_setup_form_state()
    db_url = _build_db_url_from_form()

    if not db_url:
        session["setup_err"] = "Database host, port, name and user are required."
        return redirect(url_for("setup.setup_page"))

    try:
        set_database_url(db_url)
        with get_db() as conn:
            apply_migrations(conn)
            _upsert_initialized(conn, 1)
        session.pop("setup_form", None)
        session["setup_msg"] = "Setup completed. You can sign in now."
        return redirect(url_for("auth.login"))
    except Exception as exc:
        logger.warning("setup_use_existing_failed error=%s", exc)
        session["setup_err"] = "Setup failed. Check connection and database permissions."
        return redirect(url_for("setup.setup_page"))


@setup_bp.route("/setup/create-new", methods=["POST"])
def setup_create_new():
    if is_app_initialized():
        return redirect(url_for("auth.login"))

    session["setup_form"] = _collect_setup_form_state()
    target_db_url = _build_db_url_from_form(prefix="target_")
    owner_username = (request.form.get("owner_username_new") or "").strip()
    owner_email = (request.form.get("owner_email_new") or "").strip().lower()
    owner_password = request.form.get("owner_password_new") or ""
    owner_password_confirm = request.form.get("owner_password_confirm_new") or ""

    if not target_db_url:
        session["setup_err"] = "Database connection fields are required."
        return redirect(url_for("setup.setup_page"))
    if not owner_username or not owner_email or not owner_password:
        session["setup_err"] = "Admin username, email and password are required."
        return redirect(url_for("setup.setup_page"))
    if not _is_valid_username(owner_username):
        session["setup_err"] = "Invalid username. Use 3-30 chars: letters, numbers, dot, underscore or dash."
        return redirect(url_for("setup.setup_page"))
    if not _is_valid_email(owner_email):
        session["setup_err"] = "Invalid email format."
        return redirect(url_for("setup.setup_page"))
    if owner_password != owner_password_confirm:
        session["setup_err"] = "Passwords do not match."
        return redirect(url_for("setup.setup_page"))
    if not _is_strong_password(owner_password):
        session["setup_err"] = "Password must be at least 8 chars and include uppercase, lowercase and number."
        return redirect(url_for("setup.setup_page"))

    try:
        set_database_url(target_db_url)
        with get_db() as conn:
            apply_migrations(conn)
            _ensure_owner_user(conn, owner_username, owner_email, owner_password)
            _upsert_initialized(conn, 1)
        session.pop("setup_form", None)

        session["setup_msg"] = "Database initialized."
        return redirect(url_for("auth.login"))
    except psycopg2.Error as exc:
        logger.warning("setup_create_new_db_connect_failed error=%s", exc)
        session["setup_err"] = "Connection failed. Ensure database and user already exist."
        return redirect(url_for("setup.setup_page"))
    except Exception as exc:
        logger.warning("setup_create_new_failed error=%s", exc)
        session["setup_err"] = "Initialization failed. Check setup values and logs."
        return redirect(url_for("setup.setup_page"))


@setup_bp.route("/setup/test-connection", methods=["POST"])
def setup_test_connection():
    if is_app_initialized():
        return redirect(url_for("auth.login"))
    session["setup_form"] = _collect_setup_form_state()
    prefix = (request.form.get("test_prefix") or "").strip()
    if prefix not in {"", "target_"}:
        prefix = ""
    db_url = _build_db_url_from_form(prefix=prefix)
    if not db_url:
        session["setup_err"] = "Database host, port, name and user are required."
        return redirect(url_for("setup.setup_page"))
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), COALESCE(inet_server_addr()::text, '')")
                row = cur.fetchone()
        db_name = row[0] if row else "unknown"
        db_ip = row[1] if row and row[1] else "unknown"
        session["setup_msg"] = f"Connection test OK (db={db_name}, ip={db_ip})."
    except Exception as exc:
        logger.warning("setup_test_connection_failed prefix=%s error=%s", prefix, exc)
        session["setup_err"] = "Connection test failed."
    return redirect(url_for("setup.setup_page"))
