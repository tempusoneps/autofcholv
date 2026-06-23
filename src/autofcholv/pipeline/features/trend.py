import os

import numpy as np
import pandas as pd


EPS = 1e-8


def _rolling_regression_last(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, intercept = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
    return slope * x[-1] + intercept


def _rolling_regression_slope(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, _ = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
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


    max_high = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    max_low = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    xpdm = np.where(max_high > max_low, df["High"] - df["High"].shift(1), 0.0)
    xndm = np.where(max_low > max_high, df["Low"].shift(1) - df["Low"], 0.0)
    tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - df["Close"]).abs(),
            (df["Low"] - df["Close"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    pdm = pd.Series(xpdm, index=df.index).rolling(trend_n, min_periods=1).sum()
    ndm = pd.Series(xndm, index=df.index).rolling(trend_n, min_periods=1).sum()
    tr_sum = tr.rolling(trend_n, min_periods=1).sum()
    di_plus = pdm / (tr_sum + EPS)
    di_minus = ndm / (tr_sum + EPS)
    df["adx_strength"] = (pdm + ndm) / (tr_sum + EPS)
    df["adx_di_plus"] = di_plus
    df["adx_di_minus"] = di_minus

    vi_pos = pd.Series(np.abs(df["High"] - df["Low"].shift(1)), index=df.index).rolling(trend_n, min_periods=1).sum()
    vi_neg = pd.Series(np.abs(df["Low"] - df["High"].shift(1)), index=df.index).rolling(trend_n, min_periods=1).sum()
    vi_tr = pd.Series(
        pd.concat(
            [
                (df["High"] - df["Low"]).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
                (df["High"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1),
        index=df.index,
    ).rolling(trend_n, min_periods=1).sum()
    df["vi_plus"] = vi_pos / (vi_tr + EPS)
    df["vi_minus"] = vi_neg / (vi_tr + EPS)

    turtle_high = df[["Open", "Close"]].max(axis=1).rolling(trend_n, min_periods=1).max().shift(1)
    turtle_low = df[["Open", "Close"]].min(axis=1).rolling(trend_n, min_periods=1).min().shift(1)
    turtle_width = turtle_high - turtle_low
    turtle_distance = pd.Series(np.where(df["Close"] > turtle_high, df["Close"] - turtle_high, 0.0), index=df.index)
    turtle_distance = turtle_distance.where(df["Close"] >= turtle_low, df["Close"] - turtle_low)
    df["turtle_breakout"] = turtle_distance / (turtle_width + EPS)
    df["turtle_distance"] = turtle_distance


    ma_base = df["Close"].rolling(trend_n, min_periods=1).mean()
    ma_double = ma_base.rolling(trend_n, min_periods=1).mean()
    df["ma_ratio"] = ma_base / (df["Close"] + EPS)
    df["dema_bias2"] = (2.0 * ma_base - ma_double) / (ma_base + EPS) - 1.0
    df["tema_bias2"] = (3.0 * ma_base - 3.0 * ma_double + ma_double.rolling(trend_n, min_periods=1).mean()) / (ma_base + EPS) - 1.0

    hma_base = df["High"].rolling(trend_n, min_periods=1).mean()
    df["hma_ratio"] = (df["High"] - hma_base) / (hma_base + EPS)

    close_diff = df["Close"].diff()
    up = close_diff.clip(lower=0.0)
    dn = (-close_diff).clip(lower=0.0)
    vidya_er = close_diff.abs().rolling(trend_n, min_periods=1).sum()
    vidya_vi = (df["Close"] - df["Close"].shift(trend_n)).abs() / (vidya_er + EPS)
    vidya = vidya_vi * df["Close"] + (1.0 - vidya_vi) * df["Close"].shift(1)
    df["vidya_bias"] = vidya / (ma_base + EPS) - 1.0

    tma = df["Close"].rolling(trend_n, min_periods=1).mean().rolling(trend_n, min_periods=1).mean()
    df["tma_bias2"] = df["Close"] / (tma + EPS) - 1.0

    price4 = (df["High"] + df["Low"] + df["Open"] + df["Close"]) / 4.0
    price4_ma = price4.rolling(trend_n, min_periods=1).mean()
    df["vma_ratio"] = price4 / (price4_ma + EPS) - 1.0
    df["lma_ratio"] = df["Low"] / (df["Low"].rolling(trend_n, min_periods=1).mean() + EPS) - 1.0
    df["mm_ratio"] = ma_base / (df["Close"].rolling(5 * trend_n, min_periods=1).mean() + EPS) - 1.0



    reg_slope_angle = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_slope, raw=True)
    df["reg_angle"] = np.degrees(np.arctan(reg_slope_angle))

    expma_1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    expma_2 = df["Close"].ewm(span=4 * trend_n, adjust=False).mean()
    df["expma_ratio"] = expma_1 / (expma_2 + EPS) - 1.0

    diff_ema_short = df["Close"].ewm(span=trend_n, adjust=False).mean()
    diff_ema_long = df["Close"].ewm(span=3 * trend_n, adjust=False).mean()
    diff_ema = diff_ema_short - diff_ema_long
    df["diff_ema_ratio"] = diff_ema / (diff_ema.ewm(span=trend_n, adjust=False).mean() + EPS) - 1.0

    ema = df["Close"].ewm(span=trend_n, adjust=False).mean()
    reg_ema = ema.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["regema_bias"] = df["Close"] / (reg_ema + EPS) - 1.0

    tema_1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    tema_2 = tema_1.ewm(span=trend_n, adjust=False).mean()
    tema_3 = tema_2.ewm(span=trend_n, adjust=False).mean()
    tema = 3.0 * tema_1 - 3.0 * tema_2 + tema_3
    reg_tema = tema.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["regtema_bias"] = tema / (reg_tema + EPS) - 1.0

    tr_trix = df["Close"].ewm(span=trend_n, adjust=False).mean()
    df["trtrix"] = tr_trix.pct_change()



    trv_base = df["Close"].rolling(trend_n, min_periods=1).mean()
    trv = 100.0 * (trv_base - trv_base.shift(trend_n)) / (trv_base.shift(trend_n) + EPS)
    df["trv"] = trv.rolling(trend_n, min_periods=1).mean()

    mac_price_4 = (df["High"].rolling(trend_n, min_periods=1).max() + df["Low"].rolling(trend_n, min_periods=1).min() + df["Open"]) / 3.0
    mac_short_4 = mac_price_4.rolling(trend_n, min_periods=1).mean()
    mac_long_4 = mac_price_4.rolling(2 * trend_n, min_periods=1).mean()
    df["mac_v4"] = (10.0 * (mac_short_4 - mac_long_4)).rolling(trend_n, min_periods=1).apply(_rolling_regression_last, raw=True)

    mac_price_5 = (df["High"].rolling(trend_n, min_periods=1).max() + df["Low"].rolling(trend_n, min_periods=1).min() + df["Close"]) / 3.0
    mac_short_5 = mac_price_5.rolling(trend_n, min_periods=1).mean()
    mac_long_5 = mac_price_5.rolling(2 * trend_n, min_periods=1).mean()
    df["mac_v5"] = (10.0 * (mac_short_5 - mac_long_5)).rolling(trend_n, min_periods=1).mean()



    adx = df["High"].copy()
    up_move = df["High"].diff()
    down_move = -df["Low"].diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)
    tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - df["Close"].shift(1)).abs(),
            (df["Low"] - df["Close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    tr_sum = tr.rolling(trend_n, min_periods=1).sum()
    plus_di = plus_dm.rolling(trend_n, min_periods=1).sum() / (tr_sum + EPS)
    minus_di = minus_dm.rolling(trend_n, min_periods=1).sum() / (tr_sum + EPS)
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di + EPS)
    adx = dx.rolling(trend_n, min_periods=1).mean()
    acs_base = adx / (df["Close"] + EPS)
    df["acs"] = acs_base.rolling(trend_n, min_periods=1).std(ddof=0)

    df["mak"] = (df["Close"].rolling(trend_n, min_periods=1).mean() / (
        df["Close"].rolling(trend_n, min_periods=1).mean().shift(1) + EPS
    ) - 1.0) * 1000.0

    df["sgcz"] = (df["Close"] - df["High"].rolling(trend_n, min_periods=1).mean()) / (
        df["High"].rolling(trend_n, min_periods=1).mean() + EPS
    )



    wma = df["Close"].rolling(trend_n, min_periods=1).apply(_rolling_wma_last, raw=True)
    ma = df["Close"].rolling(trend_n, min_periods=1).mean()
    gap = wma - ma
    df["gap_ratio"] = gap / (gap.abs().rolling(trend_n, min_periods=1).sum() + EPS)

    angle_slope = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_slope, raw=True)
    df["angle_reg"] = np.degrees(np.arctan(angle_slope))



    cse_roll = df["Close"].rolling(trend_n, min_periods=1)
    cse_std = (df["Close"] - cse_roll.min()) / (cse_roll.max() - cse_roll.min() + EPS)
    df["cse"] = cse_std.ewm(span=max(1, trend_n - 1), adjust=False).mean()

    ma = df["Close"].rolling(2 * trend_n, min_periods=1).mean()
    df["madis_placed"] = df["Close"] / (ma.shift(trend_n) + EPS) - 1.0

    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    norm_qv = (df["Close"] * df["Volume"]) / ((df["Close"] * df["Volume"]).rolling(trend_n, min_periods=1).mean() + EPS)
    reg_price = tp.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    trrq_base = pd.Series(reg_price, index=df.index).pct_change(trend_n) / (norm_qv + EPS)
    df["trrq"] = trrq_base.rolling(trend_n, min_periods=1).sum()



    reg_close = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["mreg"] = (df["Close"] / (reg_close + EPS) - 1.0).rolling(trend_n, min_periods=1).mean()

    up_move = df["High"].diff()
    down_move = -df["Low"].diff()
    max_high = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    max_low = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    xpdm = np.where(max_high > max_low, df["High"] - df["High"].shift(1), 0.0)
    xndm = np.where(max_low > max_high, df["Low"].shift(1) - df["Low"], 0.0)
    tr = pd.concat([
        (df["High"] - df["Low"]).abs(),
        (df["High"] - df["Close"]).abs(),
        (df["Low"] - df["Close"]).abs(),
    ], axis=1).max(axis=1)
    pdm = pd.Series(xpdm, index=df.index).rolling(trend_n, min_periods=1).sum()
    ndm = pd.Series(xndm, index=df.index).rolling(trend_n, min_periods=1).sum()
    tr_sum = tr.rolling(trend_n, min_periods=1).sum()
    di_pos = pdm / (tr_sum + EPS)
    di_neg = ndm / (tr_sum + EPS)
    adxr_pos = 0.5 * di_pos + 0.5 * di_pos.shift(trend_n)
    adxr_neg = 0.5 * di_neg + 0.5 * di_neg.shift(trend_n)
    df["adxr_pos"] = adxr_pos
    df["adxr_neg"] = adxr_neg


    return df
