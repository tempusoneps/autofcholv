import numpy as np
import pandas as pd
EPS = 1e-8
import pandas_ta as ta
from autofcholv.config.config import Config
from autofcholv.utils.indicators import get_atr, get_rolling_vwap


def _wma(series: pd.Series, k: int) -> pd.Series:
    weights = np.arange(1, k + 1, dtype=float)
    return series.rolling(k, min_periods=1).apply(lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum(), raw=True)


def _sma(series: pd.Series, k: int) -> pd.Series:
    return series.rolling(k, min_periods=1).mean()


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate mixed/combined features.
    Feature definitions follow mix.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    cols = ['body_lag1', 'open_lag1', 'close_lag1', 'high_lag1', 'low_lag1', 'volume_lag1', 'ibs', 'ibs_lag1']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    ibs_n        = config.ibs_lookback
    volatility_n = config.volatility_lookback
    one_day_bars = config.one_day_bars

    rolling_low  = df["Low"].rolling(ibs_n).min()
    rolling_high = df["High"].rolling(ibs_n).max()
    denom        = rolling_high - rolling_low
    df["ibs_n"]  = np.where(denom != 0, (df["Close"] - rolling_low) / denom, np.nan)

    high_lag2    = df["High"].shift(2)
    low_lag2     = df["Low"].shift(2)
    df["is_fvg"] = (high_lag2 < df["Low"]) | (low_lag2 > df["High"])

    ulti = ta.uo(df["High"], df["Low"], df["Close"], fast=volatility_n // 2,
                 medium=volatility_n, slow=volatility_n * 2)
    if ulti is not None and not ulti.empty:
        df["ulti_osci"] = ulti.values

    vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
    if vwap is not None and not vwap.empty:
        df["vwap"] = vwap.values

    atr = get_atr(df, config.medium_lookback)
    df["atr_medium"] = atr
    df["atr_pct_medium"] = df["atr_medium"] / df["Close"]

    adx_result = ta.adx(df["High"], df["Low"], df["Close"], length=volatility_n)
    if adx_result is not None and not adx_result.empty:
        df["adx"] = adx_result.iloc[:, 0].values

    midpoint = (df["High"] + df["Low"]) / 2
    df["dm"] = midpoint - midpoint.shift(1)

    df["eom"] = np.where(df["vbr"] != 0, df["dm"] / df["vbr"], np.nan)

    df["direction"] = np.where(df["Close"] > df["Open"], 1, -1)

    direction = df["direction"].to_numpy()
    streak    = np.zeros(len(direction), dtype=int)
    for i in range(1, len(direction)):
        if direction[i] == direction[i - 1]:
            streak[i] = direction[i] + streak[i - 1]
        else:
            streak[i] = 0
    df["streak"] = streak

    prev_day_close   = df["Close"].shift(one_day_bars)
    prev_close_price = df["Close"].shift(1)
    df["custom_001"] = 100 * (df["Close"] - prev_day_close) / prev_day_close
    df["custom_002"] = (df["Close"] - prev_day_close) / (
        df["High"].rolling(one_day_bars).max() - df["Low"].rolling(one_day_bars).min()
    )

    donchian_high = df["High"].rolling(volatility_n).max()
    donchian_low  = df["Low"].rolling(volatility_n).min()
    donchian_mid  = (donchian_high + donchian_low) / 2
    df["donchian_width"]    = (donchian_high - donchian_low) / (donchian_mid + 1e-8)
    df["donchian_position"] = (df["Close"] - donchian_low) / (donchian_high - donchian_low + 1e-8)

    volume_proxy = df["Volume"] * df["Close"]
    df["amihud_liquidity"] = (
        (df["Close"].pct_change().abs() / (volume_proxy + 1e-8))
        .rolling(volatility_n)
        .mean()
    )

    true_range = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev_close_price).abs(),
        (df["Low"]  - prev_close_price).abs(),
    ], axis=1).max(axis=1)

    prev_close = df["Close"].shift(1)
    df["true_range_pct"] = true_range / df["Close"]
    df["gap_pct"] = (df["Open"] - prev_close) / prev_close
    df["range_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-8)
    df["body_to_true_range"] = df["body"].abs() / (true_range + 1e-8)

    keltner_middle = df["Close"].ewm(span=volatility_n, adjust=False, min_periods=1).mean()
    keltner_range = 4.0 * df["atr_medium"]
    df["keltner_position"] = np.where(
        keltner_range != 0,
        (df["Close"] - keltner_middle + 2.0 * df["atr_medium"]) / keltner_range,
        np.nan,
    )

    c1 = df["High"] - df["Low"]
    c2 = (df["High"] - df["Close"].shift(1)).abs()
    c3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([c1, c2, c3], axis=1).max(axis=1)
    sma = _sma(df["Close"], volatility_n)
    str_ = tr / (sma + 1e-8)
    tr_up = np.where(df["Close"] > df["Close"].shift(1), str_, 0.0)
    tr_dn = np.where(df["Close"] < df["Close"].shift(1), str_, 0.0)
    wmatr_up_1 = _wma(pd.Series(tr_up, index=df.index), volatility_n)
    wmatr_dn_1 = _wma(pd.Series(tr_dn, index=df.index), volatility_n)
    wmatr_up_2 = _wma(pd.Series(tr_up, index=df.index), 2 * volatility_n)
    wmatr_dn_2 = _wma(pd.Series(tr_dn, index=df.index), 2 * volatility_n)
    fast_diff = wmatr_up_1 - wmatr_dn_1
    slow_diff = wmatr_up_2 - wmatr_dn_2
    fast_minus_slow = fast_diff - slow_diff
    df["fear_greed_yidai_v1"] = _wma(pd.Series(fast_minus_slow, index=df.index), volatility_n)

    rc = 100.0 * ((df["Close"] - df["Close"].shift(volatility_n)) / (df["Close"].shift(volatility_n) + 1e-8) + (df["Close"] - df["Close"].shift(2 * volatility_n)) / (df["Close"].shift(2 * volatility_n) + 1e-8))
    rc_mean = rc.rolling(volatility_n, min_periods=1).mean()
    median = df["Close"].rolling(volatility_n, min_periods=1).mean()
    std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    z_score = (df["Close"] - median).abs() / (std + 1e-8)
    m = z_score.rolling(volatility_n, min_periods=1).mean()
    bbw = std * m * 2.0 / (median + 1e-8)
    bbw_mean = bbw.rolling(volatility_n, min_periods=1).mean()
    c1 = df["High"] - df["Low"]
    c2 = (df["High"] - df["Close"].shift(1)).abs()
    c3 = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([c1, c2, c3], axis=1).max(axis=1)
    atr = tr.rolling(volatility_n, min_periods=1).mean()
    df["damaov10"] = rc_mean * bbw_mean * (atr / (median + 1e-8))

    up_move = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    down_move = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    xpdm = np.where(up_move > down_move, df["High"] - df["High"].shift(1), 0.0)
    pdm = pd.Series(xpdm, index=df.index).rolling(volatility_n, min_periods=1).sum()
    tr = pd.concat([
        (df["High"] - df["Low"]).abs(),
        (df["High"] - df["Close"]).abs(),
        (df["Low"] - df["Close"]).abs(),
    ], axis=1).max(axis=1)
    tr_sum = tr.rolling(volatility_n, min_periods=1).sum()
    di_plus = pdm / (tr_sum + 1e-8)
    mtm = (df["Close"] / (df["Close"].shift(volatility_n) + 1e-8) - 1.0).rolling(window=volatility_n, min_periods=1).mean()
    cvr_n = volatility_n
    pc = df["Close"].pct_change()
    vol = pc.rolling(cvr_n).std()
    ret = pc.rolling(cvr_n).sum()
    cvr = (ret / (vol + 1e-8)) * (df["Close"] * df["Volume"] / ((df["Close"] * df["Volume"]).rolling(cvr_n, min_periods=1).mean()))
    df["cvr_v0"] = cvr.rolling(cvr_n, min_periods=1).mean()

    rc = 100.0 * (
        (df["Close"] - df["Close"].shift(volatility_n)) / (df["Close"].shift(volatility_n) + 1e-8)
        + (df["Close"] - df["Close"].shift(2 * volatility_n)) / (df["Close"].shift(2 * volatility_n) + 1e-8)
    )
    rc = rc.rolling(volatility_n, min_periods=1).mean()
    median = df["Close"].rolling(volatility_n, min_periods=1).mean()
    std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    bbw = std / (median + 1e-8)
    corr = df["Close"].rolling(volatility_n).corr(df["Volume"]).fillna(0.0) + 1.0
    corr = corr.rolling(volatility_n, min_periods=1).mean()
    df["cbr_v1"] = rc * bbw * corr

    params = [5, 8, 13, 21, 34, 55, 89]
    fbnq_mean = 0.0
    bbw_ori = 0.0
    for pn in params:
        fbnq_mean += df["Close"].ewm(span=pn, adjust=False).mean()
        bbw_ori += df["Close"].rolling(volatility_n).std(ddof=0) / df["Close"].rolling(volatility_n, min_periods=1).mean()
    fbnq_mean = fbnq_mean / len(params)
    fbnq_mean = fbnq_mean.pct_change(volatility_n)
    bbw_ori = bbw_ori / len(params)
    df["fbnq_pct_v5"] = fbnq_mean * bbw_ori

    close_shift = df["Close"].shift(volatility_n)
    volume_shift = df["Volume"].shift(volatility_n)
    close_ratio = (df["Close"] - close_shift.rolling(volatility_n).mean()).abs() / close_shift
    volume_ratio = (df["Volume"] - volume_shift.rolling(volatility_n).mean()) / (volume_shift + 1e-8)
    angle = close_ratio * volume_ratio
    direction = np.where(angle < 0, -1.0, 1.0)
    price_volume_resist = (close_ratio / (volume_ratio.abs() + 1e-8)) * direction
    df["price_volume_resist"] = (price_volume_resist / volatility_n).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    adx_up_move = np.where(df["High"] > df["High"].shift(1), df["High"] - df["High"].shift(1), 0.0)
    adx_down_move = np.where(df["Low"].shift(1) > df["Low"], df["Low"].shift(1) - df["Low"], 0.0)
    adx_xpdm = np.where(adx_up_move > adx_down_move, df["High"] - df["High"].shift(1), 0.0)
    adx_pdm = pd.Series(adx_xpdm, index=df.index).rolling(volatility_n, min_periods=1).sum()
    adx_tr = pd.concat([
        (df["High"] - df["Low"]).abs(),
        (df["High"] - df["Close"].shift(1)).abs(),
        (df["Low"] - df["Close"].shift(1)).abs(),
    ], axis=1).max(axis=1)
    adx_tr_sum = adx_tr.rolling(volatility_n, min_periods=1).sum()
    adx_di_plus = adx_pdm / (adx_tr_sum + EPS)
    adx_mtm = (df["Close"] / (df["Close"].shift(volatility_n) + EPS) - 1.0).rolling(volatility_n, min_periods=1).mean()
    df["adx_mtm"] = adx_di_plus * adx_mtm
    adx_xndm = np.where(adx_down_move > adx_up_move, df["Low"].shift(1) - df["Low"], 0.0)
    adx_ndm = pd.Series(adx_xndm, index=df.index).rolling(volatility_n, min_periods=1).sum()
    adx_di_minus = adx_ndm / (adx_tr_sum + EPS)
    df["adx_mtm_neg"] = adx_di_minus * adx_mtm
    taker_buy = df.get("taker_buy_quote_asset_volume", pd.Series(np.where(df["Close"] > df["Close"].shift(1), df["Close"] * df["Volume"], 0.0), index=df.index))
    quote_volume = df.get("quote_volume", df["Close"] * df["Volume"])
    taker_ratio = taker_buy.rolling(volatility_n, min_periods=1).sum() / (quote_volume.rolling(volatility_n, min_periods=1).sum() + EPS)
    atr = adx_tr.rolling(volatility_n, min_periods=1).mean()
    avg_price = df["Close"].rolling(volatility_n, min_periods=1).mean()
    wd_atr = atr / (avg_price + EPS)
    mtm = df["Close"] / (df["Close"].shift(volatility_n) + EPS) - 1.0
    df["mtam"] = (mtm * taker_ratio * wd_atr).rolling(volatility_n, min_periods=1).mean()
    mtm_std = df["Close"].rolling(volatility_n, min_periods=1).std(ddof=0)
    mtm_std_mtm = (mtm_std / (mtm_std.shift(volatility_n) + EPS) - 1.0).rolling(volatility_n, min_periods=1).mean()
    bbw = mtm_std / (df["Close"].rolling(volatility_n, min_periods=1).mean() + EPS)
    bbw_mean = bbw.rolling(volatility_n, min_periods=1).mean()
    taker_buy_ratio = taker_buy.rolling(volatility_n, min_periods=1).sum() / (taker_buy.rolling(max(1, int(0.5 * volatility_n)), min_periods=1).sum() + EPS)
    df["msbt"] = mtm.rolling(volatility_n, min_periods=1).mean() * mtm_std_mtm * bbw_mean * taker_buy_ratio
    rc = 100.0 * ((df["Close"] - df["Close"].shift(volatility_n)) / (df["Close"].shift(volatility_n) + EPS) + (df["Close"] - df["Close"].shift(2 * volatility_n)) / (df["Close"].shift(2 * volatility_n) + EPS))
    rc_mean = rc.rolling(volatility_n, min_periods=1).mean()
    df["copp_atr_bull"] = rc_mean * wd_atr * taker_ratio


    below_open = (df["Close"] < df["session_open"]).astype(float)
    df["persist_short_12_shift1"] = below_open.rolling(12).mean().shift(1)

    # --- Signal-support indicators ---
    # Connors RSI is consumed by signal.py
    price_rank = df["roc_close"].rolling(100).rank(pct=True) * 100
    rsi3 = ta.rsi(df["Close"], length=3)
    streak_rsi2 = ta.rsi(df["streak"].astype(float), length=2)
    df["connors_rsi"] = (rsi3 + streak_rsi2 + price_rank) / 3.0

    return df
