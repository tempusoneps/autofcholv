import numpy as np
import pandas as pd
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate candlestick geometric features (vectorized).
    """
    epsilon = 1e-6

    df['body'] = df['Close'] - df['Open']
    df['height'] = df['High'] - df['Low']
    df["body_abs"] = df["body"].abs()
    df["body_abs_sma_medium"] = df["body_abs"].rolling(config.medium_lookback).mean()
    df["range_sma_medium"] = df["height"].rolling(config.medium_lookback).mean()

    body_top = df[['Open', 'Close']].max(axis=1)
    body_bottom = df[['Open', 'Close']].min(axis=1)

    df['upwick'] = df['High'] - body_top
    df['lowwick'] = body_bottom - df['Low']

    height_safe = df['height'].replace(0, np.nan)

    # ratios
    df['upwick_rate'] = (df['upwick'] / (height_safe + epsilon)).fillna(0)
    df['lowwick_rate'] = (df['lowwick'] / (height_safe + epsilon)).fillna(0)
    df['body_rate'] = (df['body'].abs() / (height_safe + epsilon)).fillna(0)
    df["candle_range_ratio"] = df["body_abs"] / height_safe
    df['wick_ratio'] = df['upwick'] / (df['upwick'] + df['lowwick'] + epsilon)
    df['upwick_ratio'] = df['upwick'] / (df['lowwick'] + epsilon)

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
        0, df['Volume'].rolling(window=99, min_periods=1).quantile(0.99)
    )

    # Wick imbalance
    df['wick_imbalance'] = df['upwick'] - df['lowwick']

    # Numeric color
    df['color'] = np.where(df['body'] > 0, 1, np.where(df['body'] < 0, -1, 0))

    df["heikin_ashi_close"] = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4.0
    df["heikin_ashi_open"] = (df["Open"].shift(1) + df["Close"].shift(1)) / 2.0
    df["heikin_ashi_bull"] = df["heikin_ashi_close"] > df["heikin_ashi_open"]
    df["bullish_high_break_candle"] = (
        (df["Open"] < df["Close"])
        & (df["Close"] <= df["High"] - 0.1)
        & (df["High"] > df["High"].shift(1))
    )
    df["bearish_low_break_candle"] = (
        (df["Open"] > df["Close"])
        & (df["Close"] >= df["Low"] + 0.1)
        & (df["Low"] < df["Low"].shift(1))
    )

    return df
