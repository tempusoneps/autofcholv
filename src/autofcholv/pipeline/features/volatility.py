import os

import numpy as np
import pandas as pd


EPS = 1e-8


def _scale_01(series: pd.Series, window: int) -> pd.Series:
    low = series.rolling(window, min_periods=1).min()
    high = series.rolling(window, min_periods=1).max()
    return (series - low) / (high - low + EPS)


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate volatility and channel features adapted from quant-ohlcv-feature.
    Feature definitions follow volatility.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    volatility_n = int(os.getenv("VOLATILITY_LOOKBACK", 24))

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


    prev_close_for_atr = df["Close"].shift(1)
    atr_tr = pd.concat(
        [
            (df["High"] - df["Low"]).abs(),
            (df["High"] - prev_close_for_atr).abs(),
            (prev_close_for_atr - df["Low"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_pct = atr_tr.rolling(volatility_n, min_periods=1).mean() / (df["Close"] + EPS)
    df["atr_pct"] = atr_pct

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
    df["atr_upper"] = (df["Low"].rolling(max(1, volatility_n // 2), min_periods=1).min() + 3.0 * atr) / (df["Close"].rolling(volatility_n, min_periods=1).mean() + EPS)
    df["atr_lower"] = (df["Close"].rolling(volatility_n, min_periods=1).mean() - 0.2 * volatility_n * atr) / (df["Close"].rolling(volatility_n, min_periods=1).mean() + EPS)

    fb_middle = df["Close"].rolling(volatility_n, min_periods=1).mean()
    fb_upper = fb_middle + 1.618 * atr
    fb_lower = fb_middle - 1.618 * atr
    df["fb_upper_signal"] = (df["Close"] - fb_middle - 1.618 * atr) / (fb_upper - fb_lower + EPS)

    pac_upper = df["High"].ewm(span=volatility_n, adjust=False).mean()
    pac_lower = df["Low"].ewm(span=volatility_n, adjust=False).mean()
    pac_width = pac_upper - pac_lower
    df["pac_width_signal"] = pac_width / (pac_width.rolling(volatility_n, min_periods=1).mean() + EPS) - 1.0


    return df
