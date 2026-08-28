# 📊 Features Catalog

Each module produces a set of columns documented in its corresponding `.json` file.
The pipeline executes in the order listed below.

---

## 1. Time — `time.py`

| Column | Type | Description |
|---|---|---|
| `hour` | int | Giờ giao dịch |
| `minute` | int | Phút giao dịch |
| `day_of_month` | int | Ngày trong tháng |
| `month` | int | Tháng |
| `year` | int | Năm |
| `day_of_week` | int | Ngày trong tuần |
| `time_int` | int | Time Int = 100 * hour + minute |
| `session_progress` | float | Vị trí trong phiên |
| `is_morning` | bool | True if timestamp is in morning session (time_int < 1200) |
| `is_afternoon` | bool | True if timestamp is in afternoon session (time_int > 1200) |

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
| `prev_day_r1` | float | Pivot resistance R1 from completed previous trading day |
| `prev_day_s1` | float | Pivot support S1 from completed previous trading day |
| `prev_15m_open` | float | Open price of completed 15-minute bar |
| `prev_15m_high` | float | High price of completed 15-minute bar |
| `prev_15m_low` | float | Low price of completed 15-minute bar |
| `prev_15m_close` | float | Close price of completed 15-minute bar |
| `prev_15m_volume` | float | Volume of completed 15-minute bar |
| `prev_15m_pivot` | float | Pivot point of completed 15-minute bar |
| `prev_15m_r1` | float | Pivot resistance R1 of completed 15-minute bar |
| `prev_15m_s1` | float | Pivot support S1 of completed 15-minute bar |
| `prev_15m_return` | float | Return ratio of completed 15-minute bar |
| `prev_30m_open` | float | Open price of completed 30-minute bar |
| `prev_30m_high` | float | High price of completed 30-minute bar |
| `prev_30m_low` | float | Low price of completed 30-minute bar |
| `prev_30m_close` | float | Close price of completed 30-minute bar |
| `prev_30m_volume` | float | Volume of completed 30-minute bar |
| `prev_30m_pivot` | float | Pivot point of completed 30-minute bar |
| `prev_30m_r1` | float | Pivot resistance R1 of completed 30-minute bar |
| `prev_30m_s1` | float | Pivot support S1 of completed 30-minute bar |
| `prev_30m_return` | float | Return ratio of completed 30-minute bar |
| `prev_1h_open` | float | Open price of completed 1-hour bar |
| `prev_1h_high` | float | High price of completed 1-hour bar |
| `prev_1h_low` | float | Low price of completed 1-hour bar |
| `prev_1h_close` | float | Close price of completed 1-hour bar |
| `prev_1h_volume` | float | Volume of completed 1-hour bar |
| `prev_1h_pivot` | float | Pivot point of completed 1-hour bar |
| `prev_1h_r1` | float | Pivot resistance R1 of completed 1-hour bar |
| `prev_1h_s1` | float | Pivot support S1 of completed 1-hour bar |
| `prev_1h_return` | float | Return ratio of completed 1-hour bar |

---

## 3. Candlestick Geometry — `candlestick.py`

| Column | Type | Description |
|---|---|---|
| `body` | float | candlestick body length (include both negative & positive values) |
| `height` | float | candlestick height = high - low |
| `body_abs` | float | Absolute candlestick body length |
| `body_abs_sma_medium` | float | Medium lookback simple moving average of absolute body length |
| `range_sma_medium` | float | Medium lookback simple moving average of High minus Low |
| `upwick` | float | candlestick upper wick length = high - max(open, close) |
| `lowwick` | float | candlestick lower wick length = min(open, close) - low |
| `upwick_rate` | float | upper wick rate = upper wick / height |
| `lowwick_rate` | float | lower wick rate = lower wick / height |
| `body_rate` | float | body rate = body / height |
| `candle_range_ratio` | float | Absolute body divided by High minus Low |
| `wick_ratio` | float | wick_ratio = upwick / (upwick + lowwick + epsilon) |
| `upwick_ratio` | float | upwick_ratio = upwick / (lowwick + epsilon) |
| `clv` | float | clv = 1 if High = Low else ((Close-Low) - (High-Close)) / (High - Low) |
| `ibs` | float | ibs = (close - low) / (high - low) |
| `candle_strength` | float | candle_strength = body / (height + epsilon) |
| `vbr` | float | vbr = Volume / (High - Low) |
| `wick_imbalance` | float | wick imbalance = upper wick - lower wick |
| `color` | int | color |
| `heikin_ashi_close` | float | (Open + High + Low + Close) / 4 |
| `heikin_ashi_open` | float | Previous bar Open and Close midpoint |
| `heikin_ashi_bull` | bool | True when heikin_ashi_close is greater than heikin_ashi_open |
| `bullish_high_break_candle` | bool | Bullish candle with High above previous High and Close below the bar High by at least 0.1 |
| `bearish_low_break_candle` | bool | Bearish candle with Low below previous Low and Close above the bar Low by at least 0.1 |

---

## 4. Close Price Indicators — `close.py`

| Column | Type | Description |
|---|---|---|
| `price_change` | float | One-bar difference of Close |
| `price_change_lag1` | float | Previous value of price_change |
| `return_micro` | float | Close percent change over micro lookback |
| `return_short` | float | Close percent change over short lookback |
| `return_medium` | float | Close percent change over medium lookback |
| `return_long` | float | Close percent change over long lookback |
| `return_macro` | float | Close percent change over macro lookback |
| `sma_micro` | float | Micro lookback simple moving average of Close |
| `sma_short` | float | Short lookback simple moving average of Close |
| `sma_medium` | float | Medium lookback simple moving average of Close |
| `sma_long` | float | Long lookback simple moving average of Close |
| `sma_macro` | float | Macro lookback simple moving average of Close |
| `std_micro` | float | Micro lookback rolling standard deviation of Close |
| `std_short` | float | Short lookback rolling standard deviation of Close |
| `std_medium` | float | Medium lookback rolling standard deviation of Close |
| `std_long` | float | Long lookback rolling standard deviation of Close |
| `std_macro` | float | Macro lookback rolling standard deviation of Close |
| `close_min_micro` | float | Micro lookback rolling minimum of Close |
| `close_min_short` | float | Short lookback rolling minimum of Close |
| `close_min_medium` | float | Medium lookback rolling minimum of Close |
| `close_min_long` | float | Long lookback rolling minimum of Close |
| `close_min_macro` | float | Macro lookback rolling minimum of Close |
| `close_max_micro` | float | Micro lookback rolling maximum of Close |
| `close_max_short` | float | Short lookback rolling maximum of Close |
| `close_max_medium` | float | Medium lookback rolling maximum of Close |
| `close_max_long` | float | Long lookback rolling maximum of Close |
| `close_max_macro` | float | Macro lookback rolling maximum of Close |
| `ema_fast` | float | EMA fast = ta.ema(close, length=n) with n = FAST_TREND_LOOKBACK |
| `ema_slow` | float | EMA slow = ta.ema(close, length=n) with n = SLOW_TREND_LOOKBACK |
| `rsi_micro` | float | RSI = ta.rsi(close, length=n) with n = MICRO_LOOKBACK |
| `rsi_short` | float | RSI = ta.rsi(close, length=n) with n = SHORT_LOOKBACK |
| `rsi_medium` | float | RSI = ta.rsi(close, length=n) with n = MEDIUM_LOOKBACK |
| `rsi_long` | float | RSI = ta.rsi(close, length=n) with n = LONG_LOOKBACK |
| `rsi_macro` | float | RSI = ta.rsi(close, length=n) with n = MACRO_LOOKBACK |
| `rsi_slope_medium` | float | df['rsi_medium'].diff() |
| `tsi` | float | TSI = ta.tsi(close, length=n) with n = MOMENTUM_LOOKBACK |
| `roc_close` | float | ROC = ta.roc(close, length=1) |
| `close_zscore` | float | Z-score of Close = ta.zscore(close, length=n) with n = MOMENTUM_LOOKBACK |
| `efficiency_ratio` | float | ER = change / volatility; change = abs(close - close.shift(n)); volatility = sum(abs(close - close.shift(1))) over n periods; with n = MOMENTUM_LOOKBACK |
| `macd` | float | MACD = ta.macd(close, fast=12, slow=26, signal=9) |
| `macd_hist` | float | MACD Hist = ta.macd(close, fast=12, slow=26, signal=9) |
| `macd_line` | float | MACD signal line generated by pandas-ta macd |
| `ppo` | float | PPO = ta.ppo(close, fast=12, slow=26, signal=9) |
| `ppo_hist` | float | PPO Hist = ta.ppo(close, fast=12, slow=26, signal=9) |
| `ppo_line` | float | PPO signal line generated by pandas-ta ppo |
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
| `bias` | float | Close / rolling mean Close - 1 |
| `rbias` | float | One-bar rate of change of Close / rolling mean Close |
| `mtm_mean` | float | Rolling mean of n-period close momentum |
| `mtm_max_diff` | float | Current n-period momentum minus prior rolling max momentum |
| `sroc` | float | Rate of change of EMA-smoothed Close over 2n bars |
| `ar` | float | 100 * rolling sum(High - Open) / rolling sum(Open - Low) |
| `br` | float | 100 * rolling sum(High - previous Close) / rolling sum(previous Close - Low) |
| `cr` | float | 100 * rolling upward pressure over previous typical price divided by downward pressure |
| `adtm` | float | (rolling DTM - rolling DBM) / max(rolling DTM, rolling DBM) |
| `qstick` | float | (Close - Open) normalized by rolling mean Close - Open |
| `mtm` | float | (Close / Close.shift(n) - 1) * 100 |
| `kst` | float | Weighted multi-horizon close ROC oscillator normalized by its rolling mean |
| `rmi` | float | Four-bar positive close momentum divided by rolling absolute close movement |
| `tii` | float | Normalized ratio of positive close deviations from rolling mean |
| `return_autocorr` | float | Rolling correlation of one-bar returns with lagged returns |
| `demarker` | float | Rolling positive high movement divided by positive high plus low movement |
| `imi` | float | Rolling close-open up movement divided by total close-open movement |
| `rvi` | float | Upward close volatility divided by upward plus downward close volatility |
| `bop` | float | Rolling mean of (Close - Open) / (High - Low) |
| `ultimate_oscillator_src` | float | Triple-timeframe buying pressure oscillator adapted from quant-ohlcv-feature |
| `williams_r` | float | (rolling high - Close) / (rolling high - rolling low) * 100 |
| `slow_stoch_d` | float | Slow stochastic oscillator D line adapted from SKDJ |
| `coppock` | float | Rolling mean of combined n-period and 2n-period close ROC |
| `pmo` | float | Double-smoothed close ROC momentum oscillator |
| `smi` | float | Smoothed close distance from rolling high-low midpoint |
| `psy` | float | Percent of bars in lookback where Close rose |
| `change_std` | float | Close.pct_change(n) * rolling std of one-bar returns adapted from quant-ohlcv-feature |
| `dpo` | float | (Close - shifted rolling mean Close) / rolling mean Close |
| `pfe` | float | Direction-signed price efficiency based on direct distance divided by path distance |
| `high_ma_bias` | float | (High - rolling mean High) / rolling mean High with n = FAST_TREND_LOOKBACK |
| `bollinger_width` | float | (ub - lb) / mb |
| `bollinger_percent_b` | float | (Close - lb) / (ub - lb) |
| `rsi_mean` | float | Rolling mean of RSI scaled to 0-1, adapted from quant-ohlcv Rsimean |
| `tdi` | float | Rolling-normalized spread between RSI price and signal lines |
| `osc` | float | Rolling mean of close minus its 2n-period moving average |
| `short_quiet_momentum` | float | Sum of n-period returns from the lowest-amplitude 70 percent of bars in the short window |
| `long_quiet_momentum` | float | Sum of n-period returns from the lowest-amplitude 70 percent of bars in a 10n window |
| `price_volume_momentum` | float | EMA-smoothed price momentum multiplied by EMA-smoothed quote-volume momentum |
| `dbcd` | float | Rolling average of close moving-average bias divergence |
| `pmarp` | float | Percentile rank of absolute close-to-moving-average ratio |
| `pos` | float | Position of current n-period return within its rolling min-max range |
| `swing_index` | float | Weighted price movement index adapted from quant-ohlcv Si |
| `rsi_v2` | float | Rolling-sum RSI variant using up/down close moves |
| `cmo_v2` | float | Rolling-sum CMO variant using up/down close moves |
| `bias_v13` | float | Rolling mean of short MA divided by long MA minus 1 |
| `abs_chg` | float | Absolute n-period close return |
| `stc` | float | Double-stochastic oscillator of MACD-like close momentum |
| `return_autocorr_2` | float | Rolling lag-1 autocorrelation of close returns |
| `erbull` | float | High minus EMA(close) normalized by EMA(close) |
| `erbear` | float | Low minus EMA(close) normalized by EMA(close) |
| `er_balance` | float | Bull power plus bear power |
| `burr` | float | Pullback depth or rebound height conditioned on N-bar trend direction |
| `macd_v2` | float | MACD histogram variant on midpoint price (High+Low)/2 |
| `ppo_v1` | float | EMA acceleration product variant of PPO |
| `sroc_v2` | float | Smoothed rate of change of an adaptive moving average proxy |
| `pmo_tema` | float | PMO computed from TEMA-smoothed close prices |
| `fisher_v2` | float | Fisher transform variant with stronger smoothing |
| `fisher_v3` | float | Fisher transform variant with alternate smoothing and log mapping |
| `arbr_ar` | float | AR-style range sentiment using high-open and open-low sums |
| `arbr_br` | float | BR-style range sentiment using high-prev-close and prev-close-low sums |
| `bias_v3` | float | Log close-to-moving-average bias normalized by 0.03 |
| `bias_v4` | float | Typical price divided by its moving average minus 1 |
| `bias_v11` | float | EMA-smoothed close bias weighted by quote-volume proxy |
| `bias_v14` | float | Rolling fast/slow MA bias weighted by quote-volume proxy |
| `bir` | float | Four-price average breakout pressure over rolling extrema |
| `copp_v3` | float | Coppock-style average of N and 1.618N close rates of change |
| `do` | float | Double-smoothed RSI variant |
| `po` | float | Percent oscillator from short and long EMAs |
| `cci_magic` | float | Smoothed CCI variant using MA of OHLC prices |
| `cs_mtm` | float | Composite momentum: close momentum x std momentum x volume momentum |
| `cs_mtm_v2` | float | Composite momentum using close momentum, std momentum, and quote-volume momentum |
| `mtmmean_v12` | float | MTM weighted by taker-buy volume ratio and averaged over a rolling window |
| `rsi_bbw` | float | Bollinger bandwidth change times momentum and RSI |
| `rccd` | float | Smoothed difference of moving averages applied to smoothed close ratio |
| `rccd_v2` | float | SMA-smoothed variant of RCCD |
| `bias_vol` | float | Volume relative to its moving average minus 1 |
| `bias_cubic_v2` | float | Product of three bias terms amplified by quote-volume proxy |
| `copp_min_route` | float | Coppock curve divided by normalized shortest intraday route |
| `adtm_v2` | float | Open-price sentiment normalized to 0-1 |
| `adtm_v3` | float | Open-price sentiment contrasted against close-adjusted term |
| `mtm_mean_gap` | float | Close momentum divided by candle body gap mean |
| `cmo_v3` | float | Rolling mean of a smoothed Chande Momentum Oscillator |
| `rsis_v2` | float | RSI scaled within its rolling min-max band |
| `mtm_vol_resonance` | float | Close momentum blended with quote-volume expansion |
| `tii_signal` | float | EMA-smoothed Traders Intensity Index |
| `tii_signal_v2` | float | Normalized spread between TII and its signal line |
| `roc` | float | Close divided by its N-period lag minus 1 |
| `cci_v2` | float | WMA-based CCI using all four prices |
| `cci_v3` | float | EMA-smoothed CCI using all four prices |
| `rsimean` | float | Rolling mean of RSI |
| `short_moment` | float | Momentum based on the lowest-amplitude candles in a short window |
| `long_moment` | float | Momentum based on the lowest-amplitude candles in a long window |
| `rsis` | float | RSI normalized to its rolling min-max range |
| `pmarp_yidai_v1` | float | Rolling percentile rank of absolute close-to-MA ratio |
| `dbcd_v2` | float | EWM-smoothed change in close-to-MA bias |
| `smi_v2` | float | Smoothed stochastic midpoint oscillator |
| `dbcd_v3` | float | SMA-smoothed bias divergence |
| `micd` | float | Momentum indicator based on shifted MTM averages |
| `rsj` | float | Asymmetry of upside vs downside realized variance |
| `mtm_max` | float | Current momentum minus rolling maximum prior momentum |
| `bias_v2` | float | Volume-weighted bias on regression-smoothed close |
| `rsiv` | float | Volume-based RSI analogue |
| `rsih` | float | RSI minus its EMA signal line |
| `fi` | float | Force Index z-score smoothed by EMA |
| `fi_rsi` | float | RSI of Force Index smoothed by EMA |
| `force` | float | Quote-volume force index relative to its moving average |
| `ko` | float | Klinger oscillator variant normalized to rolling range |
| `vramt` | float | Volume ratio computed from up/down/flat volume buckets |
| `v1_v2` | float | V1 composite momentum-volatility factor |
| `v1up_v2` | float | Upper adaptive band distance for V1 |
| `v1dn_v2` | float | Lower adaptive band distance for V1 |
| `mtmmean_v10` | float | Momentum mean multiplied by combined long-range and intrabar volatility |
| `mtmhcm` | float | High-based momentum mean relative to close moving-average compression |
| `si` | float | Weighted price-movement strength normalized by range components |
| `wr` | float | Position of close within the rolling high-low range |
| `rocvol` | float | Volume rate of change over the momentum lookback |
| `mtmmean_v4` | float | Rolling regression of N-period momentum |
| `uos` | float | Triple-timeframe momentum oscillator over close and true range |
| `zlmacd` | float | DEMA-based MACD variant normalized by the spread between zero-lag averages |
| `tma_bias` | float | Close divided by double-smoothed moving average minus 1 |
| `mtmmean_v8` | float | Momentum mean multiplied by high-low range volatility |
| `mtmvolmean` | float | EMA-smoothed price momentum times EMA-smoothed quote-volume momentum |
| `autocorrelation` | float | Rolling lag-1 autocorrelation of close returns |
| `copp` | float | Coppock-style moving average of combined close ROC |
| `demaker` | float | DeMarker ratio of upward and downward pressure |
| `er` | float | Bull power plus bear power around EMA baseline |
| `kdjdk` | float | K line from the KDJD oscillator |
| `kdjdd` | float | D line from the KDJD oscillator |
| `skdj` | float | Slow KDJ oscillator |
| `magiccci` | float | CCI variant using OHLC EWM-smoothed typical price |
| `magiccci_v2` | float | CCI variant using HLC EWM-smoothed typical price |
| `amplitude` | float | amplitude = (High / Low) - 1.0 |
| `stoch_rsi` | float | Stochastic RSI of Close |
| `awesome_oscillator` | float | Awesome Oscillator (5-34) |
| `roc_short` | float | Rate of change over short lookback |
| `ultimate_osc` | float | Ultimate Oscillator (7-14-28) |
| `stochrsi_k` | float | StochRSI K line |
| `stochrsi_d` | float | StochRSI D line |
| `williams_r_14` | float | Williams %R over 14 periods |
| `bb_percent_b_medium_2` | float | Bollinger Band percent B with medium lookback and 2 standard deviations |

---

## 5. Price Derived Indicators — `price.py`

| Column | Type | Description |
|---|---|---|
| `typical_price` | float | typical_price = (High + Low + Close) / 3 |
| `weighted_close` | float | weighted_close = (High + Low + 2 * Close) / 4 |
| `midpoint` | float | Midpoint of High and Low |
| `close_vs_mid` | float | Close minus the High-Low midpoint |
| `typical_price_momentum` | float | Z-scored spread between fast EMA and slow EMA of typical_price |
| `weighted_close_bias` | float | weighted_close EMA(n) / weighted_close EMA(2n) - 1 with n = MOMENTUM_LOOKBACK |
| `rolling_vwap` | float | rolling_vwap = rolling sum(typical_price * Volume) / rolling sum(Volume) |
| `vwap_bias` | float | Rolling VWAP divided by its moving average minus 1 |
| `close_to_vwap` | float | close_to_vwap = Close / rolling_vwap - 1 |
| `vwap_range_position` | float | Rolling VWAP normalized within its rolling min/max range |
| `vwap_to_high` | float | rolling_vwap / High - 1 |
| `vwap_to_low` | float | rolling_vwap / Low - 1 |
| `close_ma_price` | float | Rolling mean Close over MOMENTUM_LOOKBACK |
| `typical_to_vwap` | float | typical_price / rolling_vwap - 1 |
| `avgprice` | float | Rolling VWAP normalized within its rolling range |
| `avgpricetohigh` | float | VWAP relative to current high |
| `avgpricetolow` | float | VWAP relative to current low |
| `lowprice` | float | Rolling mean close price |
| `typ` | float | Typical price (H+L+C)/3 |
| `vwap_signal` | float | Typical price relative to rolling VWAP minus 1 |
| `wc` | float | Weighted close EMA ratio |
| `wvad` | float | Normalized rolling candle-body volume accumulation |
| `open_range_high_2` | float | High of the first two bars in each trading day |
| `open_range_low_2` | float | Low of the first two bars in each trading day |
| `session_open` | float | First Open value of each trading day |
| `session_high_shift1` | float | Running session High shifted one bar within the trading day |
| `session_low_shift1` | float | Running session Low shifted one bar within the trading day |
| `close_vs_session_range` | float | Close normalized within prior shifted session high-low range |
| `session_range_pct` | float | Running session high-low range divided by session_open, percent |
| `session_body_pct` | float | Close minus session_open divided by session_open, percent |
| `session_body_rate` | float | Close minus session_open divided by previous trading day range |
| `session_mom_y` | float | Close percent change versus previous trading day close |
| `mom_y` | float | Close percent change versus previous day close |
| `session_vwap` | float | Running session VWAP from Close and Volume |
| `session_vwap_std` | float | Running volume-weighted standard deviation around session_vwap |
| `session_vwap_upper_1_5` | float | session_vwap plus 1.5 session_vwap_std |
| `session_vwap_lower_1_5` | float | session_vwap minus 1.5 session_vwap_std |
| `session_vwap_z` | float | Close minus session_vwap divided by session_vwap_std |
| `session_vwap_dev_pct` | float | Close deviation from session_vwap divided by Close, percent |

---

## 6. Trend Indicators — `trend.py`

| Column | Type | Description |
|---|---|---|
| `hullma_bias` | float | Low-lag Hull-style EMA component divided by its sqrt-window EMA smoother minus 1 |
| `ichimoku_cloud_ratio` | float | Ichimoku span A divided by span B using trend lookback multiples |
| `t3_bias` | float | Close / Tillson T3 moving average - 1 |
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
| `ma_signal` | float | Rolling-normalized close minus moving average trend signal |
| `bbi_ratio` | float | Bull and Bear Index moving-average blend divided by close |
| `bbi_bias` | float | Close divided by Bull and Bear Index minus 1 |
| `adxr_diff` | float | Lag-smoothed DI+ minus DI- directional trend spread |
| `wma_ma_gap` | float | Weighted MA minus simple MA normalized by rolling absolute gap |
| `adx_strength` | float | Rolling normalized positive and negative directional movement over true range |
| `adx_di_plus` | float | Positive directional index component from the source ADX DI+ file |
| `adx_di_minus` | float | Negative directional index component from the source ADX DI- file |
| `vi_plus` | float | Vortex-style positive movement over true range |
| `vi_minus` | float | Vortex-style negative movement over true range |
| `turtle_breakout` | float | Close breakout distance relative to Turtle channel width |
| `turtle_distance` | float | Signed distance of close from Turtle channel boundary |
| `ma_ratio` | float | Rolling mean close divided by close |
| `dema_bias2` | float | Double-smoothed close trend bias |
| `tema_bias2` | float | Triple-smoothed close trend bias |
| `hma_ratio` | float | High price relative to rolling mean of high |
| `vidya_bias` | float | VIDYA-style adaptive average bias |
| `tma_bias2` | float | Close versus double-smoothed moving average |
| `vma_ratio` | float | Average price relative to its moving average |
| `lma_ratio` | float | Low price relative to its moving average |
| `mm_ratio` | float | Fast MA divided by slow MA minus 1 |
| `reg_angle` | float | Angle of rolling close regression slope in degrees |
| `expma_ratio` | float | Fast EMA divided by slower EMA minus 1 |
| `reg` | float | Close divided by rolling linear regression minus 1 |
| `reg_v2` | float | Percentage deviation of Close from a 2N rolling regression line |
| `reg_v3` | float | Close divided by rolling OLS regression fit minus 1 |
| `diff_ema` | float | Difference between short and long EMAs |
| `diff_ema_ratio` | float | EMA spread normalized by its own EMA |
| `regema_bias` | float | Close relative to its EMA baseline minus 1 |
| `regtema_bias` | float | TEMA relative to its regression baseline minus 1 |
| `trtrix` | float | One-bar percent change of the EMA trend line |
| `trv` | float | Smoothed percentage change of the rolling close mean |
| `mac_v4` | float | Moving average channel using rolling high/low extremes and open price |
| `mac_v5` | float | Moving average channel using rolling high/low extremes and close price |
| `acs` | float | Rolling standard deviation of normalized ADX strength |
| `mak` | float | Amplified one-bar change of the rolling close mean |
| `sgcz` | float | Close relative to the rolling mean of high prices |
| `gap_ratio` | float | Weighted moving average gap normalized by rolling absolute gap |
| `angle_reg` | float | Angle of rolling regression slope in degrees |
| `cse` | float | Time-series normalized close smoothed by EMA |
| `madis_placed` | float | Close divided by displaced moving average minus 1 |
| `trrq` | float | Typical price regression return normalized by volume proxy |
| `mreg` | float | Rolling mean of close versus linear regression residual |
| `adxr_pos` | float | Smoothed positive directional index component |
| `adxr_neg` | float | Smoothed negative directional index component |
| `hma_signal` | float | High price minus its rolling mean, normalized to a 0-1 range |
| `hullma_signal` | float | Hull moving-average spread normalized to a 0-1 range |
| `mac_v2` | float | Midpoint-price MAC normalized to a 0-1 range |
| `mac_v3` | float | Rolling channel-midpoint MAC normalized to a 0-1 range |
| `hullma_ratio` | float | Hull moving-average numerator divided by its smoothed denominator |
| `vidya_v2` | float | Open-close midpoint VIDYA normalized by close |
| `vidya_v5` | float | Typical-price VIDYA normalized by close |
| `mac` | float | Close-price moving-average convergence normalized to 0-1 |
| `pjc_distance` | float | Close distance above mean absolute deviation normalized by MAD |
| `hma` | float | High price minus its rolling mean normalized by the mean |
| `tma_v2` | float | Double-smoothed midpoint-price TMA normalized by close |
| `tma_v3` | float | Double-smoothed rolling channel midpoint TMA normalized by close |
| `vidya_v3` | float | Typical-price VIDYA normalized by close |
| `vidya_v4` | float | Open-close midpoint VIDYA normalized by close |
| `gap` | float | Weighted MA minus simple MA normalized by rolling absolute gap |
| `arron` | float | Z-scored difference between rolling high and low recency |
| `ma` | float | Close rolling mean normalized within its rolling range |
| `vma` | float | Open-high-low-close average normalized by its rolling mean |
| `mm` | float | Fast moving average divided by slow moving average minus 1 |
| `expma` | float | Difference between fast and slow EMAs normalized to [0,1] |
| `lma` | float | Low-price moving average bias |
| `dema` | float | Double exponential moving average normalized by its EMA baseline |
| `tema` | float | Triple exponential moving average normalized by its EMA baseline |
| `hlma` | float | High-low moving average spread normalized by its own mean |
| `ic_v2` | float | Close relative to the Ichimoku cloud span boundaries |
| `ic_v3` | float | Normalized Ichimoku cloud thickness |
| `ic_v4` | float | Normalized close position inside the Ichimoku cloud |
| `adxrpos` | float | Smoothed positive directional movement component |
| `dma` | float | ATR-weighted moving average difference |
| `angle` | float | Angle of the rolling linear regression line of close prices |
| `vi` | float | Vortex positive minus negative directional spread |
| `trrq_v3` | float | Asymmetric regression-return signal using quote-volume proxy |
| `adxr` | float | Source ADXR spread between smoothed DI+ and DI- |
| `bbi` | float | Bull and Bear Index normalized by close |
| `hullma` | float | Hull moving-average ratio using the source formula |
| `ic` | float | Span A divided by Span B from the source IC file |
| `regema` | float | Close divided by linear regression of EMA(close) minus 1 |
| `regtema` | float | TEMA divided by linear regression of TEMA minus 1 |
| `tema_v2` | float | Close relative to a 2N-period TEMA |
| `tma` | float | Close divided by double-smoothed moving average minus 1 |
| `turtle` | float | Source turtle-channel breakout distance normalized by channel width |
| `vidya` | float | Close relative to the source VIDYA baseline |
| `t3` | float | Close divided by Tillson T3 minus 1 |
| `hma_medium` | float | Hull Moving Average over medium lookback |
| `kama_short` | float | Kaufman Adaptive Moving Average over short lookback |
| `trix15` | float | TRIX indicator over 15 periods |
| `trix15_signal` | float | TRIX 15 signal line |
| `supertrend_dir` | float | SuperTrend direction component |
| `tenkan` | float | Ichimoku Tenkan-sen component |
| `kijun` | float | Ichimoku Kijun-sen component |
| `span_a` | float | Ichimoku Senkou Span A component |
| `span_b` | float | Ichimoku Senkou Span B component |
| `linreg_slope_medium` | float | Linear regression slope over medium lookback |
| `linreg_mid_medium` | float | Linear regression midline over medium lookback |
| `linreg_upper_medium` | float | linreg_mid_medium plus two times std_medium |
| `linreg_lower_medium` | float | linreg_mid_medium minus two times std_medium |
| `tma_short` | float | Triangular Moving Average over short lookback |
| `high_micro` | float | Micro lookback rolling maximum of High |
| `low_micro` | float | Micro lookback rolling minimum of Low |
| `high_short` | float | Short lookback rolling maximum of High |
| `low_short` | float | Short lookback rolling minimum of Low |
| `high_medium` | float | Medium lookback rolling maximum of High |
| `low_medium` | float | Medium lookback rolling minimum of Low |
| `high_long` | float | Long lookback rolling maximum of High |
| `low_long` | float | Long lookback rolling minimum of Low |
| `high_macro` | float | Macro lookback rolling maximum of High |
| `low_macro` | float | Macro lookback rolling minimum of Low |
| `range_mid_short` | float | Midpoint between high_short and low_short |
| `recent_high` | float | Medium lookback rolling High shifted by one bar |
| `recent_low` | float | Medium lookback rolling Low shifted by one bar |
| `recent_high_prev` | float | recent_high shifted by micro lookback |
| `recent_low_prev` | float | recent_low shifted by micro lookback |
| `prev_micro_low` | float | low_micro shifted by one bar |
| `prev_micro_high` | float | high_micro shifted by one bar |
| `prev_short_low` | float | low_short shifted by one bar |
| `prev_short_high` | float | high_short shifted by one bar |
| `prev_medium_low` | float | low_medium shifted by one bar |
| `prev_medium_high` | float | high_medium shifted by one bar |
| `prev_long_low` | float | low_long shifted by one bar |
| `prev_long_high` | float | high_long shifted by one bar |
| `prev_macro_low` | float | low_macro shifted by one bar |
| `prev_macro_high` | float | high_macro shifted by one bar |
| `lower_range_pos` | float | 30 percent level above low_short within the short high-low range |
| `upper_range_pos` | float | 30 percent level below high_short within the short high-low range |
| `ema_8` | float | Exponential moving average of Close over 8 periods |
| `ema_20` | float | Exponential moving average of Close over 20 periods |
| `ema_21` | float | Exponential moving average of Close over 21 periods |
| `ema_55` | float | Exponential moving average of Close over 55 periods |
| `ema_250` | float | Exponential moving average of Close over 250 periods |
| `adx_14` | float | Average Directional Index over 14 periods |
| `dmp_14` | float | Positive directional movement over 14 periods |
| `dmn_14` | float | Negative directional movement over 14 periods |
| `psar_bull` | bool | True when Parabolic SAR indicates a bullish leg |
| `psar_bear` | bool | True when Parabolic SAR indicates a bearish leg |
| `linear_regression_slope_micro` | float | Linear regression slope of Close over micro lookback |

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
| `adaptive_bollinger_width` | float | Adaptive z-score Bollinger bandwidth normalized by close moving average |
| `vwap_bbw_efficiency` | float | Rolling VWAP change times Bollinger-width change normalized by quote-volume proxy |
| `chaikin_volatility` | float | Rate of change of EMA high-low range |
| `realized_volatility` | float | Rolling standard deviation of one-bar returns |
| `realized_volatility_zscore` | float | Z-score of realized_volatility over VOLATILITY_LOOKBACK |
| `rwi` | float | Close normalized within upward/downward Random Walk Index range |
| `mssi` | float | Max of average drawdown from rolling high and reverse drawdown from rolling low |
| `vix_bw` | float | Volatile directional bandwidth proxy |
| `keltner_width` | float | Keltner channel width normalized by EMA middle band |
| `keltner_upper_signal` | float | Rolling-normalized Keltner upper band |
| `keltner_lower_signal` | float | Rolling-normalized Keltner lower band |
| `env_upper_signal` | float | Rolling-normalized 5 percent envelope upper band |
| `env_lower_signal` | float | Rolling-normalized 5 percent envelope lower band |
| `fibonacci_band_width` | float | Fibonacci ATR channel width normalized by rolling close mean |
| `fibonacci_band_position` | float | Close position inside first Fibonacci ATR channel |
| `donchian_mid_signal` | float | Close minus Donchian channel midpoint |
| `atr_micro` | float | atr = ta.atr(high, low, close, length=n) with n = MICRO_LOOKBACK |
| `atr_short` | float | atr = ta.atr(high, low, close, length=n) with n = SHORT_LOOKBACK |
| `atr_medium` | float | atr = ta.atr(high, low, close, length=n) with n = MEDIUM_LOOKBACK |
| `atr_long` | float | atr = ta.atr(high, low, close, length=n) with n = LONG_LOOKBACK |
| `atr_macro` | float | atr = ta.atr(high, low, close, length=n) with n = MACRO_LOOKBACK |
| `atr_pct_micro` | float | Micro ATR divided by close |
| `atr_pct_short` | float | Short ATR divided by close |
| `atr_pct_medium` | float | Medium ATR divided by close |
| `atr_pct_long` | float | Long ATR divided by close |
| `atr_pct_macro` | float | Macro ATR divided by close |
| `rwi_high` | float | RWI high component based on upward range |
| `rwi_low` | float | RWI low component based on downward range |
| `bbw_signal` | float | Bollinger bandwidth change times n-period momentum and RSI-like close pressure |
| `kc_signal` | float | (Close - kc_middle + 2 * kc_atr) / (4 * kc_atr + epsilon) |
| `atr_upper_medium` | float | ATR-based upper channel ratio normalized by moving average |
| `atr_lower_medium` | float | ATR-based lower channel ratio normalized by moving average |
| `fb_upper_signal` | float | Scaled signal for 1.618 Fibonacci upper band distance |
| `pac_width_signal` | float | PAC width normalized by its rolling mean minus 1 |
| `volume_std` | float | Rolling standard deviation of Volume |
| `grid` | float | N-period percent change of rolling z-score position |
| `lcsd` | float | Low price versus close moving average normalized by low |
| `atr_count` | float | Count of closes outside an ATR band over the lookback |
| `zfabsmean` | float | Ranked mean positive amplitude after filtering on average-price change |
| `bbw` | float | Bollinger bandwidth change multiplied by momentum and RSI |
| `apz` | float | Adaptive Price Zone channel width normalized by double EMA close |
| `apz_upper` | float | Upper Adaptive Price Zone channel normalized to rolling range |
| `apz_lower` | float | Lower Adaptive Price Zone channel normalized to rolling range |
| `bolling` | float | Distance from Bollinger Band normalized by standard deviation |
| `bolling_width` | float | Adaptive Bollinger width based on rolling z-score mean |
| `cv` | float | Rate of change of high-low EMA amplitude |
| `dc` | float | Distance between close and Donchian middle channel normalized by channel width |
| `dc_signal` | float | Close minus Donchian middle channel |
| `dc_v2` | float | Close relative to Donchian middle channel |
| `kcupper` | float | Keltner channel upper band normalized to rolling range |
| `kclower` | float | Keltner channel lower band normalized to rolling range |
| `pac` | float | PAC width normalized by its rolling mean |
| `pacupper` | float | PAC upper band normalized to rolling range |
| `paclower` | float | PAC lower band normalized to rolling range |
| `pacupper_v2` | float | Close minus PAC upper band, rolling averaged |
| `paclower_v2` | float | PAC lower band minus close, rolling averaged |
| `bolling_v2` | float | 2 * std / (ma + epsilon) |
| `bolling_v3` | float | (upper - upper.shift(1)) / (ma + epsilon) |
| `bolling_fancy` | float | (Close - ma) / (std + epsilon) |
| `env_signal` | float | (Close - env_lower) / (0.1 * env_middle + epsilon) |
| `env_upper` | float | Scaled upper envelope over volatility lookback |
| `env_lower` | float | Scaled lower envelope over volatility lookback |
| `kc_upper_signal` | float | Scaled distance to Keltner upper band |
| `kc_lower_signal` | float | Scaled distance to Keltner lower band |
| `vwap_bbw` | float | Cumulative product of VWAP change and BBW change over volume |
| `ret_boll_fancy` | float | Z-score of returns over rolling volatility lookback |
| `lchc_fancy` | float | -1.0 * min(Low) / Close - max(High) / Close |
| `adapt_bolling_v3` | float | Multi-period momentum and ATR composite index |
| `bollcount_dem` | float | Rolling sum of DeMarker directional signals |
| `dzcci_lower` | float | Distance between lower CCI band and short CCI MA |
| `dzcci_upper` | float | Scaled upper CCI band over volatility lookback |
| `dzrsi_lower_signal` | float | Standardized dynamic zone RSI lower signal |
| `dzrsi_upper_signal` | float | Scaled dynamic zone RSI upper signal |
| `fb_lower` | float | Scaled lower Fibonacci ATR channel band |
| `fb_upper` | float | Scaled upper Fibonacci ATR channel band |
| `dzcci_lower_signal` | float | Standardized difference between CCI lower band and close |
| `dzcci_lower_signal_v2` | float | Scaled difference between CCI lower band and short CCI MA |
| `dzcci_upper_signal` | float | Scaled difference between close and CCI upper band |
| `dzcci_upper_signal_v2` | float | Scaled difference between short CCI MA and CCI upper band |
| `fb_lower_signal` | float | Scaled signal for 1.618 Fibonacci lower band distance |
| `fb_lower_signal_v2` | float | Scaled signal for 2.618 Fibonacci lower band distance |
| `fb_lower_signal_v3` | float | Scaled signal for 4.236 Fibonacci lower band distance |
| `fb_upper_signal_v2` | float | Scaled signal for 2.618 Fibonacci upper band distance |
| `fb_upper_signal_v3` | float | Scaled signal for 4.236 Fibonacci upper band distance |
| `bb_width` | float | Standard Bollinger Band Width used for signals |
| `bb_width_q20` | float | 100-bar rolling 20th percentile of bb_width |
| `bb_width_sma_medium` | float | Medium lookback simple moving average of bb_width |
| `atr_sma_medium` | float | Medium lookback simple moving average of atr_medium |
| `kc_mid` | float | Keltner Channel mid line (EMA medium lookback) |
| `kc_upper` | float | Keltner Channel upper band (mid + 2 * atr_medium) |
| `kc_lower` | float | Keltner Channel lower band (mid - 2 * atr_medium) |
| `chop14` | float | Choppiness Index over 14 periods |
| `hurst_proxy` | float | Hurst Exponent Proxy over medium lookback |
| `body_atr_ratio` | float | Close minus Open divided by atr_medium |
| `keltner_upper_medium_2` | float | Keltner upper band with medium lookback and scalar 2 |
| `keltner_lower_medium_2` | float | Keltner lower band with medium lookback and scalar 2 |
| `donchian_high_short_shift1` | float | Short lookback rolling High maximum shifted one bar |
| `donchian_low_short_shift1` | float | Short lookback rolling Low minimum shifted one bar |
| `close_donchian_high_medium_shift1` | float | Medium lookback rolling Close maximum shifted one bar |
| `close_donchian_low_medium_shift1` | float | Medium lookback rolling Close minimum shifted one bar |

---

## 8. Volume — `volume.py`

| Column | Type | Description |
|---|---|---|
| `volume_avg` | float | Trung bình khối lượng n phiên |
| `volume_sma_medium` | float | Medium lookback simple moving average of Volume |
| `volume_zscore` | float | Z-score khối lượng |
| `roc_volume` | float | Volume / Volume.shift(n) - 1 |
| `quote_volume_sum` | float | Rolling sum of Close * Volume quote-volume proxy |
| `volume_bias_short_long` | float | Short-window quote-volume proxy mean divided by long-window mean minus 1 |
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
| `quote_volume_reg` | float | Rolling linear-regression fitted value of Close * Volume proxy |
| `quote_volume_tsf` | float | One-step rolling linear-regression forecast of Close * Volume proxy |
| `price_volume_corr` | float | Rolling correlation between Close and Close * Volume proxy |
| `obv_clv` | float | Rolling CLV-weighted volume normalized by its rolling mean |
| `cmf` | float | Rolling CLV-weighted volume divided by rolling volume |
| `emv` | float | Midpoint move divided by volume density per price range |
| `force_index` | float | EMA-smoothed z-score of Volume * Close.diff() |
| `pvo` | float | (EMA(Volume,n) - EMA(Volume,2n)) / EMA(Volume,2n) |
| `directional_volume_change` | float | Rolling maximum of quote-volume proxy change signed by close direction |
| `volume_ratio_amount` | float | (up amount + flat amount / 2) / (down amount + flat amount / 2) |
| `adosc` | float | Normalized EMA spread of cumulative CLV-weighted volume |
| `klinger_oscillator` | float | Normalized EMA spread of signed volume by typical price direction |
| `vra` | float | Dual-horizon price ROC multiplied by rolling close volatility |
| `ke` | float | Signed squared n-period price change amplified by normalized volume |
| `volume_ma_bias` | float | Volume divided by its moving average minus 1 |
| `amv_signal` | float | Rolling-normalized volume-weighted average of open-close midpoint |
| `volume_ratio` | float | Up-volume plus half neutral volume divided by down-volume plus half neutral volume |
| `macd_volume_ratio` | float | Volume MACD divided by its rolling signal minus 1 |
| `volume_analysis_oscillator` | float | Short minus long average of volume weighted by close position versus candle midpoint |
| `force_ratio` | float | Force index divided by its rolling mean |
| `quote_volume_mean` | float | Rolling mean of Close * Volume proxy |
| `quote_volume_ratio` | float | Quote-volume proxy divided by its rolling mean |
| `v1` | float | V1 momentum-volatility composite |
| `v1_up` | float | Distance from V1 to its adaptive upper Bollinger-like band |
| `v1_down` | float | Distance from V1 to its adaptive lower Bollinger-like band |
| `mfi_standard` | float | Typical-price money flow index using positive and negative flow sums |
| `chla_fancy` | float | CLV-weighted quote-volume proxy rolling sum |
| `net_vol_fancy` | float | Return-signed quote-volume proxy rolling sum |
| `srocvol` | float | Rate of change of long EMA-smoothed volume |
| `roc_vol` | float | Volume divided by its N-period lag minus 1 |
| `volume_reg` | float | Linear regression of quote-volume proxy |
| `macdvol` | float | Volume-based MACD normalized by its signal line |
| `amv` | float | Volume-weighted moving average of open-close midpoint |
| `mfi` | float | Money Flow Index based on typical price and volume |
| `obv` | float | CLV-weighted On Balance Volume variant |
| `pvt_v2` | float | Price Volume Trend normalized by rolling score |
| `pvt_v3` | float | Price Volume Trend short versus long score spread |
| `pvt_v4` | float | Price Volume Trend normalized by rolling score |
| `vr` | float | Volume ratio of up-day and down-day volume |
| `vao` | float | Volume analysis oscillator from midpoint-weighted volume |
| `vao_v2` | float | Normalized volume analysis oscillator |
| `volume_bias` | float | Short-window quote-volume proxy mean divided by long-window mean minus 1 |
| `volume` | float | Rolling sum of quote-volume proxy |
| `volumechg` | float | Direction-weighted quote-volume change |
| `maamt` | float | Volume relative to its rolling mean |
| `upnum_fancy` | float | Rolling count of positive close changes |
| `trade_num` | float | Rolling sum of trade count proxy |
| `taker_by_ratio` | float | Rolling taker-buy quote volume divided by rolling quote volume |
| `buy_vol_ratio_fancy` | float | Taker-buy quote volume divided by quote volume |
| `taker_by_ratio_per_trade` | float | Taker-buy ratio normalized by rolling trade count |
| `vol_per_trade_fancy` | float | Rolling quote volume divided by rolling trade count |
| `buy_vwap_div_vwap_fancy` | float | Taker-buy VWAP divided by rolling VWAP |
| `mtm_tb` | float | EMA-smoothed close momentum multiplied by taker-buy pressure |
| `dbcd_taker` | float | DBCD bias oscillator multiplied by taker-buy ratio |
| `mtm_bull` | float | Momentum, ATR, and taker-buy composite |
| `mtm_bear` | float | Momentum, ATR, and taker-sell composite |
| `v1dn` | float | Lower adaptive band distance for the V1 composite |
| `v1up` | float | Upper adaptive band distance for the V1 composite |
| `mfi14` | float | Money Flow Index over 14 periods |
| `vpt` | float | Cumulative Volume Price Trend indicator |
| `signed_volume` | float | Volume signed by candle direction with Close diff fallback |
| `session_flow_imbalance` | float | Running signed_volume divided by running session Volume |

---

## 9. Liquidity / Composite Proxies — `liquidity.py`

| Column | Type | Description |
|---|---|---|
| `market_placement` | float | Close relative to EMA quote-volume/volume holding-cost proxy |
| `path_liquidity` | float | Rolling quote-volume proxy per normalized shortest intrabar price path |
| `spread_proxy` | float | Rolling mean log high-low range as an OHLC bid-ask spread proxy |
| `spread_volatility_ratio` | float | spread_proxy divided by rolling close-return volatility |
| `price_volume_resistance` | float | Price move magnitude per volume move magnitude adapted from PriceVolumeResist |
| `bidask_spread` | float | Rolling bid-ask spread estimate from OHLC prices |
| `market_placement_v2` | float | VWAP-validity checked market placement proxy |
| `liquidity_v3` | float | Volume divided by log spread and return volatility proxy |
| `coppock_atr_volume` | float | Coppock momentum multiplied by normalized ATR and volume pressure |
| `amihud` | float | Amihud illiquidity proxy using intraday shortest price path |

---

## 10. Lag Features — `lag.py`

| Column | Type | Description |
|---|---|---|
| `close_lag1` | float | Close phiên trước |
| `open_lag1` | float | Open phiên trước |
| `high_lag1` | float | High phiên trước |
| `low_lag1` | float | Low phiên trước |
| `volume_lag1` | float | Volume phiên trước |
| `body_lag1` | float | Body phiên trước |
| `upwick_lag1` | float | Bóng trên phiên trước |
| `lowwick_lag1` | float | Bóng dưới phiên trước |
| `lowwick_rate_lag1` | float | Tỷ lệ bóng dưới phiên trước |
| `upwick_rate_lag1` | float | Tỷ lệ bóng trên phiên trước |
| `clv_lag1` | float | Close Location Value phiên trước |
| `ibs_lag1` | float | Internal Bar Strength phiên trước |
| `rsi_medium_lag1` | float | RSI medium phiên trước |
| `rsi_medium_delta` | float | Độ dốc/Gia tốc RSI medium (rsi_medium - rsi_medium_lag1) |
| `macd_hist_lag1` | float | MACD Histogram phiên trước |
| `macd_hist_delta` | float | Độ dốc/Gia tốc MACD Histogram (macd_hist - macd_hist_lag1) |
| `kdj_j_lag1` | float | KDJ J phiên trước |
| `ema_fast_lag1` | float | EMA Fast phiên trước |
| `ema_slow_lag1` | float | EMA Slow phiên trước |
| `vwap_lag1` | float | VWAP phiên trước |
| `atr_medium_lag1` | float | ATR medium phiên trước |
| `volatility_expansion_ratio` | float | Tỷ lệ bùng nổ biến động thanh nến hiện tại so với ATR medium phiên trước |
| `bbw_lag1` | float | Độ rộng băng Bollinger phiên trước |
| `volume_avg_lag1` | float | Khối lượng trung bình phiên trước |
| `volume_ratio_lag1` | float | Tỷ lệ khối lượng phiên hiện tại so với phiên trước |

---

## 11. Mixed / Advanced Indicators — `mix.py`

| Column | Type | Description |
|---|---|---|
| `ibs_n` | float | ibs_n = (close - lowest(n)) / (highest(n) - lowest(n)) with n = IBS_LOOKBACK |
| `is_fvg` | bool | is_fvg = True if (high_prev > low_curr) or (low_prev < high_curr) else False |
| `ulti_osci` | float | Ultimate Oscillator = ta.ultimate_oscillator(high, low, close, length=n) with n = VOLATILITY_LOOKBACK |
| `vwap` | float | vwap = ta.vwap(high, low, close, volume) |
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
| `true_range_pct` | float | True range divided by Close |
| `gap_pct` | float | (Open - previous Close) / previous Close |
| `range_position` | float | (Close - Low) / (High - Low) |
| `body_to_true_range` | float | Absolute candlestick body divided by true range |
| `keltner_position` | float | (Close - EMA(Close,n) + 2 * ATR) / (4 * ATR) adapted from quant-ohlcv-feature |
| `fear_greed_yidai_v1` | float | Weighted momentum of bullish and bearish true-range amplitudes |
| `damaov10` | float | Coppock, Bollinger width, and ATR composite |
| `cvr_v0` | float | Cumulative return over rolling return volatility multiplied by relative quote volume |
| `cbr_v1` | float | Coppock-style momentum multiplied by Bollinger bandwidth and price-volume correlation |
| `fbnq_pct_v5` | float | Fibonacci EMA momentum percent change multiplied by average Bollinger bandwidth |
| `price_volume_resist` | float | Close-to-volume breakout difficulty ratio normalized by window length |
| `adx_mtm` | float | Positive directional movement multiplied by rolling momentum |
| `adx_mtm_neg` | float | Negative directional movement multiplied by rolling momentum |
| `mtam` | float | Momentum times taker buy ratio times ATR volatility composite |
| `msbt` | float | Momentum, std momentum, BBW, and taker buy composite |
| `copp_atr_bull` | float | Coppock momentum times ATR times taker buy activity |
| `connors_rsi` | float | ConnorsRSI indicator (RSI(3) + StreakRSI(2) + PriceRank) |

---

## 12. Group / Pattern Features — `group.py`

| Column | Type | Description |
|---|---|---|
| `volume_group` | str | volume_group = comapre(Volume, vol_lag1) = VolUp \| Voldown |
| `upper_wick_group` | str | upper_wick_group = compare(upper_wick, prev_upper_wick) = Increase \| Not Increase |
| `lower_wick_group` | str | lower_wick_group = compare(lower_wick, prev_lower_wick) = Longer \| Shorter |
| `lower_shadow_group` | str | compare(lowwick, prev_lowwick) = Increase \| Not Increase |
| `vol_high_pattern` | str | vol_high_pattern = compare(Volume, vol_lag1) + compare(High, high_lag1) = VolUp_HighUp \| VolUp_HighDown \| VolDown_HighUp \| VolDown_HighDown |
| `ibs_volume_pattern` | str | ibs_volume_group = compare(Volume, vol_lag1) + compare(IBS, ibs_lag1) = VolUp_IBSUp \| VolUp_IBSDown \| VolDown_IBSUp \| VolDown_IBSDown |
| `volume_avg_group` | str | compare(volume_avg, prev_volume_avg) = Increase \| Not Increase |
| `high_rsi_pattern` | str | high_rsi_pattern = compare(High, high_lag1) + compare(RSI, rsi_lag1) = HighUp_RSIUp \| HighUp_RSIDown \| HighDown_RSIUp \| HighDown_RSIDown |
| `high_ub_pattern` | str | high_ub_pattern = compare(High, ub) = HighAboveUB \| HighBelowUB |
| `low_lb_pattern` | str | low_lb_pattern = compare(Low, lb) = LowAboveLB \| LowBelowLB |
| `equal_low` | bool | Low is approximately equal to low_lag1 within 0.1 percent of Close |
| `equal_high` | bool | High is approximately equal to high_lag1 within 0.1 percent of Close |
| `inside_bar_prev` | bool | Previous bar high-low range is inside the bar before it |
| `is_max_micro` | bool | High is higher than the max High of the previous micro lookback bars |
| `is_max_short` | bool | True if High is greater than maximum High of previous short lookback bars |
| `is_min_short` | bool | True if Low is less than minimum Low of previous short lookback bars |
| `mfi_group` | str | compare(MFI, prev_MFI) = Increase \| Not Increase |
| `higher_high_lower_vol` | bool | High > high_lag1 AND Volume < volume_lag1 |
| `lower_low_lower_vol` | bool | Low < low_lag1 AND Volume < volume_lag1 |
| `volume_higher_avg` | bool | Volume > volume_avg |
| `volume_vs_prev_vol` | str | compare(Volume, volume_lag1) = Increase \| Not Increase |
| `close_price_group` | str | > prev High \| Bong nen tren \| Than nen \| Bong nen duoi \| < prev Low |
| `open_price_group` | str | Open > prev_Close \| Open = prev_Close \| Open < prev_Close |
| `high_position` | str | > upper BB \| < upper BB |
| `bb_rejection` | bool | High > ub AND Close < ub |
| `low_position` | str | > lower BB \| <= lower BB |
| `ibs_vol_group` | str | Vol up, ibs incre \| Vol up, ibs decr \| Vol down, ibs incre \| Vol down, ibs decr |
| `rsi_area` | str | >55 \| <45 \| 45-55 |
| `long_trend` | str | StrongUp \| StrongDown = EMA_1month > EMA_6months \| EMA_1month < EMA_6months |

---
