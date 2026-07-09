# TODO: Migrate Valid Strategies Into Strategy Signals

Goal: migrate all valid strategies from `/mnt/Shares/GIT/the-new-algo/strategies/src/strategies` into `src/autofcholv/pipeline/features/strategy.py`.

`strategy.py` must remain signal-only. It may only compose already-generated feature columns into final strategy signal columns such as `signal_pro1`, `signal_pro2`, ... Any reusable condition, indicator, session aggregate, range statistic, or helper feature required by a strategy must live in the appropriate feature module before `strategy.py` runs.

## Scope

- [ ] Treat only root strategy files as valid migration sources: `strategy-001.py` through `strategy-029.py`.
- [ ] Exclude `/mnt/Shares/GIT/the-new-algo/strategies/src/strategies/invalid/**`.
- [ ] Exclude `strategy-sample.py`; use it only as style/reference material.
- [ ] Preserve causal behavior from the original strategies. Any rolling/session aggregate used for entry conditions must avoid future bars and must use `shift(1)` where the source strategy did.
- [ ] Convert source signals from `long` / `short` / empty string into the project signal convention selected for `strategy.py`. Prefer one consistent helper such as `Buy` / `Sell` / `None` if matching existing signal features.

## Implementation Plan

- [ ] Add `strategy_features` to `FEATURE_STEPS` in `src/autofcholv/pipeline/feature_engineering.py` after all condition-feature modules it depends on.
- [ ] Keep `src/autofcholv/pipeline/features/strategy.py` limited to:
  - required-column validation,
  - small signal-composition helpers,
  - assignment of `signal_pro1`, `signal_pro2`, ..., `signal_pro29`.
- [ ] Move non-signal calculations out of `strategy.py` into existing feature modules:
  - `time.py`: `trade_date`, `time_code` alias if needed, `bar_in_day`, session masks/windows.
  - `resample.py`: previous-day close/open/high/low, first close/open of session, prior day bias inputs, morning/opening-range daily joins.
  - `candlestick.py`: body, body rate, Heikin-Ashi fields, bar close position, close-vs-range position.
  - `close.py`: RSI variants, MACD histogram variants, Williams %R, StochRSI, Bollinger percent.
  - `trend.py`: EMA variants, linear-regression slope, ADX/DMP/DMN, PSAR flags, trend filters.
  - `volatility.py`: Keltner bands, Donchian channels, close Donchian channels, ATR/range features, VWAP z-score bands.
  - `volume.py`: volume moving averages, signed volume, flow imbalance.
  - `price.py` or `liquidity.py`: intraday VWAP, VWAP deviation, VWAP bands/std, pivot points.
  - `mix.py` or `group.py`: reusable composite condition features such as ORB breakout conditions, day-bias buckets, acceptance/persistence windows.
- [ ] Update each changed feature module's matching JSON metadata file when adding or renaming feature columns.
- [ ] Update `src/autofcholv/pipeline/features/strategy.json` with metadata for `signal_pro1` through `signal_pro29`.
- [ ] Regenerate `docs/FEATURES.md` with `python3 scripts/generate_feature_md_from_json.py` after metadata changes.
- [ ] Update `docs/STRUCTURE.md` for any added, moved, or renamed files.
- [ ] Run focused tests after each batch, then the full suite before finishing.

## Signal Mapping

- [ ] `signal_pro1`: migrate `strategy-001.py` / `MomentumStrategy`.
- [ ] `signal_pro2`: migrate `strategy-002.py` / `OpeningGapORBStrategy`.
- [ ] `signal_pro3`: migrate `strategy-003.py` / `NextDayMomentumBreakoutStrategy`.
- [ ] `signal_pro4`: migrate `strategy-004.py` / `MainStrategy`.
- [ ] `signal_pro5`: migrate `strategy-005.py` / `Mix3Strategy`.
- [ ] `signal_pro6`: migrate `strategy-006.py` / `OpenRangeTrendStrategy`.
- [ ] `signal_pro7`: migrate `strategy-007.py` / `OpenRangeTrend52Strategy`.
- [ ] `signal_pro8`: migrate `strategy-008.py` / `OpenRangeTrendDayBiasStrategy`.
- [ ] `signal_pro9`: migrate `strategy-009.py` / `KeltnerBreakoutStrategy`.
- [ ] `signal_pro10`: migrate `strategy-010.py` / `DonchianBreakoutStrategy`.
- [ ] `signal_pro11`: migrate `strategy-011.py` / `VWAPBandBreakoutStrategy`.
- [ ] `signal_pro12`: migrate `strategy-012.py` / `KeltnerHeikinAshiStrategy`.
- [ ] `signal_pro13`: migrate `strategy-013.py` / `PivotPointBreakoutStrategy`.
- [ ] `signal_pro14`: migrate `strategy-014.py` / `CloseDonchianBreakoutStrategy`.
- [ ] `signal_pro15`: migrate `strategy-015.py` / `KeltnerStochRSIStrategy`.
- [ ] `signal_pro16`: migrate `strategy-016.py` / `KeltnerMACDStrategy`.
- [ ] `signal_pro17`: migrate `strategy-017.py` / `KeltnerTripleEMAStrategy`.
- [ ] `signal_pro18`: migrate `strategy-018.py` / `KeltnerPSARStrategy`.
- [ ] `signal_pro19`: migrate `strategy-019.py` / `DonchianMACDStrategy`.
- [ ] `signal_pro20`: migrate `strategy-020.py` / `WilliamsRMACDStrategy`.
- [ ] `signal_pro21`: migrate `strategy-021.py` / `BBPctMACDStrategy`.
- [ ] `signal_pro22`: migrate `strategy-022.py` / `BarClosePctMACDStrategy`.
- [ ] `signal_pro23`: migrate `strategy-023.py` / `LateSessionStrengthContinuationStrategy`.
- [ ] `signal_pro24`: migrate `strategy-024.py` / `LateSessionFlowImbalanceStrategy`.
- [ ] `signal_pro25`: migrate `strategy-025.py` / `OrbBodyStrengthStrategy`.
- [ ] `signal_pro26`: migrate `strategy-026.py` / `IntradayBodyRateMomStrategy`.
- [ ] `signal_pro27`: migrate `strategy-027.py` / `LateSessionRangePositionStrategy`.
- [ ] `signal_pro28`: migrate `strategy-028.py` / `LateSessionVWAPZScoreExpansionStrategy`.
- [ ] `signal_pro29`: migrate `strategy-029.py` / `MorningRangeAcceptanceStrategy`.

## Suggested Migration Batches

- [ ] Batch 1: session/time foundations and ORB family: `strategy-002.py`, `strategy-006.py`, `strategy-007.py`, `strategy-008.py`, `strategy-025.py`.
- [ ] Batch 2: daily momentum and mixed day-bias logic: `strategy-001.py`, `strategy-003.py`, `strategy-004.py`, `strategy-005.py`, `strategy-026.py`.
- [ ] Batch 3: Keltner/Donchian/VWAP breakout family: `strategy-009.py`, `strategy-010.py`, `strategy-011.py`, `strategy-012.py`, `strategy-013.py`, `strategy-014.py`.
- [ ] Batch 4: oscillator/channel confirmations: `strategy-015.py`, `strategy-016.py`, `strategy-017.py`, `strategy-018.py`, `strategy-019.py`, `strategy-020.py`, `strategy-021.py`, `strategy-022.py`.
- [ ] Batch 5: late-session and morning acceptance strategies: `strategy-023.py`, `strategy-024.py`, `strategy-027.py`, `strategy-028.py`, `strategy-029.py`.

## Tests And Acceptance Criteria

- [ ] Add/extend tests in `tests/test_core.py` to assert `signal_pro1` through `signal_pro29` exist after `extract_features`.
- [ ] Add tests that `strategy.py` does not create non-signal columns. The set of new columns from this module should match only `signal_pro*`.
- [ ] Add focused leakage tests for previous-day aggregates, opening/morning ranges, rolling highs/lows, and session cumulative features.
- [ ] Add at least one synthetic fixture that can trigger a Buy and one that can trigger a Sell for representative strategy families.
- [ ] Run `uv run pytest tests/test_core.py`.
- [ ] Run `uv run pytest`.
