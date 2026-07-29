# Design Spec: Add TODO Group Features to autofcholv

- **Date**: 2026-07-29
- **Status**: Approved
- **Target Module**: `src/autofcholv/pipeline/features/group.py`
- **Metadata Spec**: `src/autofcholv/pipeline/features/group.json`

---

## 1. Overview

This document specifies the design for adding 16 new categorical and boolean group features requested in `docs/TODO.md`. These features analyze OHLCV candle patterns, volume dynamics, wick changes, oscillator relative movements (RSI, MFI), and Bollinger Band interactions. All operations are strictly vectorized to maintain high computational performance and avoid data leakage across bars.

---

## 2. Architecture & Pipeline Integration

The new features belong to the `group_features` step in the pipeline:
1. **Pipeline Execution Order**: `group_features` runs after `time_features`, `resample_features`, `vn30f1m_features`, `candlestick_features`, `close_features`, `price_features`, `trend_features`, `volatility_features`, `volume_features`, `liquidity_features`, `lag_features`, and `mix_features`.
2. **Pre-requisite Columns**:
   - OHLCV: `High`, `Low`, `Open`, `Close`, `Volume`
   - Lags: `high_lag1`, `low_lag1`, `open_lag1`, `close_lag1`, `volume_lag1`, `upwick_lag1`, `lowwick_lag1`
   - Candlesticks: `upwick`, `lowwick`, `ibs`, `ibs_lag1`
   - Indicators: `rsi` (or `rsi20`), `mfi14` (or `mfi`), `volume_avg`, `ub`, `lb`
3. **Module Updates**:
   - `src/autofcholv/pipeline/features/group.py`
   - `src/autofcholv/pipeline/features/group.json`
   - `tests/test_core.py`
   - Generated docs: `docs/FEATURES.md`, `README.md`

---

## 3. Feature Definitions

| Feature Column | Type | Formula / Logic |
| :--- | :--- | :--- |
| `is_max_4` | `bool` | `High > High.shift(1).rolling(3).max()` |
| `upper_wick_group` | `str` | `np.where(upwick > upwick.shift(1), "Increase", "Not Increase")` |
| `MFI_group` | `str` | `np.where(mfi14 > mfi14.shift(1), "Increase", "Not Increase")` |
| `higher_high_lower_vol` | `bool` | `(High > high_lag1) & (Volume < volume_lag1)` |
| `Volume_higher_avg` | `bool` | `Volume > volume_avg` |
| `Volume_vs_prev_Vol` | `str` | `np.where(Volume > volume_lag1, "Increase", "Not Increase")` |
| `Volume_avg_group` | `str` | `np.where(volume_avg > volume_avg.shift(1), "Increase", "Not Increase")` |
| `close_price_group` | `str` | Categorical position of `Close` relative to previous bar:<br>1. `Close > high_lag1` $\rightarrow$ `"> prev High"`<br>2. `Close > max(close_lag1, open_lag1)` $\rightarrow$ `"Bong nen tren"`<br>3. `Close >= min(close_lag1, open_lag1)` $\rightarrow$ `"Than nen"`<br>4. `Close >= low_lag1` $\rightarrow$ `"Bong nen duoi"`<br>5. `Close < low_lag1` $\rightarrow$ `"< prev Low"` |
| `open_price_group` | `str` | Categorical position of `Open` relative to previous bar `Close`:<br>1. `Open > close_lag1` $\rightarrow$ `"Open > prev_Close"`<br>2. `Open == close_lag1` $\rightarrow$ `"Open = prev_Close"`<br>3. `Open < close_lag1` $\rightarrow$ `"Open < prev_Close"` |
| `High_position` | `str` | `np.where(High > ub, "> upper BB", "< upper BB")` |
| `BB_rejection` | `bool` | `(High > ub) & (Close < ub)` |
| `lower_shadow_group` | `str` | `np.where(lowwick > lowwick.shift(1), "Increase", "Not Increase")` |
| `ibs_vol_group` | `str` | Multi-condition matrix of Volume vs `volume_lag1` and IBS vs `ibs_lag1`:<br>1. `Vol > vol_lag1 & ibs > ibs_lag1` $\rightarrow$ `"Vol up, ibs incre"`<br>2. `Vol > vol_lag1 & ibs < ibs_lag1` $\rightarrow$ `"Vol up, ibs decr"`<br>3. `Vol < vol_lag1 & ibs > ibs_lag1` $\rightarrow$ `"Vol down, ibs incre"`<br>4. `Vol < vol_lag1 & ibs < ibs_lag1` $\rightarrow$ `"Vol down, ibs decr"` |
| `rsi_area` | `str` | `np.select`:<br>1. `rsi > 55` $\rightarrow$ `">55"`<br>2. `rsi < 45` $\rightarrow$ `"<45"`<br>3. default $\rightarrow$ `"45-55"` |
| `lower_low_lower_vol` | `bool` | `(Low < low_lag1) & (Volume < volume_lag1)` |
| `Low_position` | `str` | `np.where(Low > lb, "> lower BB", "<= lower BB")` |

---

## 4. Testing & Verification

1. **Unit Tests**:
   - Add new column assertions to `test_extract_features_group_columns` in `tests/test_core.py`.
   - Add explicit value-verification tests for key features (`is_max_4`, `close_price_group`, `BB_rejection`, `ibs_vol_group`).
2. **Performance**:
   - Ensure execution time remains fast using vectorized numpy/pandas array functions.
3. **Documentation**:
   - Run `python3 scripts/generate_feature_md_from_json.py` to update `docs/FEATURES.md`.
   - Run `scripts/generate_root_readme.sh` to update `README.md`.
