"""Regression tests for authentication endpoint rate limits."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from app.rate_limiting import limiter


def _build_limited_app():
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/limited")
    @limiter.limit("2/minute")
    async def limited(request: Request):
        return {"ok": True}

    return app


def test_rate_limit_allows_requests_within_limit():
    limiter.reset()
    client = TestClient(_build_limited_app())

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200


def test_rate_limit_rejects_request_after_limit():
    limiter.reset()
    client = TestClient(_build_limited_app())

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    response = client.get("/limited")

    assert response.status_code == 429
    assert "retry-after" in response.headers
