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


def _rolling_regression_forecast(values: np.ndarray) -> float:
    if len(values) < 2 or not np.isfinite(values).all():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, intercept = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
    return slope * len(values) + intercept


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    momentum_n = config.momentum_lookback

    df["volume_avg"] = df["Volume"].rolling(momentum_n).mean()
    df["volume_sma20"] = df["Volume"].rolling(20).mean()
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


    force = df["Volume"] * (df["Close"] - df["Close"].shift(1))
    force_ma = force.rolling(momentum_n, min_periods=1).mean()
    df["force_ratio"] = force / (force_ma + EPS)


    quote_volume_mean = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean()
    df["quote_volume_mean"] = quote_volume_mean
    df["quote_volume_ratio"] = quote_volume_proxy / (quote_volume_mean + EPS)



    mtm = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    mtm_mean = mtm.rolling(window=momentum_n, min_periods=1).mean()

    c1 = df["High"] - df["Low"]
    c2 = (df["High"] - df["Close"].shift(1)).abs()
    c3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.Series(np.max(np.array([c1, c2, c3]), axis=0), index=df.index)
    atr = tr.rolling(window=momentum_n, min_periods=1).mean()
    avg_price = df["Close"].rolling(window=momentum_n, min_periods=1).mean()
    wd_atr = atr / (avg_price + EPS)

    mtm_l = df["Low"] / (df["Low"].shift(momentum_n) + EPS) - 1.0
    mtm_h = df["High"] / (df["High"].shift(momentum_n) + EPS) - 1.0
    mtm_c = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_c1 = mtm_h - mtm_l
    mtm_c2 = (mtm_h - mtm_c.shift(1)).abs()
    mtm_c3 = (mtm_l - mtm_c.shift(1)).abs()
    mtm_tr = pd.Series(np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0), index=df.index)
    mtm_atr = mtm_tr.rolling(window=momentum_n, min_periods=1).mean()

    mtm_l_mean = mtm_l.rolling(window=momentum_n, min_periods=1).mean()
    mtm_h_mean = mtm_h.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c_mean = mtm_c.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c1 = mtm_h_mean - mtm_l_mean
    mtm_c2 = (mtm_h_mean - mtm_c_mean.shift(1)).abs()
    mtm_c3 = (mtm_l_mean - mtm_c_mean.shift(1)).abs()
    mtm_tr_mean = pd.Series(np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0), index=df.index)
    mtm_atr_mean = mtm_tr_mean.rolling(window=momentum_n, min_periods=1).mean()

    v1 = mtm_mean * wd_atr * mtm_atr * mtm_atr_mean
    df["v1"] = v1

    median = v1.rolling(window=momentum_n, min_periods=1).mean()
    std = v1.rolling(momentum_n, min_periods=1).std(ddof=0)
    z_score = (v1 - median).abs() / (std + EPS)
    m1 = z_score.rolling(window=momentum_n, min_periods=1).max().shift(1)
    upper = median + std * m1
    lower = median - std * m1
    df["v1_up"] = upper - v1
    df["v1_down"] = lower - v1



    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    mf = typical_price * df["Volume"]
    mf_pos = pd.Series(np.where(typical_price >= typical_price.shift(1), mf, 0.0), index=df.index).rolling(momentum_n, min_periods=1).sum()
    mf_neg = pd.Series(np.where(typical_price <= typical_price.shift(1), mf, 0.0), index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["mfi_standard"] = 100.0 - 100.0 / (1.0 + mf_pos / (mf_neg + EPS))



    quote_volume_proxy = df["Close"] * df["Volume"]
    chla_div = (df["High"] - df["Low"]).replace(0, np.nan)
    chla = ((2.0 * df["Close"] - df["High"] - df["Low"]) / chla_div) * quote_volume_proxy
    df["chla_fancy"] = chla.rolling(momentum_n, min_periods=1).sum()

    ret_sign = np.sign(df["Close"].pct_change())
    df["net_vol_fancy"] = (ret_sign * quote_volume_proxy).rolling(momentum_n, min_periods=1).sum()



    emap = df["Volume"].ewm(span=2 * momentum_n, adjust=False).mean()
    df["srocvol"] = (emap - emap.shift(momentum_n)) / (emap.shift(momentum_n) + EPS)
    df["roc_vol"] = df["Volume"] / (df["Volume"].shift(momentum_n) + EPS) - 1.0

    quote_volume_proxy = df["Close"] * df["Volume"]
    df["volume_reg"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).apply(lambda x: x.iloc[-1] if len(x) else np.nan, raw=False)
    df["volume_tsf"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean().shift(-1)

    volume_ema_1 = df["Volume"].ewm(span=2 * momentum_n, adjust=False).mean()
    volume_ema_2 = df["Volume"].ewm(span=4 * momentum_n, adjust=False).mean()
    macdv = volume_ema_1 - volume_ema_2
    macdv_signal = macdv.rolling(momentum_n, min_periods=1).mean()
    df["macdvol"] = macdv / (macdv_signal + EPS) - 1.0


    df = df.copy()

    amov = df["Volume"] * (df["Open"] + df["Close"]) / 2.0
    amv1 = amov.rolling(momentum_n, min_periods=1).sum() / (df["Volume"].rolling(momentum_n, min_periods=1).sum() + EPS)
    df["amv"] = (amv1 - amv1.rolling(momentum_n, min_periods=1).min()) / (
        amv1.rolling(momentum_n, min_periods=1).max() - amv1.rolling(momentum_n, min_periods=1).min() + EPS
    )

    typ_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    mf = typ_price * df["Volume"]
    mf_pos = pd.Series(np.where(typ_price >= typ_price.shift(1), mf, 0.0), index=df.index).rolling(momentum_n, min_periods=1).sum()
    mf_neg = pd.Series(np.where(typ_price <= typ_price.shift(1), mf, 0.0), index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["mfi"] = 100.0 - 100.0 / (1.0 + mf_pos / (mf_neg + EPS))

    clv = (2.0 * df["Close"] - df["Low"] - df["High"]) / (df["High"] - df["Low"] + EPS)
    obv_va = clv * df["Volume"]
    obv_sum = obv_va.rolling(momentum_n, min_periods=1).sum()
    df["obv"] = obv_sum / (obv_sum.rolling(momentum_n, min_periods=1).mean() + EPS)

    pvt = df["Close"].pct_change() * df["Volume"]
    pvt_score = (pvt - pvt.rolling(momentum_n, min_periods=1).mean()) / (pvt.rolling(momentum_n, min_periods=1).std() + EPS)
    pvt_sum = pvt_score.rolling(momentum_n, min_periods=1).sum()
    df["pvt_v2"] = pvt / (pvt_sum.rolling(momentum_n, min_periods=1).mean() + EPS) - 1.0
    df["pvt_v3"] = pvt_sum.rolling(momentum_n, min_periods=1).mean() - pvt_sum.rolling(2 * momentum_n, min_periods=1).mean()
    df["pvt_v4"] = pvt / (pvt_sum.rolling(momentum_n, min_periods=1).mean() + EPS) - 1.0

    av = np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0)
    bv = np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0)
    cv = np.where(df["Close"] == df["Close"].shift(1), df["Volume"], 0.0)
    avs = pd.Series(av, index=df.index).rolling(momentum_n, min_periods=1).sum()
    bvs = pd.Series(bv, index=df.index).rolling(momentum_n, min_periods=1).sum()
    cvs = pd.Series(cv, index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["vr"] = (avs + 0.5 * cvs) / (bvs + 0.5 * cvs + EPS)

    wv = df["Volume"] * (df["Close"] - 0.5 * df["High"] - 0.5 * df["Low"])
    vao = wv + wv.shift(1)
    vao_ma1 = vao.rolling(momentum_n, min_periods=1).mean()
    vao_ma2 = vao.rolling(3 * momentum_n, min_periods=1).mean()
    df["vao"] = vao_ma1 - vao_ma2
    df["vao_v2"] = vao / (df["vao"] + EPS) - 1.0

    quote_volume_proxy = df["Close"] * df["Volume"]
    short_window = max(1, momentum_n // 4)
    df["volume_bias"] = quote_volume_proxy.rolling(short_window, min_periods=1).mean() / (
        quote_volume_proxy.rolling(momentum_n, min_periods=1).mean() + EPS
    ) - 1.0

    df["volume"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).sum()
    close_delta = df["Close"].pct_change()
    direction = np.where(close_delta > 0, 1.0, np.where(close_delta < 0, -1.0, 0.0))
    volume_change = quote_volume_proxy / (quote_volume_proxy.shift(1) + EPS) * direction
    df["volumechg"] = volume_change.rolling(momentum_n, min_periods=1).max()

    df["maamt"] = (df["Volume"] - df["Volume"].rolling(momentum_n, min_periods=1).mean()) / (
        df["Volume"].rolling(momentum_n, min_periods=1).mean() + EPS
    )

    df["upnum_fancy"] = pd.Series((df["Close"].pct_change() > 0).astype(float), index=df.index).rolling(momentum_n, min_periods=1).sum()

    trade_num_proxy = df["Volume"]
    quote_volume_series = df.get("quote_volume", quote_volume_proxy)
    taker_buy_quote_asset_volume = df.get(
        "taker_buy_quote_asset_volume",
        pd.Series(np.where(df["Close"] > df["Close"].shift(1), quote_volume_proxy, 0.0), index=df.index),
    )
    taker_buy_base_asset_volume = df.get(
        "taker_buy_base_asset_volume",
        pd.Series(np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0), index=df.index),
    )

    df["trade_num"] = trade_num_proxy.rolling(momentum_n, min_periods=1).sum()
    taker_by_ratio = taker_buy_quote_asset_volume.rolling(momentum_n, min_periods=1).sum() / (
        quote_volume_series.rolling(momentum_n, min_periods=1).sum() + EPS
    )
    df["taker_by_ratio"] = taker_by_ratio
    df["buy_vol_ratio_fancy"] = taker_by_ratio

    df["taker_by_ratio_per_trade"] = taker_by_ratio / (
        trade_num_proxy.rolling(momentum_n, min_periods=1).mean() + EPS
    )
    df["vol_per_trade_fancy"] = quote_volume_series.rolling(momentum_n, min_periods=1).sum() / (
        trade_num_proxy.rolling(momentum_n, min_periods=1).sum() + EPS
    )
    vwap = quote_volume_series.rolling(momentum_n, min_periods=1).sum() / (
        df["Volume"].rolling(momentum_n, min_periods=1).sum() + EPS
    )
    buy_vwap = taker_buy_quote_asset_volume.rolling(momentum_n, min_periods=1).sum() / (
        taker_buy_base_asset_volume.rolling(momentum_n, min_periods=1).sum() + EPS
    )
    df["buy_vwap_div_vwap_fancy"] = buy_vwap / (vwap + EPS)

    mtm_base = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_mean = mtm_base.ewm(span=momentum_n, adjust=False).mean()
    vma = quote_volume_series.rolling(momentum_n, min_periods=1).mean()
    taker_buy_ma = taker_buy_quote_asset_volume / (vma + EPS) * 100.0
    taker_buy_mean = taker_buy_ma.rolling(momentum_n, min_periods=1).mean()
    df["mtm_tb"] = mtm_mean * taker_buy_mean

    ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    bias = (df["Close"] - ma) / (ma + EPS) * 100.0
    bias_dif = bias - bias.shift(3 * momentum_n)
    df["dbcd_taker"] = bias_dif.rolling(3 * momentum_n + 2, min_periods=1).mean() * taker_by_ratio

    ma_bull = df["Close"].rolling(window=momentum_n, min_periods=1).mean()
    mtm_bull = (df["Close"] / (ma_bull.shift(momentum_n) + EPS) - 1.0) * 100.0
    mtm_bull_mean = mtm_bull.rolling(window=momentum_n, min_periods=1).mean()
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - df["Close"].shift(1)).abs()
    tr3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr_bull = pd.DataFrame({"tr1": tr1, "tr2": tr2, "tr3": tr3}).max(axis=1)
    atr_abs_bull = tr_bull.rolling(window=momentum_n, min_periods=1).mean()
    atr_bull = atr_abs_bull / (ma_bull + EPS) * 100.0
    taker_buy_ma_bull = taker_buy_quote_asset_volume / (vma + EPS) * 100.0
    taker_buy_mean_bull = taker_buy_ma_bull.rolling(window=momentum_n, min_periods=1).mean()
    df["mtm_bull"] = mtm_bull_mean * atr_bull * taker_buy_mean_bull

    taker_sell_quote_asset_volume = quote_volume_series - taker_buy_quote_asset_volume
    taker_sell_ma = taker_sell_quote_asset_volume / (vma + EPS) * 100.0
    taker_sell_mean = taker_sell_ma.rolling(window=momentum_n, min_periods=1).mean()
    df["mtm_bear"] = mtm_bull_mean * atr_bull * taker_sell_mean

    mtm = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_mean = mtm.rolling(window=momentum_n, min_periods=1).mean()
    c1 = df["High"] - df["Low"]
    c2 = abs(df["High"] - df["Close"].shift(1))
    c3 = abs(df["Low"] - df["Close"].shift(1))
    tr = np.max(np.array([c1, c2, c3]), axis=0)
    atr = pd.Series(tr, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    avg_price = df["Close"].rolling(window=momentum_n, min_periods=1).mean()
    wd_atr = atr / (avg_price + EPS)
    mtm_l = df["Low"] / (df["Low"].shift(momentum_n) + EPS) - 1.0
    mtm_h = df["High"] / (df["High"].shift(momentum_n) + EPS) - 1.0
    mtm_c = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_c1 = mtm_h - mtm_l
    mtm_c2 = abs(mtm_h - mtm_c.shift(1))
    mtm_c3 = abs(mtm_l - mtm_c.shift(1))
    mtm_tr = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)
    mtm_atr = pd.Series(mtm_tr, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    mtm_l_mean = mtm_l.rolling(window=momentum_n, min_periods=1).mean()
    mtm_h_mean = mtm_h.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c_mean = mtm_c.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c1 = mtm_h_mean - mtm_l_mean
    mtm_c2 = abs(mtm_h_mean - mtm_c_mean.shift(1))
    mtm_c3 = abs(mtm_l_mean - mtm_c_mean.shift(1))
    mtm_tr_mean = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)
    mtm_atr_mean = pd.Series(mtm_tr_mean, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    v1 = mtm_mean * wd_atr * mtm_atr * mtm_atr_mean
    median = v1.rolling(window=momentum_n, min_periods=1).mean()
    std = v1.rolling(momentum_n, min_periods=1).std(ddof=0)
    z_score = (v1 - median).abs() / (std + EPS)
    m1 = z_score.rolling(window=momentum_n, min_periods=1).max().shift(1)
    upper = median + std * m1
    lower = median - std * m1
    df["v1dn"] = lower - v1

    emap_1 = df["Volume"].ewm(span=momentum_n, adjust=False, min_periods=1).mean()
    emap_2 = df["Volume"].ewm(span=2 * momentum_n, adjust=False, min_periods=1).mean()
    df["Pvo"] = (emap_1 - emap_2) / (emap_2 + EPS)

    av = np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0)
    bv = np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0)
    cv = np.where(df["Close"] == df["Close"].shift(1), df["Volume"], 0.0)
    avs = pd.Series(av, index=df.index).rolling(momentum_n, min_periods=1).sum()
    bvs = pd.Series(bv, index=df.index).rolling(momentum_n, min_periods=1).sum()
    cvs = pd.Series(cv, index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["Vramt"] = (avs + 0.5 * cvs) / (bvs + 0.5 * cvs + EPS)

    mtm_v1 = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_v1_mean = mtm_v1.rolling(window=momentum_n, min_periods=1).mean()
    c1 = df["High"] - df["Low"]
    c2 = abs(df["High"] - df["Close"].shift(1))
    c3 = abs(df["Low"] - df["Close"].shift(1))
    tr_v1 = np.max(np.array([c1, c2, c3]), axis=0)
    atr_v1 = pd.Series(tr_v1, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    avg_price_v1 = df["Close"].rolling(window=momentum_n, min_periods=1).mean()
    wd_atr_v1 = atr_v1 / (avg_price_v1 + EPS)
    mtm_l_v1 = df["Low"] / (df["Low"].shift(momentum_n) + EPS) - 1.0
    mtm_h_v1 = df["High"] / (df["High"].shift(momentum_n) + EPS) - 1.0
    mtm_c_v1 = df["Close"] / (df["Close"].shift(momentum_n) + EPS) - 1.0
    mtm_c1_v1 = mtm_h_v1 - mtm_l_v1
    mtm_c2_v1 = abs(mtm_h_v1 - mtm_c_v1.shift(1))
    mtm_c3_v1 = abs(mtm_l_v1 - mtm_c_v1.shift(1))
    mtm_tr_v1 = np.max(np.array([mtm_c1_v1, mtm_c2_v1, mtm_c3_v1]), axis=0)
    mtm_atr_v1 = pd.Series(mtm_tr_v1, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    mtm_l_mean_v1 = mtm_l_v1.rolling(window=momentum_n, min_periods=1).mean()
    mtm_h_mean_v1 = mtm_h_v1.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c_mean_v1 = mtm_c_v1.rolling(window=momentum_n, min_periods=1).mean()
    mtm_c1_mean_v1 = mtm_h_mean_v1 - mtm_l_mean_v1
    mtm_c2_mean_v1 = abs(mtm_h_mean_v1 - mtm_c_mean_v1.shift(1))
    mtm_c3_mean_v1 = abs(mtm_l_mean_v1 - mtm_c_mean_v1.shift(1))
    mtm_tr_mean_v1 = np.max(np.array([mtm_c1_mean_v1, mtm_c2_mean_v1, mtm_c3_mean_v1]), axis=0)
    mtm_atr_mean_v1 = pd.Series(mtm_tr_mean_v1, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    v1_v2 = mtm_v1_mean * wd_atr_v1 * mtm_atr_v1 * mtm_atr_mean_v1
    median_v1 = v1_v2.rolling(window=momentum_n, min_periods=1).mean()
    std_v1 = v1_v2.rolling(momentum_n, min_periods=1).std(ddof=0)
    z_score_v1 = abs(v1_v2 - median_v1) / (std_v1 + EPS)
    m1_v1 = pd.Series(z_score_v1, index=df.index).rolling(window=momentum_n, min_periods=1).mean()
    upper_v1 = median_v1 + std_v1 * m1_v1
    lower_v1 = median_v1 - std_v1 * m1_v1
    df["v1_v2"] = v1_v2
    df["v1up_v2"] = upper_v1 - v1_v2
    df["v1dn_v2"] = lower_v1 - v1_v2

    df["v1"] = v1
    df["v1up"] = upper - v1

    df["ko"] = (ko - ko.rolling(momentum_n, min_periods=1).min()) / (ko.rolling(momentum_n, min_periods=1).max() - ko.rolling(momentum_n, min_periods=1).min() + EPS)

    df["Amv"] = df["amv"]
    df["Volume_Bias"] = df["volume_bias"]
    df["QuoteVolumeMean"] = df["quote_volume_mean"]
    df["QuoteVolumeRatio"] = df["quote_volume_ratio"]
    df["VolumeReg"] = df["volume_reg"]
    df["VolumeTSF"] = df["volume_tsf"]
    df["TradeNum"] = df["trade_num"]
    df["BuyVolRatio_fancy"] = df["buy_vol_ratio_fancy"]
    df["VolPerTrade_fancy"] = df["vol_per_trade_fancy"]
    df["BuyVwapDivVwap_fancy"] = df["buy_vwap_div_vwap_fancy"]
    df["TakerByRatio"] = df["taker_by_ratio"]
    df["TakerByRatioPerTrade"] = df["taker_by_ratio_per_trade"]
    df["V1"] = df["v1"]
    df["V1Up"] = df["v1up"]
    df["V1Dn"] = df["v1dn"]
    df["V1_v2"] = df["v1_v2"]
    df["V1Up_v2"] = df["v1up_v2"]
    df["V1Dn_v2"] = df["v1dn_v2"]

    df["Pvt"] = df["pvt"]
    df["Pvt_v2"] = df["pvt_v2"]
    df["Pvt_v3"] = df["pvt_v3"]
    df["Pvt_v4"] = df["pvt_v4"]
    df["Pvi"] = df["pvi"]
    df["Nvi"] = df["nvi"]
    df["Wad"] = df["wad"]
    df["Tmf"] = df["tmf"]
    df["Emv"] = df["emv"]
    df["Clv"] = df["clv_ma"]
    df["Adosc"] = df["adosc"]
    df["Fi"] = df["fi"]
    df["FiRsi"] = df["fi_rsi"]
    df["Vra"] = df["vra"]
    df["Ke"] = df["ke"]
    df["Ko"] = df["ko"]
    df["Mfi"] = df["mfi"]
    df["Vr"] = df["vr"]
    df["Vao"] = df["vao"]
    df["Vao_v2"] = df["vao_v2"]
    df["Volumechg"] = df["volumechg"]
    df["Wvad"] = df["wvad"]
    df["QuanlityPriceCorr"] = df["price_volume_corr"]
    df["Volume"] = df["volume"]
    df["Force"] = df["force_index"]
    df["Cmf"] = df["cmf"]
    df["Obv"] = df["obv"]
    df["Pvo"] = df["pvo"]
    df["VRA"] = df["vra"]
    df["Chla_fancy"] = df["chla_fancy"]
    df["NetVol_fancy"] = df["net_vol_fancy"]

    # --- Indicator features used by signal.py ---

    mfi_val = ta.mfi(df["High"], df["Low"], df["Close"], df["Volume"], length=14)
    df["mfi14"] = mfi_val if mfi_val is not None else np.nan

    vpt_increment = df["Volume"] * df["Close"].pct_change().fillna(0.0)
    df["vpt"] = vpt_increment.cumsum()

    df["volume_ma_20"] = df["Volume"].rolling(20).mean()
    bar_delta = df["Close"] - df["Open"]
    fallback_delta = df["Close"].diff()
    direction = bar_delta.where(bar_delta != 0, fallback_delta)
    signed_direction = pd.Series(np.sign(direction).fillna(0.0), index=df.index)
    df["signed_volume"] = signed_direction * df["Volume"]
    trade_date = pd.Series(df.index.normalize(), index=df.index)
    cum_vol = df.groupby(trade_date)["Volume"].cumsum().replace(0, np.nan)
    df["session_flow_imbalance"] = df["signed_volume"].groupby(trade_date).cumsum() / cum_vol

    return df
