import pandas as pd
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['cs_body_lag1', 'open_lag1', 'close_lag1', 'high_lag1', 'low_lag1', 'volume_lag1', 'cs_ibs', 'cs_ibs_lag1']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        print("Missing:", missing_cols)
        return df

    # states
    vol_state = np.where(df["Volume"] > df["volume_lag1"], "VolUp",
            np.where(df["Volume"] == df["volume_lag1"], "VolEqual", "VolDown"))

    high_state = np.where(df["High"] > df["high_lag1"], "HighUp",
                np.where(df["High"] == df["high_lag1"], "HighEqual", "HighDown"))
    low_state = np.where(df["Low"] < df["low_lag1"], "LowDown",
                np.where(df["Low"] == df["low_lag1"], "LowEqual", "LowUp"))
    body_state = np.where(df["cs_body"] > df["cs_body_lag1"], "BodyUp",
                np.where(df["cs_body"] == df["cs_body_lag1"], "BodyEqual", "BodyDown"))
    close_state = np.where(df["Close"] > df["close_lag1"], "CloseUp",
                np.where(df["Close"] == df["close_lag1"], "CloseEqual", "CloseDown"))

    # patterns & groups
    df['volume_group'] = vol_state
    df['volume_high_pattern'] = vol_state + "_" + high_state
    df['volume_low_pattern'] = vol_state + "_" + low_state
    df['price_body_pattern'] = close_state + "_" + body_state
    
    
    # upper_wick_group
    df['upper_wick_group'] = np.where(df["upper_wick"] > df["prev_upper_wick"], "Tang", "Giam(or Bang)")
    
    # ibs_vol_group
    cond_ibs = [
        (df["Volume"] > df["prev_Vol"]) & (df["ibs"] > df["prev_ibs"]),
        (df["Volume"] > df["prev_Vol"]) & (df["ibs"] < df["prev_ibs"]),
        (df["Volume"] < df["prev_Vol"]) & (df["ibs"] > df["prev_ibs"]),
        (df["Volume"] < df["prev_Vol"]) & (df["ibs"] < df["prev_ibs"])
    ]
    choice_ibs = [
        "Vol up, ibs incre",
        "Vol up, ibs decr",
        "Vol down, ibs incre",
        "Vol down, ibs decr"
    ]
    df["ibs_vol_group"] = np.select(cond_ibs, choice_ibs, default=None)
    
    # Volume_avg_group
    df['Volume_avg_group'] = np.where(df["avg20_Volume"] > df["prev_avg20_Volume"], "Tang", "Giam")
    
    # High_and_RSI_group
    df['High_and_RSI_group'] = (df["High"] > df["prev_High"]) & (df["RSI20"] > df["prev_RSI20"])
    
    # Close_price_group
    prev_max = np.maximum(df["prev_Close"], df["prev_Open"])
    prev_min = np.minimum(df["prev_Close"], df["prev_Open"])
    cond_close = [
        df["Close"] > df["prev_High"],
        df["Close"] > prev_max,
        (prev_max > df["Close"]) & (df["Close"] > prev_min),
        df["Close"] < prev_min,
        df["Close"] < df["prev_Low"]
    ]
    choice_close = [
        "> prev High",
        "Bong nen tren ",
        "Than nen",
        "Bong nen duoi",
        "< prev Low"
    ]
    df['Close_price_group'] = np.select(cond_close, choice_close, default=None)
    
    # Open_price_group
    cond_open = [
        df["Open"] > df["prev_Close"],
        df["Open"] == df["prev_Close"],
        df["Open"] < df["prev_Close"]
    ]
    choice_open = [
        "Open > prev_Close",
        "Open = prev_Close",
        "Open < prev_Close"
    ]
    df['Open_price_group'] = np.select(cond_open, choice_open, default=None)
    
    # lower_wick_group
    df['lower_wick_group'] = np.where(df["lower_shadow"] > df["prev_lower_shadow"], 1, -1)
    
    return df
