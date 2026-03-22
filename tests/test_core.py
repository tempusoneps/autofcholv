import pandas as pd
import numpy as np
import pytest
from autofcholv.core import extract_features


# ─────────────────────────────────────────────
# Helper: make synthetic 5-minute OHLCV data
# ─────────────────────────────────────────────

def make_ohlcv(n_bars: int = 300) -> pd.DataFrame:
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]

    rng    = np.random.default_rng(42)
    close  = 100.0 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    close  = np.maximum(close, 10.0)
    open_  = close * (1 + rng.normal(0, 0.001, len(idx)))
    high   = close * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    low    = close * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    volume = rng.integers(1000, 10000, len(idx)).astype(float)

    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
    df.index.name = "Date"
    df["High"] = df[["Open", "Close", "High"]].max(axis=1)
    df["Low"]  = df[["Open", "Close", "Low"]].min(axis=1)
    return df


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_extract_features_returns_dataframe():
    result = extract_features(make_ohlcv(300))
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_extract_features_time_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["hour", "minute", "time_int", "day_of_week", "day_of_month", "month", "year", "session_progress"]
    for col in expected:
        assert col in result.columns, f"Missing time column: '{col}'"


def test_extract_features_resample_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "day_open", "day_high", "day_low", "day_close", "day_volume", "day_pivot",
        "prev_day_open", "prev_day_high", "prev_day_low", "prev_day_close",
        "prev_day_volume", "prev_day_pivot",
    ]
    for col in expected:
        assert col in result.columns, f"Missing resample column: '{col}'"


def test_extract_features_candlestick_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "body", "height", "upwick", "lowwick",
        "upwick_rate", "lowwick_rate", "body_rate",
        "clv", "cbr", "ibs", "color",
        "wick_imbalance", "upwick_ratio",
    ]
    for col in expected:
        assert col in result.columns, f"Missing candlestick column: '{col}'"


def test_extract_features_close_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ema_fast", "ema_slow", "rsi", "rsi_slope",
        "tsi", "roc_close", "close_zscore", "efficiency_ratio",
        "macd", "macd_signal", "macd_hist",
        "ppo", "ppo_signal", "ppo_hist",
        "ulcer_index", "cmo", "roc_skew", "roc_kurt",
        "mb", "std", "ub", "lb",
    ]
    for col in expected:
        assert col in result.columns, f"Missing close column: '{col}'"


def test_extract_features_volume_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["volume_avg", "volume_zscore"]
    for col in expected:
        assert col in result.columns, f"Missing volume column: '{col}'"


def test_extract_features_lag_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "open_lag1", "high_lag1", "low_lag1", "close_lag1",
        "volume_lag1", "ibs_lag1", "rsi_lag1",
    ]
    for col in expected:
        assert col in result.columns, f"Missing lag column: '{col}'"


def test_extract_features_mix_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ibs_n", "is_fvg",
        "ulti_osci", "vwap", "atr", "adx",
        "dm", "eom",
        "direction", "streak",
        "custom_001", "custom_002",
    ]
    for col in expected:
        assert col in result.columns, f"Missing mix column: '{col}'"


def test_extract_features_group_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "volume_group", "upper_wick_group", "lower_wick_group",
        "vol_high_pattern", "ibs_volume_pattern",
        "volume_avg_group", "high_rsi_pattern",
        "high_ub_pattern", "low_lb_pattern",
    ]
    for col in expected:
        assert col in result.columns, f"Missing group column: '{col}'"


def test_extract_features_signal_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["couple_cs_signal", "ema_cross_signal"]
    for col in expected:
        assert col in result.columns, f"Missing signal column: '{col}'"


def test_extract_features_no_nan_in_ohlcv():
    result = extract_features(make_ohlcv(300))
    assert result[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum() == 0


def test_extract_features_color_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["color"].unique()).issubset({"green", "red", "doji"})


def test_extract_features_direction_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["direction"].unique()).issubset({1, -1})


def test_extract_features_signal_values():
    result = extract_features(make_ohlcv(300))
    valid = {"None", "Bullish", "Bearish"}
    assert set(result["couple_cs_signal"].unique()).issubset(valid)
    assert set(result["ema_cross_signal"].unique()).issubset(valid)


def test_extract_features_candlestick_non_negative():
    result = extract_features(make_ohlcv(300))
    assert (result["height"] >= 0).all()
    assert (result["upwick"] >= 0).all()
    assert (result["lowwick"] >= 0).all()


def test_extract_features_missing_columns_raises():
    df = pd.DataFrame({"Close": [100.0, 101.0], "Volume": [1000.0, 1100.0]})
    df.index = pd.date_range("2024-01-02 09:05", periods=2, freq="5min")
    with pytest.raises(ValueError):
        extract_features(df)


def test_extract_features_negative_price_raises():
    df = make_ohlcv(50)
    df.iloc[5, df.columns.get_loc("Close")] = -1.0
    df.iloc[5, df.columns.get_loc("Low")]   = -1.0
    with pytest.raises(ValueError):
        extract_features(df)
