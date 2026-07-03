import numpy as np
import pandas as pd
import pandas_ta as ta


WINDOW_BARS = 2
TREND_LEN = 55
RSI_LEN = 21
RSI_HIGH = 53
RSI_LOW = 47
VOL_MA_LEN = 20
FORCE_CLOSE_TIME = 1425


def _time_slice(series: pd.Series, hhmm: int, how: str) -> float:
    time_code = 100 * series.index.hour + series.index.minute
    if how == "first":
        values = series[time_code == hhmm]
        return values.iloc[0] if not values.empty else np.nan
    if how == "last":
        values = series[time_code == hhmm]
        return values.iloc[-1] if not values.empty else np.nan
    values = series[time_code < hhmm]
    if values.empty:
        return np.nan
    return values.max() if how == "max_before" else values.min()


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df["trade_date"] = df.index.normalize()
    df["bar_in_day"] = df.groupby("trade_date").cumcount()
    df["open_range_high"] = df.groupby("trade_date")["High"].transform(lambda s: s.iloc[:WINDOW_BARS].max())
    df["open_range_low"] = df.groupby("trade_date")["Low"].transform(lambda s: s.iloc[:WINDOW_BARS].min())
    df["trend"] = ta.ema(df["Close"], length=TREND_LEN)
    df["strategy_003_rsi"] = ta.rsi(df["Close"], length=RSI_LEN)
    df["strategy_003_vol_ma"] = df["Volume"].rolling(VOL_MA_LEN).mean()
    df["max_in_range"] = df["High"].rolling(10).max()
    df["min_in_range"] = df["Low"].rolling(10).min()

    daily = df.resample("D").agg(
        strategy_003_first_close=("Close", lambda s: _time_slice(s, 915, "first")),
        strategy_003_day_close=("Close", lambda s: _time_slice(s, 1445, "last")),
        strategy_003_prev_high=("High", lambda s: _time_slice(s, 1345, "max_before")),
        strategy_003_prev_low=("Low", lambda s: _time_slice(s, 1355, "min_before")),
    )
    daily = daily.dropna(subset=["strategy_003_day_close"])
    daily["strategy_003_prev_day_close"] = daily["strategy_003_day_close"].shift(1)
    df = df.join(
        daily[
            [
                "strategy_003_prev_day_close",
                "strategy_003_first_close",
                "strategy_003_prev_high",
                "strategy_003_prev_low",
            ]
        ],
        on="trade_date",
    )

    prev_close = df["strategy_003_prev_day_close"].replace(0, np.nan)
    prev_range = (df["strategy_003_prev_high"] - df["strategy_003_prev_low"]).replace(0, np.nan)
    df["strategy_003_mom_y"] = 100 * (df["Close"] - prev_close) / prev_close
    df["strategy_003_body_rate"] = (df["Close"] - df["strategy_003_first_close"]) / prev_range

    adx = ta.adx(df["High"], df["Low"], df["Close"], length=42)
    df["strategy_003_adx"] = adx["ADX_42"] if adx is not None and "ADX_42" in adx else np.nan

    distance_ok = (
        (df["Close"] - df["strategy_003_prev_low"] <= 21)
        & (df["strategy_003_prev_high"] - df["Close"] <= 21)
    )
    at_1355 = (100 * df.index.hour + df.index.minute) == 1355
    momentum_long = (
        at_1355
        & distance_ok
        & (df["strategy_003_mom_y"] > 0.26)
        & (df["strategy_003_body_rate"] > 0.65)
        & (df["strategy_003_adx"] < 26.5)
    )
    momentum_short = (
        at_1355
        & distance_ok
        & (df["strategy_003_mom_y"] < -0.18)
        & (df["strategy_003_body_rate"] < -0.39)
        & (df["strategy_003_adx"] < 26.5)
    )
    df["momentum_signal"] = np.select([momentum_long, momentum_short], ["long", "short"], default="")
    df["prev_day_bias"] = df.groupby("trade_date")["momentum_signal"].transform("max").shift(1)

    time_code = 100 * df.index.hour + df.index.minute
    session = (time_code >= 935) & (time_code < FORCE_CLOSE_TIME)
    long_signal = (
        session
        & (df["bar_in_day"] >= WINDOW_BARS)
        & (df["Close"] > df["open_range_high"])
        & (df["Close"] > df["trend"])
        & (df["strategy_003_rsi"] > RSI_HIGH)
        & (df["Volume"] > df["strategy_003_vol_ma"])
        & (df["prev_day_bias"] == "long")
    )
    short_signal = (
        session
        & (df["bar_in_day"] >= WINDOW_BARS)
        & (df["Close"] < df["open_range_low"])
        & (df["Close"] < df["trend"])
        & (df["strategy_003_rsi"] < RSI_LOW)
        & (df["Volume"] > df["strategy_003_vol_ma"])
        & (df["prev_day_bias"] == "short")
    )
    df["strategy_003_signal"] = np.select([long_signal, short_signal], ["long", "short"], default="")
    df["strategy_003_entry_signal"] = np.select(
        [df["strategy_003_signal"] == "long", df["strategy_003_signal"] == "short"],
        ["Buy", "Sell"],
        default="None",
    )
    df["signal"] = df["strategy_003_signal"]
    return df
