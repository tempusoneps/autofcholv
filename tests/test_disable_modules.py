import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from autofcholv.config.config import Config, load_config, _config_from_mapping
from autofcholv.pipeline.feature_engineering import FEATURE_STEPS, get_feature_steps
from autofcholv.core import extract_features, get_extract_progress_steps, EXTRACT_PROGRESS_STEPS


def _make_sample_df(n_bars: int = 300) -> pd.DataFrame:
    idx = pd.date_range(start="2024-01-02 09:05:00", periods=n_bars, freq="5min")
    rng = np.random.default_rng(42)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    close = np.maximum(close, 10.0)
    open_ = close * (1 + rng.normal(0, 0.001, len(idx)))
    high = close * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    low = close * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    volume = rng.integers(1000, 10000, len(idx)).astype(float)
    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
    df.index.name = "Date"
    df["High"] = df[["Open", "Close", "High"]].max(axis=1)
    df["Low"] = df[["Open", "Close", "Low"]].min(axis=1)
    return df


def test_default_config_disable_modules_empty():
    cfg = Config()
    assert cfg.disable_modules == []
    steps = get_feature_steps(cfg)
    assert len(steps) == len(FEATURE_STEPS)
    assert get_extract_progress_steps(cfg) == EXTRACT_PROGRESS_STEPS


def test_config_from_mapping_disable_modules_list():
    raw = {"DISABLE_MODULES": ["agglomerative", "optics", "spectral"]}
    cfg = _config_from_mapping(raw)
    assert cfg.disable_modules == ["agglomerative", "optics", "spectral"]

    steps = get_feature_steps(cfg)
    step_names = [s[0] for s in steps]
    assert "agglomerative_features" not in step_names
    assert "optics_features" not in step_names
    assert "spectral_features" not in step_names
    assert "kmeans_features" in step_names
    assert len(steps) == len(FEATURE_STEPS) - 3
    assert get_extract_progress_steps(cfg) == 3 + len(FEATURE_STEPS) - 3


def test_config_from_mapping_disable_modules_alias_with_space():
    raw = {"DISABLE _MODULES": ["spectral", "optics"]}
    cfg = _config_from_mapping(raw)
    assert cfg.disable_modules == ["spectral", "optics"]
    steps = get_feature_steps(cfg)
    step_names = [s[0] for s in steps]
    assert "spectral_features" not in step_names
    assert "optics_features" not in step_names


def test_config_from_mapping_disable_modules_dict():
    raw = {
        "DISABLE_MODULES": {
            "agglomerative": True,
            "spectral": True,
            "kmeans": False,
        }
    }
    cfg = _config_from_mapping(raw)
    assert "agglomerative" in cfg.disable_modules
    assert "spectral" in cfg.disable_modules
    assert "kmeans" not in cfg.disable_modules


def test_config_from_mapping_disable_modules_full_name():
    raw = {"DISABLE_MODULES": ["kmeans_features", "hdbscan_features"]}
    cfg = _config_from_mapping(raw)
    steps = get_feature_steps(cfg)
    step_names = [s[0] for s in steps]
    assert "kmeans_features" not in step_names
    assert "hdbscan_features" not in step_names


def test_extract_features_skips_disabled_modules():
    df = _make_sample_df(300)
    # Disable all clustering to make test run fast and verify skipping
    clustering_modules = [
        "kmeans", "hdbscan", "gmm", "dbscan",
        "agglomerative", "birch", "optics", "spectral"
    ]
    cfg = Config(disable_modules=clustering_modules)
    res = extract_features(df, config=cfg)

    # Base features should be present
    assert "rsi_medium" in res.columns
    assert "body" in res.columns

    # Clustering features should NOT be present
    for col in res.columns:
        assert not col.startswith("cluster_kmeans"), f"Unexpected column: {col}"
        assert not col.startswith("cluster_spectral"), f"Unexpected column: {col}"
        assert not col.startswith("cluster_agglomerative"), f"Unexpected column: {col}"
        assert not col.startswith("cluster_optics"), f"Unexpected column: {col}"


def test_cli_with_config_disable_modules():
    import subprocess
    import sys
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.csv"
        output_path = Path(tmpdir) / "output.csv"
        config_path = Path(tmpdir) / "custom_config.json"

        df = _make_sample_df(300)
        df.to_csv(input_path)

        custom_cfg = {
            "DISABLE_MODULES": [
                "kmeans", "hdbscan", "gmm", "dbscan",
                "agglomerative", "birch", "optics", "spectral"
            ]
        }
        config_path.write_text(json.dumps(custom_cfg), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "autofcholv.cli", "extract", str(input_path), "-o", str(output_path), "-c", str(config_path), "--no-progress"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"CLI error:\n{result.stderr}"
        assert output_path.exists()

        out_df = pd.read_csv(output_path, index_col="Date")
        assert "rsi_medium" in out_df.columns
        for col in out_df.columns:
            assert not col.startswith("cluster_"), f"Unexpected clustering col: {col}"
