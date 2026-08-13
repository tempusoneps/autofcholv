import numpy as np
import pandas as pd
from autofcholv.config.config import Config


EPS = 1e-8


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Calculate price-derived features adapted from quant-ohlcv-feature.
    Feature definitions follow price.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    momentum_n = config.momentum_lookback

    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    weighted_close = (df["High"] + df["Low"] + 2.0 * df["Close"]) / 4.0
    midpoint = (df["High"] + df["Low"]) / 2.0

    df["typical_price"] = typical_price
    df["weighted_close"] = weighted_close
    df["midpoint"] = midpoint
    df["close_vs_mid"] = df["Close"] - midpoint

    typ_fast = typical_price.ewm(span=momentum_n, adjust=False).mean()
    typ_slow = typical_price.ewm(span=momentum_n * 3, adjust=False).mean()
    typ_diff = typ_fast - typ_slow
    typ_diff_mean = typ_diff.rolling(momentum_n, min_periods=1).mean()
    typ_diff_std = typ_diff.rolling(momentum_n, min_periods=2).std()
    df["typical_price_momentum"] = np.where(
        typ_diff_std.abs() > EPS,
        (typ_diff - typ_diff_mean) / typ_diff_std,
        np.nan,
    )

    wc_fast = weighted_close.ewm(span=momentum_n, adjust=False).mean()
    wc_slow = weighted_close.ewm(span=momentum_n * 2, adjust=False).mean()
    df["weighted_close_bias"] = wc_fast / (wc_slow + EPS) - 1.0

    rolling_volume = df["Volume"].rolling(momentum_n, min_periods=1).sum()
    rolling_turnover = (typical_price * df["Volume"]).rolling(momentum_n, min_periods=1).sum()
    rolling_vwap = rolling_turnover / rolling_volume.replace(0.0, np.nan)
    rolling_vwap_ma = rolling_vwap.rolling(momentum_n, min_periods=1).mean()

    df["rolling_vwap"] = rolling_vwap
    df["vwap_bias"] = rolling_vwap / (rolling_vwap_ma + EPS) - 1.0
    df["close_to_vwap"] = df["Close"] / (rolling_vwap + EPS) - 1.0

    rolling_vwap_min = rolling_vwap.rolling(momentum_n, min_periods=1).min()
    rolling_vwap_max = rolling_vwap.rolling(momentum_n, min_periods=1).max()
    df["vwap_range_position"] = (rolling_vwap - rolling_vwap_min) / (
        rolling_vwap_max - rolling_vwap_min + EPS
    )
    df["vwap_to_high"] = rolling_vwap / (df["High"] + EPS) - 1.0
    df["vwap_to_low"] = rolling_vwap / (df["Low"] + EPS) - 1.0
    df["close_ma_price"] = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["typical_to_vwap"] = typical_price / (rolling_vwap + EPS) - 1.0

    df = df.copy()

    rolling_volume = df["Volume"].rolling(momentum_n, min_periods=1).sum()
    rolling_turnover = ((df["High"] + df["Low"] + df["Close"]) / 3.0 * df["Volume"]).rolling(momentum_n, min_periods=1).sum()
    avg_price = rolling_turnover / rolling_volume.replace(0.0, np.nan)
    avg_price_min = avg_price.rolling(momentum_n, min_periods=1).min()
    avg_price_max = avg_price.rolling(momentum_n, min_periods=1).max()
    df["avgprice"] = (avg_price - avg_price_min) / (avg_price_max - avg_price_min + EPS)
    df["avgpricetohigh"] = avg_price / (df["High"] + EPS) - 1.0
    df["avgpricetolow"] = avg_price / (df["Low"] + EPS) - 1.0
    df["lowprice"] = df["Close"].rolling(momentum_n, min_periods=1).mean()
    df["typ"] = (df["Close"] + df["High"] + df["Low"]) / 3.0
    rolling_vwap = avg_price
    df["vwap_signal"] = df["typ"] / (rolling_vwap + EPS) - 1.0
    wc = (df["High"] + df["Low"] + 2.0 * df["Close"]) / 4.0
    df["wc"] = wc.ewm(span=momentum_n, adjust=False).mean() / (wc.ewm(span=momentum_n * 2, adjust=False).mean() + EPS) - 1.0


    vad = (df["Close"] - df["Open"]) / (df["High"] - df["Low"] + EPS) * df["Volume"]
    df["wvad"] = vad.rolling(momentum_n, min_periods=1).sum() / (vad.rolling(momentum_n, min_periods=1).max() - vad.rolling(momentum_n, min_periods=1).min() + EPS)

    vwap_proxy = rolling_turnover / (rolling_volume + EPS)
    vwap_ma = vwap_proxy.rolling(momentum_n, min_periods=1).mean()
    df["vwap_bias"] = vwap_proxy / (vwap_ma + EPS) - 1.0


    trade_date = pd.Series(df.index.normalize(), index=df.index)
    grouped = df.groupby(trade_date)
    open_range_high = grouped["High"].transform(lambda s: s.iloc[:2].max())
    open_range_low = grouped["Low"].transform(lambda s: s.iloc[:2].min())
    df["open_range_high_2"] = open_range_high
    df["open_range_low_2"] = open_range_low
    df["session_open"] = grouped["Open"].transform("first")

    session_high = grouped["High"].cummax()
    session_low = grouped["Low"].cummin()
    df["session_high_shift1"] = session_high.groupby(trade_date).shift(1)
    df["session_low_shift1"] = session_low.groupby(trade_date).shift(1)
    session_range = session_high - session_low
    shifted_range = (df["session_high_shift1"] - df["session_low_shift1"]).replace(0, np.nan)
    df["close_vs_session_range"] = (df["Close"] - df["session_low_shift1"]) / shifted_range
    df["session_range_pct"] = 100.0 * session_range / df["session_open"].replace(0, np.nan)
    df["session_body_pct"] = 100.0 * (df["Close"] - df["session_open"]) / df["session_open"].replace(0, np.nan)

    prev_range = (df["prev_trading_day_high"] - df["prev_trading_day_low"]).replace(0, np.nan)
    df["session_body_rate"] = (df["Close"] - df["session_open"]) / prev_range
    df["session_mom_y"] = (
        100.0 * (df["Close"] - df["prev_trading_day_close"]) / df["prev_trading_day_close"].replace(0, np.nan)
    )
    prev_close_ref = df["prev_day_close"] if "prev_day_close" in df.columns else df["prev_trading_day_close"]
    df["mom_y"] = (
        100.0 * (df["Close"] - prev_close_ref) / prev_close_ref.replace(0, np.nan)
    )

    pv = df["Close"] * df["Volume"]
    pv2 = df["Close"].pow(2) * df["Volume"]
    cum_vol = grouped["Volume"].cumsum().replace(0, np.nan)
    session_vwap = pv.groupby(trade_date).cumsum() / cum_vol
    vwap_var = pv2.groupby(trade_date).cumsum() / cum_vol - session_vwap.pow(2)
    df["session_vwap"] = session_vwap
    df["session_vwap_std"] = vwap_var.clip(lower=0).pow(0.5)
    df["session_vwap_upper_1_5"] = df["session_vwap"] + 1.5 * df["session_vwap_std"]
    df["session_vwap_lower_1_5"] = df["session_vwap"] - 1.5 * df["session_vwap_std"]
    df["session_vwap_z"] = (df["Close"] - df["session_vwap"]) / df["session_vwap_std"].replace(0, np.nan)
    df["session_vwap_dev_pct"] = 100.0 * (df["Close"] - df["session_vwap"]) / df["Close"].replace(0, np.nan)

    return df
