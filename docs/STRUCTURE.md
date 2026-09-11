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
│   ├── GIT_CONVENTIONS.md            # Git workflow and structured commit conventions.
│   ├── INSTALLATION.md               # Install instructions for pip, uv, and source installs.
│   ├── PLAN_v0.4.0.md                # Implementation plan for version 0.4.0 features.
│   ├── REF.md                        # Short project references and notes.
│   ├── RESOURCES.md                  # Links to related project docs.
│   ├── RULE.md                       # Project rules or conventions.
│   ├── STRUCTURE.md                  # This repository structure guide.
│   ├── TODO.md                       # Pending documentation and implementation notes.
│   ├── USAGE.md                      # CLI and Python API usage examples.
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
│       │   ├── config.default.json   # Packaged default configuration.
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
│       │       ├── agglomerative.py  # Agglomerative hierarchical clustering features.
│       │       ├── agglomerative.json# Agglomerative feature metadata.
│       │       ├── birch.py          # BIRCH hierarchical clustering features.
│       │       ├── birch.json        # BIRCH feature metadata.
│       │       ├── candlestick.py    # Candlestick geometry features.
│       │       ├── candlestick.json  # Candlestick feature metadata.
│       │       ├── close.py          # Close-price momentum and oscillator features.
│       │       ├── close.json        # Close-price feature metadata.
│       │       ├── dbscan.py         # DBSCAN density-based clustering features.
│       │       ├── dbscan.json       # DBSCAN feature metadata.
│       │       ├── gmm.py            # Gaussian Mixture Model clustering and probabilistic regimes.
│       │       ├── gmm.json          # Gaussian Mixture Model feature metadata.
│       │       ├── group.py          # Grouped pattern/category features.
│       │       ├── group.json        # Group feature metadata.
│       │       ├── hdbscan.py        # HDBSCAN density clustering and noise detection.
│       │       ├── hdbscan.json      # HDBSCAN feature metadata.
│       │       ├── kmeans.py         # K-Means clustering features and market regimes.
│       │       ├── kmeans.json       # K-Means clustering feature metadata.
│       │       ├── lag.py            # Lagged OHLCV and indicator features.
│       │       ├── lag.json          # Lag feature metadata.
│       │       ├── liquidity.py      # Liquidity and market placement features.
│       │       ├── liquidity.json    # Liquidity feature metadata.
│       │       ├── mix.py            # Mixed and advanced composite features.
│       │       ├── mix.json          # Mixed feature metadata.
│       │       ├── optics.py         # OPTICS density-based clustering features.
│       │       ├── optics.json       # OPTICS feature metadata.
│       │       ├── price.py          # Price-derived features such as VWAP and typical price.
│       │       ├── price.json        # Price feature metadata.
│       │       ├── resample.py       # Daily resample and previous-day features.
│       │       ├── resample.json     # Resample feature metadata.
│       │       ├── spectral.py       # Spectral graph-based clustering features.
│       │       ├── spectral.json     # Spectral clustering feature metadata.
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
│           ├── indicators.py         # Cached basic indicator calculation helpers.
│           └── timing.py             # Timing helpers for pipeline steps.
│
└── tests/                            # Automated tests.
    ├── test_cli.py                   # CLI tests.
    ├── test_core.py                  # Core extraction and feature coverage tests.
    ├── test_disable_modules.py       # Fast isolated tests for DISABLE_MODULES feature filtering.
    ├── test_liquidity_proxies.py     # Fast isolated tests for liquidity and microstructure proxies.
    ├── test_regime_squeeze.py        # Fast isolated tests for TTM Squeeze and regime features.
    ├── test_smc_structure.py         # Fast isolated tests for SMC and price action structure features.
    └── test_volatility_estimators.py # Fast isolated tests for range-based volatility estimators.
```

## Notes

* Feature modules are wired into the pipeline in `src/autofcholv/pipeline/feature_engineering.py`.
* Feature metadata JSON files are used to generate `docs/FEATURES.md`.
* `README.md` is generated from selected files in `docs/` by `scripts/generate_root_readme.sh`.
* `AGENTS.md` is generated from agent-facing docs by `scripts/generate_agents_markdown.sh`.
