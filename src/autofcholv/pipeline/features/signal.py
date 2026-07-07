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
    "sig_hma20",
    "sig_kama10",
    "sig_trix15",
    "sig_trix15_signal",
    "sig_supertrend_dir",
    "sig_tenkan",
    "sig_kijun",
    "sig_span_a",
    "sig_span_b",
    "sig_linreg_slope20",
    "sig_linreg_mid20",
    "sig_tma10",
    "sig_stoch_rsi",
    "sig_ao",
    "sig_roc10",
    "sig_ultimate_osc",
    "sig_stochrsi_k",
    "sig_stochrsi_d",
    "sig_bb_width",
    "sig_kc_mid",
    "sig_kc_upper",
    "sig_kc_lower",
    "sig_chop14",
    "sig_hurst_proxy",
    "sig_mfi14",
    "sig_vpt",
    "sig_fractal_high_ffill",
    "sig_fractal_low_ffill",
    "sig_connors_rsi",
]


def _signal_from_conditions(buy_condition: pd.Series, sell_condition: pd.Series) -> pd.Series:
    buy = buy_condition.fillna(False)
    sell = sell_condition.fillna(False)
    return pd.Series(
        np.where(buy, BUY_SIGNAL, np.where(sell, SELL_SIGNAL, NONE_SIGNAL)),
        index=buy.index,
    )


def _true_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def _rolling_percentile(series: pd.Series, window: int, quantile: float) -> pd.Series:
    return series.rolling(window).quantile(quantile)


def _prepare_context(df: pd.DataFrame) -> pd.DataFrame:
    ctx = pd.DataFrame(index=df.index)
    candle_range = (df["High"] - df["Low"]).replace(0, np.nan)

    ctx["range"] = df["High"] - df["Low"]
    ctx["body_abs"] = df["body"].abs()
    ctx["body_abs_sma20"] = ctx["body_abs"].rolling(20).mean()
    ctx["range_sma20"] = ctx["range"].rolling(20).mean()
    ctx["midpoint"] = (df["High"] + df["Low"]) / 2.0
    ctx["price_change"] = df["Close"].diff()
    ctx["price_change_lag1"] = ctx["price_change"].shift(1)
    ctx["return_5"] = df["Close"].pct_change(5)
    ctx["return_10"] = df["Close"].pct_change(10)

    ctx["sma20"] = df["Close"].rolling(20).mean()
    ctx["sma50"] = df["Close"].rolling(50).mean()
    ctx["std5"] = df["Close"].rolling(5).std()
    ctx["std10"] = df["Close"].rolling(10).std()
    ctx["std20"] = df["Close"].rolling(20).std()
    ctx["std50"] = df["Close"].rolling(50).std()

    ctx["bb_width"] = df["sig_bb_width"]
    ctx["bb_width_q20"] = _rolling_percentile(ctx["bb_width"], 100, 0.2)
    ctx["bb_width_sma20"] = ctx["bb_width"].rolling(20).mean()

    ctx["close_min_10"] = df["Close"].rolling(10).min()
    ctx["close_max_10"] = df["Close"].rolling(10).max()
    ctx["high_5"] = df["High"].rolling(5).max()
    ctx["low_5"] = df["Low"].rolling(5).min()
    ctx["high_10"] = df["High"].rolling(10).max()
    ctx["low_10"] = df["Low"].rolling(10).min()
    ctx["high_20"] = df["High"].rolling(20).max()
    ctx["low_20"] = df["Low"].rolling(20).min()
    ctx["range_mid_10"] = (ctx["high_10"] + ctx["low_10"]) / 2.0

    ctx["recent_high"] = df["High"].rolling(20).max().shift(1)
    ctx["recent_low"] = df["Low"].rolling(20).min().shift(1)
    ctx["recent_high_prev"] = ctx["recent_high"].shift(5)
    ctx["recent_low_prev"] = ctx["recent_low"].shift(5)

    ctx["volume_sma20"] = df["Volume"].rolling(20).mean()
    ctx["atr_sma20"] = df["atr"].rolling(20).mean()

    ctx["mfi14"] = df["sig_mfi14"]
    ctx["hma20"] = df["sig_hma20"]
    ctx["kama10"] = df["sig_kama10"]
    ctx["trix"] = df["sig_trix15"]
    ctx["trix_signal"] = df["sig_trix15_signal"]
    ctx["stochrsi_k"] = df["sig_stochrsi_k"]
    ctx["stochrsi_d"] = df["sig_stochrsi_d"]
    ctx["supertrend_dir"] = df["sig_supertrend_dir"]

    ctx["aroon_up"] = df["aroon_up"]
    ctx["aroon_down"] = df["aroon_down"]

    ctx["tenkan"] = df["sig_tenkan"]
    ctx["kijun"] = df["sig_kijun"]
    ctx["span_a"] = df["sig_span_a"]
    ctx["span_b"] = df["sig_span_b"]

    ctx["chop14"] = df["sig_chop14"]
    ctx["ao"] = df["sig_ao"]
    ctx["roc10"] = df["sig_roc10"]
    ctx["stoch_rsi_manual"] = df["sig_stoch_rsi"]

    ctx["linreg_slope20"] = df["sig_linreg_slope20"]
    ctx["linreg_mid20"] = df["sig_linreg_mid20"]
    ctx["linreg_upper20"] = ctx["linreg_mid20"] + 2 * ctx["std20"]
    ctx["linreg_lower20"] = ctx["linreg_mid20"] - 2 * ctx["std20"]

    ctx["fractal_high_ffill"] = df["sig_fractal_high_ffill"]
    ctx["fractal_low_ffill"] = df["sig_fractal_low_ffill"]

    ctx["ultimate_manual"] = df["sig_ultimate_osc"]
    ctx["connors_rsi"] = df["sig_connors_rsi"]

    ctx["kc_mid"] = df["sig_kc_mid"]
    ctx["kc_upper"] = df["sig_kc_upper"]
    ctx["kc_lower"] = df["sig_kc_lower"]

    ctx["vpt"] = df["sig_vpt"]
    ctx["tma"] = df["sig_tma10"]
    ctx["hurst_proxy"] = df["sig_hurst_proxy"]
    ctx["lower_range_pos"] = ctx["low_10"] + (ctx["high_10"] - ctx["low_10"]) * 0.3
    ctx["upper_range_pos"] = ctx["high_10"] - (ctx["high_10"] - ctx["low_10"]) * 0.3
    ctx["equal_low"] = (df["Low"] - df["low_lag1"]).abs() < (0.001 * df["Close"])
    ctx["equal_high"] = (df["High"] - df["high_lag1"]).abs() < (0.001 * df["Close"])
    ctx["inside_bar_prev"] = (df["high_lag1"] < df["High"].shift(2)) & (df["low_lag1"] > df["Low"].shift(2))
    ctx["prev_5_low"] = ctx["low_5"].shift(1)
    ctx["prev_5_high"] = ctx["high_5"].shift(1)
    ctx["prev_10_low"] = ctx["low_10"].shift(1)
    ctx["prev_10_high"] = ctx["high_10"].shift(1)
    ctx["prev_20_low"] = ctx["low_20"].shift(1)
    ctx["prev_20_high"] = ctx["high_20"].shift(1)
    ctx["close_vs_mid"] = df["Close"] - ctx["midpoint"]
    ctx["candle_range_ratio"] = ctx["body_abs"] / candle_range

    return ctx


def extract_features(df: pd.DataFrame, _config: Config) -> pd.DataFrame:
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    ctx = _prepare_context(df)

    cond1_sell = (df["open_lag1"] > df["close_lag1"]) & (df["close_lag1"] >= df["low_lag1"] + 0.1)
    cond2_sell = (df["Open"] > df["Close"]) & (df["Close"] == df["Low"]) & (df["Low"] < df["low_lag1"])
    cond1_buy = (df["open_lag1"] < df["close_lag1"]) & (df["close_lag1"] <= df["high_lag1"] - 0.1)
    cond2_buy = (df["Open"] < df["Close"]) & (df["Close"] == df["High"]) & (df["High"] > df["high_lag1"])
    df["couple_cs_signal"] = _signal_from_conditions(cond1_buy & cond2_buy, cond1_sell & cond2_sell)

    ema_bullish = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast_lag1"] <= df["ema_slow_lag1"])
    ema_bearish = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast_lag1"] >= df["ema_slow_lag1"])
    df["ema_cross_signal"] = _signal_from_conditions(ema_bullish, ema_bearish)

    df["min_max_10_signal"] = _signal_from_conditions(
        (df["Close"] == ctx["close_min_10"]) & (df["rsi"] < 30),
        (df["Close"] == ctx["close_max_10"]) & (df["rsi"] > 70),
    )

    is_max_macd_hist = df["macd_hist"] == df["macd_hist"].rolling(10).max()
    is_min_macd_hist = df["macd_hist"] == df["macd_hist"].rolling(10).min()
    df["macd_histogram_reversal_signal"] = _signal_from_conditions(
        (df["open_lag1"] >= df["close_lag1"])
        & (df["macd_hist"] < 0)
        & is_min_macd_hist.shift(1).fillna(False)
        & (df["macd_hist"].rolling(5).sum() < 0)
        & (df["Close"] > df["open_lag1"])
        & ((df["Close"] - df["low_lag1"]) < 5),
        (df["open_lag1"] <= df["close_lag1"])
        & (df["macd_hist"] > 0)
        & is_max_macd_hist.shift(1).fillna(False)
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
        (ctx["bb_width"] < ctx["bb_width_q20"]) & (df["Close"] > df["ub"]),
        (ctx["bb_width"] < ctx["bb_width_q20"]) & (df["Close"] < df["lb"]),
    )
    df["rsi_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(5)) & (df["rsi"] > df["rsi"].shift(5)),
        (df["High"] > df["High"].shift(5)) & (df["rsi"] < df["rsi"].shift(5)),
    )
    df["atr_breakout_signal"] = _signal_from_conditions(
        (ctx["range"] > 1.5 * df["atr"]) & (df["Close"] > df["Open"]),
        (ctx["range"] > 1.5 * df["atr"]) & (df["Close"] < df["Open"]),
    )
    df["vsa_confirmation_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Volume"] > 1.2 * ctx["volume_sma20"]),
        (df["Close"] < df["Open"]) & (df["Volume"] > 1.2 * ctx["volume_sma20"]),
    )

    cloud_top = pd.concat([ctx["span_a"], ctx["span_b"]], axis=1).max(axis=1)
    cloud_bottom = pd.concat([ctx["span_a"], ctx["span_b"]], axis=1).min(axis=1)
    df["ichimoku_cloud_signal"] = _signal_from_conditions(
        (df["Close"] > cloud_top) & (ctx["tenkan"] > ctx["kijun"]),
        (df["Close"] < cloud_bottom) & (ctx["tenkan"] < ctx["kijun"]),
    )
    df["ma_stretch_signal"] = _signal_from_conditions(df["close_zscore"] < -2, df["close_zscore"] > 2)
    df["market_structure_break_signal"] = _signal_from_conditions(
        (df["Close"] > ctx["recent_high"]) & (ctx["recent_low"] < ctx["recent_low_prev"]),
        (df["Close"] < ctx["recent_low"]) & (ctx["recent_high"] > ctx["recent_high_prev"]),
    )
    df["bollinger_band_width_signal"] = _signal_from_conditions(
        ctx["bb_width"] < (ctx["bb_width_sma20"] * 0.7),
        ctx["bb_width"] > (ctx["bb_width_sma20"] * 1.3),
    )
    df["volume_confirmation_signal"] = ((df["Volume"] > ctx["volume_sma20"]) & (df["Close"] != df["close_lag1"])).fillna(False)
    df["mfi_rejection_signal"] = _signal_from_conditions(
        (ctx["mfi14"] < 20) & (ctx["mfi14"] > ctx["mfi14"].shift(1)),
        (ctx["mfi14"] > 80) & (ctx["mfi14"] < ctx["mfi14"].shift(1)),
    )
    df["donchian_breakout_signal"] = _signal_from_conditions(df["Close"] > ctx["prev_20_high"], df["Close"] < ctx["prev_20_low"])
    df["hma_reversal_signal"] = _signal_from_conditions(
        (ctx["hma20"] > ctx["hma20"].shift(1)) & (ctx["hma20"].shift(1) < ctx["hma20"].shift(2)),
        (ctx["hma20"] < ctx["hma20"].shift(1)) & (ctx["hma20"].shift(1) > ctx["hma20"].shift(2)),
    )
    df["adx_trend_filter"] = (df["adx"] > 25).fillna(False)
    df["connors_rsi_signal"] = _signal_from_conditions(ctx["connors_rsi"] < 15, ctx["connors_rsi"] > 85)
    df["choppiness_signal"] = (ctx["chop14"] < 38.2).fillna(False)
    df["keltner_channel_reversal"] = _signal_from_conditions(
        (df["Close"] < ctx["kc_lower"]) & (df["close_lag1"] > ctx["kc_lower"].shift(1)),
        (df["Close"] > ctx["kc_upper"]) & (df["close_lag1"] < ctx["kc_upper"].shift(1)),
    )
    df["fractal_breakout_signal"] = _signal_from_conditions(
        df["Close"] > ctx["fractal_high_ffill"].shift(2),
        df["Close"] < ctx["fractal_low_ffill"].shift(2),
    )
    df["supertrend_reversal"] = _signal_from_conditions(
        (ctx["supertrend_dir"] > 0) & (ctx["supertrend_dir"].shift(1) < 0),
        (ctx["supertrend_dir"] < 0) & (ctx["supertrend_dir"].shift(1) > 0),
    )
    df["aroon_oscillator_signal"] = _signal_from_conditions(
        (ctx["aroon_up"] > 70) & (ctx["aroon_down"] < 30),
        (ctx["aroon_down"] > 70) & (ctx["aroon_up"] < 30),
    )
    df["chande_momentum_oscillator_signal"] = _signal_from_conditions(
        (df["cmo"] > 50) & (df["cmo"].shift(1) < 50),
        (df["cmo"] < -50) & (df["cmo"].shift(1) > -50),
    )
    df["ultimate_oscillator_signal"] = _signal_from_conditions(
        (ctx["ultimate_manual"] < 30) & (ctx["ultimate_manual"] > ctx["ultimate_manual"].shift(1)),
        (ctx["ultimate_manual"] > 70) & (ctx["ultimate_manual"] < ctx["ultimate_manual"].shift(1)),
    )
    df["trix_crossover_signal"] = _signal_from_conditions(
        (ctx["trix"] > ctx["trix_signal"]) & (ctx["trix"].shift(1) <= ctx["trix_signal"].shift(1)),
        (ctx["trix"] < ctx["trix_signal"]) & (ctx["trix"].shift(1) >= ctx["trix_signal"].shift(1)),
    )
    df["stochastic_rsi_signal"] = _signal_from_conditions(
        (ctx["stoch_rsi_manual"] < 0.2) & (ctx["stoch_rsi_manual"] > ctx["stoch_rsi_manual"].shift(1)),
        (ctx["stoch_rsi_manual"] > 0.8) & (ctx["stoch_rsi_manual"] < ctx["stoch_rsi_manual"].shift(1)),
    )
    df["awesome_oscillator_signal"] = _signal_from_conditions(
        (ctx["ao"] > 0) & (ctx["ao"].shift(1) < ctx["ao"]),
        (ctx["ao"] < 0) & (ctx["ao"].shift(1) > ctx["ao"]),
    )
    df["rate_of_change_signal"] = _signal_from_conditions(
        (ctx["roc10"] > 0) & (ctx["roc10"].shift(1) < ctx["roc10"]),
        (ctx["roc10"] < 0) & (ctx["roc10"].shift(1) > ctx["roc10"]),
    )
    df["price_channel_breakout_signal"] = _signal_from_conditions(df["Close"] > ctx["prev_20_high"], df["Close"] < ctx["prev_20_low"])
    df["linear_regression_slope_signal"] = _signal_from_conditions(
        (ctx["linreg_slope20"] > 0) & (ctx["linreg_slope20"].shift(1) < ctx["linreg_slope20"]),
        (ctx["linreg_slope20"] < 0) & (ctx["linreg_slope20"].shift(1) > ctx["linreg_slope20"]),
    )
    df["zig_zag_reversal_signal"] = _signal_from_conditions(ctx["fractal_low"].notna(), ctx["fractal_high"].notna())
    df["kaufman_ama_signal"] = _signal_from_conditions(
        (ctx["kama10"] > ctx["kama10"].shift(1)) & (ctx["kama10"].shift(1) < ctx["kama10"].shift(2)),
        (ctx["kama10"] < ctx["kama10"].shift(1)) & (ctx["kama10"].shift(1) > ctx["kama10"].shift(2)),
    )
    df["tma_reversal_signal"] = _signal_from_conditions(
        (df["Close"] > ctx["tma"]) & (df["close_lag1"] < ctx["tma"].shift(1)),
        (df["Close"] < ctx["tma"]) & (df["close_lag1"] > ctx["tma"].shift(1)),
    )
    df["linear_regression_channel_signal"] = _signal_from_conditions(
        (df["Close"] < ctx["linreg_lower20"]) & (df["close_lag1"] > ctx["linreg_lower20"].shift(1)),
        (df["Close"] > ctx["linreg_upper20"]) & (df["close_lag1"] < ctx["linreg_upper20"].shift(1)),
    )
    df["fractal_channel_signal"] = _signal_from_conditions(df["Close"] > ctx["fractal_high_ffill"], df["Close"] < ctx["fractal_low_ffill"])
    df["hurst_exponent_signal"] = (ctx["hurst_proxy"] < 0.5).fillna(False)
    df["vpt_divergence_signal"] = _signal_from_conditions(
        (df["Low"] < df["Low"].shift(5)) & (ctx["vpt"] > ctx["vpt"].shift(5)),
        (df["High"] > df["High"].shift(5)) & (ctx["vpt"] < ctx["vpt"].shift(5)),
    )
    df["liquidity_sweep_signal"] = _signal_from_conditions(
        (df["Low"] < ctx["prev_5_low"]) & (df["Close"] > ctx["prev_5_low"]),
        (df["High"] > ctx["prev_5_high"]) & (df["Close"] < ctx["prev_5_high"]),
    )
    df["equal_high_low_sweep_signal"] = _signal_from_conditions(ctx["equal_low"] & (df["Close"] > df["low_lag1"]), ctx["equal_high"] & (df["Close"] < df["high_lag1"]))
    df["inside_bar_breakout_signal"] = _signal_from_conditions(
        ctx["inside_bar_prev"] & (df["Close"] > df["High"].shift(2)),
        ctx["inside_bar_prev"] & (df["Close"] < df["Low"].shift(2)),
    )
    df["fakey_pattern_signal"] = _signal_from_conditions(
        (df["Low"] < ctx["prev_5_low"]) & (df["Close"] > df["Open"]),
        (df["High"] > ctx["prev_5_high"]) & (df["Close"] < df["Open"]),
    )
    df["pin_bar_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * df["upwick"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * df["lowwick"]) & (df["Close"] < df["Open"]),
    )
    df["engulfing_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["Open"] < df["close_lag1"]) & (df["Close"] > df["open_lag1"]),
        (df["Close"] < df["Open"]) & (df["Open"] > df["close_lag1"]) & (df["Close"] < df["open_lag1"]),
    )
    compression = ctx["std5"] < (ctx["std20"] * 0.5)
    df["compression_breakout_signal"] = _signal_from_conditions(compression & (df["Close"] > df["Close"].rolling(5).max().shift(1)), compression & (df["Close"] < df["Close"].rolling(5).min().shift(1)))
    df["atr_expansion_signal"] = _signal_from_conditions(
        (df["atr"] > ctx["atr_sma20"] * 1.5) & (df["Close"] > df["close_lag1"]),
        (df["atr"] > ctx["atr_sma20"] * 1.5) & (df["Close"] < df["close_lag1"]),
    )
    df["zscore_reversion_signal"] = _signal_from_conditions(df["close_zscore"] < -2, df["close_zscore"] > 2)
    df["range_breakout_signal"] = _signal_from_conditions(df["Close"] > ctx["prev_10_high"], df["Close"] < ctx["prev_10_low"])
    df["volume_spike_signal"] = _signal_from_conditions(
        (df["Volume"] > ctx["volume_sma20"] * 2) & (df["Close"] > df["Open"]),
        (df["Volume"] > ctx["volume_sma20"] * 2) & (df["Close"] < df["Open"]),
    )
    df["return_momentum_signal"] = _signal_from_conditions(ctx["return_5"] > 0.02, ctx["return_5"] < -0.02)
    df["volatility_break_signal"] = _signal_from_conditions(ctx["std10"] > ctx["std50"], ctx["std10"] < ctx["std50"])
    df["mean_cross_signal"] = _signal_from_conditions(
        (df["Close"] > ctx["sma20"]) & (df["close_lag1"] < ctx["sma20"].shift(1)),
        (df["Close"] < ctx["sma20"]) & (df["close_lag1"] > ctx["sma20"].shift(1)),
    )
    df["high_low_break_signal"] = _signal_from_conditions(df["Close"] > df["high_lag1"], df["Close"] < df["low_lag1"])
    df["range_compression_signal"] = _signal_from_conditions(
        (ctx["range"] < ctx["range_sma20"] * 0.5) & (df["Close"] >= ctx["sma20"]),
        (ctx["range"] < ctx["range_sma20"] * 0.5) & (df["Close"] < ctx["sma20"]),
    )
    df["gap_up_down_signal"] = _signal_from_conditions(df["Open"] > df["high_lag1"], df["Open"] < df["low_lag1"])
    df["body_size_signal"] = _signal_from_conditions(
        (ctx["body_abs"] > ctx["body_abs_sma20"] * 2) & (df["Close"] > df["Open"]),
        (ctx["body_abs"] > ctx["body_abs_sma20"] * 2) & (df["Close"] < df["Open"]),
    )
    df["wick_rejection_signal"] = _signal_from_conditions(
        (df["lowwick"] > 2 * ctx["body_abs"]) & (df["Close"] > df["Open"]),
        (df["upwick"] > 2 * ctx["body_abs"]) & (df["Close"] < df["Open"]),
    )
    df["trend_strength_signal"] = _signal_from_conditions(
        (df["Close"] > ctx["sma50"]) & (ctx["sma20"] > ctx["sma50"]),
        (df["Close"] < ctx["sma50"]) & (ctx["sma20"] < ctx["sma50"]),
    )
    df["pullback_signal"] = _signal_from_conditions(
        (df["Close"] < ctx["sma20"]) & (ctx["sma20"] > ctx["sma50"]),
        (df["Close"] > ctx["sma20"]) & (ctx["sma20"] < ctx["sma50"]),
    )
    df["break_retest_signal"] = _signal_from_conditions(
        (df["close_lag1"] > ctx["high_10"].shift(2)) & (df["Close"] < df["close_lag1"]),
        (df["close_lag1"] < ctx["low_10"].shift(2)) & (df["Close"] > df["close_lag1"]),
    )
    df["momentum_shift_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)),
    )
    df["range_mid_reversion_signal"] = _signal_from_conditions(df["Close"] < ctx["range_mid_10"], df["Close"] > ctx["range_mid_10"])
    df["volatility_drop_signal"] = _signal_from_conditions(
        (ctx["std5"] < ctx["std20"] * 0.5) & (df["Close"] >= ctx["sma20"]),
        (ctx["std5"] < ctx["std20"] * 0.5) & (df["Close"] < ctx["sma20"]),
    )
    df["price_acceleration_signal"] = _signal_from_conditions(ctx["price_change"] > ctx["price_change_lag1"], ctx["price_change"] < ctx["price_change_lag1"])
    df["extreme_move_signal"] = _signal_from_conditions(ctx["return_10"] > 0.05, ctx["return_10"] < -0.05)
    df["mean_distance_signal"] = _signal_from_conditions(df["Close"] < (ctx["sma20"] * 0.95), df["Close"] > (ctx["sma20"] * 1.05))
    df["range_shift_signal"] = _signal_from_conditions(ctx["low_5"] > ctx["low_10"], ctx["high_5"] < ctx["high_10"])
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
        (ctx["range"] > ctx["range_sma20"] * 1.5) & (df["Close"] > df["Open"]),
        (ctx["range"] > ctx["range_sma20"] * 1.5) & (df["Close"] < df["Open"]),
    )
    df["body_direction_signal"] = _signal_from_conditions(
        (df["Close"] > df["Open"]) & (df["close_lag1"] > df["open_lag1"]),
        (df["Close"] < df["Open"]) & (df["close_lag1"] < df["open_lag1"]),
    )
    df["range_position_signal"] = _signal_from_conditions(df["Close"] < ctx["lower_range_pos"], df["Close"] > ctx["upper_range_pos"])
    df["close_strength_signal"] = _signal_from_conditions(
        (df["Close"] > ctx["midpoint"]) & (df["Close"] > df["Open"]),
        (df["Close"] < ctx["midpoint"]) & (df["Close"] < df["Open"]),
    )
    df["trend_exhaustion_signal"] = _signal_from_conditions(
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)) & (df["Close"].shift(2) > df["Close"].shift(3)),
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)) & (df["Close"].shift(2) < df["Close"].shift(3)),
    )
    df["range_flip_signal"] = _signal_from_conditions(df["Close"] > ctx["prev_5_high"], df["Close"] < ctx["prev_5_low"])
    df["vol_price_divergence_signal"] = _signal_from_conditions(
        (df["Close"] < df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
        (df["Close"] > df["close_lag1"]) & (df["Volume"] > df["volume_lag1"]),
    )
    df["final_push_signal"] = _signal_from_conditions(
        (df["Close"] > df["close_lag1"]) & (df["close_lag1"] > df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
        (df["Close"] < df["close_lag1"]) & (df["close_lag1"] < df["Close"].shift(2)) & (df["Volume"] < df["volume_lag1"]),
    )

    return df
