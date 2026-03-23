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
    return os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "autofcholv")


def _make_ohlcv_csv(path: str, n_bars: int = 300) -> None:
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]

    rng    = np.random.default_rng(0)
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
    result = subprocess.run([_cli_path(), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "autofcholv" in result.stdout


def test_cli_version():
    result = subprocess.run([_cli_path(), "--version"], capture_output=True, text=True)
    assert result.returncode == 0


def test_cli_no_input_prints_help():
    result = subprocess.run([_cli_path()], capture_output=True, text=True)
    assert result.returncode == 0


def test_cli_nonexistent_file():
    result = subprocess.run(
        [_cli_path(), "extract", "nonexistent_file_xyz.csv"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_successful_extraction():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "input.csv")
        output_path = os.path.join(tmpdir, "output.csv")
        _make_ohlcv_csv(input_path, n_bars=300)

        result = subprocess.run(
            [_cli_path(), "extract", input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
        assert os.path.exists(output_path), "Output file was not created"

        out_df = pd.read_csv(output_path, index_col="Date")
        assert len(out_df) > 0, "Output CSV is empty"

        # Spot-check one key column per module
        expected_cols = [
            "hour", "session_progress",          # time.py
            "day_high", "prev_day_close",         # resample.py
            "body", "color",                      # candlestick.py
            "ema_fast", "ema_slow", "rsi",        # close.py
            "volume_avg", "volume_zscore",        # volume.py
            "close_lag1", "rsi_lag1",             # lag.py
            "atr", "vwap", "custom_001",          # mix.py
            "volume_group", "vol_high_pattern",   # group.py
            "couple_cs_signal", "ema_cross_signal",  # signal.py
        ]
        for col in expected_cols:
            assert col in out_df.columns, f"Missing output column: '{col}'"


def test_cli_output_log_messages():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "input.csv")
        output_path = os.path.join(tmpdir, "output.csv")
        _make_ohlcv_csv(input_path, n_bars=300)

        result = subprocess.run(
            [_cli_path(), "extract", input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert "Input CSV length" in result.stdout
        assert "Total extracting time" in result.stdout
        assert "Output CSV length" in result.stdout
        assert "Output CSV columns" in result.stdout


def test_cli_generate_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.env")

        result = subprocess.run(
            [_cli_path(), "generate-config", "--path", config_path],
            capture_output=True, text=True,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
        assert os.path.exists(config_path), "Config file was not created"

        with open(config_path) as f:
            content = f.read()
        assert "SELECTED_TIME_FRAME" in content


def test_cli_invalid_csv_no_ohlcv():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "bad_input.csv")
        output_path = os.path.join(tmpdir, "output.csv")

        bad_df = pd.DataFrame({"Date": ["2024-01-02"], "foo": [1]})
        bad_df.to_csv(input_path, index=False)

        result = subprocess.run(
            [_cli_path(), "extract", input_path, "--output", output_path],
            capture_output=True, text=True,
        )

        assert result.returncode == 1
        assert "Error" in result.stderr
