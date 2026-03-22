import numpy as np
import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate candlestick geometric features (vectorized).

    Features:
        body        : Close - Open (positive = green, negative = red)
        height      : High - Low
        upwick      : upper wick
        lowwick     : lower wick
        upwick_rate : upper wick / candle height % ratio
        lowwick_rate: lower wick / candle height % ratio
        ibs         : Internal Bar Strength
        color       : 'green' | 'red' | 'doji'
    """
    df['body']   = df['Close'] - df['Open']
    df['height'] = df['High'] - df['Low']

    body_top    = df[['Open', 'Close']].max(axis=1)
    body_bottom = df[['Open', 'Close']].min(axis=1)

    df['upwick']  = df['High'] - body_top
    df['lowwick'] = body_bottom - df['Low']

    height_safe = df['height'].replace(0, np.nan)
    df['upwick_rate']  = (df['upwick']  * 100 / height_safe).round(2).fillna(0)
    df['lowwick_rate'] = (df['lowwick'] * 100 / height_safe).round(2).fillna(0)
    df['body_rate']    = (df['body'].abs() * 100 / height_safe).round(2).fillna(0)
    
    clv = np.where(df['height'] == 0, 1, ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / height_safe)
    df['clv'] = pd.Series(clv).fillna(0)
    
    df['cbr'] = (df['body'].abs() / height_safe).fillna(0)
    df['vbr'] = (df['Volume'] / height_safe).fillna(0)
    
    df['ibs'] = ((df['Close'] - df['Low']) / height_safe).fillna(0)

    df['wick_imbalance'] = df['upwick'] - df['lowwick']
    epsilon = 1e-9
    df['upwick_ratio']   = df['upwick'] / (df['lowwick'] + epsilon)

    df['color'] = np.where(
        df['body'] == 0, 'doji',
        np.where(df['body'] > 0, 'green', 'red')
    )    

    return df