import os
import pandas as pd
import pandas_ta as ta
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['high_lag1', 'low_lag1', 'volume_lag1', 'ibs', 'ibs_lag1',
            'upwick', 'lowwick', 'rsi', 'rsi_lag1', 'volume_avg', 'ub', 'lb']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    vol_state  = np.where(df["Volume"] > df["volume_lag1"], "VolUp", "VolDown")
    high_state = np.where(df["High"]   > df["high_lag1"],  "HighUp", "HighDown")
    ibs_state  = np.where(df["ibs"]    > df["ibs_lag1"],   "IBSUp",  "IBSDown")
    rsi_state  = np.where(df["rsi"]    > df["rsi_lag1"],   "RSIUp",  "RSIDown")

    df['volume_group']     = vol_state
    df['upper_wick_group'] = np.where(df["upwick"] > df["upwick"].shift(1), "Longer", "Shorter")
    df['lower_wick_group'] = np.where(df["lowwick"] > df["lowwick"].shift(1), "Longer", "Shorter")

    df['vol_high_pattern']    = vol_state + "_" + high_state
    df['ibs_volume_pattern']  = vol_state + "_" + ibs_state
    df['volume_avg_group']    = np.where(df["Volume"] > df["volume_avg"], "VolAboveAvg", "VolBelowAvg")
    df['high_rsi_pattern']    = high_state + "_" + rsi_state
    df['high_ub_pattern']     = np.where(df["High"] > df["ub"], "HighAboveUB", "HighBelowUB")
    df['low_lb_pattern']      = np.where(df["Low"]  < df["lb"], "LowBelowLB",  "LowAboveLB")

    _1day_bars     = int(os.getenv("ONE_DAY_BARS", 49))
    _1month_bars   = _1day_bars * 22
    _6month_bars   = _1month_bars * 6
    if len(df) < _6month_bars:
        raise ValueError(f"Not enough data to calculate long trend. Need {_6month_bars} bars, got {len(df)}")
    ema_1month = ta.ema(df["Close"], length=_1month_bars)
    ema_6month = ta.ema(df["Close"], length=_6month_bars)
    mask = ema_1month.notna() & ema_6month.notna()   
    df["long_trend"] = None
    df.loc[mask, "long_trend"] = np.where(
        ema_1month[mask] > ema_6month[mask],
        "StrongUp",
        "StrongDown"
    )

    return df
