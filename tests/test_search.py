from app.services.search_service import SearchService


class FakeSearchRepository:
    def search_stocks(self, query, limit=10, offset=0):
        return [
            {
                "symbol": "TCS",
                "company_name": "TATA CONSULTANCY SERVICES",
                "exchange": "NSE",
                "series": None,
            }
        ]


def test_search_accepts_stock_without_series():
    service = SearchService(FakeSearchRepository())

    result = service.search_stocks("TCS")

    assert result.total == 1
    assert result.stocks[0].symbol == "TCS"
    assert result.stocks[0].series is None


import logging

import pytest

from app.exceptions.database_exceptions import DatabaseOperationError
from app.repositories import search_repository, stock_repository


class FailingCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, *_args, **_kwargs):
        raise RuntimeError("sensitive database detail")

    def fetchall(self):
        return []

    def fetchone(self):
        return None


class FailingConnection:
    def cursor(self, **_kwargs):
        return FailingCursor()


@pytest.mark.parametrize(
    ("module", "invoke", "expected_message", "sensitive_input"),
    [
        (
            search_repository,
            lambda: search_repository.SearchRepository().search_stocks(
                "private-search-term"
            ),
            "Unable to complete stock search.",
            "private-search-term",
        ),
        (
            stock_repository,
            lambda: stock_repository.StockRepository().get_stock_by_symbol(
                "PRIVATE-SYMBOL"
            ),
            "Unable to retrieve stock information.",
            "PRIVATE-SYMBOL",
        ),
    ],
)
def test_repository_errors_are_sanitized(
    module,
    invoke,
    expected_message,
    sensitive_input,
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(module, "get_connection", lambda: FailingConnection())
    monkeypatch.setattr(module, "release_connection", lambda _connection: None)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(DatabaseOperationError) as error:
            invoke()

    assert str(error.value) == expected_message
    assert "sensitive database detail" not in str(error.value)
    assert "sensitive database detail" not in caplog.text
    assert sensitive_input not in caplog.text
