import pandas as pd
import numpy as np
import pytest
from autofcholv.core import extract_features


# ─────────────────────────────────────────────
# Helper: tạo dữ liệu OHLCV 5-minute tổng hợp
# ─────────────────────────────────────────────

def make_ohlcv(n_bars: int = 300) -> pd.DataFrame:
    """
    Tạo DataFrame OHLCV với DatetimeIndex dạng 5-minute.
    Đảm bảo: High >= max(O,C), Low <= min(O,C), không có NaN, không có giá âm.
    """
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    # Loại bỏ các bar 11:30 và 14:30 (cleaning.py sẽ loại, nhưng tốt hơn là không đưa vào)
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]

    rng = np.random.default_rng(42)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    close = np.maximum(close, 10.0)

    open_  = close * (1 + rng.normal(0, 0.001, len(idx)))
    high   = close * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    low    = close * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    volume = rng.integers(1000, 10000, len(idx)).astype(float)

    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
    df.index.name = "Date"

    # Đảm bảo tính hợp lệ OHLC
    df["High"] = df[["Open", "Close", "High"]].max(axis=1)
    df["Low"]  = df[["Open", "Close", "Low"]].min(axis=1)

    return df


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_extract_features_returns_dataframe():
    """Đầu ra phải là DataFrame không rỗng."""
    result = extract_features(make_ohlcv(300))
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_extract_features_time_columns():
    """Kiểm tra các cột từ time.py."""
    result = extract_features(make_ohlcv(300))
    expected = ["hour", "minute", "day_of_month", "month", "year", "session_progress"]
    for col in expected:
        assert col in result.columns, f"Thiếu cột time: '{col}'"


def test_extract_features_resample_columns():
    """Kiểm tra các cột từ resample.py (daily aggregated)."""
    result = extract_features(make_ohlcv(300))
    expected = [
        "day_high", "day_low", "day_close", "day_open", "day_vol", "day_pivot",
        "prev_day_close", "prev_day_open", "prev_day_high", "prev_day_low",
        "prev_day_vol", "prev_day_pivot",
    ]
    for col in expected:
        assert col in result.columns, f"Thiếu cột resample: '{col}'"


def test_extract_features_candlestick_columns():
    """Kiểm tra các cột từ candlestick.py."""
    result = extract_features(make_ohlcv(300))
    expected = [
        "cs_body", "cs_height", "cs_upwick", "cs_lowwick",
        "cs_upwick_rate", "cs_lowwick_rate", "cs_ibs", "cs_color",
    ]
    for col in expected:
        assert col in result.columns, f"Thiếu cột candlestick: '{col}'"


def test_extract_features_close_columns():
    """Kiểm tra các cột từ close.py."""
    result = extract_features(make_ohlcv(300))
    expected = ["EMA20", "EMA250", "MB", "STD", "UB", "LB", "RSI20", "RSI10"]
    for col in expected:
        assert col in result.columns, f"Thiếu cột close: '{col}'"


def test_extract_features_mix_columns():
    """Kiểm tra các cột từ mix.py (theo mix.json)."""
    result = extract_features(make_ohlcv(300))
    expected = [
        "cs_ibs_n",
        "is_fvg", "is_lower_low_higher_volume",
        "high_position", "low_position",
        "VWAP", "ATR14", "ADX14",
        "z_score", "typical_price",
        "DM", "VBR", "EOM",
        "keltner_channel",
        "hurst_exponent", "hurst_exponent_100",
        "parkinson_vol_20",
        "up_streak", "down_streak",
        "fea_g1_001", "fea_g1_002",
    ]
    for col in expected:
        assert col in result.columns, f"Thiếu cột mix: '{col}'"


def test_extract_features_no_nan_in_ohlcv():
    """Các cột OHLCV gốc không được có NaN sau pipeline."""
    result = extract_features(make_ohlcv(300))
    assert result[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum() == 0


def test_extract_features_cs_color_values():
    """cs_color chỉ được chứa 'green', 'red', hoặc 'doji'."""
    result = extract_features(make_ohlcv(300))
    assert set(result["cs_color"].unique()).issubset({"green", "red", "doji"})


def test_extract_features_candlestick_non_negative():
    """cs_height, cs_upwick, cs_lowwick không được âm."""
    result = extract_features(make_ohlcv(300))
    assert (result["cs_height"] >= 0).all()
    assert (result["cs_upwick"] >= 0).all()
    assert (result["cs_lowwick"] >= 0).all()


def test_extract_features_missing_columns_raises():
    """Thiếu cột OHLCV phải raise ValueError."""
    df = pd.DataFrame({"Close": [100.0, 101.0], "Volume": [1000.0, 1100.0]})
    df.index = pd.date_range("2024-01-02 09:05", periods=2, freq="5min")
    with pytest.raises(ValueError):
        extract_features(df)


def test_extract_features_negative_price_raises():
    """Giá âm phải raise ValueError."""
    df = make_ohlcv(50)
    df.iloc[5, df.columns.get_loc("Close")] = -1.0
    df.iloc[5, df.columns.get_loc("Low")]   = -1.0
    with pytest.raises(ValueError):
        extract_features(df)
