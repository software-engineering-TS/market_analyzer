"""Runtime configuration security validation tests."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def _settings(**overrides):
    values = {
        "DB_HOST": "localhost",
        "DB_NAME": "market_analyzer",
        "DB_USER": "app",
        "DB_PASSWORD": "test-password",
        "JWT_SECRET_KEY": "test-secret-key-with-at-least-32-characters",
        "ENVIRONMENT": "development",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_only_explicitly_supported_jwt_algorithm_is_accepted():
    with pytest.raises(ValidationError, match="HS256"):
        _settings(JWT_ALGORITHM="none")


def test_production_requires_shared_redis_storage():
    with pytest.raises(ValidationError, match="Redis"):
        _settings(ENVIRONMENT="production", RATE_LIMIT_STORAGE_URI="memory://")


def test_production_rejects_placeholder_jwt_secret():
    with pytest.raises(ValidationError, match="unique JWT secret"):
        _settings(
            ENVIRONMENT="production",
            RATE_LIMIT_STORAGE_URI="rediss://redis.example.test:6379/0",
            JWT_SECRET_KEY="change-me-this-is-long-enough-to-pass-length",
        )


def test_production_accepts_redis_and_non_placeholder_secret():
    configured = _settings(
        ENVIRONMENT="production",
        RATE_LIMIT_STORAGE_URI="rediss://redis.example.test:6379/0",
    )
    assert configured.ENVIRONMENT == "production"
