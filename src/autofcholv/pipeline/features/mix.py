import os

import numpy as np
import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate mixed/combined features.
    Feature definitions follow mix.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    cols = ['body_lag1', 'open_lag1', 'close_lag1', 'high_lag1', 'low_lag1', 'volume_lag1', 'ibs', 'ibs_lag1']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    ibs_n        = int(os.getenv("IBS_LOOKBACK", 5))
    volatility_n = int(os.getenv("VOLATILITY_LOOKBACK", 24))
    one_day_bars = int(os.getenv("ONE_DAY_BARS", 49))

    rolling_low  = df["Low"].rolling(ibs_n).min()
    rolling_high = df["High"].rolling(ibs_n).max()
    denom        = rolling_high - rolling_low
    df["ibs_n"]  = np.where(denom != 0, (df["Close"] - rolling_low) / denom, np.nan)

    high_lag2    = df["High"].shift(2)
    low_lag2     = df["Low"].shift(2)
    df["is_fvg"] = (high_lag2 < df["Low"]) | (low_lag2 > df["High"])

    ulti = ta.uo(df["High"], df["Low"], df["Close"], fast=volatility_n // 2,
                 medium=volatility_n, slow=volatility_n * 2)
    if ulti is not None and not ulti.empty:
        df["ulti_osci"] = ulti.values

    vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
    if vwap is not None and not vwap.empty:
        df["vwap"] = vwap.values

    atr = ta.atr(df["High"], df["Low"], df["Close"], length=volatility_n)
    if atr is not None and not atr.empty:
        df["atr"] = atr.values

    adx_result = ta.adx(df["High"], df["Low"], df["Close"], length=volatility_n)
    if adx_result is not None and not adx_result.empty:
        df["adx"] = adx_result.iloc[:, 0].values

    midpoint = (df["High"] + df["Low"]) / 2
    df["dm"] = midpoint - midpoint.shift(1)

    hl_range  = df["High"] - df["Low"]
    vbr       = np.where(hl_range != 0, df["Volume"] / hl_range, np.nan)
    df["eom"] = np.where(vbr != 0, df["dm"] / vbr, np.nan)

    df["direction"] = np.where(df["Close"] > df["Open"], 1, -1)

    direction = df["direction"].to_numpy()
    streak    = np.zeros(len(direction), dtype=int)
    for i in range(1, len(direction)):
        if direction[i] == direction[i - 1]:
            streak[i] = direction[i] + streak[i - 1]
        else:
            streak[i] = 0
    df["streak"] = streak

    prev_day_close   = df["Close"].shift(one_day_bars)
    df["custom_001"] = 100.0 * (df["Close"] - prev_day_close) / prev_day_close

    close_n          = df["Close"].shift(one_day_bars)
    high_n           = df["High"].rolling(one_day_bars).max()
    low_n            = df["Low"].rolling(one_day_bars).min()
    denom2           = high_n - low_n
    df["custom_002"] = np.where(denom2 != 0, (df["Close"] - close_n) / denom2, np.nan)

    return df
