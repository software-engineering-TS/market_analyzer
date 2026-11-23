"""Shared rate-limiter configuration for API routes.

Use Redis storage in production so limits are shared across workers and instances.
The in-memory backend is intended only for local development and isolated tests.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    strategy="fixed-window",
    headers_enabled=True,
)
