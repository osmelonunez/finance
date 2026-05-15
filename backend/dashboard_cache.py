import threading
import time


_LOCK = threading.Lock()
_CACHE = {}
_TTL_SECONDS = 30


def _now() -> float:
    return time.time()


def make_key(selected_month: str, years_span: int):
    return (selected_month, int(years_span))


def get_cached(key):
    with _LOCK:
        entry = _CACHE.get(key)
        if not entry:
            return None
        if _now() - entry["ts"] > _TTL_SECONDS:
            _CACHE.pop(key, None)
            return None
        return entry["value"]


def set_cached(key, value):
    with _LOCK:
        _CACHE[key] = {"ts": _now(), "value": value}


def invalidate_dashboard_cache():
    with _LOCK:
        _CACHE.clear()
