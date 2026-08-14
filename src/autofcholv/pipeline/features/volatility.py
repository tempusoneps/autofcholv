import numpy as np
import pandas as pd
import pandas_ta as ta
from autofcholv.config.config import Config
from autofcholv.utils.indicators import get_true_range, get_atr, get_sma_close, get_std_close


EPS = 1e-8


def _scale_01(series: pd.Series, window: int) -> pd.Series:
    low = series.rolling(window, min_periods=1).min()
    high = series.rolling(window, min_periods=1).max()
    return (series - low) / (high - low + EPS)


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate volatility and channel features adapted from quant-ohlcv-feature.
    Feature definitions follow volatility.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    volatility_n = config.volatility_lookback

    quote_volume_proxy = df["Close"] * df["Volume"]
    df["quote_volume_std"] = quote_volume_proxy.rolling(volatility_n, min_periods=2).std()

    hourly_amplitude = np.maximum(
        (df["High"] / (df["Open"] + EPS) - 1.0).abs(),
        (df["Low"] / (df["Open"] + EPS) - 1.0).abs(),
    )
    df["amplitude_max"] = hourly_amplitude.rolling(volatility_n, min_periods=1).max()

    avg_price = (df["Close"] + df["High"] + df["Low"]) / 3.0
    positive_amplitude = np.where(
        avg_price.pct_change() > 0,
        (df["High"] - df["Low"]) / (df["Open"] + EPS),
        0.0,
    )
    positive_amplitude_mean = pd.Series(positive_amplitude, index=df.index).rolling(
        volatility_n,
        min_periods=1,
    ).mean()
    df["positive_amplitude_rank"] = positive_amplitude_mean.rolling(
        volatility_n,
        min_periods=1,
    ).rank(pct=True)

    high_low_range = df["High"] - df["Low"]
    apz_vol = high_low_range.ewm(span=volatility_n, adjust=False).mean().ewm(
        span=volatility_n,
        adjust=False,
    ).mean()
    apz_center = df["Close"].ewm(span=volatility_n * 2, adjust=False).mean().ewm(
        span=volatility_n * 2,
        adjust=False,
    ).mean()
    df["apz_width"] = apz_vol / (apz_center + EPS)

    pac_upper = df["High"].ewm(span=volatility_n, adjust=False).mean()
    pac_lower = df["Low"].ewm(span=volatility_n, adjust=False).mean()
    pac_width = pac_upper - pac_lower
    pac_width_ma = pac_width.rolling(volatility_n, min_periods=1).mean()
    df["pac_width_bias"] = pac_width / (pac_width_ma + EPS) - 1.0
    df["pac_position"] = (df["Close"] - pac_lower) / (pac_width + EPS)

    env_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    env_lower = env_middle * 0.95
    env_upper = env_middle * 1.05
    df["env_position"] = (df["Close"] - env_lower) / (env_upper - env_lower + EPS)


    close_ma = df["Close"].rolling(volatility_n, min_periods=volatility_n).mean()
    close_std = df["Close"].rolling(volatility_n, min_periods=2).std(ddof=0)
    z_score = (df["Close"] - close_ma).abs() / (close_std + EPS)
    adaptive_mult = z_score.rolling(volatility_n, min_periods=1).mean()
    df["adaptive_bollinger_width"] = 2.0 * close_std * adaptive_mult / (close_ma + EPS)

    quote_volume_proxy = df["Close"] * df["Volume"]
    vwap_proxy = quote_volume_proxy / (df["Volume"] + EPS)
    vwap_change = vwap_proxy.pct_change(volatility_n)
    bbw_top = close_ma + 2.0 * close_std
    bbw_bottom = close_ma - 2.0 * close_std
    bbw_ratio = bbw_top / (bbw_bottom + EPS)
    bbw_change = bbw_ratio.pct_change(volatility_n)
    quote_volume_normalized = quote_volume_proxy / (
        quote_volume_proxy.rolling(volatility_n, min_periods=1).mean() + EPS
    )
    vwap_bbw_component = (vwap_change * bbw_change) / (quote_volume_normalized + EPS)
    df["vwap_bbw_efficiency"] = vwap_bbw_component.rolling(volatility_n, min_periods=1).sum()

    high_low_ema = (df["High"] - df["Low"]).ewm(span=volatility_n, adjust=False).mean()
    df["chaikin_volatility"] = (
        (high_low_ema - high_low_ema.shift(volatility_n))
        / (high_low_ema.shift(volatility_n) + EPS)
        * 100.0
    )

    realized_volatility = df["Close"].pct_change().rolling(
        volatility_n,
        min_periods=2,
    ).std(ddof=0)
    df["realized_volatility"] = realized_volatility
    df["realized_volatility_zscore"] = (
        realized_volatility - realized_volatility.rolling(volatility_n, min_periods=2).mean()
    ) / (realized_volatility.rolling(volatility_n, min_periods=2).std(ddof=0) + EPS)


    prev_close = df["Close"].shift(1)
    true_range = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - prev_close).abs(),
            (prev_close - df["Low"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = true_range.rolling(volatility_n, min_periods=1).mean()
    rwih = (df["High"] - df["Low"].shift(1)) / (np.sqrt(volatility_n) * atr + EPS)
    rwil = (df["High"].shift(1) - df["Low"]) / (np.sqrt(volatility_n) * atr + EPS)
    df["rwi"] = (df["Close"] - rwil) / (rwih - rwil + EPS)

    rolling_high = df["High"].rolling(volatility_n, min_periods=1).max()
    drawdown = (df["Close"] / (rolling_high + EPS) - 1.0).abs()
    avg_max_drawdown = drawdown.rolling(volatility_n, min_periods=1).mean()
    rolling_low = df["Low"].rolling(volatility_n, min_periods=1).min()
    reverse_drawdown = (df["Close"] / (rolling_low + EPS) - 1.0).abs()
    avg_reverse_drawdown = reverse_drawdown.rolling(volatility_n, min_periods=1).mean()
    df["mssi"] = pd.concat([avg_max_drawdown, avg_reverse_drawdown], axis=1).max(axis=1)

    vix_like = df["Close"] / df["Close"].shift(volatility_n) - 1.0
    vix_median = vix_like.rolling(volatility_n, min_periods=1).mean()
    vix_std = vix_like.rolling(volatility_n, min_periods=2).std()
    vix_score = (vix_like - vix_median).abs() / (vix_std + EPS)
    vix_band_mult = vix_score.rolling(volatility_n, min_periods=1).mean().shift(1)
    vix_upper = vix_median + vix_band_mult * vix_std
    vix_lower = vix_median - vix_band_mult * vix_std
    vix_direction = np.sign(vix_median.diff(volatility_n))
    vix_bw = (vix_upper - vix_lower) * vix_direction
    conflict_1 = vix_direction != np.sign(vix_median.diff(1))
    conflict_2 = vix_direction != np.sign(vix_median.diff(1).shift(1))
    df["vix_bw"] = np.where(conflict_1 | conflict_2, 0.0, vix_bw)


    kc_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    kc_upper = kc_middle + 2.0 * atr
    kc_lower = kc_middle - 2.0 * atr
    df["keltner_width"] = (kc_upper - kc_lower) / (kc_middle + EPS)
    df["keltner_upper_signal"] = _scale_01(kc_upper, volatility_n)
    df["keltner_lower_signal"] = _scale_01(kc_lower, volatility_n)

    df["env_upper_signal"] = _scale_01(env_upper, volatility_n)
    df["env_lower_signal"] = _scale_01(env_lower, volatility_n)

    fb_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    fb_upper_1 = fb_middle + 1.618 * atr
    fb_lower_1 = fb_middle - 1.618 * atr
    fb_upper_2 = fb_middle + 2.618 * atr
    fb_lower_2 = fb_middle - 2.618 * atr
    df["fibonacci_band_width"] = (fb_upper_2 - fb_lower_2) / (fb_middle + EPS)
    df["fibonacci_band_position"] = (df["Close"] - fb_lower_1) / (fb_upper_1 - fb_lower_1 + EPS)

    donchian_mid = (df["High"].rolling(volatility_n, min_periods=1).max() + df["Low"].rolling(volatility_n, min_periods=1).min()) / 2.0
    df["donchian_mid_signal"] = df["Close"] - donchian_mid


    atr_tr = get_true_range(df)

    # 5-tier ATR
    df["atr_micro"] = get_atr(df, config.micro_lookback)
    df["atr_short"] = get_atr(df, config.short_lookback)
    df["atr_medium"] = get_atr(df, config.medium_lookback)
    df["atr_long"] = get_atr(df, config.long_lookback)
    df["atr_macro"] = get_atr(df, config.macro_lookback)

    # 5-tier ATR Pct
    df["atr_pct_micro"] = df["atr_micro"] / (df["Close"] + EPS)
    df["atr_pct_short"] = df["atr_short"] / (df["Close"] + EPS)
    df["atr_pct_medium"] = df["atr_medium"] / (df["Close"] + EPS)
    df["atr_pct_long"] = df["atr_long"] / (df["Close"] + EPS)
    df["atr_pct_macro"] = df["atr_macro"] / (df["Close"] + EPS)

    pfe_direct = (df["Close"] - df["Close"].shift(volatility_n - 1))
    pfe_direct = (pfe_direct ** 2 + (volatility_n - 1) ** 2) ** 0.5
    pfe_each = (df["Close"].diff() ** 2 + 1.0) ** 0.5
    pfe_actual = pfe_each.rolling(max(1, volatility_n - 1)).sum()
    df["pfe"] = 100.0 * (pfe_direct / (pfe_actual + EPS)) * df["Close"].pct_change(volatility_n - 1)
    df["change_std"] = df["Close"].pct_change(volatility_n) * df["Close"].pct_change().rolling(volatility_n).std(ddof=0)

    rwi_atr = atr_tr.rolling(volatility_n, min_periods=1).mean()
    df["rwi_high"] = (df["High"] - df["Low"].shift(1)) / (rwi_atr * np.sqrt(volatility_n) + EPS)
    df["rwi_low"] = (df["High"].shift(1) - df["Low"]) / (rwi_atr * np.sqrt(volatility_n) + EPS)


    close_dif = df["Close"].diff()
    bbw_up = pd.Series(np.where(close_dif > 0, close_dif, 0.0), index=df.index)
    bbw_down = pd.Series(np.where(close_dif < 0, -close_dif, 0.0), index=df.index)
    bbw_up_sum = bbw_up.rolling(volatility_n, min_periods=1).sum()
    bbw_down_sum = bbw_down.rolling(volatility_n, min_periods=1).sum()
    bbw_rsi = 100.0 * bbw_up_sum / (bbw_up_sum + bbw_down_sum + EPS)
    bbw_median = df["Close"].rolling(volatility_n, min_periods=1).mean()
    bbw_std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    bbw = (bbw_std / (bbw_median + EPS)).diff(volatility_n)
    df["bbw_signal"] = bbw * (df["Close"].pct_change(volatility_n) + EPS) * bbw_rsi



    tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - df["Close"].shift(1)).abs(),
            (df["Low"] - df["Close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(volatility_n, min_periods=1).mean()
    kc_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    kc_upper = kc_middle + 2.0 * atr
    kc_lower = kc_middle - 2.0 * atr
    df["kc_signal"] = (df["Close"] - kc_middle + 2.0 * atr) / (4.0 * atr + EPS)
    df["atr_upper_medium"] = (df["Low"].rolling(max(1, volatility_n // 2), min_periods=1).min() + 3.0 * atr) / (df["Close"].rolling(volatility_n, min_periods=1).mean() + EPS)
    df["atr_lower_medium"] = (df["Close"].rolling(volatility_n, min_periods=1).mean() - 0.2 * volatility_n * atr) / (df["Close"].rolling(volatility_n, min_periods=1).mean() + EPS)

    fb_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    fb_upper = fb_middle + 1.618 * atr
    fb_lower = fb_middle - 1.618 * atr
    df["fb_upper_signal"] = (df["Close"] - fb_middle - 1.618 * atr) / (fb_upper - fb_lower + EPS)

    pac_upper = df["High"].ewm(span=volatility_n, adjust=False).mean()
    pac_lower = df["Low"].ewm(span=volatility_n, adjust=False).mean()
    pac_width = pac_upper - pac_lower
    df["pac_width_signal"] = pac_width / (pac_width.rolling(volatility_n, min_periods=1).mean() + EPS) - 1.0

    df["volume_std"] = (df["Volume"].rolling(volatility_n, min_periods=2).std(ddof=0))

    grid_median = df["Close"].rolling(volatility_n, min_periods=1).mean()
    grid_std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    grid = (df["Close"] - grid_median) / (grid_std + EPS)
    grid_shift = grid.shift(volatility_n)
    df["grid"] = ((grid - grid_shift) / (grid_shift.abs() + EPS)).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    df["lcsd"] = (df["Low"] - df["Close"].rolling(volatility_n, min_periods=1).mean()) / (df["Low"] + EPS)

    atr_count_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    atr_count_atr = true_range.rolling(volatility_n, min_periods=1).mean()
    atr_count_upper = atr_count_middle + 2.0 * atr_count_atr
    atr_count_lower = atr_count_middle - 2.0 * atr_count_atr
    atr_count = pd.Series(np.zeros(len(df)), index=df.index)
    atr_count.loc[df["Close"] > atr_count_upper] = 1.0
    atr_count.loc[df["Close"] < atr_count_lower] = -1.0
    df["atr_count"] = atr_count.rolling(volatility_n, min_periods=1).sum()

    zf_avg_price = (df["Close"] + df["High"] + df["Low"]) / 3.0
    zf_change = zf_avg_price.pct_change()
    zf_amplitude = (df["High"] - df["Low"]) / (df["Open"] + EPS)
    zf_amplitude = np.where(zf_change > 0, zf_amplitude, 0.0)
    zf_amplitude_mean = pd.Series(zf_amplitude, index=df.index).rolling(volatility_n, min_periods=1).mean()
    df["zfabsmean"] = zf_amplitude_mean.rolling(volatility_n, min_periods=1).rank(ascending=True, pct=True)

    bbw_close_dif = df["Close"].diff()
    bbw_up = np.where(bbw_close_dif > 0, bbw_close_dif, 0.0)
    bbw_down = np.where(bbw_close_dif < 0, -bbw_close_dif, 0.0)
    bbw_rsi_num = pd.Series(bbw_up, index=df.index).rolling(volatility_n, min_periods=1).sum()
    bbw_rsi_den = pd.Series(bbw_down, index=df.index).rolling(volatility_n, min_periods=1).sum()
    bbw_rsi = 100.0 * bbw_rsi_num / (bbw_rsi_num + bbw_rsi_den + EPS)
    bbw_median = df["Close"].rolling(volatility_n, min_periods=1).mean()
    bbw_std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    bbw = (bbw_std / (bbw_median + EPS)).diff(volatility_n)
    df["bbw"] = bbw * (df["Close"].pct_change(volatility_n) + EPS) * bbw_rsi

    df = df.copy()

    hl = df["High"] - df["Low"]
    ema_hl = hl.ewm(span=volatility_n, adjust=False).mean()
    apz_vol = ema_hl.ewm(span=volatility_n, adjust=False).mean()
    ema_close = df["Close"].ewm(span=2 * volatility_n, adjust=False).mean()
    ema_ema_close = ema_close.ewm(span=2 * volatility_n, adjust=False).mean()
    df["apz"] = apz_vol / (ema_ema_close + EPS)
    upper = ema_ema_close + 2.0 * apz_vol
    lower = ema_ema_close - 2.0 * apz_vol
    df["apz_upper"] = (upper - upper.rolling(volatility_n, min_periods=1).min()) / (
        upper.rolling(volatility_n, min_periods=1).max() - upper.rolling(volatility_n, min_periods=1).min() + EPS
    )
    df["apz_lower"] = (lower - lower.rolling(volatility_n, min_periods=1).min()) / (
        lower.rolling(volatility_n, min_periods=1).max() - lower.rolling(volatility_n, min_periods=1).min() + EPS
    )

    std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    ma = df["Close"].rolling(volatility_n, min_periods=1).mean()
    upper_boll = ma + std
    lower_boll = ma - std
    distance = pd.Series(0.0, index=df.index)
    distance.loc[df["Close"] > upper_boll] = df["Close"] - upper_boll
    distance.loc[df["Close"] < lower_boll] = df["Close"] - lower_boll
    df["bolling"] = distance / (std + EPS)
    df["bolling_width"] = 2.0 * std * distance.abs().rolling(volatility_n, min_periods=1).mean() / (ma + EPS)

    hl_ema = (df["High"] - df["Low"]).ewm(span=volatility_n, adjust=False).mean()
    df["cv"] = (hl_ema - hl_ema.shift(volatility_n)) / (hl_ema.shift(volatility_n) + EPS) * 100.0

    df = df.copy()

    dc_upper = df["High"].rolling(volatility_n, min_periods=1).max()
    dc_lower = df["Low"].rolling(volatility_n, min_periods=1).min()
    dc_middle = (dc_upper + dc_lower) / 2.0
    df["dc"] = (dc_upper - dc_lower) / (dc_middle + EPS)
    df["dc_signal"] = df["Close"] - dc_middle
    df["dc_v2"] = (df["Close"] - dc_middle) / (dc_middle + EPS)

    kc_tmp1 = df["High"] - df["Low"]
    kc_tmp2 = (df["High"] - df["Close"].shift(1)).abs()
    kc_tmp3 = (df["Low"] - df["Close"].shift(1)).abs()
    kc_atr = pd.Series(np.max(np.array([kc_tmp1, kc_tmp2, kc_tmp3]), axis=0), index=df.index).rolling(volatility_n, min_periods=1).mean()
    kc_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    kc_upper = kc_middle + 2.0 * kc_atr
    kc_lower = kc_middle - 2.0 * kc_atr
    df["kcupper"] = (kc_upper - kc_upper.rolling(volatility_n, min_periods=1).min()) / (
        kc_upper.rolling(volatility_n, min_periods=1).max() - kc_upper.rolling(volatility_n, min_periods=1).min() + EPS
    )
    df["kclower"] = (kc_lower - kc_lower.rolling(volatility_n, min_periods=1).min()) / (
        kc_lower.rolling(volatility_n, min_periods=1).max() - kc_lower.rolling(volatility_n, min_periods=1).min() + EPS
    )

    pac_upper = df["High"].ewm(alpha=1 / volatility_n, adjust=False).mean()
    pac_lower = df["Low"].ewm(alpha=1 / volatility_n, adjust=False).mean()
    df["pac"] = (pac_upper - pac_lower).rolling(volatility_n, min_periods=1).mean() / (
        (pac_upper - pac_lower).rolling(volatility_n, min_periods=1).mean().rolling(volatility_n, min_periods=1).mean() + EPS
    )
    df["pacupper"] = (pac_upper - pac_upper.rolling(volatility_n, min_periods=1).min()) / (
        pac_upper.rolling(volatility_n, min_periods=1).max() - pac_upper.rolling(volatility_n, min_periods=1).min() + EPS
    )
    df["paclower"] = (pac_lower - pac_lower.rolling(volatility_n, min_periods=1).min()) / (
        pac_lower.rolling(volatility_n, min_periods=1).max() - pac_lower.rolling(volatility_n, min_periods=1).min() + EPS
    )
    df["pacupper_v2"] = (df["Close"] - pac_upper - 0.0).rolling(volatility_n, min_periods=1).mean()
    df["paclower_v2"] = (pac_lower - df["Close"]).rolling(volatility_n, min_periods=1).mean()


    df = df.copy()

    std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    ma = df["Close"].rolling(volatility_n, min_periods=1).mean()
    upper = ma + std
    lower = ma - std
    distance = pd.Series(0.0, index=df.index)
    distance.loc[df["Close"] > upper] = df["Close"] - upper
    distance.loc[df["Close"] < lower] = df["Close"] - lower
    df["bolling"] = distance / (std + EPS)
    df["bolling_v2"] = (std * 2.0) / (ma + EPS)
    df["bolling_v3"] = (upper - upper.shift(1)) / (ma + EPS)
    df["bolling_fancy"] = (df["Close"] - ma) / (std + EPS)

    env_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    env_lower = env_middle * 0.95
    env_upper = env_middle * 1.05
    df["env_signal"] = (df["Close"] - env_lower) / (0.1 * env_middle + EPS)
    df["env_upper"] = _scale_01(env_upper, volatility_n)
    df["env_lower"] = _scale_01(env_lower, volatility_n)

    kc_tmp1 = df["High"] - df["Low"]
    kc_tmp2 = (df["High"] - df["Close"].shift(1)).abs()
    kc_tmp3 = (df["Low"] - df["Close"].shift(1)).abs()
    kc_atr = pd.Series(np.max(np.array([kc_tmp1, kc_tmp2, kc_tmp3]), axis=0), index=df.index).rolling(volatility_n, min_periods=1).mean()
    kc_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    df["kc_signal"] = (df["Close"] - kc_middle + 2.0 * kc_atr) / (4.0 * kc_atr + EPS)
    df["kc_upper_signal"] = _scale_01(df["Close"] - kc_middle + 2.0 * kc_atr, volatility_n)
    df["kc_lower_signal"] = _scale_01(kc_middle - 2.0 * kc_atr - df["Close"], volatility_n)

    quote_volume_proxy = df["Close"] * df["Volume"]
    vwap = quote_volume_proxy / (df["Volume"] + EPS)
    vwap_chg = vwap.pct_change(volatility_n)
    width = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0) * 2.0
    avg = df["Close"].rolling(volatility_n, min_periods=1).mean()
    bbw = (avg + width) / (avg - width + EPS)
    bbw_chg = bbw.pct_change(volatility_n)
    quote_volume_normalized = quote_volume_proxy / (quote_volume_proxy.rolling(volatility_n, min_periods=1).mean() + EPS)
    feature = (vwap_chg * bbw_chg) / (quote_volume_normalized + EPS)
    df["vwap_bbw"] = feature.rolling(volatility_n, min_periods=1).sum()

    ret = df["Close"].pct_change()
    df["ret_boll_fancy"] = (ret - ret.rolling(volatility_n, min_periods=1).mean()) / (ret.rolling(volatility_n, min_periods=1).std() + EPS)

    df["lchc_fancy"] = -1.0 * df["Low"].rolling(volatility_n, min_periods=1).min() / (df["Close"] + EPS) - df["High"].rolling(volatility_n, min_periods=1).max() / (df["Close"] + EPS)


    mtm = df["Close"] / (df["Close"].shift(volatility_n) + EPS) - 1.0
    mtm_mean = mtm.rolling(volatility_n, min_periods=1).mean()
    c1 = df["High"] - df["Low"]
    c2 = (df["High"] - df["Close"].shift(1)).abs()
    c3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([c1, c2, c3], axis=1).max(axis=1)
    atr = tr.rolling(volatility_n, min_periods=1).mean()
    avg_price = df["Close"].rolling(volatility_n, min_periods=1).mean()
    wd_atr = atr / (avg_price + EPS)
    mtm_l = df["Low"] / (df["Low"].shift(volatility_n) + EPS) - 1.0
    mtm_h = df["High"] / (df["High"].shift(volatility_n) + EPS) - 1.0
    mtm_c = df["Close"] / (df["Close"].shift(volatility_n) + EPS) - 1.0
    mtm_c1 = mtm_h - mtm_l
    mtm_c2 = (mtm_h - mtm_c.shift(1)).abs()
    mtm_c3 = (mtm_l - mtm_c.shift(1)).abs()
    mtm_tr = pd.concat([mtm_c1, mtm_c2, mtm_c3], axis=1).max(axis=1)
    mtm_atr = mtm_tr.rolling(volatility_n, min_periods=1).mean()
    mtm_l_mean = mtm_l.rolling(volatility_n, min_periods=1).mean()
    mtm_h_mean = mtm_h.rolling(volatility_n, min_periods=1).mean()
    mtm_c_mean = mtm_c.rolling(volatility_n, min_periods=1).mean()
    mtm_c1 = mtm_h_mean - mtm_l_mean
    mtm_c2 = (mtm_h_mean - mtm_c_mean.shift(1)).abs()
    mtm_c3 = (mtm_l_mean - mtm_c_mean.shift(1)).abs()
    mtm_atr_mean = pd.concat([mtm_c1, mtm_c2, mtm_c3], axis=1).max(axis=1).rolling(volatility_n, min_periods=1).mean()
    df["adapt_bolling_v3"] = mtm_mean * mtm_atr * mtm_atr_mean * wd_atr * 100000000

    demax = df["High"].diff().clip(lower=0.0)
    demin = (df["Low"].shift(1) - df["Low"]).clip(lower=0.0)
    ma_demax = demax.rolling(volatility_n, min_periods=1).mean()
    ma_demin = demin.rolling(volatility_n, min_periods=1).mean()
    demaker = ma_demax / (ma_demax + ma_demin + EPS)
    count = pd.Series(0.0, index=df.index)
    count.loc[demaker > 0.7] = 1.0
    count.loc[demaker < 0.3] = -1.0
    df["bollcount_dem"] = count.rolling(volatility_n, min_periods=1).sum()

    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    cci_ma = tp.rolling(volatility_n, min_periods=1).mean()
    cci_md = (tp - cci_ma).abs().rolling(volatility_n, min_periods=1).mean()
    cci = (tp - cci_ma) / (0.015 * cci_md + EPS)
    cci_middle = cci.rolling(volatility_n, min_periods=1).mean()
    cci_lower = cci_middle - 2.0 * cci.rolling(volatility_n, min_periods=1).std()
    cci_upper = cci_middle + 2.0 * cci.rolling(volatility_n, min_periods=1).std()
    cci_ma_short = cci.rolling(max(1, int(volatility_n / 4)), min_periods=1).mean()
    df["dzcci_lower"] = cci_lower - cci_ma_short
    df["dzcci_upper"] = _scale_01(cci_upper, volatility_n)

    rtn = df["Close"].diff()
    up = rtn.clip(lower=0.0)
    dn = (-rtn).clip(lower=0.0)
    a = up.rolling(volatility_n, min_periods=1).sum() * 1e3
    b = dn.rolling(volatility_n, min_periods=1).sum() * 1e3
    rsi = a / (a + b + EPS)
    rsi_middle = rsi.rolling(volatility_n, min_periods=1).mean()
    rsi_lower = rsi_middle - 2.0 * rsi.rolling(volatility_n, min_periods=1).std()
    rsi_upper = rsi_middle + 2.0 * rsi.rolling(volatility_n, min_periods=1).std()
    rsi_ma = rsi.rolling(max(1, int(volatility_n / 2)), min_periods=1).mean()
    dzrsi_lower = rsi_lower - rsi_ma
    dzrsi_upper = rsi_ma - rsi_upper
    dzrsi_lower_mean = dzrsi_lower.rolling(volatility_n, min_periods=1).mean()
    dzrsi_lower_std = dzrsi_lower.rolling(volatility_n, min_periods=1).std()
    df["dzrsi_lower_signal"] = (dzrsi_lower - dzrsi_lower_mean) / (dzrsi_lower_std + EPS)
    df["dzrsi_upper_signal"] = (dzrsi_upper - dzrsi_upper.rolling(volatility_n, min_periods=1).min()) / (dzrsi_upper.rolling(volatility_n, min_periods=1).max() - dzrsi_upper.rolling(volatility_n, min_periods=1).min() + EPS)

    fb_atr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift(1)).abs(),
        (df["Low"] - df["Close"].shift(1)).abs(),
    ], axis=1).max(axis=1).rolling(volatility_n, min_periods=1).mean()
    fb_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    df["fb_lower"] = _scale_01(fb_middle - 1.618 * fb_atr, volatility_n)
    df["fb_upper"] = _scale_01(fb_middle + 1.618 * fb_atr, volatility_n)

    tp2 = (df["High"] + df["Low"] + df["Close"]) / 3.0
    cci_ma2 = tp2.rolling(volatility_n, min_periods=1).mean()
    cci_md2 = (tp2 - cci_ma2).abs().rolling(volatility_n, min_periods=1).mean()
    cci2 = (tp2 - cci_ma2) / (0.015 * cci_md2 + EPS)
    cci_middle2 = cci2.rolling(volatility_n, min_periods=1).mean()
    cci_lower2 = cci_middle2 - 2.0 * cci2.rolling(volatility_n, min_periods=1).std()
    cci_upper2 = cci_middle2 + 2.0 * cci2.rolling(volatility_n, min_periods=1).std()
    cci_ma_short2 = cci2.rolling(max(1, int(volatility_n / 4)), min_periods=1).mean()
    df["dzcci_lower_signal"] = (cci_lower2 - df["Close"]).rolling(volatility_n, min_periods=1).mean() / ((cci_lower2 - df["Close"]).rolling(volatility_n, min_periods=1).std() + EPS)
    df["dzcci_lower_signal_v2"] = _scale_01(cci_lower2 - cci_ma_short2, volatility_n)
    df["dzcci_upper_signal"] = _scale_01(df["Close"] - cci_upper2, volatility_n)
    df["dzcci_upper_signal_v2"] = _scale_01(cci_ma_short2 - cci_upper2, volatility_n)

    fb_tmp1 = df["High"] - df["Low"]
    fb_tmp2 = (df["High"] - df["Close"].shift(1)).abs()
    fb_tmp3 = (df["Low"] - df["Close"].shift(1)).abs()
    fb_tr = pd.concat([fb_tmp1, fb_tmp2, fb_tmp3], axis=1).max(axis=1)
    fb_atr = fb_tr.rolling(volatility_n, min_periods=1).mean()
    fb_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    df["fb_lower_signal"] = _scale_01(fb_middle - 1.618 * fb_atr - df["Close"], volatility_n)
    df["fb_lower_signal_v2"] = _scale_01(fb_middle - 2.618 * fb_atr - df["Close"], volatility_n)
    df["fb_lower_signal_v3"] = _scale_01(fb_middle - 4.236 * fb_atr - df["Close"], volatility_n)
    df["fb_upper_signal"] = _scale_01(df["Close"] - fb_middle - 1.618 * fb_atr, volatility_n)
    df["fb_upper_signal_v2"] = _scale_01(df["Close"] - fb_middle - 2.618 * fb_atr, volatility_n)
    df["fb_upper_signal_v3"] = _scale_01(df["Close"] - fb_middle - 4.236 * fb_atr, volatility_n)

    vix = df["Close"] / (df["Close"].shift(volatility_n) + EPS) - 1.0
    vix_median = vix.rolling(volatility_n, min_periods=1).mean()
    vix_std = vix.rolling(volatility_n, min_periods=1).std()
    vix_score = (vix - vix_median).abs() / (vix_std + EPS)
    vix_max = vix_score.rolling(volatility_n, min_periods=1).mean().shift(1)
    vix_upper = vix_median + vix_max * vix_std
    vix_lower = vix_median - vix_max * vix_std
    vix_bw = (vix_upper - vix_lower) * np.sign(vix_median.diff(volatility_n))
    direction = np.sign(vix_median.diff(volatility_n))
    short_dir = np.sign(vix_median.diff(1))
    prev_short_dir = np.sign(vix_median.diff(1).shift(1))
    vix_bw = vix_bw.where(direction == short_dir, 0.0)
    vix_bw = vix_bw.where(direction == prev_short_dir, 0.0)
    df["vix_bw"] = vix_bw

    # --- Indicator features used by signal.py ---

    df["bb_width"] = (df["ub"] - df["lb"]) / df["mb"].replace(0, np.nan)
    df["bb_width_q20"] = df["bb_width"].rolling(100).quantile(0.2)
    df["bb_width_sma_medium"] = df["bb_width"].rolling(config.medium_lookback).mean()
    df["atr_sma_medium"] = df["atr_medium"].rolling(config.medium_lookback).mean()

    ema20 = ta.ema(df["Close"], length=config.medium_lookback)
    kc_mid = ema20 if ema20 is not None else pd.Series(np.nan, index=df.index)
    atr_local = df["atr_medium"]

    df["kc_mid"] = kc_mid
    df["kc_upper"] = kc_mid + 2 * atr_local
    df["kc_lower"] = kc_mid - 2 * atr_local

    # Choppiness 14
    diff_chop = (df["High"].rolling(14).max() - df["Low"].rolling(14).min()).replace(0, np.nan)
    atr_chop_series = ta.atr(df["High"], df["Low"], df["Close"], length=1)
    if atr_chop_series is not None and not atr_chop_series.empty:
        atr_chop_sum = atr_chop_series.rolling(14).sum().replace(0, np.nan)
        df["chop14"] = 100.0 * (np.log10(atr_chop_sum) - np.log10(diff_chop)) / np.log10(14)
    else:
        df["chop14"] = np.nan

    # Hurst proxy
    lagged_diff = df["Close"].diff().abs().rolling(config.medium_lookback).sum()
    displacement = df["Close"].diff(config.medium_lookback).abs()
    df["hurst_proxy"] = displacement / lagged_diff.replace(0, np.nan)

    df["body_atr_ratio"] = (df["Close"] - df["Open"]) / df["atr_medium"].replace(0, np.nan)

    keltner_20_2 = ta.kc(df["High"], df["Low"], df["Close"], length=config.medium_lookback, scalar=2.0)
    if keltner_20_2 is not None and not keltner_20_2.empty:
        upper_cols = [col for col in keltner_20_2.columns if col.startswith("KCU")]
        lower_cols = [col for col in keltner_20_2.columns if col.startswith("KCL")]
        df["keltner_upper_medium_2"] = keltner_20_2[upper_cols[0]] if upper_cols else np.nan
        df["keltner_lower_medium_2"] = keltner_20_2[lower_cols[0]] if lower_cols else np.nan
    else:
        df["keltner_upper_medium_2"] = np.nan
        df["keltner_lower_medium_2"] = np.nan

    df["donchian_high_short_shift1"] = df["High"].rolling(config.short_lookback).max().shift(1)
    df["donchian_low_short_shift1"] = df["Low"].rolling(config.short_lookback).min().shift(1)
    df["donchian_high_30_shift1"] = df["High"].rolling(30).max().shift(1)
    df["donchian_low_30_shift1"] = df["Low"].rolling(30).min().shift(1)
    df["close_donchian_high_medium_shift1"] = df["Close"].rolling(config.medium_lookback).max().shift(1)
    df["close_donchian_low_medium_shift1"] = df["Close"].rolling(config.medium_lookback).min().shift(1)

    return df
