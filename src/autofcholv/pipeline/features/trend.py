import numpy as np
import pandas as pd
import pandas_ta as ta
from autofcholv.config.config import Config


EPS = 1e-8


def _rolling_regression_last(values: np.ndarray) -> float:
    if len(values) < 2 or not np.isfinite(values).all():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, intercept = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
    return slope * x[-1] + intercept


def _rolling_regression_slope(values: np.ndarray) -> float:
    if len(values) < 2 or not np.isfinite(values).all():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, _ = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
    return slope


def _linear_regression_slope(series: pd.Series, window: int) -> pd.Series:
    x = np.arange(window, dtype=float)

    def slope(values: np.ndarray) -> float:
        if len(values) < 2 or not np.isfinite(values).all():
            return np.nan
        try:
            coeffs = np.polyfit(x, values, 1)
        except Exception:
            return np.nan
        return coeffs[0]

    return series.rolling(window).apply(slope, raw=True)


def _linear_regression_midline(series: pd.Series, window: int) -> pd.Series:
    x = np.arange(window, dtype=float)

    def endpoint(values: np.ndarray) -> float:
        if len(values) < 2 or not np.isfinite(values).all():
            return np.nan
        try:
            slope, intercept = np.polyfit(x, values, 1)
        except Exception:
            return np.nan
        return intercept + slope * x[-1]

    return series.rolling(window).apply(endpoint, raw=True)


def _rolling_wma_last(values: np.ndarray) -> float:
    if np.isnan(values).all():
        return np.nan
    weights = np.arange(1, len(values) + 1, dtype=float)
    valid = ~np.isnan(values)
    return np.dot(values[valid], weights[valid]) / weights[valid].sum()


def _scale_01(values, window: int) -> pd.Series:
    values = pd.Series(values)
    low = values.rolling(window, min_periods=1).min()
    high = values.rolling(window, min_periods=1).max()
    return (values - low) / (high - low + EPS)


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate trend-following features adapted from quant-ohlcv-feature.
    Feature definitions follow trend.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    trend_n = config.fast_trend_lookback

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

    reg_line = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["reg"] = df["Close"] / (reg_line + EPS) - 1.0

    reg_v2_line = df["Close"].rolling(2 * trend_n, min_periods=2 * trend_n).apply(_rolling_regression_last, raw=True)
    df["reg_v2"] = 100.0 * (df["Close"] - reg_v2_line) / (reg_v2_line + EPS)

    reg_v3_line = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["reg_v3"] = df["Close"] / (reg_v3_line + EPS) - 1.0

    df["diff_ema"] = diff_ema
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

    hma_signal_base = df["High"] - df["High"].rolling(trend_n, min_periods=1).mean()
    df["hma_signal"] = _scale_01(hma_signal_base, trend_n)

    hull_fast = df["Close"].ewm(span=max(1, trend_n // 2), adjust=False, min_periods=1).mean()
    hull_slow = df["Close"].ewm(span=trend_n, adjust=False, min_periods=1).mean()
    hull_x = 2.0 * hull_fast - hull_slow
    hullma_signal = hull_x.ewm(span=max(1, int(np.sqrt(trend_n))), adjust=False, min_periods=1).mean()
    df["hullma_signal"] = _scale_01(hull_x - hullma_signal, trend_n)

    mac_price_2 = (df["High"] + df["Low"]) / 2.0
    mac_short_2 = mac_price_2.rolling(trend_n, min_periods=1).mean()
    mac_long_2 = mac_price_2.rolling(2 * trend_n, min_periods=1).mean()
    df["mac_v2"] = _scale_01(10.0 * (mac_short_2 - mac_long_2), trend_n)

    mac_price_3 = (df["High"].rolling(trend_n, min_periods=1).max() + df["Low"].rolling(trend_n, min_periods=1).min()) / 2.0
    mac_short_3 = mac_price_3.rolling(trend_n, min_periods=1).mean()
    mac_long_3 = mac_price_3.rolling(2 * trend_n, min_periods=1).mean()
    df["mac_v3"] = _scale_01(10.0 * (mac_short_3 - mac_long_3), trend_n)

    hullma_ema1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    hullma_ema2 = df["Close"].ewm(span=2 * trend_n, adjust=False).mean()
    hullma_x = 2.0 * hullma_ema1 - hullma_ema2
    hullma = hullma_x.ewm(span=max(1, int(np.sqrt(2 * trend_n))), adjust=False).mean()
    df["hullma_ratio"] = hullma_x / (hullma + EPS)

    vidya_base_v2 = (df["Open"] + df["Close"]) / 2.0
    vidya_v2_vi = (vidya_base_v2 - vidya_base_v2.shift(trend_n)).abs() / (
        vidya_base_v2 - vidya_base_v2.shift(1)
    ).abs().rolling(trend_n, min_periods=1).sum()
    vidya_v2 = vidya_v2_vi * vidya_base_v2 + (1.0 - vidya_v2_vi) * vidya_base_v2.shift(1)
    df["vidya_v2"] = vidya_v2 / (df["Close"] + EPS)

    vidya_base_v5 = (df["High"] + df["Low"] + df["Close"]) / 3.0
    vidya_v5_vi = (vidya_base_v5 - vidya_base_v5.shift(trend_n)).abs() / (
        vidya_base_v5 - vidya_base_v5.shift(1)
    ).abs().rolling(trend_n, min_periods=1).sum()
    vidya_v5 = vidya_v5_vi * vidya_base_v5 + (1.0 - vidya_v5_vi) * vidya_base_v5.shift(1)
    df["vidya_v5"] = vidya_v5 / (df["Close"] + EPS)

    mac_short = df["Close"].rolling(trend_n, min_periods=1).mean()
    mac_long = df["Close"].rolling(2 * trend_n, min_periods=1).mean()
    df["mac"] = _scale_01(10.0 * (mac_short - mac_long), trend_n)

    median = df["Close"].rolling(trend_n, min_periods=1).mean()
    cha = (df["Close"] - median).abs()
    ping_jun_cha = cha.rolling(trend_n, min_periods=1).mean()
    distance = pd.Series(np.where(df["Close"] > ping_jun_cha, df["Close"] - ping_jun_cha, 0.0), index=df.index)
    df["pjc_distance"] = distance / (ping_jun_cha + EPS) - 1.0

    hma = df["High"].rolling(trend_n, min_periods=1).mean()
    df["hma"] = (df["High"] - hma) / (hma + EPS)

    tma2_source = (df["High"] + df["Low"]) / 2.0
    tma2_close_ma = tma2_source.rolling(trend_n, min_periods=1).mean()
    tma2 = tma2_close_ma.rolling(trend_n, min_periods=1).mean()
    df["tma_v2"] = df["Close"] / (tma2 + EPS) - 1.0

    tma3_source = (df["High"].rolling(trend_n, min_periods=1).max() + df["Low"].rolling(trend_n, min_periods=1).min()) / 2.0
    tma3_close_ma = tma3_source.rolling(trend_n, min_periods=1).mean()
    tma3 = tma3_close_ma.rolling(trend_n, min_periods=1).mean()
    df["tma_v3"] = df["Close"] / (tma3 + EPS) - 1.0

    vidya_v3_base = (df["High"] + df["Low"]) / 2.0
    vidya_v3_vi = (vidya_v3_base - vidya_v3_base.shift(trend_n)).abs() / (
        vidya_v3_base - vidya_v3_base.shift(1)
    ).abs().rolling(trend_n, min_periods=1).sum()
    vidya_v3 = vidya_v3_vi * vidya_v3_base + (1.0 - vidya_v3_vi) * vidya_v3_base.shift(1)
    df["vidya_v3"] = vidya_v3 / (df["Close"] + EPS)

    vidya_v4_base = df[["Open", "Close"]].sum(axis=1) / 2.0
    vidya_v4_vi = (vidya_v4_base - vidya_v4_base.shift(trend_n)).abs() / (
        vidya_v4_base - vidya_v4_base.shift(1)
    ).abs().rolling(trend_n, min_periods=1).sum()
    vidya_v4 = vidya_v4_vi * vidya_v4_base + (1.0 - vidya_v4_vi) * vidya_v4_base.shift(1)
    df["vidya_v4"] = vidya_v4 / (df["Close"] + EPS)

    gap_wma = df["Close"].rolling(trend_n, min_periods=1).apply(_rolling_wma_last, raw=True)
    gap_ma = df["Close"].rolling(trend_n, min_periods=1).mean()
    gap = gap_wma - gap_ma
    df["gap"] = gap / (gap.abs().rolling(trend_n, min_periods=1).sum() + EPS)

    low_len = df["Low"].rolling(trend_n, min_periods=1).apply(np.argmin, raw=True)
    high_len = df["High"].rolling(trend_n, min_periods=1).apply(np.argmax, raw=True)
    arron_raw = (high_len - low_len) * 100.0 / trend_n
    df["arron"] = _scale_01(pd.Series(arron_raw, index=df.index), trend_n)

    ma = df["Close"].rolling(trend_n, min_periods=1).mean()
    df["ma"] = _scale_01(ma, trend_n)

    vma_price = (df["High"] + df["Low"] + df["Open"] + df["Close"]) / 4.0
    vma = vma_price.rolling(trend_n, min_periods=1).mean()
    df["vma"] = vma_price / (vma + EPS) - 1.0

    mm_fast = df["Close"].rolling(trend_n, min_periods=1).mean()
    mm_slow = df["Close"].rolling(5 * trend_n, min_periods=1).mean()
    df["mm"] = mm_fast / (mm_slow + EPS) - 1.0

    expma_1 = df["Close"].ewm(span=trend_n, min_periods=1).mean()
    expma_2 = df["Close"].ewm(span=4 * trend_n, min_periods=1).mean()
    df["expma"] = _scale_01(expma_1 - expma_2, trend_n)

    lma = df["Low"].rolling(trend_n, min_periods=1).mean()
    df["lma"] = df["Low"] / (lma + EPS) - 1.0

    dema_ema = df["Close"].ewm(span=trend_n, adjust=False).mean()
    dema_ema_ema = dema_ema.ewm(span=trend_n, adjust=False).mean()
    dema = 2.0 * dema_ema - dema_ema_ema
    df["dema"] = dema / (dema_ema + EPS) - 1.0

    tema_ema1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    tema_ema2 = tema_ema1.ewm(span=trend_n, adjust=False).mean()
    tema_ema3 = tema_ema2.ewm(span=trend_n, adjust=False).mean()
    tema = 3.0 * tema_ema1 - 3.0 * tema_ema2 + tema_ema3
    df["tema"] = tema_ema1 / (tema + EPS) - 1.0

    hlma_high = df["High"].rolling(trend_n, min_periods=1).mean()
    hlma_low = df["Low"].rolling(trend_n, min_periods=1).mean()
    hlma = hlma_high - hlma_low
    hlma_mean = hlma.rolling(trend_n, min_periods=1).mean()
    df["hlma"] = hlma / (hlma_mean + EPS) - 1.0

    high_max1 = df["High"].rolling(trend_n, min_periods=1).max()
    high_max2 = df["High"].rolling(2 * trend_n, min_periods=1).max()
    high_max3 = df["High"].rolling(3 * trend_n, min_periods=1).max()
    low_min1 = df["Low"].rolling(trend_n, min_periods=1).min()
    low_min2 = df["Low"].rolling(2 * trend_n, min_periods=1).min()
    low_min3 = df["Low"].rolling(3 * trend_n, min_periods=1).min()
    ts = (high_max1 + low_min1) / 2.0
    ks = (high_max2 + low_min2) / 2.0
    span_a = (ts + ks) / 2.0
    span_b = (high_max3 + low_min3) / 2.0
    df["ic_v2"] = (df["Close"] - span_b) / (span_a - span_b + EPS)
    df["ic_v3"] = _scale_01(span_a - span_b, trend_n)
    df["ic_v4"] = _scale_01((df["Close"] - span_b) / (span_a - span_b + EPS), trend_n)

    max_high = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    max_low = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    xpdm = np.where(pd.Series(max_high, index=df.index) > pd.Series(max_low, index=df.index),
                    pd.Series(max_high, index=df.index) - pd.Series(max_high, index=df.index).shift(1), 0.0)
    tr = np.max(np.array([
        (df["High"] - df["Low"]).abs(),
        (df["High"] - df["Close"]).abs(),
        (df["Low"] - df["Close"]).abs(),
    ]), axis=0)
    pdm = pd.Series(xpdm, index=df.index).rolling(trend_n, min_periods=1).sum()
    di_pos = pd.Series(pdm / pd.Series(tr, index=df.index).rolling(trend_n, min_periods=1).sum())
    df["adxrpos"] = 0.5 * di_pos + 0.5 * di_pos.shift(trend_n)

    atr = (df["High"] - df["Low"]).abs().ewm(span=trend_n, adjust=False).mean()
    atr_x = atr / (atr.rolling(trend_n, min_periods=1).sum() + EPS)
    ma_short = df["Close"].rolling(trend_n, min_periods=1).mean()
    ma_long = df["Close"].rolling(2 * trend_n, min_periods=1).mean()
    ma_dif = ma_short - ma_long
    dma = (ma_dif / (ma_dif.abs().rolling(2 * trend_n, min_periods=1).sum() + EPS)) + 1.0
    df["dma"] = dma * (1.0 + atr_x)

    angle_angle = df["Close"].rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_slope, raw=True)
    df["angle"] = np.degrees(np.arctan(angle_angle))

    vi_pos = pd.Series(
        np.where(df["High"] > df["Low"].shift(1), (df["High"] - df["Low"].shift(1)).abs(), 0.0),
        index=df.index,
    ).rolling(trend_n, min_periods=1).sum()
    vi_neg = pd.Series(
        np.where(df["Low"] < df["High"].shift(1), (df["Low"] - df["High"].shift(1)).abs(), 0.0),
        index=df.index,
    ).rolling(trend_n, min_periods=1).sum()
    vi_tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["Low"] - df["Close"].shift(1)).abs(),
            (df["High"] - df["Close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1).rolling(trend_n, min_periods=1).sum()
    df["vi"] = vi_pos / (vi_tr + EPS) - vi_neg / (vi_tr + EPS)

    trrq_tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    quote_volume_proxy = df["Close"] * df["Volume"]
    trrq_norm_qv = quote_volume_proxy / (quote_volume_proxy.rolling(trend_n, min_periods=1).mean() + EPS)
    trrq_reg_price = trrq_tp.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    trrq_v3_base = pd.Series(trrq_reg_price, index=df.index).pct_change(trend_n) / (trrq_norm_qv + EPS)
    df["trrq_v3"] = trrq_v3_base.rolling(trend_n, min_periods=1).sum()

    df = df.copy()

    # Source-aligned aliases and exact variants for remaining trend files.
    max_high = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    max_low = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    xpdm = np.where(pd.Series(max_high, index=df.index) > pd.Series(max_low, index=df.index),
                    pd.Series(max_high, index=df.index) - pd.Series(max_high, index=df.index).shift(1), 0.0)
    xndm = np.where(pd.Series(max_low, index=df.index) > pd.Series(max_high, index=df.index),
                    pd.Series(max_low, index=df.index).shift(1) - pd.Series(max_low, index=df.index), 0.0)
    tr = np.max(np.array([
        (df["High"] - df["Low"]).abs(),
        (df["High"] - df["Close"]).abs(),
        (df["Low"] - df["Close"]).abs(),
    ]), axis=0)
    pdm = pd.Series(xpdm, index=df.index).rolling(trend_n, min_periods=1).sum()
    ndm = pd.Series(xndm, index=df.index).rolling(trend_n, min_periods=1).sum()
    tr_sum = pd.Series(tr, index=df.index).rolling(trend_n, min_periods=1).sum()
    df["adx_di_plus"] = pdm / (tr_sum + EPS)
    df["adx_di_minus"] = ndm / (tr_sum + EPS)
    df["adxdip"] = df["adx_di_plus"]
    df["adxdim"] = df["adx_di_minus"]
    df["adxr"] = 0.5 * df["adx_di_plus"] + 0.5 * df["adx_di_plus"].shift(trend_n) - (
        0.5 * df["adx_di_minus"] + 0.5 * df["adx_di_minus"].shift(trend_n)
    )

    bbi_ma1 = df["Close"].rolling(trend_n, min_periods=1).mean()
    bbi_ma2 = df["Close"].rolling(2 * trend_n, min_periods=1).mean()
    bbi_ma3 = df["Close"].rolling(4 * trend_n, min_periods=1).mean()
    bbi_ma4 = df["Close"].rolling(8 * trend_n, min_periods=1).mean()
    bbi = (bbi_ma1 + bbi_ma2 + bbi_ma3 + bbi_ma4) / 4.0
    df["bbi"] = bbi / (df["Close"] + EPS)

    hullma_ema1 = df["Close"].ewm(span=trend_n // 2 if trend_n > 1 else 1, adjust=False).mean()
    hullma_ema2 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    hullma_x = 2.0 * hullma_ema1 - hullma_ema2
    hullma = hullma_x.ewm(span=max(1, int(np.sqrt(trend_n))), adjust=False).mean()
    df["hullma"] = hullma_x / (hullma + EPS)

    ic_n2 = 3 * trend_n
    ic_n3 = 2 * ic_n2
    ic_ts = (
        df["High"].rolling(trend_n, min_periods=1).max()
        + df["Low"].rolling(trend_n, min_periods=1).min()
    ) / 2.0
    ic_ks = (
        df["High"].rolling(ic_n2, min_periods=1).max()
        + df["Low"].rolling(ic_n2, min_periods=1).min()
    ) / 2.0
    ic_span_a = (ic_ts + ic_ks) / 2.0
    ic_span_b = (
        df["High"].rolling(ic_n3, min_periods=1).max()
        + df["Low"].rolling(ic_n3, min_periods=1).min()
    ) / 2.0
    df["ic"] = ic_span_a / (ic_span_b + EPS)

    regema_ema = df["Close"].ewm(span=trend_n, adjust=False).mean()
    regema_reg = regema_ema.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["regema"] = df["Close"] / (regema_reg + EPS) - 1.0

    regtema_ema1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    regtema_ema2 = regtema_ema1.ewm(span=trend_n, adjust=False).mean()
    regtema_ema3 = regtema_ema2.ewm(span=trend_n, adjust=False).mean()
    regtema_tema = 3.0 * regtema_ema1 - 3.0 * regtema_ema2 + regtema_ema3
    regtema_reg = regtema_tema.rolling(trend_n, min_periods=trend_n).apply(_rolling_regression_last, raw=True)
    df["regtema"] = regtema_tema / (regtema_reg + EPS) - 1.0

    tema2_ema1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    tema2_ema2 = tema2_ema1.ewm(span=trend_n, adjust=False).mean()
    tema2_ema3 = tema2_ema2.ewm(span=trend_n, adjust=False).mean()
    tema2_val = 3.0 * tema2_ema1 - 3.0 * tema2_ema2 + tema2_ema3
    df["tema_v2"] = 100.0 * (df["Close"] - tema2_val) / (tema2_val + EPS)

    tma_ma1 = df["Close"].rolling(trend_n, min_periods=1).mean()
    tma_ma2 = tma_ma1.rolling(trend_n, min_periods=1).mean()
    df["tma"] = df["Close"] / (tma_ma2 + EPS) - 1.0

    turtle_open_close_high = df[["Open", "Close"]].max(axis=1)
    turtle_open_close_low = df[["Open", "Close"]].min(axis=1)
    turtle_up = turtle_open_close_high.rolling(window=trend_n, min_periods=1).max().shift(1)
    turtle_dn = turtle_open_close_low.rolling(window=trend_n, min_periods=1).min().shift(1)
    turtle_d = pd.Series(0.0, index=df.index)
    turtle_d = turtle_d.where(~((df["Close"] > turtle_up) | (df["Close"] < turtle_dn)), turtle_d)
    turtle_d.loc[df["Close"] > turtle_up] = df["Close"] - turtle_up
    turtle_d.loc[df["Close"] < turtle_dn] = df["Close"] - turtle_dn
    df["turtle"] = turtle_d / (turtle_up - turtle_dn + EPS)

    vidya_base = df["Close"]
    vidya_er = (vidya_base - vidya_base.shift(trend_n)).abs() / (
        vidya_base - vidya_base.shift(1)
    ).abs().rolling(trend_n, min_periods=1).sum()
    vidya_val = vidya_er * vidya_base + (1.0 - vidya_er) * vidya_base.shift(1)
    df["vidya"] = vidya_val / (df["Close"].rolling(trend_n, min_periods=1).mean() + EPS) - 1.0

    t3_va = 0.5
    t3_ema1 = df["Close"].ewm(span=trend_n, adjust=False).mean()
    t3_ema2 = t3_ema1.ewm(span=trend_n, adjust=False).mean()
    t3_t1 = t3_ema1 * (1.0 + t3_va) - t3_ema2 * t3_va
    t3_t1_ema1 = t3_t1.ewm(span=trend_n, adjust=False).mean()
    t3_t1_ema2 = t3_t1_ema1.ewm(span=trend_n, adjust=False).mean()
    t3_t2 = t3_t1_ema1 * (1.0 + t3_va) - t3_t1_ema2 * t3_va
    t3_t2_ema1 = t3_t2.ewm(span=trend_n, adjust=False).mean()
    t3_t2_ema2 = t3_t2_ema1.ewm(span=trend_n, adjust=False).mean()
    t3_val = t3_t2_ema1 * (1.0 + t3_va) - t3_t2_ema2 * t3_va
    df.loc[:, "t3"] = df["Close"] / (t3_val + EPS) - 1.0

    df["Mac_v2"] = df["mac_v2"]
    df["Mac_v3"] = df["mac_v3"]
    df["Mac_v4"] = df["mac_v4"]
    df["Mac_v5"] = df["mac_v5"]
    df["Vidya_v2"] = df["vidya_v2"]
    df["Vidya_v3"] = df["vidya_v3"]
    df["Vidya_v4"] = df["vidya_v4"]
    df["Vidya_v5"] = df["vidya_v5"]
    df["Tma_v2"] = df["tma_v2"]
    df["Tma_v3"] = df["tma_v3"]
    df["Arron"] = df["arron"]
    df["Mac"] = df["mac"]
    df["Vidya"] = df["vidya"]
    df["Tma"] = df["tma"]
    df["Ma"] = df["ma"]
    df["Vma"] = df["vma"]
    df["Mm"] = df["mm"]
    df["Gap"] = df["gap"]
    df["Dema"] = df["dema"]
    df["Tema"] = df["tema"]
    df["Hma"] = df["hma"]
    df["Reg"] = df["reg"]
    df["Reg_v2"] = df["reg_v2"]
    df["Reg_v3"] = df["reg_v3"]
    df["T3"] = df["t3"]
    df["DiffEma"] = df["diff_ema"]
    df["Adxrpos"] = df["adxr_pos"]
    df["Adxrneg"] = df["adxr_neg"]
    df["Expma"] = df["expma"]
    df["Vi"] = df["vi"]
    df["Bbi"] = df["bbi"]
    df["RegTema"] = df["regtema"]
    df["Turtle"] = df["turtle"]
    df["MaSignal"] = df["ma_signal"]
    df["HmaSignal"] = df["hma_signal"]
    df["HullmaSignal"] = df["hullma_signal"]
    df["Ic"] = df["ic"]
    df["Ic_v2"] = df["ic_v2"]
    df["Ic_v3"] = df["ic_v3"]
    df["Ic_v4"] = df["ic_v4"]
    df["Adxr"] = df["adxr"]
    df["Regema"] = df["regema"]
    df["Adx"] = df["adx_strength"]
    df["Dma"] = df["dma"]
    df["Vi+"] = df["vi_plus"]
    df["Vi-"] = df["vi_minus"]
    df["Reg"] = df["reg"]
    df["Acs"] = df["acs"]
    df["Mak"] = df["mak"]
    df["Sgcz"] = df["sgcz"]
    df["Cse"] = df["cse"]
    df["Trrq"] = df["trrq"]
    df["Mreg"] = df["mreg"]
    df["Angle"] = df["angle_reg"]
    df["AdxDi+"] = df["adx_di_plus"]
    df["AdxDi-"] = df["adx_di_minus"]
    df["BbiBias"] = df["bbi_bias"]
    df["Trv"] = df["trv"]
    df["PjcDistance"] = df["pjc_distance"]
    df["Trrq_v3"] = df["trrq_v3"]
    df["TrTrix"] = df["trtrix"]

    # --- Indicator features used by signal.py ---
    # They use fixed windows rather than config-based lookbacks.

    hma_20 = ta.hma(df["Close"], length=20)
    df["hma20"] = hma_20 if hma_20 is not None else np.nan

    kama_10 = ta.kama(df["Close"], length=10)
    df["kama10"] = kama_10 if kama_10 is not None else np.nan

    trix_result = ta.trix(df["Close"], length=15, signal=9)
    if trix_result is not None and not trix_result.empty:
        df["trix15"] = trix_result.iloc[:, 0]
        df["trix15_signal"] = trix_result.iloc[:, 1]
    else:
        df["trix15"] = np.nan
        df["trix15_signal"] = np.nan

    supertrend_result = ta.supertrend(df["High"], df["Low"], df["Close"], length=10, multiplier=3.0)
    if supertrend_result is not None and not supertrend_result.empty:
        df["supertrend_dir"] = supertrend_result.iloc[:, 1]
    else:
        df["supertrend_dir"] = np.nan

    ichimoku_result = ta.ichimoku(df["High"], df["Low"], df["Close"])
    if isinstance(ichimoku_result, tuple):
        ichimoku_result = ichimoku_result[0]
    if ichimoku_result is not None and not ichimoku_result.empty:
        df["tenkan"] = ichimoku_result.iloc[:, 0]
        df["kijun"] = ichimoku_result.iloc[:, 1]
        df["span_a"] = ichimoku_result.iloc[:, 2]
        df["span_b"] = ichimoku_result.iloc[:, 3]
    else:
        df["tenkan"] = np.nan
        df["kijun"] = np.nan
        df["span_a"] = np.nan
        df["span_b"] = np.nan

    df["linreg_slope20"] = _linear_regression_slope(df["Close"], 20)
    df["linreg_mid20"] = _linear_regression_midline(df["Close"], 20)
    df["linreg_upper20"] = df["linreg_mid20"] + 2 * df["std20"]
    df["linreg_lower20"] = df["linreg_mid20"] - 2 * df["std20"]

    df["tma10"] = df["Close"].rolling(10).mean().rolling(10).mean()

    df["high_5"] = df["High"].rolling(5).max()
    df["low_5"] = df["Low"].rolling(5).min()
    df["high_10"] = df["High"].rolling(10).max()
    df["low_10"] = df["Low"].rolling(10).min()
    df["high_20"] = df["High"].rolling(20).max()
    df["low_20"] = df["Low"].rolling(20).min()
    df["range_mid_10"] = (df["high_10"] + df["low_10"]) / 2.0
    df["recent_high"] = df["High"].rolling(20).max().shift(1)
    df["recent_low"] = df["Low"].rolling(20).min().shift(1)
    df["recent_high_prev"] = df["recent_high"].shift(5)
    df["recent_low_prev"] = df["recent_low"].shift(5)
    df["prev_5_low"] = df["low_5"].shift(1)
    df["prev_5_high"] = df["high_5"].shift(1)
    df["prev_10_low"] = df["low_10"].shift(1)
    df["prev_10_high"] = df["high_10"].shift(1)
    df["prev_20_low"] = df["low_20"].shift(1)
    df["prev_20_high"] = df["high_20"].shift(1)
    df["lower_range_pos"] = df["low_10"] + (df["high_10"] - df["low_10"]) * 0.3
    df["upper_range_pos"] = df["high_10"] - (df["high_10"] - df["low_10"]) * 0.3

    df["ema_8"] = ta.ema(df["Close"], length=8)
    df["ema_20"] = ta.ema(df["Close"], length=20)
    df["ema_21"] = ta.ema(df["Close"], length=21)
    df["ema_55"] = ta.ema(df["Close"], length=55)
    df["ema_250"] = ta.ema(df["Close"], length=250)
    df["ema_20_cross_above_ema_250"] = (
        (df["ema_20"].shift(1) < df["ema_250"].shift(1))
        & (df["ema_20"] > df["ema_250"])
    )
    df["ema_20_cross_below_ema_250"] = (
        (df["ema_20"].shift(1) > df["ema_250"].shift(1))
        & (df["ema_20"] < df["ema_250"])
    )

    adx_14 = ta.adx(df["High"], df["Low"], df["Close"], length=14)
    if adx_14 is not None and not adx_14.empty:
        df["adx_14"] = adx_14["ADX_14"] if "ADX_14" in adx_14 else np.nan
        df["dmp_14"] = adx_14["DMP_14"] if "DMP_14" in adx_14 else np.nan
        df["dmn_14"] = adx_14["DMN_14"] if "DMN_14" in adx_14 else np.nan
    else:
        df["adx_14"] = np.nan
        df["dmp_14"] = np.nan
        df["dmn_14"] = np.nan

    adx_42 = ta.adx(df["High"], df["Low"], df["Close"], length=42)
    if adx_42 is not None and not adx_42.empty and "ADX_42" in adx_42:
        df["adx_42"] = adx_42["ADX_42"]
    else:
        df["adx_42"] = np.nan

    psar = ta.psar(df["High"], df["Low"], df["Close"])
    if psar is not None and not psar.empty:
        bull_cols = [col for col in psar.columns if "PSARl" in col]
        bear_cols = [col for col in psar.columns if "PSARs" in col]
        df["psar_bull"] = psar[bull_cols[0]].notna() if bull_cols else False
        df["psar_bear"] = psar[bear_cols[0]].notna() if bear_cols else False
    else:
        df["psar_bull"] = False
        df["psar_bear"] = False

    df["linear_regression_slope_5"] = ta.slope(df["Close"], length=5)
    df["linear_regression_slope_8"] = ta.slope(df["Close"], length=8)

    return df
