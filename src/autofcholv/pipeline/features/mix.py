import numpy as np
import pandas as pd
import pandas_ta as ta


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
_BB_WINDOW = 20
_BB_STD_MULT = 1.5
_STREAK_WINDOW = 100   # max look-back for streak counting


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def _hurst_exponent(series: pd.Series) -> float:
    """
    Tính Hurst Exponent bằng phương pháp R/S analysis.
    Trả về 0.5 nếu không đủ dữ liệu hoặc bị lỗi.
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
        log_tau = np.log(tau)
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
    tp_vol = typical * df["Volume"]
    date_key = df.index.date
    cumvol = df.groupby(date_key)["Volume"].cumsum()
    cumtp = tp_vol.groupby(date_key).cumsum()
    return cumtp / cumvol


# ─────────────────────────────────────────────
# Main feature extractor
# ─────────────────────────────────────────────

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán tất cả features được định nghĩa trong mix.json.

    Features:
        Candlestick geometry:
            body, upper_wick, lower_wick,
            upper_wick_ratio, lower_wick_ratio, candlestick_height,
            ibs, clv, cbr, candle_color

        Pattern / position:
            is_fvg, is_lower_low_higher_volume,
            high_position, low_position, is_bb_rejection

        Indicators (pandas_ta):
            ATR14, ADX14, VWAP

        Trend / momentum (derived):
            EMA20_slope, z_score,
            pct_change, skew_100, kurt_100,
            typical_price,
            DM, VBR, EOM,
            keltner_channel (upper band),
            hurst_exponent, hurst_exponent_100,
            parkinson_vol_20,
            up_streak, down_streak

        Bollinger Bands:
            BB_middle, BB_std, BB_upper

        Custom features:
            fea_g1_001, fea_g1_002

    Args:
        df: DataFrame với DatetimeIndex chứa các cột:
            Open, High, Low, Close, Volume.
            Nếu close.py đã chạy trước, EMA20 cũng sẵn có.

    Returns:
        DataFrame được bổ sung các cột features mới.
    """

    # ── Candlestick geometry ──────────────────────────────────────
    df["candlestick_height"] = df["High"] - df["Low"]

    df["body"] = (df["Close"] - df["Open"]).abs()

    df["upper_wick"] = df["High"] - df[["Open", "Close"]].max(axis=1)
    df["lower_wick"] = df[["Open", "Close"]].min(axis=1) - df["Low"]

    hl_safe = df["candlestick_height"].replace(0, np.nan)
    df["upper_wick_ratio"] = (df["upper_wick"] / hl_safe).round(4)
    df["lower_wick_ratio"] = (df["lower_wick"] / hl_safe).round(4)

    # IBS – Internal Bar Strength
    df["ibs"] = ((df["Close"] - df["Low"]) / hl_safe).where(hl_safe.notna(), 1.0)

    # CLV – Close Location Value
    df["clv"] = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl_safe

    # CBR – Candlestick Body Ratio
    df["cbr"] = (df["body"] / hl_safe).round(4)

    # Candle color
    df["candle_color"] = np.where(
        df["Open"] == df["Close"], "doji",
        np.where(df["Close"] > df["Open"], "green", "red")
    )

    # ── Bollinger Bands (needed by several features below) ───────
    df["BB_middle"] = df["Close"].rolling(_BB_WINDOW).mean()
    df["BB_std"]    = df["Close"].rolling(_BB_WINDOW).std()
    df["BB_upper"]  = df["BB_middle"] + _BB_STD_MULT * df["BB_std"]
    bb_lower        = df["BB_middle"] - _BB_STD_MULT * df["BB_std"]

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
    df["high_position"] = np.where(df["High"] > df["BB_upper"], "> upper BB", "< upper BB")

    # Low position vs Bollinger lower band
    df["low_position"] = np.where(df["Low"] < bb_lower, "< lower BB", "> lower BB")

    # BB rejection: Close vẫn nằm dưới BB upper (từ chối phá vỡ)
    df["is_bb_rejection"] = df["Close"] < df["BB_upper"]

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
    # EMA20_slope – dùng EMA20 từ close.py nếu đã có, không thì tính lại
    if "EMA20" not in df.columns:
        df["EMA20"] = ta.ema(df["Close"], length=20)
    df["EMA20_slope"] = df["EMA20"] - df["EMA20"].shift(1)

    # Z-score của Close
    df["z_score"] = (df["Close"] - df["BB_middle"]) / df["BB_std"]

    # Percentage change
    df["pct_change"] = df["Close"].pct_change()

    # Skewness & Kurtosis of pct_change rolling 100
    df["skew_100"] = df["pct_change"].rolling(100).skew()
    df["kurt_100"] = df["pct_change"].rolling(100).kurt()

    # Typical price
    df["typical_price"] = (df["High"] + df["Low"] + df["Close"]) / 3

    # ── Ease of Movement (EOM) ────────────────────────────────────
    mid_point = (df["High"] + df["Low"]) / 2
    df["DM"]  = mid_point - mid_point.shift(1)                  # Distance Moved
    df["VBR"] = df["Volume"] / hl_safe                           # Volume Box Ratio
    df["EOM"] = df["DM"] / df["VBR"]                            # Ease of Movement

    # ── Keltner Channel upper band ────────────────────────────────
    # Upper = EMA20 + ATR14
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
    # fea_g1_001: 100 * (Close - day_close.shift(1)) / day_close.shift(1)
    # Dùng Close của phiên cuối ngày (resample daily last)
    if isinstance(df.index, pd.DatetimeIndex):
        day_close = df["Close"].resample("D").last().reindex(
            df.index, method="ffill"
        )
        prev_day_close = day_close.groupby(day_close.index.date).transform("first").shift(1)
        # Dùng shift trên daily rồi map lại intraday
        daily_last = df["Close"].resample("D").last()
        daily_prev = daily_last.shift(1)
        prev_day_close_mapped = daily_prev.reindex(df.index, method="ffill")
        df["fea_g1_001"] = 100 * (df["Close"] - prev_day_close_mapped) / prev_day_close_mapped
    else:
        df["fea_g1_001"] = np.nan

    # fea_g1_002: (Close - close.shift(49)) / (max_high_49bars - min_low_49bars)
    rolling_max_high = df["High"].rolling(49).max()
    rolling_min_low  = df["Low"].rolling(49).min()
    denom = (rolling_max_high - rolling_min_low).replace(0, np.nan)
    df["fea_g1_002"] = (df["Close"] - df["Close"].shift(49)) / denom

    return df
