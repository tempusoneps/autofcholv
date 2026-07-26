import numpy as np
import pandas as pd

from autofcholv.config.config import Config


def _daily_time_value(data: pd.DataFrame, column: str, hhmm: int, how: str) -> pd.Series:
    time_int = 100 * data.index.hour + data.index.minute
    trade_date = data.index.normalize()

    def aggregate(series: pd.Series) -> float:
        codes = pd.Series(time_int, index=data.index).loc[series.index]
        if how == "first_at":
            values = series[codes == hhmm]
            return values.iloc[0] if not values.empty else np.nan
        if how == "last_at":
            values = series[codes == hhmm]
            return values.iloc[-1] if not values.empty else np.nan
        if how == "max_before":
            values = series[codes < hhmm]
            return values.max() if not values.empty else np.nan
        if how == "min_before":
            values = series[codes < hhmm]
            return values.min() if not values.empty else np.nan
        raise ValueError(f"Unsupported aggregation: {how}")

    daily = data[column].groupby(trade_date).agg(aggregate)
    return pd.Series(trade_date, index=data.index).map(daily)


def get_1D_data(df: pd.DataFrame) -> pd.DataFrame:
    tmp_data = df.copy()
    tmp_data["day_high"] = tmp_data["High"]
    tmp_data["day_low"] = tmp_data["Low"]
    tmp_data["day_close"] = tmp_data["Close"]
    tmp_data["day_open"] = tmp_data["Open"]
    tmp_data["day_volume"] = tmp_data["Volume"]
    daily_data = tmp_data.resample("D").agg(
        {
            "day_high": "max",
            "day_low": "min",
            "day_close": "last",
            "day_open": "first",
            "day_volume": "sum",
        }
    )
    daily_data.dropna(subset=["day_high"], inplace=True)
    daily_data["day_pivot"] = (
        daily_data["day_high"] + daily_data["day_low"] + daily_data["day_close"]
    ) / 3
    daily_data["prev_day_close"] = daily_data["day_close"].shift(1)
    daily_data["prev_day_open"] = daily_data["day_open"].shift(1)
    daily_data["prev_day_high"] = daily_data["day_high"].shift(1)
    daily_data["prev_day_low"] = daily_data["day_low"].shift(1)
    daily_data["prev_day_volume"] = daily_data["day_volume"].shift(1)
    daily_data["prev_day_pivot"] = daily_data["day_pivot"].shift(1)
    return daily_data[
        [
            "prev_day_close",
            "prev_day_open",
            "prev_day_high",
            "prev_day_low",
            "prev_day_volume",
            "prev_day_pivot",
        ]
    ]


def _get_htf_data(
    df: pd.DataFrame, freq: str, prefix: str, delta: pd.Timedelta
) -> pd.DataFrame:
    tmp_data = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    htf = tmp_data.resample(freq).agg(
        {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
    ).dropna(subset=["High"])

    if htf.empty:
        cols = [
            f"{prefix}_open",
            f"{prefix}_high",
            f"{prefix}_low",
            f"{prefix}_close",
            f"{prefix}_volume",
            f"{prefix}_pivot",
            f"{prefix}_r1",
            f"{prefix}_s1",
            f"{prefix}_return",
            f"{prefix}_ema_bias_20",
        ]
        return pd.DataFrame(columns=cols, index=df.index)

    htf["pivot"] = (htf["High"] + htf["Low"] + htf["Close"]) / 3.0
    htf["r1"] = 2.0 * htf["pivot"] - htf["Low"]
    htf["s1"] = 2.0 * htf["pivot"] - htf["High"]
    htf["return"] = (htf["Close"] - htf["Open"]) / htf["Open"].replace(0, np.nan)

    ema20 = htf["Close"].ewm(span=20, adjust=False).mean()
    bias = pd.Series(0, index=htf.index)
    bias[htf["Close"] > ema20] = 1
    bias[htf["Close"] < ema20] = -1
    htf["ema_bias_20"] = bias

    # Shift completion timestamp by delta so that bar starting at T completes at T + delta
    htf.index = htf.index + delta

    htf = htf.rename(
        columns={
            "Open": f"{prefix}_open",
            "High": f"{prefix}_high",
            "Low": f"{prefix}_low",
            "Close": f"{prefix}_close",
            "Volume": f"{prefix}_volume",
            "pivot": f"{prefix}_pivot",
            "r1": f"{prefix}_r1",
            "s1": f"{prefix}_s1",
            "return": f"{prefix}_return",
            "ema_bias_20": f"{prefix}_ema_bias_20",
        }
    )

    cols = [
        f"{prefix}_open",
        f"{prefix}_high",
        f"{prefix}_low",
        f"{prefix}_close",
        f"{prefix}_volume",
        f"{prefix}_pivot",
        f"{prefix}_r1",
        f"{prefix}_s1",
        f"{prefix}_return",
        f"{prefix}_ema_bias_20",
    ]
    return htf[cols]


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    daily_data = get_1D_data(df)
    data = df.copy()
    data = data.assign(time_d=pd.PeriodIndex(data.index, freq="1D").to_timestamp())

    merged_data = pd.merge(data, daily_data, left_on="time_d", right_index=True, how="left")
    merged_data = merged_data.drop(columns=["time_d"])
    merged_data.index = data.index

    trade_date = pd.Series(merged_data.index.normalize(), index=merged_data.index)
    grouped = merged_data.groupby(trade_date)
    trading_daily = grouped.agg(
        day_high=("High", "max"),
        day_low=("Low", "min"),
        day_close=("Close", "last"),
    )
    prev_trading_daily = trading_daily.shift(1)
    merged_data["prev_trading_day_high"] = trade_date.map(prev_trading_daily["day_high"])
    merged_data["prev_trading_day_low"] = trade_date.map(prev_trading_daily["day_low"])
    merged_data["prev_trading_day_close"] = trade_date.map(prev_trading_daily["day_close"])
    prev = prev_trading_daily
    pp = (prev["day_high"] + prev["day_low"] + prev["day_close"]) / 3.0
    merged_data["prev_day_r1"] = trade_date.map(2.0 * pp - prev["day_low"])
    merged_data["prev_day_s1"] = trade_date.map(2.0 * pp - prev["day_high"])

    merged_data["first_close_0915"] = _daily_time_value(merged_data, "Close", 915, "first_at")
    merged_data["pre_1345_high"] = _daily_time_value(merged_data, "High", 1345, "max_before")
    merged_data["pre_1355_low"] = _daily_time_value(merged_data, "Low", 1355, "min_before")

    day_close_1445 = _daily_time_value(merged_data, "Close", 1445, "last_at")
    prev_1445 = day_close_1445.groupby(trade_date).first().shift(1)
    merged_data["prev_day_1445_close"] = trade_date.map(prev_1445).fillna(
        merged_data["prev_trading_day_close"]
    )

    day_ema = trading_daily["day_close"].ewm(span=20, adjust=False).mean()
    day_bias = pd.Series(0, index=trading_daily.index)
    day_bias[trading_daily["day_close"] > day_ema] = 1
    day_bias[trading_daily["day_close"] < day_ema] = -1
    merged_data["prev_day_ema_bias_20"] = trade_date.map(day_bias.shift(1))

    merged_data["morning_high"] = _daily_time_value(merged_data, "High", 1101, "max_before")
    merged_data["morning_low"] = _daily_time_value(merged_data, "Low", 1101, "min_before")
    merged_data["morning_mid"] = (merged_data["morning_high"] + merged_data["morning_low"]) / 2.0

    # Resample Higher Timeframe Features (15m, 30m, 1H)
    for freq, prefix, delta in [
        ("15min", "prev_15m", pd.Timedelta(minutes=15)),
        ("30min", "prev_30m", pd.Timedelta(minutes=30)),
        ("1h", "prev_1h", pd.Timedelta(hours=1)),
    ]:
        htf_df = _get_htf_data(df, freq, prefix, delta)
        if not htf_df.empty:
            merged_data = pd.merge_asof(
                merged_data,
                htf_df,
                left_index=True,
                right_index=True,
                direction="backward",
            )
        else:
            for col in htf_df.columns:
                merged_data[col] = np.nan

    return merged_data
