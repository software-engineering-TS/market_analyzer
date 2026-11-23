"""Short-lived JWT revocation storage."""
from __future__ import annotations

from functools import lru_cache
from math import ceil
from threading import Lock
from time import time

from redis import Redis
from redis.exceptions import RedisError

from app.config import settings
from app.exceptions.auth_exceptions import TokenStoreUnavailableError

_MEMORY_REVOKED: dict[str, float] = {}
_MEMORY_LOCK = Lock()


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(
        settings.RATE_LIMIT_STORAGE_URI,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
        decode_responses=True,
    )


def ping_token_store() -> bool:
    """Check production Redis connectivity without exposing connection details."""
    try:
        return bool(_redis_client().ping())
    except RedisError as exc:
        raise TokenStoreUnavailableError("Session revocation storage is unavailable.") from exc


def revoke_token_id(token_id: str, expires_at: int | float) -> None:
    """Mark a token ID revoked until its original expiry."""
    ttl = ceil(float(expires_at) - time())
    if ttl <= 0:
        return
    if settings.ENVIRONMENT.lower() == "production":
        try:
            _redis_client().set(f"market-analyzer:revoked-jwt:{token_id}", "1", ex=ttl)
        except RedisError as exc:
            raise TokenStoreUnavailableError("Session revocation storage is unavailable.") from exc
        return
    now = time()
    with _MEMORY_LOCK:
        expired = [key for key, expiry in _MEMORY_REVOKED.items() if expiry <= now]
        for key in expired:
            _MEMORY_REVOKED.pop(key, None)
        _MEMORY_REVOKED[token_id] = now + ttl


def is_token_id_revoked(token_id: str) -> bool:
    """Return whether a token ID has been revoked."""
    if settings.ENVIRONMENT.lower() == "production":
        try:
            return bool(_redis_client().exists(f"market-analyzer:revoked-jwt:{token_id}"))
        except RedisError as exc:
            raise TokenStoreUnavailableError("Session revocation storage is unavailable.") from exc
    now = time()
    with _MEMORY_LOCK:
        expiry = _MEMORY_REVOKED.get(token_id)
        if expiry is None:
            return False
        if expiry <= now:
            _MEMORY_REVOKED.pop(token_id, None)
            return False
        return True
