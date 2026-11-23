"""Shared test configuration.

Defaults keep unit tests isolated from a developer's real credentials and database.
Integration tests use TEST_DATABASE_URL when explicitly configured.
"""

import os

os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "market_analyzer_test")
os.environ.setdefault("DB_USER", "market_analyzer")
os.environ.setdefault("DB_PASSWORD", "unit-test-only-password")
os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret-key-at-least-32-characters-long")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
