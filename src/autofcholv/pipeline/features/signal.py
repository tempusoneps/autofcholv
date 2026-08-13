import numpy as np
import pandas as pd
from autofcholv.config.config import Config


BUY_SIGNAL = "Buy"
SELL_SIGNAL = "Sell"
NONE_SIGNAL = "None"


REQUIRED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "open_lag1",
    "close_lag1",
    "high_lag1",
    "low_lag1",
    "volume_lag1",
    "ema_fast",
    "ema_slow",
    "ema_fast_lag1",
    "ema_slow_lag1",
    "rsi",
    "rsi_lag1",
    "macd",
    "macd_hist",
    "long_trend",
    "ub",
    "lb",
    "mb",
    "std",
    "body",
    "upwick",
    "lowwick",
    "volume_avg",
    "close_zscore",
    "roc_close",
    "cmo",
    "efficiency_ratio",
    "ulti_osci",
    "atr",
    "adx",
    "direction",
    "streak",
    "aroon_up",
    "aroon_down",
    "hma20",
    "kama10",
    "trix15",
    "trix15_signal",
    "supertrend_dir",
    "tenkan",
    "kijun",
    "span_a",
    "span_b",
    "linreg_slope20",
    "linreg_mid20",
    "tma10",
    "stoch_rsi",
    "awesome_oscillator",
    "roc10",
    "ultimate_osc",
    "stochrsi_k",
    "stochrsi_d",
    "bb_width",
    "kc_mid",
    "kc_upper",
    "kc_lower",
    "chop14",
    "hurst_proxy",
    "mfi14",
    "vpt",
    "connors_rsi",
    "height",
    "body_abs",
    "body_abs_sma20",
    "range_sma20",
    "midpoint",
    "price_change",
    "price_change_lag1",
    "return_5",
    "return_10",
    "sma20",
    "sma50",
    "std5",
    "std10",
    "std20",
    "std50",
    "bb_width_q20",
    "bb_width_sma20",
    "close_min_10",
    "close_max_10",
    "high_5",
    "low_5",
    "high_10",
    "low_10",
    "high_20",
    "low_20",
    "range_mid_10",
    "recent_high",
    "recent_low",
    "recent_high_prev",
    "recent_low_prev",
    "volume_sma20",
    "atr_sma20",
    "linreg_upper20",
    "linreg_lower20",
    "lower_range_pos",
    "upper_range_pos",
    "equal_low",
    "equal_high",
    "inside_bar_prev",
    "prev_5_low",
    "prev_5_high",
    "prev_10_low",
    "prev_10_high",
    "prev_20_low",
    "prev_20_high",
    "close_vs_mid",
    "candle_range_ratio",
]


def _signal_from_conditions(buy: pd.Series, sell: pd.Series) -> pd.Series:
    buy_clean = buy.fillna(False).astype(bool)
    sell_clean = sell.fillna(False).astype(bool)
    return pd.Series(
        np.where(buy_clean, BUY_SIGNAL, np.where(sell_clean, SELL_SIGNAL, NONE_SIGNAL)),
        index=buy.index,
    )


def _true_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    cond1_sell = (df["open_lag1"] > df["close_lag1"]) & (df["close_lag1"] >= df["low_lag1"] + 0.1)
    cond2_sell = (df["Open"] > df["Close"]) & (df["Close"] == df["Low"]) & (df["Low"] < df["low_lag1"])
    cond1_buy = (df["open_lag1"] < df["close_lag1"]) & (df["close_lag1"] <= df["high_lag1"] - 0.1)
    cond2_buy = (df["Open"] < df["Close"]) & (df["Close"] == df["High"]) & (df["High"] > df["high_lag1"])
    df["couple_cs_signal"] = _signal_from_conditions(cond1_buy & cond2_buy, cond1_sell & cond2_sell)

    ema_bullish = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast_lag1"] <= df["ema_slow_lag1"])
    ema_bearish = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast_lag1"] >= df["ema_slow_lag1"])
    df["ema_cross_signal"] = _signal_from_conditions(ema_bullish, ema_bearish)

    df["min_max_10_signal"] = _signal_from_conditions(
        (df["Close"] == df["close_min_10"]) & (df["rsi"] < 30),
        (df["Close"] == df["close_max_10"]) & (df["rsi"] > 70),
    )

    is_max_macd_hist = df["macd_hist"] == df["macd_hist"].rolling(10).max()
    is_min_macd_hist = df["macd_hist"] == df["macd_hist"].rolling(10).min()
    df["macd_histogram_reversal_signal"] = _signal_from_conditions(
        (df["open_lag1"] >= df["close_lag1"])
        & (df["macd_hist"] < 0)
        & is_min_macd_hist.shift(1, fill_value=False)
        & (df["macd_hist"].rolling(5).sum() < 0)
        & (df["Close"] > df["open_lag1"])
        & ((df["Close"] - df["low_lag1"]) < 5),
        (df["open_lag1"] <= df["close_lag1"])
        & (df["macd_hist"] > 0)
        & is_max_macd_hist.shift(1, fill_value=False)
        & (df["macd_hist"].rolling(5).sum() > 0)
        & (df["Close"] < df["open_lag1"])
        & ((df["high_lag1"] - df["Close"]) < 5),
    )

    df["bb_rejection_signal"] = _signal_from_conditions(
        (df["Low"] < df["lb"])
        & (df["Close"] > df["lb"])
        & (df["rsi"] < 35)
        & (df["lowwick"] > df["body"].abs())
        & (df["long_trend"] == "StrongUp"),
        (df["High"] > df["ub"])
        & (df["Close"] < df["ub"])
        & (df["rsi"] > 65)
        & (df["upwick"] > df["body"].abs())
        & (df["long_trend"] == "StrongDown"),
    )

    df["bb_squeeze_signal"] = _signal_from_conditions(
        (df["bb_width"] < df["bb_width_q20"]) & (df["Close"] > df["ub"]),
        (df["bb_width"] < df["bb_width_q20"]) & (df["Close"] < df["lb"]),
    )
    df["rsi_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(5)) & (df["rsi"] > df["rsi"].shift(5)),
        (df["High"] > df["High"].shift(5)) & (df["rsi"] < df["rsi"].shift(5)),
    )
    df["atr_breakout_signal"] = _signal_from_conditions(
        (df["height"] > 1.5 * df["atr"]) & (df["Close"] > df["Open"]),
        (df["height"] > 1.5 * df["atr"]) & (df["Close"] < df["Open"]),
    )
    df["vsa_confirmation_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Volume"] > 1.2 * df["volume_sma20"]),
        (df["Close"] < df["Open"]) & (df["Volume"] > 1.2 * df["volume_sma20"]),
    )

    cloud_top = pd.concat([df["span_a"], df["span_b"]], axis=1).max(axis=1)
    cloud_bottom = pd.concat([df["span_a"], df["span_b"]], axis=1).min(axis=1)
    df["ichimoku_cloud_signal"] = _signal_from_conditions(
        (df["Close"] > cloud_top) & (df["tenkan"] > df["kijun"]),
        (df["Close"] < cloud_bottom) & (df["tenkan"] < df["kijun"]),
    )
    df["ma_stretch_signal"] = _signal_from_conditions(df["close_zscore"] < -2, df["close_zscore"] > 2)
    df["market_structure_break_signal"] = _signal_from_conditions(
        (df["Close"] > df["recent_high"]) & (df["recent_low"] < df["recent_low_prev"]),
        (df["Close"] < df["recent_low"]) & (df["recent_high"] > df["recent_high_prev"]),
    )
    df["bollinger_band_width_signal"] = _signal_from_conditions(
        df["bb_width"] < (df["bb_width_sma20"] * 0.7),
        df["bb_width"] > (df["bb_width_sma20"] * 1.3),
    )
    df["volume_confirmation_signal"] = ((df["Volume"] > df["volume_sma20"]) & (df["Close"] != df["close_lag1"])).fillna(False)
    df["mfi_rejection_signal"] = _signal_from_conditions(
        (df["mfi14"] < 20) & (df["mfi14"] > df["mfi14"].shift(1)),
        (df["mfi14"] > 80) & (df["mfi14"] < df["mfi14"].shift(1)),
    )
    df["donchian_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_20_high"], df["Close"] < df["prev_20_low"])
    df["hma_reversal_signal"] = _signal_from_conditions(
        (df["hma20"] > df["hma20"].shift(1)) & (df["hma20"].shift(1) < df["hma20"].shift(2)),
        (df["hma20"] < df["hma20"].shift(1)) & (df["hma20"].shift(1) > df["hma20"].shift(2)),
    )
    df["adx_trend_filter"] = (df["adx"] > 25).fillna(False)
    df["connors_rsi_signal"] = _signal_from_conditions(df["connors_rsi"] < 15, df["connors_rsi"] > 85)
    df["choppiness_signal"] = (df["chop14"] < 38.2).fillna(False)
    df["keltner_channel_reversal"] = _signal_from_conditions(
        (df["Close"] < df["kc_lower"]) & (df["close_lag1"] > df["kc_lower"].shift(1)),
        (df["Close"] > df["kc_upper"]) & (df["close_lag1"] < df["kc_upper"].shift(1)),
    )
    
    df["supertrend_reversal"] = _signal_from_conditions(
        (df["supertrend_dir"] > 0) & (df["supertrend_dir"].shift(1) < 0),
        (df["supertrend_dir"] < 0) & (df["supertrend_dir"].shift(1) > 0),
    )
    df["aroon_oscillator_signal"] = _signal_from_conditions(
        (df["aroon_up"] > 70) & (df["aroon_down"] < 30),
        (df["aroon_down"] > 70) & (df["aroon_up"] < 30),
    )
    df["chande_momentum_oscillator_signal"] = _signal_from_conditions(
        (df["cmo"] > 50) & (df["cmo"].shift(1) < 50),
        (df["cmo"] < -50) & (df["cmo"].shift(1) > -50),
    )
    df["ultimate_oscillator_signal"] = _signal_from_conditions(
        (df["ultimate_osc"] < 30) & (df["ultimate_osc"] > df["ultimate_osc"].shift(1)),
        (df["ultimate_osc"] > 70) & (df["ultimate_osc"] < df["ultimate_osc"].shift(1)),
    )
    df["trix_crossover_signal"] = _signal_from_conditions(
        (df["trix15"] > df["trix15_signal"]) & (df["trix15"].shift(1) <= df["trix15_signal"].shift(1)),
        (df["trix15"] < df["trix15_signal"]) & (df["trix15"].shift(1) >= df["trix15_signal"].shift(1)),
    )
    df["stochastic_rsi_signal"] = _signal_from_conditions(
        (df["stoch_rsi"] < 0.2) & (df["stoch_rsi"] > df["stoch_rsi"].shift(1)),
        (df["stoch_rsi"] > 0.8) & (df["stoch_rsi"] < df["stoch_rsi"].shift(1)),
    )
    df["awesome_oscillator_signal"] = _signal_from_conditions(
        (df["awesome_oscillator"] > 0) & (df["awesome_oscillator"].shift(1) < df["awesome_oscillator"]),
        (df["awesome_oscillator"] < 0) & (df["awesome_oscillator"].shift(1) > df["awesome_oscillator"]),
    )
    df["rate_of_change_signal"] = _signal_from_conditions(
        (df["roc10"] > 0) & (df["roc10"].shift(1) < df["roc10"]),
        (df["roc10"] < 0) & (df["roc10"].shift(1) > df["roc10"]),
    )
    df["price_channel_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_20_high"], df["Close"] < df["prev_20_low"])
    df["linear_regression_slope_signal"] = _signal_from_conditions(
        (df["linreg_slope20"] > 0) & (df["linreg_slope20"].shift(1) < df["linreg_slope20"]),
        (df["linreg_slope20"] < 0) & (df["linreg_slope20"].shift(1) > df["linreg_slope20"]),
    )
    df["kaufman_ama_signal"] = _signal_from_conditions(
        (df["kama10"] > df["kama10"].shift(1)) & (df["kama10"].shift(1) < df["kama10"].shift(2)),
        (df["kama10"] < df["kama10"].shift(1)) & (df["kama10"].shift(1) > df["kama10"].shift(2)),
    )
    df["tma_reversal_signal"] = _signal_from_conditions(
        (df["Close"] > df["tma10"]) & (df["close_lag1"] < df["tma10"].shift(1)),
        (df["Close"] < df["tma10"]) & (df["close_lag1"] > df["tma10"].shift(1)),
    )
    df["linear_regression_channel_signal"] = _signal_from_conditions(
        (df["Close"] < df["linreg_lower20"]) & (df["close_lag1"] > df["linreg_lower20"].shift(1)),
        (df["Close"] > df["linreg_upper20"]) & (df["close_lag1"] < df["linreg_upper20"].shift(1)),
    )
    df["hurst_exponent_signal"] = (df["hurst_proxy"] < 0.5).fillna(False)
    df["vpt_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(5)) & (df["vpt"] > df["vpt"].shift(5)),
        (df["High"] > df["High"].shift(5)) & (df["vpt"] < df["vpt"].shift(5)),
    )
    df["liquidity_sweep_signal"] = _signal_from_conditions(
        (df["Low"] < df["prev_5_low"]) & (df["Close"] > df["prev_5_low"]),
        (df["High"] > df["prev_5_high"]) & (df["Close"] < df["prev_5_high"]),
    )
    df["equal_high_low_sweep_signal"] = _signal_from_conditions(df["equal_low"] & (df["Close"] > df["low_lag1"]), df["equal_high"] & (df["Close"] < df["high_lag1"]))
    df["inside_bar_breakout_signal"] = _signal_from_conditions(
        df["inside_bar_prev"] & (df["Close"] > df["High"].shift(2)),
        df["inside_bar_prev"] & (df["Close"] < df["Low"].shift(2)),
    )
    df["fakey_pattern_signal"] = _signal_from_conditions(
        (df["Low"] < df["prev_5_low"]) & (df["Close"] > df["Open"]),
        (df["High"] > df["prev_5_high"]) & (df["Close"] < df["Open"]),
    )
    df["pin_bar_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * df["upwick"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * df["lowwick"]) & (df["Close"] < df["Open"]),
    )
    df["engulfing_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Open"] < df["close_lag1"]) & (df["Close"] > df["open_lag1"]),
        (df["Close"] < df["Open"]) & (df["Open"] > df["close_lag1"]) & (df["Close"] < df["open_lag1"]),
    )
    compression = df["std5"] < (df["std20"] * 0.5)
    df["compression_breakout_signal"] = _signal_from_conditions(compression & (df["Close"] > df["Close"].rolling(config.micro_lookback).max().shift(1)), compression & (df["Close"] < df["Close"].rolling(config.micro_lookback).min().shift(1)))
    df["atr_expansion_signal"] = _signal_from_conditions(
        (df["atr"] > df["atr_sma20"] * 1.5) & (df["Close"] > df["close_lag1"]),
        (df["atr"] > df["atr_sma20"] * 1.5) & (df["Close"] < df["close_lag1"]),
    )
    df["zscore_reversion_signal"] = _signal_from_conditions(df["close_zscore"] < -2, df["close_zscore"] > 2)
    df["range_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_10_high"], df["Close"] < df["prev_10_low"])
    df["volume_spike_signal"] = _signal_from_conditions(
        (df["Volume"] > df["volume_sma20"] * 2) & (df["Close"] > df["Open"]),
        (df["Volume"] > df["volume_sma20"] * 2) & (df["Close"] < df["Open"]),
    )
    df["return_momentum_signal"] = _signal_from_conditions(df["return_5"] > 0.02, df["return_5"] < -0.02)
    df["volatility_break_signal"] = _signal_from_conditions(df["std10"] > df["std50"], df["std10"] < df["std50"])
    df["mean_cross_signal"] = _signal_from_conditions(
        (df["Close"] > df["sma20"]) & (df["close_lag1"] < df["sma20"].shift(1)),
        (df["Close"] < df["sma20"]) & (df["close_lag1"] > df["sma20"].shift(1)),
    )
    df["high_low_break_signal"] = _signal_from_conditions(df["Close"] > df["high_lag1"], df["Close"] < df["low_lag1"])
    df["range_compression_signal"] = _signal_from_conditions(
        (df["height"] < df["range_sma20"] * 0.5) & (df["Close"] >= df["sma20"]),
        (df["height"] < df["range_sma20"] * 0.5) & (df["Close"] < df["sma20"]),
    )
    df["gap_up_down_signal"] = _signal_from_conditions(df["Open"] > df["high_lag1"], df["Open"] < df["low_lag1"])
    df["body_size_signal"] = _signal_from_conditions(
        (df["body_abs"] > df["body_abs_sma20"] * 2) & (df["Close"] > df["Open"]),
        (df["body_abs"] > df["body_abs_sma20"] * 2) & (df["Close"] < df["Open"]),
    )
    df["wick_rejection_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * df["body_abs"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * df["body_abs"]) & (df["Close"] < df["Open"]),
    )
    df["trend_strength_signal"] = _signal_from_conditions(
        (df["Close"] > df["sma50"]) & (df["sma20"] > df["sma50"]),
        (df["Close"] < df["sma50"]) & (df["sma20"] < df["sma50"]),
    )
    df["pullback_signal"] = _signal_from_conditions(
        (df["Close"] < df["sma20"]) & (df["sma20"] > df["sma50"]),
        (df["Close"] > df["sma20"]) & (df["sma20"] < df["sma50"]),
    )
    df["break_retest_signal"] = _signal_from_conditions(
        (df["close_lag1"] > df["high_10"].shift(2)) & (df["Close"] < df["close_lag1"]),
        (df["close_lag1"] < df["low_10"].shift(2)) & (df["Close"] > df["close_lag1"]),
    )
    df["momentum_shift_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)),
    )
    df["range_mid_reversion_signal"] = _signal_from_conditions(df["Close"] < df["range_mid_10"], df["Close"] > df["range_mid_10"])
    df["volatility_drop_signal"] = _signal_from_conditions(
        (df["std5"] < df["std20"] * 0.5) & (df["Close"] >= df["sma20"]),
        (df["std5"] < df["std20"] * 0.5) & (df["Close"] < df["sma20"]),
    )
    df["price_acceleration_signal"] = _signal_from_conditions(df["price_change"] > df["price_change_lag1"], df["price_change"] < df["price_change_lag1"])
    df["extreme_move_signal"] = _signal_from_conditions(df["return_10"] > 0.05, df["return_10"] < -0.05)
    df["mean_distance_signal"] = _signal_from_conditions(df["Close"] < (df["sma20"] * 0.95), df["Close"] > (df["sma20"] * 1.05))
    df["range_shift_signal"] = _signal_from_conditions(df["low_5"] > df["low_10"], df["high_5"] < df["high_10"])
    df["volume_trend_signal"] = _signal_from_conditions(
        (df["Volume"] > df["volume_lag1"]) & (df["volume_lag1"] > df["Volume"].shift(2)),
        (df["Volume"] < df["volume_lag1"]) & (df["volume_lag1"] < df["Volume"].shift(2)),
    )
    df["price_rejection_signal"] = _signal_from_conditions(
        (df["Low"] < df["low_lag1"]) & (df["Close"] > df["Open"]),
        (df["High"] > df["high_lag1"]) & (df["Close"] < df["Open"]),
    )
    df["micro_trend_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)),
    )
    df["micro_reversal_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)),
    )
    df["range_expansion_signal"] = _signal_from_conditions(
        (df["height"] > df["range_sma20"] * 1.5) & (df["Close"] > df["Open"]),
        (df["height"] > df["range_sma20"] * 1.5) & (df["Close"] < df["Open"]),
    )
    df["body_direction_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["close_lag1"] > df["open_lag1"]),
        (df["Close"] < df["Open"]) & (df["close_lag1"] < df["open_lag1"]),
    )
    df["range_position_signal"] = _signal_from_conditions(df["Close"] < df["lower_range_pos"], df["Close"] > df["upper_range_pos"])
    df["close_strength_signal"] = _signal_from_conditions(
        (df["Close"] > df["midpoint"]) & (df["Close"] > df["Open"]),
        (df["Close"] < df["midpoint"]) & (df["Close"] < df["Open"]),
    )
    df["trend_exhaustion_signal"] = _signal_from_conditions(
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)) & (df["Close"].shift(2) > df["Close"].shift(3)),
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)) & (df["Close"].shift(2) < df["Close"].shift(3)),
    )
    df["range_flip_signal"] = _signal_from_conditions(df["Close"] > df["prev_5_high"], df["Close"] < df["prev_5_low"])
    df["vol_price_divergence_signal"] = _signal_from_conditions(
        (df["Close"] < df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
        (df["Close"] > df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
    )
    df["final_push_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
    )

    return df
