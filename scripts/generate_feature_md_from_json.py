#!/usr/bin/env python3
"""Generate the feature catalog markdown from feature JSON metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEATURE_DIR = REPO_ROOT / "src" / "autofcholv" / "pipeline" / "features"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "FEATURES.md"

PIPELINE_ORDER = [
    "time",
    "resample",
    "candlestick",
    "close",
    "price",
    "trend",
    "volatility",
    "volume",
    "liquidity",
    "lag",
    "mix",
    "group",
<<<<<<< HEAD
=======
    "kmeans",
    "hdbscan",
    "gmm",
    "signal",
>>>>>>> d1a4959 (develop(v0.4.0): add some clustering features)
]

MODULE_TITLES = {
    "time": "Time",
    "resample": "Daily Resample",
    "candlestick": "Candlestick Geometry",
    "close": "Close Price Indicators",
    "price": "Price Derived Indicators",
    "trend": "Trend Indicators",
    "volatility": "Volatility Indicators",
    "volume": "Volume",
    "liquidity": "Liquidity / Composite Proxies",
    "lag": "Lag Features",
    "mix": "Mixed / Advanced Indicators",
    "group": "Group / Pattern Features",
<<<<<<< HEAD
=======
    "kmeans": "K-Means Clustering Features",
    "hdbscan": "HDBSCAN Clustering Features",
    "gmm": "Gaussian Mixture Model (GMM) Clustering Features",
    "signal": "Signals",
>>>>>>> d1a4959 (develop(v0.4.0): add some clustering features)
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a markdown catalog from feature JSON files."
    )
    parser.add_argument(
        "--features-dir",
        type=Path,
        default=DEFAULT_FEATURE_DIR,
        help=f"Directory containing feature JSON files (default: {DEFAULT_FEATURE_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Markdown file to write (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def markdown_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def module_sort_key(path: Path) -> tuple[int, str]:
    try:
        return (PIPELINE_ORDER.index(path.stem), path.stem)
    except ValueError:
        return (len(PIPELINE_ORDER), path.stem)


def module_title(stem: str) -> str:
    return MODULE_TITLES.get(stem, stem.replace("_", " ").title())


def load_feature_file(path: Path) -> dict[str, dict[str, Any]]:
    if path.stat().st_size == 0:
        return {}

    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    for column, metadata in data.items():
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}: metadata for {column!r} must be an object")

    return data


def render_markdown(feature_files: list[Path]) -> str:
    lines = [
        "# 📊 Features Catalog",
        "",
        "Each module produces a set of columns documented in its corresponding `.json` file.",
        "The pipeline executes in the order listed below.",
        "",
        "---",
        "",
    ]

    for index, path in enumerate(feature_files, start=1):
        features = load_feature_file(path)
        if not features:
            continue

        lines.extend(
            [
                f"## {index}. {module_title(path.stem)} — `{path.stem}.py`",
                "",
                "| Column | Type | Description |",
                "|---|---|---|",
            ]
        )

        for column, metadata in features.items():
            lines.append(
                "| "
                f"`{markdown_escape(column)}` | "
                f"{markdown_escape(metadata.get('type', ''))} | "
                f"{markdown_escape(metadata.get('comment', ''))} |"
            )

        lines.extend(["", "---", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    features_dir = args.features_dir.resolve()
    output = args.output.resolve()

    feature_files = sorted(
        (path for path in features_dir.glob("*.json") if path.stat().st_size > 0),
        key=module_sort_key,
    )
    if not feature_files:
        raise FileNotFoundError(f"No JSON files found in {features_dir}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(feature_files), encoding="utf-8")
    print(f"Generated {output} from {len(feature_files)} JSON files.")


if __name__ == "__main__":
    main()
