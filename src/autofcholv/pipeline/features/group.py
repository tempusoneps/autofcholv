import pandas as pd
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

    return df
