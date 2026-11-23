"""JWT access-token claim validation tests."""
import time

import pytest

from app.exceptions.auth_exceptions import AuthenticationError
from app.security.jwt_handler import JWTService


@pytest.mark.parametrize("payload", [
    {},
    {"sub": ""},
    {"sub": 7},
    {"sub": "7", "iat": "now", "exp": 2_000_000_000, "jti": "id"},
    {"sub": "7", "iat": 1_700_000_000, "jti": "id"},
    {"sub": "7", "iat": 2_000_000_000, "exp": 2_100_000_000, "jti": "id"},
    {"sub": "7", "iat": time.time() - 10, "exp": time.time() + 300},
])
def test_verify_access_token_rejects_missing_or_invalid_required_claims(monkeypatch, payload):
    monkeypatch.setattr("app.security.jwt_handler.jwt.decode", lambda *args, **kwargs: payload)
    with pytest.raises(AuthenticationError):
        JWTService.verify_access_token("test-token")


def test_verify_access_token_accepts_required_claims(monkeypatch):
    payload = {"sub": "7", "iat": time.time() - 10,
               "exp": time.time() + 300, "jti": "test-token-id"}
    monkeypatch.setattr("app.security.jwt_handler.jwt.decode", lambda *args, **kwargs: payload)
    monkeypatch.setattr("app.security.jwt_handler.is_token_id_revoked", lambda token_id: False)
    assert JWTService.verify_access_token("test-token") == payload


def test_verify_access_token_rejects_revoked_token(monkeypatch):
    payload = {"sub": "7", "iat": time.time() - 10,
               "exp": time.time() + 300, "jti": "revoked-token-id"}
    monkeypatch.setattr("app.security.jwt_handler.jwt.decode", lambda *args, **kwargs: payload)
    monkeypatch.setattr("app.security.jwt_handler.is_token_id_revoked", lambda token_id: True)
    with pytest.raises(AuthenticationError):
        JWTService.verify_access_token("test-token")


def test_revoke_access_token_stores_token_id_until_expiry(monkeypatch):
    payload = {"jti": "token-to-revoke", "exp": time.time() + 120}
    revoked = {}
    monkeypatch.setattr("app.security.jwt_handler.jwt.decode", lambda *args, **kwargs: payload)
    monkeypatch.setattr("app.security.jwt_handler.revoke_token_id",
                        lambda token_id, expires_at: revoked.update(
                            token_id=token_id, expires_at=expires_at))
    JWTService.revoke_access_token("test-token")
    assert revoked["token_id"] == "token-to-revoke"
    assert revoked["expires_at"] == payload["exp"]
