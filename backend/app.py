import logging
import os
import secrets
import time
import uuid
import json
from datetime import datetime, timedelta

from flask import Flask, g, has_request_context, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from db import get_db, init_db, is_app_initialized
from backup_service import maybe_run_scheduled_backup
from report_service import start_report_scheduler
from routes.dashboard import dashboard_bp
from routes.movements import movements_bp
from routes.management import management_bp
from routes.categories import categories_bp
from routes.auth import auth_bp
from routes.backups import backups_bp
from routes.setup import setup_bp
from routes.loans import loans_bp
from i18n import category_description, category_name, get_lang, t
from security import limiter
from log_safety import redact_text
from log_formatting import color_enabled, text_formatter


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, "request_id", "-")
            record.user = session.get("user_name", "-")
            record.path = request.path
            record.method = request.method
        else:
            record.request_id = getattr(record, "request_id", "-")
            record.user = getattr(record, "user", "-")
            record.path = getattr(record, "path", "")
            record.method = getattr(record, "method", "")
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        message = redact_text(record.getMessage())
        payload = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", "log"),
            "message": message,
            "request_id": getattr(record, "request_id", "-"),
            "user": getattr(record, "user", "-"),
        }
        for key in ("path", "method", "status", "duration_ms", "ip"):
            value = getattr(record, key, None)
            if value not in (None, ""):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging():
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_format = os.environ.get("LOG_FORMAT", "json").strip().lower()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    handler = logging.StreamHandler()
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            text_formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                color_enabled(log_format),
            )
        )
    handler.addFilter(RequestContextFilter())
    root.addHandler(handler)


configure_logging()
logger = logging.getLogger("finance.app")
DEFAULT_SECRET_KEY = "dev-secret"
DEFAULT_SMTP_ENCRYPTION_KEY = "change-this-smtp-key"
DEFAULT_DB_CONFIG_ENCRYPTION_KEY = "change-this-db-config-key"

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/public",
    static_url_path="/static"
)
app.secret_key = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)
app.config["APP_VERSION"] = os.environ.get("APP_VERSION", "3.4.0")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _ensure_csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def _is_https_request() -> bool:
    if request.is_secure:
        return True
    proto = (request.headers.get("X-Forwarded-Proto") or "").strip().lower()
    return proto == "https"


def _strict_secrets_enabled() -> bool:
    env = (os.environ.get("APP_ENV") or "").strip().lower()
    if env == "production":
        return True
    return _env_bool("FINANCE_STRICT_SECRETS", False)


def _validate_runtime_secrets():
    if not _strict_secrets_enabled():
        return
    secret_key = (os.environ.get("SECRET_KEY") or "").strip()
    smtp_key = (os.environ.get("SMTP_ENCRYPTION_KEY") or "").strip()
    db_config_key = (os.environ.get("DB_CONFIG_ENCRYPTION_KEY") or "").strip()
    uses_env_database_url = bool((os.environ.get("DATABASE_URL") or "").strip())
    if not secret_key or secret_key == DEFAULT_SECRET_KEY:
        logger.error("startup_blocked reason=invalid_secret_key")
        raise RuntimeError("SECRET_KEY must be set to a non-default value in production.")
    if not smtp_key or smtp_key == DEFAULT_SMTP_ENCRYPTION_KEY:
        logger.error("startup_blocked reason=invalid_smtp_encryption_key")
        raise RuntimeError("SMTP_ENCRYPTION_KEY must be set to a non-default value in production.")
    if not uses_env_database_url and (not db_config_key or db_config_key == DEFAULT_DB_CONFIG_ENCRYPTION_KEY):
        logger.error("startup_blocked reason=invalid_db_config_encryption_key")
        raise RuntimeError(
            "DB_CONFIG_ENCRYPTION_KEY must be set to a non-default value in production when using APP_CONFIG_PATH."
        )


session_lifetime_hours_raw = os.environ.get("SESSION_LIFETIME_HOURS", "12")
try:
    session_lifetime_hours = max(1, int(session_lifetime_hours_raw))
except (TypeError, ValueError):
    session_lifetime_hours = 12
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=session_lifetime_hours)
app.config["SESSION_COOKIE_SECURE"] = _env_bool("SESSION_COOKIE_SECURE", True)
app.config["SESSION_COOKIE_HTTPONLY"] = _env_bool("SESSION_COOKIE_HTTPONLY", True)
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
app.config["RATELIMIT_STORAGE_URI"] = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
app.config["RATELIMIT_STRATEGY"] = os.environ.get("RATELIMIT_STRATEGY", "fixed-window")
app.config["RATELIMIT_HEADERS_ENABLED"] = True
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
_validate_runtime_secrets()
limiter.init_app(app)

app.register_blueprint(dashboard_bp)
app.register_blueprint(movements_bp)
app.register_blueprint(management_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(backups_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(loans_bp)
start_report_scheduler()


@app.context_processor
def inject_template_globals():
    lang = get_lang()
    return {
        "current_year": datetime.now().year,
        "app_version": app.config.get("APP_VERSION", "3.4.0"),
        "current_lang": lang,
        "t": lambda text: t(text, lang),
        "cat_name": lambda name: category_name(name, lang),
        "cat_desc": lambda name, desc: category_description(name, desc, lang),
        "csrf_token": _ensure_csrf_token(),
    }


@app.before_request
def require_login():
    g.request_id = (request.headers.get("X-Request-ID") or "").strip() or str(uuid.uuid4())
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not request.path.startswith("/static"):
        expected = session.get("csrf_token")
        provided = (request.form.get("csrf_token") or request.headers.get("X-CSRF-Token") or "").strip()
        if not expected or not provided or not secrets.compare_digest(expected, provided):
            logger.warning("csrf_invalid", extra={"event": "csrf_invalid", "ip": request.remote_addr})
            return "Invalid CSRF token", 400

    g.request_started_at = time.time()
    try:
        maybe_run_scheduled_backup()
    except Exception as exc:
        logger.warning("scheduled_backup_check_failed error=%s", exc)
    public_paths = {
        "/login",
        "/register",
        "/setup",
        "/setup/use-existing",
        "/setup/create-new",
        "/setup/test-connection",
        "/health/live",
        "/health/ready",
    }
    if request.path.startswith("/static"):
        return None
    if request.path in public_paths:
        return None
    if not is_app_initialized():
        return redirect(url_for("setup.setup_page"))
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    role = session.get("role")
    if request.path.startswith("/management/backups") and role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if request.path.startswith("/management") and role not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    if request.path.startswith("/categories") and session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    return None


@app.after_request
def log_request(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if _is_https_request():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    elapsed_ms = int((time.time() - getattr(g, "request_started_at", time.time())) * 1000)
    logger.info(
        "request",
        extra={
            "event": "request",
            "status": response.status_code,
            "duration_ms": elapsed_ms,
            "ip": request.remote_addr,
        },
    )
    response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
    return response


@app.errorhandler(429)
def handle_ratelimit(_err):
    logger.warning("rate_limited path=%s ip=%s", request.path, request.remote_addr)
    return t("Too many attempts. Please wait and try again."), 429


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    if isinstance(err, HTTPException):
        return err
    logger.exception("unhandled_exception")
    request_id = getattr(g, "request_id", "-")
    if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
        return {"error": "Internal server error", "request_id": request_id}, 500
    return (
        render_template(
            "error.html",
            title=t("Something went wrong"),
            message=t("An unexpected error occurred. Please try again."),
            request_id=request_id,
        ),
        500,
    )


@app.get("/health/live")
def health_live():
    return {"status": "ok"}, 200


@app.get("/health/ready")
def health_ready():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"status": "ready"}, 200
    except Exception:
        logger.exception("health_ready_failed")
        return {"status": "not_ready"}, 503


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
