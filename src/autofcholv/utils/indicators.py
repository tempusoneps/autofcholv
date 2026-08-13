import numpy as np
import pandas as pd

EPS = 1e-8


def get_true_range(df: pd.DataFrame) -> pd.Series:
    """Calculate and cache True Range."""
    if "_temp_tr" in df.columns:
        return df["_temp_tr"]
    
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["_temp_tr"] = tr
    return tr


def get_atr(df: pd.DataFrame, window: int) -> pd.Series:
    """Calculate and cache ATR for specific window n."""
    col_name = f"_temp_atr_{window}"
    if col_name in df.columns:
        return df[col_name]
    
    tr = get_true_range(df)
    atr = tr.rolling(window, min_periods=1).mean()
    df[col_name] = atr
    return atr


def get_sma_close(df: pd.DataFrame, window: int) -> pd.Series:
    """Calculate and cache SMA of Close for specific window n."""
    col_name = f"_temp_sma_close_{window}"
    if col_name in df.columns:
        return df[col_name]
    
    sma = df["Close"].rolling(window, min_periods=1).mean()
    df[col_name] = sma
    return sma


def get_std_close(df: pd.DataFrame, window: int, ddof: int = 0) -> pd.Series:
    """Calculate and cache Rolling Std of Close for specific window n and ddof."""
    col_name = f"_temp_std_close_{window}_d{ddof}"
    if col_name in df.columns:
        return df[col_name]
    
    std = df["Close"].rolling(window, min_periods=max(1, min(2, window))).std(ddof=ddof).fillna(0.0)
    df[col_name] = std
    return std


def get_rolling_vwap(df: pd.DataFrame, window: int) -> pd.Series:
    """Calculate and cache Rolling VWAP for specific window n."""
    col_name = f"_temp_vwap_{window}"
    if col_name in df.columns:
        return df[col_name]
    
    quote_vol = df["Close"] * df["Volume"]
    rolling_quote = quote_vol.rolling(window, min_periods=1).sum()
    rolling_vol = df["Volume"].rolling(window, min_periods=1).sum()
    vwap = rolling_quote / (rolling_vol + EPS)
    df[col_name] = vwap
    return vwap
