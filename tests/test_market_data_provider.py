"""Regression tests for incomplete and unavailable Yahoo Finance responses."""

from app.models.stock_models import ProviderStockDetails
from app.providers.market_data_provider import MarketDataProvider


class FakeTicker:
    def __init__(self, info, fast_info=None):
        self.info = info
        self.fast_info = fast_info or {}


def test_provider_accepts_missing_company_exchange_and_currency(monkeypatch):
    ticker = FakeTicker(
        info={
            "longName": None,
            "shortName": None,
            "fullExchangeName": None,
            "exchange": None,
            "currency": None,
            "currentPrice": 100.0,
            "previousClose": 98.0,
        }
    )
    monkeypatch.setattr(
        "app.providers.market_data_provider.yf.Ticker",
        lambda symbol: ticker,
    )

    result = MarketDataProvider().get_stock_details("TCS")

    assert isinstance(result, ProviderStockDetails)
    assert result.company_name is None
    assert result.exchange is None
    assert result.currency is None
    assert result.current_price == 100.0


def test_provider_returns_none_when_yahoo_finance_request_fails(monkeypatch):
    class FailingTicker:
        @property
        def info(self):
            raise RuntimeError("temporary provider transport failure")

    monkeypatch.setattr(
        "app.providers.market_data_provider.yf.Ticker",
        lambda symbol: FailingTicker(),
    )

    assert MarketDataProvider().get_stock_details("TCS") is None


def test_provider_retries_transient_failures_and_returns_success(monkeypatch):
    attempts = 0
    delays = []
    
    def flaky_request():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary provider failure")
        return {"price": 123.45}

    monkeypatch.setattr(
        "app.providers.market_data_provider.time.sleep",
        delays.append,
    )

    result = MarketDataProvider()._fetch_with_retry(
        flaky_request,
        "TCS",
        "test request",
    )

    assert result == {"price": 123.45}
    assert attempts == 3
    assert delays == [0.25, 0.5]


def test_provider_stops_after_maximum_retry_attempts(monkeypatch):
    attempts = 0
    monkeypatch.setattr(
        "app.providers.market_data_provider.time.sleep",
        lambda _delay: None,
    )

    def failing_request():
        nonlocal attempts
        attempts += 1
        raise RuntimeError("provider unavailable")

    result = MarketDataProvider()._fetch_with_retry(
        failing_request,
        "TCS",
        "test request",
    )

    assert result is None
    assert attempts == MarketDataProvider.MAX_ATTEMPTS
