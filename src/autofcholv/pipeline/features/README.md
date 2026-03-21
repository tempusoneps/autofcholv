# 📊 Features Catalog

Each module produces a set of columns documented in its corresponding `.json` file.
The pipeline executes in the order listed below.

---

## 1. Time — `time.py`

| Column | Type | Description |
|---|---|---|
| `hour` | int | Giờ giao dịch |
| `minute` | int | Phút giao dịch |
| `time_int` | int | `100 * hour + minute` |
| `session_progress` | float | Vị trí trong phiên |
| `day_of_week` | int | Ngày trong tuần |
| `day_of_month` | int | Ngày trong tháng |
| `month` | int | Tháng |
| `year` | int | Năm |

---

## 2. Daily Resample — `resample.py`

| Column | Type | Description |
|---|---|---|
| `day_open` | float | Giá mở cửa trong ngày |
| `day_high` | float | Giá cao nhất trong ngày |
| `day_low` | float | Giá thấp nhất trong ngày |
| `day_close` | float | Giá đóng cửa trong ngày |
| `day_volume` | float | Tổng khối lượng trong ngày |
| `day_pivot` | float | `(High + Low + Close) / 3` |
| `prev_day_open` | float | `day_open.shift(1)` |
| `prev_day_high` | float | `day_high.shift(1)` |
| `prev_day_low` | float | `day_low.shift(1)` |
| `prev_day_close` | float | `day_close.shift(1)` |
| `prev_day_volume` | float | `day_volume.shift(1)` |
| `prev_day_pivot` | float | `day_pivot.shift(1)` |

---

## 3. Candlestick Geometry — `candlestick.py`

| Column | Type | Description |
|---|---|---|
| `body` | float | `Close - Open` (âm = nến đỏ) |
| `height` | float | `High - Low` |
| `upwick` | float | `High - max(Open, Close)` |
| `lowwick` | float | `min(Open, Close) - Low` |
| `upwick_rate` | float | `upwick / height` |
| `lowwick_rate` | float | `lowwick / height` |
| `body_rate` | float | `body / height` |
| `clv` | float | Close Location Value |
| `cbr` | float | `abs(Close - Open) / height` |
| `vbr` | float | `Volume / (High - Low)` |
| `ibs` | float | `(Close - Low) / (High - Low)` |
| `color` | str | `green` \| `red` \| `doji` |
| `wick_imbalance` | float | `upwick - lowwick` |
| `upwick_ratio` | float | `upwick / (lowwick + ε)` |

---

## 4. Close Price Indicators — `close.py`

| Column | Type | Description |
|---|---|---|
| `ema_fast` | float | EMA(`FAST_TREND_LOOKBACK`) |
| `ema_slow` | float | EMA(`LOW_TREND_LOOKBACK`) |
| `rsi` | float | RSI(`MOMENTUM_LOOKBACK`) |
| `rsi_slope` | float | `rsi.diff()` |
| `tsi` | float | True Strength Index |
| `roc_close` | float | Rate of Change (length=1) |
| `close_zscore` | float | Z-score of Close (`MOMENTUM_LOOKBACK`) |
| `efficiency_ratio` | float | Kaufman Efficiency Ratio |
| `macd` | float | MACD (12, 26, 9) |
| `macd_signal` | float | MACD Signal |
| `macd_hist` | float | MACD Histogram |
| `ppo` | float | PPO (12, 26, 9) |
| `ppo_signal` | float | PPO Signal |
| `ppo_hist` | float | PPO Histogram |
| `ulcer_index` | float | Ulcer Index (`MOMENTUM_LOOKBACK`) |
| `cmo` | float | Chande Momentum Oscillator |
| `roc_skew` | float | Rolling skew of ROC |
| `roc_kurt` | float | Rolling kurtosis of ROC |
| `mb` | float | Middle Bollinger Band = SMA(`FAST_TREND_LOOKBACK`) |
| `std` | float | Stdev(`FAST_TREND_LOOKBACK`) |
| `ub` | float | `mb + 2 * std` |
| `lb` | float | `mb - 2 * std` |

---

## 5. Volume — `volume.py`

| Column | Type | Description |
|---|---|---|
| `volume_avg` | float | Rolling mean of Volume (`MOMENTUM_LOOKBACK`) |
| `volume_zscore` | float | Z-score of Volume (`MOMENTUM_LOOKBACK`) |

---

## 6. Lag Features — `lag.py`

| Column | Type | Description |
|---|---|---|
| `open_lag1` | float | Open phiên trước |
| `high_lag1` | float | High phiên trước |
| `low_lag1` | float | Low phiên trước |
| `close_lag1` | float | Close phiên trước |
| `volume_lag1` | float | Volume phiên trước |
| `body_lag1` | float | Body phiên trước |
| `upper_wick_lag1` | float | Upper wick phiên trước |
| `lower_wick_lag1` | float | Lower wick phiên trước |
| `ema20_lag1` | float | EMA20 phiên trước |
| `ibs_lag1` | float | IBS phiên trước |
| `rsi_lag1` | float | RSI phiên trước |

---

## 7. Mixed / Advanced Indicators — `mix.py`

| Column | Type | Description |
|---|---|---|
| `ibs_n` | float | IBS over `IBS_LOOKBACK` bars: `(Close - lowest(n)) / (highest(n) - lowest(n))` |
| `is_fvg` | bool | Fair Value Gap: `high_lag2 < Low` or `low_lag2 > High` |
| `ulti_osci` | float | Ultimate Oscillator (`VOLATILITY_LOOKBACK`) |
| `vwap` | float | Volume Weighted Average Price |
| `atr` | float | Average True Range (`VOLATILITY_LOOKBACK`) |
| `adx` | float | Average Directional Index (`VOLATILITY_LOOKBACK`) |
| `dm` | float | Distance Moved = midpoint − midpoint_prev |
| `eom` | float | Ease of Movement = `dm / vbr` |
| `direction` | int | `1` (bullish) \| `-1` (bearish) |
| `streak` | int | Số nến liên tiếp cùng chiều (có dấu) |
| `custom_001` | float | `100 * (Close - prev_day_close) / prev_day_close` |
| `custom_002` | float | `(Close - Close_n) / (highest_n - lowest_n)` với n = `ONE_DAY_BARS` |

---

## 8. Group / Pattern Features — `group.py`

| Column | Type | Description |
|---|---|---|
| `volume_group` | string | `VolUp` \| `VolDown` |
| `upper_wick_group` | string | `Longer` \| `Shorter` |
| `lower_wick_group` | string | `Longer` \| `Shorter` |
| `vol_high_pattern` | string | `VolUp_HighUp` \| `VolUp_HighDown` \| `VolDown_HighUp` \| `VolDown_HighDown` |
| `ibs_volume_pattern` | string | `VolUp_IBSUp` \| `VolUp_IBSDown` \| `VolDown_IBSUp` \| `VolDown_IBSDown` |
| `volume_avg_group` | string | `VolAboveAvg` \| `VolBelowAvg` |
| `high_rsi_pattern` | string | `HighUp_RSIUp` \| `HighUp_RSIDown` \| `HighDown_RSIUp` \| `HighDown_RSIDown` |
| `high_ub_pattern` | string | `HighAboveUB` \| `HighBelowUB` |
| `low_lb_pattern` | string | `LowBelowLB` \| `LowAboveLB` |

---

## 9. Signals — `signal.py`

| Column | Type | Description |
|---|---|---|
| `couple_cs_signal` | string | Cặp nến: `None` \| `Bullish` \| `Bearish` |
| `ema_cross_signal` | string | EMA cross (`ema_fast` vs `ema_slow`): `None` \| `Bullish` \| `Bearish` |
