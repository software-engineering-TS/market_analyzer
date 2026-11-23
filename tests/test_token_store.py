"""Tests for token revocation storage behavior."""
from time import time

from app.security import token_store


def test_development_store_revokes_token_until_expiry(monkeypatch):
    monkeypatch.setattr(token_store.settings, "ENVIRONMENT", "development")
    token_id = "development-token"
    token_store.revoke_token_id(token_id, time() + 60)
    assert token_store.is_token_id_revoked(token_id) is True


def test_expired_development_revocation_is_removed(monkeypatch):
    monkeypatch.setattr(token_store.settings, "ENVIRONMENT", "development")
    token_id = "expired-token"
    token_store._MEMORY_REVOKED[token_id] = time() - 1
    assert token_store.is_token_id_revoked(token_id) is False
    assert token_id not in token_store._MEMORY_REVOKED


def test_production_store_uses_redis(monkeypatch):
    monkeypatch.setattr(token_store.settings, "ENVIRONMENT", "production")

    class FakeRedis:
        def __init__(self):
            self.values = set()

        def set(self, key, value, ex):
            assert ex > 0
            self.values.add(key)

        def exists(self, key):
            return key in self.values

    client = FakeRedis()
    monkeypatch.setattr(token_store, "_redis_client", lambda: client)
    token_store.revoke_token_id("production-token", time() + 60)
    assert token_store.is_token_id_revoked("production-token") is True
