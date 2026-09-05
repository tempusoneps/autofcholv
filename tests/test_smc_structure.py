import numpy as np
import pandas as pd
import pytest
from autofcholv.config.config import Config
from autofcholv.pipeline.features.mix import extract_features


def make_mix_test_df(n: int = 100) -> pd.DataFrame:
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
    # Required lag and indicator columns for mix.py
    df["body"] = (df["Close"] - df["Open"]).abs()
    df["body_lag1"] = df["body"].shift(1)
    df["open_lag1"] = df["Open"].shift(1)
    df["close_lag1"] = df["Close"].shift(1)
    df["high_lag1"] = df["High"].shift(1)
    df["low_lag1"] = df["Low"].shift(1)
    df["volume_lag1"] = df["Volume"].shift(1)
    df["ibs"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-8)
    df["ibs_lag1"] = df["ibs"].shift(1)
    df["vbr"] = df["Volume"] / (df["High"] - df["Low"] + 1e-8)
    df["roc_close"] = df["Close"].pct_change()
    return df


def test_smc_structure_columns_exist():
    df = make_mix_test_df(100)
    config = Config(short_lookback=10)
    result = extract_features(df, config)

    expected_cols = [
        "liquidity_sweep_high",
        "liquidity_sweep_low",
        "fvg_bullish",
        "fvg_bearish",
        "fvg_gap_pct",
        "equal_highs",
        "equal_lows",
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing column {col}"

    assert result["liquidity_sweep_high"].dtype == bool
    assert result["liquidity_sweep_low"].dtype == bool
    assert result["fvg_bullish"].dtype == bool
    assert result["fvg_bearish"].dtype == bool
    assert (result["fvg_gap_pct"].dropna() >= 0.0).all()
    assert result["equal_highs"].dtype == bool
    assert result["equal_lows"].dtype == bool


def test_smc_structure_logic():
    # Construct a small deterministic dataframe
    dates = pd.date_range("2026-01-01", periods=10, freq="5min")
    # bar 0: H=100, L=90, C=95, O=92
    # bar 1: H=100.02 (equal high to bar 0: diff 0.02% <= 0.05%), L=90.01 (equal low: diff 0.01% <= 0.05%), C=95, O=92
    # bar 2: Bullish FVG: Low=102 > bar 0 High=100. H=110, C=105, O=103
    # bar 3: Bearish FVG setup: bar 2 Low=102. bar 4 High=101 < bar 2 Low=102.
    df = pd.DataFrame({
        "Date": dates,
        "Open":   [92.0,  92.0,   103.0, 95.0,  90.0,  98.0,  95.0, 95.0, 95.0, 95.0],
        "High":   [100.0, 100.02, 110.0, 96.0,  101.0, 106.0, 96.0, 96.0, 96.0, 96.0],
        "Low":    [90.0,  90.01,  102.0, 94.0,  88.0,  85.0,  94.0, 94.0, 94.0, 94.0],
        "Close":  [95.0,  95.0,   105.0, 95.0,  89.0,  94.0,  95.0, 95.0, 95.0, 95.0],
        "Volume": [1000.0] * 10,
    })
    df["body"] = (df["Close"] - df["Open"]).abs()
    df["body_lag1"] = df["body"].shift(1)
    df["open_lag1"] = df["Open"].shift(1)
    df["close_lag1"] = df["Close"].shift(1)
    df["high_lag1"] = df["High"].shift(1)
    df["low_lag1"] = df["Low"].shift(1)
    df["volume_lag1"] = df["Volume"].shift(1)
    df["ibs"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-8)
    df["ibs_lag1"] = df["ibs"].shift(1)
    df["vbr"] = df["Volume"] / (df["High"] - df["Low"] + 1e-8)
    df["roc_close"] = df["Close"].pct_change()

    config = Config(short_lookback=3)
    res = extract_features(df, config)

    # Bar 1 should have equal highs and lows to Bar 0
    assert res.loc[1, "equal_highs"] == True
    assert res.loc[1, "equal_lows"] == True

    # Bar 2: Low (102.0) > Bar 0 High (100.0) -> Bullish FVG
    assert res.loc[2, "fvg_bullish"] == True
    assert res.loc[2, "fvg_bearish"] == False
    assert np.isclose(res.loc[2, "fvg_gap_pct"], (102.0 - 100.0) / (105.0 + 1e-8))

    # Bar 4: High (101.0) < Bar 2 Low (102.0) -> Bearish FVG
    assert res.loc[4, "fvg_bearish"] == True
    assert res.loc[4, "fvg_bullish"] == False
    assert np.isclose(res.loc[4, "fvg_gap_pct"], (102.0 - 101.0) / (89.0 + 1e-8))

    # Bar 5: Lookback=3 (bars 2, 3, 4).
    # Prior swing high = max(High[2,3,4]) = max(110, 96, 101) = 110.0.
    # Bar 5 High = 106 < 110 -> not a sweep of 110.
    # But prior swing low = min(Low[2,3,4]) = min(102, 94, 88) = 88.0.
    # Bar 5 Low = 85.0 < 88.0, and Close = 94.0 > 88.0 -> Liquidity sweep low!
    assert res.loc[5, "liquidity_sweep_low"] == True
    assert res.loc[5, "liquidity_sweep_high"] == False

