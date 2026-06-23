import os

import numpy as np
import pandas as pd


EPS = 1e-8


def _rolling_regression_last(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(x, values, 1)
    return slope * x[-1] + intercept


def _rolling_regression_slope(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    slope, _ = np.polyfit(x, values, 1)
    return slope


def _rolling_wma_last(values: np.ndarray) -> float:
    if np.isnan(values).all():
        return np.nan
    weights = np.arange(1, len(values) + 1, dtype=float)
    valid = ~np.isnan(values)
    return np.dot(values[valid], weights[valid]) / weights[valid].sum()


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trend-following features adapted from quant-ohlcv-feature.
    Feature definitions follow trend.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    trend_n = int(os.getenv("FAST_TREND_LOOKBACK", 24))

    ema_1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    ema_2 = ema_1.ewm(span=trend_n, adjust=False).mean()
    ema_3 = ema_2.ewm(span=trend_n, adjust=False).mean()


    hull_x = 2.0 * ema_1 - df["Close"].ewm(span=trend_n * 2, adjust=False).mean()
    hull_smooth = hull_x.ewm(span=max(1, int(np.sqrt(2 * trend_n))), adjust=False).mean()
    df["hullma_bias"] = hull_x / (hull_smooth + EPS) - 1.0

    ichimoku_n2 = 3 * trend_n
    ichimoku_n3 = 2 * ichimoku_n2
    tenkan = (
        df["High"].rolling(trend_n, min_periods=1).max()
        + df["Low"].rolling(trend_n, min_periods=1).min()
    ) / 2.0
    kijun = (
        df["High"].rolling(ichimoku_n2, min_periods=1).max()
        + df["Low"].rolling(ichimoku_n2, min_periods=1).min()
    ) / 2.0
    span_a = (tenkan + kijun) / 2.0
    span_b = (
        df["High"].rolling(ichimoku_n3, min_periods=1).max()
        + df["Low"].rolling(ichimoku_n3, min_periods=1).min()
    ) / 2.0
    df["ichimoku_cloud_ratio"] = span_a / (span_b + EPS)

    va = 0.5
    t3_ema = ema_1
    t3_ema2 = ema_2
    t1 = t3_ema * (1.0 + va) - t3_ema2 * va
    t1_ema = t1.ewm(span=trend_n, adjust=False).mean()
    t1_ema2 = t1_ema.ewm(span=trend_n, adjust=False).mean()
    t2 = t1_ema * (1.0 + va) - t1_ema2 * va
    t2_ema = t2.ewm(span=trend_n, adjust=False).mean()
    t2_ema2 = t2_ema.ewm(span=trend_n, adjust=False).mean()
    t3 = t2_ema * (1.0 + va) - t2_ema2 * va
    df["t3_bias"] = df["Close"] / (t3 + EPS) - 1.0

    dema = 2.0 * ema_1 - ema_2
    tema = 3.0 * ema_1 - 3.0 * ema_2 + ema_3
    df["dema_bias"] = dema / (ema_1 + EPS) - 1.0
    df["tema_bias"] = ema_1 / (tema + EPS) - 1.0
    df["trix"] = ema_3.pct_change()

    high_argmax = df["High"].rolling(trend_n, min_periods=1).apply(np.argmax, raw=True)
    low_argmin = df["Low"].rolling(trend_n, min_periods=1).apply(np.argmin, raw=True)
    window_count = df["High"].rolling(trend_n, min_periods=1).count()
    aroon_up = (high_argmax + 1.0) / window_count * 100.0
    aroon_down = (low_argmin + 1.0) / window_count * 100.0
    df["aroon_up"] = aroon_up
    df["aroon_down"] = aroon_down
    df["aroon_osc"] = aroon_up - aroon_down

    prev_close = df["Close"].shift(1)
    true_range = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    vm_plus = (df["High"] - df["Low"].shift(1)).abs()
    vm_minus = (df["Low"] - df["High"].shift(1)).abs()
    tr_sum = true_range.rolling(trend_n, min_periods=trend_n).sum()
    df["vortex_plus"] = vm_plus.rolling(trend_n, min_periods=trend_n).sum() / (tr_sum + EPS)
    df["vortex_minus"] = vm_minus.rolling(trend_n, min_periods=trend_n).sum() / (tr_sum + EPS)
    df["vortex_diff"] = df["vortex_plus"] - df["vortex_minus"]

    reg_line = df["Close"].rolling(trend_n, min_periods=trend_n).apply(
        _rolling_regression_last,
        raw=True,
    )
    reg_slope = df["Close"].rolling(trend_n, min_periods=trend_n).apply(
        _rolling_regression_slope,
        raw=True,
    )
    df["regression_bias"] = df["Close"] / (reg_line + EPS) - 1.0
    df["regression_slope"] = reg_slope / (df["Close"].rolling(trend_n, min_periods=trend_n).mean() + EPS)


    ma_signal_spread = df["Close"] - df["Close"].rolling(trend_n, min_periods=1).mean()
    df["ma_signal"] = (ma_signal_spread - ma_signal_spread.rolling(trend_n, min_periods=1).min()) / (
        ma_signal_spread.rolling(trend_n, min_periods=1).max()
        - ma_signal_spread.rolling(trend_n, min_periods=1).min()
        + EPS
    )


    bbi_ma1 = df["Close"].rolling(trend_n, min_periods=1).mean()
    bbi_ma2 = df["Close"].rolling(2 * trend_n, min_periods=1).mean()
    bbi_ma3 = df["Close"].rolling(4 * trend_n, min_periods=1).mean()
    bbi_ma4 = df["Close"].rolling(8 * trend_n, min_periods=1).mean()
    bbi = (bbi_ma1 + bbi_ma2 + bbi_ma3 + bbi_ma4) / 4.0
    df["bbi_ratio"] = bbi / (df["Close"] + EPS)
    df["bbi_bias"] = df["Close"] / (bbi + EPS) - 1.0

    up_move = df["High"].diff()
    down_move = -df["Low"].diff()
    pdm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    ndm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)
    adxr_tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - df["Close"].shift(1)).abs(),
            (df["Low"] - df["Close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    adxr_tr_sum = adxr_tr.rolling(trend_n, min_periods=1).sum()
    di_plus = pdm.rolling(trend_n, min_periods=1).sum() / (adxr_tr_sum + EPS)
    di_minus = ndm.rolling(trend_n, min_periods=1).sum() / (adxr_tr_sum + EPS)
    df["adxr_diff"] = 0.5 * (di_plus - di_minus) + 0.5 * (di_plus.shift(trend_n) - di_minus.shift(trend_n))

    wma = df["Close"].rolling(trend_n, min_periods=1).apply(_rolling_wma_last, raw=True)
    ma = df["Close"].rolling(trend_n, min_periods=1).mean()
    wma_gap = wma - ma
    df["wma_ma_gap"] = wma_gap / (wma_gap.abs().rolling(trend_n, min_periods=1).sum() + EPS)

    return df
