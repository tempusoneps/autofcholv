import numpy as np
import pandas as pd
import pytest
from autofcholv.config.config import Config
from autofcholv.pipeline.features.liquidity import extract_features


def make_liquidity_test_df(n: int = 100) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range("2026-01-01", periods=n, freq="5min")
    close = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.random.uniform(0.1, 1.0, size=n)
    low = close - np.random.uniform(0.1, 1.0, size=n)
    open_ = low + np.random.uniform(0.0, 1.0, size=n) * (high - low)
    volume = np.random.randint(100, 10000, size=n).astype(float)
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        }
    )


def test_liquidity_proxies_columns_exist():
    df = make_liquidity_test_df(100)
    config = Config(volume_lookback=24)
    result = extract_features(df, config)

    expected_cols = [
        "corwin_schultz_spread",
        "roll_spread",
        "kyles_lambda",
        "amihud_illiq",
        "amihud_zscore",
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing column {col}"
        valid = result[col].dropna()
        assert len(valid) > 0, f"Column {col} has only NaNs"
        assert np.isfinite(valid).all(), f"Column {col} contains inf values"

    # Specific property assertions
    assert (result["corwin_schultz_spread"].dropna() >= 0.0).all()
    assert (result["roll_spread"].dropna() >= 0.0).all()
    assert (result["amihud_illiq"].dropna() >= 0.0).all()


def test_liquidity_proxies_edge_cases_zero_volume_flat_price():
    df = make_liquidity_test_df(50)
    # inject zero volumes and flat prices
    df.loc[10:15, "Volume"] = 0.0
    df.loc[20:25, "High"] = 100.0
    df.loc[20:25, "Low"] = 100.0
    df.loc[20:25, "Open"] = 100.0
    df.loc[20:25, "Close"] = 100.0
    config = Config(volume_lookback=24)
    result = extract_features(df, config)
    for col in ["corwin_schultz_spread", "roll_spread", "kyles_lambda", "amihud_illiq", "amihud_zscore"]:
        assert col in result.columns
        valid = result[col].dropna()
        assert np.isfinite(valid).all(), f"Col {col} has inf on zero volume / flat price"
