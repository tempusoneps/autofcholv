import os

import numpy as np
import pandas as pd


EPS = 1e-8


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate liquidity and price-volume composite features adapted from quant-ohlcv-feature.
    Feature definitions follow liquidity.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    n = int(os.getenv("VOLUME_LOOKBACK", os.getenv("MOMENTUM_LOOKBACK", 24)))

    quote_volume_proxy = df["Close"] * df["Volume"]
    quote_volume_ema = quote_volume_proxy.ewm(span=n, adjust=False).mean()
    volume_ema = df["Volume"].ewm(span=n, adjust=False).mean()
    avg_holding_cost = quote_volume_ema / (volume_ema + EPS)
    df["market_placement"] = df["Close"] / (avg_holding_cost + EPS) - 1.0

    path_first = (df["High"] - df["Open"]) + (df["High"] - df["Low"]) + (df["Close"] - df["Low"])
    path_second = (df["Open"] - df["Low"]) + (df["High"] - df["Low"]) + (df["High"] - df["Close"])
    path_min = pd.concat([path_first, path_second], axis=1).min(axis=1)
    candle_range = df["High"] - df["Low"]
    path_min = np.where(path_min == 0.0, candle_range, path_min)
    path_min = pd.Series(path_min, index=df.index) + (df["Open"] - df["Close"].shift(1)).abs()
    path_shortest = path_min / (df["Close"] + EPS)
    liquidity_path = np.where(path_shortest == 0.0, np.nan, quote_volume_proxy / path_shortest)
    df["path_liquidity"] = pd.Series(liquidity_path, index=df.index).rolling(n, min_periods=1).sum()

    log_high = np.log(df["High"] + EPS)
    log_low = np.log(df["Low"] + EPS)
    log_close = np.log(df["Close"] + EPS)
    df["spread_proxy"] = (log_high - log_low).rolling(n, min_periods=2).mean()
    df["spread_volatility_ratio"] = df["spread_proxy"] / (
        log_close.diff().rolling(n, min_periods=2).std(ddof=0).abs() + EPS
    )

    close_shift = df["Close"].shift(n)
    volume_shift = df["Volume"].shift(n)
    close_ratio = ((df["Close"] - close_shift.rolling(n, min_periods=1).mean()) / (close_shift + EPS)).abs()
    volume_ratio = (df["Volume"] - volume_shift.rolling(n, min_periods=1).mean()) / (volume_shift + EPS)
    raw_resistance = close_ratio / (volume_ratio.abs() + EPS)
    df["price_volume_resistance"] = np.where(volume_ratio < 0, -raw_resistance, raw_resistance) / n

    coppock = 100.0 * (
        df["Close"].pct_change(n) + df["Close"].pct_change(2 * n)
    )
    coppock_mean = coppock.rolling(n, min_periods=1).mean()
    prev_close = df["Close"].shift(1)
    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    normalized_atr = true_range.rolling(n, min_periods=1).mean() / (
        df["Close"].rolling(n, min_periods=1).mean() + EPS
    )
    volume_pressure = df["Volume"] / (df["Volume"].rolling(n, min_periods=1).mean() + EPS)
    df["coppock_atr_volume"] = coppock_mean * normalized_atr * volume_pressure

    return df
