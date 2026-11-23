"""Technical indicator regression tests."""

import pandas as pd

from app.utils.indicator_calculator import IndicatorCalculator


def test_rsi_returns_100_when_prices_only_rise():
    data = pd.DataFrame({"Close": [float(value) for value in range(1, 31)]})
    assert IndicatorCalculator.calculate_rsi(data) == 100.0


def test_rsi_returns_50_for_flat_market():
    data = pd.DataFrame({"Close": [100.0] * 30})
    assert IndicatorCalculator.calculate_rsi(data) == 50.0


def test_rsi_returns_zero_for_prices_only_falling():
    data = pd.DataFrame({"Close": [float(value) for value in range(30, 0, -1)]})
    assert IndicatorCalculator.calculate_rsi(data) == 0.0


def test_indicators_return_none_when_history_is_too_short():
    data = pd.DataFrame({"Close": [10.0, 11.0, 12.0]})
    assert IndicatorCalculator.calculate_sma(data, 20) is None
    assert IndicatorCalculator.calculate_ema(data, 20) is None
    assert IndicatorCalculator.calculate_rsi(data, 14) is None


def test_indicator_rejects_missing_close_column():
    data = pd.DataFrame({"Open": [10.0, 11.0]})
    assert IndicatorCalculator.calculate_sma(data, 2) is None
    assert IndicatorCalculator.calculate_rsi(data, 1) is None


def test_macd_returns_empty_values_for_short_history():
    data = pd.DataFrame({"Close": [float(value) for value in range(1, 20)]})
    assert IndicatorCalculator.calculate_macd(data) == (None, None, None)


def test_bollinger_bands_return_ordered_bounds():
    data = pd.DataFrame({"Close": [float(value) for value in range(1, 31)]})
    upper, middle, lower = IndicatorCalculator.calculate_bollinger_bands(data, 20)
    assert lower < middle < upper
