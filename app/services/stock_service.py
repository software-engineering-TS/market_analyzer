"""Stock business logic."""

from app.exceptions.business_exceptions import (
    MarketDataUnavailableException,
    ResourceNotFoundException,
)
from app.logger import logger
from app.models.indicators_models import (
    BollingerBands,
    MACD,
    MovingAverage,
    RSI,
    TechnicalIndicators,
)
from app.models.stock_models import StockDetails
from app.providers.market_data_provider import MarketDataProvider
from app.repositories.stock_repository import StockRepository
from app.utils.indicator_calculator import IndicatorCalculator
from app.utils.stock_constants import VALID_INTERVALS, VALID_PERIODS


class StockService:
    def __init__(
        self,
        stock_repository: StockRepository,
        market_data_provider: MarketDataProvider,
    ):
        self.stock_repository = stock_repository
        self.market_data_provider = market_data_provider

    def get_stock_details(self, symbol: str) -> StockDetails:
        symbol = symbol.strip().upper()
        logger.info("Retrieving stock details | Symbol=%s", symbol)

        stock = self.stock_repository.get_stock_by_symbol(symbol)
        if stock is None:
            raise ResourceNotFoundException(f"Stock '{symbol}' not found.")

        market_data = self.market_data_provider.get_stock_details(symbol)
        if market_data is None:
            raise MarketDataUnavailableException(
                f"Market data is unavailable for '{symbol}'."
            )

        dividend_yield = market_data.dividend_yield
        if dividend_yield is not None and dividend_yield < 1:
            dividend_yield *= 100

        return StockDetails(
            symbol=stock["symbol"],
            company_name=stock["company_name"],
            exchange=stock["exchange"],
            currency=market_data.currency,
            sector=market_data.sector,
            industry=market_data.industry,
            website=market_data.website,
            summary=market_data.summary,
            current_price=market_data.current_price,
            previous_close=market_data.previous_close,
            day_high=market_data.day_high,
            day_low=market_data.day_low,
            fifty_two_week_high=market_data.fifty_two_week_high,
            fifty_two_week_low=market_data.fifty_two_week_low,
            volume=market_data.volume,
            market_cap=market_data.market_cap,
            change=market_data.change,
            change_percent=market_data.change_percent,
            pe_ratio=market_data.pe_ratio,
            eps=market_data.eps,
            book_value=market_data.book_value,
            dividend_yield=dividend_yield,
            beta=market_data.beta,
            employee_count=market_data.employee_count,
            ceo=market_data.ceo,
            country=market_data.country,
        )

    @staticmethod
    def _validate_history_request(period: str, interval: str) -> tuple[str, str]:
        period = period.lower().strip()
        interval = interval.lower().strip()

        if period not in VALID_PERIODS:
            raise ValueError(
                f"Invalid period '{period}'. Allowed values: {sorted(VALID_PERIODS)}"
            )
        if interval not in VALID_INTERVALS:
            raise ValueError(
                f"Invalid interval '{interval}'. Allowed values: {sorted(VALID_INTERVALS)}"
            )
        return period, interval

    def get_stock_history(self, symbol: str, period: str, interval: str):
        period, interval = self._validate_history_request(period, interval)
        history = self.market_data_provider.get_stock_history(
            symbol=symbol.strip().upper(),
            period=period,
            interval=interval,
        )
        if history is None:
            raise MarketDataUnavailableException(
                f"Historical market data is unavailable for '{symbol.upper()}'."
            )
        return history

    def get_technical_indicators(
        self,
        symbol: str,
        period: str,
        interval: str,
    ) -> TechnicalIndicators:
        # Validate once and fetch one DataFrame. The previous implementation
        # downloaded the same range twice through two provider methods.
        period, interval = self._validate_history_request(period, interval)
        history = self.market_data_provider.get_history_dataframe(
            symbol=symbol.strip().upper(),
            period=period,
            interval=interval,
        )
        if history is None or history.empty:
            raise MarketDataUnavailableException(
                f"Historical market data is unavailable for '{symbol.upper()}'."
            )

        macd, signal, histogram = IndicatorCalculator.calculate_macd(history)
        upper, middle, lower = IndicatorCalculator.calculate_bollinger_bands(history)

        return TechnicalIndicators(
            symbol=symbol.upper(),
            moving_average=MovingAverage(
                sma20=IndicatorCalculator.calculate_sma(history, 20),
                sma50=IndicatorCalculator.calculate_sma(history, 50),
                ema20=IndicatorCalculator.calculate_ema(history, 20),
                ema50=IndicatorCalculator.calculate_ema(history, 50),
            ),
            rsi=RSI(value=IndicatorCalculator.calculate_rsi(history)),
            macd=MACD(macd=macd, signal=signal, histogram=histogram),
            bollinger_bands=BollingerBands(
                upper=upper,
                middle=middle,
                lower=lower,
            ),
        )
