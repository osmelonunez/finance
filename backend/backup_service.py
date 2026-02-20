import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from db import get_db, get_database_url

logger = logging.getLogger("finance.backups")

_SCHED_LOCK = threading.Lock()
_LAST_SCHED_CHECK = 0.0
_SCHED_CHECK_INTERVAL_SECONDS = 300

_WEEKDAYS = {
    "0": "Monday",
    "1": "Tuesday",
    "2": "Wednesday",
    "3": "Thursday",
    "4": "Friday",
    "5": "Saturday",
    "6": "Sunday",
}


def _backup_dir() -> Path:
    return Path(os.environ.get("BACKUP_DIR", "/backups")).resolve()


def _now() -> datetime:
    return datetime.now()


def get_backup_config(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT frequency, weekly_day, retain_count, last_run_at, last_cleanup_at
            FROM backup_config
            WHERE id=1
            """
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                """
                INSERT INTO backup_config (id, frequency, weekly_day, retain_count)
                VALUES (1, 'daily', 0, 7)
                """
            )
            conn.commit()
            return {
                "frequency": "daily",
                "weekly_day": 0,
                "retain_count": 7,
                "last_run_at": None,
                "last_cleanup_at": None,
            }
    return {
        "frequency": row[0],
        "weekly_day": int(row[1]),
        "retain_count": int(row[2]),
        "last_run_at": row[3],
        "last_cleanup_at": row[4],
    }


def update_backup_config(conn, frequency, weekly_day, retain_count):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE backup_config
            SET frequency=%s, weekly_day=%s, retain_count=%s, updated_at=NOW()
            WHERE id=1
            """,
            (frequency, weekly_day, retain_count),
        )
    conn.commit()


def _is_due(config, now_dt):
    last_run_at = config.get("last_run_at")
    last_run_date = last_run_at.date() if last_run_at else None
    today = now_dt.date()
    frequency = config.get("frequency", "daily")

    if last_run_date == today:
        return False

    if frequency == "daily":
        return True

    if frequency == "weekly":
        return now_dt.weekday() == int(config.get("weekly_day", 0))

    if frequency == "monthly_last_day":
        tomorrow = today + timedelta(days=1)
        return tomorrow.day == 1

    return False


def _cleanup_old_backups(retain_count):
    backup_dir = _backup_dir()
    files = sorted(
        [*backup_dir.glob("*.sql"), *backup_dir.glob("*.dump")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    deleted_names = []
    for old in files[retain_count:]:
        try:
            old.unlink(missing_ok=True)
            logger.info("backup_prune file=%s", old.name)
            deleted_names.append(old.name)
        except OSError as exc:
            logger.warning("backup_prune_failed file=%s error=%s", old.name, exc)
    return deleted_names


def _cleanup_old_backup_runs(conn, deleted_names, retain_count):
    with conn.cursor() as cur:
        if deleted_names:
            cur.execute(
                "DELETE FROM backup_runs WHERE filename = ANY(%s)",
                (deleted_names,),
            )
        # Remove success rows whose file has already been deleted/unavailable.
        cur.execute(
            """
            SELECT id, file_path
            FROM backup_runs
            WHERE status='success'
              AND file_path IS NOT NULL
              AND file_path <> ''
            """
        )
        rows = cur.fetchall()
        stale_ids = []
        for run_id, file_path in rows:
            if not Path(file_path).is_file():
                stale_ids.append(run_id)
        if stale_ids:
            cur.execute("DELETE FROM backup_runs WHERE id = ANY(%s)", (stale_ids,))

        # Enforce keep policy also in DB table: keep only newest N successful backups.
        cur.execute(
            """
            SELECT id
            FROM backup_runs
            WHERE status='success'
              AND filename IS NOT NULL
            ORDER BY created_at DESC, id DESC
            OFFSET %s
            """,
            (retain_count,),
        )
        old_success_ids = [r[0] for r in cur.fetchall()]
        if old_success_ids:
            cur.execute("DELETE FROM backup_runs WHERE id = ANY(%s)", (old_success_ids,))

        cur.execute(
            """
            DELETE FROM backup_runs
            WHERE status='success'
              AND filename IS NOT NULL
              AND (file_path IS NULL OR file_path = '')
            """
        )
    conn.commit()


def _run_pg_dump(destination: Path):
    db_url = get_database_url()
    parsed = urlparse(db_url)
    if not parsed.hostname or not parsed.username:
        raise RuntimeError("Database connection is incomplete for backup.")
    db_name = (parsed.path or "").lstrip("/")
    if not db_name:
        raise RuntimeError("Database connection does not include database name.")

    env = os.environ.copy()
    env["PGPASSWORD"] = parsed.password or ""

    cmd = [
        "pg_dump",
        "-h",
        parsed.hostname,
        "-p",
        str(parsed.port or 5432),
        "-U",
        parsed.username,
        "-d",
        db_name,
        "--no-owner",
        "--no-privileges",
        "-f",
        str(destination),
    ]
    subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)


def _run_pg_restore(source: Path):
    db_url = get_database_url()
    parsed = urlparse(db_url)
    if not parsed.hostname or not parsed.username:
        raise RuntimeError("Database connection is incomplete for restore.")
    db_name = (parsed.path or "").lstrip("/")
    if not db_name:
        raise RuntimeError("Database connection does not include database name.")

    env = os.environ.copy()
    env["PGPASSWORD"] = parsed.password or ""

    if source.suffix.lower() == ".sql":
        cmd = [
            "psql",
            "-h",
            parsed.hostname,
            "-p",
            str(parsed.port or 5432),
            "-U",
            parsed.username,
            "-d",
            db_name,
            "-v",
            "ON_ERROR_STOP=1",
            "-f",
            str(source),
        ]
    else:
        cmd = [
            "pg_restore",
            "-h",
            parsed.hostname,
            "-p",
            str(parsed.port or 5432),
            "-U",
            parsed.username,
            "-d",
            db_name,
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            str(source),
        ]
    subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)


def _record_run(conn, trigger, status, created_by, filename=None, file_path=None, size_bytes=None, message=None):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO backup_runs (trigger, filename, file_path, size_bytes, status, message, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (trigger, filename, file_path, size_bytes, status, message, created_by),
        )
    conn.commit()


def run_backup(trigger="manual", created_by=None):
    backup_dir = _backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)
    now_dt = _now()
    filename = f"finance_{now_dt.strftime('%Y%m%d_%H%M%S')}.sql"
    destination = backup_dir / filename

    with get_db() as conn:
        config = get_backup_config(conn)
        try:
            _run_pg_dump(destination)
            size_bytes = destination.stat().st_size
            deleted_names = _cleanup_old_backups(config["retain_count"])
            _cleanup_old_backup_runs(conn, deleted_names, config["retain_count"])
            with conn.cursor() as cur:
                cur.execute("UPDATE backup_config SET last_run_at=NOW(), updated_at=NOW() WHERE id=1")
            conn.commit()
            _record_run(
                conn,
                trigger=trigger,
                status="success",
                created_by=created_by,
                filename=filename,
                file_path=str(destination),
                size_bytes=size_bytes,
                message="Backup created successfully.",
            )
            logger.info("backup_success trigger=%s file=%s size_bytes=%s", trigger, filename, size_bytes)
            return True, filename, "Backup created successfully."
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            message = stderr or "pg_dump failed."
            _record_run(
                conn,
                trigger=trigger,
                status="failed",
                created_by=created_by,
                message=message[:1000],
            )
            logger.error("backup_failed trigger=%s error=%s", trigger, message)
            return False, None, message
        except Exception as exc:  # pragma: no cover
            _record_run(
                conn,
                trigger=trigger,
                status="failed",
                created_by=created_by,
                message=str(exc)[:1000],
            )
            logger.error("backup_failed trigger=%s error=%s", trigger, exc)
            return False, None, str(exc)


def maybe_run_scheduled_backup():
    global _LAST_SCHED_CHECK
    now_monotonic = time.monotonic()
    if now_monotonic - _LAST_SCHED_CHECK < _SCHED_CHECK_INTERVAL_SECONDS:
        return

    with _SCHED_LOCK:
        now_monotonic = time.monotonic()
        if now_monotonic - _LAST_SCHED_CHECK < _SCHED_CHECK_INTERVAL_SECONDS:
            return
        _LAST_SCHED_CHECK = now_monotonic

    with get_db() as conn:
        config = get_backup_config(conn)
        now_dt = _now()
        # Retention cleanup every day at 00:00 (first request after midnight).
        last_cleanup = config.get("last_cleanup_at")
        if now_dt.hour == 0 and (not last_cleanup or last_cleanup.date() < now_dt.date()):
            deleted_names = _cleanup_old_backups(config["retain_count"])
            _cleanup_old_backup_runs(conn, deleted_names, config["retain_count"])
            with conn.cursor() as cur:
                cur.execute("UPDATE backup_config SET last_cleanup_at=NOW(), updated_at=NOW() WHERE id=1")
            conn.commit()
            logger.info("backup_daily_cleanup_done deleted_files=%s", len(deleted_names))

        if _is_due(config, now_dt):
            run_backup(trigger="scheduled", created_by="system")


def read_backup_page_data():
    with get_db() as conn:
        config = get_backup_config(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, trigger, filename, size_bytes, status, message, created_by, created_at
                FROM backup_runs
                ORDER BY id DESC
                LIMIT 50
                """
            )
            runs = cur.fetchall()
            cur.execute(
                """
                SELECT filename, file_path, created_at
                FROM backup_runs
                WHERE status='success' AND filename IS NOT NULL
                ORDER BY id DESC
                LIMIT 1
                """
            )
            latest = cur.fetchone()
    return config, runs, latest


def week_day_options():
    return _WEEKDAYS


def enforce_keep_cleanup_now():
    with get_db() as conn:
        config = get_backup_config(conn)
        deleted_names = _cleanup_old_backups(config["retain_count"])
        _cleanup_old_backup_runs(conn, deleted_names, config["retain_count"])
        with conn.cursor() as cur:
            cur.execute("UPDATE backup_config SET updated_at=NOW() WHERE id=1")
        conn.commit()
    logger.info("backup_keep_cleanup_now retain=%s deleted_files=%s", config["retain_count"], len(deleted_names))
    return len(deleted_names)


def get_backup_file_for_run(run_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, file_path, status
                FROM backup_runs
                WHERE id=%s
                """,
                (run_id,),
            )
            row = cur.fetchone()
    return row


def restore_backup(run_id: int, restored_by=None):
    run = get_backup_file_for_run(run_id)
    if not run:
        return False, "Backup run not found."
    _, filename, file_path, status = run
    if status != "success" or not filename or not file_path:
        return False, "Selected backup is not restorable."
    source = Path(file_path)
    if not source.is_file():
        return False, "Backup file not found on disk."

    with get_db() as conn:
        try:
            _run_pg_restore(source)
            _record_run(
                conn,
                trigger="restore",
                status="success",
                created_by=restored_by,
                filename=filename,
                file_path=str(source),
                size_bytes=source.stat().st_size,
                message=f"Database restored from backup run {run_id}.",
            )
            logger.info("backup_restore_success run_id=%s file=%s", run_id, filename)
            return True, "Backup restored successfully."
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            message = stderr or "pg_restore failed."
            _record_run(
                conn,
                trigger="restore",
                status="failed",
                created_by=restored_by,
                filename=filename,
                file_path=str(source),
                size_bytes=source.stat().st_size if source.exists() else None,
                message=message[:1000],
            )
            logger.error("backup_restore_failed run_id=%s error=%s", run_id, message)
            return False, message


def delete_backup_file(run_id: int, deleted_by=None):
    row = get_backup_file_for_run(run_id)
    if not row:
        return False, "Backup run not found."

    _, filename, file_path, _status = row
    if not file_path:
        return False, "Backup file already removed."

    target = Path(file_path)
    try:
        if target.is_file():
            target.unlink()
    except OSError as exc:
        logger.error("backup_delete_failed run_id=%s file=%s error=%s", run_id, file_path, exc)
        return False, f"Could not delete backup file: {exc}"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM backup_runs WHERE id=%s", (run_id,))
        conn.commit()

    logger.info("backup_delete_success run_id=%s file=%s by=%s", run_id, filename, deleted_by or "unknown")
    return True, "Backup file deleted."
