"""Pure calculations for common technical indicators."""

import math

import pandas as pd


class IndicatorCalculator:
    """Calculate indicators from OHLC DataFrames without external I/O."""

    @staticmethod
    def _close(data: pd.DataFrame, minimum_rows: int, period: int) -> pd.Series | None:
        if period < 1 or data is None or "Close" not in data.columns:
            return None
        close = pd.to_numeric(data["Close"], errors="coerce").dropna()
        if len(close) < minimum_rows:
            return None
        return close

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> float | None:
        close = IndicatorCalculator._close(data, period, period)
        if close is None:
            return None
        value = float(close.rolling(window=period).mean().iloc[-1])
        return round(value, 2) if math.isfinite(value) else None

    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> float | None:
        close = IndicatorCalculator._close(data, period, period)
        if close is None:
            return None
        value = float(close.ewm(span=period, adjust=False).mean().iloc[-1])
        return round(value, 2) if math.isfinite(value) else None

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float | None:
        close = IndicatorCalculator._close(data, period + 1, period)
        if close is None:
            return None

        delta = close.diff().dropna()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        average_gain = float(gains.tail(period).mean())
        average_loss = float(losses.tail(period).mean())

        if average_loss == 0:
            return 50.0 if average_gain == 0 else 100.0

        relative_strength = average_gain / average_loss
        value = 100 - (100 / (1 + relative_strength))
        return round(value, 2) if math.isfinite(value) else None

    @staticmethod
    def calculate_macd(
        data: pd.DataFrame,
    ) -> tuple[float | None, float | None, float | None]:
        close = IndicatorCalculator._close(data, 35, 1)
        if close is None:
            return None, None, None

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line

        return tuple(
            round(float(series.iloc[-1]), 2)
            for series in (macd_line, signal_line, histogram)
        )

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
    ) -> tuple[float | None, float | None, float | None]:
        close = IndicatorCalculator._close(data, period, period)
        if close is None:
            return None, None, None

        rolling = close.rolling(window=period)
        middle = rolling.mean().iloc[-1]
        standard_deviation = rolling.std().iloc[-1]
        upper = middle + (2 * standard_deviation)
        lower = middle - (2 * standard_deviation)

        return (
            round(float(upper), 2),
            round(float(middle), 2),
            round(float(lower), 2),
        )
