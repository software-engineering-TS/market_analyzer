"""Security helper regression tests."""

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies.security_dependencies import get_current_user
from app.exceptions.auth_exceptions import AuthenticationError
from app.security.jwt_handler import JWTService


class FakeRepository:
    def __init__(self, user):
        self.user = user

    def get_user_by_id(self, user_id):
        return self.user


def test_authenticated_profile_projection_excludes_internal_fields(monkeypatch):
    monkeypatch.setattr(
        JWTService,
        "verify_access_token",
        lambda token: {"sub": "3"},
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    result = get_current_user(
        credentials=credentials,
        repository=FakeRepository({
            "id": 3,
            "username": "analyst",
            "email": "analyst@example.com",
            "created_at": "2026-01-01T00:00:00Z",
            "hash_password": "secret-hash",
            "is_admin": True,
        }),
    )

    assert result == {
        "id": 3,
        "username": "analyst",
        "email": "analyst@example.com",
        "created_at": "2026-01-01T00:00:00Z",
    }


@pytest.mark.parametrize("subject", [None, "", "not-an-integer", "-9"])
def test_invalid_jwt_subject_is_rejected(monkeypatch, subject):
    monkeypatch.setattr(
        JWTService,
        "verify_access_token",
        lambda token: {"sub": subject},
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(AuthenticationError):
        get_current_user(
            credentials=credentials,
            repository=FakeRepository({"id": 1, "username": "analyst"}),
        )
