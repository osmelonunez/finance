from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import backup_service
import pytest
from werkzeug.datastructures import FileStorage


pytestmark = pytest.mark.integration


def test_run_backup_creates_verified_custom_dump(db_query, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))

    def fake_dump(destination):
        destination.write_bytes(b"custom dump")

    monkeypatch.setattr(backup_service, "_run_pg_dump", fake_dump)
    monkeypatch.setattr(backup_service, "_verify_dump", lambda _path: None)

    ok, filename, _message = backup_service.run_backup(created_by="admin_test")

    assert ok is True
    assert filename.endswith(".dump")
    assert (tmp_path / filename).is_file()
    rows = db_query("SELECT trigger, status, checksum_sha256 FROM backup_runs WHERE filename=%s", (filename,), fetch="all")
    assert rows == [("manual", "success", backup_service._checksum(tmp_path / filename))]


def test_retention_keeps_only_backups_created_within_configured_days(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    now = datetime(2026, 7, 27, 0, 0)
    files = []
    for days_ago in (0, 1, 2, 36, 100):
        path = tmp_path / f"finance_{days_ago}.dump"
        path.write_bytes(b"dump")
        timestamp = (now - timedelta(days=days_ago)).timestamp()
        path.touch()
        import os
        os.utime(path, (timestamp, timestamp))
        files.append(path)

    deleted = backup_service._cleanup_old_backups(
        {"retain_days": 2}, now
    )

    assert str(files[-1]) in deleted
    assert files[0].is_file()
    assert files[1].is_file()
    assert not files[2].exists()


def test_restore_rejects_changed_backup_before_running_restore(db_query, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    path = tmp_path / "finance_test.dump"
    path.write_bytes(b"original")
    digest = backup_service._checksum(path)
    db_query(
        """INSERT INTO backup_runs (trigger, filename, file_path, size_bytes, checksum_sha256, status)
           VALUES ('manual', %s, %s, %s, %s, 'success')""",
        (path.name, str(path), path.stat().st_size, digest), fetch="none",
    )
    run_id = db_query("SELECT MAX(id) FROM backup_runs")[0]
    path.write_bytes(b"changed")
    called = []
    monkeypatch.setattr(backup_service, "_run_pg_restore", lambda _path: called.append(True))

    ok, message = backup_service.restore_backup(run_id, "admin_test")

    assert ok is False
    assert "integrity" in message.lower()
    assert called == []


def test_schedule_due_rules_cover_daily_weekly_and_month_end():
    monday = datetime(2026, 7, 27)
    assert backup_service._is_due({"frequency": "daily"}, monday) is True
    assert backup_service._is_due({"frequency": "weekly", "weekly_day": 0}, monday) is True
    assert backup_service._is_due({"frequency": "weekly", "weekly_day": 1}, monday) is False
    assert backup_service._is_due({"frequency": "monthly_last_day"}, datetime(2026, 7, 31)) is True
    assert backup_service._is_due({"frequency": "monthly_last_day"}, datetime(2026, 7, 30)) is False
    assert backup_service._is_due({"frequency": "daily", "last_run_at": monday}, monday) is False


def test_import_backup_verifies_and_records_uploaded_file(db_query, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    monkeypatch.setattr(backup_service, "_verify_dump", lambda _path: None)
    upload = FileStorage(stream=BytesIO(b"uploaded dump"), filename="from-device.dump")

    ok, message = backup_service.import_backup(upload, "admin_test")

    assert ok is True
    assert "verified" in message.lower()
    row = db_query(
        "SELECT trigger, filename, status, checksum_sha256 FROM backup_runs WHERE trigger='upload'"
    )
    assert row[:3] == ("upload", "from-device.dump", "success")
    assert len(row[3]) == 64


def test_import_backup_rejects_invalid_extension_and_oversize(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    invalid = FileStorage(stream=BytesIO(b"plain"), filename="backup.sql")
    assert backup_service.import_backup(invalid) == (False, "Only .dump backup files can be uploaded.")

    monkeypatch.setenv("BACKUP_MAX_UPLOAD_MB", "1")
    oversized = FileStorage(stream=BytesIO(b"x" * (1024 * 1024 + 1)), filename="large.dump")
    ok, message = backup_service.import_backup(oversized)
    assert ok is False
    assert "upload limit" in message
    assert not list(tmp_path.rglob("*.dump"))


def test_restore_creates_safety_backup_and_audits_success(db_query, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    source = tmp_path / "source.dump"
    source.write_bytes(b"original")
    digest = backup_service._checksum(source)
    db_query(
        """INSERT INTO backup_runs (trigger, filename, file_path, size_bytes, checksum_sha256, status)
           VALUES ('manual', %s, %s, %s, %s, 'success')""",
        (source.name, str(source), source.stat().st_size, digest), fetch="none",
    )
    run_id = db_query("SELECT MAX(id) FROM backup_runs")[0]

    def fake_dump(destination):
        destination.write_bytes(b"safety")

    restored = []
    monkeypatch.setattr(backup_service, "_run_pg_dump", fake_dump)
    monkeypatch.setattr(backup_service, "_verify_dump", lambda _path: None)
    monkeypatch.setattr(backup_service, "_run_pg_restore", lambda path: restored.append(path))

    ok, message = backup_service.restore_backup(run_id, "admin_test")

    assert ok is True
    assert "safety backup" in message.lower()
    assert restored == [source]
    triggers = db_query(
        "SELECT trigger FROM backup_runs WHERE trigger IN ('pre_restore', 'restore') ORDER BY id",
        fetch="all",
    )
    assert triggers == [("pre_restore",), ("restore",)]


def test_backup_lock_and_delete_protection(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    monkeypatch.setattr(backup_service, "_try_lock", lambda _conn: False)
    assert backup_service.run_backup()[0] is False
    outside = tmp_path.parent / "outside.dump"
    outside.write_bytes(b"outside")
    monkeypatch.setattr(backup_service, "get_backup_file_for_run", lambda _id: (1, "outside.dump", str(outside), "success", None))
    ok, message = backup_service.delete_backup_file(1)
    assert ok is False
    assert "managed backup directory" in message


def test_scheduled_cycle_cleans_then_runs_only_when_due(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    calls = []
    monkeypatch.setattr(backup_service, "_cleanup_old_backups", lambda *_args: calls.append("cleanup") or [])
    monkeypatch.setattr(backup_service, "_cleanup_old_backup_runs", lambda *_args: calls.append("clean-runs"))
    monkeypatch.setattr(backup_service, "run_backup", lambda **kwargs: calls.append(kwargs) or (True, "scheduled.dump", "ok"))

    result = backup_service.run_scheduled_backup_cycle(datetime(2026, 7, 27))

    assert result[0] is True
    assert calls[-1] == {"trigger": "scheduled", "created_by": "system"}


def test_service_read_cleanup_delete_and_failure_paths(db_query, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    kept = tmp_path / "kept.dump"
    kept.write_bytes(b"kept")
    digest = backup_service._checksum(kept)
    db_query(
        """INSERT INTO backup_runs (trigger, filename, file_path, size_bytes, checksum_sha256, status)
           VALUES ('manual', %s, %s, %s, %s, 'success')""",
        (kept.name, str(kept), kept.stat().st_size, digest), fetch="none",
    )
    run_id = db_query("SELECT MAX(id) FROM backup_runs")[0]
    config, runs, latest = backup_service.read_backup_page_data()
    assert config["retain_days"] == 7
    assert any(row[0] == run_id for row in runs)
    assert latest[0] == kept.name
    assert backup_service.week_day_options()["0"] == "Monday"
    assert backup_service.enforce_keep_cleanup_now() == 0
    assert backup_service.delete_backup_file(run_id)[0] is True
    assert not kept.exists()
    assert backup_service.delete_backup_file(999999)[0] is False

    monkeypatch.setattr(backup_service, "_create_backup_locked", lambda *_args: (_ for _ in ()).throw(RuntimeError("dump failed")))
    ok, _filename, message = backup_service.run_backup()
    assert ok is False
    assert "dump failed" in message


def test_restore_rejects_missing_status_file_and_lock(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    assert backup_service.restore_backup(999999)[0] is False
    monkeypatch.setattr(backup_service, "get_backup_file_for_run", lambda _id: (1, "x.dump", None, "success", None))
    assert "not restorable" in backup_service.restore_backup(1)[1]
    missing = tmp_path / "missing.dump"
    monkeypatch.setattr(backup_service, "get_backup_file_for_run", lambda _id: (1, missing.name, str(missing), "success", None))
    assert "not found" in backup_service.restore_backup(1)[1]
    missing.write_bytes(b"dump")
    monkeypatch.setattr(backup_service, "_try_lock", lambda _conn: False)
    assert "already running" in backup_service.restore_backup(1)[1]
