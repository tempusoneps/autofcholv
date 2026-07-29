# TODO Group Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 16 new vectorized group features in `autofcholv` from `docs/TODO.md`, update JSON metadata, and regenerate documentation.

**Architecture:** Features will be implemented in `src/autofcholv/pipeline/features/group.py` using numpy/pandas vectorized operations (`np.where`, `np.select`). Metadata will be updated in `group.json`, followed by automated documentation generation.

**Tech Stack:** Python 3.12, Pandas, NumPy, pytest, uv.

## Global Constraints
- Preserve existing column names and pipeline interface contracts.
- Avoid row-by-row `apply` loops for performance and data leakage prevention.
- Keep `src/autofcholv/pipeline/features/group.json` in sync with `group.py`.
- Regenerate `docs/FEATURES.md` and `README.md` using project scripts.

---

### Task 1: Implement 16 Group Features and Unit Tests

**Files:**
- Modify: `src/autofcholv/pipeline/features/group.py`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: OHLCV DataFrame with `high_lag1`, `low_lag1`, `open_lag1`, `close_lag1`, `volume_lag1`, `upwick`, `lowwick`, `ibs`, `ibs_lag1`, `rsi` (or `rsi20`), `mfi14`, `volume_avg`, `ub`, `lb`.
- Produces: DataFrame enriched with 16 new columns: `is_max_4`, `upper_wick_group`, `MFI_group`, `higher_high_lower_vol`, `Volume_higher_avg`, `Volume_vs_prev_Vol`, `Volume_avg_group`, `close_price_group`, `open_price_group`, `High_position`, `BB_rejection`, `lower_shadow_group`, `ibs_vol_group`, `rsi_area`, `lower_low_lower_vol`, `Low_position`.

- [ ] **Step 1: Write the failing test in `tests/test_core.py`**

Add test function `test_extract_features_todo_group_columns` in `tests/test_core.py`:

```python
def test_extract_features_todo_group_columns():
    df = make_ohlcv(300)
    result = extract_features(df)
    new_cols = [
        "is_max_4", "upper_wick_group", "MFI_group", "higher_high_lower_vol",
        "Volume_higher_avg", "Volume_vs_prev_Vol", "Volume_avg_group",
        "close_price_group", "open_price_group", "High_position",
        "BB_rejection", "lower_shadow_group", "ibs_vol_group",
        "rsi_area", "lower_low_lower_vol", "Low_position",
    ]
    for col in new_cols:
        assert col in result.columns, f"Missing expected column: '{col}'"

    # Specific assertion checks
    assert result["is_max_4"].dtype == bool
    assert result["higher_high_lower_vol"].dtype == bool
    assert result["BB_rejection"].dtype == bool
    assert result["lower_low_lower_vol"].dtype == bool
    assert set(result["rsi_area"].dropna().unique()).issubset({">55", "<45", "45-55"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_core.py::test_extract_features_todo_group_columns -v`
Expected: FAIL with `AssertionError: Missing expected column: 'is_max_4'`

- [ ] **Step 3: Implement minimal vectorized code in `src/autofcholv/pipeline/features/group.py`**

Update `group.py` `extract_features`:

```python
import numpy as np
import pandas as pd
import pandas_ta as ta
from autofcholv.config.config import Config


def extract_features(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    cols = ['high_lag1', 'low_lag1', 'volume_lag1', 'ibs', 'ibs_lag1',
            'upwick', 'lowwick', 'rsi', 'rsi_lag1', 'volume_avg', 'ub', 'lb']
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    vol_state  = np.where(df["Volume"] > df["volume_lag1"], "VolUp", "VolDown")
    high_state = np.where(df["High"]   > df["high_lag1"],  "HighUp", "HighDown")
    ibs_state  = np.where(df["ibs"]    > df["ibs_lag1"],   "IBSUp",  "IBSDown")
    rsi_state  = np.where(df["rsi"]    > df["rsi_lag1"],   "RSIUp",  "RSIDown")

    df['volume_group']     = vol_state
    df['upper_wick_group'] = np.where(df["upwick"] > df["upwick"].shift(1), "Increase", "Not Increase")
    df['lower_wick_group'] = np.where(df["lowwick"] > df["lowwick"].shift(1), "Longer", "Shorter")
    df['lower_shadow_group'] = np.where(df["lowwick"] > df["lowwick"].shift(1), "Increase", "Not Increase")

    df['vol_high_pattern']    = vol_state + "_" + high_state
    df['ibs_volume_pattern']  = vol_state + "_" + ibs_state
    df['volume_avg_group']    = np.where(df["Volume"] > df["volume_avg"], "VolAboveAvg", "VolBelowAvg")
    df['high_rsi_pattern']    = high_state + "_" + rsi_state
    df['high_ub_pattern']     = np.where(df["High"] > df["ub"], "HighAboveUB", "HighBelowUB")
    df['low_lb_pattern']      = np.where(df["Low"]  < df["lb"], "LowBelowLB",  "LowAboveLB")
    df["equal_low"] = (df["Low"] - df["low_lag1"]).abs() < (0.001 * df["Close"])
    df["equal_high"] = (df["High"] - df["high_lag1"]).abs() < (0.001 * df["Close"])
    df["inside_bar_prev"] = (df["high_lag1"] < df["High"].shift(2)) & (df["low_lag1"] > df["Low"].shift(2))

    # New TODO features
    df['is_max_4'] = df["High"] > df["High"].shift(1).rolling(3).max()
    mfi_col = "mfi14" if "mfi14" in df.columns else ("mfi" if "mfi" in df.columns else None)
    if mfi_col:
        df['MFI_group'] = np.where(df[mfi_col] > df[mfi_col].shift(1), "Increase", "Not Increase")
    else:
        df['MFI_group'] = "Not Increase"

    df['higher_high_lower_vol'] = (df["High"] > df["high_lag1"]) & (df["Volume"] < df["volume_lag1"])
    df['lower_low_lower_vol'] = (df["Low"] < df["low_lag1"]) & (df["Volume"] < df["volume_lag1"])
    df['Volume_higher_avg'] = df["Volume"] > df["volume_avg"]
    df['Volume_vs_prev_Vol'] = np.where(df["Volume"] > df["volume_lag1"], "Increase", "Not Increase")
    df['Volume_avg_group'] = np.where(df["volume_avg"] > df["volume_avg"].shift(1), "Increase", "Not Increase")

    # close_price_group
    c_prev_max = np.maximum(df["close_lag1"], df["open_lag1"])
    c_prev_min = np.minimum(df["close_lag1"], df["open_lag1"])
    close_conds = [
        df["Close"] > df["high_lag1"],
        df["Close"] > c_prev_max,
        df["Close"] >= c_prev_min,
        df["Close"] >= df["low_lag1"],
        df["Close"] < df["low_lag1"]
    ]
    close_choices = ["> prev High", "Bong nen tren", "Than nen", "Bong nen duoi", "< prev Low"]
    df['close_price_group'] = np.select(close_conds, close_choices, default="< prev Low")

    # open_price_group
    open_conds = [
        df["Open"] > df["close_lag1"],
        df["Open"] == df["close_lag1"],
        df["Open"] < df["close_lag1"]
    ]
    open_choices = ["Open > prev_Close", "Open = prev_Close", "Open < prev_Close"]
    df['open_price_group'] = np.select(open_conds, open_choices, default="Open < prev_Close")

    # Bollinger band positions
    df['High_position'] = np.where(df["High"] > df["ub"], "> upper BB", "< upper BB")
    df['BB_rejection'] = (df["High"] > df["ub"]) & (df["Close"] < df["ub"])
    df['Low_position'] = np.where(df["Low"] > df["lb"], "> lower BB", "<= lower BB")

    # ibs_vol_group
    vol_up = df["Volume"] > df["volume_lag1"]
    ibs_up = df["ibs"] > df["ibs_lag1"]
    ibs_conds = [
        vol_up & ibs_up,
        vol_up & (~ibs_up),
        (~vol_up) & ibs_up,
        (~vol_up) & (~ibs_up)
    ]
    ibs_choices = ["Vol up, ibs incre", "Vol up, ibs decr", "Vol down, ibs incre", "Vol down, ibs decr"]
    df['ibs_vol_group'] = np.select(ibs_conds, ibs_choices, default="Vol down, ibs decr")

    # rsi_area
    rsi_col = "rsi" if "rsi" in df.columns else ("rsi20" if "rsi20" in df.columns else None)
    rsi_val = df[rsi_col] if rsi_col else df["rsi"]
    rsi_conds = [rsi_val > 55, rsi_val < 45]
    rsi_choices = [">55", "<45"]
    df['rsi_area'] = np.select(rsi_conds, rsi_choices, default="45-55")

    _1day_bars     = config.one_day_bars
    _1month_bars   = _1day_bars * 22
    _6month_bars   = _1month_bars * 6
    if len(df) < _6month_bars:
        raise ValueError(f"Not enough data to calculate long trend. Need {_6month_bars} bars, got {len(df)}")
    ema_1month = ta.ema(df["Close"], length=_1month_bars)
    ema_6month = ta.ema(df["Close"], length=_6month_bars)
    mask = ema_1month.notna() & ema_6month.notna()   
    df["long_trend"] = None
    df.loc[mask, "long_trend"] = np.where(
        ema_1month[mask] > ema_6month[mask],
        "StrongUp",
        "StrongDown"
    )

    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_core.py::test_extract_features_todo_group_columns -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/autofcholv/pipeline/features/group.py tests/test_core.py
git commit -m "feat: add 16 TODO group features"
```

---

### Task 2: Update Metadata JSON, Regenerate Docs, and Update TODO.md

**Files:**
- Modify: `src/autofcholv/pipeline/features/group.json`
- Modify: `docs/TODO.md`
- Regenerate: `docs/FEATURES.md`, `README.md`

**Interfaces:**
- Consumes: JSON schemas in `group.json`.
- Produces: Updated `group.json`, `docs/FEATURES.md`, `README.md`, cleared `docs/TODO.md`.

- [ ] **Step 1: Update `src/autofcholv/pipeline/features/group.json`**

Add JSON definitions for all 16 new columns (`is_max_4`, `MFI_group`, `higher_high_lower_vol`, `Volume_higher_avg`, `Volume_vs_prev_Vol`, `Volume_avg_group`, `close_price_group`, `open_price_group`, `High_position`, `BB_rejection`, `lower_shadow_group`, `ibs_vol_group`, `rsi_area`, `lower_low_lower_vol`, `Low_position`).

- [ ] **Step 2: Run doc generation scripts**

Run:
```bash
python3 scripts/generate_feature_md_from_json.py
scripts/generate_root_readme.sh
```

- [ ] **Step 3: Update `docs/TODO.md`**

Mark all items in `docs/TODO.md` as completed `- [x]`.

- [ ] **Step 4: Run tests to verify full pipeline passes**

Run: `uv run pytest tests/test_core.py::test_extract_features_group_columns -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/autofcholv/pipeline/features/group.json docs/FEATURES.md README.md docs/TODO.md
git commit -m "docs: update metadata json and regenerate features doc"
```
