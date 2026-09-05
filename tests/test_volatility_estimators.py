import numpy as np
import pandas as pd
import pytest
from autofcholv.config.config import Config
from autofcholv.pipeline.features.volatility import (
    extract_features,
    calc_parkinson_vol,
    calc_garman_klass_vol,
    calc_rogers_satchell_vol,
    calc_yang_zhang_vol,
)


def make_test_df(n: int = 100) -> pd.DataFrame:
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
    # Bolling band dependencies for downstream features in volatility.py
    df["ub"] = high
    df["lb"] = low
    df["mb"] = close
    return df


def test_volatility_estimators_columns_exist():
    df = make_test_df(100)
    config = Config(volatility_lookback=24)
    result = extract_features(df, config)

    expected_cols = [
        "parkinson_vol",
        "garman_klass_vol",
        "rogers_satchell_vol",
        "yang_zhang_vol",
        "volatility_ratio_yz",
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing column {col}"
        valid = result[col].dropna()
        assert len(valid) > 0, f"Column {col} has only NaNs"
        assert (valid >= 0.0).all(), f"Column {col} contains negative values"
        assert np.isfinite(valid).all(), f"Column {col} contains inf values"


def test_individual_estimators_functions():
    df = make_test_df(50)
    window = 10

    pv = calc_parkinson_vol(df, window)
    gk = calc_garman_klass_vol(df, window)
    rs = calc_rogers_satchell_vol(df, window)
    yz = calc_yang_zhang_vol(df, window)

    for name, series in [
        ("parkinson", pv),
        ("garman_klass", gk),
        ("rogers_satchell", rs),
        ("yang_zhang", yz),
    ]:
        assert len(series) == len(df), f"{name} length mismatch"
        valid = series.dropna()
        assert len(valid) > 0, f"{name} has only NaNs"
        assert (valid >= 0.0).all(), f"{name} contains negative values"
        assert np.isfinite(valid).all(), f"{name} contains inf values"


def test_estimators_constant_prices():
    n = 30
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=n, freq="5min"),
            "Open": np.full(n, 100.0),
            "High": np.full(n, 100.0),
            "Low": np.full(n, 100.0),
            "Close": np.full(n, 100.0),
            "Volume": np.full(n, 1000.0),
        }
    )
    window = 5
    pv = calc_parkinson_vol(df, window).dropna()
    gk = calc_garman_klass_vol(df, window).dropna()
    rs = calc_rogers_satchell_vol(df, window).dropna()
    yz = calc_yang_zhang_vol(df, window).dropna()

    assert np.allclose(pv, 0.0, atol=1e-5)
    assert np.allclose(gk, 0.0, atol=1e-5)
    assert np.allclose(rs, 0.0, atol=1e-5)
    assert np.allclose(yz, 0.0, atol=1e-5)


def test_estimators_small_window_and_edge_cases():
    df = make_test_df(20)
    for window in [1, 2]:
        pv = calc_parkinson_vol(df, window)
        gk = calc_garman_klass_vol(df, window)
        rs = calc_rogers_satchell_vol(df, window)
        yz = calc_yang_zhang_vol(df, window)

        for s in [pv, gk, rs, yz]:
            valid = s.dropna()
            assert (valid >= 0.0).all()
            assert np.isfinite(valid).all()


def test_volatility_lookback_config():
    df1 = make_test_df(50)
    df2 = df1.copy()
    res1 = extract_features(df1, Config(volatility_lookback=10))
    res2 = extract_features(df2, Config(volatility_lookback=20))

    # Different lookbacks should produce different results
    assert not np.allclose(
        res1["parkinson_vol"].dropna().values[-10:],
        res2["parkinson_vol"].dropna().values[-10:],
    )
    assert not np.allclose(
        res1["yang_zhang_vol"].dropna().values[-10:],
        res2["yang_zhang_vol"].dropna().values[-10:],
    )
