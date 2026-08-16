# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-16

### Added
- **New Feature Modules**:
  - `trend.py` & `trend.json`: Comprehensive trend, moving averages, Ichimoku, ADX, Aroon, Vortex, and directional features.
  - `volatility.py` & `volatility.json`: Volatility, Bollinger Bands, ATR, Keltner/Donchian channels, Choppiness, and historical volatility.
  - `price.py` & `price.json`: Price action dynamics, VWAP, typical price, intraday range ratios, and gap features.
  - `liquidity.py` & `liquidity.json`: Liquidity measures, bid/ask spread proxies, order flow imbalances, and market impact metrics.
- **Dynamic Configuration & Lookback Windows**:
  - Flexible `CLASSIC_INDICATORS` dictionary config for standard technical indicators (RSI, STOCHRSI, MACD, PPO, WILLIAMS_R, AO, UO, MFI, SUPERTREND, TRIX, ADX, CHOP, CONNORS_RSI).
  - Dynamic `EMA_WINDOWS` list configuration for multi-period exponential moving average generation.
  - Configurable 5-tier rolling windows (`T1` to `T5`) and session-based bar counts (`MORNING_BARS`, `AFTERNOON_BARS`, `SESSION_BARS`).
  - Configurable sequence coercion for string/list lookback parameters.
- **I/O & CLI Enhancements**:
  - Native Apache Parquet (`.parquet`, `.pq`) support for fast feature extraction reading and writing.
  - Interactive progress bar (`tqdm`) with stage-by-stage timing during feature extraction.
- **Indicator Calculation Cache**:
  - `src/autofcholv/utils/indicators.py`: Shared caching layer for common indicators to eliminate redundant calculations across modules.
- **Documentation & Automation Tooling**:
  - Automated feature catalog generator (`scripts/generate_feature_md_from_json.py`).
  - Automated documentation synchronizers (`scripts/generate_root_readme.sh`, `scripts/generate_agents_markdown.sh`).
  - Feature JSON metadata catalog paired with all feature modules.

### Changed
- **Feature Standardization**:
  - Converted all output feature column names to standard `snake_case`.
- **Signal Re-architecture**:
  - Refactored `signal.py` to strictly produce boolean/numeric trading signals derived from existing upstream features, preserving modular pipeline separation.
- **Lookback Parameterization**:
  - Completely removed all hardcoded window lookbacks across feature modules, migrating them to configuration-driven lookbacks.
- **Data Integrity & Leakage Prevention**:
  - Audited and fixed lookahead data leakage in resampled daily aggregates and session-level features with strict `.shift(1)` lookback boundaries.
- **Memory & Performance**:
  - Implemented strategic `df = df.copy()` memory defragmentation checkpoints across heavy feature modules, eliminating `PerformanceWarning: DataFrame is highly fragmented` and optimizing memory layout.

### Removed
- Removed asset-specific `vn30f1m.py` module to maintain `autofcholv` as a generic OHLCV feature engineering library.
- Removed deprecated/unused fixed-period named feature columns (`ema_20_cross_*`, `adx_42`, `linear_regression_slope_8`, `bias36`, `bias36ma`, `macd_hist_12_26_9`, `donchian_*_30_shift1`, `persist_short_12_shift1`, `prev_*_ema_bias_20`).
- Removed legacy duplicate indicators and unreferenced strategy helper scripts.

### Fixed / Quality
- Expanded test suite to 55 comprehensive tests (15 CLI tests, 40 core pipeline tests) covering configuration propagation, edge cases, schema validation, and multi-timeframe feature extraction.


## [0.2.0] - 2026-03-23

### Added
- New flexible configuration system supporting:
    - Environment variables.
    - JSON and YAML configuration files.
    - Built-in defaults.
- Added `PyYAML` dependency for YAML support.
- New CLI command: `generate-config` to create a template `.env` file.
- New CLI option: `--config` (`-c`) for `extract` command to provide custom configuration.
- Exported `load_config` and `generate_default_config_file` in the main package for API use.

### Changed
- `extract_features` now automatically calls `load_config()`.

### Fixed
- Improved CLI tests to be more portable across different environments.
- Fixed path issues in `test_cli.py`.

## [0.1.0] - 2026-03-01
### Initial Release
- Basic OHLCV feature extraction pipeline.
- CLI support for feature extraction.
