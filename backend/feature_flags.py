from functools import lru_cache

from db import get_db


@lru_cache(maxsize=1)
def loans_enabled():
    return _enabled("loans_enabled")


@lru_cache(maxsize=1)
def budgets_enabled():
    return _enabled("budgets_enabled")


def _enabled(key):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT value FROM settings WHERE key=%s", (key,))
                row = cur.fetchone()
        return bool(row[0]) if row else True
    except Exception:
        return True


def clear_feature_flags_cache():
    loans_enabled.cache_clear()
    budgets_enabled.cache_clear()
