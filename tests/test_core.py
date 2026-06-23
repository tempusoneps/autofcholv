import json
import os
import tempfile

import pandas as pd
import numpy as np
import pytest
from autofcholv.core import extract_features
from autofcholv.config.config import load_config, DEFAULT_CONFIG


# ─────────────────────────────────────────────
# Helper: make synthetic 5-minute OHLCV data
# ─────────────────────────────────────────────

def make_ohlcv(n_bars: int = 300) -> pd.DataFrame:
    n_bars = max(n_bars, 7000)
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]

    rng    = np.random.default_rng(42)
    close  = 100.0 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    close  = np.maximum(close, 10.0)
    open_  = close * (1 + rng.normal(0, 0.001, len(idx)))
    high   = close * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    low    = close * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    volume = rng.integers(1000, 10000, len(idx)).astype(float)

    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
    df.index.name = "Date"
    df["High"] = df[["Open", "Close", "High"]].max(axis=1)
    df["Low"]  = df[["Open", "Close", "Low"]].min(axis=1)
    return df


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_extract_features_returns_dataframe():
    result = extract_features(make_ohlcv(300))
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_extract_features_time_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["hour", "minute", "time_int", "day_of_week", "day_of_month", "month", "year", "session_progress"]
    for col in expected:
        assert col in result.columns, f"Missing time column: '{col}'"


def test_extract_features_resample_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "prev_day_open", "prev_day_high", "prev_day_low", "prev_day_close",
        "prev_day_volume", "prev_day_pivot",
    ]
    for col in expected:
        assert col in result.columns, f"Missing resample column: '{col}'"

    leaking_cols = [
        "day_open", "day_high", "day_low", "day_close", "day_volume", "day_pivot",
    ]
    for col in leaking_cols:
        assert col not in result.columns, f"Leaking current-day column should be dropped: '{col}'"


def test_extract_features_candlestick_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "body", "height", "upwick", "lowwick",
        "upwick_rate", "lowwick_rate", "body_rate",
        "clv", "cbr", "ibs", "color",
        "wick_imbalance", "upwick_ratio",
    ]
    for col in expected:
        assert col in result.columns, f"Missing candlestick column: '{col}'"


def test_extract_features_close_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ema_fast", "ema_slow", "rsi", "rsi_slope",
        "tsi", "roc_close", "close_zscore", "efficiency_ratio",
        "macd", "macd_signal", "macd_hist",
        "ppo", "ppo_signal", "ppo_hist",
        "ulcer_index", "cmo", "roc_skew", "roc_kurt",
        "mb", "std", "ub", "lb",
        "cci", "kdj_k", "kdj_d", "kdj_j", "fisher",
        "kama", "kama_bias", "high_ma_bias",
        "bollinger_width", "bollinger_percent_b",
        "change_std", "dpo", "pfe",
        "williams_r", "slow_stoch_d", "coppock", "pmo", "smi", "psy",
        "return_autocorr", "demarker", "imi", "rvi", "bop", "ultimate_oscillator_src",
        "kst", "rmi", "tii",
        "ar", "br", "cr", "adtm", "qstick", "mtm",
        "bias", "rbias", "mtm_mean", "mtm_max_diff", "sroc", "rsi_mean", "tdi", "osc", "short_quiet_momentum", "long_quiet_momentum", "price_volume_momentum", "dbcd", "pmarp", "pos", "bias36", "swing_index", "rsi_v2", "cmo_v2", "bias_v13", "abs_chg", "stc", "return_autocorr_2", "erbull", "erbear", "er_balance", "burr", "do", "po", "cci_magic", "cs_mtm", "rsi_bbw", "rccd", "rccd_v2", "bias_vol", "bias_cubic_v2", "srocvol", "copp_min_route", "adtm_v2", "adtm_v3", "mtm_mean_gap", "cmo_v3", "rsis_v2", "mtm_vol_resonance", "tii_signal", "tii_signal_v2", "macd_v2", "ppo_v1", "sroc_v2", "pmo_tema", "fisher_v2", "fisher_v3", "arbr_ar", "arbr_br",
    ]
    for col in expected:
        assert col in result.columns, f"Missing close column: '{col}'"


def test_extract_features_trend_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "dema_bias", "tema_bias", "trix",
        "aroon_up", "aroon_down", "aroon_osc",
        "vortex_plus", "vortex_minus", "vortex_diff",
        "regression_bias", "regression_slope", "ma_signal", "bbi_ratio", "bbi_bias", "adxr_diff", "wma_ma_gap", "adx_strength", "adx_di_plus", "adx_di_minus", "vi_plus", "vi_minus", "turtle_breakout", "turtle_distance", "ma_ratio", "dema_bias2", "tema_bias2", "hma_ratio", "vidya_bias", "tma_bias2", "vma_ratio", "lma_ratio", "mm_ratio", "reg_angle", "expma_ratio", "diff_ema_ratio", "regema_bias", "regtema_bias", "trtrix", "trv", "mac_v4", "mac_v5", "gap_ratio", "angle_reg", "cse", "madis_placed", "trrq", "mreg", "adxr_pos", "adxr_neg", "acs", "mak", "sgcz",
        "hullma_bias", "ichimoku_cloud_ratio", "t3_bias",
    ]
    for col in expected:
        assert col in result.columns, f"Missing trend column: '{col}'"


def test_extract_features_volatility_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "quote_volume_std", "amplitude_max", "positive_amplitude_rank",
        "apz_width", "pac_width_bias", "pac_position", "env_position",
        "realized_volatility", "realized_volatility_zscore",
        "rwi", "mssi", "vix_bw",
        "adaptive_bollinger_width", "vwap_bbw_efficiency", "chaikin_volatility", "keltner_width", "keltner_upper_signal", "keltner_lower_signal", "env_upper_signal", "env_lower_signal", "fibonacci_band_width", "fibonacci_band_position", "donchian_mid_signal", "bbw_signal", "kc_signal", "atr_upper", "atr_lower", "fb_upper_signal", "pac_width_signal",
    ]
    for col in expected:
        assert col in result.columns, f"Missing volatility column: '{col}'"


def test_extract_features_volume_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "volume_avg", "volume_zscore",
        "pvt", "pvt_signal",
        "volume_up_ratio", "volume_down_ratio",
        "money_flow_index", "pvi", "nvi",
        "clv_ma", "wad", "tmf",
        "obv_clv", "cmf", "emv", "force_index", "pvo", "directional_volume_change",
        "quote_volume_reg", "quote_volume_tsf", "price_volume_corr",
        "quote_volume_sum", "volume_bias_short_long", "volume_ratio_amount",
        "adosc", "wvad", "klinger_oscillator", "vra", "ke",
        "roc_volume", "volume_ma_bias", "amv_signal", "volume_ratio", "macd_volume_ratio", "volume_analysis_oscillator", "quote_volume_mean", "quote_volume_ratio", "v1", "v1_up", "v1_down", "mfi_standard", "chla_fancy", "net_vol_fancy", "force_ratio",
    ]
    for col in expected:
        assert col in result.columns, f"Missing volume column: '{col}'"


def test_extract_features_price_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "typical_price", "weighted_close",
        "typical_price_momentum", "weighted_close_bias",
        "rolling_vwap", "vwap_bias", "close_to_vwap",
        "vwap_range_position", "vwap_to_high", "vwap_to_low",
        "close_ma_price", "typical_to_vwap",
    ]
    for col in expected:
        assert col in result.columns, f"Missing price column: '{col}'"


def test_extract_features_liquidity_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "market_placement", "path_liquidity", "spread_proxy",
        "spread_volatility_ratio", "price_volume_resistance", "coppock_atr_volume",
    ]
    for col in expected:
        assert col in result.columns, f"Missing liquidity column: '{col}'"


def test_extract_features_lag_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "open_lag1", "high_lag1", "low_lag1", "close_lag1",
        "volume_lag1", "ibs_lag1", "rsi_lag1",
    ]
    for col in expected:
        assert col in result.columns, f"Missing lag column: '{col}'"


def test_extract_features_mix_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ibs_n", "is_fvg",
        "ulti_osci", "vwap", "atr", "adx",
        "atr_pct",
        "dm", "eom",
        "direction", "streak",
        "custom_001", "custom_002",
        "donchian_width", "donchian_position", "amihud_liquidity",
        "keltner_position",
        "true_range_pct", "gap_pct", "range_position", "body_to_true_range",
    ]
    for col in expected:
        assert col in result.columns, f"Missing mix column: '{col}'"


def test_extract_features_group_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "volume_group", "upper_wick_group", "lower_wick_group",
        "vol_high_pattern", "ibs_volume_pattern",
        "volume_avg_group", "high_rsi_pattern",
        "high_ub_pattern", "low_lb_pattern",
    ]
    for col in expected:
        assert col in result.columns, f"Missing group column: '{col}'"


def test_extract_features_signal_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["couple_cs_signal", "ema_cross_signal"]
    for col in expected:
        assert col in result.columns, f"Missing signal column: '{col}'"


def test_extract_features_no_nan_in_ohlcv():
    result = extract_features(make_ohlcv(300))
    assert result[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum() == 0


def test_extract_features_color_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["color"].unique()).issubset({"green", "red", "doji"})


def test_extract_features_direction_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["direction"].unique()).issubset({1, -1})


def test_extract_features_signal_values():
    result = extract_features(make_ohlcv(300))
    valid = {"None", "Bullish", "Bearish"}
    assert set(result["couple_cs_signal"].unique()).issubset(valid)
    assert set(result["ema_cross_signal"].unique()).issubset(valid)


def test_extract_features_candlestick_non_negative():
    result = extract_features(make_ohlcv(300))
    assert (result["height"] >= 0).all()
    assert (result["upwick"] >= 0).all()
    assert (result["lowwick"] >= 0).all()


def test_extract_features_missing_columns_raises():
    df = pd.DataFrame({"Close": [100.0, 101.0], "Volume": [1000.0, 1100.0]})
    df.index = pd.date_range("2024-01-02 09:05", periods=2, freq="5min")
    with pytest.raises(ValueError):
        extract_features(df)


def test_extract_features_negative_price_raises():
    df = make_ohlcv(50)
    df.iloc[5, df.columns.get_loc("Close")] = -1.0
    df.iloc[5, df.columns.get_loc("Low")]   = -1.0
    with pytest.raises(ValueError):
        extract_features(df)


# ─────────────────────────────────────────────
# Config tests
# ─────────────────────────────────────────────

def test_load_config_sets_defaults():
    for key in DEFAULT_CONFIG:
        os.environ.pop(key, None)
    load_config()
    for key, value in DEFAULT_CONFIG.items():
        assert os.environ.get(key) == value, f"Missing default for {key}"


def test_load_config_from_json_file():
    for key in DEFAULT_CONFIG:
        os.environ.pop(key, None)

    custom = dict(DEFAULT_CONFIG)
    custom["SELECTED_TIME_FRAME"] = "15m"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(custom, f)
        json_path = f.name

    try:
        load_config(json_path)
        assert os.environ.get("SELECTED_TIME_FRAME") == "15m"
    finally:
        os.unlink(json_path)
        for key in DEFAULT_CONFIG:
            os.environ.pop(key, None)


def test_load_config_env_takes_priority():
    for key, value in DEFAULT_CONFIG.items():
        os.environ[key] = value
    os.environ["SELECTED_TIME_FRAME"] = "1h"
    load_config()
    assert os.environ.get("SELECTED_TIME_FRAME") == "1h"
    for key in DEFAULT_CONFIG:
        os.environ.pop(key, None)
