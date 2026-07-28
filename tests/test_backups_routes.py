from io import BytesIO

import pytest
from routes import backups as backup_routes


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data=None):
    return client.post(path, data={"csrf_token": "test-csrf-token", **(data or {})}, follow_redirects=False)


def test_backup_page_and_config_validation(admin_client, monkeypatch):
    response = admin_client.get("/management/backups")
    assert response.status_code == 200
    assert b"Conservar copias" in response.data

    captured = {}
    monkeypatch.setattr(backup_routes, "update_backup_config", lambda _conn, *values: captured.update(values=values))
    monkeypatch.setattr(backup_routes, "enforce_keep_cleanup_now", lambda: 2)
    response = _post(admin_client, "/management/backups/config", {"frequency": "invalid", "weekly_day": "99", "retain_days": "999"})
    assert response.status_code == 302
    assert captured["values"] == ("daily", 6, 365)
    response = _post(admin_client, "/management/backups/config", {"frequency": "weekly", "weekly_day": "x", "retain_days": "x"})
    assert response.status_code == 302
    assert captured["values"] == ("weekly", 0, 7)


def test_backup_run_upload_restore_and_delete_routes(admin_client, monkeypatch):
    monkeypatch.setattr(backup_routes, "run_backup", lambda **_kwargs: (True, "test.dump", "ok"))
    assert _post(admin_client, "/management/backups/run-now").status_code == 302
    monkeypatch.setattr(backup_routes, "run_backup", lambda **_kwargs: (False, None, "failed"))
    assert _post(admin_client, "/management/backups/run-now").status_code == 302

    assert _post(admin_client, "/management/backups/upload").status_code == 302
    monkeypatch.setattr(backup_routes, "import_backup", lambda *_args, **_kwargs: (True, "verified"))
    response = admin_client.post(
        "/management/backups/upload",
        data={"csrf_token": "test-csrf-token", "backup_file": (BytesIO(b"dump"), "device.dump")},
        follow_redirects=False,
    )
    assert response.status_code == 302
    monkeypatch.setattr(backup_routes, "import_backup", lambda *_args, **_kwargs: (False, "invalid dump"))
    response = admin_client.post(
        "/management/backups/upload",
        data={"csrf_token": "test-csrf-token", "backup_file": (BytesIO(b"dump"), "device.dump")},
        follow_redirects=False,
    )
    assert response.status_code == 302

    invalidated = []
    monkeypatch.setattr(backup_routes, "restore_backup", lambda *_args, **_kwargs: (True, "restored"))
    monkeypatch.setattr(backup_routes, "invalidate_dashboard_cache", lambda: invalidated.append(True))
    assert _post(admin_client, "/management/backups/restore/1").status_code == 302
    assert invalidated == [True]
    monkeypatch.setattr(backup_routes, "restore_backup", lambda *_args, **_kwargs: (False, "restore failed"))
    assert _post(admin_client, "/management/backups/restore/1").status_code == 302
    monkeypatch.setattr(backup_routes, "delete_backup_file", lambda *_args, **_kwargs: (False, "cannot delete"))
    assert _post(admin_client, "/management/backups/delete/1").status_code == 302
    monkeypatch.setattr(backup_routes, "delete_backup_file", lambda *_args, **_kwargs: (True, "deleted"))
    assert _post(admin_client, "/management/backups/delete/1").status_code == 302


def test_backup_download_routes_handle_missing_and_available_files(admin_client, monkeypatch, tmp_path):
    monkeypatch.setattr(backup_routes, "read_backup_page_data", lambda: ({}, [], None))
    assert admin_client.get("/management/backups/download-latest").status_code == 302

    path = tmp_path / "available.dump"
    path.write_bytes(b"dump")
    monkeypatch.setattr(backup_routes, "read_backup_page_data", lambda: ({}, [], (path.name, str(path), None)))
    response = admin_client.get("/management/backups/download-latest")
    assert response.status_code == 200
    assert response.data == b"dump"

    monkeypatch.setattr(backup_routes, "get_backup_file_for_run", lambda _id: None)
    assert admin_client.get("/management/backups/download/10").status_code == 302
    monkeypatch.setattr(backup_routes, "get_backup_file_for_run", lambda _id: (1, "missing.dump", None, "failed", None))
    assert admin_client.get("/management/backups/download/1").status_code == 302
    monkeypatch.setattr(backup_routes, "get_backup_file_for_run", lambda _id: (1, "missing.dump", str(tmp_path / "missing.dump"), "success", None))
    assert admin_client.get("/management/backups/download/1").status_code == 302
    monkeypatch.setattr(backup_routes, "get_backup_file_for_run", lambda _id: (1, path.name, str(path), "success", None))
    assert admin_client.get("/management/backups/download/1").status_code == 200
