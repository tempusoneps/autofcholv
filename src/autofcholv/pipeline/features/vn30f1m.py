import numpy as np
import pandas as pd
from autofcholv.config.config import Config


def _get_third_thursday_of_month(year: int, month: int) -> pd.Timestamp:
    """Calculate the 3rd Thursday of a given year and month."""
    first_day = pd.Timestamp(year=year, month=month, day=1)
    offset = (3 - first_day.dayofweek) % 7
    first_thursday = first_day + pd.Timedelta(days=offset)
    third_thursday = first_thursday + pd.Timedelta(weeks=2)
    return third_thursday


def _daily_time_value(data: pd.DataFrame, column: str, hhmm: int, how: str) -> pd.Series:
    """Helper to compute specific daily intraday time milestone values."""
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


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    """
    Tính toán các features đặc thù dành riêng cho Hợp đồng Tương lai VN30F1M.

    Args:
        df: DataFrame đầu vào chứa OHLCV với index dạng DatetimeIndex.
        _config: Cấu hình pipeline.

    Returns:
        DataFrame bổ sung các cột feature dành riêng cho VN30F1M.
    """
    df = df.copy()

    if "trade_date" in df.columns:
        trade_dates = df["trade_date"]
    else:
        trade_dates = pd.Series(df.index.normalize(), index=df.index)

    time_int = df.index.hour * 100 + df.index.minute

    # 1. VN30F1M Trading Session & Window Flags
    df["vn30_is_ato"] = (time_int >= 845) & (time_int < 900)
    df["vn30_is_atc"] = (time_int >= 1430) & (time_int <= 1445)
    df["vn30_session_morning"] = (time_int >= 845) & (time_int <= 1130)
    df["vn30_session_afternoon"] = (time_int >= 1300) & (time_int <= 1445)
    df["vn30_pre_market_lead"] = df["vn30_is_ato"]

    df["vn30_session_0930_1335"] = (time_int >= 930) & (time_int <= 1335)
    df["vn30_session_0935_1425"] = (time_int >= 935) & (time_int < 1425)
    df["vn30_session_0935_1335"] = (time_int >= 935) & (time_int <= 1335)
    df["vn30_late_session_1325"] = time_int.isin({1325, 1340, 1355})
    df["vn30_late_session_1310"] = time_int.isin({1310, 1325, 1340, 1355})
    df["vn30_entry_window_1300_1425"] = (time_int >= 1300) & (time_int <= 1425)

    minutes_from_open = (df.index.hour * 60 + df.index.minute) - (8 * 60 + 45)
    lunch_break = np.where(time_int >= 1300, 90, 0)
    trading_minutes = minutes_from_open - lunch_break
    df["vn30_session_progress"] = np.clip(trading_minutes / 255.0, 0.0, 1.0)

    # 2. Expiration Day Features (Đáo hạn phái sinh: Thứ 5 tuần thứ 3 trong tháng)
    days = df.index.day
    dayofweek = df.index.dayofweek

    is_third_thursday = (dayofweek == 3) & (days >= 15) & (days <= 21)
    df["vn30_is_expiration_day"] = is_third_thursday

    thursday_day_of_week = days + (3 - dayofweek)
    df["vn30_is_expiration_week"] = (thursday_day_of_week >= 15) & (thursday_day_of_week <= 21)

    df["vn30_is_expiry_settlement_window"] = df["vn30_is_expiration_day"] & (time_int >= 1400) & (time_int <= 1445)

    unique_dates = pd.Series(trade_dates.unique()).sort_values()
    expiry_map = {}
    for d in unique_dates:
        expiry_curr = _get_third_thursday_of_month(d.year, d.month)
        if d > expiry_curr:
            next_month = d.month % 12 + 1
            next_year = d.year + (1 if d.month == 12 else 0)
            expiry_target = _get_third_thursday_of_month(next_year, next_month)
        else:
            expiry_target = expiry_curr
        expiry_map[d] = (expiry_target - d).days

    df["vn30_days_to_expiration"] = trade_dates.map(expiry_map).astype(int)

    # 3. Intraday Opening Range (ORB) & Gap Features
    session_first_open = df.groupby(trade_dates)["Open"].transform("first")
    daily_close = df.groupby(trade_dates)["Close"].last().shift(1)
    prev_day_close_mapped = trade_dates.map(daily_close)
    df["vn30_opening_gap"] = (session_first_open - prev_day_close_mapped) / (prev_day_close_mapped + 1e-8)

    bar_in_day = df.groupby(trade_dates).cumcount()
    orb_15_mask = bar_in_day < 3

    orb_15_high = df["High"].where(orb_15_mask).groupby(trade_dates).transform("max")
    orb_15_low = df["Low"].where(orb_15_mask).groupby(trade_dates).transform("min")

    df["vn30_orb_15m_high"] = orb_15_high.groupby(trade_dates).ffill()
    df["vn30_orb_15m_low"] = orb_15_low.groupby(trade_dates).ffill()
    df["vn30_orb_15m_range"] = df["vn30_orb_15m_high"] - df["vn30_orb_15m_low"]

    df["vn30_orb_15m_breakout"] = np.where(
        bar_in_day >= 3,
        np.where(
            df["Close"] > df["vn30_orb_15m_high"],
            1,
            np.where(df["Close"] < df["vn30_orb_15m_low"], -1, 0),
        ),
        0,
    )

    orb_30_mask = bar_in_day < 6
    orb_30_high = df["High"].where(orb_30_mask).groupby(trade_dates).transform("max")
    orb_30_low = df["Low"].where(orb_30_mask).groupby(trade_dates).transform("min")

    df["vn30_orb_30m_high"] = orb_30_high.groupby(trade_dates).ffill()
    df["vn30_orb_30m_low"] = orb_30_low.groupby(trade_dates).ffill()
    df["vn30_orb_30m_range"] = df["vn30_orb_30m_high"] - df["vn30_orb_30m_low"]

    df["vn30_orb_30m_breakout"] = np.where(
        bar_in_day >= 6,
        np.where(
            df["Close"] > df["vn30_orb_30m_high"],
            1,
            np.where(df["Close"] < df["vn30_orb_30m_low"], -1, 0),
        ),
        0,
    )

    # 4. VN30 Intraday Milestone Features (moved from resample.py)
    df["first_close_0915"] = _daily_time_value(df, "Close", 915, "first_at")
    df["pre_1345_high"] = _daily_time_value(df, "High", 1345, "max_before")
    df["pre_1355_low"] = _daily_time_value(df, "Low", 1355, "min_before")

    day_close_1445 = _daily_time_value(df, "Close", 1445, "last_at")
    prev_1445 = day_close_1445.groupby(trade_dates).first().shift(1)
    fallback_close = df["prev_trading_day_close"] if "prev_trading_day_close" in df.columns else df.groupby(trade_dates)["Close"].last().shift(1)
    df["prev_day_1445_close"] = trade_dates.map(prev_1445).fillna(fallback_close)

    df["morning_high"] = _daily_time_value(df, "High", 1101, "max_before")
    df["morning_low"] = _daily_time_value(df, "Low", 1101, "min_before")
    df["morning_mid"] = (df["morning_high"] + df["morning_low"]) / 2.0

    # 5. Late Session Intraday Metrics
    cum_high = df.groupby(trade_dates)["High"].cummax()
    cum_low = df.groupby(trade_dates)["Low"].cummin()
    cum_range = cum_high - cum_low
    df["vn30_late_session_range_pos"] = np.where(
        cum_range > 0,
        (df["Close"] - cum_low) / (cum_range + 1e-8),
        0.5,
    )

    return df
