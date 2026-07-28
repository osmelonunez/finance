import os
import socket
import logging
from urllib.parse import urlparse

import psycopg2

from migrations import apply_migrations

logger = logging.getLogger("finance.db")


def get_database_url():
    return (os.environ.get("DATABASE_URL") or "").strip()


def has_database_url():
    return bool(get_database_url())


def get_db():
    db_url = get_database_url()
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured.")
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
