import numpy as np
import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán các features hình học của candlestick (vectorized).

    Features:
        cs_body        : Close - Open (dương = xanh, âm = đỏ)
        cs_height      : High - Low
        cs_upwick      : bóng trên
        cs_lowwick     : bóng dưới
        cs_upwick_rate : tỉ lệ % bóng trên / chiều cao nến
        cs_lowwick_rate: tỉ lệ % bóng dưới / chiều cao nến
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
    df['cs_upwick_rate']  = (df['cs_upwick']  * 100 / height_safe).round(3).fillna(1)
    df['cs_lowwick_rate'] = (df['cs_lowwick'] * 100 / height_safe).round(3).fillna(1)
    df['cs_ibs'] = ((df['Close'] - df['Low']) / height_safe).fillna(1)

    df['cs_color'] = np.where(
        df['cs_body'] == 0, 'doji',
        np.where(df['cs_body'] > 0, 'green', 'red')
    )

    return df