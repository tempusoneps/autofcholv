import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df['High_Volume_group'] = df.apply(lambda r: get_high_volume_group(r) , axis=1)  
    df['Low_Volume_group'] = df.apply(lambda r: get_low_volume_group(r) , axis=1)  
    df['Volume_group'] = df.apply(lambda r: "Tang" if r["Volume"] > r["prev_Vol"] else "Giam", axis=1)
    df["price_vs_body_group"] = df.apply(lambda r: price_vs_body_group(r) , axis=1)
    df['upper_wick_group'] = df.apply(lambda r: "Tang" if r["upper_wick"] > r["prev_upper_wick"] else "Giam(or Bang)", axis=1)
    df["ibs_vol_group"] = df.apply(lambda r: get_ibs_vol_group(r) , axis=1)
    df['Volume_avg_group'] = df.apply(lambda r: "Tang" if r["avg20_Volume"] > r["prev_avg20_Volume"] else "Giam", axis=1)
    df['High_and_RSI_group'] = df.apply(lambda r: True if (r["High"] > r["prev_High"] and r["RSI20"] > r["prev_RSI20"]) else False, axis=1)
    df['Close_price_group'] = df.apply(lambda r: get_close_price_position(r), axis=1) 
    df['Open_price_group'] = df.apply(lambda r: get_open_price_position(r), axis=1)
    df['lower_wick_group'] = df.apply(
        lambda r: 1 if r["lower_shadow"] > r["prev_lower_shadow"] else -1, axis=1)
    return df


def get_high_volume_group(r):
    group = ""
    if r["Volume"] > r["prev_Vol"]:
        group = "VolUp"
    elif r["Volume"] == r["prev_Vol"]:
        group = "VolEqual"
    else:
        group = "VolDown"
    if r["High"] > r["prev_High"]:
        group = group + "_HighUp"
    elif r["High"] == r["prev_High"]:
        group = group + "_HighEqual"
    else:
        group = group + "_HighDown"
    return group


def get_low_volume_group(r):
    group = ""
    if r["Volume"] > r["prev_Vol"]:
        group = "VolUp"
    elif r["Volume"] == r["prev_Vol"]:
        group = "VolEqual"
    else:
        group = "VolDown"
    if r["Low"] < r["prev_Low"]:
        group = group + "_LowDown"
    elif r["Low"] == r["prev_Low"]:
        group = group + "_LowEqual"
    else:
        group = group + "_LowUp"
    return group


def get_open_price_position(r):
    if r["Open"] > r["prev_Close"]:
        return "Open > prev_Close"
    if r["Open"] == r["prev_Close"]:
        return "Open = prev_Close"
    if r["Open"] < r["prev_Close"]:
        return "Open < prev_Close"


def get_close_price_position(r):
    if r["Close"] > r["prev_High"]:
        return "> prev High"
    if r["Close"] > max(r["prev_Close"], r["prev_Open"]):
        return "Bong nen tren "
    if max(r["prev_Close"], r["prev_Open"]) > r["Close"] > min(r["prev_Close"], r["prev_Open"]):
        return "Than nen"
    if r["Close"] < min(r["prev_Close"], r["prev_Open"]):
        return "Bong nen duoi"
    if r["Close"] < r["prev_Low"]:
        return "< prev Low"  


def get_ibs_vol_group(r):
    if r["Volume"] > r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
        return "Vol up, ibs incre"
    if r["Volume"] > r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
        return "Vol up, ibs decr"
    if r["Volume"] < r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
        return "Vol down, ibs incre"
    if r["Volume"] < r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
        return "Vol down, ibs decr"

    
def price_vs_body_group(r):
    if r["Close"] > r["prev_Close"] and r["body"] > r["prev_body"]:
        return "Gia tang, body tang"
    if r["Close"] > r["prev_Close"] and r["body"] < r["prev_body"]:
        return "Gia tang, body giam"
    if r["Close"] < r["prev_Close"] and r["body"] > r["prev_body"]:
        return "Gia giam, body tang"
    if r["Close"] < r["prev_Close"] and r["body"] < r["prev_body"]:
        return "Gia giam, body giam"
