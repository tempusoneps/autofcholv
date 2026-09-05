import numpy as np
import pandas as pd
import pytest
from autofcholv.config.config import Config
from autofcholv.pipeline.features.volatility import extract_features


def make_regime_test_df(n: int = 120) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range("2026-01-01", periods=n, freq="5min")
    close = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.random.uniform(0.1, 1.0, size=n)
    low = close - np.random.uniform(0.1, 1.0, size=n)
    open_ = low + np.random.uniform(0.0, 1.0, size=n) * (high - low)
    volume = np.random.randint(100, 10000, size=n).astype(float)
    df = pd.DataFrame(
        {
            "Date": dates,
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        }
    )
    df["ub"] = high + 0.5
    df["lb"] = low - 0.5
    df["mb"] = close
    return df


def test_regime_squeeze_columns_exist():
    df = make_regime_test_df(120)
    config = Config(volatility_lookback=24, short_lookback=10, long_lookback=50)
    result = extract_features(df, config)

    expected_cols = [
        "squeeze_on",
        "squeeze_off",
        "squeeze_count",
        "squeeze_momentum",
        "hvr",
        "rvi_14",
        "is_choppy",
        "is_trending",
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing column {col}"

    assert result["squeeze_on"].dtype == bool
    assert result["squeeze_off"].dtype == bool
    assert (result["squeeze_on"] == ~result["squeeze_off"]).all()
    assert (result["squeeze_count"].dropna() >= 0).all()
    assert (result["hvr"].dropna() >= 0.0).all()
    assert ((result["rvi_14"].dropna() >= 0.0) & (result["rvi_14"].dropna() <= 100.0)).all()
    assert result["is_choppy"].dtype == bool
    assert result["is_trending"].dtype == bool


def test_regime_squeeze_values_and_types():
    df = make_regime_test_df(120)
    config = Config(volatility_lookback=24, short_lookback=10, long_lookback=50)
    result = extract_features(df, config)

    # is_choppy and is_trending cannot both be True simultaneously
    assert not (result["is_choppy"] & result["is_trending"]).any()

    # Squeeze momentum should be finite
    assert np.isfinite(result["squeeze_momentum"].dropna()).all()

    # Squeeze count should be non-negative
    assert (result["squeeze_count"] >= 0).all()
