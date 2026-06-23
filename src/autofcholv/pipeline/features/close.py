import os

import numpy as np
import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate features based on Close column.
    Feature definitions follow close.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    fast_n     = int(os.getenv("FAST_TREND_LOOKBACK", 24))
    slow_n     = int(os.getenv("SLOW_TREND_LOOKBACK", 245))
    momentum_n = int(os.getenv("MOMENTUM_LOOKBACK", 24))

    df["ema_fast"] = ta.ema(df["Close"], length=fast_n)
    df["ema_slow"] = ta.ema(df["Close"], length=slow_n)

    df["rsi"] = ta.rsi(df["Close"], length=momentum_n)
    df["rsi_slope"] = df["rsi"].diff()

    tsi_result = ta.tsi(df["Close"])
    if tsi_result is not None and not tsi_result.empty:
        df["tsi"] = tsi_result.iloc[:, 0]

    df["roc_close"] = ta.roc(df["Close"], length=1)

    df["close_zscore"] = ta.zscore(df["Close"], length=momentum_n)

    change     = df["Close"].diff(1).abs()
    net_change = (df["Close"] - df["Close"].shift(momentum_n)).abs()
    volatility = change.rolling(momentum_n).sum()
    df["efficiency_ratio"] = net_change / volatility

    macd_result = ta.macd(df["Close"], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        df["macd"]        = macd_result.iloc[:, 0]
        df["macd_hist"]   = macd_result.iloc[:, 1]
        df["macd_signal"] = macd_result.iloc[:, 2]

    ppo_result = ta.ppo(df["Close"], fast=12, slow=26, signal=9)
    if ppo_result is not None and not ppo_result.empty:
        df["ppo"]        = ppo_result.iloc[:, 0]
        df["ppo_hist"]   = ppo_result.iloc[:, 1]
        df["ppo_signal"] = ppo_result.iloc[:, 2]

    df["ulcer_index"] = ta.ui(df["Close"], length=momentum_n)
    df["cmo"]         = ta.cmo(df["Close"], length=momentum_n)

    df["roc_skew"] = df["roc_close"].rolling(momentum_n).skew()
    df["roc_kurt"] = df["roc_close"].rolling(momentum_n).kurt()

    df['mb'] = df['Close'].rolling(fast_n).mean()
    df['std'] = df['Close'].rolling(fast_n).std()

    df['ub'] = df['mb'] + 2 * df['std']
    df['lb'] = df['mb'] - 2 * df['std']


    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    typical_ma = typical_price.rolling(momentum_n, min_periods=1).mean()
    typical_md = (typical_price - typical_ma).abs().rolling(momentum_n, min_periods=1).mean()
    df["cci"] = (typical_price - typical_ma) / (0.015 * typical_md + 1e-8)

    lowest_low = df["Low"].rolling(momentum_n, min_periods=1).min()
    highest_high = df["High"].rolling(momentum_n, min_periods=1).max()
    rsv = (df["Close"] - lowest_low) / (highest_high - lowest_low + 1e-8) * 100.0
    df["kdj_k"] = rsv.ewm(com=2, adjust=False).mean()
    df["kdj_d"] = df["kdj_k"].ewm(com=2, adjust=False).mean()
    df["kdj_j"] = 3.0 * df["kdj_k"] - 2.0 * df["kdj_d"]

    median_price = (df["High"] + df["Low"]) / 2.0
    median_low = median_price.rolling(momentum_n, min_periods=1).min()
    median_high = median_price.rolling(momentum_n, min_periods=1).max()
    fisher_value = 2.0 * ((median_price - median_low) / (median_high - median_low + 1e-8) - 0.5)
    fisher_value = pd.Series(fisher_value, index=df.index).ewm(alpha=1.0 / momentum_n, adjust=False).mean()
    fisher_value = fisher_value.clip(-0.999, 0.999)
    df["fisher"] = 0.5 * np.log((1.0 + fisher_value) / (1.0 - fisher_value))

    direction_n = (df["Close"] - df["Close"].shift(momentum_n)).abs()
    volatility_n = df["Close"].diff().abs().rolling(momentum_n, min_periods=1).sum()
    er = direction_n / (volatility_n + 1e-8)
    fast_sc = 2.0 / (2 + 1)
    slow_sc = 2.0 / (30 + 1)
    smoothing = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama = np.full(len(df), np.nan)
    close_values = df["Close"].to_numpy(dtype=float)
    smoothing_values = smoothing.fillna(0.0).to_numpy(dtype=float)
    if len(close_values):
        kama[0] = close_values[0]
        for i in range(1, len(close_values)):
            previous = kama[i - 1]
            kama[i] = previous + smoothing_values[i] * (close_values[i] - previous)
    df["kama"] = kama
    df["kama_bias"] = df["Close"] / (df["kama"] + 1e-8) - 1.0







    bias_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["bias"] = df["Close"] / (bias_ma + 1e-8) - 1.0
    df["rbias"] = (df["Close"] / (bias_ma + 1e-8)) / (
        df["Close"].shift(1) / (bias_ma.shift(1) + 1e-8)
    ) - 1.0

    mtm_base = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    df["mtm_mean"] = mtm_base.rolling(momentum_n, min_periods=1).mean()
    df["mtm_max_diff"] = mtm_base - mtm_base.rolling(momentum_n, min_periods=momentum_n).max().shift(1)

    sroc_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    sroc_ref = sroc_ema.shift(2 * momentum_n)
    df["sroc"] = (sroc_ema - sroc_ref) / (sroc_ref + 1e-8)

    ar_up = (df["High"] - df["Open"]).rolling(momentum_n, min_periods=1).sum()
    ar_down = (df["Open"] - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["ar"] = 100.0 * ar_up / (ar_down + 1e-8)

    prev_close_pressure = df["Close"].shift(1)
    br_up = (df["High"] - prev_close_pressure).rolling(momentum_n, min_periods=1).sum()
    br_down = (prev_close_pressure - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["br"] = 100.0 * br_up / (br_down + 1e-8)

    cr_typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
    cr_h = (df["High"] - cr_typical.shift(1)).clip(lower=0.0)
    cr_l = (cr_typical.shift(1) - df["Low"]).clip(lower=0.0)
    df["cr"] = 100.0 * cr_h.rolling(momentum_n, min_periods=1).sum() / (
        cr_l.rolling(momentum_n, min_periods=1).sum() + 1e-8
    )

    open_diff = df["Open"] - df["Open"].shift(1)
    dtm = np.where(
        df["Open"] > df["Open"].shift(1),
        np.maximum(df["High"] - df["Open"], open_diff),
        0.0,
    )
    dbm = np.where(
        df["Open"] < df["Open"].shift(1),
        np.maximum(df["Open"] - df["Low"], -open_diff),
        0.0,
    )
    stm = pd.Series(dtm, index=df.index).rolling(momentum_n, min_periods=1).sum()
    sbm = pd.Series(dbm, index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["adtm"] = (stm - sbm) / (pd.concat([stm, sbm], axis=1).max(axis=1) + 1e-8)

    close_open = df["Close"] - df["Open"]
    qstick_ma = close_open.rolling(momentum_n, min_periods=1).mean()
    df["qstick"] = close_open / (qstick_ma + 1e-8) - 1.0

    df["mtm"] = (df["Close"] / df["Close"].shift(momentum_n) - 1.0) * 100.0

    kst_roc1 = df["Close"] - df["Close"].shift(momentum_n)
    kst_roc2 = df["Close"] - df["Close"].shift(int(momentum_n * 1.5))
    kst_roc3 = df["Close"] - df["Close"].shift(momentum_n * 2)
    kst_roc4 = df["Close"] - df["Close"].shift(momentum_n * 3)
    kst_ind = (
        kst_roc1.rolling(momentum_n, min_periods=1).mean()
        + 2.0 * kst_roc2.rolling(momentum_n, min_periods=1).mean()
        + 3.0 * kst_roc3.rolling(momentum_n, min_periods=1).mean()
        + 4.0 * kst_roc4.rolling(momentum_n, min_periods=1).mean()
    )
    kst_smooth = kst_ind.rolling(momentum_n, min_periods=1).mean()
    df["kst"] = kst_ind / (kst_smooth + 1e-8)

    rmi_up = (df["Close"] - df["Close"].shift(4)).clip(lower=0.0)
    rmi_abs = df["Close"].diff().abs()
    df["rmi"] = 100.0 * rmi_up.rolling(momentum_n, min_periods=1).mean() / (
        rmi_abs.rolling(momentum_n, min_periods=1).mean() + 1e-8
    )

    tii_close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tii_dev = df["Close"] - tii_close_ma
    tii_devpos = pd.Series(np.where(tii_dev > 0, tii_dev, 0.0), index=df.index)
    tii_devneg = pd.Series(np.where(tii_dev < 0, -tii_dev, 0.0), index=df.index)
    tii_window = int(1 + momentum_n / 2)
    tii_raw = 100.0 * tii_devpos.rolling(tii_window, min_periods=1).sum() / (
        tii_devpos.rolling(tii_window, min_periods=1).sum()
        + tii_devneg.rolling(tii_window, min_periods=1).sum()
        + 1e-8
    )
    df["tii"] = (tii_raw - tii_raw.rolling(momentum_n, min_periods=1).min()) / (
        tii_raw.rolling(momentum_n, min_periods=1).max()
        - tii_raw.rolling(momentum_n, min_periods=1).min()
        + 1e-8
    )

    close_return_for_corr = df["Close"].pct_change()
    df["return_autocorr"] = close_return_for_corr.rolling(momentum_n, min_periods=2).corr(
        close_return_for_corr.shift(1)
    )

    demax = (df["High"] - df["High"].shift(1)).clip(lower=0.0)
    demin = (df["Low"].shift(1) - df["Low"]).clip(lower=0.0)
    demax_ma = demax.rolling(momentum_n, min_periods=1).mean()
    demin_ma = demin.rolling(momentum_n, min_periods=1).mean()
    df["demarker"] = demax_ma / (demax_ma + demin_ma + 1e-8)

    imi_inc = np.where(df["Close"] > df["Open"], df["Close"] - df["Open"], 0.0)
    imi_dec = np.where(df["Open"] > df["Close"], df["Open"] - df["Close"], 0.0)
    imi_inc_sum = pd.Series(imi_inc, index=df.index).rolling(momentum_n, min_periods=1).sum()
    imi_dec_sum = pd.Series(imi_dec, index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["imi"] = imi_inc_sum / (imi_inc_sum + imi_dec_sum + 1e-8)

    rvi_std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    rvi_up = pd.Series(np.where(df["Close"] > df["Close"].shift(1), rvi_std, 0.0), index=df.index)
    rvi_down = pd.Series(np.where(df["Close"] < df["Close"].shift(1), rvi_std, 0.0), index=df.index)
    rvi_up_sum = rvi_up.rolling(2 * momentum_n, min_periods=1).sum()
    rvi_down_sum = rvi_down.rolling(2 * momentum_n, min_periods=1).sum()
    df["rvi"] = 100.0 * rvi_up_sum / (rvi_up_sum + rvi_down_sum + 1e-8)

    df["bop"] = ((df["Close"] - df["Open"]) / (df["High"] - df["Low"] + 1e-8)).rolling(
        momentum_n,
        min_periods=1,
    ).mean()

    prev_close_uo = df["Close"].shift(1)
    true_high_uo = pd.concat([df["High"], prev_close_uo], axis=1).max(axis=1)
    true_low_uo = pd.concat([df["Low"], prev_close_uo], axis=1).min(axis=1)
    true_range_uo = true_high_uo - true_low_uo
    buying_pressure_uo = df["Close"] - true_low_uo
    uo_fast = buying_pressure_uo.rolling(momentum_n, min_periods=momentum_n).sum() / (
        true_range_uo.rolling(momentum_n, min_periods=momentum_n).sum() + 1e-8
    )
    uo_medium_n = 2 * momentum_n
    uo_slow_n = 4 * momentum_n
    uo_medium = buying_pressure_uo.rolling(uo_medium_n, min_periods=uo_medium_n).sum() / (
        true_range_uo.rolling(uo_medium_n, min_periods=uo_medium_n).sum() + 1e-8
    )
    uo_slow = buying_pressure_uo.rolling(uo_slow_n, min_periods=uo_slow_n).sum() / (
        true_range_uo.rolling(uo_slow_n, min_periods=uo_slow_n).sum() + 1e-8
    )
    df["ultimate_oscillator_src"] = 100.0 * (
        uo_fast * uo_medium_n * uo_slow_n
        + uo_medium * momentum_n * uo_slow_n
        + uo_slow * momentum_n * uo_medium_n
    ) / (momentum_n * uo_medium_n + momentum_n * uo_slow_n + uo_medium_n * uo_slow_n)

    highest_high_m = df["High"].rolling(momentum_n, min_periods=1).max()
    lowest_low_m = df["Low"].rolling(momentum_n, min_periods=1).min()
    df["williams_r"] = (highest_high_m - df["Close"]) / (highest_high_m - lowest_low_m + 1e-8) * 100.0

    slow_stoch_rsv = (df["Close"] - lowest_low_m) / (highest_high_m - lowest_low_m + 1e-8) * 100.0
    slow_stoch_k = slow_stoch_rsv.ewm(com=2, adjust=False).mean().ewm(com=2, adjust=False).mean()
    df["slow_stoch_d"] = slow_stoch_k.rolling(3, min_periods=1).mean()

    coppock_roc = 100.0 * (df["Close"].pct_change(momentum_n) + df["Close"].pct_change(2 * momentum_n))
    df["coppock"] = coppock_roc.rolling(momentum_n, min_periods=1).mean()

    close_roc_1 = df["Close"].pct_change() * 100.0
    pmo_base = close_roc_1.rolling(momentum_n, min_periods=1).mean() * 10.0
    pmo = pmo_base.rolling(4 * momentum_n, min_periods=1).mean()
    df["pmo"] = pmo.rolling(2 * momentum_n, min_periods=1).mean()

    smi_mid = (highest_high_m + lowest_low_m) / 2.0
    smi_distance = df["Close"] - smi_mid
    smi_distance_smoothed = smi_distance.ewm(span=momentum_n, adjust=False).mean().ewm(
        span=momentum_n,
        adjust=False,
    ).mean()
    smi_range_smoothed = (highest_high_m - lowest_low_m).ewm(span=momentum_n, adjust=False).mean().ewm(
        span=momentum_n,
        adjust=False,
    ).mean()
    smi = 100.0 * smi_distance_smoothed / (smi_range_smoothed + 1e-8)
    df["smi"] = smi.rolling(momentum_n, min_periods=1).mean()

    psy_up = pd.Series(
        np.where(df["Close"] > df["Close"].shift(1), 1.0, 0.0),
        index=df.index,
    )
    df["psy"] = psy_up.rolling(momentum_n, min_periods=1).sum() / momentum_n * 100.0

    close_return = df["Close"].pct_change()
    df["change_std"] = df["Close"].pct_change(momentum_n) * close_return.rolling(
        momentum_n, min_periods=momentum_n
    ).std(ddof=0)

    dpo_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["dpo"] = (df["Close"] - dpo_ma.shift(int(momentum_n / 2) + 1)) / (dpo_ma + 1e-8)

    direct_y = df["Close"] - df["Close"].shift(momentum_n - 1)
    direct_distance = (direct_y.pow(2) + (momentum_n - 1) ** 2) ** 0.5
    step_distance = (df["Close"].diff().pow(2) + 1.0) ** 0.5
    actual_distance = step_distance.rolling(momentum_n - 1, min_periods=momentum_n - 1).sum()
    pfe_raw = 100.0 * direct_distance / (actual_distance + 1e-8)
    pfe_direction = df["Close"].pct_change(momentum_n - 1)
    df["pfe"] = pfe_raw * pfe_direction

    high_ma = df["High"].rolling(fast_n, min_periods=1).mean()
    df["high_ma_bias"] = (df["High"] - high_ma) / (high_ma + 1e-8)

    boll_width = df["ub"] - df["lb"]
    df["bollinger_width"] = boll_width / (df["mb"] + 1e-8)
    df["bollinger_percent_b"] = (df["Close"] - df["lb"]) / (boll_width + 1e-8)


    rsi_frac = df["rsi"] / 100.0
    df["rsi_mean"] = rsi_frac.rolling(momentum_n, min_periods=1).mean()
    rsi_price_line = rsi_frac.ewm(span=momentum_n, adjust=False).mean()
    rsi_signal_line = rsi_frac.ewm(span=2 * momentum_n, adjust=False).mean()
    tdi_spread = rsi_price_line - rsi_signal_line
    df["tdi"] = (tdi_spread - tdi_spread.rolling(momentum_n, min_periods=1).min()) / (
        tdi_spread.rolling(momentum_n, min_periods=1).max()
        - tdi_spread.rolling(momentum_n, min_periods=1).min()
        + 1e-8
    )

    osc_raw = df["Close"] - df["Close"].rolling(2 * momentum_n, min_periods=1).mean()
    df["osc"] = osc_raw.rolling(momentum_n, min_periods=1).mean()


    quiet_price_change = df["Close"].pct_change(momentum_n)
    quiet_amplitude = df["High"] / (df["Low"] + 1e-8) - 1.0

    def quiet_momentum(window: pd.Series, keep_ratio: float) -> float:
        keep_count = max(1, int(len(window) * keep_ratio))
        selected_idx = quiet_amplitude.loc[window.index].nsmallest(keep_count).index
        return quiet_price_change.loc[selected_idx].sum()

    df["short_quiet_momentum"] = quiet_price_change.rolling(
        momentum_n,
        min_periods=momentum_n,
    ).apply(lambda window: quiet_momentum(window, 0.7), raw=False)
    df["long_quiet_momentum"] = quiet_price_change.rolling(
        10 * momentum_n,
        min_periods=10 * momentum_n,
    ).apply(lambda window: quiet_momentum(window, 0.7), raw=False)

    quote_volume_proxy_close = df["Close"] * df["Volume"]
    price_momentum_ema = (df["Close"] / (df["Close"].shift(momentum_n) + 1e-8) - 1.0).ewm(
        span=momentum_n,
        adjust=False,
    ).mean() * 100.0
    volume_momentum_ema = (
        quote_volume_proxy_close / (quote_volume_proxy_close.shift(momentum_n) + 1e-8) - 1.0
    ).ewm(span=momentum_n, adjust=False).mean() * 100.0
    df["price_volume_momentum"] = price_momentum_ema * volume_momentum_ema


    dbcd_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    dbcd_bias = (df["Close"] - dbcd_ma) / (dbcd_ma + 1e-8) * 100.0
    dbcd_bias_diff = dbcd_bias - dbcd_bias.shift(3 * momentum_n)
    df["dbcd"] = dbcd_bias_diff.rolling(3 * momentum_n + 2, min_periods=1).mean()

    pmar = (df["Close"] / (bias_ma + 1e-8)).abs()
    df["pmarp"] = pmar.rolling(momentum_n, min_periods=1).rank(pct=True) * 100.0

    pos_price = df["Close"].pct_change(momentum_n)
    pos_min = pos_price.rolling(momentum_n, min_periods=momentum_n).min()
    pos_max = pos_price.rolling(momentum_n, min_periods=momentum_n).max()
    df["pos"] = (pos_price - pos_min) / (pos_max - pos_min + 1e-8)

    bias36 = df["Close"].rolling(3, min_periods=1).mean() - df["Close"].rolling(6, min_periods=1).mean()
    bias36_centered = bias36 - bias36.rolling(momentum_n, min_periods=1).mean()
    df["bias36"] = (bias36_centered - bias36_centered.rolling(momentum_n, min_periods=1).min()) / (
        bias36_centered.rolling(momentum_n, min_periods=1).max()
        - bias36_centered.rolling(momentum_n, min_periods=1).min()
        + 1e-8
    )

    si_a = (df["High"] - df["Close"].shift(1)).abs()
    si_b = (df["Low"] - df["Close"].shift(1)).abs()
    si_c = (df["High"] - df["Low"].shift(1)).abs()
    si_d = (df["Close"].shift(1) - df["Open"].shift(1)).abs()
    si_k = pd.concat([si_a, si_b], axis=1).max(axis=1)
    si_m = (df["High"] - df["Low"]).rolling(momentum_n, min_periods=momentum_n).max()
    si_r1 = si_a + 0.5 * si_b + 0.25 * si_d
    si_r2 = si_b + 0.5 * si_a + 0.25 * si_d
    si_r3 = si_c + 0.25 * si_d
    si_r4 = pd.Series(np.where((si_a >= si_b) & (si_a >= si_c), si_r1, si_r2), index=df.index)
    si_r = pd.Series(np.where((si_c >= si_a) & (si_c >= si_b), si_r3, si_r4), index=df.index)
    si_move = df["Close"].diff() + (df["Close"].shift(1) - df["Open"].shift(1)) + 0.5 * (
        df["Close"] - df["Open"]
    )
    df["swing_index"] = 50.0 * si_move / (si_r + 1e-8) * si_k / (si_m + 1e-8)


    close_diff = df["Close"].diff()
    close_up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    close_down = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    close_up_sum = close_up.rolling(momentum_n, min_periods=1).sum()
    close_down_sum = close_down.rolling(momentum_n, min_periods=1).sum()
    df["rsi_v2"] = close_up_sum / (close_up_sum + close_down_sum + 1e-8)

    cmo_up = close_up.rolling(momentum_n, min_periods=1).sum()
    cmo_down = close_down.rolling(momentum_n, min_periods=1).sum()
    df["cmo_v2"] = (cmo_up - cmo_down) / (cmo_up + cmo_down + 1e-8)

    bias_fast = df["Close"].rolling(max(1, momentum_n // 2), min_periods=1).mean()
    bias_slow = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["bias_v13"] = (bias_fast / (bias_slow + 1e-8) - 1.0).rolling(momentum_n, min_periods=1).mean()

    df["abs_chg"] = df["Close"].pct_change(momentum_n).abs()

    stc_fast = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    stc_slow = df["Close"].ewm(span=2 * momentum_n, adjust=False).mean()
    stc_macd = stc_fast - stc_slow
    stc_low_1 = stc_macd.rolling(2 * momentum_n, min_periods=1).min()
    stc_high_1 = stc_macd.rolling(2 * momentum_n, min_periods=1).max()
    fk = (stc_macd - stc_low_1) / (stc_high_1 - stc_low_1 + 1e-8) * 100.0
    fd = fk.rolling(2 * momentum_n, min_periods=1).mean()
    stc_low_2 = fd.rolling(2 * momentum_n, min_periods=1).min()
    stc_high_2 = fd.rolling(2 * momentum_n, min_periods=1).max()
    sk = (fd - stc_low_2) / (stc_high_2 - stc_low_2 + 1e-8) * 100.0
    df["stc"] = sk.rolling(momentum_n, min_periods=1).mean()


    return_ac = df["Close"].pct_change().rolling(momentum_n, min_periods=2).corr(df["Close"].pct_change().shift(1))
    df["return_autocorr_2"] = return_ac

    er_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    df["erbull"] = (df["High"] - er_ema) / (er_ema + 1e-8)
    df["erbear"] = (df["Low"] - er_ema) / (er_ema + 1e-8)
    df["er_balance"] = df["erbull"] + df["erbear"]

    df["burr"] = (
        (1.0 - df["Close"] / (df["High"].rolling(momentum_n, min_periods=1).max() + 1e-8)).where(
            df["Close"] - df["Open"].shift(momentum_n) > 0
        ).fillna(0.0)
        + (1.0 - df["Close"] / (df["Low"].rolling(momentum_n, min_periods=1).min() + 1e-8)).where(
            df["Close"] - df["Open"].shift(momentum_n) < 0
        ).fillna(0.0)
    )

    mid_price = (df["High"] + df["Low"]) / 2.0
    macd_v2_ema1 = mid_price.ewm(span=momentum_n, adjust=False).mean()
    macd_v2_ema2 = mid_price.ewm(span=2 * momentum_n, adjust=False).mean()
    macd_v2_dif = macd_v2_ema1 - macd_v2_ema2
    macd_v2_dea = macd_v2_dif.ewm(span=max(1, int(momentum_n / 2)), adjust=False).mean()
    df["macd_v2"] = 10.0 * (2.0 * macd_v2_dif - macd_v2_dea)

    ppo_v1_ema1 = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    ppo_v1_ema2 = df["Close"].ewm(span=2 * momentum_n, adjust=False).mean()
    ppo_v1_base = (ppo_v1_ema1 / (ppo_v1_ema1.shift(momentum_n) + 1e-8) - 1.0) * (
        (ppo_v1_ema2 / (ppo_v1_ema2.shift(2 * momentum_n) + 1e-8) - 1.0).abs()
    )
    df["ppo_v1"] = ppo_v1_base.ewm(span=momentum_n, adjust=False).mean()

    sroc_v2_kama = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    sroc_v2_ref = sroc_v2_kama.shift(2 * momentum_n)
    df["sroc_v2"] = (sroc_v2_kama - sroc_v2_ref) / (sroc_v2_ref + 1e-8)

    tema_ema_1 = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    tema_ema_2 = tema_ema_1.ewm(span=momentum_n, adjust=False).mean()
    tema_ema_3 = tema_ema_2.ewm(span=momentum_n, adjust=False).mean()
    tema = 3.0 * tema_ema_1 - 3.0 * tema_ema_2 + tema_ema_3
    tema_roc = tema.pct_change() * 100.0
    tema_roc_ma = tema_roc.rolling(momentum_n, min_periods=1).mean() * 10.0
    pmo_tema = tema_roc_ma.rolling(4 * momentum_n, min_periods=1).mean()
    df["pmo_tema"] = pmo_tema.rolling(2 * momentum_n, min_periods=1).mean()

    fisher_price = (df["High"] + df["Low"]) / 2.0
    fisher_min_low = df["Low"].rolling(momentum_n, min_periods=1).min()
    fisher_max_high = df["High"].rolling(momentum_n, min_periods=1).max()
    fisher_base = 2.0 * ((fisher_price - fisher_min_low) / (fisher_max_high - fisher_min_low + 1e-8) - 0.5)
    fisher_v2_price_change = fisher_base + 0.5 * fisher_base.shift(1)
    fisher_v2_price_change = fisher_v2_price_change.clip(-0.999, 0.999)
    df["fisher_v2"] = 0.3 * fisher_v2_price_change + 0.7 * fisher_v2_price_change.shift(1)

    fisher_v3_price_change = 0.33 * fisher_base + 0.67 * fisher_base.shift(1)
    fisher_v3_price_change = fisher_v3_price_change.clip(-0.999, 0.999)
    df["fisher_v3"] = 0.5 * fisher_v3_price_change.shift(1) + 0.5 * np.log(
        (1.0 + fisher_v3_price_change) / (1.0 - fisher_v3_price_change)
    )

    arbr_ar_up = (df["High"] - df["Open"]).rolling(momentum_n, min_periods=1).sum()
    arbr_ar_dn = (df["Open"] - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["arbr_ar"] = 100.0 * arbr_ar_up / (arbr_ar_dn + 1e-8)

    arbr_br_up = (df["High"] - df["Close"].shift(1)).rolling(momentum_n, min_periods=1).sum()
    arbr_br_dn = (df["Close"].shift(1) - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["arbr_br"] = 100.0 * arbr_br_up / (arbr_br_dn + 1e-8)

    df = df.copy()

    close_diff = df["Close"].diff()
    up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    dn = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    rsi_raw = up.rolling(momentum_n, min_periods=1).sum() / (up.rolling(momentum_n, min_periods=1).sum() + dn.rolling(momentum_n, min_periods=1).sum() + 1e-8)
    do_smooth = rsi_raw.ewm(span=momentum_n, adjust=False).mean().ewm(span=momentum_n, adjust=False).mean()
    df["do"] = do_smooth

    ema_short = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    ema_long = df["Close"].ewm(span=3 * momentum_n, adjust=False).mean()
    df["po"] = (ema_short - ema_long) / (ema_long + 1e-8) * 100.0

    open_ma = df["Open"].rolling(momentum_n, min_periods=1).mean()
    high_ma = df["High"].rolling(momentum_n, min_periods=1).mean()
    low_ma = df["Low"].rolling(momentum_n, min_periods=1).mean()
    close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tp = (high_ma + low_ma + close_ma) / 3.0
    tp_ma = tp.rolling(momentum_n, min_periods=1).mean()
    md = (tp - close_ma).abs().rolling(momentum_n, min_periods=1).mean()
    df["cci_magic"] = (tp - tp_ma) / (0.015 * md + 1e-8)

    quote_volume_proxy = df["Close"] * df["Volume"]
    c_mtm = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    c_mtm = c_mtm.rolling(momentum_n, min_periods=1).mean()
    s_std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    s_mtm = (s_std / s_std.shift(momentum_n)).rolling(momentum_n, min_periods=1).mean()
    v_mtm = (quote_volume_proxy / (quote_volume_proxy.shift(momentum_n) + 1e-8)).rolling(momentum_n, min_periods=1).mean()
    df["cs_mtm"] = c_mtm * s_mtm * v_mtm



    close_dif = df["Close"].diff()
    up = pd.Series(np.where(close_dif > 0, close_dif, 0.0), index=df.index)
    down = pd.Series(np.where(close_dif < 0, -close_dif, 0.0), index=df.index)
    a = up.rolling(momentum_n, min_periods=1).sum()
    b = down.rolling(momentum_n, min_periods=1).sum()
    rsi = 100.0 * a / (a + b + 1e-8)
    median = df["Close"].rolling(momentum_n, min_periods=1).mean()
    std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    bbw = (std / (median + 1e-8)).diff(momentum_n)
    df["rsi_bbw"] = bbw * (df["Close"].pct_change(momentum_n)) * rsi



    rc = df["Close"] / df["Close"].shift(2 * momentum_n)
    arc1 = rc.rolling(2 * momentum_n, min_periods=1).mean()
    ma1 = arc1.shift(1).rolling(momentum_n, min_periods=1).mean()
    ma2 = arc1.shift(1).rolling(2 * momentum_n, min_periods=1).mean()
    dif = ma1 - ma2
    df["rccd"] = dif.rolling(2 * momentum_n, min_periods=1).mean()

    def sma_like(ser: pd.Series, n: int, m: int = 1) -> pd.Series:
        out = []
        for i, v in enumerate(ser.fillna(0.0)):
            if i == 0:
                out.append(v)
            else:
                r = m / n
                out.append(r * v + (1 - r) * out[-1])
        return pd.Series(out, index=ser.index)

    rccd_v2_arc1 = sma_like(rc, momentum_n, 1)
    rccd_v2_ma1 = rccd_v2_arc1.shift(1).rolling(momentum_n, min_periods=1).mean()
    rccd_v2_ma2 = rccd_v2_arc1.shift(1).rolling(2 * momentum_n, min_periods=1).mean()
    rccd_v2_dif = rccd_v2_ma1 - rccd_v2_ma2
    df["rccd_v2"] = sma_like(rccd_v2_dif, momentum_n, 1)

    ma_volume = df["Volume"].rolling(momentum_n, min_periods=1).mean()
    df["bias_vol"] = (df["Volume"] - ma_volume) / (ma_volume + 1e-8)

    ma_1 = df["Close"].rolling(max(1, momentum_n // 2), min_periods=1).mean()
    ma_2 = df["Close"].rolling(momentum_n, min_periods=1).mean()
    ma_3 = df["Close"].rolling(2 * momentum_n, min_periods=1).mean()
    bias_1 = df["Close"] / (ma_1 + 1e-8) - 1.0
    bias_2 = df["Close"] / (ma_2 + 1e-8) - 1.0
    bias_3 = df["Close"] / (ma_3 + 1e-8) - 1.0
    quote_volume_proxy = df["Close"] * df["Volume"]
    df["bias_cubic_v2"] = (bias_1 * bias_2 * bias_3) * (quote_volume_proxy / (quote_volume_proxy.rolling(momentum_n, min_periods=1).mean() + 1e-8)).rolling(momentum_n, min_periods=1).mean()

    route_1 = (df["High"] - df["Open"]) + (df["High"] - df["Low"]) + (df["Close"] - df["Low"])
    route_2 = (df["Open"] - df["Low"]) + (df["High"] - df["Low"]) + (df["High"] - df["Close"])
    min_route = pd.concat([route_1, route_2], axis=1).min(axis=1) / (df["Open"] + 1e-8)
    rc_copp = 100.0 * (df["Close"] / df["Close"].shift(momentum_n) - 1.0 + df["Close"] / df["Close"].shift(2 * momentum_n) - 1.0)
    rc_copp = rc_copp.ewm(span=momentum_n, adjust=False).mean()
    min_route = min_route.ewm(span=momentum_n, adjust=False).mean()
    df["copp_min_route"] = rc_copp / (min_route + 1e-8)



    open_prev = df["Open"].shift(1)
    tmp1 = df["High"] - df["Open"]
    tmp2 = df["Open"] - open_prev
    tmp3 = df["Open"] - df["Low"]
    tmp4 = open_prev - df["Open"]
    dtm = pd.Series(np.where(df["Open"] > open_prev, np.maximum(tmp1, tmp2), 0.0), index=df.index)
    dbm = pd.Series(np.where(df["Open"] < open_prev, np.maximum(tmp3, tmp4), 0.0), index=df.index)
    stm = dtm.rolling(momentum_n, min_periods=1).sum()
    sbm = dbm.rolling(momentum_n, min_periods=1).sum()
    adtm_base = (stm - sbm) / (pd.concat([stm, sbm], axis=1).max(axis=1) + 1e-8)
    df["adtm_v2"] = (adtm_base - adtm_base.rolling(momentum_n, min_periods=1).min()) / (
        adtm_base.rolling(momentum_n, min_periods=1).max() - adtm_base.rolling(momentum_n, min_periods=1).min() + 1e-8
    )

    adtm_v3_base = adtm_base - df["Close"] / (adtm_base + 1e-8)
    df["adtm_v3"] = (adtm_v3_base - adtm_v3_base.rolling(momentum_n, min_periods=1).min()) / (
        adtm_v3_base.rolling(momentum_n, min_periods=1).max() - adtm_v3_base.rolling(momentum_n, min_periods=1).min() + 1e-8
    )

    mtm_gap = df["Close"].pct_change(momentum_n)
    body_gap = 1.0 - (df["Close"] - df["Open"]).abs() / (df["High"] - df["Low"] + 1e-8)
    df["mtm_mean_gap"] = mtm_gap.rolling(momentum_n, min_periods=1).mean() / (
        body_gap.rolling(momentum_n, min_periods=1).mean() + 1e-8
    )




    close_diff = df["Close"].diff()
    cmo_up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    cmo_dn = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    cmo_up_sum = cmo_up.rolling(momentum_n, min_periods=1).sum()
    cmo_dn_sum = cmo_dn.rolling(momentum_n, min_periods=1).sum()
    cmo_v3_raw = 100.0 * (cmo_up_sum - cmo_dn_sum) / (cmo_up_sum + cmo_dn_sum + 1e-8)
    df["cmo_v3"] = cmo_v3_raw.rolling(momentum_n, min_periods=1).mean()

    close_diff_pos = np.where(df["Close"] > df["Close"].shift(1), df["Close"] - df["Close"].shift(1), 0.0)
    rsis_a = pd.Series(close_diff_pos, index=df.index).ewm(alpha=1 / (4 * momentum_n), adjust=False).mean()
    rsis_b = (df["Close"] - df["Close"].shift(1)).abs().ewm(alpha=1 / (4 * momentum_n), adjust=False).mean()
    rsis = 100.0 * rsis_a / (1e-9 + rsis_b)
    rsis_min = rsis.rolling(int(4 * momentum_n), min_periods=1).min()
    rsis_max = rsis.rolling(int(4 * momentum_n), min_periods=1).max()
    df["rsis_v2"] = 100.0 * (rsis - rsis_min) / (1e-9 + rsis_max - rsis_min)

    quote_volume_proxy = df["Close"] * df["Volume"]
    mtm_resonance = (df["Close"] / df["Close"].shift(momentum_n) - 1.0).rolling(momentum_n, min_periods=1).mean()
    quote_volume_mean = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean()
    quote_volume_change_mean = (quote_volume_proxy / (quote_volume_mean + 1e-8)).rolling(momentum_n, min_periods=1).mean()
    df["mtm_vol_resonance"] = mtm_resonance * quote_volume_change_mean



    tii_close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tii_dev = df["Close"] - tii_close_ma
    tii_dev_pos = pd.Series(np.where(tii_dev > 0, tii_dev, 0.0), index=df.index)
    tii_dev_neg = pd.Series(np.where(tii_dev < 0, -tii_dev, 0.0), index=df.index)
    tii_sum_pos = tii_dev_pos.rolling(int(1 + momentum_n / 2), min_periods=1).sum()
    tii_sum_neg = tii_dev_neg.rolling(int(1 + momentum_n / 2), min_periods=1).sum()
    tii_raw = 100.0 * tii_sum_pos / (tii_sum_pos + tii_sum_neg + 1e-8)
    tii_signal = tii_raw.ewm(span=max(1, int(momentum_n / 2)), adjust=False, min_periods=1).mean()
    df["tii_signal"] = tii_signal
    tii_signal_diff = tii_raw - tii_signal
    tii_signal_diff_min = tii_signal_diff.rolling(momentum_n, min_periods=1).min()
    tii_signal_diff_max = tii_signal_diff.rolling(momentum_n, min_periods=1).max()
    df["tii_signal_v2"] = (tii_signal_diff - tii_signal_diff_min) / (1e-9 + tii_signal_diff_max - tii_signal_diff_min)

    return df
