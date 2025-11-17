"""In-memory TTL cache for small datasets used by the data layer.
"""
import os
import time
from typing import Any, Optional

_CACHE = {}

DEFAULT_TTL = int(os.environ.get('STATES_CACHE_TTL', '60'))


def _now() -> float:
    return time.time()


def get(key: str) -> Optional[Any]:
    entry = _CACHE.get(key)
    if not entry:
        return None
    value, expires_at = entry
    if expires_at is None or _now() < expires_at:
        return value
    # Indicates that the cache is expired
    del _CACHE[key]
    return None


def set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    if ttl is None:
        ttl = DEFAULT_TTL
    expires_at = None if ttl <= 0 else _now() + ttl
    _CACHE[key] = (value, expires_at)


def invalidate(key: str) -> None:
    _CACHE.pop(key, None)


def clear() -> None:
    _CACHE.clear()
