# Project Structure

```text
.
├── README.md                         # Root README generated from selected docs files.
├── CHANGELOG.md                      # Release notes and project change history.
├── LICENSE                           # Project license.
├── pyproject.toml                    # Package metadata, dependencies, and CLI entry point.
├── uv.lock                           # Locked dependency versions for uv.
├── AGENTS.md                         # Local agent/development instructions.
│
├── docs/                             # Human-facing project documentation.
│   ├── AI_AGENT_GUIDELINE.md         # Source guideline text for generated AGENTS.md.
│   ├── CONFIGURATION.md              # Configuration loading and priority rules.
│   ├── FEATURES.md                   # Generated catalog of feature columns from JSON metadata.
│   ├── FEATURES_OVERVIEW.md          # High-level feature set overview.
│   ├── INSTALLATION.md               # Install instructions for pip, uv, and source installs.
│   ├── REF.md                        # Short project references and notes.
│   ├── RESOURCES.md                  # Links to related project docs.
│   ├── RULE.md                       # Project rules or conventions.
│   ├── STRUCTURE.md                  # This repository structure guide.
│   ├── TODO.md                       # Pending documentation and implementation notes.
│   └── USAGE.md                      # CLI and Python API usage examples.
│
├── examples/                         # Small examples for users.
│   └── simple_usage.py               # Minimal Python API usage example.
│
├── scripts/                          # Maintenance and documentation scripts.
│   ├── generate_agents_markdown.sh   # Rebuilds AGENTS.md from agent-facing docs.
│   ├── generate_feature_md_from_json.py
│   │                                   # Generates docs/FEATURES.md from feature JSON metadata.
│   └── generate_root_readme.sh        # Rebuilds README.md from selected docs files.
│
├── src/                              # Python source root.
│   └── autofcholv/                   # Main package.
│       ├── __init__.py               # Package exports.
│       ├── cli.py                    # Command line interface.
│       ├── core.py                   # Public extract_features(df) API.
│       │
│       ├── config/                   # Configuration support.
│       │   └── config.py             # Default config values and config loading.
│       │
│       ├── pipeline/                 # OHLCV processing pipeline.
│       │   ├── README.md             # Pipeline overview and processing stages.
│       │   ├── cleaning.py           # Cleans and normalizes raw OHLCV data.
│       │   ├── validation.py         # Validates OHLCV schema and price logic.
│       │   ├── feature_engineering.py
│       │   │                           # Runs feature modules in the configured order.
│       │   ├── preprocessing.py      # Final cleanup before returning features.
│       │   │
│       │   └── features/             # Feature modules and their metadata.
│       │       ├── __init__.py       # Feature package marker.
│       │       ├── candlestick.py    # Candlestick geometry features.
│       │       ├── candlestick.json  # Candlestick feature metadata.
│       │       ├── close.py          # Close-price momentum and oscillator features.
│       │       ├── close.json        # Close-price feature metadata.
│       │       ├── group.py          # Grouped pattern/category features.
│       │       ├── group.json        # Group feature metadata.
│       │       ├── lag.py            # Lagged OHLCV and indicator features.
│       │       ├── lag.json          # Lag feature metadata.
│       │       ├── liquidity.py      # Liquidity and market placement features.
│       │       ├── liquidity.json    # Liquidity feature metadata.
│       │       ├── mix.py            # Mixed and advanced composite features.
│       │       ├── mix.json          # Mixed feature metadata.
│       │       ├── price.py          # Price-derived features such as VWAP and typical price.
│       │       ├── price.json        # Price feature metadata.
│       │       ├── resample.py       # Daily resample and previous-day features.
│       │       ├── resample.json     # Resample feature metadata.
│       │       ├── signal.py         # Signal/idea features.
│       │       ├── signal.json       # Signal feature metadata.
│       │       ├── strategy.py       # Strategy-oriented feature logic under development.
│       │       ├── strategy.json     # Strategy metadata placeholder.
│       │       ├── time.py           # Time/session features.
│       │       ├── time.json         # Time feature metadata.
│       │       ├── trend.py          # Trend and moving-average features.
│       │       ├── trend.json        # Trend feature metadata.
│       │       ├── volatility.py     # Volatility, bands, ATR, and channel features.
│       │       ├── volatility.json   # Volatility feature metadata.
│       │       ├── volume.py         # Volume and money-flow features.
│       │       └── volume.json       # Volume feature metadata.
│       │
│       └── utils/                    # Shared utilities.
│           └── timing.py             # Timing helpers for pipeline steps.
│
└── tests/                            # Automated tests.
    ├── test_cli.py                   # CLI tests.
    └── test_core.py                  # Core extraction and feature coverage tests.
```

## Notes

* Feature modules are wired into the pipeline in `src/autofcholv/pipeline/feature_engineering.py`.
* Feature metadata JSON files are used to generate `docs/FEATURES.md`.
* `README.md` is generated from selected files in `docs/` by `scripts/generate_root_readme.sh`.
* `AGENTS.md` is generated from agent-facing docs by `scripts/generate_agents_markdown.sh`.
