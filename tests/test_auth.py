"""Authentication security regression tests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI

from app.api.auth_controller import router as auth_router
from app.dependencies.security_dependencies import get_current_user
from app.exceptions.exceptions_handlers import register_exception_handlers


def test_authenticated_user_dependency_never_returns_password_hash(monkeypatch):
    from fastapi.security import HTTPAuthorizationCredentials
    from app.security.jwt_handler import JWTService

    monkeypatch.setattr(
        JWTService, "verify_access_token",
        lambda token: {"sub": "7", "username": "sample"},
    )

    class Repository:
        def get_user_by_id(self, user_id):
            assert user_id == 7
            return {
                "id": 7, "username": "sample", "email": "sample@example.com",
                "created_at": "2026-01-01T00:00:00+00:00",
                "hash_password": "must-never-be-returned",
            }

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="unit-test-token",
    )
    result = get_current_user(credentials=credentials, repository=Repository())
    assert result == {
        "id": 7, "username": "sample", "email": "sample@example.com",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    assert "hash_password" not in result


def test_auth_routes_include_logout():
    routes = {
        (route.path, method)
        for route in auth_router.routes
        for method in getattr(route, "methods", set())
    }
    assert ("/sma/v1/logout", "POST") in routes


def test_me_endpoint_is_registered_once():
    me_routes = [
        route for route in auth_router.routes
        if getattr(route, "path", None) == "/sma/v1/me"
    ]
    assert len(me_routes) == 1


def test_unexpected_error_does_not_leak_exception_details():
    app = FastAPI()
    register_exception_handlers(app)
    handler = app.exception_handlers[Exception]
    request = Mock()
    request.url = SimpleNamespace(path="/private-error")
    secret_error = RuntimeError("database-password-must-not-leak")
    response = asyncio.run(handler(request, secret_error))
    body = response.body.decode("utf-8")
    assert response.status_code == 500
    assert "database-password-must-not-leak" not in body
    assert "unexpected error" in body.lower()
