"""Internal backup scheduler. Runs in the application container, independently of web traffic."""
import logging
import os
import signal
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from backup_service import run_scheduled_backup_cycle
from log_formatting import color_enabled, text_formatter

handler = logging.StreamHandler()
handler.setFormatter(text_formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", color_enabled("text")))
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
logger = logging.getLogger("finance.backup_cron")
running = True


def _stop(_signal, _frame):
    global running
    running = False


def _wait_until_midnight(zone):
    while running:
        now = datetime.now(zone)
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = max(1, (next_midnight - now).total_seconds())
        time.sleep(min(wait_seconds, 60))
        if datetime.now(zone).date() == next_midnight.date() and datetime.now(zone).hour == 0:
            return


def run_scheduler():
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    zone = ZoneInfo(os.environ.get("TZ", "UTC"))
    logger.info("backup_cron_started timezone=%s", zone.key)
    while running:
        # Check immediately on startup so a restart or a short outage around
        # midnight does not make the application miss the whole day's run.
        # run_scheduled_backup_cycle uses last_run_at to prevent duplicates.
        try:
            run_scheduled_backup_cycle(datetime.now(zone).replace(tzinfo=None))
        except Exception:
            logger.exception("backup_cron_cycle_failed")
        if running:
            _wait_until_midnight(zone)


if __name__ == "__main__":
    run_scheduler()
