"""Tests for PostgreSQL connection-pool cleanup."""

import app.database.connection as database_connection


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
    closed = 0

    def __init__(self):
        self.put_calls = []

    def putconn(self, connection, close=False):
        self.put_calls.append((connection, close))


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
