"""Regression tests for baseline response security headers."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.request_logger import RequestLoggingMiddleware


def test_request_middleware_sets_baseline_security_headers():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )
