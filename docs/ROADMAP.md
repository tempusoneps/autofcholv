# 📊 Features Catalog

Each module produces a set of columns documented in its corresponding `.json` file.
The pipeline executes in the order listed below.

`Status`: `[x]` implemented, `[ ]` planned.

---

## 1. Time — `time.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `hour` | int | Capture intraday timing effects | Giờ giao dịch |
| [x] | `minute` | int | Capture fine-grained time position | Phút giao dịch |
| [x] | `time_int` | int | Provide compact sortable session time | `100 * hour + minute` |
| [x] | `session_progress` | float | Normalize where the bar sits inside the trading session | Vị trí trong phiên |
| [x] | `day_of_week` | int | Capture weekday seasonality | Ngày trong tuần |
| [x] | `day_of_month` | int | Capture month-cycle effects | Ngày trong tháng |
| [x] | `month` | int | Capture monthly seasonality | Tháng |
| [x] | `year` | int | Preserve long-term calendar context | Năm |

---

## 2. Daily Resample — `resample.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `prev_day_open` | float | Provide previous session opening reference without look-ahead leakage | `day_open.shift(1)` |
| [x] | `prev_day_high` | float | Provide previous session resistance reference without look-ahead leakage | `day_high.shift(1)` |
| [x] | `prev_day_low` | float | Provide previous session support reference without look-ahead leakage | `day_low.shift(1)` |
| [x] | `prev_day_close` | float | Provide previous session closing anchor without look-ahead leakage | `day_close.shift(1)` |
| [x] | `prev_day_volume` | float | Compare current activity against prior daily participation | `day_volume.shift(1)` |
| [x] | `prev_day_pivot` | float | Provide prior-day balance level for bias and mean-reversion signals | `day_pivot.shift(1)` |

Current-day daily aggregates are used only as intermediate values to compute
`prev_day_*`, then dropped to avoid intraday look-ahead leakage.

---

## 3. Candlestick Geometry — `candlestick.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `body` | float | Measure candle directional displacement | `Close - Open` (âm = nến đỏ) |
| [x] | `height` | float | Measure total candle range | `High - Low` |
| [x] | `upwick` | float | Measure upper rejection pressure | `High - max(Open, Close)` |
| [x] | `lowwick` | float | Measure lower rejection pressure | `min(Open, Close) - Low` |
| [x] | `upwick_rate` | float | Normalize upper wick by full candle range | `upwick / height` |
| [x] | `lowwick_rate` | float | Normalize lower wick by full candle range | `lowwick / height` |
| [x] | `body_rate` | float | Normalize body size by full candle range | `body / height` |
| [x] | `clv` | float | Locate close inside the candle range | Close Location Value |
| [x] | `cbr` | float | Measure body dominance inside the range | `abs(Close - Open) / height` |
| [x] | `vbr` | float | Relate volume to candle range | `Volume / (High - Low)` |
| [x] | `ibs` | float | Locate close between high and low | `(Close - Low) / (High - Low)` |
| [x] | `color` | str | Encode candle direction as category | `green` \| `red` \| `doji` |
| [x] | `wick_imbalance` | float | Compare upper and lower rejection strength | `upwick - lowwick` |
| [x] | `upwick_ratio` | float | Express upper wick relative to lower wick | `upwick / (lowwick + ε)` |

---

## 4. Close Price Indicators — `close.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `ema_fast` | float | Track short-term trend level | EMA(`FAST_TREND_LOOKBACK`) |
| [x] | `ema_slow` | float | Track slower trend level | EMA(`LOW_TREND_LOOKBACK`) |
| [x] | `rsi` | float | Measure momentum exhaustion and strength | RSI(`MOMENTUM_LOOKBACK`) |
| [x] | `rsi_slope` | float | Capture momentum acceleration or fading | `rsi.diff()` |
| [x] | `tsi` | float | Smooth directional momentum signal | True Strength Index |
| [x] | `roc_close` | float | Measure one-bar close momentum | Rate of Change (length=1) |
| [x] | `close_zscore` | float | Detect statistically stretched closes | Z-score of Close (`MOMENTUM_LOOKBACK`) |
| [x] | `efficiency_ratio` | float | Distinguish directional movement from noise | Kaufman Efficiency Ratio |
| [x] | `macd` | float | Capture trend momentum spread | MACD (12, 26, 9) |
| [x] | `macd_signal` | float | Smooth MACD for crossover context | MACD Signal |
| [x] | `macd_hist` | float | Measure MACD impulse strength | MACD Histogram |
| [x] | `ppo` | float | Capture percentage trend momentum spread | PPO (12, 26, 9) |
| [x] | `ppo_signal` | float | Smooth PPO for crossover context | PPO Signal |
| [x] | `ppo_hist` | float | Measure PPO impulse strength | PPO Histogram |
| [x] | `ulcer_index` | float | Quantify downside risk and drawdown pressure | Ulcer Index (`MOMENTUM_LOOKBACK`) |
| [x] | `cmo` | float | Measure directional momentum balance | Chande Momentum Oscillator |
| [x] | `roc_skew` | float | Capture asymmetry of recent returns | Rolling skew of ROC |
| [x] | `roc_kurt` | float | Capture tail risk of recent returns | Rolling kurtosis of ROC |
| [x] | `mb` | float | Provide Bollinger baseline | Middle Bollinger Band = SMA(`FAST_TREND_LOOKBACK`) |
| [x] | `std` | float | Measure rolling close dispersion | Stdev(`FAST_TREND_LOOKBACK`) |
| [x] | `ub` | float | Provide upper volatility envelope | `mb + 2 * std` |
| [x] | `lb` | float | Provide lower volatility envelope | `mb - 2 * std` |

---

## 5. Volume — `volume.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `volume_avg` | float | Establish normal participation baseline | Rolling mean of Volume (`MOMENTUM_LOOKBACK`) |
| [x] | `volume_zscore` | float | Detect abnormal participation | Z-score of Volume (`MOMENTUM_LOOKBACK`) |

---

## 6. Lag Features — `lag.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `open_lag1` | float | Provide previous-bar open context | Open phiên trước |
| [x] | `high_lag1` | float | Provide previous-bar high context | High phiên trước |
| [x] | `low_lag1` | float | Provide previous-bar low context | Low phiên trước |
| [x] | `close_lag1` | float | Provide previous-bar close context | Close phiên trước |
| [x] | `volume_lag1` | float | Provide previous-bar participation context | Volume phiên trước |
| [x] | `body_lag1` | float | Compare current candle body with prior body | Body phiên trước |
| [x] | `upwick_lag1` | float | Compare current upper wick with prior wick | Upper wick phiên trước |
| [x] | `lowwick_lag1` | float | Compare current lower wick with prior wick | Lower wick phiên trước |
| [x] | `ema_fast_lag1` | float | Provide prior fast trend state | EMA fast phiên trước |
| [x] | `ema_slow_lag1` | float | Provide prior slow trend state | EMA slow phiên trước |
| [x] | `ibs_lag1` | float | Provide prior close-location state | IBS phiên trước |
| [x] | `rsi_lag1` | float | Provide prior momentum state | RSI phiên trước |

---

## 7. Mixed / Advanced Indicators — `mix.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `ibs_n` | float | Smooth close-location signal over a lookback window | IBS over `IBS_LOOKBACK` bars: `(Close - lowest(n)) / (highest(n) - lowest(n))` |
| [x] | `is_fvg` | bool | Flag potential price imbalance zones | Fair Value Gap: `high_lag2 < Low` or `low_lag2 > High` |
| [x] | `ulti_osci` | float | Blend momentum across multiple horizons | Ultimate Oscillator (`VOLATILITY_LOOKBACK`) |
| [x] | `vwap` | float | Track volume-weighted fair price | Volume Weighted Average Price |
| [x] | `atr` | float | Measure current volatility regime | Average True Range (`VOLATILITY_LOOKBACK`) |
| [x] | `adx` | float | Measure trend strength independent of direction | Average Directional Index (`VOLATILITY_LOOKBACK`) |
| [x] | `dm` | float | Measure midpoint displacement | Distance Moved = midpoint − midpoint_prev |
| [x] | `eom` | float | Relate price movement ease to volume-range density | Ease of Movement = `dm / vbr` |
| [x] | `direction` | int | Encode candle direction numerically | `1` (bullish) \| `-1` (bearish) |
| [x] | `streak` | int | Capture persistence of same-direction candles | Số nến liên tiếp cùng chiều (có dấu) |
| [x] | `custom_001` | float | Measure distance from previous daily close in percent | `100 * (Close - prev_day_close) / prev_day_close` |
| [x] | `custom_002` | float | Normalize daily momentum by recent range | `(Close - Close_n) / (highest_n - lowest_n)` với n = `ONE_DAY_BARS` |

---

## 8. Group / Pattern Features — `group.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `volume_group` | string | Bucket whether volume is increasing or decreasing | `VolUp` \| `VolDown` |
| [x] | `upper_wick_group` | string | Bucket upper wick expansion or contraction | `Longer` \| `Shorter` |
| [x] | `lower_wick_group` | string | Bucket lower wick expansion or contraction | `Longer` \| `Shorter` |
| [x] | `vol_high_pattern` | string | Combine volume direction with high movement | `VolUp_HighUp` \| `VolUp_HighDown` \| `VolDown_HighUp` \| `VolDown_HighDown` |
| [x] | `ibs_volume_pattern` | string | Combine participation with close-location movement | `VolUp_IBSUp` \| `VolUp_IBSDown` \| `VolDown_IBSUp` \| `VolDown_IBSDown` |
| [x] | `volume_avg_group` | string | Bucket volume relative to its rolling baseline | `VolAboveAvg` \| `VolBelowAvg` |
| [x] | `high_rsi_pattern` | string | Combine price extension with momentum movement | `HighUp_RSIUp` \| `HighUp_RSIDown` \| `HighDown_RSIUp` \| `HighDown_RSIDown` |
| [x] | `high_ub_pattern` | string | Flag high relative to upper Bollinger envelope | `HighAboveUB` \| `HighBelowUB` |
| [x] | `low_lb_pattern` | string | Flag low relative to lower Bollinger envelope | `LowBelowLB` \| `LowAboveLB` |

---

## 9. Signals — `signal.py`

| Status | Column | Type | Goal | Description |
|---|---|---|---|---|
| [x] | `couple_cs_signal` | string | Detect two-candle directional reversal or continuation patterns | Cặp nến: `None` \| `Bullish` \| `Bearish` |
| [x] | `ema_cross_signal` | string | Detect trend crossover events | EMA cross (`ema_fast` vs `ema_slow`): `None` \| `Bullish` \| `Bearish` |
