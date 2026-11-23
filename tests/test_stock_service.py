"""Stock service tests using in-memory fakes."""

import pandas as pd
import pytest

from app.exceptions.business_exceptions import MarketDataUnavailableException
from app.models.stock_models import ProviderStockDetails
from app.services.stock_service import StockService


class FakeRepository:
    def get_stock_by_symbol(self, symbol):
        return {
            "symbol": symbol,
            "company_name": "Example Limited",
            "exchange": "NSE",
        }


class FakeProvider:
    def __init__(self, frame=None, details=None):
        self.frame = frame
        self.details = details
        self.history_dataframe_calls = 0
        self.stock_history_calls = 0

    def get_stock_details(self, symbol):
        return self.details

    def get_stock_history(self, **kwargs):
        self.stock_history_calls += 1
        return object()

    def get_history_dataframe(self, **kwargs):
        self.history_dataframe_calls += 1
        return self.frame


def test_missing_market_data_raises_typed_error():
    service = StockService(FakeRepository(), FakeProvider(details=None))
    with pytest.raises(MarketDataUnavailableException):
        service.get_stock_details("TCS")


def test_technical_indicators_fetch_history_dataframe_once():
    frame = pd.DataFrame({"Close": [float(value) for value in range(1, 61)]})
    provider = FakeProvider(frame=frame)
    service = StockService(FakeRepository(), provider)

    result = service.get_technical_indicators("TCS", "1y", "1d")

    assert result.symbol == "TCS"
    assert provider.history_dataframe_calls == 1
    assert provider.stock_history_calls == 0


def test_invalid_period_is_rejected_before_provider_call():
    provider = FakeProvider(frame=pd.DataFrame({"Close": [1.0]}))
    service = StockService(FakeRepository(), provider)

    with pytest.raises(ValueError, match="Invalid period"):
        service.get_technical_indicators("TCS", "invalid", "1d")

    assert provider.history_dataframe_calls == 0



def test_stock_details_falls_back_to_stock_master_when_provider_metadata_is_missing():
    provider_details = ProviderStockDetails(
        symbol="TCS",
        company_name=None,
        exchange=None,
        currency=None,
    )
    service = StockService(
        FakeRepository(),
        FakeProvider(details=provider_details),
    )

    result = service.get_stock_details("TCS")

    assert result.company_name == "Example Limited"
    assert result.exchange == "NSE"
    assert result.currency == "INR"


def test_stock_details_uses_provider_metadata_when_stock_master_is_incomplete():
    class IncompleteRepository:
        def get_stock_by_symbol(self, symbol):
            return {
                "symbol": symbol,
                "company_name": None,
                "exchange": None,
                "currency": None,
            }

    provider_details = ProviderStockDetails(
        symbol="TCS",
        company_name="Tata Consultancy Services",
        exchange="NSE",
        currency="INR",
    )
    service = StockService(
        IncompleteRepository(),
        FakeProvider(details=provider_details),
    )

    result = service.get_stock_details("TCS")

    assert result.company_name == "Tata Consultancy Services"
    assert result.exchange == "NSE"
    assert result.currency == "INR"


def test_stock_details_returns_typed_provider_error_when_required_metadata_is_missing():
    class IncompleteRepository:
        def get_stock_by_symbol(self, symbol):
            return {
                "symbol": symbol,
                "company_name": None,
                "exchange": None,
                "currency": None,
            }

    provider_details = ProviderStockDetails(
        symbol="TCS",
        company_name=None,
        exchange=None,
        currency=None,
    )
    service = StockService(
        IncompleteRepository(),
        FakeProvider(details=provider_details),
    )

    with pytest.raises(MarketDataUnavailableException):
        service.get_stock_details("TCS")
