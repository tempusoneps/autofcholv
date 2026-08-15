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
    "rsi_medium",
    "rsi_medium_lag1",
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
    "atr_medium",
    "adx",
    "direction",
    "streak",
    "aroon_up",
    "aroon_down",
    "hma_medium",
    "kama_short",
    "trix15",
    "trix15_signal",
    "supertrend_dir",
    "tenkan",
    "kijun",
    "span_a",
    "span_b",
    "linreg_slope_medium",
    "linreg_mid_medium",
    "tma_short",
    "stoch_rsi",
    "awesome_oscillator",
    "roc_short",
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
    "body_abs_sma_medium",
    "range_sma_medium",
    "midpoint",
    "price_change",
    "price_change_lag1",
    "return_micro",
    "return_short",
    "sma_medium",
    "sma_long",
    "std_micro",
    "std_short",
    "std_medium",
    "std_long",
    "bb_width_q20",
    "bb_width_sma_medium",
    "close_min_short",
    "close_max_short",
    "high_micro",
    "low_micro",
    "high_short",
    "low_short",
    "high_medium",
    "low_medium",
    "range_mid_short",
    "recent_high",
    "recent_low",
    "recent_high_prev",
    "recent_low_prev",
    "volume_sma_medium",
    "atr_sma_medium",
    "linreg_upper_medium",
    "linreg_lower_medium",
    "lower_range_pos",
    "upper_range_pos",
    "equal_low",
    "equal_high",
    "inside_bar_prev",
    "prev_micro_low",
    "prev_micro_high",
    "prev_short_low",
    "prev_short_high",
    "prev_medium_low",
    "prev_medium_high",
    "close_vs_mid",
    "candle_range_ratio",
]


def _signal_from_conditions(buy: pd.Series, sell: pd.Series) -> pd.Series:
    buy_clean = buy.fillna(False).astype(bool)
    sell_clean = sell.fillna(False).astype(bool)
    return pd.Series(
        np.select(
            [
                buy_clean & ~sell_clean,
                sell_clean & ~buy_clean,
            ],
            [1, -1],
            default=0,
        ),
        index=buy.index,
        dtype=int,
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

    df["min_max_short_signal"] = _signal_from_conditions(
        (df["Close"] == df["close_min_short"]) & (df["rsi_medium"] < 30),
        (df["Close"] == df["close_max_short"]) & (df["rsi_medium"] > 70),
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
        & (df["rsi_medium"] < 35)
        & (df["lowwick"] > df["body"].abs())
        & (df["long_trend"] == "StrongUp"),
        (df["High"] > df["ub"])
        & (df["Close"] < df["ub"])
        & (df["rsi_medium"] > 65)
        & (df["upwick"] > df["body"].abs())
        & (df["long_trend"] == "StrongDown"),
    )

    df["bb_squeeze_signal"] = _signal_from_conditions(
        (df["bb_width"] < df["bb_width_q20"]) & (df["Close"] > df["ub"]),
        (df["bb_width"] < df["bb_width_q20"]) & (df["Close"] < df["lb"]),
    )
    df["rsi_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(config.micro_lookback)) & (df["rsi_medium"] > df["rsi_medium"].shift(config.micro_lookback)),
        (df["High"] > df["High"].shift(config.micro_lookback)) & (df["rsi_medium"] < df["rsi_medium"].shift(config.micro_lookback)),
    )
    df["atr_breakout_signal"] = _signal_from_conditions(
        (df["height"] > 1.5 * df["atr_medium"]) & (df["Close"] > df["Open"]),
        (df["height"] > 1.5 * df["atr_medium"]) & (df["Close"] < df["Open"]),
    )
    df["vsa_confirmation_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Volume"] > 1.2 * df["volume_sma_medium"]),
        (df["Close"] < df["Open"]) & (df["Volume"] > 1.2 * df["volume_sma_medium"]),
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
        df["bb_width"] < (df["bb_width_sma_medium"] * 0.7),
        df["bb_width"] > (df["bb_width_sma_medium"] * 1.3),
    )
    df["volume_confirmation_signal"] = ((df["Volume"] > df["volume_sma_medium"]) & (df["Close"] != df["close_lag1"])).fillna(False)
    df["mfi_rejection_signal"] = _signal_from_conditions(
        (df["mfi14"] < 20) & (df["mfi14"] > df["mfi14"].shift(1)),
        (df["mfi14"] > 80) & (df["mfi14"] < df["mfi14"].shift(1)),
    )
    df["donchian_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_medium_high"], df["Close"] < df["prev_medium_low"])
    df["hma_reversal_signal"] = _signal_from_conditions(
        (df["hma_medium"] > df["hma_medium"].shift(1)) & (df["hma_medium"].shift(1) < df["hma_medium"].shift(2)),
        (df["hma_medium"] < df["hma_medium"].shift(1)) & (df["hma_medium"].shift(1) > df["hma_medium"].shift(2)),
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
        (df["roc_short"] > 0) & (df["roc_short"].shift(1) < df["roc_short"]),
        (df["roc_short"] < 0) & (df["roc_short"].shift(1) > df["roc_short"]),
    )
    df["price_channel_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_medium_high"], df["Close"] < df["prev_medium_low"])
    df["linear_regression_slope_signal"] = _signal_from_conditions(
        (df["linreg_slope_medium"] > 0) & (df["linreg_slope_medium"].shift(1) < df["linreg_slope_medium"]),
        (df["linreg_slope_medium"] < 0) & (df["linreg_slope_medium"].shift(1) > df["linreg_slope_medium"]),
    )
    df["kaufman_ama_signal"] = _signal_from_conditions(
        (df["kama_short"] > df["kama_short"].shift(1)) & (df["kama_short"].shift(1) < df["kama_short"].shift(2)),
        (df["kama_short"] < df["kama_short"].shift(1)) & (df["kama_short"].shift(1) > df["kama_short"].shift(2)),
    )
    df["tma_reversal_signal"] = _signal_from_conditions(
        (df["Close"] > df["tma_short"]) & (df["close_lag1"] < df["tma_short"].shift(1)),
        (df["Close"] < df["tma_short"]) & (df["close_lag1"] > df["tma_short"].shift(1)),
    )
    df["linear_regression_channel_signal"] = _signal_from_conditions(
        (df["Close"] < df["linreg_lower_medium"]) & (df["close_lag1"] > df["linreg_lower_medium"].shift(1)),
        (df["Close"] > df["linreg_upper_medium"]) & (df["close_lag1"] < df["linreg_upper_medium"].shift(1)),
    )
    df["hurst_exponent_signal"] = (df["hurst_proxy"] < 0.5).fillna(False)
    df["vpt_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(config.micro_lookback)) & (df["vpt"] > df["vpt"].shift(config.micro_lookback)),
        (df["High"] > df["High"].shift(config.micro_lookback)) & (df["vpt"] < df["vpt"].shift(config.micro_lookback)),
    )
    df["liquidity_sweep_signal"] = _signal_from_conditions(
        (df["Low"] < df["prev_micro_low"]) & (df["Close"] > df["prev_micro_low"]),
        (df["High"] > df["prev_micro_high"]) & (df["Close"] < df["prev_micro_high"]),
    )
    df["equal_high_low_sweep_signal"] = _signal_from_conditions(df["equal_low"] & (df["Close"] > df["low_lag1"]), df["equal_high"] & (df["Close"] < df["high_lag1"]))
    df["inside_bar_breakout_signal"] = _signal_from_conditions(
        df["inside_bar_prev"] & (df["Close"] > df["High"].shift(2)),
        df["inside_bar_prev"] & (df["Close"] < df["Low"].shift(2)),
    )
    df["fakey_pattern_signal"] = _signal_from_conditions(
        (df["Low"] < df["prev_micro_low"]) & (df["Close"] > df["Open"]),
        (df["High"] > df["prev_micro_high"]) & (df["Close"] < df["Open"]),
    )
    df["pin_bar_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * df["upwick"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * df["lowwick"]) & (df["Close"] < df["Open"]),
    )
    df["engulfing_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Open"] < df["close_lag1"]) & (df["Close"] > df["open_lag1"]),
        (df["Close"] < df["Open"]) & (df["Open"] > df["close_lag1"]) & (df["Close"] < df["open_lag1"]),
    )
    compression = df["std_micro"] < (df["std_medium"] * 0.5)
    df["compression_breakout_signal"] = _signal_from_conditions(compression & (df["Close"] > df["Close"].rolling(config.micro_lookback).max().shift(1)), compression & (df["Close"] < df["Close"].rolling(config.micro_lookback).min().shift(1)))
    df["atr_expansion_signal"] = _signal_from_conditions(
        (df["atr_medium"] > df["atr_sma_medium"] * 1.5) & (df["Close"] > df["close_lag1"]),
        (df["atr_medium"] > df["atr_sma_medium"] * 1.5) & (df["Close"] < df["close_lag1"]),
    )
    df["zscore_reversion_signal"] = _signal_from_conditions(df["close_zscore"] < -2, df["close_zscore"] > 2)
    df["range_breakout_signal"] = _signal_from_conditions(df["Close"] > df["prev_short_high"], df["Close"] < df["prev_short_low"])
    df["volume_spike_signal"] = _signal_from_conditions(
        (df["Volume"] > df["volume_sma_medium"] * 2) & (df["Close"] > df["Open"]),
        (df["Volume"] > df["volume_sma_medium"] * 2) & (df["Close"] < df["Open"]),
    )
    df["return_momentum_signal"] = _signal_from_conditions(df["return_micro"] > 0.02, df["return_micro"] < -0.02)
    df["volatility_break_signal"] = _signal_from_conditions(df["std_short"] > df["std_long"], df["std_short"] < df["std_long"])
    df["mean_cross_signal"] = _signal_from_conditions(
        (df["Close"] > df["sma_medium"]) & (df["close_lag1"] < df["sma_medium"].shift(1)),
        (df["Close"] < df["sma_medium"]) & (df["close_lag1"] > df["sma_medium"].shift(1)),
    )
    df["high_low_break_signal"] = _signal_from_conditions(df["Close"] > df["high_lag1"], df["Close"] < df["low_lag1"])
    df["range_compression_signal"] = _signal_from_conditions(
        (df["height"] < df["range_sma_medium"] * 0.5) & (df["Close"] >= df["sma_medium"]),
        (df["height"] < df["range_sma_medium"] * 0.5) & (df["Close"] < df["sma_medium"]),
    )
    df["gap_up_down_signal"] = _signal_from_conditions(df["Open"] > df["high_lag1"], df["Open"] < df["low_lag1"])
    df["body_size_signal"] = _signal_from_conditions(
        (df["body_abs"] > df["body_abs_sma_medium"] * 2) & (df["Close"] > df["Open"]),
        (df["body_abs"] > df["body_abs_sma_medium"] * 2) & (df["Close"] < df["Open"]),
    )
    df["wick_rejection_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * df["body_abs"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * df["body_abs"]) & (df["Close"] < df["Open"]),
    )
    df["trend_strength_signal"] = _signal_from_conditions(
        (df["Close"] > df["sma_long"]) & (df["sma_medium"] > df["sma_long"]),
        (df["Close"] < df["sma_long"]) & (df["sma_medium"] < df["sma_long"]),
    )
    df["pullback_signal"] = _signal_from_conditions(
        (df["Close"] < df["sma_medium"]) & (df["sma_medium"] > df["sma_long"]),
        (df["Close"] > df["sma_medium"]) & (df["sma_medium"] < df["sma_long"]),
    )
    df["break_retest_signal"] = _signal_from_conditions(
        (df["close_lag1"] > df["high_short"].shift(2)) & (df["Close"] < df["close_lag1"]),
        (df["close_lag1"] < df["low_short"].shift(2)) & (df["Close"] > df["close_lag1"]),
    )
    df["momentum_shift_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)),
    )
    df["range_mid_reversion_signal"] = _signal_from_conditions(df["Close"] < df["range_mid_short"], df["Close"] > df["range_mid_short"])
    df["volatility_drop_signal"] = _signal_from_conditions(
        (df["std_micro"] < df["std_medium"] * 0.5) & (df["Close"] >= df["sma_medium"]),
        (df["std_micro"] < df["std_medium"] * 0.5) & (df["Close"] < df["sma_medium"]),
    )
    df["price_acceleration_signal"] = _signal_from_conditions(df["price_change"] > df["price_change_lag1"], df["price_change"] < df["price_change_lag1"])
    df["extreme_move_signal"] = _signal_from_conditions(df["return_short"] > 0.05, df["return_short"] < -0.05)
    df["mean_distance_signal"] = _signal_from_conditions(df["Close"] < (df["sma_medium"] * 0.95), df["Close"] > (df["sma_medium"] * 1.05))
    df["range_shift_signal"] = _signal_from_conditions(df["low_micro"] > df["low_short"], df["high_micro"] < df["high_short"])
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
        (df["height"] > df["range_sma_medium"] * 1.5) & (df["Close"] > df["Open"]),
        (df["height"] > df["range_sma_medium"] * 1.5) & (df["Close"] < df["Open"]),
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
    df["range_flip_signal"] = _signal_from_conditions(df["Close"] > df["prev_micro_high"], df["Close"] < df["prev_micro_low"])
    df["vol_price_divergence_signal"] = _signal_from_conditions(
        (df["Close"] < df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
        (df["Close"] > df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
    )
    df["final_push_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
    )

    return df
