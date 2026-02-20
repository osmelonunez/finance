import os
import socket
import logging
import json
import base64
from urllib.parse import urlparse

import psycopg2
from cryptography.fernet import Fernet, InvalidToken

from migrations import apply_migrations

logger = logging.getLogger("finance.db")
DEFAULT_DB_CONFIG_ENCRYPTION_KEY = "change-this-db-config-key"
APP_CONFIG_PATH = os.environ.get(
    "APP_CONFIG_PATH",
    os.path.join(os.path.dirname(__file__), ".app_config.json"),
)


def _read_app_config():
    if not os.path.exists(APP_CONFIG_PATH):
        return {}
    try:
        with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _config_cipher():
    key = (os.environ.get("DB_CONFIG_ENCRYPTION_KEY") or "").strip()
    if not key:
        return None
    try:
        candidate = key.encode("utf-8")
        if len(candidate) != 44:
            candidate = base64.urlsafe_b64encode(candidate[:32].ljust(32, b"0"))
        return Fernet(candidate)
    except Exception:
        logger.warning("db_config_cipher_invalid")
        return None


def _decrypt_value(enc_value: str) -> str:
    if not enc_value:
        return ""
    cipher = _config_cipher()
    if not cipher:
        return ""
    try:
        return cipher.decrypt(enc_value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        logger.warning("db_config_decrypt_failed")
        return ""


def _encrypt_value(raw_value: str) -> str:
    if not raw_value:
        return ""
    cipher = _config_cipher()
    if not cipher:
        return ""
    return cipher.encrypt(raw_value.encode("utf-8")).decode("utf-8")


def _read_config_value(data: dict, plain_key: str, encrypted_key: str) -> str:
    encrypted_value = (data.get(encrypted_key) or "").strip()
    if encrypted_value:
        decrypted = _decrypt_value(encrypted_value)
        if decrypted:
            return decrypted
    return (data.get(plain_key) or "").strip()


def get_database_url():
    env_url = os.environ.get("DATABASE_URL", "").strip()
    if env_url:
        return env_url
    data = _read_app_config()
    file_url = _read_config_value(data, "database_url", "database_url_encrypted")
    if file_url:
        return file_url
    return ""


def get_previous_database_url():
    data = _read_app_config()
    return _read_config_value(data, "previous_database_url", "previous_database_url_encrypted")


def set_database_url(database_url, previous_database_url=None):
    payload = _read_app_config()
    current_url = (database_url or "").strip()
    encrypted_current = _encrypt_value(current_url)
    if encrypted_current:
        payload["database_url_encrypted"] = encrypted_current
        payload.pop("database_url", None)
    else:
        payload["database_url"] = current_url
        payload.pop("database_url_encrypted", None)
    if previous_database_url is not None:
        previous_url = (previous_database_url or "").strip()
        encrypted_previous = _encrypt_value(previous_url)
        if encrypted_previous:
            payload["previous_database_url_encrypted"] = encrypted_previous
            payload.pop("previous_database_url", None)
        else:
            payload["previous_database_url"] = previous_url
            payload.pop("previous_database_url_encrypted", None)
    config_dir = os.path.dirname(APP_CONFIG_PATH)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    # Restrict config file to owner read/write only.
    try:
        os.chmod(APP_CONFIG_PATH, 0o600)
    except OSError:
        pass


def has_database_url():
    return bool(get_database_url())


def get_db():
    db_url = get_database_url()
    if not db_url:
        raise RuntimeError("Database URL is not configured. Run setup wizard first.")
    return psycopg2.connect(db_url)


def is_app_initialized():
    if not has_database_url():
        return False
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name='settings'")
                if not cur.fetchone():
                    return False
                cur.execute("SELECT COALESCE(value,0) FROM settings WHERE key='app_initialized'")
                row = cur.fetchone()
                return bool(row and float(row[0]) >= 1)
    except Exception:
        return False


def _log_db_connection(conn):
    db_url = get_database_url()
    parsed = urlparse(db_url)
    host = parsed.hostname or "unknown"
    resolved_ip = "unknown"
    db_name = "unknown"

    try:
        resolved_ip = socket.gethostbyname(host)
    except OSError:
        pass

    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), COALESCE(inet_server_addr()::text, '')")
        row = cur.fetchone()
        if row:
            db_name = row[0] or db_name
            server_ip = row[1] or ""
            if server_ip:
                resolved_ip = server_ip

    logger.info(
        "db_connection_ok host=%s ip=%s db=%s",
        host,
        resolved_ip,
        db_name,
    )


def init_db():
    if not has_database_url():
        logger.info("init_db_skipped reason=no_database_url_configured")
        return
    try:
        conn = get_db()
    except psycopg2.OperationalError as exc:
        message = str(exc)
        if "does not exist" in message.lower():
            raise RuntimeError(
                "Database does not exist. Create it first and restart the application."
            ) from exc
        raise

    with conn:
        logger.info("init_db_start")
        _log_db_connection(conn)
        apply_migrations(conn)
        logger.info("init_db_done")
