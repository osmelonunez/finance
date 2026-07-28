import hashlib
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from db import get_db, get_database_url

logger = logging.getLogger("finance.backups")

_LOCK_KEY = 372021700
_WEEKDAYS = {str(index): day for index, day in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))}


def _backup_dir() -> Path:
    return Path(os.environ.get("BACKUP_DIR", "/backups")).resolve()


def _managed_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(_backup_dir()):
        raise ValueError("Backup file is outside the managed backup directory.")
    return resolved


def _now() -> datetime:
    return datetime.now()


def _checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _try_lock(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s)", (_LOCK_KEY,))
        return bool(cur.fetchone()[0])


def _unlock(conn) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (_LOCK_KEY,))
    except Exception:
        logger.warning("backup_lock_release_failed", exc_info=True)


def get_backup_config(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT frequency, weekly_day, retain_days,
                   last_run_at, last_cleanup_at
            FROM backup_config WHERE id=1
            """
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                """
                INSERT INTO backup_config
                    (id, frequency, weekly_day, retain_days)
                VALUES (1, 'daily', 0, 7)
                """
            )
            conn.commit()
            return {"frequency": "daily", "weekly_day": 0, "retain_days": 7, "last_run_at": None,
                    "last_cleanup_at": None}
    return {"frequency": row[0], "weekly_day": int(row[1]), "retain_days": int(row[2]),
            "last_run_at": row[3], "last_cleanup_at": row[4]}


def update_backup_config(conn, frequency, weekly_day, retain_days):
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE backup_config
               SET frequency=%s, weekly_day=%s, retain_days=%s, updated_at=NOW() WHERE id=1""",
            (frequency, weekly_day, retain_days),
        )
    conn.commit()


def _is_due(config, now_dt):
    last_run = config.get("last_run_at")
    if last_run and last_run.date() == now_dt.date():
        return False
    if config.get("frequency") == "weekly":
        return now_dt.weekday() == int(config.get("weekly_day", 0))
    if config.get("frequency") == "monthly_last_day":
        return (now_dt.date() + timedelta(days=1)).day == 1
    return True


def _backup_files():
    root = _backup_dir()
    if not root.exists():
        return []
    return sorted((path for path in root.rglob("*.dump") if path.is_file() and _managed_path(path)),
                  key=lambda path: path.stat().st_mtime, reverse=True)


def _cleanup_old_backups(config, now_dt=None):
    now_dt = now_dt or _now()
    keep = set()
    for path in _backup_files():
        created = datetime.fromtimestamp(path.stat().st_mtime)
        if 0 <= (now_dt.date() - created.date()).days < config["retain_days"]:
            keep.add(path)
    deleted = []
    for path in _backup_files():
        if path in keep:
            continue
        try:
            path.unlink()
            deleted.append(str(path))
            logger.info("backup_prune file=%s", path.name)
        except OSError as exc:
            logger.warning("backup_prune_failed file=%s error=%s", path.name, exc)
    return deleted


def _cleanup_old_backup_runs(conn, deleted_paths):
    with conn.cursor() as cur:
        if deleted_paths:
            cur.execute("DELETE FROM backup_runs WHERE file_path = ANY(%s)", (deleted_paths,))
        cur.execute("SELECT id, file_path FROM backup_runs WHERE status='success' AND file_path IS NOT NULL")
        stale = [row[0] for row in cur.fetchall() if not Path(row[1]).is_file()]
        if stale:
            cur.execute("DELETE FROM backup_runs WHERE id = ANY(%s)", (stale,))
    conn.commit()


def _pg_connection_parts():
    parsed = urlparse(get_database_url())
    db_name = (parsed.path or "").lstrip("/")
    if not parsed.hostname or not parsed.username or not db_name:
        raise RuntimeError("Database connection is incomplete for backup.")
    environment = os.environ.copy()
    environment["PGPASSWORD"] = parsed.password or ""
    return parsed, db_name, environment


def _run_pg_dump(destination: Path):
    parsed, db_name, environment = _pg_connection_parts()
    subprocess.run([
        "pg_dump", "-h", parsed.hostname, "-p", str(parsed.port or 5432), "-U", parsed.username,
        "-d", db_name, "--format=custom", "--no-owner", "--no-privileges", "-f", str(destination),
    ], check=True, env=environment, capture_output=True, text=True)


def _verify_dump(source: Path):
    if source.suffix.lower() != ".dump":
        raise ValueError("Only verified .dump backups can be restored.")
    parsed, _db_name, environment = _pg_connection_parts()
    subprocess.run(["pg_restore", "--list", str(source)], check=True, env=environment,
                   capture_output=True, text=True)


def _run_pg_restore(source: Path):
    _verify_dump(source)
    parsed, db_name, environment = _pg_connection_parts()
    subprocess.run([
        "pg_restore", "-h", parsed.hostname, "-p", str(parsed.port or 5432), "-U", parsed.username,
        "-d", db_name, "--clean", "--if-exists", "--no-owner", "--no-privileges", str(source),
    ], check=True, env=environment, capture_output=True, text=True)


def _record_run(conn, trigger, status, created_by, filename=None, file_path=None, size_bytes=None,
                checksum_sha256=None, message=None):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO backup_runs
                (trigger, filename, file_path, size_bytes, checksum_sha256, status, message, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (trigger, filename, file_path, size_bytes, checksum_sha256, status, message, created_by),
        )
    conn.commit()


def _create_backup_locked(conn, trigger, created_by):
    backup_dir = _backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)
    destination = backup_dir / f"finance_{_now().strftime('%Y%m%d_%H%M%S')}.dump"
    _run_pg_dump(destination)
    _verify_dump(destination)
    size = destination.stat().st_size
    digest = _checksum(destination)
    config = get_backup_config(conn)
    _record_run(conn, trigger, "success", created_by, destination.name, str(destination), size, digest,
                "Backup created and verified.")
    deleted = _cleanup_old_backups(config)
    _cleanup_old_backup_runs(conn, deleted)
    return destination


def run_backup(trigger="manual", created_by=None):
    with get_db() as conn:
        if not _try_lock(conn):
            return False, None, "Another backup or restore operation is already running."
        try:
            destination = _create_backup_locked(conn, trigger, created_by)
            with conn.cursor() as cur:
                cur.execute("UPDATE backup_config SET last_run_at=NOW(), updated_at=NOW() WHERE id=1")
            conn.commit()
            logger.info("backup_success trigger=%s file=%s", trigger, destination.name)
            return True, destination.name, "Backup created and verified."
        except Exception as exc:
            _record_run(conn, trigger, "failed", created_by, message=str(exc)[:1000])
            logger.exception("backup_failed trigger=%s", trigger)
            return False, None, str(exc)
        finally:
            _unlock(conn)


def run_scheduled_backup_cycle(now_dt=None):
    now_dt = now_dt or _now()
    with get_db() as conn:
        config = get_backup_config(conn)
        if config.get("last_cleanup_at") is None or config["last_cleanup_at"].date() < now_dt.date():
            deleted = _cleanup_old_backups(config, now_dt)
            _cleanup_old_backup_runs(conn, deleted)
            with conn.cursor() as cur:
                cur.execute("UPDATE backup_config SET last_cleanup_at=NOW(), updated_at=NOW() WHERE id=1")
            conn.commit()
        due = _is_due(config, now_dt)
    if due:
        return run_backup(trigger="scheduled", created_by="system")
    return True, None, "Backup is not due today."


def read_backup_page_data():
    with get_db() as conn:
        config = get_backup_config(conn)
        with conn.cursor() as cur:
            cur.execute("""SELECT id, trigger, filename, size_bytes, status, message, created_by, created_at,
                                  checksum_sha256
                           FROM backup_runs ORDER BY id DESC LIMIT 50""")
            runs = cur.fetchall()
            cur.execute("""SELECT filename, file_path, created_at FROM backup_runs
                           WHERE status='success' AND filename IS NOT NULL ORDER BY id DESC LIMIT 1""")
            latest = cur.fetchone()
    return config, runs, latest


def week_day_options():
    return _WEEKDAYS


def enforce_keep_cleanup_now():
    with get_db() as conn:
        config = get_backup_config(conn)
        deleted = _cleanup_old_backups(config)
        _cleanup_old_backup_runs(conn, deleted)
        return len(deleted)


def get_backup_file_for_run(run_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, filename, file_path, status, checksum_sha256 FROM backup_runs WHERE id=%s", (run_id,))
            return cur.fetchone()


def import_backup(upload, uploaded_by=None):
    filename = Path(upload.filename or "").name
    if not filename.lower().endswith(".dump"):
        return False, "Only .dump backup files can be uploaded."
    max_bytes = int(os.environ.get("BACKUP_MAX_UPLOAD_MB", "512")) * 1024 * 1024
    target_dir = _backup_dir() / "imported"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"uploaded_{_now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}.dump"
    size = 0
    digest = hashlib.sha256()
    try:
        with target.open("wb") as destination:
            while chunk := upload.stream.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError(f"Backup exceeds the {max_bytes // 1048576} MB upload limit.")
                digest.update(chunk)
                destination.write(chunk)
        _verify_dump(target)
        with get_db() as conn:
            _record_run(conn, "upload", "success", uploaded_by, filename, str(target), size,
                        digest.hexdigest(), "Uploaded backup verified and ready to restore.")
        return True, "Backup uploaded and verified."
    except Exception as exc:
        target.unlink(missing_ok=True)
        logger.warning("backup_upload_failed error=%s", exc)
        return False, str(exc)


def restore_backup(run_id: int, restored_by=None):
    run = get_backup_file_for_run(run_id)
    if not run:
        return False, "Backup run not found."
    _, filename, file_path, status, expected_checksum = run
    if status != "success" or not filename or not file_path:
        return False, "Selected backup is not restorable."
    source = _managed_path(Path(file_path))
    if not source.is_file():
        return False, "Backup file not found on disk."
    if expected_checksum and _checksum(source) != expected_checksum:
        return False, "Backup integrity check failed. The file has changed since verification."

    with get_db() as lock_conn:
        if not _try_lock(lock_conn):
            return False, "Another backup or restore operation is already running."
        try:
            # A recoverable rollback point is always made immediately before a destructive restore.
            emergency = _backup_dir() / f"pre_restore_{_now().strftime('%Y%m%d_%H%M%S')}.dump"
            _run_pg_dump(emergency)
            _verify_dump(emergency)
            _run_pg_restore(source)
        except Exception as exc:
            logger.exception("backup_restore_failed run_id=%s", run_id)
            return False, str(exc)
        finally:
            _unlock(lock_conn)

    # The restore replaced the database, so record the audit event through a fresh connection.
    with get_db() as conn:
        _record_run(conn, "pre_restore", "success", restored_by, emergency.name, str(emergency),
                    emergency.stat().st_size, _checksum(emergency), "Automatic safety backup before restore.")
        _record_run(conn, "restore", "success", restored_by, filename, str(source), source.stat().st_size,
                    _checksum(source), f"Database restored from backup run {run_id}.")
    logger.info("backup_restore_success run_id=%s file=%s", run_id, filename)
    return True, "Backup restored successfully. A safety backup was created first."


def delete_backup_file(run_id: int, deleted_by=None):
    row = get_backup_file_for_run(run_id)
    if not row:
        return False, "Backup run not found."
    _, filename, file_path, _status, _checksum_value = row
    if not file_path:
        return False, "Backup file already removed."
    try:
        target = _managed_path(Path(file_path))
        target.unlink(missing_ok=True)
    except (OSError, ValueError) as exc:
        logger.error("backup_delete_failed run_id=%s error=%s", run_id, exc)
        return False, f"Could not delete backup file: {exc}"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM backup_runs WHERE id=%s", (run_id,))
        conn.commit()
    logger.info("backup_delete_success run_id=%s file=%s by=%s", run_id, filename, deleted_by or "unknown")
    return True, "Backup file deleted."
