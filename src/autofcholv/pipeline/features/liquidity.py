import numpy as np
import pandas as pd
from autofcholv.config.config import Config


EPS = 1e-8


def edge_rolling(df: pd.DataFrame, window: int, sign: bool = False, **kwargs) -> pd.Series:
    df = df.rename(columns=str.lower, inplace=False)
    o = np.log(df["open"])
    h = np.log(df["high"])
    l = np.log(df["low"])
    c = np.log(df["close"])
    m = (h + l) / 2.0

    h1 = h.shift(1)
    l1 = l.shift(1)
    c1 = c.shift(1)
    m1 = m.shift(1)

    r1 = m - o
    r2 = o - m1
    r3 = m - c1
    r4 = c1 - m1
    r5 = o - c1

    tau = np.where(np.isnan(h) | np.isnan(l) | np.isnan(c1), np.nan, (h != l) | (l != c1))
    po1 = tau * np.where(np.isnan(o) | np.isnan(h), np.nan, o != h)
    po2 = tau * np.where(np.isnan(o) | np.isnan(l), np.nan, o != l)
    pc1 = tau * np.where(np.isnan(c1) | np.isnan(h1), np.nan, c1 != h1)
    pc2 = tau * np.where(np.isnan(c1) | np.isnan(l1), np.nan, c1 != l1)

    r12 = r1 * r2
    r15 = r1 * r5
    r34 = r3 * r4
    r45 = r4 * r5
    tr1 = tau * r1
    tr2 = tau * r2
    tr4 = tau * r4
    tr5 = tau * r5

    x = pd.DataFrame({
        1: r12,
        2: r34,
        3: r15,
        4: r45,
        5: tau,
        6: r1,
        7: tr2,
        8: r3,
        9: tr4,
        10: r5,
        11: r12 ** 2,
        12: r34 ** 2,
        13: r15 ** 2,
        14: r45 ** 2,
        15: r12 * r34,
        16: r15 * r45,
        17: tr2 * r2,
        18: tr4 * r4,
        19: tr5 * r5,
        20: tr2 * r12,
        21: tr4 * r34,
        22: tr5 * r15,
        23: tr4 * r45,
        24: tr4 * r12,
        25: tr2 * r34,
        26: tr2 * r4,
        27: tr1 * r45,
        28: tr5 * r45,
        29: tr4 * r5,
        30: tr5,
        31: po1,
        32: po2,
        33: pc1,
        34: pc2,
    }, index=df.index)

    x.iloc[0] = np.nan
    if isinstance(window, (int, np.integer)):
        window = max(0, window - 1)
    if 'min_periods' in kwargs and isinstance(kwargs['min_periods'], (int, np.integer)):
        kwargs['min_periods'] = max(0, kwargs['min_periods'] - 1)

    m = x.rolling(window=window, **kwargs).mean()
    pt = m[5]
    po = m[31] + m[32]
    pc = m[33] + m[34]
    nt = x[5].rolling(window=window, **kwargs).sum()
    m[(nt < 2) | (po == 0) | (pc == 0)] = np.nan

    a1 = -4.0 / po
    a2 = -4.0 / pc
    a3 = m[6] / pt
    a4 = m[9] / pt
    a5 = m[8] / pt
    a6 = m[10] / pt
    a12 = 2 * a1 * a2
    a11 = a1 ** 2
    a22 = a2 ** 2
    a33 = a3 ** 2
    a55 = a5 ** 2
    a66 = a6 ** 2

    e1 = a1 * (m[1] - a3 * m[7]) + a2 * (m[2] - a4 * m[8])
    e2 = a1 * (m[3] - a3 * m[30]) + a2 * (m[4] - a4 * m[10])

    v1 = -e1 ** 2 + (
        a11 * (m[11] - 2 * a3 * m[20] + a33 * m[17]) +
        a22 * (m[12] - 2 * a5 * m[21] + a55 * m[18]) +
        a12 * (m[15] - a3 * m[25] - a5 * m[24] + a3 * a5 * m[26])
    )
    v2 = -e2 ** 2 + (
        a11 * (m[13] - 2 * a3 * m[22] + a33 * m[19]) +
        a22 * (m[14] - 2 * a6 * m[23] + a66 * m[18]) +
        a12 * (m[16] - a3 * m[28] - a6 * m[27] + a3 * a6 * m[29])
    )

    vt = v1 + v2
    s2 = pd.Series.where(cond=vt > 0, self=(v2 * e1 + v1 * e2) / vt, other=(e1 + e2) / 2.0)
    s = np.sqrt(np.abs(s2))
    if sign:
        s *= np.sign(s2)
    return pd.Series(s, index=df.index)


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate liquidity and price-volume composite features adapted from quant-ohlcv-feature.
    Feature definitions follow liquidity.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    n = config.volume_lookback

    quote_volume_proxy = df["Close"] * df["Volume"]
    quote_volume_ema = quote_volume_proxy.ewm(span=n, adjust=False).mean()
    volume_ema = df["Volume"].ewm(span=n, adjust=False).mean()
    avg_holding_cost = quote_volume_ema / (volume_ema + EPS)
    df["market_placement"] = df["Close"] / (avg_holding_cost + EPS) - 1.0

    path_first = (df["High"] - df["Open"]) + (df["High"] - df["Low"]) + (df["Close"] - df["Low"])
    path_second = (df["Open"] - df["Low"]) + (df["High"] - df["Low"]) + (df["High"] - df["Close"])
    path_min = pd.concat([path_first, path_second], axis=1).min(axis=1)
    candle_range = df["High"] - df["Low"]
    path_min = np.where(path_min == 0.0, candle_range, path_min)
    path_min = pd.Series(path_min, index=df.index) + (df["Open"] - df["Close"].shift(1)).abs()
    path_shortest = path_min / (df["Close"] + EPS)
    liquidity_path = np.where(path_shortest == 0.0, np.nan, quote_volume_proxy / path_shortest)
    df["path_liquidity"] = pd.Series(liquidity_path, index=df.index).rolling(n, min_periods=1).sum()

    log_high = np.log(df["High"] + EPS)
    log_low = np.log(df["Low"] + EPS)
    log_close = np.log(df["Close"] + EPS)
    df["spread_proxy"] = (log_high - log_low).rolling(n, min_periods=2).mean()
    df["spread_volatility_ratio"] = df["spread_proxy"] / (
        log_close.diff().rolling(n, min_periods=2).std(ddof=0).abs() + EPS
    )

    close_shift = df["Close"].shift(n)
    volume_shift = df["Volume"].shift(n)
    close_ratio = ((df["Close"] - close_shift.rolling(n, min_periods=1).mean()) / (close_shift + EPS)).abs()
    volume_ratio = (df["Volume"] - volume_shift.rolling(n, min_periods=1).mean()) / (volume_shift + EPS)
    raw_resistance = close_ratio / (volume_ratio.abs() + EPS)
    df["price_volume_resistance"] = np.where(volume_ratio < 0, -raw_resistance, raw_resistance) / n

    bidask_estimate = edge_rolling(df, window=1000, sign=False)
    df["bidask_spread"] = bidask_estimate.rolling(n, min_periods=1).mean()

    quote_volume_ema = (df["Close"] * df["Volume"]).ewm(span=n, adjust=False).mean()
    volume_ema = df["Volume"].ewm(span=n, adjust=False).mean()
    avg_holding_cost = quote_volume_ema / (volume_ema + EPS)
    cost = (df["Open"] + df["Low"] + df["Close"]) / 3.0
    cost_ema = cost.ewm(span=n, adjust=False).mean()
    avg_p = np.where(df["Volume"] > 0, (df["Close"] * df["Volume"]) / (df["Volume"] + EPS), df["Close"].shift(1))
    avg_p = pd.Series(avg_p, index=df.index)
    in_range = (avg_p <= df["High"]) & (avg_p >= df["Low"])
    avg_holding_cost_v2 = pd.Series(np.where(in_range, avg_holding_cost, cost_ema), index=df.index)
    df["market_placement_v2"] = df["Close"] / (avg_holding_cost_v2 + EPS) - 1.0

    log_spread = (np.log(df["High"] + EPS) - np.log(df["Low"] + EPS)).rolling(n, min_periods=2).mean()
    log_vol = np.log(df["Close"] + EPS).diff().rolling(n, min_periods=2).std(ddof=0).abs()
    df["liquidity_v3"] = (df["Volume"] / (log_spread + EPS)) / (log_vol + EPS)

    coppock = 100.0 * (
        df["Close"].pct_change(n) + df["Close"].pct_change(2 * n)
    )
    coppock_mean = coppock.rolling(n, min_periods=1).mean()
    prev_close = df["Close"].shift(1)
    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    normalized_atr = true_range.rolling(n, min_periods=1).mean() / (
        df["Close"].rolling(n, min_periods=1).mean() + EPS
    )
    volume_pressure = df["Volume"] / (df["Volume"].rolling(n, min_periods=1).mean() + EPS)
    df["coppock_atr_volume"] = coppock_mean * normalized_atr * volume_pressure

    df = df.copy()

    route_1 = 2.0 * (df["High"] - df["Low"]) + (df["Open"] - df["Close"])
    route_2 = 2.0 * (df["High"] - df["Low"]) + (df["Close"] - df["Open"])
    shortest_path = np.minimum(route_1, route_2)
    normalized_shortest_path = shortest_path / (df["Open"] + EPS)
    amihud_premium = (df["Close"] * df["Volume"]) / (normalized_shortest_path + EPS)
    df["amihud"] = pd.Series(amihud_premium, index=df.index).rolling(n, min_periods=2).mean()



    return df
