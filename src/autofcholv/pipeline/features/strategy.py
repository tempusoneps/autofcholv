import numpy as np
import pandas as pd

from autofcholv.config.config import Config


SIGNAL_NONE = "None"
SIGNAL_BUY = "Buy"
SIGNAL_SELL = "Sell"

BASE_COLUMNS = {"Open", "High", "Low", "Close", "Volume"}
REQUIRED_HELPER_COLUMNS = {
    "accept_long_4_shift1",
    "adx_14",
    "adx_42",
    "ibs",
    "bearish_low_break_candle",
    "body_atr_ratio",
    "body_rate_first_close",
    "bullish_high_break_candle",
    "close_donchian_high_20_shift1",
    "close_donchian_low_20_shift1",
    "close_vs_session_range",
    "dmn_14",
    "dmp_14",
    "donchian_high_10_shift1",
    "donchian_high_30_shift1",
    "donchian_low_10_shift1",
    "donchian_low_30_shift1",
    "ema_8",
    "ema_20_cross_above_ema_250",
    "ema_20_cross_below_ema_250",
    "ema_21",
    "ema_55",
    "entry_window_1300_1425",
    "first_close_0915",
    "heikin_ashi_bull",
    "keltner_lower_20_2",
    "keltner_upper_20_2",
    "late_session_1310",
    "late_session_1325",
    "linear_regression_slope_5",
    "linear_regression_slope_8",
    "macd_hist_12_26_9",
    "mom_y",
    "morning_breakout_long",
    "open_range_high_2",
    "open_range_low_2",
    "opening_gap_pct",
    "persist_short_12_shift1",
    "pre_1345_high",
    "pre_1355_low",
    "prev_day_ema_bias_20",
    "prev_day_momentum_signal_bias",
    "prev_day_r1",
    "prev_day_s1",
    "psar_bear",
    "psar_bull",
    "rsi_5",
    "rsi_8",
    "rsi_14",
    "rsi_21",
    "session_0930_1335",
    "session_0935_1335",
    "session_0935_1425",
    "session_body_pct",
    "session_body_rate",
    "session_flow_imbalance",
    "session_mom_y",
    "session_range_pct",
    "session_vwap_dev_pct",
    "session_vwap_lower_1_5",
    "session_vwap_upper_1_5",
    "session_vwap_z",
    "stochrsi_k",
    "time_int",
    "bar_in_day",
    "volume_sma20",
    "williams_r_14",
    "bb_percent_b_20_2",
}


def _signal_from_conditions(long_cond: pd.Series, short_cond: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [long_cond.fillna(False), short_cond.fillna(False)],
            [SIGNAL_BUY, SIGNAL_SELL],
            default=SIGNAL_NONE,
        ),
        index=long_cond.index,
    )


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing_helpers = sorted(REQUIRED_HELPER_COLUMNS - set(df.columns))
    if missing_helpers:
        raise ValueError(f"Missing strategy helper columns: {missing_helpers}")

    missing_base = sorted(BASE_COLUMNS - set(df.columns))
    if missing_base:
        raise ValueError(f"Missing base OHLCV columns for strategy signals: {missing_base}")


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    _validate_required_columns(df)

    in_orb = df["bar_in_day"] >= 2
    vol_ok = df["Volume"] > df["volume_sma20"]
    close_gt_ema55 = df["Close"] > df["ema_55"]
    close_lt_ema55 = df["Close"] < df["ema_55"]
    close_gt_orh = df["Close"] > df["open_range_high_2"]
    close_lt_orl = df["Close"] < df["open_range_low_2"]
    at_1355 = df["time_int"] == 1355

    not_extreme = (
        (df["Close"] - df["pre_1355_low"] <= 21)
        & (df["pre_1345_high"] - df["Close"] <= 21)
    )
    momentum_long = not_extreme & (df["mom_y"] > 0.26) & (df["body_rate_first_close"] > 0.65)
    momentum_short = not_extreme & (df["mom_y"] < -0.18) & (df["body_rate_first_close"] < -0.39)
    momentum_long_adx = momentum_long & (df["adx_42"] < 26.5)
    momentum_short_adx = momentum_short & (df["adx_42"] < 26.5)

    df["signal_pro1"] = _signal_from_conditions(at_1355 & momentum_long_adx, at_1355 & momentum_short_adx)
    df["signal_pro2"] = _signal_from_conditions(
        df["session_0935_1425"] & in_orb & close_gt_orh & close_gt_ema55 & vol_ok & (df["opening_gap_pct"] > 0.10),
        df["session_0935_1425"] & in_orb & close_lt_orl & close_lt_ema55 & vol_ok & (df["opening_gap_pct"] < -0.10),
    )
    df["signal_pro3"] = _signal_from_conditions(
        df["session_0935_1425"] & in_orb & close_gt_orh & close_gt_ema55 & (df["rsi_21"] > 53) & vol_ok & (df["prev_day_momentum_signal_bias"] == SIGNAL_BUY),
        df["session_0935_1425"] & in_orb & close_lt_orl & close_lt_ema55 & (df["rsi_21"] < 47) & vol_ok & (df["prev_day_momentum_signal_bias"] == SIGNAL_SELL),
    )
    df["signal_pro4"] = _signal_from_conditions(
        df["ema_20_cross_above_ema_250"] | momentum_long | df["bullish_high_break_candle"],
        df["ema_20_cross_below_ema_250"] | momentum_short | df["bearish_low_break_candle"],
    )
    orb5_long = in_orb & close_gt_orh & close_gt_ema55 & (df["rsi_14"] > 58) & (df["prev_day_ema_bias_20"] >= 0)
    orb5_short = in_orb & close_lt_orl & close_lt_ema55 & (df["rsi_14"] < 42) & (df["prev_day_ema_bias_20"] <= 0)
    df["signal_pro5"] = _signal_from_conditions(orb5_long | (at_1355 & momentum_long), orb5_short | (at_1355 & momentum_short))
    df["signal_pro6"] = _signal_from_conditions(
        df["session_0930_1335"] & in_orb & close_gt_orh & close_gt_ema55 & (df["rsi_14"] >= 54),
        df["session_0930_1335"] & in_orb & close_lt_orl & close_lt_ema55 & (df["rsi_14"] <= 46),
    )
    df["signal_pro7"] = _signal_from_conditions(
        df["session_0930_1335"] & in_orb & close_gt_orh & close_gt_ema55 & (df["rsi_14"] >= 52),
        df["session_0930_1335"] & in_orb & close_lt_orl & close_lt_ema55 & (df["rsi_14"] <= 48),
    )
    df["signal_pro8"] = _signal_from_conditions(
        df["session_0930_1335"] & in_orb & close_gt_orh & close_gt_ema55 & (df["rsi_14"] >= 54) & (df["prev_day_ema_bias_20"] >= 0),
        df["session_0930_1335"] & in_orb & close_lt_orl & close_lt_ema55 & (df["rsi_14"] <= 46) & (df["prev_day_ema_bias_20"] <= 0),
    )

    channel_session = df["session_0930_1335"]
    df["signal_pro9"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & close_lt_ema55 & vol_ok)
    df["signal_pro10"] = _signal_from_conditions(channel_session & (df["Close"] > df["donchian_high_30_shift1"]) & close_gt_ema55 & vol_ok & (df["rsi_14"] > 54), channel_session & (df["Close"] < df["donchian_low_30_shift1"]) & close_lt_ema55 & vol_ok & (df["rsi_14"] < 46))
    df["signal_pro11"] = _signal_from_conditions(channel_session & (df["Close"] > df["session_vwap_upper_1_5"]) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["session_vwap_lower_1_5"]) & close_lt_ema55 & vol_ok)
    df["signal_pro12"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & df["heikin_ashi_bull"] & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & (~df["heikin_ashi_bull"]) & close_lt_ema55 & vol_ok)
    df["signal_pro13"] = _signal_from_conditions(channel_session & (df["Close"] > df["prev_day_r1"]) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["prev_day_s1"]) & close_lt_ema55 & vol_ok)
    df["signal_pro14"] = _signal_from_conditions(channel_session & (df["Close"] > df["close_donchian_high_20_shift1"]) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["close_donchian_low_20_shift1"]) & close_lt_ema55 & vol_ok)
    df["signal_pro15"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & (df["stochrsi_k"] > 65) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & (df["stochrsi_k"] < 35) & close_lt_ema55 & vol_ok)
    df["signal_pro16"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & (df["macd_hist_12_26_9"] > 0) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & (df["macd_hist_12_26_9"] < 0) & close_lt_ema55 & vol_ok)
    df["signal_pro17"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & (df["ema_8"] > df["ema_21"]) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & (df["ema_8"] < df["ema_21"]) & close_lt_ema55 & vol_ok)
    df["signal_pro18"] = _signal_from_conditions(channel_session & (df["Close"] > df["keltner_upper_20_2"]) & df["psar_bull"] & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["keltner_lower_20_2"]) & df["psar_bear"] & close_lt_ema55 & vol_ok)
    df["signal_pro19"] = _signal_from_conditions(channel_session & (df["Close"] > df["donchian_high_10_shift1"]) & (df["macd_hist_12_26_9"] > 0) & close_gt_ema55 & vol_ok, channel_session & (df["Close"] < df["donchian_low_10_shift1"]) & (df["macd_hist_12_26_9"] < 0) & close_lt_ema55 & vol_ok)
    df["signal_pro20"] = _signal_from_conditions(channel_session & (df["williams_r_14"] > -25) & (df["macd_hist_12_26_9"] > 0) & close_gt_ema55 & vol_ok, channel_session & (df["williams_r_14"] < -75) & (df["macd_hist_12_26_9"] < 0) & close_lt_ema55 & vol_ok)
    df["signal_pro21"] = _signal_from_conditions(channel_session & (df["bb_percent_b_20_2"] > 0.8) & (df["macd_hist_12_26_9"] > 0) & close_gt_ema55 & vol_ok, channel_session & (df["bb_percent_b_20_2"] < 0.2) & (df["macd_hist_12_26_9"] < 0) & close_lt_ema55 & vol_ok)
    df["signal_pro22"] = _signal_from_conditions(channel_session & (df["ibs"] > 0.62) & (df["macd_hist_12_26_9"] > 0) & close_gt_ema55 & vol_ok, channel_session & (df["ibs"] < 0.38) & (df["macd_hist_12_26_9"] < 0) & close_lt_ema55 & vol_ok)

    df["signal_pro23"] = _signal_from_conditions(df["late_session_1325"] & (df["rsi_8"] >= 61.11) & (df["session_vwap_dev_pct"] >= 0.16) & (df["session_body_pct"] >= 0.14), df["late_session_1325"] & (df["rsi_8"] <= 42.0) & (df["session_vwap_dev_pct"] <= -0.06) & (df["session_body_pct"] <= -0.11))
    df["signal_pro24"] = _signal_from_conditions(df["late_session_1325"] & (df["session_flow_imbalance"] >= 0.0) & (df["rsi_8"] >= 61.11) & (df["session_vwap_dev_pct"] >= 0.14) & (df["session_body_pct"] >= 0.12), df["late_session_1325"] & (df["session_flow_imbalance"] <= 0.0) & (df["rsi_8"] <= 42.0) & (df["session_vwap_dev_pct"] <= -0.05) & (df["session_body_pct"] <= -0.10))
    df["signal_pro25"] = _signal_from_conditions(df["session_0935_1335"] & in_orb & close_gt_orh & (df["body_atr_ratio"] > 0.20) & close_gt_ema55 & (df["rsi_14"] > 54), df["session_0935_1335"] & in_orb & close_lt_orl & (df["body_atr_ratio"] < -0.20) & close_lt_ema55 & (df["rsi_14"] < 46))
    df["signal_pro26"] = _signal_from_conditions((df["adx_42"] < 26.5) & (df["session_body_rate"] > 0.50) & (df["session_mom_y"] > 0.20) & (df["ibs"] > 0.65), (df["adx_42"] < 26.5) & (df["session_body_rate"] < -0.50) & (df["session_mom_y"] < -0.20) & (df["ibs"] < 0.35))
    df["signal_pro27"] = _signal_from_conditions(df["late_session_1310"] & (df["close_vs_session_range"] > 0.79) & (df["rsi_5"] > 62) & (df["session_body_pct"] > 0.12) & (df["adx_14"] > 17) & (df["dmp_14"] > df["dmn_14"]) & (df["linear_regression_slope_8"] > 0), df["late_session_1310"] & (df["persist_short_12_shift1"] > 0.42) & (df["rsi_5"] < 38) & (df["session_body_pct"] < -0.12) & (df["adx_14"] > 17) & (df["dmn_14"] > df["dmp_14"]) & (df["linear_regression_slope_8"] < 0))
    df["signal_pro28"] = _signal_from_conditions(df["late_session_1325"] & (df["session_vwap_z"] >= 0.75) & (df["rsi_8"] >= 54.0) & (df["session_body_pct"] >= 0.05) & (df["session_range_pct"] >= 0.12), df["late_session_1325"] & (df["session_vwap_z"] <= -1.00) & (df["rsi_8"] <= 41.0) & (df["session_body_pct"] <= -0.10) & (df["session_range_pct"] >= 0.18))
    df["signal_pro29"] = _signal_from_conditions(df["entry_window_1300_1425"] & (df["accept_long_4_shift1"] >= 0.42) & (df["morning_breakout_long"] >= 0.0) & (df["ibs"] >= 0.55) & (df["rsi_8"] >= 54) & (df["linear_regression_slope_5"] > 0), pd.Series(False, index=df.index))

    for signal_index in range(1, 30):
        column = f"signal_pro{signal_index}"
        df[column] = df[column].fillna(SIGNAL_NONE)
    return df
