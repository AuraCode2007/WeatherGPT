"""
cache.py
Redis caching helpers with graceful degradation when Redis is unavailable.
"""
import json
import redis
from backend.config import REDIS_URL

try:
    _redis = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _redis.ping()
    _REDIS_AVAILABLE = True
except Exception:
    _REDIS_AVAILABLE = False
    _redis = None  # type: ignore[assignment]


def get_cached(key: str) -> dict | str | None:
    """Return parsed JSON value from Redis, or None on miss / unavailable."""
    if not _REDIS_AVAILABLE:
        return None
    try:
        raw = _redis.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set_cached(key: str, value: dict | str, ttl: int = 300) -> None:
    """Store value in Redis with a TTL (seconds). No-op if Redis unavailable."""
    if not _REDIS_AVAILABLE:
        return
    try:
        _redis.setex(key, ttl, json.dumps(value))
    except Exception:
        pass
