"""Regression tests for rate-limit behavior and production configuration."""

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from pydantic import ValidationError
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


def _build_limited_app(path: str):
    # Each test app gets an independent in-memory store. The production app
    # uses the shared limiter configured in app.rate_limiting.
    app_limiter = Limiter(
        key_func=get_remote_address,
        storage_uri="memory://",
        strategy="fixed-window",
        headers_enabled=True,
    )
    app = FastAPI()
    app.state.limiter = app_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get(path)
    @app_limiter.limit("2/minute")
    async def limited(request: Request, response: Response):
        return {"ok": True}

    return app


def test_rate_limit_allows_requests_within_limit():
    path = "/limited-allowed"
    client = TestClient(_build_limited_app(path))

    assert client.get(path).status_code == 200
    assert client.get(path).status_code == 200


def test_rate_limit_rejects_request_after_limit():
    path = "/limited-exceeded"
    client = TestClient(_build_limited_app(path))

    assert client.get(path).status_code == 200
    assert client.get(path).status_code == 200
    response = client.get(path)

    assert response.status_code == 429
    assert "retry-after" in response.headers


def test_production_settings_require_shared_redis_storage():
    from app.config import Settings

    common = {
        "DB_HOST": "localhost",
        "DB_NAME": "market_analyzer",
        "DB_USER": "market_analyzer",
        "DB_PASSWORD": "test-password",
        "JWT_SECRET_KEY": "unit-test-secret-key-at-least-32-characters-long",
        "ENVIRONMENT": "production",
    }

    with pytest.raises(ValidationError):
        Settings(**common)

    settings = Settings(**common, RATE_LIMIT_STORAGE_URI="rediss://redis.internal:6379/0")
    assert settings.RATE_LIMIT_STORAGE_URI.startswith("rediss://")
