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
        df["atr_pct"] = df["atr"] / df["Close"]

    adx_result = ta.adx(df["High"], df["Low"], df["Close"], length=volatility_n)
    if adx_result is not None and not adx_result.empty:
        df["adx"] = adx_result.iloc[:, 0].values

    midpoint = (df["High"] + df["Low"]) / 2
    df["dm"] = midpoint - midpoint.shift(1)

    df["eom"] = np.where(df["vbr"] != 0, df["dm"] / df["vbr"], np.nan)

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

    high_n           = df["High"].rolling(one_day_bars).max()
    low_n            = df["Low"].rolling(one_day_bars).min()
    denom2           = high_n - low_n
    df["custom_002"] = np.where(denom2 != 0, (df["Close"] - prev_day_close) / denom2, np.nan)

    channel_high = df["High"].rolling(volatility_n, min_periods=1).max()
    channel_low = df["Low"].rolling(volatility_n, min_periods=1).min()
    channel_mid = (channel_high + channel_low) / 2.0
    channel_width = channel_high - channel_low
    df["donchian_width"] = np.where(channel_mid != 0, channel_width / channel_mid, np.nan)
    df["donchian_position"] = np.where(
        channel_width != 0,
        (df["Close"] - channel_low) / channel_width,
        np.nan,
    )

    route_1 = 2.0 * (df["High"] - df["Low"]) + (df["Open"] - df["Close"])
    route_2 = 2.0 * (df["High"] - df["Low"]) + (df["Close"] - df["Open"])
    shortest_path = np.minimum(route_1, route_2)
    normalized_path = shortest_path / df["Open"]
    quote_volume_proxy = df["Close"] * df["Volume"]
    liquidity_premium = np.where(
        normalized_path != 0,
        quote_volume_proxy / normalized_path,
        np.nan,
    )
    df["amihud_liquidity"] = (
        pd.Series(liquidity_premium, index=df.index)
        .rolling(volatility_n, min_periods=2)
        .mean()
    )


    prev_close = df["Close"].shift(1)
    true_high = pd.concat([df["High"], prev_close], axis=1).max(axis=1)
    true_low = pd.concat([df["Low"], prev_close], axis=1).min(axis=1)
    true_range = true_high - true_low
    df["true_range_pct"] = true_range / df["Close"]
    df["gap_pct"] = (df["Open"] - prev_close) / prev_close
    df["range_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-8)
    df["body_to_true_range"] = df["body"].abs() / (true_range + 1e-8)

    keltner_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    keltner_range = 4.0 * df["atr"]
    df["keltner_position"] = np.where(
        keltner_range != 0,
        (df["Close"] - keltner_middle + 2.0 * df["atr"]) / keltner_range,
        np.nan,
    )

    return df
