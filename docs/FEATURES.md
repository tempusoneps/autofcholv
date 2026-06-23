# 📊 Features Catalog

Each module produces a set of columns documented in its corresponding `.json` file.
The pipeline executes in the order listed below.

---

## 1. Time — `time.py`

| Column | Type | Description |
|---|---|---|
| `hour` | int | Giờ giao dịch |
| `minute` | int | Phút giao dịch |
| `time_int` | int | Time Int = 100 * hour + minute |
| `session_progress` | float | Vị trí trong phiên |
| `day_of_week` | int | Ngày trong tuần |
| `day_of_month` | int | Ngày trong tháng |
| `month` | int | Tháng |
| `year` | int | Năm |

---

## 2. Daily Resample — `resample.py`

| Column | Type | Description |
|---|---|---|
| `prev_day_close` | float | day_close.shift(1) |
| `prev_day_open` | float | day_open.shift(1) |
| `prev_day_high` | float | day_high.shift(1) |
| `prev_day_low` | float | day_low.shift(1) |
| `prev_day_volume` | float | day_volume.shift(1) |
| `prev_day_pivot` | float | day_pivot.shift(1) |

---

## 3. Candlestick Geometry — `candlestick.py`

| Column | Type | Description |
|---|---|---|
| `body` | float | candlestick body length (include both negative & positive values) |
| `height` | float | candlestick height = high - low |
| `upwick` | float | candlestick upper wick length = high - max(open, close) |
| `lowwick` | float | candlestick lower wick length = min(open, close) - low |
| `upwick_rate` | float | upper wick rate = upper wick / height |
| `lowwick_rate` | float | lower wick rate = lower wick / height |
| `body_rate` | float | body rate = body / height |
| `clv` | float | clv = 1 if High = Low else ((Close-Low) - (High-Close)) / (High - Low) |
| `cbr` | float | cbr = abs(close - open) / height |
| `vbr` | float | vbr = Volume / (High - Low) |
| `ibs` | float | ibs = (close - low) / (high - low) |
| `color` | str | color |
| `wick_imbalance` | float | wick imbalance = upper wick - lower wick |
| `upwick_ratio` | float | upwick_ratio = upwick / (lowwick + epsilon) |

---

## 4. Close Price Indicators — `close.py`

| Column | Type | Description |
|---|---|---|
| `ema_fast` | float | EMA fast = ta.ema(close, length=n) with n = FAST_TREND_LOOKBACK |
| `ema_slow` | float | EMA slow = ta.ema(close, length=n) with n = SLOW_TREND_LOOKBACK |
| `rsi` | float | RSI = ta.rsi(close, length=n) with n = MOMENTUM_LOOKBACK |
| `rsi_slope` | float | df['rsi'].diff() |
| `tsi` | float | TSI = ta.tsi(close, length=n) with n = MOMENTUM_LOOKBACK |
| `roc_close` | float | ROC = ta.roc(close, length=1) |
| `close_zscore` | float | Z-score of Close = ta.zscore(close, length=n) with n = MOMENTUM_LOOKBACK |
| `efficiency_ratio` | float | ER = change / volatility; change = abs(close - close.shift(n)); volatility = sum(abs(close - close.shift(1))) over n periods; with n = MOMENTUM_LOOKBACK |
| `macd` | float | MACD = ta.macd(close, fast=12, slow=26, signal=9) |
| `macd_signal` | float | MACD Signal = ta.macd(close, fast=12, slow=26, signal=9) |
| `macd_hist` | float | MACD Hist = ta.macd(close, fast=12, slow=26, signal=9) |
| `ppo` | float | PPO = ta.ppo(close, fast=12, slow=26, signal=9) |
| `ppo_signal` | float | PPO Signal = ta.ppo(close, fast=12, slow=26, signal=9) |
| `ppo_hist` | float | PPO Hist = ta.ppo(close, fast=12, slow=26, signal=9) |
| `ulcer_index` | float | Ulcer Index = ta.ui(close, length=n) with n = MOMENTUM_LOOKBACK |
| `cmo` | float | CMO = ta.cmo(close, length=n) with n = MOMENTUM_LOOKBACK |
| `roc_skew` | float | df['roc_close'].rolling(n).skew() with n = MOMENTUM_LOOKBACK |
| `roc_kurt` | float | df['roc_close'].rolling(n).kurt() with n = MOMENTUM_LOOKBACK |
| `mb` | float | Middle Bollinger Band = ta.sma(close, length=n) with n = TREND_LOOKBACK |
| `std` | float | Standard Deviation = ta.stdev(close, length=n) with n = TREND_LOOKBACK |
| `ub` | float | Upper Bollinger Band = ta.sma(close, length=n) + 2 * ta.stdev(close, length=n) with n = TREND_LOOKBACK |
| `lb` | float | Lower Bollinger Band = ta.sma(close, length=n) - 2 * ta.stdev(close, length=n) with n = TREND_LOOKBACK |
| `cci` | float | CCI = (typical_price - rolling mean typical_price) / (0.015 * mean absolute deviation) |
| `kdj_k` | float | Smoothed stochastic RSV over MOMENTUM_LOOKBACK adapted from quant-ohlcv-feature |
| `kdj_d` | float | Smoothed KDJ K line |
| `kdj_j` | float | kdj_j = 3 * kdj_k - 2 * kdj_d |
| `fisher` | float | Fisher transform of median price position within the rolling high-low range |
| `kama` | float | Adaptive moving average weighted by efficiency ratio |
| `kama_bias` | float | kama_bias = Close / kama - 1 |
| `high_ma_bias` | float | (High - rolling mean High) / rolling mean High with n = FAST_TREND_LOOKBACK |
| `bollinger_width` | float | (ub - lb) / mb |
| `bollinger_percent_b` | float | (Close - lb) / (ub - lb) |
| `change_std` | float | Close.pct_change(n) * rolling std of one-bar returns adapted from quant-ohlcv-feature |
| `dpo` | float | (Close - shifted rolling mean Close) / rolling mean Close |
| `pfe` | float | Direction-signed price efficiency based on direct distance divided by path distance |
| `williams_r` | float | (rolling high - Close) / (rolling high - rolling low) * 100 |
| `slow_stoch_d` | float | Slow stochastic oscillator D line adapted from SKDJ |
| `coppock` | float | Rolling mean of combined n-period and 2n-period close ROC |
| `pmo` | float | Double-smoothed close ROC momentum oscillator |
| `smi` | float | Smoothed close distance from rolling high-low midpoint |
| `psy` | float | Percent of bars in lookback where Close rose |
| `return_autocorr` | float | Rolling correlation of one-bar returns with lagged returns |
| `demarker` | float | Rolling positive high movement divided by positive high plus low movement |
| `imi` | float | Rolling close-open up movement divided by total close-open movement |
| `rvi` | float | Upward close volatility divided by upward plus downward close volatility |
| `bop` | float | Rolling mean of (Close - Open) / (High - Low) |
| `ultimate_oscillator_src` | float | Triple-timeframe buying pressure oscillator adapted from quant-ohlcv-feature |
| `kst` | float | Weighted multi-horizon close ROC oscillator normalized by its rolling mean |
| `rmi` | float | Four-bar positive close momentum divided by rolling absolute close movement |
| `tii` | float | Normalized ratio of positive close deviations from rolling mean |
| `ar` | float | 100 * rolling sum(High - Open) / rolling sum(Open - Low) |
| `br` | float | 100 * rolling sum(High - previous Close) / rolling sum(previous Close - Low) |
| `cr` | float | 100 * rolling upward pressure over previous typical price divided by downward pressure |
| `adtm` | float | (rolling DTM - rolling DBM) / max(rolling DTM, rolling DBM) |
| `qstick` | float | (Close - Open) normalized by rolling mean Close - Open |
| `mtm` | float | (Close / Close.shift(n) - 1) * 100 |
| `bias` | float | Close / rolling mean Close - 1 |
| `rbias` | float | One-bar rate of change of Close / rolling mean Close |
| `mtm_mean` | float | Rolling mean of n-period close momentum |
| `mtm_max_diff` | float | Current n-period momentum minus prior rolling max momentum |
| `sroc` | float | Rate of change of EMA-smoothed Close over 2n bars |
| `rsi_mean` | float | Rolling mean of RSI scaled to 0-1, adapted from quant-ohlcv Rsimean |
| `tdi` | float | Rolling-normalized spread between RSI price and signal lines |
| `osc` | float | Rolling mean of close minus its 2n-period moving average |
| `short_quiet_momentum` | float | Sum of n-period returns from the lowest-amplitude 70 percent of bars in the short window |
| `long_quiet_momentum` | float | Sum of n-period returns from the lowest-amplitude 70 percent of bars in a 10n window |
| `price_volume_momentum` | float | EMA-smoothed price momentum multiplied by EMA-smoothed quote-volume momentum |
| `dbcd` | float | Rolling average of close moving-average bias divergence |
| `pmarp` | float | Percentile rank of absolute close-to-moving-average ratio |
| `pos` | float | Position of current n-period return within its rolling min-max range |
| `bias36` | float | Rolling-normalized difference between 3-bar and 6-bar moving-average spread and its mean |
| `swing_index` | float | Weighted price movement index adapted from quant-ohlcv Si |

---

## 5. Price Derived Indicators — `price.py`

| Column | Type | Description |
|---|---|---|
| `typical_price` | float | typical_price = (High + Low + Close) / 3 |
| `weighted_close` | float | weighted_close = (High + Low + 2 * Close) / 4 |
| `typical_price_momentum` | float | Z-scored spread between fast EMA and slow EMA of typical_price |
| `weighted_close_bias` | float | weighted_close EMA(n) / weighted_close EMA(2n) - 1 with n = MOMENTUM_LOOKBACK |
| `rolling_vwap` | float | rolling_vwap = rolling sum(typical_price * Volume) / rolling sum(Volume) |
| `vwap_bias` | float | rolling_vwap / rolling mean(rolling_vwap, n) - 1 with n = MOMENTUM_LOOKBACK |
| `close_to_vwap` | float | close_to_vwap = Close / rolling_vwap - 1 |
| `vwap_range_position` | float | Rolling VWAP normalized within its rolling min/max range |
| `vwap_to_high` | float | rolling_vwap / High - 1 |
| `vwap_to_low` | float | rolling_vwap / Low - 1 |
| `close_ma_price` | float | Rolling mean Close over MOMENTUM_LOOKBACK |
| `typical_to_vwap` | float | typical_price / rolling_vwap - 1 |

---

## 6. Trend Indicators — `trend.py`

| Column | Type | Description |
|---|---|---|
| `dema_bias` | float | Double EMA normalized by single EMA minus 1 |
| `tema_bias` | float | EMA divided by triple EMA minus 1 |
| `trix` | float | One-bar percent change of triple-smoothed EMA |
| `aroon_up` | float | Relative recency of rolling high on a 0-100 scale |
| `aroon_down` | float | Relative recency of rolling low on a 0-100 scale |
| `aroon_osc` | float | aroon_up - aroon_down |
| `vortex_plus` | float | Rolling positive vortex movement divided by rolling true range |
| `vortex_minus` | float | Rolling negative vortex movement divided by rolling true range |
| `vortex_diff` | float | vortex_plus - vortex_minus |
| `regression_bias` | float | Close / rolling linear-regression estimate - 1 |
| `regression_slope` | float | Rolling linear-regression slope normalized by rolling mean close |
| `hullma_bias` | float | Low-lag Hull-style EMA component divided by its sqrt-window EMA smoother minus 1 |
| `ichimoku_cloud_ratio` | float | Ichimoku span A divided by span B using trend lookback multiples |
| `t3_bias` | float | Close / Tillson T3 moving average - 1 |
| `ma_signal` | float | Rolling-normalized close minus moving average trend signal |
| `bbi_ratio` | float | Bull and Bear Index moving-average blend divided by close |
| `bbi_bias` | float | Close divided by Bull and Bear Index minus 1 |
| `adxr_diff` | float | Lag-smoothed DI+ minus DI- directional trend spread |
| `wma_ma_gap` | float | Weighted MA minus simple MA normalized by rolling absolute gap |

---

## 7. Volatility Indicators — `volatility.py`

| Column | Type | Description |
|---|---|---|
| `quote_volume_std` | float | Rolling standard deviation of Close * Volume proxy |
| `amplitude_max` | float | Rolling max of max(\|High/Open - 1\|, \|Low/Open - 1\|) |
| `positive_amplitude_rank` | float | Rolling percentile rank of positive-price-change amplitude mean |
| `apz_width` | float | Double EMA high-low volatility divided by double EMA close |
| `pac_width_bias` | float | PAC width divided by rolling mean PAC width minus 1 |
| `pac_position` | float | (Close - PAC lower) / PAC width |
| `env_position` | float | Close position inside +/-5 percent moving-average envelope |
| `realized_volatility` | float | Rolling standard deviation of one-bar returns |
| `realized_volatility_zscore` | float | Z-score of realized_volatility over VOLATILITY_LOOKBACK |
| `rwi` | float | Close normalized within upward/downward Random Walk Index range |
| `mssi` | float | Max of average drawdown from rolling high and reverse drawdown from rolling low |
| `vix_bw` | float | Signed adaptive bandwidth of n-period close return |
| `adaptive_bollinger_width` | float | Adaptive z-score Bollinger bandwidth normalized by close moving average |
| `vwap_bbw_efficiency` | float | Rolling VWAP change times Bollinger-width change normalized by quote-volume proxy |
| `chaikin_volatility` | float | Rate of change of EMA high-low range |
| `keltner_width` | float | Keltner channel width normalized by EMA middle band |
| `keltner_upper_signal` | float | Rolling-normalized Keltner upper band |
| `keltner_lower_signal` | float | Rolling-normalized Keltner lower band |
| `env_upper_signal` | float | Rolling-normalized 5 percent envelope upper band |
| `env_lower_signal` | float | Rolling-normalized 5 percent envelope lower band |
| `fibonacci_band_width` | float | Fibonacci ATR channel width normalized by rolling close mean |
| `fibonacci_band_position` | float | Close position inside first Fibonacci ATR channel |
| `donchian_mid_signal` | float | Close minus Donchian channel midpoint |

---

## 8. Volume — `volume.py`

| Column | Type | Description |
|---|---|---|
| `volume_avg` | float | Trung bình khối lượng n phiên |
| `volume_zscore` | float | Z-score khối lượng |
| `pvt` | float | pvt = Close.pct_change() * Volume |
| `pvt_signal` | float | Rolling normalized PVT signal adapted from quant-ohlcv-feature |
| `volume_up_ratio` | float | Rolling share of volume on bars where Close rises |
| `volume_down_ratio` | float | Rolling share of volume on bars where Close falls |
| `money_flow_index` | float | Volume-weighted positive and negative money flow oscillator |
| `pvi` | float | Cumulative close return on bars where Volume rises |
| `nvi` | float | Cumulative close return on bars where Volume falls |
| `clv_ma` | float | Rolling mean of (2 * Close - Low - High) / (High - Low) |
| `wad` | float | Cumulative Williams AD normalized by its rolling mean |
| `tmf` | float | EMA of true-range volume flow divided by EMA volume |
| `obv_clv` | float | Rolling CLV-weighted volume normalized by its rolling mean |
| `cmf` | float | Rolling CLV-weighted volume divided by rolling volume |
| `emv` | float | Midpoint move divided by volume density per price range |
| `force_index` | float | EMA-smoothed z-score of Volume * Close.diff() |
| `pvo` | float | (EMA(Volume,n) - EMA(Volume,2n)) / EMA(Volume,2n) |
| `directional_volume_change` | float | Rolling maximum of quote-volume proxy change signed by close direction |
| `quote_volume_reg` | float | Rolling linear-regression fitted value of Close * Volume proxy |
| `quote_volume_tsf` | float | One-step rolling linear-regression forecast of Close * Volume proxy |
| `price_volume_corr` | float | Rolling correlation between Close and Close * Volume proxy |
| `quote_volume_sum` | float | Rolling sum of Close * Volume quote-volume proxy |
| `volume_bias_short_long` | float | Short-window quote-volume proxy mean divided by long-window mean minus 1 |
| `volume_ratio_amount` | float | (up amount + flat amount / 2) / (down amount + flat amount / 2) |
| `adosc` | float | Normalized EMA spread of cumulative CLV-weighted volume |
| `wvad` | float | Normalized rolling sum of body-weighted volume |
| `klinger_oscillator` | float | Normalized EMA spread of signed volume by typical price direction |
| `vra` | float | Dual-horizon price ROC multiplied by rolling close volatility |
| `ke` | float | Signed squared n-period price change amplified by normalized volume |
| `roc_volume` | float | Volume / Volume.shift(n) - 1 |
| `volume_ma_bias` | float | Volume divided by its moving average minus 1 |
| `amv_signal` | float | Rolling-normalized volume-weighted average of open-close midpoint |
| `volume_ratio` | float | Up-volume plus half neutral volume divided by down-volume plus half neutral volume |
| `macd_volume_ratio` | float | Volume MACD divided by its rolling signal minus 1 |
| `volume_analysis_oscillator` | float | Short minus long average of volume weighted by close position versus candle midpoint |

---

## 9. Liquidity / Composite Proxies — `liquidity.py`

| Column | Type | Description |
|---|---|---|
| `market_placement` | float | Close relative to EMA quote-volume/volume holding-cost proxy |
| `path_liquidity` | float | Rolling quote-volume proxy per normalized shortest intrabar price path |
| `spread_proxy` | float | Rolling mean log high-low range as an OHLC bid-ask spread proxy |
| `spread_volatility_ratio` | float | spread_proxy divided by rolling close-return volatility |
| `price_volume_resistance` | float | Price move magnitude per volume move magnitude adapted from PriceVolumeResist |
| `coppock_atr_volume` | float | Coppock momentum multiplied by normalized ATR and volume pressure |

---

## 10. Lag Features — `lag.py`

| Column | Type | Description |
|---|---|---|
| `open_lag1` | float | Open phiên trước |
| `high_lag1` | float | High phiên trước |
| `low_lag1` | float | Low phiên trước |
| `close_lag1` | float | Close phiên trước |
| `volume_lag1` | float | Volume phiên trước |
| `body_lag1` | float | Body phiên trước |
| `upwick_lag1` | numerical |  |
| `lowwick_lag1` | numerical |  |
| `prev_ema_fast` | numerical |  |
| `prev_ema_slow` | numerical |  |
| `ibs_lag1` | numerical |  |
| `rsi_lag1` | numerical |  |

---

## 11. Mixed / Advanced Indicators — `mix.py`

| Column | Type | Description |
|---|---|---|
| `ibs_n` | float | ibs_n = (close - lowest(n)) / (highest(n) - lowest(n)) with n = IBS_LOOKBACK |
| `is_fvg` | bool | is_fvg = True if (high_prev > low_curr) or (low_prev < high_curr) else False |
| `ulti_osci` | float | Ultimate Oscillator = ta.ultimate_oscillator(high, low, close, length=n) with n = VOLATILITY_LOOKBACK |
| `vwap` | float | vwap = ta.vwap(high, low, close, volume) |
| `atr` | float | atr = ta.atr(high, low, close, length=n) with n = VOLATILITY_LOOKBACK |
| `atr_pct` | float | atr_pct = atr / Close |
| `adx` | float | adx = ta.adx(high, low, close, length=n) with n = ADX_VOLATILITY_LOOKBACKLOOKBACK |
| `dm` | float | dm = (High + Low) / 2 - (high_lag1 + low_lag1) / 2 |
| `eom` | float | eom = dm / vbr |
| `direction` | int | direction = 1 if close > open else -1 |
| `streak` | int | up_streak = 0 if direction != direction_lag1 else direction + up_streak_lag1 |
| `custom_001` | float | 100 * (Close - prev_day_close) / prev_day_close |
| `custom_002` | float | (Close - close.shift(n)) / (High.rolling(n).max() - Low.rolling(n).min()) with n = ONE_DAY_BARS |
| `donchian_width` | float | (rolling max High - rolling min Low) / channel midpoint with n = VOLATILITY_LOOKBACK |
| `donchian_position` | float | (Close - rolling min Low) / (rolling max High - rolling min Low) with n = VOLATILITY_LOOKBACK |
| `amihud_liquidity` | float | Rolling quote-volume proxy per normalized intraday shortest path adapted from quant-ohlcv-feature |
| `keltner_position` | float | (Close - EMA(Close,n) + 2 * ATR) / (4 * ATR) adapted from quant-ohlcv-feature |
| `true_range_pct` | float | True range divided by Close |
| `gap_pct` | float | (Open - previous Close) / previous Close |
| `range_position` | float | (Close - Low) / (High - Low) |
| `body_to_true_range` | float | Absolute candlestick body divided by true range |

---

## 12. Group / Pattern Features — `group.py`

| Column | Type | Description |
|---|---|---|
| `volume_group` | string | volume_group = comapre(Volume, vol_lag1) = VolUp \| Voldown |
| `upper_wick_group` | string | upper_wick_group = compare(upper_wick, prev_upper_wick) = Longer \| Shorter |
| `lower_wick_group` | string | lower_wick_group = compare(lower_wick, prev_lower_wick) = Longer \| Shorter |
| `vol_high_pattern` | string | vol_high_pattern = compare(Volume, vol_lag1) + compare(High, high_lag1) = VolUp_HighUp \| VolUp_HighDown \| VolDown_HighUp \| VolDown_HighDown |
| `ibs_volume_pattern` | string | ibs_volume_group = compare(Volume, vol_lag1) + compare(IBS, ibs_lag1) = VolUp_IBSUp \| VolUp_IBSDown \| VolDown_IBSUp \| VolDown_IBSDown |
| `volume_avg_group` | string | volume_avg_group = comapre(Volume, vol_avg) = VolAboveAvg \| VolBelowAvg |
| `high_rsi_pattern` | string | high_rsi_pattern = compare(High, high_lag1) + compare(RSI, rsi_lag1) = HighUp_RSIUp \| HighUp_RSIDown \| HighDown_RSIUp \| HighDown_RSIDown |
| `high_ub_pattern` | string | high_ub_pattern = compare(High, ub) = HighAboveUB \| HighBelowUB |
| `low_lb_pattern` | string | low_lb_pattern = compare(Low, lb) = LowAboveLB \| LowBelowLB |
| `long_trend` | string | StrongUp \| StrongDown = EMA_1month > EMA_6months \| EMA_1month < EMA_6months |
| `body_size_group` | string | body_size_group = compare(abs(Close-Open), prev_abs_body) = Expanding \| Contracting |
| `candle_color_sequence` | string | sequence = current_color + prev_color = Bull_Bull \| Bull_Bear \| Bear_Bull \| Bear_Bear |
| `gap_pattern` | string | gap_pattern = compare(Open, prev_Close) = GapUp \| GapDown \| Flat |
| `atr_regime` | string | atr_regime = compare(ATR, ATR_avg) = HighVol \| LowVol |
| `bb_width_group` | string | bb_width_group = compare(BB_Width, prev_BB_Width) = Expanding \| Squeezing |
| `range_position` | string | range_pos = (Close - Low) / (High - Low) = Top_Third \| Mid_Third \| Bottom_Third |
| `ma_cross_pattern` | string | ma_cross = compare(Close, EMA_20) = PriceAboveMA \| PriceBelowMA |
| `distance_from_ma` | string | dist_ma = (Close - EMA_20) / ATR = Overextended_Up \| Neutral \| Overextended_Down |
| `rsi_extreme_group` | string | rsi_group = RSI > 70 ? Overbought : (RSI < 30 ? Oversold : Neutral) |
| `volume_price_divergence` | string | vol_price = compare(Vol, vol_lag1) + compare(Abs_Return, abs_ret_lag1) = Effort_Confirmed \| Effort_Divergence |
| `obv_trend` | string | obv_trend = compare(OBV, OBV_lag1) = Accumulation \| Distribution |
| `effort_result_pattern` | string | effort_result = compare(Volume, vol_lag1) + compare(abs(Close-Open), abs_body_lag1) = HighEffort_LowResult \| HighEffort_HighResult \| LowEffort_HighResult \| LowEffort_LowResult |
| `spread_group` | string | spread_group = compare(High-Low, avg_range_20) = WideSpread \| NarrowSpread |
| `stopping_volume_pattern` | string | stopping_vol = (Volume > vol_avg_20) + (ibs > 0.8 \| ibs < 0.2) = Potential_Climax \| Normal_Flow |
| `ma_distance_group` | string | ma_dist = (Close - EMA20) / ATR = Extreme_Upper \| Above_Mean \| Below_Mean \| Extreme_Lower |
| `bollinger_bandwidth_regime` | string | bb_regime = compare(bb_width, bb_width_avg_100) = High_Vol_Expansion \| Low_Vol_Squeeze |
| `consecutive_days_group` | string | consecutive_group = count_consecutive(Close > Open) = 3_Up_Days \| 3_Down_Days \| Mixed |
| `rsi_velocity_pattern` | string | rsi_velocity = compare(RSI, rsi_lag1) + compare(RSI, rsi_lag2) = Accelerating_Up \| Decelerating_Up \| Accelerating_Down \| Decelerating_Down |
| `price_rsi_divergence` | string | div_hint = compare(High, high_lag1) + compare(RSI, rsi_lag1) = Bullish_Confirm \| Bearish_Divergence \| Bearish_Confirm \| Bullish_Divergence |
| `volatility_regime_shift` | string | vol_shift = compare(ATR_short, ATR_long) = Vol_Rising \| Vol_Falling |
| `ma_slope_direction` | string | ma_slope = compare(EMA_20, EMA_20_lag1) = Uptrend \| Downtrend \| Sideways |
| `ma_ribbon_position` | string | ribbon_pos = compare(Close, EMA_50) = Above_Ribbon \| Below_Ribbon |
| `ma_cross_count` | string | cross_count = count_cross(EMA_20, EMA_50) = Frequent_Cross \| Rare_Cross |
| `close_return_group` | string | close_return = compare(Close, close_lag1) = Up \| Down \| Flat |
| `return_magnitude_group` | string | ret_mag = abs(Return) compare ret_avg = LargeMove \| NormalMove \| SmallMove |
| `high_low_expansion` | string | range_expansion = compare(High-Low, prev_range) = Expansion \| Contraction |
| `close_position_vs_prev_range` | string | close_pos_prev = (Close - prev_Low) / (prev_High - prev_Low) = BreakAbove \| Inside \| BreakBelow |
| `open_position_vs_prev_range` | string | open_pos_prev = (Open - prev_Low) / (prev_High - prev_Low) = GapBreakUp \| Inside \| GapBreakDown |
| `wick_to_body_ratio` | string | wick_body = (upper_wick + lower_wick) / body = WickDominant \| Balanced \| BodyDominant |
| `upper_lower_wick_balance` | string | wick_balance = compare(upper_wick, lower_wick) = UpperDominant \| LowerDominant \| Symmetric |
| `volume_spike_pattern` | string | vol_spike = Volume > 2 * vol_avg_20 = Spike \| Normal |
| `price_acceleration` | string | price_acc = compare(Return, return_lag1) = Accelerating \| Decelerating |
| `multi_timeframe_trend_alignment` | string | mtf_trend = EMA_20 > EMA_50 > EMA_200 = StrongBull \| StrongBear \| Mixed |
| `ema_compression_pattern` | string | ema_compress = std(EMA_20, EMA_50, EMA_100) = Tight \| Expanding |
| `price_vs_vwap` | string | price_vwap = compare(Close, VWAP) = AboveVWAP \| BelowVWAP |
| `vwap_deviation_group` | string | vwap_dev = (Close - VWAP) / ATR = Overextended \| Neutral |
| `intraday_trend_pattern` | string | intra_trend = compare(Open, Close) + compare(Close, High/Low) = TrendUp \| TrendDown \| Chop |
| `breakout_strength` | string | breakout = (Close > prev_High) + volume_condition = StrongBreak \| WeakBreak \| NoBreak |
| `false_break_pattern` | string | false_break = (High > prev_High AND Close < prev_High) OR (Low < prev_Low AND Close > prev_Low) = BullTrap \| BearTrap \| None |
| `liquidity_sweep_pattern` | string | liq_sweep = sweep(prev_high/low) + rejection = SweepHighReject \| SweepLowReject \| NoSweep |
| `orderflow_proxy_pattern` | string | orderflow = compare(body_size, wick_size) + volume = AggressiveBuy \| AggressiveSell \| Passive |
| `imbalance_candle_pattern` | string | imbalance = body >> wick AND range_expansion = ImbalanceUp \| ImbalanceDown \| Balanced |
| `mean_reversion_signal` | string | mean_rev = distance_from_ma + rsi_extreme = RevertDown \| RevertUp \| Neutral |
| `trend_exhaustion_pattern` | string | exhaustion = HighUp + RSI_Down OR LowDown + RSI_Up = BullExhaust \| BearExhaust \| None |
| `compression_breakout_setup` | string | compression = BB squeeze + low ATR = ReadyBreakout \| NotReady |
| `volatility_cluster_pattern` | string | vol_cluster = consecutive HighVol OR LowVol = ClusterHigh \| ClusterLow \| Mixed |
| `price_efficiency_ratio` | string | efficiency = abs(Close - Close_n) / sum(abs(return)) = EfficientTrend \| Noisy |
| `swing_structure_pattern` | string | structure = HH_HL \| LH_LL \| Range |
| `micro_trend_pattern` | string | micro_trend = compare(Close, Close_lag3) = MicroUp \| MicroDown \| Flat |
| `range_compression_ratio` | string | range_ratio = (High-Low)/avg_range_10 = Compressed \| Normal \| Expanded |
| `volume_trend_alignment` | string | vol_trend = compare(Volume_trend, Price_trend) = Confirmed \| Diverging |
| `breakout_failure_strength` | string | failure = breakout_attempt + reversal_strength = StrongFailure \| WeakFailure \| None |

---

## 13. Signals — `signal.py`

| Column | Type | Description |
|---|---|---|
| `couple_cs_signal` | string | Signal of couple candlestick pattern (Both Green or Both Red) |
| `ema_cross_signal` | string | Signal of EMA cross pattern (cross up or cross down) |
| `min_max_10_signal` | string | Signal of min max 10 Close (min or max) |
| `macd_histogram_reversal_signal` | string | Tín hiệu sớm về sự suy yếu của lực đẩy |
| `bb_rejection_signal` | string | Signal of BB rejection pattern |
| `bb_squeeze_signal` | string | Tín hiệu dự báo bùng nổ biến động khi giá đi ngang quá lâu |
| `rsi_divergence_signal` | string | Tín hiệu phân kỳ giữa giá và RSI để bắt đỉnh/đáy |
| `atr_breakout_signal` | string | Xác nhận tín hiệu dựa trên độ biến động thực tế |
| `vsa_confirmation_signal` | string | Xác nhận nỗ lực tăng/giảm qua khối lượng giao dịch |
| `ichimoku_cloud_signal` | string | Tín hiệu dựa trên mây Ichimoku |
| `ma_stretch_signal` | string | Đo lường độ căng của giá so với đường trung bình (Z-Score concept) |
| `market_structure_break_signal` | string | Xác định sự thay đổi xu hướng từ Bearish sang Bullish và ngược lại |
| `bollinger_band_width_signal` | string | Đo lường độ biến động (Volatility) của thị trường |
| `volume_confirmation_signal` | boolean | Xác nhận nỗ lực của giá thông qua khối lượng |
| `mfi_rejection_signal` | string | Dòng tiền thông minh vào vùng cực đại |
| `donchian_breakout_signal` | string | Tín hiệu thuận xu hướng dựa trên đỉnh/đáy cao nhất |
| `hma_reversal_signal` | string | Xác định điểm xoay của xu hướng nhanh hơn EMA |
| `adx_trend_filter` | boolean | Chỉ kích hoạt giao dịch khi xu hướng đủ mạnh (> 25) |
| `connors_rsi_signal` | string | Tín hiệu Mean Reversion cực nhanh cho scalping |
| `choppiness_signal` | boolean | Dùng để bật/tắt các signal khác. < 38.2 là có xu hướng, > 61.8 là đi ngang |
| `keltner_channel_reversal` | string | Tín hiệu đảo chiều khi giá chạm biên Keltner |
| `fractal_breakout_signal` | string | Xác định đỉnh/đáy cục bộ để giao dịch breakout |
| `supertrend_reversal` | string | Tín hiệu đảo chiều xu hướng mạnh mẽ |
| `aroon_oscillator_signal` | string | Xác định sức mạnh và hướng của xu hướng |
| `chande_momentum_oscillator_signal` | string | Đo lường động lượng thị trường |
| `ultimate_oscillator_signal` | string | Tín hiệu kết hợp 3 chu kỳ (7, 14, 28) |
| `trix_crossover_signal` | string | Tín hiệu đảo chiều dựa trên TRIX |
| `stochastic_rsi_signal` | string | Đo lường RSI trong vùng quá mua/quá bán |
| `awesome_oscillator_signal` | string | Tín hiệu động lượng dựa trên nến |
| `rate_of_change_signal` | string | Đo lường tốc độ thay đổi giá |
| `price_channel_breakout_signal` | string | Tín hiệu breakout dựa trên kênh giá |
| `linear_regression_slope_signal` | string | Đo lường độ dốc của đường xu hướng |
| `zig_zag_reversal_signal` | string | Xác định đỉnh/đáy cục bộ |
| `kaufman_ama_signal` | string | Đường trung bình thích ứng với biến động |
| `tma_reversal_signal` | string | Tín hiệu đảo chiều dựa trên TMA |
| `linear_regression_channel_signal` | string | Kênh giá dựa trên hồi quy tuyến tính |
| `fractal_channel_signal` | string | Kênh giá dựa trên fractal |
| `hurst_exponent_signal` | boolean | Xác định tính ngẫu nhiên của thị trường |
| `vpt_divergence_signal` | string | Xác định sự phân kỳ của dòng tiền thực |
| `liquidity_sweep_signal` | string | Quét high/low gần nhất và đảo chiều |
| `equal_high_low_sweep_signal` | string | Quét vùng equal highs/lows |
| `inside_bar_breakout_signal` | string | Breakout khỏi inside bar |
| `fakey_pattern_signal` | string | False breakout |
| `pin_bar_signal` | string | Nến rút chân mạnh |
| `engulfing_signal` | string | Bao trùm nến trước |
| `compression_breakout_signal` | string | Nhiều nến nhỏ → breakout |
| `atr_expansion_signal` | string | Volatility breakout |
| `zscore_reversion_signal` | string | Giá lệch khỏi mean |
| `range_breakout_signal` | string | Break range |
| `volume_spike_signal` | string | Volume đột biến |
| `return_momentum_signal` | string | Momentum dựa trên return |
| `volatility_break_signal` | string | Biến động vượt ngưỡng |
| `mean_cross_signal` | string | Giá cắt MA |
| `high_low_break_signal` | string | Phá đỉnh/đáy gần |
| `range_compression_signal` | string | Range co hẹp |
| `gap_up_down_signal` | string | Gap giá |
| `body_size_signal` | string | Thân nến lớn |
| `wick_rejection_signal` | string | Từ chối giá bằng bóng nến |
| `trend_strength_signal` | string | Xu hướng mạnh |
| `pullback_signal` | string | Pullback trong trend |
| `break_retest_signal` | string | Break và retest |
| `momentum_shift_signal` | string | Đổi chiều momentum |
| `range_mid_reversion_signal` | string | Hồi về mid range |
| `volatility_drop_signal` | string | Giảm biến động |
| `price_acceleration_signal` | string | Gia tốc giá |
| `extreme_move_signal` | string | Move lớn bất thường |
| `mean_distance_signal` | string | Khoảng cách tới MA |
| `range_shift_signal` | string | Dịch chuyển range |
| `volume_trend_signal` | string | Xu hướng volume |
| `price_rejection_signal` | string | Từ chối vùng giá |
| `micro_trend_signal` | string | Trend ngắn hạn |
| `micro_reversal_signal` | string | Đảo chiều ngắn hạn |
| `range_expansion_signal` | string | Range tăng |
| `body_direction_signal` | string | Chuỗi nến cùng màu |
| `range_position_signal` | string | Vị trí trong range |
| `close_strength_signal` | string | Đóng cửa gần high/low |
| `trend_exhaustion_signal` | string | Kiệt sức xu hướng |
| `range_flip_signal` | string | Đảo range |
| `vol_price_divergence_signal` | string | Volume không confirm giá |
| `final_push_signal` | string | Đẩy cuối trend |

---
