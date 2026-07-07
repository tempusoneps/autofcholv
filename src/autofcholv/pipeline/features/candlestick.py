import numpy as np
import pandas as pd
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
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
    epsilon = 1e-6

    df['body'] = df['Close'] - df['Open']
    df['height'] = df['High'] - df['Low']

    body_top = df[['Open', 'Close']].max(axis=1)
    body_bottom = df[['Open', 'Close']].min(axis=1)

    df['upwick'] = df['High'] - body_top
    df['lowwick'] = body_bottom - df['Low']

    height_safe = df['height'].replace(0, np.nan)

    # ratios
    df['body_ratio'] = (df['body'].abs() / (height_safe + epsilon)).fillna(0)
    df['wick_ratio'] = df['upwick'] / (df['upwick'] + df['lowwick'] + epsilon)

    # CLV
    df['clv'] = np.where(
        df['height'] == 0,
        0,
        ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (height_safe + epsilon)
    )

    # IBS
    df['ibs'] = ((df['Close'] - df['Low']) / (height_safe + epsilon)).fillna(0)

    # Candle strength
    df['candle_strength'] = df['body'] / (height_safe + epsilon)

    # Volume (safe)
    df['vbr'] = (df['Volume'] / (height_safe + epsilon)).clip(
        0, df['Volume'].quantile(0.99)
    )

    # Wick imbalance
    df['wick_imbalance'] = df['upwick'] - df['lowwick']

    # Numeric color
    df['color'] = np.where(df['body'] > 0, 1, np.where(df['body'] < 0, -1, 0))

    # --- Signal-support indicators ---
    # These columns are consumed by signal.py to derive Buy/Sell/None signals.

    fractal_high = np.where(
        (df["High"] > df["High"].shift(1))
        & (df["High"] > df["High"].shift(2))
        & (df["High"] > df["High"].shift(-1))
        & (df["High"] > df["High"].shift(-2)),
        df["High"],
        np.nan,
    )
    fractal_low = np.where(
        (df["Low"] < df["Low"].shift(1))
        & (df["Low"] < df["Low"].shift(2))
        & (df["Low"] < df["Low"].shift(-1))
        & (df["Low"] < df["Low"].shift(-2)),
        df["Low"],
        np.nan,
    )
    df["sig_fractal_high_ffill"] = pd.Series(fractal_high, index=df.index).ffill()
    df["sig_fractal_low_ffill"] = pd.Series(fractal_low, index=df.index).ffill()

    return df
