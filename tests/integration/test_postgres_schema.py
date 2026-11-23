"""PostgreSQL schema smoke test (runs when TEST_DATABASE_URL is configured)."""

import os
from pathlib import Path

import psycopg2
import pytest


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)
def test_schema_creates_core_tables():
    connection = psycopg2.connect(os.environ["TEST_DATABASE_URL"])
    try:
        with connection:
            with connection.cursor() as cursor:
                schema = Path("app/database/schema.sql").read_text(encoding="utf-8")
                cursor.execute(schema)
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name IN (
                        'user_credentials',
                        'users_login_info',
                        'stocks',
                        'watchlist'
                      );
                    """
                )
                tables = {row[0] for row in cursor.fetchall()}
        assert tables == {
            "user_credentials",
            "users_login_info",
            "stocks",
            "watchlist",
        }
    finally:
        connection.close()
