# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-16

### Added
- Flexible `CLASSIC_INDICATORS` configuration dictionary for standard indicators: RSI, STOCHRSI, MACD, PPO, WILLIAMS_R, AO, UO, MFI, SUPERTREND, TRIX, ADX, CHOP, CONNORS_RSI.
- Dynamic `EMA_WINDOWS` list configuration enabling custom multi-period EMA generation.
- Memory defragmentation checkpoints across all feature modules to optimize memory usage and eliminate `PerformanceWarning`.

### Changed
- Parameterized all remaining hardcoded lookback windows (5-tiers, morning/afternoon session bars, and classical indicator parameters).
- Enhanced configuration coercion for sequence/list types.

### Removed
- Removed unused and deprecated fixed-number named feature columns (`ema_20_cross_*`, `adx_42`, `linear_regression_slope_8`, `bias36`, `bias36ma`, `macd_hist_12_26_9`, `donchian_*_30_shift1`, `persist_short_12_shift1`, `prev_*_ema_bias_20`).

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
