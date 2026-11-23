"""Regression tests for authentication endpoint rate limits."""

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from app.rate_limiting import limiter


def _build_limited_app(path: str):
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get(path)
    @limiter.limit("2/minute")
    async def limited(request: Request, response: Response):
        return {"ok": True}

    return app


def test_rate_limit_allows_requests_within_limit():
    client = TestClient(_build_limited_app("/limited-allowed"))

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200


def test_rate_limit_rejects_request_after_limit():
    client = TestClient(_build_limited_app("/limited-exceeded"))

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    response = client.get("/limited")

    assert response.status_code == 429
    assert "retry-after" in response.headers


def test_production_settings_require_shared_redis_storage():
    import pytest
    from pydantic import ValidationError

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
