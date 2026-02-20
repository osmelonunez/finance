from pathlib import Path

from flask import Blueprint, redirect, render_template, request, send_file, session, url_for

from backup_service import (
    enforce_keep_cleanup_now,
    delete_backup_file,
    get_backup_file_for_run,
    read_backup_page_data,
    restore_backup,
    run_backup,
    update_backup_config,
    week_day_options,
)
from db import get_db
from i18n import t

backups_bp = Blueprint("backups", __name__)


@backups_bp.route("/management/backups")
def backups_page():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    config, runs, latest = read_backup_page_data()
    message = session.pop("backup_msg", "")
    error = session.pop("backup_err", "")
    return render_template(
        "backups.html",
        current_page="management",
        config=config,
        runs=runs,
        latest=latest,
        week_days=week_day_options(),
        message=message,
        error=error,
    )


@backups_bp.route("/management/backups/config", methods=["POST"])
def backups_update_config():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    frequency = (request.form.get("frequency") or "daily").strip()
    if frequency not in {"daily", "weekly", "monthly_last_day"}:
        frequency = "daily"
    try:
        weekly_day = int(request.form.get("weekly_day", "0"))
    except ValueError:
        weekly_day = 0
    weekly_day = min(max(weekly_day, 0), 6)
    try:
        retain_count = int(request.form.get("retain_count", "7"))
    except ValueError:
        retain_count = 7
    retain_count = min(max(retain_count, 1), 365)

    with get_db() as conn:
        update_backup_config(conn, frequency, weekly_day, retain_count)
    removed = enforce_keep_cleanup_now()
    if removed > 0:
        session["backup_msg"] = f"{t('Backup settings saved')}. {t('Cleanup removed')} {removed} {t('file(s)')}."
    else:
        session["backup_msg"] = f"{t('Backup settings saved')}. {t('Cleanup applied')}."
    return redirect(url_for("backups.backups_page"))


@backups_bp.route("/management/backups/run-now", methods=["POST"])
def backups_run_now():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    ok, _, message = run_backup(trigger="manual", created_by=session.get("user_name"))
    if ok:
        session["backup_msg"] = t("Backup created")
    else:
        session["backup_err"] = message
    return redirect(url_for("backups.backups_page"))


@backups_bp.route("/management/backups/download-latest")
def backups_download_latest():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    _, _, latest = read_backup_page_data()
    if not latest:
        session["backup_err"] = t("No backup available")
        return redirect(url_for("backups.backups_page"))
    file_path = Path(latest[1] or "")
    if not file_path.is_file():
        session["backup_err"] = t("Latest backup file not found")
        return redirect(url_for("backups.backups_page"))
    return send_file(file_path, as_attachment=True, download_name=latest[0] or file_path.name)


@backups_bp.route("/management/backups/download/<int:run_id>")
def backups_download_run(run_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    row = get_backup_file_for_run(run_id)
    if not row:
        session["backup_err"] = t("Backup run not found")
        return redirect(url_for("backups.backups_page"))
    _, filename, file_path, status = row
    if status != "success" or not file_path:
        session["backup_err"] = t("Backup not available for download")
        return redirect(url_for("backups.backups_page"))
    path = Path(file_path)
    if not path.is_file():
        session["backup_err"] = t("Backup file not found")
        return redirect(url_for("backups.backups_page"))
    return send_file(path, as_attachment=True, download_name=filename or path.name)


@backups_bp.route("/management/backups/restore/<int:run_id>", methods=["POST"])
def backups_restore_run(run_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    ok, message = restore_backup(run_id, restored_by=session.get("user_name"))
    if ok:
        session["backup_msg"] = t("Backup restored successfully")
    else:
        session["backup_err"] = message
    return redirect(url_for("backups.backups_page"))


@backups_bp.route("/management/backups/delete/<int:run_id>", methods=["POST"])
def backups_delete_run_file(run_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard.dashboard"))
    ok, message = delete_backup_file(run_id, deleted_by=session.get("user_name"))
    if ok:
        session["backup_msg"] = t("Backup file deleted")
    else:
        session["backup_err"] = message
    return redirect(url_for("backups.backups_page"))
