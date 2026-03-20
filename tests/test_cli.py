import os
import subprocess
import tempfile

import numpy as np
import pandas as pd
import pytest


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def _cli_path() -> str:
    """Đường dẫn tới CLI trong venv."""
    return os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "autofcholv")


def _make_ohlcv_csv(path: str, n_bars: int = 300) -> None:
    """Ghi file CSV OHLCV 5-minute hợp lệ ra `path`."""
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]

    rng = np.random.default_rng(0)
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
    df.to_csv(path)


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def test_cli_help():
    """--help phải trả về returncode 0 và in tên tool."""
    result = subprocess.run([_cli_path(), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "autofcholv" in result.stdout


def test_cli_version():
    """--version phải trả về returncode 0."""
    result = subprocess.run([_cli_path(), "--version"], capture_output=True, text=True)
    assert result.returncode == 0


def test_cli_no_input_prints_help():
    """Không truyền input → in help và exit 0 (không crash)."""
    result = subprocess.run([_cli_path()], capture_output=True, text=True)
    assert result.returncode == 0


def test_cli_nonexistent_file():
    """File không tồn tại → exit 1 và in thông báo lỗi ra stderr."""
    result = subprocess.run(
        [_cli_path(), "nonexistent_file_xyz.csv"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_successful_extraction():
    """Pipeline đầy đủ: input hợp lệ → output CSV được tạo với đúng cột."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "input.csv")
        output_path = os.path.join(tmpdir, "output.csv")
        _make_ohlcv_csv(input_path, n_bars=300)

        result = subprocess.run(
            [_cli_path(), input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert result.returncode == 0, f"CLI thất bại:\n{result.stderr}"
        assert os.path.exists(output_path), "File output không được tạo"

        out_df = pd.read_csv(output_path, index_col="Date")
        assert len(out_df) > 0, "Output CSV rỗng"

        # Kiểm tra các cột key từ mỗi module
        expected_cols = [
            "hour", "session_progress",           # time.py
            "day_high", "prev_day_close",          # resample.py
            "cs_body", "cs_color",                 # candlestick.py
            "EMA20", "EMA250", "RSI20",            # close.py
            "ATR14", "VWAP", "fea_g1_001",         # mix.py
        ]
        for col in expected_cols:
            assert col in out_df.columns, f"Thiếu cột output: '{col}'"


def test_cli_output_log_messages():
    """Stdout phải chứa các dòng log về kích thước và thời gian."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "input.csv")
        output_path = os.path.join(tmpdir, "output.csv")
        _make_ohlcv_csv(input_path, n_bars=300)

        result = subprocess.run(
            [_cli_path(), input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert "Input CSV length" in result.stdout
        assert "Total extracting time" in result.stdout
        assert "Output CSV length" in result.stdout
        assert "Output CSV columns" in result.stdout


def test_cli_invalid_csv_no_ohlcv():
    """CSV thiếu cột OHLCV → exit 1 và in lỗi ra stderr."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "bad_input.csv")
        output_path = os.path.join(tmpdir, "output.csv")

        # CSV có cột Date nhưng thiếu OHLCV
        bad_df = pd.DataFrame({"Date": ["2024-01-02"], "foo": [1]})
        bad_df.to_csv(input_path, index=False)

        result = subprocess.run(
            [_cli_path(), input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert result.returncode == 1
        assert "Error" in result.stderr
