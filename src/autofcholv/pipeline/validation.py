from typing import Dict, Any, Tuple
import pandas as pd


def validate_ohlcv_dataset(data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate OHLCV DataFrame với columns:
    Open, High, Low, Close, Volume
    """

    required_cols = ["Open", "High", "Low", "Close", "Volume"]

    # ==============================
    # 1️⃣ Check missing columns
    # ==============================
    missing_cols = [c for c in required_cols if c not in data.columns]
    if missing_cols:
        return {
            "is_valid": False,
            "error": f"Missing columns: {missing_cols}"
        }

    df = data.copy()

    # ==============================
    # 2️⃣ Convert numeric columns
    # ==============================
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    errors = []

    # ==============================
    # 4️⃣ Check NaN
    # ==============================
    nan_mask = df[required_cols].isnull().any(axis=1)
    if nan_mask.any():
        for idx in df[nan_mask].index:
            errors.append({
                "index": str(idx),
                "error": "Contains NaN values"
            })

    # ==============================
    # 5️⃣ Price logic
    # ==============================

    price_negative = (df[["Open", "High", "Low", "Close"]] < 0).any(axis=1)
    volume_negative = df["Volume"] < 0

    high_invalid = df["High"] < df[["Open", "Close", "Low"]].max(axis=1)
    low_invalid = df["Low"] > df[["Open", "Close", "High"]].min(axis=1)

    for idx in df.index:
        row_errors = {}

        if price_negative.loc[idx]:
            row_errors["price"] = "Negative price detected"

        if volume_negative.loc[idx]:
            row_errors["Volume"] = "Negative volume"

        if high_invalid.loc[idx]:
            row_errors["High"] = "High is not highest price"

        if low_invalid.loc[idx]:
            row_errors["Low"] = "Low is not lowest price"

        if row_errors:
            errors.append({
                "index": str(idx),
                "error": row_errors
            })

    # ==============================
    # 6️⃣ Duplicate Date
    # ==============================
    dup_mask = df.index.duplicated()
    if dup_mask.any():
        for idx in df[dup_mask].index:
            errors.append({
                "index": str(idx),
                "error": {"Date": "Duplicate date"}
            })

    delta = df.index.to_series().diff().median()
    if delta >= pd.Timedelta(days=1):
        errors.append({
            "index": 1,
            "error": "Only access dataframe 1m, 5m, 15m, 30m, 1h, 4h"
        })
    
    is_valid = len(errors) == 0
    return is_valid, {
        "is_valid": is_valid,
        "total_records": len(df),
        "invalid_records": len(errors),
        "error_details": errors
    }