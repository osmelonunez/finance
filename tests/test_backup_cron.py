import backup_cron
from datetime import datetime as RealDateTime


def test_stop_and_wait_exit_without_sleep(monkeypatch):
    backup_cron.running = True
    backup_cron._stop(None, None)
    assert backup_cron.running is False
    monkeypatch.setattr(backup_cron, "running", False)
    backup_cron._wait_until_midnight("Europe/Madrid")


def test_wait_until_midnight_runs_one_short_sleep(monkeypatch):
    backup_cron.running = True
    values = iter((RealDateTime(2026, 7, 1, 23, 59, 59), RealDateTime(2026, 7, 2, 0, 0), RealDateTime(2026, 7, 2, 0, 0)))

    class Clock:
        @classmethod
        def now(cls, _zone):
            return next(values)

    sleeps = []
    monkeypatch.setattr(backup_cron, "datetime", Clock)
    monkeypatch.setattr(backup_cron.time, "sleep", lambda seconds: sleeps.append(seconds))
    backup_cron._wait_until_midnight("zone")
    assert sleeps == [1]


def test_scheduler_runs_cycle_and_stops(monkeypatch):
    backup_cron.running = True
    registered = []
    cycles = []
    monkeypatch.setattr(backup_cron.signal, "signal", lambda *args: registered.append(args))

    def wait(_zone):
        return None

    def cycle(now):
        cycles.append(now)
        backup_cron.running = False

    monkeypatch.setattr(backup_cron, "_wait_until_midnight", wait)
    monkeypatch.setattr(backup_cron, "run_scheduled_backup_cycle", cycle)
    backup_cron.run_scheduler()
    assert len(registered) == 2
    assert len(cycles) == 1


def test_scheduler_logs_cycle_errors_and_stops(monkeypatch):
    backup_cron.running = True
    monkeypatch.setattr(backup_cron.signal, "signal", lambda *_args: None)
    monkeypatch.setattr(backup_cron, "_wait_until_midnight", lambda _zone: None)

    def failing_cycle(_now):
        backup_cron.running = False
        raise RuntimeError("scheduled failure")

    monkeypatch.setattr(backup_cron, "run_scheduled_backup_cycle", failing_cycle)
    backup_cron.run_scheduler()
    assert backup_cron.running is False
