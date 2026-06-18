---
name: create-feature
description: Use when adding a new feature to the autofcholv pipeline — covers requirement clarification, roadmap check, JSON schema update, code implementation, unit test, and roadmap completion.
---

# Create Feature

## Overview

Quy trình chuẩn để thêm một feature mới vào pipeline autofcholv. Gồm 6 bước tuần tự — không bỏ bước nào.

---

## Step 1 — Requirement

Xác định rõ trước khi viết bất kỳ dòng code nào:

- **Tên cột output** (ví dụ: `parkinson_vol`, `roc_3`)
- **Kiểu dữ liệu** (`float` / `int` / `str` / `bool`)
- **Công thức / logic**
- **Cột phụ thuộc** — feature này cần cột nào từ bước trước?
- **Config key** — có cần lookback period không? Dùng key nào trong `DEFAULT_CONFIG`?
- **Module** — thêm vào file `.py` nào? (file mới hay ghép vào file có sẵn?)

**Thứ tự pipeline hiện tại** (phụ thuộc phải đứng TRƯỚC):
```
1. time        2. resample    3. candlestick  4. close
5. volume      6. lag         7. mix          8. group
9. signal
```

---

## Step 2 — Check Roadmap

Mở `docs/ROADMAP.md`, tìm feature theo tên:

```
- [ ] `parkinson_vol` = Parkinson Volatility = ...
```

- Nếu **có** → feature đã được plan, tiếp tục bước 3.
- Nếu **không có** → thêm dòng mới vào đúng nhóm trong ROADMAP trước khi implement.

---

## Step 3 — Update JSON File

Mỗi feature module có file JSON tương ứng tại:
`src/autofcholv/pipeline/features/{module}.json`

Thêm entry cho từng cột output mới:

```json
{
    "parkinson_vol": {
        "type": "float",
        "name": "Parkinson Volatility",
        "comment": "Rolling Parkinson Volatility = sqrt(1/(4n*ln2) * sum(ln(H/L)^2))"
    }
}
```

**Format bắt buộc:**
- `type`: `"float"` | `"int"` | `"str"` | `"bool"`
- `name`: Tên hiển thị (viết hoa chữ đầu)
- `comment`: Công thức hoặc mô tả ngắn

---

## Step 4 — Implement Code

### 4a. Tạo / sửa file feature

`src/autofcholv/pipeline/features/{module}.py`

```python
import os
import numpy as np
import pandas as pd

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    # Guard: kiểm tra cột phụ thuộc nếu có
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

**Lưu ý bắt buộc:**
- Tên hàm phải là `extract_features`
- Luôn `return df`
- Gán numpy array trực tiếp (`df['col'] = arr`), không wrap qua `pd.Series()` để tránh lệch index
- Dùng `os.getenv("KEY", default)` để đọc config

### 4b. Đăng ký vào pipeline

`src/autofcholv/pipeline/feature_engineering.py`:

```python
# Thêm import
from autofcholv.pipeline.features.volatility import extract_features as extract_volatility_features

# Thêm vào steps[] đúng vị trí thứ tự phụ thuộc
steps = [
    ...
    ("volatility_features", extract_volatility_features),
    ...
]
```

### 4c. Thêm config key (nếu cần)

`src/autofcholv/config/config.py` — thêm vào `DEFAULT_CONFIG`:

```python
DEFAULT_CONFIG = {
    ...
    "MY_LOOKBACK": "20",
}
```

---

## Step 5 — Unit Test

Thêm test vào `tests/test_core.py` theo đúng pattern hiện có:

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

Chạy test:
```bash
pytest tests/test_core.py -v
```

Test phải **pass** trước khi sang bước 6.

---

## Step 6 — Update Roadmap

Mở `docs/ROADMAP.md`, đổi `[ ]` → `[x]`:

```
- [x] `parkinson_vol` = Parkinson Volatility = ...
```

Sau đó cập nhật `src/autofcholv/pipeline/features/README.md` — thêm cột mới vào bảng của module tương ứng.

---

## Checklist

```
□ 1. Requirement: tên cột, kiểu, công thức, phụ thuộc, config, module
□ 2. Check ROADMAP.md — thêm nếu chưa có
□ 3. Thêm entry vào {module}.json
□ 4a. Implement extract_features() trong {module}.py
□ 4b. Đăng ký trong feature_engineering.py
□ 4c. Thêm DEFAULT_CONFIG key nếu cần
□ 5. Viết + chạy unit test (pytest pass)
□ 6. Đổi [ ] → [x] trong ROADMAP.md + cập nhật features/README.md
```
