import json
import os
import tempfile
import warnings

import pandas as pd
import numpy as np
import pytest
from autofcholv.core import extract_features
from autofcholv.config.config import Config, load_config, DEFAULT_CONFIG
from autofcholv.pipeline.features import close as close_features
from autofcholv.pipeline.features import resample as resample_features
from autofcholv.pipeline.features.close import _rolling_regression_last as close_regression_last
from autofcholv.pipeline.features.trend import _linear_regression_midline, _linear_regression_slope
from autofcholv.pipeline.features.volume import (
    _rolling_regression_forecast as volume_regression_forecast,
    _rolling_regression_last as volume_regression_last,
)
from autofcholv.pipeline.feature_engineering import FEATURE_STEPS


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


def test_close_features_defragments_input_without_performance_warning():
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=180, freq="5min")
    close = pd.Series(np.linspace(100.0, 120.0, len(idx)), index=idx)
    df = pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": np.linspace(1000.0, 2000.0, len(idx)),
        },
        index=idx,
    )
    df.index.name = "Date"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", pd.errors.PerformanceWarning)
        for i in range(140):
            df[f"fragment_{i}"] = i

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = close_features.extract_features(df, Config())

    performance_warnings = [
        warning for warning in caught
        if issubclass(warning.category, pd.errors.PerformanceWarning)
    ]
    assert performance_warnings == []
    assert "ppo_v1" in result.columns


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_extract_features_returns_dataframe():
    result = extract_features(make_ohlcv(300))
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_extract_features_progress_callback_reports_pipeline_steps():
    steps = []
    result = extract_features(make_ohlcv(300), progress_callback=steps.append)

    assert len(result) > 0
    assert steps[0] == "validation"
    assert steps[1] == "cleaning"
    assert "close_features" in steps
    assert steps[-1] == "preprocessing"


def test_extract_features_time_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["hour", "minute", "time_int", "day_of_week", "day_of_month", "month", "year", "session_progress"]
    for col in expected:
        assert col in result.columns, f"Missing time column: '{col}'"


def test_extract_features_removes_duplicate_alias_columns():
    result = extract_features(make_ohlcv(300))
    aliases = {
        "time_code",
        "range",
        "body_ratio",
        "cbr",
        "bar_close_position",
        "stochrsi_k_14_14_3_3",
        "volume_ma_20",
        "AvgPrice",
        "AvgPriceToHigh",
        "AvgPriceToLow",
        "LowPrice",
        "Typ",
        "VwapSignal",
        "Vwap",
        "Wc",
        "MarketPl",
        "MarketPl_v2",
        "Liquidity_v3",
        "Amihud",
        "BidaskSpread",
        "Damaov10",
        "FearGreed_Yidai_v1",
        "Mac_v2",
        "Mac_v3",
        "Mac_v4",
        "Mac_v5",
        "Vidya_v2",
        "Vidya_v3",
        "Vidya_v4",
        "Vidya_v5",
        "Tma_v2",
        "Tma_v3",
        "VolumeStd",
        "Atr",
        "VolumeReg",
        "VolumeTSF",
        "FiRsi",
        "Pvo",
        "VRA",
    }

    assert aliases.isdisjoint(result.columns)


def test_extract_features_resample_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "prev_day_open", "prev_day_high", "prev_day_low", "prev_day_close",
        "prev_day_volume", "prev_day_pivot",
        "prev_day_r1", "prev_day_s1",
        "prev_15m_open", "prev_15m_high", "prev_15m_low", "prev_15m_close",
        "prev_15m_volume", "prev_15m_pivot", "prev_15m_r1", "prev_15m_s1",
        "prev_15m_return",
        "prev_30m_open", "prev_30m_high", "prev_30m_low", "prev_30m_close",
        "prev_30m_volume", "prev_30m_pivot", "prev_30m_r1", "prev_30m_s1",
        "prev_30m_return",
        "prev_1h_open", "prev_1h_high", "prev_1h_low", "prev_1h_close",
        "prev_1h_volume", "prev_1h_pivot", "prev_1h_r1", "prev_1h_s1",
        "prev_1h_return",
    ]
    for col in expected:
        assert col in result.columns, f"Missing resample column: '{col}'"

    leaking_cols = [
        "day_open", "day_high", "day_low", "day_close", "day_volume", "day_pivot",
    ]
    for col in leaking_cols:
        assert col not in result.columns, f"Leaking current-day column should be dropped: '{col}'"


def test_htf_resample_features_non_leakage():
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=12, freq="5min")
    df = pd.DataFrame(
        {
            "Open": [10.0, 12.0, 14.0, 20.0, 22.0, 24.0, 30.0, 32.0, 34.0, 40.0, 42.0, 44.0],
            "High": [11.0, 13.0, 15.0, 21.0, 23.0, 25.0, 31.0, 33.0, 35.0, 41.0, 43.0, 45.0],
            "Low":  [9.0,  11.0, 13.0, 19.0, 21.0, 23.0, 29.0, 31.0, 33.0, 39.0, 41.0, 43.0],
            "Close": [10.5, 12.5, 14.5, 20.5, 22.5, 24.5, 30.5, 32.5, 34.5, 40.5, 42.5, 44.5],
            "Volume": [100.0] * 12,
        },
        index=idx,
    )
    df.index.name = "Date"
    res = resample_features.extract_features(df, Config())

    # Bars at 09:05:00 and 09:10:00 are before first 15m block (09:00-09:15) completion at 09:15:00
    assert np.isnan(res.loc["2024-01-02 09:05:00", "prev_15m_close"])
    assert np.isnan(res.loc["2024-01-02 09:10:00", "prev_15m_close"])

    # At 09:15:00, the 09:00-09:15 block (09:05 and 09:10 bars) is completed
    # prev_15m_close at 09:15:00 should equal the Close of 09:10:00 bar (14.5)
    close_0910 = df.loc["2024-01-02 09:10:00", "Close"]
    assert res.loc["2024-01-02 09:15:00", "prev_15m_close"] == close_0910
    assert res.loc["2024-01-02 09:20:00", "prev_15m_close"] == close_0910

    # At 09:30:00, the 09:15-09:30 block (09:15, 09:20, 09:25 bars) is completed
    close_0925 = df.loc["2024-01-02 09:25:00", "Close"]
    assert res.loc["2024-01-02 09:30:00", "prev_15m_close"] == close_0925






def test_extract_features_candlestick_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "body", "height", "upwick", "lowwick",
        "upwick_rate", "lowwick_rate", "body_rate",
        "clv", "ibs", "color",
        "wick_imbalance", "upwick_ratio",
    ]
    for col in expected:
        assert col in result.columns, f"Missing candlestick column: '{col}'"


def test_extract_features_close_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ema_fast", "ema_slow", "rsi_medium", "rsi_slope_medium", "tsi", "roc_close",
        "close_zscore", "efficiency_ratio", "macd", "macd_line", "macd_hist", "ppo",
        "ppo_line", "ppo_hist", "ulcer_index", "cmo", "roc_skew", "roc_kurt",
        "mb", "std", "ub", "lb", "cci", "kdj_k",
        "kdj_d", "kdj_j", "fisher", "kama", "kama_bias", "high_ma_bias",
        "bollinger_width", "bollinger_percent_b", "change_std", "dpo", "pfe", "williams_r",
        "slow_stoch_d", "coppock", "pmo", "smi", "psy", "return_autocorr",
        "demarker", "imi", "rvi", "bop", "ultimate_oscillator_src", "kst",
        "rmi", "tii", "ar", "br", "cr", "adtm",
        "qstick", "mtm", "bias", "rbias", "mtm_mean", "mtm_max_diff",
        "sroc", "rsi_mean", "tdi", "osc", "short_quiet_momentum", "long_quiet_momentum",
        "price_volume_momentum", "dbcd", "pmarp", "pos", "swing_index",
        "rsi_v2", "cmo_v2", "bias_v13", "abs_chg", "stc", "return_autocorr_2",
        "erbull", "erbear", "er_balance", "burr", "do", "po",
        "cci_magic", "cs_mtm", "cs_mtm_v2", "rsi_bbw", "rccd", "rccd_v2",
        "bias_vol", "bias_cubic_v2", "srocvol", "roc_vol", "copp_min_route", "adtm_v2",
        "adtm_v3", "mtm_mean_gap", "cmo_v3", "rsis_v2", "mtm_vol_resonance", "tii_signal",
        "tii_signal_v2", "macd_v2", "ppo_v1", "sroc_v2", "pmo_tema", "fisher_v2",
        "fisher_v3", "arbr_ar", "arbr_br", "bias_v3", "bias_v4", "bias_v11",
        "bias_v14", "bir", "copp_v3", "roc", "cci_v2",
        "cci_v3", "rsimean", "dbcd_v3", "micd", "rsj", "mtm_max",
        "bias_v2", "rsiv", "rsih", "fi", "fi_rsi", "force",
        "ko", "vramt", "rsis", "pmarp_yidai_v1", "dbcd_v2", "smi_v2",
        "volume_reg", "v1_v2", "v1up_v2", "v1dn_v2", "mtmmean_v10",
        "mtmmean_v12", "mtmhcm", "short_moment", "long_moment", "si", "wr",
        "rocvol", "mtmmean_v4", "atr_count", "zfabsmean", "bbw", "amv",
        "mfi", "obv", "pvt_v2", "pvt_v3", "pvt_v4", "vr",
        "vao", "vao_v2", "volume_bias", "volume", "volumechg", "maamt",
        "upnum_fancy", "trade_num", "taker_by_ratio", "buy_vol_ratio_fancy", "taker_by_ratio_per_trade", "vol_per_trade_fancy",
        "mtm_tb", "dbcd_taker", "mtm_bull", "mtm_bear", "buy_vwap_div_vwap_fancy", "vramt",
        "v1", "v1up", "v1_v2", "v1up_v2", "v1dn_v2", "v1dn",
        "Volume", "autocorrelation", "copp", "demaker", "er", "kdjdk",
        "kdjdd", "skdj", "magiccci", "magiccci_v2",
    ]
    for col in expected:
        assert col in result.columns, f"Missing close column: '{col}'"


def test_extract_features_trend_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "dema_bias", "tema_bias", "trix",
        "aroon_up", "aroon_down", "aroon_osc",
        "vortex_plus", "vortex_minus", "vortex_diff",
        "regression_bias", "regression_slope", "ma_signal", "bbi_ratio", "bbi_bias", "adxr_diff", "wma_ma_gap", "adx_strength", "adx_di_plus", "adx_di_minus", "vi_plus", "vi_minus", "turtle_breakout", "turtle_distance", "ma_ratio", "dema_bias2", "tema_bias2", "hma_ratio", "vidya_bias", "tma_bias2", "vma_ratio", "lma_ratio", "mm_ratio", "reg_angle", "expma_ratio", "reg", "reg_v2", "reg_v3", "diff_ema", "diff_ema_ratio", "regema_bias", "regtema_bias", "trtrix", "trv", "mac_v4", "mac_v5", "gap_ratio", "angle_reg", "cse", "madis_placed", "trrq", "mreg", "adxr_pos", "adxr_neg", "acs", "mak", "sgcz", "gap", "arron", "ma", "vma", "mm", "expma", "lma", "dema", "tema", "hlma", "ic_v2", "ic_v3", "ic_v4", "adxrpos", "regema_bias", "regtema_bias", "diff_ema", "dma", "angle", "vi", "trrq_v3", "uos", "zlmacd", "tma_bias", "mtmmean_v8", "mtmvolmean", "adx_di_plus", "adx_di_minus", "adxr", "bbi", "hullma", "ic", "regema", "regtema", "tema_v2", "tma", "turtle", "vidya", "t3",
        "hullma_bias", "ichimoku_cloud_ratio", "t3_bias", "hma_signal", "hullma_signal", "mac_v2", "mac_v3", "hullma_ratio", "vidya_v2", "vidya_v5", "mac", "pjc_distance", "hma", "tma_v2", "tma_v3", "vidya_v3", "vidya_v4",
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
        "parkinson_vol", "garman_klass_vol", "rogers_satchell_vol", "yang_zhang_vol", "volatility_ratio_yz",
        "squeeze_on", "squeeze_off", "squeeze_count", "squeeze_momentum", "hvr", "rvi_14", "is_choppy", "is_trending",
        "adaptive_bollinger_width", "vwap_bbw_efficiency", "chaikin_volatility", "keltner_width", "keltner_upper_signal", "keltner_lower_signal", "env_upper_signal", "env_lower_signal", "fibonacci_band_width", "fibonacci_band_position", "donchian_mid_signal", "bbw_signal", "kc_signal", "atr_upper_medium", "atr_lower_medium", "fb_upper_signal", "pac_width_signal", "volume_std", "grid", "lcsd",
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
        "adosc", "wvad", "klinger_oscillator", "ko", "vra", "ke",
        "roc_volume", "roc_vol", "macdvol", "volume_reg", "volume_ma_bias", "amv_signal", "volume_ratio", "macd_volume_ratio", "volume_analysis_oscillator", "quote_volume_mean", "quote_volume_ratio", "v1", "v1_up", "v1_down", "mfi_standard", "chla_fancy", "net_vol_fancy", "force_ratio",
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
        "close_ma_price", "typical_to_vwap", "avgprice", "avgpricetohigh", "avgpricetolow", "lowprice", "typ", "vwap_signal", "wvad", "vwap_bias", "wc",
    ]
    for col in expected:
        assert col in result.columns, f"Missing price column: '{col}'"


def test_extract_features_liquidity_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "market_placement", "path_liquidity", "spread_proxy",
        "spread_volatility_ratio", "price_volume_resistance", "coppock_atr_volume", "bidask_spread", "market_placement_v2", "liquidity_v3", "amihud", "apz", "apz_upper", "apz_lower", "bolling", "bolling_width", "cv", "dc", "dc_signal", "dc_v2", "kcupper", "kclower", "pac", "pacupper", "paclower", "pacupper_v2", "paclower_v2",
        "corwin_schultz_spread", "roll_spread", "kyles_lambda", "amihud_illiq", "amihud_zscore",
    ]
    for col in expected:
        assert col in result.columns, f"Missing liquidity column: '{col}'"


def test_extract_features_lag_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "open_lag1", "high_lag1", "low_lag1", "close_lag1",
        "volume_lag1", "body_lag1", "upwick_lag1", "lowwick_lag1",
        "lowwick_rate_lag1", "upwick_rate_lag1", "clv_lag1", "ibs_lag1",
        "rsi_medium_lag1", "rsi_medium_delta", "macd_hist_lag1", "macd_hist_delta",
        "kdj_j_lag1", "ema_fast_lag1", "ema_slow_lag1", "vwap_lag1",
        "atr_medium_lag1", "volatility_expansion_ratio", "bbw_lag1",
        "volume_avg_lag1", "volume_ratio_lag1",
    ]
    for col in expected:
        assert col in result.columns, f"Missing lag column: '{col}'"



def test_extract_features_mix_columns():
    result = extract_features(make_ohlcv(300))
    expected = [
        "ibs_n", "is_fvg",
        "ulti_osci", "vwap", "atr_medium", "adx",
        "atr_pct_medium",
        "dm",
        "direction", "streak",
        "custom_001", "custom_002",
        "donchian_width", "donchian_position", "amihud_liquidity",
        "keltner_position",
        "true_range_pct", "gap_pct", "range_position", "body_to_true_range", "fear_greed_yidai_v1", "damaov10", "adx_mtm", "mtam", "msbt", "copp_atr_bull", "adx_mtm_neg",
        "cvr_v0", "cbr_v1", "fbnq_pct_v5", "price_volume_resist",
        "liquidity_sweep_high", "liquidity_sweep_low",
        "fvg_bullish", "fvg_bearish", "fvg_gap_pct",
        "equal_highs", "equal_lows",
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


def test_extract_features_signal_context_helper_columns():
    result = extract_features(make_ohlcv(300))
    expected = [ "body_abs", "body_abs_sma_medium", "range_sma_medium", "candle_range_ratio",
        "midpoint", "close_vs_mid",
        "price_change", "price_change_lag1",
        "return_micro", "return_short", "return_medium", "return_long", "return_macro",
        "sma_micro", "sma_short", "sma_medium", "sma_long", "sma_macro",
        "std_micro", "std_short", "std_medium", "std_long", "std_macro",
        "close_min_micro", "close_min_short", "close_min_medium", "close_min_long", "close_min_macro",
        "close_max_micro", "close_max_short", "close_max_medium", "close_max_long", "close_max_macro",
        "rsi_micro", "rsi_short", "rsi_medium", "rsi_long", "rsi_macro",
        "bb_width_q20", "bb_width_sma_medium", "atr_sma_medium",
        "high_micro", "low_micro", "high_short", "low_short", "high_medium", "low_medium",
        "range_mid_short", "recent_high", "recent_low", "recent_high_prev", "recent_low_prev",
        "prev_micro_low", "prev_micro_high", "prev_short_low", "prev_short_high", "prev_medium_low", "prev_medium_high",
        "lower_range_pos", "upper_range_pos", "linreg_upper_medium", "linreg_lower_medium",
        "volume_sma_medium", "equal_low", "equal_high", "inside_bar_prev",
    ]
    for col in expected:
        assert col in result.columns, f"Missing moved signal helper column: '{col}'"


def test_extract_features_no_nan_in_ohlcv():
    result = extract_features(make_ohlcv(300))
    assert result[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum() == 0


def test_extract_features_color_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["color"].unique()).issubset({1, -1})


def test_extract_features_direction_values():
    result = extract_features(make_ohlcv(300))
    assert set(result["direction"].unique()).issubset({1, -1})


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


def test_rolling_regressions_skip_invalid_values_without_lapack_noise(capfd):
    bad_values = np.array([1.0, np.inf, 3.0])
    short_values = np.array([1.0])

    assert np.isnan(close_regression_last(bad_values))
    assert np.isnan(close_regression_last(short_values))
    assert np.isnan(volume_regression_last(bad_values))
    assert np.isnan(volume_regression_forecast(bad_values))

    series = pd.Series([1.0, np.inf, 3.0, 4.0])
    assert _linear_regression_slope(series, 3).isna().iloc[2]
    assert _linear_regression_midline(series, 3).isna().iloc[2]

    captured = capfd.readouterr()
    assert "DLASCL" not in captured.out
    assert "DLASCL" not in captured.err


# ─────────────────────────────────────────────
# Config tests
# ─────────────────────────────────────────────

def test_load_config_sets_defaults():
    config = load_config()
    assert config == Config()


def test_load_config_from_json_file():
    custom = dict(DEFAULT_CONFIG)
    custom["SELECTED_TIME_FRAME"] = "15m"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(custom, f)
        json_path = f.name

    try:
        config = load_config(json_path)
        assert config.selected_time_frame == "15m"
    finally:
        os.unlink(json_path)


def test_load_config_from_json_file_coerces_numeric_strings():
    custom = dict(DEFAULT_CONFIG)
    custom["ONE_DAY_BARS"] = "49"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(custom, f)
        json_path = f.name

    try:
        config = load_config(json_path)
        assert config.one_day_bars == 49
        assert isinstance(config.one_day_bars, int)
    finally:
        os.unlink(json_path)


def test_load_config_from_yaml_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("SELECTED_TIME_FRAME: 15m\nONE_DAY_BARS: 49\nMICRO_LOOKBACK: 5\n")
        yaml_path = f.name

    try:
        config = load_config(yaml_path)
        assert config.selected_time_frame == "15m"
        assert config.one_day_bars == 49
        assert config.micro_lookback == 5
    finally:
        os.unlink(yaml_path)


def test_load_config_env_file_is_not_supported():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SELECTED_TIME_FRAME=15m\n")
        env_path = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported config file format"):
            load_config(env_path)
    finally:
        os.unlink(env_path)


def test_load_config_classic_indicators():
    config = load_config()
    assert hasattr(config, "classic_indicators")
    assert config.classic_indicators["RSI"] == 14
    assert config.classic_indicators["MACD"] == [12, 26, 9]

    custom = dict(DEFAULT_CONFIG)
    custom["CLASSIC_INDICATORS"] = {"RSI": 10, "MACD": [10, 20, 5]}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(custom, f)
        json_path = f.name

    try:
        cfg = load_config(json_path)
        assert cfg.classic_indicators["RSI"] == 10
        assert cfg.classic_indicators["MACD"] == [10, 20, 5]
    finally:
        os.unlink(json_path)


def test_classic_indicators_custom_params_used():
    cfg_custom = Config(
        classic_indicators={
            "RSI": 14,
            "STOCHRSI": 14,
            "MACD": [5, 10, 3],
            "PPO": [5, 10, 3],
            "WILLIAMS_R": 10,
            "AO": [3, 10],
            "UO": [5, 10, 20],
            "MFI": 10,
            "SUPERTREND": [5, 2.0],
            "TRIX": [10, 5],
        }
    )
    from autofcholv.pipeline.features import close as close_features
    from autofcholv.pipeline.features import trend as trend_features
    from autofcholv.pipeline.features import volume as volume_features

    df = make_ohlcv(60)
    df_close = close_features.extract_features(df, cfg_custom)
    df_trend = trend_features.extract_features(df, cfg_custom)
    df_volume = volume_features.extract_features(df, cfg_custom)

    assert "macd" in df_close.columns
    assert "trix15" in df_trend.columns
    assert "mfi14" in df_volume.columns


def test_5tier_and_session_bars_config_propagation():
    cfg = Config(
        micro_lookback=4,
        short_lookback=8,
        medium_lookback=16,
        macro_lookback=80,
        morning_bars=25,
        one_hour_bars=10,
    )
    from autofcholv.pipeline.features import volatility as vol_features
    from autofcholv.pipeline.features import mix as mix_features
    from autofcholv.pipeline.features import resample as resample_features
    from autofcholv.pipeline.features import trend as trend_features

    df = make_ohlcv(120)
    df["ub"] = df["Close"] * 1.02
    df["lb"] = df["Close"] * 0.98
    df["mb"] = df["Close"]
    df["atr_medium"] = 1.0
    df["low_short"] = df["Low"]
    df["high_short"] = df["High"]
    df["low_micro"] = df["Low"]
    df["high_micro"] = df["High"]
    df["low_medium"] = df["Low"]
    df["high_medium"] = df["High"]
    df["low_long"] = df["Low"]
    df["high_long"] = df["High"]
    df["low_macro"] = df["Low"]
    df["high_macro"] = df["High"]
    df["session_open"] = df["Open"].iloc[0]
    df["roc_close"] = df["Close"].pct_change()
    df["streak"] = 1
    df["body_lag1"] = df["Close"].shift(1) - df["Open"].shift(1)
    df["open_lag1"] = df["Open"].shift(1)
    df["close_lag1"] = df["Close"].shift(1)
    df["high_lag1"] = df["High"].shift(1)
    df["low_lag1"] = df["Low"].shift(1)
    df["volume_lag1"] = df["Volume"].shift(1)
    df["ibs"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-9)
    df["ibs_lag1"] = df["ibs"].shift(1)
    df["vbr"] = 1.0
    df["body"] = df["Close"] - df["Open"]

    df_vol = vol_features.extract_features(df, cfg)
    df_mix = mix_features.extract_features(df, cfg)
    df_resample = resample_features.extract_features(df, cfg)
    df_trend = trend_features.extract_features(df, cfg)

    assert "bb_width_q20" in df_vol.columns
    assert "connors_rsi" in df_mix.columns
    assert "ema_20" in df_trend.columns


def test_dynamic_ema_and_classic_trend_lookbacks():
    cfg = Config(
        ema_windows=[9, 13, 34],
        classic_indicators={"ADX": 10},
    )
    from autofcholv.pipeline.features import trend as trend_features
    df = make_ohlcv(50)
    df_trend = trend_features.extract_features(df, cfg)

    assert "ema_9" in df_trend.columns
    assert "ema_13" in df_trend.columns
    assert "ema_34" in df_trend.columns
    assert "adx_14" in df_trend.columns






def test_load_config_does_not_read_environment_variables():
    os.environ["SELECTED_TIME_FRAME"] = "1h"
    try:
        config = load_config()
        assert config.selected_time_frame == "5m"
    finally:
        os.environ.pop("SELECTED_TIME_FRAME", None)


def test_load_config_loads_local_default_config_file_when_present(tmp_path, monkeypatch):
    custom_default = dict(DEFAULT_CONFIG)
    custom_default["MOMENTUM_LOOKBACK"] = 48
    config_file = tmp_path / "config.default.json"
    config_file.write_text(json.dumps(custom_default), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.momentum_lookback == 48


def test_extract_features_todo_group_columns():
    df = make_ohlcv(300)
    result = extract_features(df)
    new_cols = [
        "is_max_micro", "upper_wick_group", "mfi_group", "higher_high_lower_vol",
        "volume_higher_avg", "volume_vs_prev_vol", "volume_avg_group",
        "close_price_group", "open_price_group", "high_position",
        "bb_rejection", "lower_shadow_group", "ibs_vol_group",
        "rsi_area", "lower_low_lower_vol", "low_position",
    ]
    for col in new_cols:
        assert col in result.columns, f"Missing expected column: '{col}'"

    # Specific assertion checks
    assert result["is_max_micro"].dtype == bool
    assert result["higher_high_lower_vol"].dtype == bool
    assert result["bb_rejection"].dtype == bool
    assert result["lower_low_lower_vol"].dtype == bool
    assert set(result["rsi_area"].dropna().unique()).issubset({">55", "<45", "45-55"})


def test_group_features_module_direct_extraction():
    from autofcholv.pipeline.features import group as group_features
    df = make_ohlcv(50)
    # Add dummy prerequisite columns required by group module
    df['high_lag1'] = df['High'].shift(1)
    df['low_lag1'] = df['Low'].shift(1)
    df['open_lag1'] = df['Open'].shift(1)
    df['close_lag1'] = df['Close'].shift(1)
    df['volume_lag1'] = df['Volume'].shift(1)
    df['upwick'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['lowwick'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    df['ibs'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
    df['ibs_lag1'] = df['ibs'].shift(1)
    df['rsi_medium'] = 50.0
    df['rsi_medium_lag1'] = 50.0
    df['volume_avg'] = df['Volume'].rolling(10, min_periods=1).mean()
    df['ub'] = df['Close'] * 1.02
    df['lb'] = df['Close'] * 0.98

    res = group_features.extract_features(df, Config())
    new_cols = [
        "is_max_micro", "upper_wick_group", "mfi_group", "higher_high_lower_vol",
        "volume_higher_avg", "volume_vs_prev_vol", "volume_avg_group",
        "close_price_group", "open_price_group", "high_position",
        "bb_rejection", "lower_shadow_group", "ibs_vol_group",
        "rsi_area", "lower_low_lower_vol", "low_position",
    ]
    for col in new_cols:
        assert col in res.columns



