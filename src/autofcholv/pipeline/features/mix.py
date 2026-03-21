import numpy as np
import pandas as pd
import pandas_ta as ta


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
_BB_WINDOW   = 20
_BB_STD_MULT = 1.5


# ─────────────────────────────────────────────
# Main feature extractor
# ─────────────────────────────────────────────

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán tất cả features được định nghĩa trong mix.json.

    Args:
        df: DataFrame với DatetimeIndex chứa Open, High, Low, Close, Volume.

    Returns:
        DataFrame được bổ sung các cột features mới.
    """

    cols = ['cs_body_lag1', 'open_lag1', 'close_lag1', 'high_lag1', 'low_lag1', 'volume_lag1', 'cs_ibs', 'cs_ibs_lag1']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        print("Missing:", missing_cols)
        return df

    hl_safe = (df["High"] - df["Low"]).replace(0, np.nan)

    # ── Bollinger Bands (dùng nội bộ cho các features bên dưới) ──
    bb_middle = df["Close"].rolling(_BB_WINDOW).mean()
    bb_std    = df["Close"].rolling(_BB_WINDOW).std()
    bb_upper  = bb_middle + _BB_STD_MULT * bb_std
    bb_lower  = bb_middle - _BB_STD_MULT * bb_std

    # ── cs_ibs_n: (Close - lowest_n) / (highest_n - lowest_n) ───
    # Dùng n = ONE_DAY_BARS từ env (mặc định 49)
    _n = int(pd.options.mode.copy_on_write and 49 or 49)  # placeholder, default 49
    try:
        import os
        _n = int(os.environ.get("ONE_DAY_BARS", 49))
    except (ValueError, TypeError):
        _n = 49
    rolling_high_n = df["High"].rolling(_n).max()
    rolling_low_n  = df["Low"].rolling(_n).min()
    denom_ibs_n    = (rolling_high_n - rolling_low_n).replace(0, np.nan)
    df["cs_ibs_n"] = (df["Close"] - rolling_low_n) / denom_ibs_n

    # ── Pattern / position ────────────────────────────────────────
    # Fair Value Gap: nến hiện tại tạo khoảng trống với 2 nến trước
    df["is_fvg"] = (
        (df["Low"] > df["High"].shift(2)) |
        (df["High"] < df["Low"].shift(2))
    )

    # Đáy thấp hơn với volume cao hơn (Lower Low + Higher Volume)
    df["is_lower_low_higher_volume"] = (
        (df["Low"] < df["Low"].shift(1)) &
        (df["Volume"] > df["Volume"].shift(1))
    )

    # High position vs Bollinger upper band
    df["high_position"] = np.where(df["High"] > bb_upper, "> upper BB", "< upper BB")

    # Low position vs Bollinger lower band
    df["low_position"] = np.where(df["Low"] < bb_lower, "< lower BB", "> lower BB")

    # ── Indicators ────────────────────────────────────────────────
    # VWAP (reset hàng ngày)
    try:
        df["VWAP"] = _vwap_daily(df)
    except Exception:
        df["VWAP"] = np.nan

    # ATR14
    df["ATR14"] = ta.atr(df["High"], df["Low"], df["Close"], length=14)

    # ADX14
    adx_df = ta.adx(df["High"], df["Low"], df["Close"], length=14)
    if adx_df is not None and "ADX_14" in adx_df.columns:
        df["ADX14"] = adx_df["ADX_14"]
    else:
        df["ADX14"] = np.nan

    # ── Trend / momentum ─────────────────────────────────────────
    # Z-score của Close
    df["z_score"] = (df["Close"] - bb_middle) / bb_std

    # Typical price
    df["typical_price"] = (df["High"] + df["Low"] + df["Close"]) / 3

    # ── Ease of Movement (EOM) ────────────────────────────────────
    mid_point   = (df["High"] + df["Low"]) / 2
    df["DM"]    = mid_point - mid_point.shift(1)   # Distance Moved
    df["VBR"]   = df["Volume"] / hl_safe            # Volume Box Ratio
    df["EOM"]   = df["DM"] / df["VBR"]             # Ease of Movement

    # ── Keltner Channel upper band ────────────────────────────────
    # Dùng EMA20 từ close.py nếu đã có, không thì tính lại
    if "EMA20" not in df.columns:
        df["EMA20"] = ta.ema(df["Close"], length=20)
    df["keltner_channel"] = df["EMA20"] + df["ATR14"]

    # ── Hurst Exponent ────────────────────────────────────────────
    df["hurst_exponent"]     = _rolling_hurst(df["Close"], window=10)
    df["hurst_exponent_100"] = _rolling_hurst(df["Close"], window=100)

    # ── Parkinson Volatility ──────────────────────────────────────
    df["parkinson_vol_20"] = _parkinson_vol(df["High"], df["Low"], window=20)

    # ── Streak counters ───────────────────────────────────────────
    df["up_streak"]   = _up_streak(df["Close"])
    df["down_streak"] = _down_streak(df["Close"])

    # ── Custom features ───────────────────────────────────────────
    # fea_g1_001: 100 * (Close - prev_day_close) / prev_day_close
    if isinstance(df.index, pd.DatetimeIndex):
        daily_last            = df["Close"].resample("D").last()
        daily_prev            = daily_last.shift(1)
        prev_day_close_mapped = daily_prev.reindex(df.index, method="ffill")
        df["fea_g1_001"] = 100 * (df["Close"] - prev_day_close_mapped) / prev_day_close_mapped
    else:
        df["fea_g1_001"] = np.nan

    # fea_g1_002: (Close - close.shift(49)) / (max_high_49 - min_low_49)
    rolling_max_high = df["High"].rolling(49).max()
    rolling_min_low  = df["Low"].rolling(49).min()
    denom_g2         = (rolling_max_high - rolling_min_low).replace(0, np.nan)
    df["fea_g1_002"] = (df["Close"] - df["Close"].shift(49)) / denom_g2

    return df


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def _hurst_exponent(series: pd.Series) -> float:
    """
    Tính Hurst Exponent bằng phương pháp R/S analysis.
    Trả về np.nan nếu không đủ dữ liệu hoặc bị lỗi.
    """
    n = len(series)
    if n < 4:
        return np.nan
    try:
        lags = range(2, max(3, n // 2))
        tau = []
        for lag in lags:
            diff = series[lag:].values - series[:-lag].values
            if len(diff) == 0 or np.std(diff) == 0:
                continue
            tau.append(np.std(diff))
        if len(tau) < 2:
            return np.nan
        log_lags = np.log(list(lags[: len(tau)]))
        log_tau  = np.log(tau)
        poly = np.polyfit(log_lags, log_tau, 1)
        return poly[0]
    except Exception:
        return np.nan


def _rolling_hurst(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).apply(_hurst_exponent, raw=False)


def _parkinson_vol(high: pd.Series, low: pd.Series, window: int = 20) -> pd.Series:
    """
    Parkinson Volatility = sqrt( 1/(4*ln2) * rolling_mean( (ln(H/L))^2 ) )
    """
    log_hl = np.log(high / low) ** 2
    factor = 1.0 / (4.0 * np.log(2))
    return np.sqrt(factor * log_hl.rolling(window).mean())


def _up_streak(close: pd.Series) -> pd.Series:
    """Số nến tăng liên tiếp tính từ nến hiện tại về trước."""
    result = np.zeros(len(close), dtype=int)
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i - 1]:
            result[i] = result[i - 1] + 1
        else:
            result[i] = 0
    return pd.Series(result, index=close.index)


def _down_streak(close: pd.Series) -> pd.Series:
    """Số nến giảm liên tiếp tính từ nến hiện tại về trước."""
    result = np.zeros(len(close), dtype=int)
    for i in range(1, len(close)):
        if close.iloc[i] < close.iloc[i - 1]:
            result[i] = result[i - 1] + 1
        else:
            result[i] = 0
    return pd.Series(result, index=close.index)


def _vwap_daily(df: pd.DataFrame) -> pd.Series:
    """
    VWAP reset theo từng ngày giao dịch.
    Yêu cầu DatetimeIndex.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    tp_vol   = typical * df["Volume"]
    date_key = df.index.date
    cumvol   = df.groupby(date_key)["Volume"].cumsum()
    cumtp    = tp_vol.groupby(date_key).cumsum()
    return cumtp / cumvol
