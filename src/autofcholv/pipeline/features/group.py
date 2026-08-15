import pandas as pd
import pandas_ta as ta
import numpy as np
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    cols = ['high_lag1', 'low_lag1', 'volume_lag1', 'ibs', 'ibs_lag1',
            'upwick', 'lowwick', 'rsi_medium', 'rsi_medium_lag1', 'volume_avg', 'ub', 'lb']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    vol_state  = np.where(df["Volume"] > df["volume_lag1"], "VolUp", "VolDown")
    high_state = np.where(df["High"]   > df["high_lag1"],  "HighUp", "HighDown")
    ibs_state  = np.where(df["ibs"]    > df["ibs_lag1"],   "IBSUp",  "IBSDown")
    rsi_state  = np.where(df["rsi_medium"] > df["rsi_medium_lag1"], "RSIUp", "RSIDown")

    df['volume_group']     = vol_state
    df['upper_wick_group'] = np.where(df["upwick"] > df["upwick"].shift(1), "Increase", "Not Increase")
    df['lower_wick_group'] = np.where(df["lowwick"] > df["lowwick"].shift(1), "Longer", "Shorter")
    df['lower_shadow_group'] = np.where(df["lowwick"] > df["lowwick"].shift(1), "Increase", "Not Increase")

    df['vol_high_pattern']    = vol_state + "_" + high_state
    df['ibs_volume_pattern']  = vol_state + "_" + ibs_state
    df['volume_avg_group']    = np.where(df["Volume"] > df["volume_avg"], "VolAboveAvg", "VolBelowAvg")
    df['high_rsi_pattern']    = high_state + "_" + rsi_state
    df['high_ub_pattern']     = np.where(df["High"] > df["ub"], "HighAboveUB", "HighBelowUB")
    df['low_lb_pattern']      = np.where(df["Low"]  < df["lb"], "LowBelowLB",  "LowAboveLB")
    df["equal_low"] = (df["Low"] - df["low_lag1"]).abs() < (0.001 * df["Close"])
    df["equal_high"] = (df["High"] - df["high_lag1"]).abs() < (0.001 * df["Close"])
    df["inside_bar_prev"] = (df["high_lag1"] < df["High"].shift(2)) & (df["low_lag1"] > df["Low"].shift(2))

    # New features
    df['is_max_micro'] = df["High"] > df["High"].shift(1).rolling(max(2, config.micro_lookback - 2)).max()
    df['is_max_short'] = df["High"] > df["High"].shift(1).rolling(max(3, config.short_lookback - 1)).max()
    df['is_min_short'] = df["Low"] < df["Low"].shift(1).rolling(max(3, config.short_lookback - 1)).min()
    mfi_col = "mfi14" if "mfi14" in df.columns else ("mfi" if "mfi" in df.columns else None)
    if mfi_col:
        df['mfi_group'] = np.where(df[mfi_col] > df[mfi_col].shift(1), "Increase", "Not Increase")
    else:
        df['mfi_group'] = "Not Increase"

    df['higher_high_lower_vol'] = (df["High"] > df["high_lag1"]) & (df["Volume"] < df["volume_lag1"])
    df['lower_low_lower_vol'] = (df["Low"] < df["low_lag1"]) & (df["Volume"] < df["volume_lag1"])
    df['volume_higher_avg'] = df["Volume"] > df["volume_avg"]
    df['volume_vs_prev_vol'] = np.where(df["Volume"] > df["volume_lag1"], "Increase", "Not Increase")
    df['volume_avg_group'] = np.where(df["volume_avg"] > df["volume_avg"].shift(1), "Increase", "Not Increase")

    # close_price_group
    c_prev_max = np.maximum(df["close_lag1"], df["open_lag1"])
    c_prev_min = np.minimum(df["close_lag1"], df["open_lag1"])
    close_conds = [
        df["Close"] > df["high_lag1"],
        df["Close"] > c_prev_max,
        df["Close"] >= c_prev_min,
        df["Close"] >= df["low_lag1"],
        df["Close"] < df["low_lag1"]
    ]
    close_choices = ["> prev High", "Bong nen tren", "Than nen", "Bong nen duoi", "< prev Low"]
    df['close_price_group'] = np.select(close_conds, close_choices, default="< prev Low")

    # open_price_group
    open_conds = [
        df["Open"] > df["close_lag1"],
        df["Open"] == df["close_lag1"],
        df["Open"] < df["close_lag1"]
    ]
    open_choices = ["Open > prev_Close", "Open = prev_Close", "Open < prev_Close"]
    df['open_price_group'] = np.select(open_conds, open_choices, default="Open < prev_Close")

    # Bollinger band positions
    df['high_position'] = np.where(df["High"] > df["ub"], "> upper BB", "< upper BB")
    df['bb_rejection'] = (df["High"] > df["ub"]) & (df["Close"] < df["ub"])
    df['low_position'] = np.where(df["Low"] > df["lb"], "> lower BB", "<= lower BB")

    # ibs_vol_group
    vol_up = df["Volume"] > df["volume_lag1"]
    ibs_up = df["ibs"] > df["ibs_lag1"]
    ibs_conds = [
        vol_up & ibs_up,
        vol_up & (~ibs_up),
        (~vol_up) & ibs_up,
        (~vol_up) & (~ibs_up)
    ]
    ibs_choices = ["Vol up, ibs incre", "Vol up, ibs decr", "Vol down, ibs incre", "Vol down, ibs decr"]
    df['ibs_vol_group'] = np.select(ibs_conds, ibs_choices, default="Vol down, ibs decr")

    # rsi_area
    rsi_col = "rsi_medium" if "rsi_medium" in df.columns else ("rsi" if "rsi" in df.columns else None)
    rsi_val = df[rsi_col] if rsi_col else df["rsi_medium"]
    rsi_conds = [rsi_val > 55, rsi_val < 45]
    rsi_choices = [">55", "<45"]
    df['rsi_area'] = np.select(rsi_conds, rsi_choices, default="45-55")

    _1day_bars     = config.one_day_bars
    span_short     = min(_1day_bars * 22, max(5, len(df) // 4))
    span_long      = min(_1day_bars * 132, max(10, len(df)))
    ema_short      = df["Close"].ewm(span=span_short, adjust=False).mean()
    ema_long       = df["Close"].ewm(span=span_long, adjust=False).mean()
    df["long_trend"] = np.where(
        ema_short > ema_long,
        "StrongUp",
        "StrongDown"
    )

    return df
