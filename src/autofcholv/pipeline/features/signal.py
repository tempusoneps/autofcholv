import pandas as pd
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['high_lag1', 'low_lag1', 'ema_slow_lag1', 'ema_fast_lag1']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # Vectorized Couple Candlesticks Signal
    cond1_S = (df['Open'] > df['Close']) & (df['Close'] >= df['Low'] + 0.1)
    cond1_L = (df['Open'] < df['Close']) & (df['Close'] <= df['High'] - 0.1)
    
    cond2_S = (df['Open'] > df['Close']) & (df['Close'] == df['Low']) & (df['Low'] < df['low_lag1'])
    cond2_L = (df['Open'] < df['Close']) & (df['Close'] == df['High']) & (df['High'] > df['high_lag1'])
    
    is_bearish = cond1_S & cond2_S
    is_bullish = cond1_L & cond2_L
    
    df['couple_cs_signal'] = np.where(is_bullish, 'Bullish', np.where(is_bearish, 'Bearish', 'None'))

    # Vectorized EMA Cross Signal
    ema_bullish = (df['ema_fast'] > df['ema_slow']) & (df['ema_fast_lag1'] <= df['ema_slow_lag1'])
    ema_bearish = (df['ema_fast'] < df['ema_slow']) & (df['ema_fast_lag1'] >= df['ema_slow_lag1'])
    
    df['ema_cross_signal'] = np.where(ema_bullish, 'Bullish', np.where(ema_bearish, 'Bearish', 'None'))
    
    return df