"""Deployment health endpoint tests."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import health_controller


def _client():
    app = FastAPI()
    app.include_router(health_controller.router)
    return TestClient(app)


def test_liveness_does_not_depend_on_backing_services(monkeypatch):
    monkeypatch.setattr(
        health_controller,
        "_database_is_ready",
        lambda: (_ for _ in ()).throw(AssertionError("must not probe database")),
    )
    response = _client().get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_database_failure(monkeypatch):
    monkeypatch.setattr(health_controller, "_database_is_ready", lambda: False)
    monkeypatch.setattr(health_controller.settings, "ENVIRONMENT", "development")
    response = _client().get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "components": {"database": False},
    }


def test_readiness_checks_session_store_in_production(monkeypatch):
    monkeypatch.setattr(health_controller, "_database_is_ready", lambda: True)
    monkeypatch.setattr(health_controller.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(health_controller, "ping_token_store", lambda: True)
    response = _client().get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "components": {"database": True, "session_store": True},
    }


def test_readiness_fails_when_production_session_store_is_down(monkeypatch):
    monkeypatch.setattr(health_controller, "_database_is_ready", lambda: True)
    monkeypatch.setattr(health_controller.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(health_controller, "ping_token_store", lambda: False)
    response = _client().get("/health/ready")
    assert response.status_code == 503
    assert response.json()["components"]["session_store"] is False
