import logging
import os
import re

from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, is_app_initialized
from email_service import notify_admins_pending_user
from security import limiter


auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger("finance.auth")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def _redirect_with_message(next_path, key, message):
    if not next_path:
        next_path = "/"
    sep = "&" if "?" in next_path else "?"
    return redirect(f"{next_path}{sep}{key}={message}")


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


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit(
    os.environ.get("RATE_LIMIT_LOGIN_IP", "10 per minute;60 per hour"),
    methods=["POST"],
)
@limiter.limit(
    os.environ.get("RATE_LIMIT_LOGIN_ID", "5 per minute;30 per hour"),
    methods=["POST"],
    key_func=lambda: f"{get_remote_address()}:{(request.form.get('email') or '').strip().lower()}",
)
def login():
    if not is_app_initialized():
        return redirect(url_for("setup.setup_page"))
    error = None
    if request.method == "POST":
        identifier = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, password_hash, is_active, is_admin, username, email, role, COALESCE(per_page, 15), COALESCE(language, 'en'),
                           COALESCE(email_notifications, TRUE)
                    FROM users
                    WHERE LOWER(email)=LOWER(%s) OR LOWER(username)=LOWER(%s)
                    """,
                    (identifier, identifier)
                )
                row = cur.fetchone()

        if not row or not check_password_hash(row[1], password):
            error = "Invalid email or password."
        elif not row[2]:
            error = "Account pending approval."
        else:
            session.permanent = True
            session["user_id"] = row[0]
            session["user_email"] = row[5]
            session["is_admin"] = row[3]
            session["role"] = row[6]
            session["user_name"] = row[4]
            session["per_page"] = int(row[7] or 15)
            session["lang"] = (row[8] or "en")
            session["email_notifications"] = bool(row[9])
            return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html", error=error)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit(
    os.environ.get("RATE_LIMIT_REGISTER_IP", "5 per 10 minutes;20 per hour"),
    methods=["POST"],
)
def register():
    if not is_app_initialized():
        return redirect(url_for("setup.setup_page"))
    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        if not email or not password or not username:
            error = "Email, username, and password are required."
        elif not _is_valid_email(email):
            error = "Invalid email format."
        elif not _is_valid_username(username):
            error = "Invalid username. Use 3-30 chars: letters, numbers, dot, underscore or dash."
        elif password != confirm:
            error = "Passwords do not match."
        elif not _is_strong_password(password):
            error = "Password must be at least 8 chars and include uppercase, lowercase and number."
        else:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM users WHERE email=%s", (email,))
                    exists = cur.fetchone()
                    if exists:
                        error = "Email already registered."
                    else:
                        cur.execute("SELECT 1 FROM users WHERE LOWER(username)=LOWER(%s)", (username,))
                        exists_username = cur.fetchone()
                        if exists_username:
                            error = "Username already taken."
                        else:
                            cur.execute(
                            "INSERT INTO users (email, username, password_hash, role, is_active) VALUES (%s, %s, %s, 'user', FALSE)",
                            (email, username, generate_password_hash(password))
                        )
                            conn.commit()
                            notify_admins_pending_user(username, email)
                            logger.info("user_registered_pending username=%s email=%s", username, email)
                            return redirect(url_for("auth.login"))

    return render_template("register.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(email_notifications, TRUE) FROM users WHERE id=%s",
                (session["user_id"],),
            )
            row = cur.fetchone()
    email_notifications = bool(row[0]) if row else True
    session["email_notifications"] = email_notifications
    return render_template(
        "profile.html",
        success=request.args.get("profile_success"),
        error=request.args.get("profile_error"),
        email_notifications=email_notifications,
        current_page="profile",
    )


@auth_bp.route("/profile/username", methods=["POST"])
def update_username():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    username = (request.form.get("username") or "").strip()
    next_path = request.form.get("next") or "/"

    if not username:
        return _redirect_with_message(next_path, "profile_error", "Username is required.")
    if not _is_valid_username(username):
        return _redirect_with_message(next_path, "profile_error", "Invalid username. Use 3-30 chars: letters, numbers, dot, underscore or dash.")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE LOWER(username)=LOWER(%s) AND id<>%s", (username, session["user_id"]))
            if cur.fetchone():
                return _redirect_with_message(next_path, "profile_error", "Username already taken.")
            cur.execute("UPDATE users SET username=%s WHERE id=%s", (username, session["user_id"]))
            conn.commit()

    session["user_name"] = username
    return _redirect_with_message(next_path, "profile_success", "Username updated.")


@auth_bp.route("/profile/email", methods=["POST"])
def update_email():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    email = (request.form.get("email") or "").strip().lower()
    next_path = request.form.get("next") or "/"

    if not email:
        return _redirect_with_message(next_path, "profile_error", "Email is required.")
    if not _is_valid_email(email):
        return _redirect_with_message(next_path, "profile_error", "Invalid email format.")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE LOWER(email)=LOWER(%s) AND id<>%s", (email, session["user_id"]))
            if cur.fetchone():
                return _redirect_with_message(next_path, "profile_error", "Email already in use.")
            cur.execute("UPDATE users SET email=%s WHERE id=%s", (email, session["user_id"]))
            conn.commit()

    session["user_email"] = email
    return _redirect_with_message(next_path, "profile_success", "Email updated.")


@auth_bp.route("/profile/password", methods=["POST"])
@limiter.limit(
    os.environ.get("RATE_LIMIT_PASSWORD_CHANGE", "5 per 15 minutes"),
    key_func=lambda: f"{get_remote_address()}:{session.get('user_id', 'anon')}",
)
def update_password():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    current_password = request.form.get("current_password") or ""
    new_password = request.form.get("new_password") or ""
    confirm_password = request.form.get("confirm_password") or ""
    next_path = request.form.get("next") or "/"

    if not current_password or not new_password:
        return _redirect_with_message(next_path, "profile_error", "All password fields are required.")
    if new_password != confirm_password:
        return _redirect_with_message(next_path, "profile_error", "Passwords do not match.")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE id=%s", (session["user_id"],))
            row = cur.fetchone()
            if not row or not check_password_hash(row[0], current_password):
                return _redirect_with_message(next_path, "profile_error", "Current password is incorrect.")
            cur.execute(
                "UPDATE users SET password_hash=%s WHERE id=%s",
                (generate_password_hash(new_password), session["user_id"])
            )
            conn.commit()

    return _redirect_with_message(next_path, "profile_success", "Password updated.")


@auth_bp.route("/profile/per-page", methods=["POST"])
def update_per_page_pref():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    next_path = request.form.get("next") or "/"
    raw = (request.form.get("per_page") or "15").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 15
    if value < 5:
        value = 5
    if value > 100:
        value = 100

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET per_page=%s WHERE id=%s", (value, session["user_id"]))
            conn.commit()
    session["per_page"] = value
    return _redirect_with_message(next_path, "profile_success", "Rows per page updated.")


@auth_bp.route("/profile/language", methods=["POST"])
def update_language_pref():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    next_path = request.form.get("next") or "/profile"
    lang = (request.form.get("language") or "en").strip().lower()
    if lang not in {"en", "es"}:
        lang = "en"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET language=%s WHERE id=%s", (lang, session["user_id"]))
            conn.commit()
    session["lang"] = lang
    return _redirect_with_message(next_path, "profile_success", "Language updated.")


@auth_bp.route("/profile/email-notifications", methods=["POST"])
def update_email_notifications_pref():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    next_path = request.form.get("next") or "/profile"
    enabled = request.form.get("email_notifications") == "1"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET email_notifications=%s WHERE id=%s",
                (enabled, session["user_id"]),
            )
            conn.commit()
    session["email_notifications"] = enabled
    return _redirect_with_message(next_path, "profile_success", "Email notifications updated.")
