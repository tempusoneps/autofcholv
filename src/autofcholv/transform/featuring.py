import os
from pathlib import Path
import numpy as np
import pandas as pd
import numpy as np
import pandas_ta as ta


OLD_1DAY_BARS = 51
CURRENT_1DAY_BARS = 49
SHORT_WINDOW = 20
LONG_WINDOW = 250


def feature_engineering(df):
    tmp_data = df.copy()
    tmp_data['DayHigh'] = tmp_data['High']
    tmp_data['DayLow'] = tmp_data['Low']
    tmp_data['DayClose'] = tmp_data['Close']
    tmp_data['DayOpen'] = tmp_data['Open']
    tmp_data['DayVol'] = tmp_data['Volume']
    daily_data = tmp_data.resample('D').agg({
            'DayHigh': 'max',
            'DayLow': 'min',
            'DayClose': 'last',
            'DayOpen': 'first',
            'DayVol': 'sum'
        })
    daily_data.dropna(subset=['DayHigh'], inplace=True)
    #
    data = df.copy()
    data = data.assign(time_d=pd.PeriodIndex(data.index, freq='1D').to_timestamp())
    #
    merged_data = pd.merge(data, daily_data, left_on="time_d", right_index=True, how="left")
    # Features
    merged_data['hour'] = merged_data.index.hour
    merged_data['minute'] = merged_data.index.minute
    merged_data["session_progress"] = ((merged_data.hour * 60 + merged_data.minute) - 9 * 60) / (51 * 5)
    merged_data["ema20"] = ta.ema(merged_data["Close"], length=20)
    merged_data["ema250"] = ta.ema(merged_data["Close"], length=250)
    merged_data['upper_wick'] = merged_data.apply(lambda r: r["High"] - max(r["Open"], r["Close"]), axis=1)
    merged_data['lower_shadow'] = merged_data.apply(lambda r: min(r["Open"], r["Close"]) - r["Low"], axis=1)
    merged_data['RSI20'] = ta.rsi(merged_data["Close"], length=20)
    merged_data['RSI10'] = ta.rsi(merged_data["Close"], length=10)
    merged_data['avg20_Volume'] = merged_data['Volume'].rolling(20).mean()
    merged_data["MB"] = merged_data["Close"].rolling(20).mean()
    merged_data["STD"] = merged_data["Close"].rolling(20).std()
    merged_data["UB"] = merged_data["MB"] + 1.5 * merged_data["STD"]
    merged_data["LB"] = merged_data["MB"] - 1.5 * merged_data["STD"]
    merged_data["MF"] = merged_data.apply(lambda r: get_mfm(r), axis=1)
    merged_data["MF3d_direction"] = merged_data["MF"].rolling(150).sum()
    merged_data["MF5d_direction"] = merged_data["MF"].rolling(250).sum()
    merged_data['HL_range'] = merged_data.apply(lambda r: (r["High"] - r["Low"]) * 1000 / r["Close"], axis=1)
    merged_data['candlestick_height'] = merged_data.apply(lambda r: r["High"] - r["Low"], axis=1)
    merged_data['volume_z'] = (merged_data['Volume'] - merged_data['Volume'].rolling(20).mean()) / merged_data['Volume'].rolling(20).std()
    merged_data['body'] = merged_data.apply(lambda r: r["Close"] - r["Open"], axis=1)
    merged_data['upper_wick_on_length'] = merged_data.apply(lambda r: 1 if r["candlestick_height"] == 0 else round(r["upper_wick"] * 100 / r["candlestick_height"], 3), axis=1)
    merged_data['lower_shadow_on_length'] = merged_data.apply(lambda r: 1 if r["candlestick_height"] == 0 else round(r["lower_shadow"] * 100 / r["candlestick_height"], 3), axis=1)
    merged_data['ibs'] = merged_data.apply(lambda r: 1 if r["High"] == r["Low"] else (r["Close"] - r["Low"]) / (r["High"] - r["Low"]), axis=1)
    merged_data['color'] = merged_data.apply(lambda r: 'doji' if r["Open"] == r["Close"] else ('green' if r["Open"] < r["Close"] else 'red'), axis=1)
    merged_data['is_FVG'] = (merged_data["Low"] > merged_data["High"].shift(2)) | (merged_data["High"] < merged_data["Low"].shift(2))
    merged_data['Volume_higher_avg'] = merged_data.apply(lambda r: True if r["Volume"] > r["avg20_Volume"] else False, axis=1)
    merged_data['High_position'] = merged_data.apply(lambda r: '> upper BB' if r["High"] > r["UB"] else '< upper BB', axis=1)
    merged_data["MFI_1d"] = ta.mfi(
        high=merged_data["High"],
        low=merged_data["Low"],
        close=merged_data["Close"],
        volume=merged_data["Volume"],
        length=50
    )
    merged_data["BB_rejection"] = merged_data.apply(lambda r: True if r["Close"] < r["UB"] else False, axis=1) 
    merged_data['Low_position'] = merged_data.apply(lambda r: 1 if r["Low"] < r["LB"] else -1, axis=1)
    # shift data
    merged_data['prev_High'] = merged_data['High'].shift(1)
    merged_data['prev_Low'] = merged_data['Low'].shift(1)
    merged_data['prev_Close'] = merged_data['Close'].shift(1)
    merged_data['prev_Open'] = merged_data['Open'].shift(1)
    merged_data['prev_Vol'] = merged_data['Volume'].shift(1)
    merged_data['prev_upper_wick'] = merged_data['upper_wick'].shift(1)
    merged_data['prev_avg20_Volume'] = merged_data['avg20_Volume'].shift(1)
    merged_data['prev_ema20'] = merged_data['ema20'].shift(1)
    merged_data['prev_ema250'] = merged_data['ema250'].shift(1)
    merged_data['prev_body'] = merged_data['body'].shift(1)
    merged_data['prev_ibs'] = merged_data['ibs'].shift(1)
    merged_data["prev_MFI_1d"] = merged_data["MFI_1d"].shift(1)
    merged_data['prev_lower_shadow'] = merged_data['lower_shadow'].shift(1)
    merged_data['prev_RSI20'] = merged_data['RSI20'].shift(1)
    # group data  
    merged_data['High_Volume_group'] = merged_data.apply(lambda r: get_high_volume_group(r) , axis=1)  
    merged_data['Low_Volume_group'] = merged_data.apply(lambda r: get_low_volume_group(r) , axis=1)  
    merged_data['Volume_group'] = merged_data.apply(lambda r: "Tang" if r["Volume"] > r["prev_Vol"] else "Giam", axis=1)
    merged_data["price_vs_body_group"] = merged_data.apply(lambda r: price_vs_body_group(r) , axis=1)
    merged_data['upper_wick_group'] = merged_data.apply(lambda r: "Tang" if r["upper_wick"] > r["prev_upper_wick"] else "Giam(or Bang)", axis=1)
    merged_data["ibs_vol_group"] = merged_data.apply(lambda r: get_ibs_vol_group(r) , axis=1)
    merged_data['Volume_avg_group'] = merged_data.apply(lambda r: "Tang" if r["avg20_Volume"] > r["prev_avg20_Volume"] else "Giam", axis=1)
    merged_data['High_and_RSI_group'] = merged_data.apply(lambda r: True if (r["High"] > r["prev_High"] and r["RSI20"] > r["prev_RSI20"]) else False, axis=1)
    merged_data['Close_price_group'] = merged_data.apply(lambda r: get_close_price_position(r), axis=1) 
    merged_data['Open_price_group'] = merged_data.apply(lambda r: get_open_price_position(r), axis=1)
    merged_data['lower_wick_group'] = merged_data.apply(
        lambda r: 1 if r["lower_shadow"] > r["prev_lower_shadow"] else -1, axis=1)
    # signals
    merged_data['couple_cs_1st_cond'] = merged_data.apply(get_couple_cs_1st_cond, axis=1)
    merged_data['couple_cs_2rd_cond'] = merged_data.apply(get_couple_cs_2rd_cond, axis=1)
    merged_data['couple_cs_signal'] = merged_data.apply(get_couple_candleticks_signal, axis=1)
    merged_data["ema20_250_cross_signal"] = merged_data.apply(get_ema20_250_cross_signal, axis=1)
    #
    return merged_data


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


def get_couple_cs_1st_cond(r):
    cond = ''
    if r['Open'] > r['Close'] >= r['Low'] + 0.1:
        # Do va co bong nen duoi
        cond = 'S'
    elif r['Open'] < r['Close'] <= r['High'] - 0.1:
        # Xanh va co bong nen tren
        cond = 'L'
    return cond


def get_couple_cs_2rd_cond(r):
    cond = ''
    if r['Open'] > r['Close'] == r['Low'] and r['Low'] < r['prev_Low']:
        # Do va khong co bong nen duoi
        cond = 'S'
    elif r['Open'] < r['Close'] == r['High'] and r['High'] > r['prev_High']:
        # Xanh va khong co bong nen tren
        cond = 'L'
    return cond
    

def get_couple_candleticks_signal(r):
    signal = ''
    if r['couple_cs_1st_cond'] == 'S' and r['couple_cs_2rd_cond'] == 'S':
        signal = 'short'
    elif r['couple_cs_1st_cond'] == 'L' and r['couple_cs_2rd_cond'] == 'L':
        signal = 'long'
    return signal


def get_ema20_250_cross_signal(r):
    signal = ''
    if r['ema20'] > r['ema250'] and r['prev_ema20'] <= r['prev_ema250']:
        signal = 'long'
    elif r['ema20'] < r['ema250'] and r['prev_ema20'] >= r['prev_ema250']:
        signal = 'short'
    return signal


def get_mfm(r):
    if r['High'] == r['Low']:
        return 0
    direction = 1 if r['Close'] > r['Open'] else (-1 if r['Close'] < r['Open'] else 0)
    MFM = ((r['Close'] - r['Low']) - (r['High'] - r['Close'])) / (r['High'] - r['Low'])
    MoneyFlow = MFM * r['Volume'] * direction
    return MoneyFlow