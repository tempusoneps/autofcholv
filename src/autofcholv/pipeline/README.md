# Pipeline Overview

Transforms raw OHLCV data into a feature-rich DataFrame ready for modeling or analytics.

```
Raw OHLCV DataFrame
  → 1. Clean
  → 2. Validate
  → 3. Feature Engineering
  → 4. Preprocessing
  → Model / Analytics
```

---

## 1. Clean — `cleaning.py`

**Entry point:** `clean_ohlcv(df, dropna, remove_negative, remove_duplicates, sort_by_index)`

Sanitizes raw OHLCV data before any processing.

| Step | Action |
|---|---|
| Index check | Converts index to `DatetimeIndex` |
| Required columns | Asserts `Open`, `High`, `Low`, `Close`, `Volume` exist |
| Type coercion | Converts OHLCV columns to numeric |
| NaN handling | Drops rows or raises on NaN (controlled by `dropna`) |
| Negative values | Removes or raises on negative prices/volume |
| OHLC logic | Raises if `High < max(O,L,C)` or `Low > min(O,H,C)` |
| Duplicates | Removes or raises on duplicate timestamps |
| Sort | Sorts by index ascending |
| Legacy fix | Drops 11:30 and 14:30 bars from historical data |

---

## 2. Validate — `validation.py`

**Entry point:** `validate_ohlcv_dataset(df) → (is_valid, report)`

Returns a validation report without mutating the DataFrame.

| Check | Description |
|---|---|
| Missing columns | Required OHLCV columns present |
| NaN values | No nulls in OHLCV columns |
| Negative prices | All prices ≥ 0 |
| Negative volume | Volume ≥ 0 |
| High logic | `High` is the highest price of the bar |
| Low logic | `Low` is the lowest price of the bar |
| Duplicate timestamps | No repeated index values |
| Timeframe guard | Rejects daily (≥ 1D) data; only intraday supported |

---

## 3. Feature Engineering — `feature_engineering.py`

**Entry point:** `build_features(df) → df`

Runs 9 sub-modules in order. Each module adds columns according to its `.json` specification (see [`features/README.md`](features/README.md)).

| # | Module | File | Key outputs |
|---|---|---|---|
| 1 | Time | `time.py` | `hour`, `minute`, `time_int`, `session_progress`, `day_of_week`, … |
| 2 | Resample | `resample.py` | `day_open/high/low/close/volume/pivot`, `prev_day_*` |
| 3 | Candlestick | `candlestick.py` | `body`, `height`, `upwick`, `lowwick`, `ibs`, `clv`, `cbr`, `vbr`, … |
| 4 | Close | `close.py` | `ema_fast`, `ema_slow`, `rsi`, `macd`, `mb`, `ub`, `lb`, … |
| 5 | Volume | `volume.py` | `volume_avg`, `volume_zscore` |
| 6 | Lag | `lag.py` | `*_lag1` columns for OHLCV, body, wicks, ibs, rsi |
| 7 | Mix | `mix.py` | `ibs_n`, `is_fvg`, `vwap`, `atr`, `adx`, `direction`, `streak`, … |
| 8 | Group | `group.py` | `volume_group`, `vol_high_pattern`, `ibs_volume_pattern`, `high_rsi_pattern`, `high_ub_pattern`, … |
| 9 | Signal | `signal.py` | `couple_cs_signal`, `ema_cross_signal` |

---

## 4. Preprocessing — `preprocessing.py`

**Entry point:** `preprocess_data(df) → df`

Final cleanup before model input: drops all rows that still contain `NaN` after feature engineering.