import numpy as np
import pandas as pd
import pandas_ta as ta
from autofcholv.config.config import Config


def _rolling_regression_last(values: np.ndarray) -> float:
    if len(values) < 2 or not np.isfinite(values).all():
        return np.nan
    x = np.arange(len(values), dtype=float)
    try:
        slope, intercept = np.polyfit(x, values, 1)
    except Exception:
        return np.nan
    return slope * x[-1] + intercept


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate features based on Close column.
    Feature definitions follow close.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    fast_n     = config.fast_trend_lookback
    slow_n     = config.slow_trend_lookback
    momentum_n = config.momentum_lookback
    epsilon = 1e-8

    df = df.copy()

    df["price_change"] = df["Close"].diff()
    df["price_change_lag1"] = df["price_change"].shift(1)

    # 5-tier Returns
    df["return_micro"] = df["Close"].pct_change(config.micro_lookback)
    df["return_short"] = df["Close"].pct_change(config.short_lookback)
    df["return_medium"] = df["Close"].pct_change(config.medium_lookback)
    df["return_long"] = df["Close"].pct_change(config.long_lookback)
    df["return_macro"] = df["Close"].pct_change(config.macro_lookback)

    # 5-tier SMA
    df["sma_micro"] = df["Close"].rolling(config.micro_lookback).mean()
    df["sma_short"] = df["Close"].rolling(config.short_lookback).mean()
    df["sma_medium"] = df["Close"].rolling(config.medium_lookback).mean()
    df["sma_long"] = df["Close"].rolling(config.long_lookback).mean()
    df["sma_macro"] = df["Close"].rolling(config.macro_lookback).mean()

    # 5-tier STD
    df["std_micro"] = df["Close"].rolling(config.micro_lookback).std()
    df["std_short"] = df["Close"].rolling(config.short_lookback).std()
    df["std_medium"] = df["Close"].rolling(config.medium_lookback).std()
    df["std_long"] = df["Close"].rolling(config.long_lookback).std()
    df["std_macro"] = df["Close"].rolling(config.macro_lookback).std()

    # 5-tier Close Min / Max
    df["close_min_micro"] = df["Close"].rolling(config.micro_lookback).min()
    df["close_min_short"] = df["Close"].rolling(config.short_lookback).min()
    df["close_min_medium"] = df["Close"].rolling(config.medium_lookback).min()
    df["close_min_long"] = df["Close"].rolling(config.long_lookback).min()
    df["close_min_macro"] = df["Close"].rolling(config.macro_lookback).min()

    df["close_max_micro"] = df["Close"].rolling(config.micro_lookback).max()
    df["close_max_short"] = df["Close"].rolling(config.short_lookback).max()
    df["close_max_medium"] = df["Close"].rolling(config.medium_lookback).max()
    df["close_max_long"] = df["Close"].rolling(config.long_lookback).max()
    df["close_max_macro"] = df["Close"].rolling(config.macro_lookback).max()

    df["ema_fast"] = ta.ema(df["Close"], length=fast_n)
    df["ema_slow"] = ta.ema(df["Close"], length=slow_n)

    # 5-tier RSI
    df["rsi_micro"] = ta.rsi(df["Close"], length=config.micro_lookback)
    df["rsi_short"] = ta.rsi(df["Close"], length=config.short_lookback)
    df["rsi_medium"] = ta.rsi(df["Close"], length=config.medium_lookback)
    df["rsi_long"] = ta.rsi(df["Close"], length=config.long_lookback)
    df["rsi_macro"] = ta.rsi(df["Close"], length=config.macro_lookback)
    df["rsi_slope_medium"] = df["rsi_medium"].diff()

    tsi_result = ta.tsi(df["Close"])
    if tsi_result is not None and not tsi_result.empty:
        df["tsi"] = tsi_result.iloc[:, 0]

    df["roc_close"] = ta.roc(df["Close"], length=1)

    df["close_zscore"] = ta.zscore(df["Close"], length=momentum_n)

    change     = df["Close"].diff(1).abs()
    net_change = (df["Close"] - df["Close"].shift(momentum_n)).abs()
    volatility = change.rolling(momentum_n).sum()
    df["efficiency_ratio"] = net_change / volatility

    macd_params = config.classic_indicators.get("MACD", [12, 26, 9])
    fast, slow, signal = macd_params[0], macd_params[1], macd_params[2]
    macd_result = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
    if macd_result is not None and not macd_result.empty:
        df["macd"]        = macd_result.iloc[:, 0]
        df["macd_hist"]   = macd_result.iloc[:, 1]
        df["macd_line"] = macd_result.iloc[:, 2]

    ppo_params = config.classic_indicators.get("PPO", [12, 26, 9])
    ppo_fast, ppo_slow, ppo_signal = ppo_params[0], ppo_params[1], ppo_params[2]
    ppo_result = ta.ppo(df["Close"], fast=ppo_fast, slow=ppo_slow, signal=ppo_signal)
    if ppo_result is not None and not ppo_result.empty:
        df["ppo"]        = ppo_result.iloc[:, 0]
        df["ppo_hist"]   = ppo_result.iloc[:, 1]
        df["ppo_line"] = ppo_result.iloc[:, 2]

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
    df["cci"] = (typical_price - typical_ma) / (0.015 * typical_md + epsilon)

    lowest_low = df["Low"].rolling(momentum_n, min_periods=1).min()
    highest_high = df["High"].rolling(momentum_n, min_periods=1).max()
    rsv = (df["Close"] - lowest_low) / (highest_high - lowest_low + epsilon) * 100.0
    df["kdj_k"] = rsv.ewm(com=2, adjust=False).mean()
    df["kdj_d"] = df["kdj_k"].ewm(com=2, adjust=False).mean()
    df["kdj_j"] = 3.0 * df["kdj_k"] - 2.0 * df["kdj_d"]

    median_price = (df["High"] + df["Low"]) / 2.0
    median_low = median_price.rolling(momentum_n, min_periods=1).min()
    median_high = median_price.rolling(momentum_n, min_periods=1).max()
    fisher_value = 2.0 * ((median_price - median_low) / (median_high - median_low + epsilon) - 0.5)
    fisher_value = pd.Series(fisher_value, index=df.index).ewm(alpha=1.0 / momentum_n, adjust=False).mean()
    fisher_value = fisher_value.clip(-0.999, 0.999)
    df["fisher"] = 0.5 * np.log((1.0 + fisher_value) / (1.0 - fisher_value))

    direction_n = (df["Close"] - df["Close"].shift(momentum_n)).abs()
    volatility_n = df["Close"].diff().abs().rolling(momentum_n, min_periods=1).sum()
    er = direction_n / (volatility_n + epsilon)
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
    df["kama_bias"] = df["Close"] / (df["kama"] + epsilon) - 1.0

    bias_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["bias"] = df["Close"] / (bias_ma + epsilon) - 1.0
    df["rbias"] = (df["Close"] / (bias_ma + epsilon)) / (
        df["Close"].shift(1) / (bias_ma.shift(1) + epsilon)
    ) - 1.0

    mtm_base = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    df["mtm_mean"] = mtm_base.rolling(momentum_n, min_periods=1).mean()
    df["mtm_max_diff"] = mtm_base - mtm_base.rolling(momentum_n, min_periods=momentum_n).max().shift(1)

    sroc_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    sroc_ref = sroc_ema.shift(2 * momentum_n)
    df["sroc"] = (sroc_ema - sroc_ref) / (sroc_ref + epsilon)

    ar_up = (df["High"] - df["Open"]).rolling(momentum_n, min_periods=1).sum()
    ar_down = (df["Open"] - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["ar"] = 100.0 * ar_up / (ar_down + epsilon)

    prev_close_pressure = df["Close"].shift(1)
    br_up = (df["High"] - prev_close_pressure).rolling(momentum_n, min_periods=1).sum()
    br_down = (prev_close_pressure - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["br"] = 100.0 * br_up / (br_down + epsilon)

    cr_typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
    cr_h = (df["High"] - cr_typical.shift(1)).clip(lower=0.0)
    cr_l = (cr_typical.shift(1) - df["Low"]).clip(lower=0.0)
    df["cr"] = 100.0 * cr_h.rolling(momentum_n, min_periods=1).sum() / (
        cr_l.rolling(momentum_n, min_periods=1).sum() + epsilon
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
    df["adtm"] = (stm - sbm) / (pd.concat([stm, sbm], axis=1).max(axis=1) + epsilon)

    close_open = df["Close"] - df["Open"]
    qstick_ma = close_open.rolling(momentum_n, min_periods=1).mean()
    df["qstick"] = close_open / (qstick_ma + epsilon) - 1.0

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
    df["kst"] = kst_ind / (kst_smooth + epsilon)

    rmi_up = (df["Close"] - df["Close"].shift(4)).clip(lower=0.0)
    rmi_abs = df["Close"].diff().abs()
    df["rmi"] = 100.0 * rmi_up.rolling(momentum_n, min_periods=1).mean() / (
        rmi_abs.rolling(momentum_n, min_periods=1).mean() + epsilon
    )

    tii_close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tii_dev = df["Close"] - tii_close_ma
    tii_devpos = pd.Series(np.where(tii_dev > 0, tii_dev, 0.0), index=df.index)
    tii_devneg = pd.Series(np.where(tii_dev < 0, -tii_dev, 0.0), index=df.index)
    tii_window = int(1 + momentum_n / 2)
    tii_raw = 100.0 * tii_devpos.rolling(tii_window, min_periods=1).sum() / (
        tii_devpos.rolling(tii_window, min_periods=1).sum()
        + tii_devneg.rolling(tii_window, min_periods=1).sum()
        + epsilon
    )
    df["tii"] = (tii_raw - tii_raw.rolling(momentum_n, min_periods=1).min()) / (
        tii_raw.rolling(momentum_n, min_periods=1).max()
        - tii_raw.rolling(momentum_n, min_periods=1).min()
        + epsilon
    )

    close_return_for_corr = df["Close"].pct_change()
    df["return_autocorr"] = close_return_for_corr.rolling(momentum_n, min_periods=2).corr(
        close_return_for_corr.shift(1)
    )

    demax = (df["High"] - df["High"].shift(1)).clip(lower=0.0)
    demin = (df["Low"].shift(1) - df["Low"]).clip(lower=0.0)
    demax_ma = demax.rolling(momentum_n, min_periods=1).mean()
    demin_ma = demin.rolling(momentum_n, min_periods=1).mean()
    df["demarker"] = demax_ma / (demax_ma + demin_ma + epsilon)

    imi_inc = np.where(df["Close"] > df["Open"], df["Close"] - df["Open"], 0.0)
    imi_dec = np.where(df["Open"] > df["Close"], df["Open"] - df["Close"], 0.0)
    imi_inc_sum = pd.Series(imi_inc, index=df.index).rolling(momentum_n, min_periods=1).sum()
    imi_dec_sum = pd.Series(imi_dec, index=df.index).rolling(momentum_n, min_periods=1).sum()
    df["imi"] = imi_inc_sum / (imi_inc_sum + imi_dec_sum + epsilon)

    rvi_std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    rvi_up = pd.Series(np.where(df["Close"] > df["Close"].shift(1), rvi_std, 0.0), index=df.index)
    rvi_down = pd.Series(np.where(df["Close"] < df["Close"].shift(1), rvi_std, 0.0), index=df.index)
    rvi_up_sum = rvi_up.rolling(2 * momentum_n, min_periods=1).sum()
    rvi_down_sum = rvi_down.rolling(2 * momentum_n, min_periods=1).sum()
    df["rvi"] = 100.0 * rvi_up_sum / (rvi_up_sum + rvi_down_sum + epsilon)

    df["bop"] = ((df["Close"] - df["Open"]) / (df["High"] - df["Low"] + epsilon)).rolling(
        momentum_n,
        min_periods=1,
    ).mean()

    prev_close_uo = df["Close"].shift(1)
    true_high_uo = pd.concat([df["High"], prev_close_uo], axis=1).max(axis=1)
    true_low_uo = pd.concat([df["Low"], prev_close_uo], axis=1).min(axis=1)
    true_range_uo = true_high_uo - true_low_uo
    buying_pressure_uo = df["Close"] - true_low_uo
    uo_fast = buying_pressure_uo.rolling(momentum_n, min_periods=momentum_n).sum() / (
        true_range_uo.rolling(momentum_n, min_periods=momentum_n).sum() + epsilon
    )
    uo_medium_n = 2 * momentum_n
    uo_slow_n = 4 * momentum_n
    uo_medium = buying_pressure_uo.rolling(uo_medium_n, min_periods=uo_medium_n).sum() / (
        true_range_uo.rolling(uo_medium_n, min_periods=uo_medium_n).sum() + epsilon
    )
    uo_slow = buying_pressure_uo.rolling(uo_slow_n, min_periods=uo_slow_n).sum() / (
        true_range_uo.rolling(uo_slow_n, min_periods=uo_slow_n).sum() + epsilon
    )
    df["ultimate_oscillator_src"] = 100.0 * (
        uo_fast * uo_medium_n * uo_slow_n
        + uo_medium * momentum_n * uo_slow_n
        + uo_slow * momentum_n * uo_medium_n
    ) / (momentum_n * uo_medium_n + momentum_n * uo_slow_n + uo_medium_n * uo_slow_n)

    highest_high_m = df["High"].rolling(momentum_n, min_periods=1).max()
    lowest_low_m = df["Low"].rolling(momentum_n, min_periods=1).min()
    df["williams_r"] = (highest_high_m - df["Close"]) / (highest_high_m - lowest_low_m + epsilon) * 100.0

    slow_stoch_rsv = (df["Close"] - lowest_low_m) / (highest_high_m - lowest_low_m + epsilon) * 100.0
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
    smi = 100.0 * smi_distance_smoothed / (smi_range_smoothed + epsilon)
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
    df["dpo"] = (df["Close"] - dpo_ma.shift(int(momentum_n / 2) + 1)) / (dpo_ma + epsilon)

    direct_y = df["Close"] - df["Close"].shift(momentum_n - 1)
    direct_distance = (direct_y.pow(2) + (momentum_n - 1) ** 2) ** 0.5
    step_distance = (df["Close"].diff().pow(2) + 1.0) ** 0.5
    actual_distance = step_distance.rolling(momentum_n - 1, min_periods=momentum_n - 1).sum()
    pfe_raw = 100.0 * direct_distance / (actual_distance + epsilon)
    pfe_direction = df["Close"].pct_change(momentum_n - 1)
    df["pfe"] = pfe_raw * pfe_direction

    high_ma = df["High"].rolling(fast_n, min_periods=1).mean()
    df["high_ma_bias"] = (df["High"] - high_ma) / (high_ma + epsilon)

    boll_width = df["ub"] - df["lb"]
    df["bollinger_width"] = boll_width / (df["mb"] + epsilon)
    df["bollinger_percent_b"] = (df["Close"] - df["lb"]) / (boll_width + epsilon)


    rsi_frac = df["rsi_medium"] / 100.0
    df["rsi_mean"] = rsi_frac.rolling(momentum_n, min_periods=1).mean()
    rsi_price_line = rsi_frac.ewm(span=momentum_n, adjust=False).mean()
    rsi_signal_line = rsi_frac.ewm(span=2 * momentum_n, adjust=False).mean()
    tdi_spread = rsi_price_line - rsi_signal_line
    df["tdi"] = (tdi_spread - tdi_spread.rolling(momentum_n, min_periods=1).min()) / (
        tdi_spread.rolling(momentum_n, min_periods=1).max()
        - tdi_spread.rolling(momentum_n, min_periods=1).min()
        + epsilon
    )

    osc_raw = df["Close"] - df["Close"].rolling(2 * momentum_n, min_periods=1).mean()
    df["osc"] = osc_raw.rolling(momentum_n, min_periods=1).mean()


    quiet_price_change = df["Close"].pct_change(momentum_n)
    quiet_amplitude = df["High"] / (df["Low"] + epsilon) - 1.0

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
    price_momentum_ema = (df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0).ewm(
        span=momentum_n,
        adjust=False,
    ).mean() * 100.0
    volume_momentum_ema = (
        quote_volume_proxy_close / (quote_volume_proxy_close.shift(momentum_n) + epsilon) - 1.0
    ).ewm(span=momentum_n, adjust=False).mean() * 100.0
    df["price_volume_momentum"] = price_momentum_ema * volume_momentum_ema


    dbcd_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    dbcd_bias = (df["Close"] - dbcd_ma) / (dbcd_ma + epsilon) * 100.0
    dbcd_bias_diff = dbcd_bias - dbcd_bias.shift(3 * momentum_n)
    df["dbcd"] = dbcd_bias_diff.rolling(3 * momentum_n + 2, min_periods=1).mean()

    pmar = (df["Close"] / (bias_ma + epsilon)).abs()
    df["pmarp"] = pmar.rolling(momentum_n, min_periods=1).rank(pct=True) * 100.0

    pos_price = df["Close"].pct_change(momentum_n)
    pos_min = pos_price.rolling(momentum_n, min_periods=momentum_n).min()
    pos_max = pos_price.rolling(momentum_n, min_periods=momentum_n).max()
    df["pos"] = (pos_price - pos_min) / (pos_max - pos_min + epsilon)

    bias36_params = config.classic_indicators.get("BIAS36", [3, 6])
    b3 = bias36_params[0] if isinstance(bias36_params, list) else int(bias36_params)
    b6 = bias36_params[1] if isinstance(bias36_params, list) and len(bias36_params) > 1 else 6
    bias36 = df["Close"].rolling(b3, min_periods=1).mean() - df["Close"].rolling(b6, min_periods=1).mean()
    bias36_centered = bias36 - bias36.rolling(momentum_n, min_periods=1).mean()
    df["bias36"] = (bias36_centered - bias36_centered.rolling(momentum_n, min_periods=1).min()) / (
        bias36_centered.rolling(momentum_n, min_periods=1).max()
        - bias36_centered.rolling(momentum_n, min_periods=1).min()
        + epsilon
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
    df["swing_index"] = 50.0 * si_move / (si_r + epsilon) * si_k / (si_m + epsilon)


    close_diff = df["Close"].diff()
    close_up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    close_down = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    close_up_sum = close_up.rolling(momentum_n, min_periods=1).sum()
    close_down_sum = close_down.rolling(momentum_n, min_periods=1).sum()
    df["rsi_v2"] = close_up_sum / (close_up_sum + close_down_sum + epsilon)

    cmo_up = close_up.rolling(momentum_n, min_periods=1).sum()
    cmo_down = close_down.rolling(momentum_n, min_periods=1).sum()
    df["cmo_v2"] = (cmo_up - cmo_down) / (cmo_up + cmo_down + epsilon)

    bias_fast = df["Close"].rolling(max(1, momentum_n // 2), min_periods=1).mean()
    bias_slow = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["bias_v13"] = (bias_fast / (bias_slow + epsilon) - 1.0).rolling(momentum_n, min_periods=1).mean()

    df["abs_chg"] = df["Close"].pct_change(momentum_n).abs()

    stc_fast = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    stc_slow = df["Close"].ewm(span=2 * momentum_n, adjust=False).mean()
    stc_macd = stc_fast - stc_slow
    stc_low_1 = stc_macd.rolling(2 * momentum_n, min_periods=1).min()
    stc_high_1 = stc_macd.rolling(2 * momentum_n, min_periods=1).max()
    fk = (stc_macd - stc_low_1) / (stc_high_1 - stc_low_1 + epsilon) * 100.0
    fd = fk.rolling(2 * momentum_n, min_periods=1).mean()
    stc_low_2 = fd.rolling(2 * momentum_n, min_periods=1).min()
    stc_high_2 = fd.rolling(2 * momentum_n, min_periods=1).max()
    sk = (fd - stc_low_2) / (stc_high_2 - stc_low_2 + epsilon) * 100.0
    df["stc"] = sk.rolling(momentum_n, min_periods=1).mean()


    return_ac = df["Close"].pct_change().rolling(momentum_n, min_periods=2).corr(df["Close"].pct_change().shift(1))
    df["return_autocorr_2"] = return_ac

    er_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    df["erbull"] = (df["High"] - er_ema) / (er_ema + epsilon)
    df["erbear"] = (df["Low"] - er_ema) / (er_ema + epsilon)
    df["er_balance"] = df["erbull"] + df["erbear"]

    df["burr"] = (
        (1.0 - df["Close"] / (df["High"].rolling(momentum_n, min_periods=1).max() + epsilon)).where(
            df["Close"] - df["Open"].shift(momentum_n) > 0
        ).fillna(0.0)
        + (1.0 - df["Close"] / (df["Low"].rolling(momentum_n, min_periods=1).min() + epsilon)).where(
            df["Close"] - df["Open"].shift(momentum_n) < 0
        ).fillna(0.0)
    )

    df = df.copy()

    mid_price = (df["High"] + df["Low"]) / 2.0
    macd_v2_ema1 = mid_price.ewm(span=momentum_n, adjust=False).mean()
    macd_v2_ema2 = mid_price.ewm(span=2 * momentum_n, adjust=False).mean()
    macd_v2_dif = macd_v2_ema1 - macd_v2_ema2
    macd_v2_dea = macd_v2_dif.ewm(span=max(1, int(momentum_n / 2)), adjust=False).mean()
    df["macd_v2"] = 10.0 * (2.0 * macd_v2_dif - macd_v2_dea)

    ppo_v1_ema1 = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    ppo_v1_ema2 = df["Close"].ewm(span=2 * momentum_n, adjust=False).mean()
    ppo_v1_base = (ppo_v1_ema1 / (ppo_v1_ema1.shift(momentum_n) + epsilon) - 1.0) * (
        (ppo_v1_ema2 / (ppo_v1_ema2.shift(2 * momentum_n) + epsilon) - 1.0).abs()
    )
    df["ppo_v1"] = ppo_v1_base.ewm(span=momentum_n, adjust=False).mean()

    sroc_v2_kama = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    sroc_v2_ref = sroc_v2_kama.shift(2 * momentum_n)
    df["sroc_v2"] = (sroc_v2_kama - sroc_v2_ref) / (sroc_v2_ref + epsilon)

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
    fisher_base = 2.0 * ((fisher_price - fisher_min_low) / (fisher_max_high - fisher_min_low + epsilon) - 0.5)
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
    df["arbr_ar"] = 100.0 * arbr_ar_up / (arbr_ar_dn + epsilon)

    arbr_br_up = (df["High"] - df["Close"].shift(1)).rolling(momentum_n, min_periods=1).sum()
    arbr_br_dn = (df["Close"].shift(1) - df["Low"]).rolling(momentum_n, min_periods=1).sum()
    df["arbr_br"] = 100.0 * arbr_br_up / (arbr_br_dn + epsilon)

    bias_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["bias_v3"] = np.log(df["Close"] / (bias_ma + epsilon)) / 0.03

    typical_bias_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    typical_bias_ma = typical_bias_price.rolling(momentum_n, min_periods=1).mean()
    df["bias_v4"] = typical_bias_price / (typical_bias_ma + epsilon) - 1.0

    quote_volume_proxy = df["Close"] * df["Volume"]
    quote_volume_mean = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean()
    bias_v11_base = (df["Close"] / (bias_ma + epsilon) - 1.0) * quote_volume_proxy / (quote_volume_mean + epsilon)
    df["bias_v11"] = bias_v11_base.ewm(span=momentum_n, adjust=False).mean()

    fast_bias_ma = df["Close"].rolling(max(1, momentum_n // 2), min_periods=1).mean()
    bias_v14_base = (fast_bias_ma / (bias_ma + epsilon) - 1.0) * quote_volume_proxy / (quote_volume_mean + epsilon)
    df["bias_v14"] = bias_v14_base.rolling(momentum_n, min_periods=1).mean()

    bias36_raw = df["Close"].rolling(b3, min_periods=1).mean() - df["Close"].rolling(b6, min_periods=1).mean()
    df["bias36ma"] = bias36_raw.rolling(momentum_n, min_periods=1).mean()

    four_price = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4.0
    four_price_max = four_price.rolling(momentum_n, min_periods=1).max()
    four_price_min = four_price.rolling(momentum_n, min_periods=1).min()
    bir_short = max(1, momentum_n // 3)
    bir_up_ref = four_price_max.shift(bir_short)
    bir_down_ref = four_price_min.shift(bir_short)
    bir_up = pd.Series(np.where(four_price > bir_up_ref, four_price, bir_up_ref), index=df.index)
    bir_down = pd.Series(np.where(four_price < bir_down_ref, four_price, bir_down_ref), index=df.index)
    bir_up = (bir_up - bir_up_ref) / (bir_up_ref + epsilon)
    bir_down = (bir_down - bir_down_ref) / (bir_down_ref + epsilon)
    df["bir"] = (bir_up + bir_down).rolling(bir_short, min_periods=1).mean()

    copp_v3_rc = 100.0 * (
        (df["Close"] - df["Close"].shift(momentum_n)) / (df["Close"].shift(momentum_n) + epsilon)
        + (df["Close"] - df["Close"].shift(max(1, int(1.618 * momentum_n))))
        / (df["Close"].shift(max(1, int(1.618 * momentum_n))) + epsilon)
    )
    df["copp_v3"] = copp_v3_rc.rolling(momentum_n, min_periods=1).mean()

    df = df.copy()

    close_diff = df["Close"].diff()
    up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    dn = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    rsi_raw = up.rolling(momentum_n, min_periods=1).sum() / (up.rolling(momentum_n, min_periods=1).sum() + dn.rolling(momentum_n, min_periods=1).sum() + epsilon)
    do_smooth = rsi_raw.ewm(span=momentum_n, adjust=False).mean().ewm(span=momentum_n, adjust=False).mean()
    df["do"] = do_smooth

    ema_short = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    ema_long = df["Close"].ewm(span=3 * momentum_n, adjust=False).mean()
    df["po"] = (ema_short - ema_long) / (ema_long + epsilon) * 100.0

    open_ma = df["Open"].rolling(momentum_n, min_periods=1).mean()
    high_ma = df["High"].rolling(momentum_n, min_periods=1).mean()
    low_ma = df["Low"].rolling(momentum_n, min_periods=1).mean()
    close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tp = (high_ma + low_ma + close_ma) / 3.0
    tp_ma = tp.rolling(momentum_n, min_periods=1).mean()
    md = (tp - close_ma).abs().rolling(momentum_n, min_periods=1).mean()
    df["cci_magic"] = (tp - tp_ma) / (0.015 * md + epsilon)

    quote_volume_proxy = df["Close"] * df["Volume"]
    c_mtm = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    c_mtm = c_mtm.rolling(momentum_n, min_periods=1).mean()
    s_std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    s_mtm = (s_std / s_std.shift(momentum_n)).rolling(momentum_n, min_periods=1).mean()
    v_mtm = (quote_volume_proxy / (quote_volume_proxy.shift(momentum_n) + epsilon)).rolling(momentum_n, min_periods=1).mean()
    df["cs_mtm"] = c_mtm * s_mtm * v_mtm

    c_mtm_v2 = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    c_mtm_v2 = c_mtm_v2.rolling(momentum_n, min_periods=1).mean()
    s_std_v2 = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    s_mtm_v2 = (s_std_v2 / (s_std_v2.shift(momentum_n) + epsilon)).rolling(momentum_n, min_periods=1).mean()
    v_mtm_v2 = (quote_volume_proxy / (quote_volume_proxy.shift(momentum_n) + epsilon)).rolling(momentum_n, min_periods=1).mean()
    df["cs_mtm_v2"] = c_mtm_v2 * s_mtm_v2 * v_mtm_v2

    mtm_v12 = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0
    taker_buy_quote_asset_volume = pd.Series(np.where(df["Close"] > df["Close"].shift(1), quote_volume_proxy, 0.0), index=df.index)
    taker_buy_quote_mean = taker_buy_quote_asset_volume.rolling(window=momentum_n, min_periods=1).mean()
    mtm_v12 = mtm_v12 * taker_buy_quote_asset_volume / (taker_buy_quote_mean + epsilon)
    df["mtmmean_v12"] = mtm_v12.rolling(window=momentum_n, min_periods=1).mean()





    close_dif = df["Close"].diff()
    up = pd.Series(np.where(close_dif > 0, close_dif, 0.0), index=df.index)
    down = pd.Series(np.where(close_dif < 0, -close_dif, 0.0), index=df.index)
    a = up.rolling(momentum_n, min_periods=1).sum()
    b = down.rolling(momentum_n, min_periods=1).sum()
    rsi = 100.0 * a / (a + b + epsilon)
    median = df["Close"].rolling(momentum_n, min_periods=1).mean()
    std = df["Close"].rolling(momentum_n, min_periods=1).std(ddof=0)
    bbw = (std / (median + epsilon)).diff(momentum_n)
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
    df["bias_vol"] = (df["Volume"] - ma_volume) / (ma_volume + epsilon)

    ma_1 = df["Close"].rolling(max(1, momentum_n // 2), min_periods=1).mean()
    ma_2 = df["Close"].rolling(momentum_n, min_periods=1).mean()
    ma_3 = df["Close"].rolling(2 * momentum_n, min_periods=1).mean()
    bias_1 = df["Close"] / (ma_1 + epsilon) - 1.0
    bias_2 = df["Close"] / (ma_2 + epsilon) - 1.0
    bias_3 = df["Close"] / (ma_3 + epsilon) - 1.0
    quote_volume_proxy = df["Close"] * df["Volume"]
    df["bias_cubic_v2"] = (bias_1 * bias_2 * bias_3) * (quote_volume_proxy / (quote_volume_proxy.rolling(momentum_n, min_periods=1).mean() + epsilon)).rolling(momentum_n, min_periods=1).mean()

    route_1 = (df["High"] - df["Open"]) + (df["High"] - df["Low"]) + (df["Close"] - df["Low"])
    route_2 = (df["Open"] - df["Low"]) + (df["High"] - df["Low"]) + (df["High"] - df["Close"])
    min_route = pd.concat([route_1, route_2], axis=1).min(axis=1) / (df["Open"] + epsilon)
    rc_copp = 100.0 * (df["Close"] / df["Close"].shift(momentum_n) - 1.0 + df["Close"] / df["Close"].shift(2 * momentum_n) - 1.0)
    rc_copp = rc_copp.ewm(span=momentum_n, adjust=False).mean()
    min_route = min_route.ewm(span=momentum_n, adjust=False).mean()
    df["copp_min_route"] = rc_copp / (min_route + epsilon)



    open_prev = df["Open"].shift(1)
    tmp1 = df["High"] - df["Open"]
    tmp2 = df["Open"] - open_prev
    tmp3 = df["Open"] - df["Low"]
    tmp4 = open_prev - df["Open"]
    dtm = pd.Series(np.where(df["Open"] > open_prev, np.maximum(tmp1, tmp2), 0.0), index=df.index)
    dbm = pd.Series(np.where(df["Open"] < open_prev, np.maximum(tmp3, tmp4), 0.0), index=df.index)
    stm = dtm.rolling(momentum_n, min_periods=1).sum()
    sbm = dbm.rolling(momentum_n, min_periods=1).sum()
    adtm_base = (stm - sbm) / (pd.concat([stm, sbm], axis=1).max(axis=1) + epsilon)
    df["adtm_v2"] = (adtm_base - adtm_base.rolling(momentum_n, min_periods=1).min()) / (
        adtm_base.rolling(momentum_n, min_periods=1).max() - adtm_base.rolling(momentum_n, min_periods=1).min() + epsilon
    )

    adtm_v3_base = adtm_base - df["Close"] / (adtm_base + epsilon)
    df["adtm_v3"] = (adtm_v3_base - adtm_v3_base.rolling(momentum_n, min_periods=1).min()) / (
        adtm_v3_base.rolling(momentum_n, min_periods=1).max() - adtm_v3_base.rolling(momentum_n, min_periods=1).min() + epsilon
    )

    mtm_gap = df["Close"].pct_change(momentum_n)
    body_gap = 1.0 - (df["Close"] - df["Open"]).abs() / (df["High"] - df["Low"] + epsilon)
    df["mtm_mean_gap"] = mtm_gap.rolling(momentum_n, min_periods=1).mean() / (
        body_gap.rolling(momentum_n, min_periods=1).mean() + epsilon
    )




    close_diff = df["Close"].diff()
    cmo_up = pd.Series(np.where(close_diff > 0, close_diff, 0.0), index=df.index)
    cmo_dn = pd.Series(np.where(close_diff < 0, -close_diff, 0.0), index=df.index)
    cmo_up_sum = cmo_up.rolling(momentum_n, min_periods=1).sum()
    cmo_dn_sum = cmo_dn.rolling(momentum_n, min_periods=1).sum()
    cmo_v3_raw = 100.0 * (cmo_up_sum - cmo_dn_sum) / (cmo_up_sum + cmo_dn_sum + epsilon)
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
    quote_volume_change_mean = (quote_volume_proxy / (quote_volume_mean + epsilon)).rolling(momentum_n, min_periods=1).mean()
    df["mtm_vol_resonance"] = mtm_resonance * quote_volume_change_mean



    tii_close_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tii_dev = df["Close"] - tii_close_ma
    tii_dev_pos = pd.Series(np.where(tii_dev > 0, tii_dev, 0.0), index=df.index)
    tii_dev_neg = pd.Series(np.where(tii_dev < 0, -tii_dev, 0.0), index=df.index)
    tii_sum_pos = tii_dev_pos.rolling(int(1 + momentum_n / 2), min_periods=1).sum()
    tii_sum_neg = tii_dev_neg.rolling(int(1 + momentum_n / 2), min_periods=1).sum()
    tii_raw = 100.0 * tii_sum_pos / (tii_sum_pos + tii_sum_neg + epsilon)
    tii_signal = tii_raw.ewm(span=max(1, int(momentum_n / 2)), adjust=False, min_periods=1).mean()
    df["tii_signal"] = tii_signal
    tii_signal_diff = tii_raw - tii_signal
    tii_signal_diff_min = tii_signal_diff.rolling(momentum_n, min_periods=1).min()
    tii_signal_diff_max = tii_signal_diff.rolling(momentum_n, min_periods=1).max()
    df["tii_signal_v2"] = (tii_signal_diff - tii_signal_diff_min) / (1e-9 + tii_signal_diff_max - tii_signal_diff_min)

    df["roc"] = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0

    open_wma = df["Open"].rolling(momentum_n, min_periods=1).mean()
    high_wma = df["High"].rolling(momentum_n, min_periods=1).mean()
    low_wma = df["Low"].rolling(momentum_n, min_periods=1).mean()
    close_wma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tp_v2 = (open_wma + high_wma + low_wma + close_wma) / 4.0
    ma_v2 = tp_v2.rolling(momentum_n, min_periods=1).mean()
    md_v2 = (ma_v2 - close_wma).abs().rolling(momentum_n, min_periods=1).mean()
    df["cci_v2"] = (tp_v2 - ma_v2) / (md_v2 + epsilon)

    open_ema = df["Open"].ewm(span=momentum_n, adjust=False).mean()
    high_ema = df["High"].ewm(span=momentum_n, adjust=False).mean()
    low_ema = df["Low"].ewm(span=momentum_n, adjust=False).mean()
    close_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    tp_v3 = (open_ema + high_ema + low_ema + close_ema) / 4.0
    ma_v3 = tp_v3.ewm(span=momentum_n, adjust=False).mean()
    md_v3 = (close_ema - ma_v3).abs().ewm(span=momentum_n, adjust=False).mean()
    df["cci_v3"] = (tp_v3 - ma_v3) / (md_v3 + epsilon)

    close_dif = df["Close"].diff()
    up = pd.Series(np.where(close_dif > 0, close_dif, 0.0), index=df.index)
    down = pd.Series(np.where(close_dif < 0, -close_dif, 0.0), index=df.index)
    rsi_num = up.rolling(momentum_n, min_periods=1).sum()
    rsi_den = up.rolling(momentum_n, min_periods=1).sum() + down.rolling(momentum_n, min_periods=1).sum() + epsilon
    df["rsimean"] = (rsi_num / rsi_den).rolling(momentum_n, min_periods=1).mean()

    price_change = df["Close"].pct_change(momentum_n).to_numpy(dtype=float)
    amplitude = (df["High"] / df["Low"] - 1.0).to_numpy(dtype=float)

    def quiet_moment(window: int) -> np.ndarray:
        out = np.full(len(df), np.nan)
        keep = max(1, int(window * 0.7))
        for i in range(len(df)):
            start = max(0, i - window + 1)
            amps = amplitude[start : i + 1]
            rets = price_change[start : i + 1]
            valid = ~(np.isnan(amps) | np.isnan(rets))
            if not valid.any():
                continue
            amps = amps[valid]
            rets = rets[valid]
            order = np.argsort(amps)
            out[i] = rets[order[: min(keep, len(order))]].sum()
        return out

    df["short_moment"] = quiet_moment(momentum_n)
    df["long_moment"] = quiet_moment(momentum_n * 10)

    df = df.copy()

    close_dif = df["Close"].diff()
    close_up = pd.Series(np.where(close_dif > 0, close_dif, 0.0), index=df.index)
    close_down = pd.Series(np.where(close_dif < 0, -close_dif, 0.0), index=df.index)
    up_sum = close_up.ewm(alpha=1 / (4 * momentum_n), adjust=False).mean()
    down_sum = close_down.ewm(alpha=1 / (4 * momentum_n), adjust=False).mean()
    rsi = 100.0 * up_sum / (1e-9 + down_sum)
    rsi_min = rsi.rolling(int(4 * momentum_n), min_periods=1).min()
    rsi_max = rsi.rolling(int(4 * momentum_n), min_periods=1).max()
    df["rsis"] = 100.0 * (rsi - rsi_min) / (1e-9 + rsi_max - rsi_min)

    pmar = (df["Close"] / (df["Close"].rolling(momentum_n, min_periods=1).mean() + epsilon)).abs()
    pmar_arr = pmar.to_numpy(dtype=float)
    out = np.full(len(df), np.nan)
    for i in range(len(df)):
        start = max(0, i - momentum_n + 1)
        window = pmar_arr[start : i + 1]
        window = window[~np.isnan(window)]
        if window.size == 0 or np.isnan(pmar_arr[i]):
            continue
        out[i] = (window < pmar_arr[i]).sum() / momentum_n * 100.0
    df["pmarp_yidai_v1"] = out

    bias_series = 100.0 * (df["Close"] - df["Close"].rolling(momentum_n, min_periods=1).mean()) / (df["Close"].rolling(momentum_n, min_periods=1).mean() + epsilon)
    bias_dif = bias_series - bias_series.shift(int(3 * momentum_n + 1))
    df["dbcd_v2"] = bias_dif.ewm(alpha=1 / (3 * momentum_n + 2), adjust=False).mean()

    m = 0.5 * df["High"].rolling(momentum_n, min_periods=1).max() + 0.5 * df["Low"].rolling(momentum_n, min_periods=1).min()
    d = df["Close"] - m
    ds = d.ewm(span=momentum_n, adjust=False, min_periods=1).mean().ewm(span=momentum_n, adjust=False, min_periods=1).mean()
    dhl = (df["High"].rolling(momentum_n, min_periods=1).max() - df["Low"].rolling(momentum_n, min_periods=1).min()).ewm(span=momentum_n, adjust=False, min_periods=1).mean().ewm(span=momentum_n, adjust=False, min_periods=1).mean()
    smi = 100.0 * ds / (dhl + epsilon)
    smi_mean = smi.rolling(momentum_n, min_periods=1).mean()
    smi_low = smi_mean.rolling(momentum_n, min_periods=1).min()
    smi_high = smi_mean.rolling(momentum_n, min_periods=1).max()
    df["smi_v2"] = (smi_mean - smi_low) / (1e-9 + smi_high - smi_low)

    bias = 100.0 * (df["Close"] - df["Close"].rolling(momentum_n, min_periods=1).mean()) / (df["Close"].rolling(momentum_n, min_periods=1).mean() + epsilon)
    bias_dif = bias - bias.shift(3 * momentum_n)
    t = 3 * momentum_n + 2
    out = np.zeros(len(df), dtype=float)
    vals = bias_dif.fillna(0.0).to_numpy(dtype=float)
    for i, v in enumerate(vals):
        if i == 0:
            out[i] = v
        else:
            r = 1 / t
            out[i] = r * v + (1 - r) * out[i - 1]
    df["dbcd_v3"] = out

    mi = df["Close"] - df["Close"].shift(1)
    mimma = mi.rolling(momentum_n, min_periods=1).mean()
    mimma_ma1 = mimma.shift(1).rolling(momentum_n, min_periods=1).mean()
    mimma_ma2 = mimma.shift(1).rolling(2 * momentum_n, min_periods=1).mean()
    dif = mimma_ma1 - mimma_ma2
    df["micd"] = dif / (dif.rolling(momentum_n, min_periods=1).mean() + epsilon)

    ret = df["Close"] / df["Close"].shift(1) - 1.0
    rv = ret.pow(2).rolling(momentum_n, min_periods=1).sum()
    rv_pos = np.where(ret > 0, ret, 0.0)
    rv_neg = np.where(ret < 0, ret, 0.0)
    rv_plus = pd.Series(rv_pos, index=df.index).pow(2).rolling(momentum_n, min_periods=1).sum()
    rv_minus = pd.Series(rv_neg, index=df.index).pow(2).rolling(momentum_n, min_periods=1).sum()
    df["rsj"] = (rv_plus - rv_minus) / (rv + epsilon)

    mtm = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    df["mtm_max"] = mtm - mtm.rolling(window=momentum_n, min_periods=1).max().shift(1)

    reg_close = df["Close"].rolling(momentum_n, min_periods=1).mean()
    reg_close = reg_close.rolling(momentum_n, min_periods=1).mean()
    quote_proxy = ((df["High"] + df["Low"]) / 2.0) * df["Volume"]
    df["bias_v2"] = quote_proxy / (reg_close + epsilon) - 1.0

    vol_up = pd.Series(np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    vol_down = pd.Series(np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    sum_up = vol_up.rolling(momentum_n, min_periods=1).sum()
    sum_down = vol_down.rolling(momentum_n, min_periods=1).sum()
    df["rsiv"] = 100.0 * sum_up / (sum_up + sum_down + epsilon)

    close_diff_pos = np.where(df["Close"] > df["Close"].shift(1), df["Close"] - df["Close"].shift(1), 0.0)
    rsi_fast = pd.Series(close_diff_pos, index=df.index).ewm(span=momentum_n, adjust=False).mean()
    rsi_slow = (df["Close"] - df["Close"].shift(1)).abs().ewm(span=momentum_n, adjust=False).mean()
    rsi = 100.0 * rsi_fast / (rsi_slow + epsilon)
    rsi_signal = rsi.ewm(span=4 * momentum_n, adjust=False).mean()
    df["rsih"] = rsi - rsi_signal

    close_diff = df["Close"].diff()
    fi = df["Volume"] * close_diff
    fi_z = (fi - fi.rolling(momentum_n, min_periods=1).mean()) / (fi.rolling(momentum_n, min_periods=1).std(ddof=0) + epsilon)
    df["fi"] = fi_z.ewm(span=momentum_n, adjust=False, min_periods=1).mean()

    fi_rsi_pos = pd.Series(np.where(fi.diff() > 0, fi.diff(), 0.0), index=df.index)
    fi_rsi_neg = pd.Series(np.where(fi.diff() < 0, -fi.diff(), 0.0), index=df.index)
    fi_rsi_a = fi_rsi_pos.rolling(momentum_n, min_periods=1).sum()
    fi_rsi_b = fi_rsi_neg.rolling(momentum_n, min_periods=1).sum()
    df["fi_rsi"] = (fi_rsi_a / (fi_rsi_a + fi_rsi_b + epsilon)).ewm(span=momentum_n, adjust=False, min_periods=1).mean()

    volume_force = df["Volume"] * close_diff
    df["force"] = volume_force / (volume_force.rolling(momentum_n, min_periods=1).mean() + epsilon)

    price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    signed_volume = np.where(price > price.shift(1), df["Volume"], -df["Volume"])
    ko_ema1 = pd.Series(signed_volume, index=df.index).ewm(span=momentum_n, adjust=False).mean()
    ko_ema2 = pd.Series(signed_volume, index=df.index).ewm(span=int(momentum_n * 1.618), adjust=False).mean()
    ko = ko_ema1 - ko_ema2
    df["ko"] = (ko - ko.rolling(momentum_n, min_periods=1).min()) / (ko.rolling(momentum_n, min_periods=1).max() - ko.rolling(momentum_n, min_periods=1).min() + epsilon)

    av = pd.Series(np.where(df["Close"] > df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    bv = pd.Series(np.where(df["Close"] < df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    cv = pd.Series(np.where(df["Close"] == df["Close"].shift(1), df["Volume"], 0.0), index=df.index)
    avs = av.rolling(momentum_n, min_periods=1).sum()
    bvs = bv.rolling(momentum_n, min_periods=1).sum()
    cvs = cv.rolling(momentum_n, min_periods=1).sum()
    df["vramt"] = (avs + cvs / 2.0) / (bvs + cvs / 2.0 + epsilon)

    mtm = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    mtm_mean = mtm.rolling(window=momentum_n, min_periods=1).mean()

    c1 = df["High"] - df["Low"]
    c2 = (df["High"] - df["Close"].shift(1)).abs()
    c3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.Series(np.max(np.array([c1, c2, c3]), axis=0), index=df.index)
    atr = tr.rolling(window=momentum_n, min_periods=1).mean()
    avg_price = df["Close"].rolling(window=momentum_n, min_periods=1).mean()
    wd_atr = atr / (avg_price + epsilon)

    mtm_l = df["Low"] / (df["Low"].shift(momentum_n) + epsilon) - 1.0
    mtm_h = df["High"] / (df["High"].shift(momentum_n) + epsilon) - 1.0
    mtm_c = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0
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

    v1_v2 = mtm_mean * wd_atr * mtm_atr * mtm_atr_mean
    df["v1_v2"] = v1_v2

    median = v1_v2.rolling(window=momentum_n, min_periods=1).mean()
    std = v1_v2.rolling(window=momentum_n, min_periods=1).std(ddof=0)
    z_score = (v1_v2 - median).abs() / (std + epsilon)
    m1 = z_score.rolling(window=momentum_n, min_periods=1).max().shift(1)
    upper = median + std * m1
    lower = median - std * m1
    df["v1up_v2"] = upper - v1_v2
    df["v1dn_v2"] = lower - v1_v2

    mtm_v10 = df["Close"] / df["Close"].shift(momentum_n) - 1.0
    mtm_v10_vol = df["High"].rolling(momentum_n, min_periods=1).max() / df["Low"].rolling(momentum_n, min_periods=1).min() - 1.0
    mtm_v10_hourly = df["High"] / df["Low"] - 1.0
    mtm_v10_hourly_mean = mtm_v10_hourly.rolling(momentum_n, min_periods=1).mean()
    df["mtmmean_v10"] = mtm_v10.rolling(window=momentum_n, min_periods=1).mean() * (mtm_v10_vol + mtm_v10_hourly_mean)

    mtm_hcm = df["High"] / df["High"].shift(momentum_n) - 1.0
    mtm_hcm_mean = mtm_hcm.rolling(window=momentum_n, min_periods=1).mean()
    ma_close = df["Close"].rolling(momentum_n, min_periods=1).mean()
    cm = df["Close"] / (ma_close + epsilon)
    df["mtmhcm"] = (mtm_hcm_mean - cm) / (cm + epsilon)

    a = (df["High"] - df["Close"].shift(1)).abs()
    b = (df["Low"] - df["Close"].shift(1)).abs()
    c = (df["High"] - df["Low"].shift(1)).abs()
    d = (df["Close"].shift(1) - df["Open"].shift(1)).abs()
    k = pd.concat([a, b], axis=1).max(axis=1)
    m = (df["High"] - df["Low"]).rolling(momentum_n, min_periods=1).max()
    r1 = a + 0.5 * b + 0.25 * d
    r2 = b + 0.5 * a + 0.25 * d
    r3 = c + 0.25 * d
    r4 = pd.Series(np.where((a >= b) & (a >= c), r1, r2), index=df.index)
    r = pd.Series(np.where((c >= a) & (c >= b), r3, r4), index=df.index)
    df["si"] = 50.0 * (
        df["Close"] - df["Close"].shift(1)
        + (df["Close"].shift(1) - df["Open"].shift(1))
        + 0.5 * (df["Close"] - df["Open"])
    ) / (r + epsilon) * k / (m + epsilon)

    high_n = df["High"].rolling(momentum_n, min_periods=1).max()
    low_n = df["Low"].rolling(momentum_n, min_periods=1).min()
    df["wr"] = (high_n - df["Close"]) / (high_n - low_n + epsilon) * 100.0

    df["rocvol"] = df["Volume"] / (df["Volume"].shift(momentum_n) + epsilon) - 1.0

    mtm_v4 = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0
    df["mtmmean_v4"] = mtm_v4.rolling(momentum_n, min_periods=1).apply(_rolling_regression_last, raw=True)

    prev_close = df["Close"].shift(1)
    th = pd.concat([df["High"], prev_close], axis=1).max(axis=1)
    tl = pd.concat([df["Low"], prev_close], axis=1).min(axis=1)
    tr = th - tl
    xr = df["Close"] - tl
    uos_m = xr.rolling(momentum_n, min_periods=1).sum() / (tr.rolling(momentum_n, min_periods=1).sum() + epsilon)
    uos_n = xr.rolling(2 * momentum_n, min_periods=1).sum() / (tr.rolling(2 * momentum_n, min_periods=1).sum() + epsilon)
    uos_o = xr.rolling(4 * momentum_n, min_periods=1).sum() / (tr.rolling(4 * momentum_n, min_periods=1).sum() + epsilon)
    df["uos"] = 100.0 * (
        uos_m * (2 * momentum_n) * (4 * momentum_n)
        + uos_n * momentum_n * (4 * momentum_n)
        + uos_o * momentum_n * (2 * momentum_n)
    ) / (
        momentum_n * (2 * momentum_n)
        + momentum_n * (4 * momentum_n)
        + (2 * momentum_n) * (4 * momentum_n)
    )

    zl_ema1 = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    zl_ema2 = zl_ema1.ewm(span=momentum_n, adjust=False).mean()
    zl_dema1 = 2.0 * zl_ema1 - zl_ema2
    zl_ema3 = zl_dema1.ewm(span=5 * momentum_n, adjust=False).mean()
    zl_ema4 = zl_ema3.ewm(span=5 * momentum_n, adjust=False).mean()
    zl_dema2 = 2.0 * zl_ema3 - zl_ema4
    df["zlmacd"] = df["Close"] / (zl_dema1 - zl_dema2 + epsilon) - 1.0

    tma_bias_ma = df["Close"].rolling(momentum_n, min_periods=1).mean()
    tma_bias_tma = tma_bias_ma.rolling(momentum_n, min_periods=1).mean()
    df["tma_bias"] = df["Close"] / (tma_bias_tma + epsilon) - 1.0

    mtm_v8 = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0
    mtm_v8_vol = df["High"].rolling(momentum_n, min_periods=1).max() / (df["Low"].rolling(momentum_n, min_periods=1).min() + epsilon) - 1.0
    df["mtmmean_v8"] = mtm_v8.rolling(window=momentum_n, min_periods=1).mean() * mtm_v8_vol

    close_change = (df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0).ewm(span=momentum_n, adjust=False).mean() * 100.0
    quote_volume_proxy = df["Close"] * df["Volume"]
    vol_change = (quote_volume_proxy / (quote_volume_proxy.shift(momentum_n) + epsilon) - 1.0).ewm(span=momentum_n, adjust=False).mean() * 100.0
    df["mtmvolmean"] = close_change * vol_change

    df = df.copy()

    close_return = df["Close"].pct_change()
    df["autocorrelation"] = close_return.rolling(momentum_n, min_periods=2).corr(close_return.shift(1))

    copp_rc = 100.0 * (df["Close"].pct_change(momentum_n) + df["Close"].pct_change(2 * momentum_n))
    df["copp"] = copp_rc.rolling(momentum_n, min_periods=1).mean()

    demax = (df["High"] - df["High"].shift(1)).clip(lower=0.0)
    demin = (df["Low"].shift(1) - df["Low"]).clip(lower=0.0)
    df["demaker"] = demax.rolling(momentum_n, min_periods=1).mean() / (
        demax.rolling(momentum_n, min_periods=1).mean() + demin.rolling(momentum_n, min_periods=1).mean() + epsilon
    )

    er_ema = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    df["er"] = (df["High"] - er_ema) / (er_ema + epsilon) + (df["Low"] - er_ema) / (er_ema + epsilon)

    min_low = df["Low"].rolling(momentum_n).min()
    max_high = df["High"].rolling(momentum_n).max()
    stochastics = (df["Close"] - min_low) / (max_high - min_low + epsilon) * 100.0
    stochastics_low = stochastics.rolling(momentum_n * 3).min()
    stochastics_high = stochastics.rolling(momentum_n * 3).max()
    stochastics_double = (stochastics - stochastics_low) / (stochastics_high - stochastics_low + epsilon)
    df["kdjdk"] = stochastics_double.ewm(com=2).mean()
    df["kdjdd"] = df["kdjdk"].ewm(com=2).mean()

    rsv = (df["Close"] - df["Low"].rolling(momentum_n, min_periods=1).min()) / (
        df["High"].rolling(momentum_n, min_periods=1).max() - df["Low"].rolling(momentum_n, min_periods=1).min() + epsilon
    ) * 100.0
    mar_sv = rsv.ewm(com=2).mean()
    k = mar_sv.ewm(com=2).mean()
    df["skdj"] = k.rolling(3, min_periods=1).mean()

    oma = df["Open"].ewm(span=momentum_n, adjust=False).mean()
    hma = df["High"].ewm(span=momentum_n, adjust=False).mean()
    lma = df["Low"].ewm(span=momentum_n, adjust=False).mean()
    cma = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    tp = (oma + hma + lma + cma) / 4.0
    ma = tp.ewm(span=momentum_n, adjust=False).mean()
    md = (tp - ma).abs().ewm(span=momentum_n, adjust=False).mean()
    df["magiccci"] = (tp - ma) / (md + epsilon)

    hma2 = df["High"].ewm(span=momentum_n, adjust=False).mean()
    lma2 = df["Low"].ewm(span=momentum_n, adjust=False).mean()
    cma2 = df["Close"].ewm(span=momentum_n, adjust=False).mean()
    tp2 = (hma2 + lma2 + cma2) / 3.0
    ma2 = tp2.ewm(span=momentum_n, adjust=False).mean()
    md2 = (tp2 - ma2).abs().ewm(span=momentum_n, adjust=False).mean()
    df["magiccci_v2"] = (tp2 - ma2) / (md2 + epsilon)

    def range_plus(x, np_tmp, rolling_window, lam):
        li = df.index.get_indexer(x.index)
        np_tmp2 = np_tmp[li, :]
        np_tmp2 = np_tmp2[np.argsort(np_tmp2[:, 0])]
        t = int(rolling_window * lam)
        np_tmp2 = np_tmp2[:t, :]
        return np_tmp2[:, 1].sum()

    df["price_change"] = df["Close"].pct_change(momentum_n)
    df["amplitude"] = (df["High"] / df["Low"]) - 1.0
    np_tmp = df[["amplitude", "price_change"]].values
    df["short_moment"] = df["price_change"].rolling(momentum_n).apply(range_plus, args=(np_tmp, momentum_n, 0.7), raw=False)
    df["long_moment"] = df["price_change"].rolling(momentum_n * 10).apply(range_plus, args=(np_tmp, momentum_n * 10, 0.7), raw=False)


    mtm = df["Close"] / (df["Close"].shift(momentum_n) + epsilon) - 1.0
    volatility = df["High"].rolling(momentum_n, min_periods=1).max() / (df["Low"].rolling(momentum_n, min_periods=1).min() + epsilon) - 1.0
    hourly_volatility = (df["High"] / (df["Low"] + epsilon) - 1.0).rolling(momentum_n, min_periods=1).mean()
    df["mtmmean_v10"] = mtm.rolling(window=momentum_n, min_periods=1).mean() * (volatility + hourly_volatility)

    # --- Indicator features used by signal.py ---

    stochrsi_param = config.classic_indicators.get("STOCHRSI", 14)
    stochrsi_len = stochrsi_param[0] if isinstance(stochrsi_param, list) else int(stochrsi_param)
    rolling_max_rsi = df["rsi_medium"].rolling(stochrsi_len).max()
    rolling_min_rsi = df["rsi_medium"].rolling(stochrsi_len).min()
    df["stoch_rsi"] = (df["rsi_medium"] - rolling_min_rsi) / (rolling_max_rsi - rolling_min_rsi).replace(0, np.nan)

    ao_params = config.classic_indicators.get("AO", [5, 34])
    ao_fast, ao_slow = ao_params[0], ao_params[1]
    typical_price_ao = (df["High"] + df["Low"] + df["Close"]) / 3.0
    df["awesome_oscillator"] = typical_price_ao.rolling(ao_fast).mean() - typical_price_ao.rolling(ao_slow).mean()

    df["roc_short"] = ta.roc(df["Close"], length=config.short_lookback)

    prev_close_uo_fixed = df["Close"].shift(1)
    uo_buying_pressure = df["Close"] - np.minimum(df["Low"], prev_close_uo_fixed)
    uo_true_range = np.maximum(df["High"], prev_close_uo_fixed) - np.minimum(df["Low"], prev_close_uo_fixed)
    uo_params = config.classic_indicators.get("UO", [7, 14, 28])
    uo_p1, uo_p2, uo_p3 = uo_params[0], uo_params[1], uo_params[2]
    bp7 = uo_buying_pressure.rolling(uo_p1).sum()
    bp14 = uo_buying_pressure.rolling(uo_p2).sum()
    bp28 = uo_buying_pressure.rolling(uo_p3).sum()
    tr7 = uo_true_range.rolling(uo_p1).sum()
    tr14 = uo_true_range.rolling(uo_p2).sum()
    tr28 = uo_true_range.rolling(uo_p3).sum()
    df["ultimate_osc"] = 100 * ((4 * (bp7 / tr7.replace(0, np.nan))) + (2 * (bp14 / tr14.replace(0, np.nan))) + (bp28 / tr28.replace(0, np.nan))) / 7

    stochrsi_params = config.classic_indicators.get("STOCHRSI", [14, 14, 3, 3])
    if isinstance(stochrsi_params, list):
        s_len = stochrsi_params[0]
        s_rsi_len = stochrsi_params[1] if len(stochrsi_params) > 1 else s_len
        s_k = stochrsi_params[2] if len(stochrsi_params) > 2 else 3
        s_d = stochrsi_params[3] if len(stochrsi_params) > 3 else 3
    else:
        s_len = s_rsi_len = int(stochrsi_params)
        s_k = s_d = 3
    stochrsi_res = ta.stochrsi(df["Close"], length=s_len, rsi_length=s_rsi_len, k=s_k, d=s_d)
    if stochrsi_res is not None and not stochrsi_res.empty:
        df["stochrsi_k"] = stochrsi_res.iloc[:, 0]
        df["stochrsi_d"] = stochrsi_res.iloc[:, 1]
    else:
        df["stochrsi_k"] = np.nan
        df["stochrsi_d"] = np.nan

    willr_param = config.classic_indicators.get("WILLIAMS_R", 14)
    willr_len = willr_param[0] if isinstance(willr_param, list) else int(willr_param)
    williams_r = ta.willr(df["High"], df["Low"], df["Close"], length=willr_len)
    df["williams_r_14"] = williams_r if williams_r is not None else np.nan
    bbands = ta.bbands(df["Close"], length=config.medium_lookback, std=2.0)
    if bbands is not None and not bbands.empty:
        bbp_cols = [col for col in bbands.columns if col.startswith("BBP_")]
        df["bb_percent_b_medium_2"] = bbands[bbp_cols[0]] if bbp_cols else np.nan
    else:
        df["bb_percent_b_medium_2"] = np.nan
    macd_12_26_9 = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
    if macd_12_26_9 is not None and not macd_12_26_9.empty:
        macdh_cols = [col for col in macd_12_26_9.columns if "MACDh" in col]
        df["macd_hist_12_26_9"] = macd_12_26_9[macdh_cols[0]] if macdh_cols else np.nan
    else:
        df["macd_hist_12_26_9"] = np.nan

    return df
