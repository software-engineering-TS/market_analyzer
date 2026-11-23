"""Regression tests for sanitized watchlist repository failures."""

import logging

import pytest

from app.exceptions.database_exceptions import DatabaseOperationError
from app.repositories import watchlist_repository


class FailingCursor:
    rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, *_args, **_kwargs):
        raise RuntimeError("sensitive database detail")

    def fetchone(self):
        return None

    def fetchall(self):
        return []


class FailingConnection:
    def cursor(self, **_kwargs):
        return FailingCursor()

    def rollback(self):
        pass


@pytest.mark.parametrize(
    ("invoke", "expected_message", "sensitive_input"),
    [
        (
            lambda repository: repository.add_watchlist(9876, "PRIVATE-SYMBOL"),
            "Unable to add the watchlist item.",
            "PRIVATE-SYMBOL",
        ),
        (
            lambda repository: repository.get_watchlist(9876),
            "Unable to retrieve the watchlist.",
            "9876",
        ),
        (
            lambda repository: repository.remove_watchlist(9876, "PRIVATE-SYMBOL"),
            "Unable to remove the watchlist item.",
            "PRIVATE-SYMBOL",
        ),
    ],
)
def test_watchlist_repository_errors_are_sanitized(
    invoke, expected_message, sensitive_input, monkeypatch, caplog
):
    monkeypatch.setattr(
        watchlist_repository, "get_connection", lambda: FailingConnection()
    )
    monkeypatch.setattr(
        watchlist_repository, "release_connection", lambda _connection: None
    )
    repository = watchlist_repository.WatchlistRepository()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(DatabaseOperationError) as error:
            invoke(repository)

    assert str(error.value) == expected_message
    assert "sensitive database detail" not in str(error.value)
    assert "sensitive database detail" not in caplog.text
    assert sensitive_input not in caplog.text
