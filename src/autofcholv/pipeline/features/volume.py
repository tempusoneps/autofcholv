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


def _rolling_regression_forecast(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(x, values, 1)
    return slope * len(values) + intercept


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    momentum_n = int(os.getenv("MOMENTUM_LOOKBACK", 24))

    df["volume_avg"] = df["Volume"].rolling(momentum_n).mean()
    df["volume_zscore"] = (df["Volume"] - df["volume_avg"]) / df["Volume"].rolling(momentum_n).std()


    df["roc_volume"] = df["Volume"] / (df["Volume"].shift(momentum_n) + EPS) - 1.0

    close_pct = df["Close"].pct_change()
    quote_volume_proxy = df["Close"] * df["Volume"]

    short_window = max(1, momentum_n // 4)
    df["quote_volume_sum"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).sum()
    df["volume_bias_short_long"] = (
        quote_volume_proxy.rolling(short_window, min_periods=1).mean()
        / (quote_volume_proxy.rolling(momentum_n, min_periods=1).mean() + EPS)
        - 1.0
    )

    pvt = close_pct * df["Volume"]
    pvt_ma = pvt.rolling(momentum_n, min_periods=1).mean()
    pvt_signal = pvt / (pvt_ma + EPS) - 1.0
    df["pvt"] = pvt
    df["pvt_signal"] = pvt_signal.rolling(momentum_n, min_periods=1).sum()

    up_volume = np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0)
    down_volume = np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0)
    rolling_volume = df["Volume"].rolling(momentum_n, min_periods=1).sum()
    df["volume_up_ratio"] = (
        pd.Series(up_volume, index=df.index).rolling(momentum_n, min_periods=1).sum()
        / (rolling_volume + EPS)
    )
    df["volume_down_ratio"] = (
        pd.Series(down_volume, index=df.index).rolling(momentum_n, min_periods=1).sum()
        / (rolling_volume + EPS)
    )

    positive_flow = np.where(close_pct > 0, df["Volume"] * df["Close"], 0.0)
    negative_flow = np.where(close_pct < 0, df["Volume"] * df["Close"], 0.0)
    positive_flow_sum = pd.Series(positive_flow, index=df.index).rolling(momentum_n, min_periods=1).sum()
    negative_flow_sum = pd.Series(negative_flow, index=df.index).rolling(momentum_n, min_periods=1).sum()
    money_ratio = positive_flow_sum / (negative_flow_sum + EPS)
    df["money_flow_index"] = 100.0 - (100.0 / (1.0 + money_ratio))

    positive_volume = df["Volume"] > df["Volume"].shift(1)
    negative_volume = df["Volume"] < df["Volume"].shift(1)
    df["pvi"] = (1.0 + close_pct.where(positive_volume, 0.0)).cumprod()
    df["nvi"] = (1.0 + close_pct.where(negative_volume, 0.0)).cumprod()

    clv = (2.0 * df["Close"] - df["Low"] - df["High"]) / (df["High"] - df["Low"] + EPS)
    df["clv_ma"] = clv.rolling(momentum_n, min_periods=1).mean()

    prev_close = df["Close"].shift(1)
    true_high = pd.concat([df["High"], prev_close], axis=1).max(axis=1)
    true_low = pd.concat([df["Low"], prev_close], axis=1).min(axis=1)
    ad = np.where(
        df["Close"] > prev_close,
        df["Close"] - true_low,
        df["Close"] - true_high,
    )
    ad = np.where(df["Close"] == prev_close, 0.0, ad)
    wad = pd.Series(ad, index=df.index).cumsum()
    wad_ma = wad.rolling(momentum_n, min_periods=1).mean()
    df["wad"] = wad / (wad_ma + EPS)

    true_range = true_high - true_low
    tmf_flow = df["Volume"] * (2.0 * df["Close"] - true_high - true_low) / (true_range + EPS)
    df["tmf"] = (
        pd.Series(tmf_flow, index=df.index).ewm(span=momentum_n, adjust=False).mean()
        / (df["Volume"].ewm(span=momentum_n, adjust=False).mean() + EPS)
    )

    df["quote_volume_reg"] = quote_volume_proxy.rolling(
        momentum_n,
        min_periods=momentum_n,
    ).apply(_rolling_regression_last, raw=True)
    df["quote_volume_tsf"] = quote_volume_proxy.rolling(
        momentum_n,
        min_periods=momentum_n,
    ).apply(_rolling_regression_forecast, raw=True)
    df["price_volume_corr"] = df["Close"].rolling(momentum_n, min_periods=momentum_n).corr(
        quote_volume_proxy
    )

    clv_weight = (2.0 * df["Close"] - df["Low"] - df["High"]) / (df["High"] - df["Low"] + EPS)
    va = clv_weight * df["Volume"]
    obv_clv = va.rolling(momentum_n, min_periods=1).sum()
    df["obv_clv"] = obv_clv / (obv_clv.rolling(momentum_n, min_periods=1).mean() + EPS)
    df["cmf"] = va.rolling(momentum_n, min_periods=1).sum() / (
        df["Volume"].rolling(momentum_n, min_periods=1).sum() + EPS
    )

    midpoint_move = (df["High"] + df["Low"]) / 2.0 - (df["High"].shift(1) + df["Low"].shift(1)) / 2.0
    box_ratio = (
        df["Volume"]
        / (df["Volume"].rolling(momentum_n, min_periods=1).mean() + EPS)
        / (df["High"] - df["Low"] + EPS)
    )
    df["emv"] = midpoint_move / (box_ratio + EPS)

    force = df["Volume"] * df["Close"].diff()
    force_zscore = (force - force.rolling(momentum_n, min_periods=1).mean()) / (
        force.rolling(momentum_n, min_periods=2).std() + EPS
    )
    df["force_index"] = force_zscore.ewm(span=momentum_n, adjust=False, min_periods=1).mean()

    volume_ema_fast = df["Volume"].ewm(span=momentum_n, adjust=False, min_periods=1).mean()
    volume_ema_slow = df["Volume"].ewm(span=momentum_n * 2, adjust=False, min_periods=1).mean()
    df["pvo"] = (volume_ema_fast - volume_ema_slow) / (volume_ema_slow + EPS)

    direction = np.where(df["Close"].pct_change() >= 0, 1.0, -1.0)
    volume_change = quote_volume_proxy / (quote_volume_proxy.shift(1) + EPS) * direction
    df["directional_volume_change"] = volume_change.rolling(momentum_n, min_periods=1).max()

    amount_up = pd.Series(
        np.where(df["Close"] > df["Close"].shift(1), quote_volume_proxy, 0.0),
        index=df.index,
    )
    amount_down = pd.Series(
        np.where(df["Close"] < df["Close"].shift(1), quote_volume_proxy, 0.0),
        index=df.index,
    )
    amount_flat = pd.Series(
        np.where(df["Close"] == df["Close"].shift(1), quote_volume_proxy, 0.0),
        index=df.index,
    )
    amount_up_sum = amount_up.rolling(momentum_n, min_periods=1).sum()
    amount_down_sum = amount_down.rolling(momentum_n, min_periods=1).sum()
    amount_flat_sum = amount_flat.rolling(momentum_n, min_periods=1).sum()
    df["volume_ratio_amount"] = (amount_up_sum + amount_flat_sum / 2.0) / (
        amount_down_sum + amount_flat_sum / 2.0 + EPS
    )

    clv_accum = (2.0 * df["Close"] - df["Low"] - df["High"]) / (df["High"] - df["Low"] + EPS)
    ad_line = (clv_accum * df["Volume"]).cumsum()
    adosc = ad_line.ewm(span=momentum_n, adjust=False).mean() - ad_line.ewm(
        span=momentum_n * 2,
        adjust=False,
    ).mean()
    df["adosc"] = (adosc - adosc.rolling(momentum_n, min_periods=1).min()) / (
        adosc.rolling(momentum_n, min_periods=1).max()
        - adosc.rolling(momentum_n, min_periods=1).min()
        + EPS
    )

    vad = (df["Close"] - df["Open"]) / (df["High"] - df["Low"] + EPS) * df["Volume"]
    wvad = vad.rolling(momentum_n, min_periods=1).sum()
    df["wvad"] = (wvad - wvad.rolling(momentum_n, min_periods=1).min()) / (
        wvad.rolling(momentum_n, min_periods=1).max()
        - wvad.rolling(momentum_n, min_periods=1).min()
        + EPS
    )

    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    signed_volume = pd.Series(
        np.where(typical_price > typical_price.shift(1), df["Volume"], -df["Volume"]),
        index=df.index,
    )
    ko = signed_volume.ewm(span=momentum_n, adjust=False).mean() - signed_volume.ewm(
        span=max(1, int(momentum_n * 1.618)),
        adjust=False,
    ).mean()
    df["klinger_oscillator"] = (ko - ko.rolling(momentum_n, min_periods=1).min()) / (
        ko.rolling(momentum_n, min_periods=1).max() - ko.rolling(momentum_n, min_periods=1).min() + EPS
    )

    vra_volatility = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0) / (
        df["Close"].rolling(momentum_n, min_periods=1).mean() + EPS
    ) * 100.0
    vra_rc = 100.0 * (
        (df["High"] - df["High"].shift(momentum_n)) / (df["Close"].shift(momentum_n) + EPS)
        + (df["Close"] - df["Close"].shift(2 * momentum_n)) / (df["Low"].shift(2 * momentum_n) + EPS)
    )
    df["vra"] = vra_rc.rolling(momentum_n, min_periods=1).mean() * vra_volatility

    volume_standard = df["Volume"] / (df["Volume"].rolling(momentum_n, min_periods=1).mean() + EPS)
    price_change_n = df["Close"].pct_change(momentum_n)
    df["ke"] = np.sign(price_change_n) * volume_standard * price_change_n.pow(2)


    volume_ma = df["Volume"].rolling(momentum_n, min_periods=1).mean()
    df["volume_ma_bias"] = df["Volume"] / (volume_ma + EPS) - 1.0

    amv_flow = df["Volume"] * (df["Open"] + df["Close"]) / 2.0
    amv = amv_flow.rolling(momentum_n, min_periods=1).sum() / (
        df["Volume"].rolling(momentum_n, min_periods=1).sum() + EPS
    )
    df["amv_signal"] = (amv - amv.rolling(momentum_n, min_periods=1).min()) / (
        amv.rolling(momentum_n, min_periods=1).max() - amv.rolling(momentum_n, min_periods=1).min() + EPS
    )

    vr_up = pd.Series(np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    vr_down = pd.Series(np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    vr_flat = pd.Series(np.where(df["Close"] == df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    df["volume_ratio"] = (
        vr_up.rolling(momentum_n, min_periods=1).sum()
        + 0.5 * vr_flat.rolling(momentum_n, min_periods=1).sum()
    ) / (
        vr_down.rolling(momentum_n, min_periods=1).sum()
        + 0.5 * vr_flat.rolling(momentum_n, min_periods=1).sum()
        + EPS
    )

    volume_ema_1 = df["Volume"].ewm(span=2 * momentum_n, adjust=False, min_periods=1).mean()
    volume_ema_2 = df["Volume"].ewm(span=4 * momentum_n, adjust=False, min_periods=1).mean()
    macd_volume = volume_ema_1 - volume_ema_2
    macd_volume_signal = macd_volume.rolling(momentum_n, min_periods=1).mean()
    df["macd_volume_ratio"] = macd_volume / (macd_volume_signal + EPS) - 1.0

    vao_weighted_volume = df["Volume"] * (df["Close"] - 0.5 * df["High"] - 0.5 * df["Low"])
    vao = vao_weighted_volume + vao_weighted_volume.shift(1)
    df["volume_analysis_oscillator"] = vao.rolling(momentum_n, min_periods=1).mean() - vao.rolling(
        3 * momentum_n,
        min_periods=1,
    ).mean()

    return df
