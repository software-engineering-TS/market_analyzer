"""Tests for PostgreSQL connection-pool lifecycle and cleanup."""

import pytest
from psycopg2.pool import PoolError

import app.database.connection as database_connection
from app.exceptions.database_exceptions import DatabaseConnectionError


class FakeConnection:
    def __init__(self, rollback_error=None):
        self.closed = 0
        self.rollback_error = rollback_error
        self.rollback_calls = 0
        self.close_calls = 0

    def rollback(self):
        self.rollback_calls += 1
        if self.rollback_error is not None:
            raise self.rollback_error

    def close(self):
        self.close_calls += 1
        self.closed = 1


class FakePool:
    def __init__(self, closed=0, get_error=None, connection=None):
        self.closed = closed
        self.get_error = get_error
        self.connection = connection
        self.put_calls = []
        self.closeall_calls = 0

    def getconn(self):
        if self.get_error is not None:
            raise self.get_error
        return self.connection

    def putconn(self, connection, close=False):
        self.put_calls.append((connection, close))

    def closeall(self):
        self.closeall_calls += 1
        self.closed = 1


def test_get_connection_rejects_uninitialized_pool(monkeypatch):
    monkeypatch.setattr(database_connection, "connection_pool", None)

    with pytest.raises(DatabaseConnectionError, match="not initialized"):
        database_connection.get_connection()


def test_get_connection_rejects_closed_pool(monkeypatch):
    monkeypatch.setattr(database_connection, "connection_pool", FakePool(closed=1))

    with pytest.raises(DatabaseConnectionError, match="not initialized"):
        database_connection.get_connection()


def test_get_connection_wraps_pool_exhaustion(monkeypatch):
    monkeypatch.setattr(
        database_connection,
        "connection_pool",
        FakePool(get_error=PoolError("pool exhausted")),
    )

    with pytest.raises(DatabaseConnectionError, match="currently available"):
        database_connection.get_connection()


def test_get_connection_returns_borrowed_connection(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(
        database_connection,
        "connection_pool",
        FakePool(connection=connection),
    )

    assert database_connection.get_connection() is connection


def test_release_connection_rolls_back_before_returning_to_pool(monkeypatch):
    connection = FakeConnection()
    fake_pool = FakePool()
    monkeypatch.setattr(database_connection, "connection_pool", fake_pool)

    database_connection.release_connection(connection)

    assert connection.rollback_calls == 1
    assert connection.close_calls == 0
    assert fake_pool.put_calls == [(connection, False)]


def test_release_connection_discards_connection_when_rollback_fails(monkeypatch):
    connection = FakeConnection(rollback_error=RuntimeError("connection is broken"))
    fake_pool = FakePool()
    monkeypatch.setattr(database_connection, "connection_pool", fake_pool)

    database_connection.release_connection(connection)

    assert connection.rollback_calls == 1
    assert connection.close_calls == 1
    assert fake_pool.put_calls == [(connection, True)]


def test_release_connection_closes_connection_when_pool_is_unavailable(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(database_connection, "connection_pool", None)

    database_connection.release_connection(connection)

    assert connection.close_calls == 1
    assert connection.rollback_calls == 0


def test_close_connection_pool_closes_and_resets_global(monkeypatch):
    fake_pool = FakePool()
    monkeypatch.setattr(database_connection, "connection_pool", fake_pool)

    database_connection.close_connection_pool()

    assert fake_pool.closeall_calls == 1
    assert database_connection.connection_pool is None


def test_close_connection_pool_is_safe_when_uninitialized(monkeypatch):
    monkeypatch.setattr(database_connection, "connection_pool", None)

    database_connection.close_connection_pool()

    assert database_connection.connection_pool is None
