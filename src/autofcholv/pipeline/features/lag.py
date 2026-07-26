import pandas as pd
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    """
    Calculate lag, shift, momentum acceleration, and volatility expansion features.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new lag and shift features.
    """
    # 1. Base OHLCV Lags
    df["close_lag1"] = df["Close"].shift(1)
    df["open_lag1"] = df["Open"].shift(1)
    df["high_lag1"] = df["High"].shift(1)
    df["low_lag1"] = df["Low"].shift(1)
    df["volume_lag1"] = df["Volume"].shift(1)

    # 2. Candlestick Geometry Lags
    if "body" in df.columns:
        df["body_lag1"] = df["body"].shift(1)
    if "upwick" in df.columns:
        df["upwick_lag1"] = df["upwick"].shift(1)
    if "lowwick" in df.columns:
        df["lowwick_lag1"] = df["lowwick"].shift(1)
    if "lowwick_rate" in df.columns:
        df["lowwick_rate_lag1"] = df["lowwick_rate"].shift(1)
    if "upwick_rate" in df.columns:
        df["upwick_rate_lag1"] = df["upwick_rate"].shift(1)
    if "clv" in df.columns:
        df["clv_lag1"] = df["clv"].shift(1)
    if "ibs" in df.columns:
        df["ibs_lag1"] = df["ibs"].shift(1)

    # 3. Momentum & Oscillator Lags & Acceleration Deltas
    if "rsi" in df.columns:
        df["rsi_lag1"] = df["rsi"].shift(1)
        df["rsi_delta"] = df["rsi"] - df["rsi_lag1"]
    if "macd_hist" in df.columns:
        df["macd_hist_lag1"] = df["macd_hist"].shift(1)
        df["macd_hist_delta"] = df["macd_hist"] - df["macd_hist_lag1"]
    if "kdj_j" in df.columns:
        df["kdj_j_lag1"] = df["kdj_j"].shift(1)

    # 4. Moving Average & Trend Lags
    if "ema_fast" in df.columns:
        df["ema_fast_lag1"] = df["ema_fast"].shift(1)
    if "ema_slow" in df.columns:
        df["ema_slow_lag1"] = df["ema_slow"].shift(1)
    vwap_col = "vwap" if "vwap" in df.columns else ("rolling_vwap" if "rolling_vwap" in df.columns else None)
    if vwap_col:
        df["vwap_lag1"] = df[vwap_col].shift(1)

    # 5. Volatility Lags & Volatility Expansion Metrics
    if "atr" in df.columns:
        df["atr_lag1"] = df["atr"].shift(1)
        df["volatility_expansion_ratio"] = (df["High"] - df["Low"]) / df["atr_lag1"].replace(0, pd.NA)
    bbw_col = "bbw" if "bbw" in df.columns else ("bollinger_width" if "bollinger_width" in df.columns else None)
    if bbw_col:
        df["bbw_lag1"] = df[bbw_col].shift(1)

    # 6. Volume Lags & Relative Volume Ratio
    if "volume_avg" in df.columns:
        df["volume_avg_lag1"] = df["volume_avg"].shift(1)
    df["volume_ratio_lag1"] = df["Volume"] / df["volume_lag1"].replace(0, pd.NA)

    return df
