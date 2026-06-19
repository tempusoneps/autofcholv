---
name: create-feature
description: Use when adding a new feature to the autofcholv pipeline — covers requirement clarification, roadmap check, JSON schema update, code implementation, unit test, and roadmap completion.
---

# Create Feature

## Overview

Standard process for adding a new feature to the autofcholv pipeline. Consists of 6 sequential steps — do not skip any.

---

## Step 1 — Requirement

Clarify all of the following before writing any code:

- **Output column name** (e.g. `parkinson_vol`, `roc_3`)
- **Data type** (`float` / `int` / `str` / `bool`)
- **Formula / logic**
- **Dependency columns** — which columns from previous steps does this feature require?
- **Config key** — is a lookback period needed? Which key in `DEFAULT_CONFIG`?
- **Module** — which `.py` file to add it to? (new file or append to an existing one?)

**Current pipeline order** (dependencies must come BEFORE):
```
1. time        2. resample    3. candlestick  4. close
5. volume      6. lag         7. mix          8. group
9. signal
```

---

## Step 2 — Check Roadmap

Open `docs/ROADMAP.md` and find the feature by name:

```
- [ ] `parkinson_vol` = Parkinson Volatility = ...
```

- If **found** → feature is already planned, proceed to step 3.
- If **not found** → add a new line to the correct group in ROADMAP before implementing.

---

## Step 3 — Update JSON File

Each feature module has a corresponding JSON file at:
`src/autofcholv/pipeline/features/{module}.json`

Add an entry for each new output column:

```json
{
    "parkinson_vol": {
        "type": "float",
        "name": "Parkinson Volatility",
        "comment": "Rolling Parkinson Volatility = sqrt(1/(4n*ln2) * sum(ln(H/L)^2))"
    }
}
```

**Required format:**
- `type`: `"float"` | `"int"` | `"str"` | `"bool"`
- `name`: Display name (title case)
- `comment`: Formula or short description

---

## Step 4 — Implement Code

### 4a. Create / edit the feature file

`src/autofcholv/pipeline/features/{module}.py`

```python
import os
import numpy as np
import pandas as pd

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    # Guard: check dependency columns if any
    deps = ['High', 'Low']
    missing = [c for c in deps if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    window = int(os.getenv("VOLATILITY_LOOKBACK", 24))

    hl_log = np.log(df['High'] / df['Low'])
    factor = 1 / (4 * window * np.log(2))
    df['parkinson_vol'] = np.sqrt(factor * (hl_log ** 2).rolling(window).sum())

    return df
```

**Required rules:**
- Function name must be `extract_features`
- Always `return df`
- Assign numpy arrays directly (`df['col'] = arr`), do not wrap with `pd.Series()` to avoid index misalignment
- Use `os.getenv("KEY", default)` to read config

### 4b. Register in the pipeline

`src/autofcholv/pipeline/feature_engineering.py`:

```python
# Add import
from autofcholv.pipeline.features.volatility import extract_features as extract_volatility_features

# Add to steps[] at the correct position respecting dependency order
steps = [
    ...
    ("volatility_features", extract_volatility_features),
    ...
]
```

### 4c. Add config key (if needed)

`src/autofcholv/config/config.py` — add to `DEFAULT_CONFIG`:

```python
DEFAULT_CONFIG = {
    ...
    "MY_LOOKBACK": "20",
}
```

---

## Step 5 — Unit Test

Add tests to `tests/test_core.py` following the existing pattern:

```python
def test_extract_features_volatility_columns():
    result = extract_features(make_ohlcv(300))
    expected = ["parkinson_vol"]
    for col in expected:
        assert col in result.columns, f"Missing column: '{col}'"

def test_parkinson_vol_non_negative():
    result = extract_features(make_ohlcv(300))
    assert (result["parkinson_vol"].dropna() >= 0).all()
```

Run tests:
```bash
pytest tests/test_core.py -v
```

Tests must **pass** before moving to step 6.

---

## Step 6 — Update Roadmap

Open `docs/ROADMAP.md` and change `[ ]` → `[x]`:

```
- [x] `parkinson_vol` = Parkinson Volatility = ...
```

Then update `src/autofcholv/pipeline/features/README.md` — add the new column to the table for the corresponding module.

---

## Checklist

```
□ 1. Requirement: column name, type, formula, dependencies, config, module
□ 2. Check ROADMAP.md — add entry if missing
□ 3. Add entry to {module}.json
□ 4a. Implement extract_features() in {module}.py
□ 4b. Register in feature_engineering.py
□ 4c. Add DEFAULT_CONFIG key if needed
□ 5. Write + run unit tests (pytest pass)
□ 6. Change [ ] → [x] in ROADMAP.md + update features/README.md
```
