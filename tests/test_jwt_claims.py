"""JWT access-token claim validation tests."""

import pytest

from app.exceptions.auth_exceptions import AuthenticationError
from app.security.jwt_handler import JWTService


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"sub": ""},
        {"sub": 7},
        {"sub": "7", "iat": "now", "exp": 2_000_000_000},
        {"sub": "7", "iat": 1_700_000_000},
        {"sub": "7", "iat": 2_000_000_000, "exp": 2_100_000_000},
    ],
)
def test_verify_access_token_rejects_missing_or_invalid_required_claims(
    monkeypatch,
    payload,
):
    monkeypatch.setattr(
        "app.security.jwt_handler.jwt.decode",
        lambda *args, **kwargs: payload,
    )

    with pytest.raises(AuthenticationError):
        JWTService.verify_access_token("test-token")


def test_verify_access_token_accepts_required_claims(monkeypatch):
    import time

    payload = {
        "sub": "7",
        "iat": time.time() - 10,
        "exp": time.time() + 300,
    }
    monkeypatch.setattr(
        "app.security.jwt_handler.jwt.decode",
        lambda *args, **kwargs: payload,
    )

    assert JWTService.verify_access_token("test-token") == payload
