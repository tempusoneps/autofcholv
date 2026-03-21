import numpy as np
import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate candlestick geometric features (vectorized).

    Features:
        cs_body        : Close - Open (positive = green, negative = red)
        cs_height      : High - Low
        cs_upwick      : upper wick
        cs_lowwick     : lower wick
        cs_upwick_rate : upper wick / candle height % ratio
        cs_lowwick_rate: lower wick / candle height % ratio
        cs_ibs         : Internal Bar Strength
        cs_color       : 'green' | 'red' | 'doji'
    """
    df['cs_body']   = df['Close'] - df['Open']
    df['cs_height'] = df['High'] - df['Low']

    body_top    = df[['Open', 'Close']].max(axis=1)
    body_bottom = df[['Open', 'Close']].min(axis=1)

    df['cs_upwick']  = df['High'] - body_top
    df['cs_lowwick'] = body_bottom - df['Low']

    height_safe = df['cs_height'].replace(0, np.nan)
    df['cs_upwick_rate']  = (df['cs_upwick']  * 100 / height_safe).round(2).fillna(0)
    df['cs_lowwick_rate'] = (df['cs_lowwick'] * 100 / height_safe).round(2).fillna(0)
    df['cs_ibs'] = ((df['Close'] - df['Low']) / height_safe).fillna(0)

    df['cs_color'] = np.where(
        df['cs_body'] == 0, 'doji',
        np.where(df['cs_body'] > 0, 'green', 'red')
    )    

    return df