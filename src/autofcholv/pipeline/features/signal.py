import pandas as pd
import numpy as np


BUY_SIGNAL = "Buy"
SELL_SIGNAL = "Sell"
NONE_SIGNAL = "None"


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['open_lag1', 'close_lag1', 'high_lag1', 'low_lag1', 'ema_slow_lag1', 'ema_fast_lag1', "macd", "macd_signal", "macd_hist", "long_trend", "rsi", "ub", "lb", "upwick", "lowwick", "body"]
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    df = add_couple_cs_signal(df)
    df = add_ema_cross_signal(df)
    df = add_macd_signal(df)
    df = add_min_max_10_signal(df)
    df = add_bb_rejection_signal(df)
    
    return df

def add_couple_cs_signal(df: pd.DataFrame) -> pd.DataFrame:
    # Vectorized Couple Candlesticks Signal
    cond1_S = (df['open_lag1'] > df['close_lag1']) & (df['close_lag1'] >= df['low_lag1'] + 0.1) # Cay nen truoc phai do va co bong nen duoi
    cond2_S = (df['Open'] > df['Close']) & (df['Close'] == df['Low']) & (df['Low'] < df['low_lag1']) # Do va khong co bong nen duoi
    #
    cond1_L = (df['open_lag1'] < df['close_lag1']) & (df['close_lag1'] <= df['high_lag1'] - 0.1) # Cay nen truoc phai xanh va co bong nen tren
    cond2_L = (df['Open'] < df['Close']) & (df['Close'] == df['High']) & (df['High'] > df['high_lag1']) # Xanh va khong co bong nen tren
    
    is_bearish = cond1_S & cond2_S
    is_bullish = cond1_L & cond2_L
    
    df['couple_cs_signal'] = np.where(is_bullish, 'Buy', np.where(is_bearish, 'Sell', 'None'))
    return df

def add_ema_cross_signal(df: pd.DataFrame) -> pd.DataFrame:
    # Vectorized EMA Cross Signal
    ema_bullish = (df['ema_fast'] > df['ema_slow']) & (df['ema_fast_lag1'] <= df['ema_slow_lag1'])
    ema_bearish = (df['ema_fast'] < df['ema_slow']) & (df['ema_fast_lag1'] >= df['ema_slow_lag1'])
    
    df['ema_cross_signal'] = np.where(ema_bullish, BUY_SIGNAL, np.where(ema_bearish, SELL_SIGNAL, NONE_SIGNAL))
    return df

def add_min_max_10_signal(df: pd.DataFrame) -> pd.DataFrame:
    is_min_10 = df['Close'] == df['Close'].rolling(window=10).min()
    is_max_10 = df['Close'] == df['Close'].rolling(window=10).max()
    rsi_oversold = df['rsi'] < 30
    rsi_overbought = df['rsi'] > 70

    buy_signal = is_min_10 & rsi_oversold
    sell_signal = is_max_10 & rsi_overbought

    df['min_max_10_signal'] = np.where(buy_signal, BUY_SIGNAL, np.where(sell_signal, SELL_SIGNAL, NONE_SIGNAL))
    return df

def add_macd_signal(df: pd.DataFrame) -> pd.DataFrame:
    is_max_macd_hist = df['macd_hist'] == df['macd_hist'].rolling(10).max()
    after_max_MACDh = is_max_macd_hist.shift(1)
    after_positive_MACDh_series = df['macd_hist'].rolling(5).sum() > 0
    is_min_MACDh = df['macd_hist'] == df['macd_hist'].rolling(10).min()
    after_negative_MACDh_series = df['macd_hist'].rolling(5).sum() < 0
    after_min_MACDh = is_min_MACDh.shift(1)

    buy_signal = (df['open_lag1'] >= df['close_lag1']) & (df['macd_hist'] < 0) & (after_min_MACDh) & (after_negative_MACDh_series) & (df["Close"] > df["open_lag1"]) & (df["Close"] - df["low_lag1"] < 5)
    sell_signal = (df['open_lag1'] <= df['close_lag1']) & (df['macd_hist'] > 0) & (after_max_MACDh) & (after_positive_MACDh_series) & (df["Close"] < df["open_lag1"]) & (df["high_lag1"] - df["Close"] < 5)
    df['macd_signal'] = np.where(buy_signal, BUY_SIGNAL, np.where(sell_signal, SELL_SIGNAL, NONE_SIGNAL))
    return df
    
def add_bb_rejection_signal(df: pd.DataFrame) -> pd.DataFrame:
    buy_cond = (
        (df['Low'] < df['lb']) & 
        (df['Close'] > df['lb']) & 
        (df['rsi'] < 35) & 
        (df['lowwick'] > df['body'].abs()) & 
        (df['long_trend'] == 'StrongUp')
    )
    
    sell_cond = (
        (df['High'] > df['ub']) & 
        (df['Close'] < df['ub']) & 
        (df['rsi'] > 65) & 
        (df['upwick'] > df['body'].abs()) & 
        (df['long_trend'] == 'StrongDown')
    )
    
    df['bb_rejection_signal'] = np.where(buy_cond, BUY_SIGNAL, np.where(sell_cond, SELL_SIGNAL, NONE_SIGNAL))
    return df