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
| `trade_date` | datetime | Normalized trading date from the timestamp index |
| `bar_in_day` | int | Zero-based bar number within each trading day |
| `session_0930_1335` | bool | True when time_int is between 09:30 and 13:35 inclusive |
| `session_0935_1425` | bool | True when time_int is between 09:35 inclusive and 14:25 exclusive |
| `session_0935_1335` | bool | True when time_int is between 09:35 and 13:35 inclusive |
| `late_session_1325` | bool | True for 13:25, 13:40, and 13:55 bars |
| `late_session_1310` | bool | True for 13:10, 13:25, 13:40, and 13:55 bars |
| `entry_window_1300_1425` | bool | True when time_int is between 13:00 and 14:25 inclusive |

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
| `prev_trading_day_close` | float | Completed previous trading day's close |
| `prev_trading_day_high` | float | Completed previous trading day's high |
| `prev_trading_day_low` | float | Completed previous trading day's low |
| `prev_day_r1` | float | Pivot resistance R1 from completed previous trading day |
| `prev_day_s1` | float | Pivot support S1 from completed previous trading day |
| `prev_day_ema_bias_20` | int | Previous trading day close versus its 20-day EMA, encoded as 1, -1, or 0 |
| `prev_15m_open` | float | Open price of completed 15-minute bar |
| `prev_15m_high` | float | High price of completed 15-minute bar |
| `prev_15m_low` | float | Low price of completed 15-minute bar |
| `prev_15m_close` | float | Close price of completed 15-minute bar |
| `prev_15m_volume` | float | Volume of completed 15-minute bar |
| `prev_15m_pivot` | float | Pivot point of completed 15-minute bar |
| `prev_15m_r1` | float | Pivot resistance R1 of completed 15-minute bar |
| `prev_15m_s1` | float | Pivot support S1 of completed 15-minute bar |
| `prev_15m_return` | float | Return ratio of completed 15-minute bar |
| `prev_15m_ema_bias_20` | int | Completed 15-minute close versus its 20-period EMA, encoded as 1, -1, or 0 |
| `prev_30m_open` | float | Open price of completed 30-minute bar |
| `prev_30m_high` | float | High price of completed 30-minute bar |
| `prev_30m_low` | float | Low price of completed 30-minute bar |
| `prev_30m_close` | float | Close price of completed 30-minute bar |
| `prev_30m_volume` | float | Volume of completed 30-minute bar |
| `prev_30m_pivot` | float | Pivot point of completed 30-minute bar |
| `prev_30m_r1` | float | Pivot resistance R1 of completed 30-minute bar |
| `prev_30m_s1` | float | Pivot support S1 of completed 30-minute bar |
| `prev_30m_return` | float | Return ratio of completed 30-minute bar |
| `prev_30m_ema_bias_20` | int | Completed 30-minute close versus its 20-period EMA, encoded as 1, -1, or 0 |
| `prev_1h_open` | float | Open price of completed 1-hour bar |
| `prev_1h_high` | float | High price of completed 1-hour bar |
| `prev_1h_low` | float | Low price of completed 1-hour bar |
| `prev_1h_close` | float | Close price of completed 1-hour bar |
| `prev_1h_volume` | float | Volume of completed 1-hour bar |
| `prev_1h_pivot` | float | Pivot point of completed 1-hour bar |
| `prev_1h_r1` | float | Pivot resistance R1 of completed 1-hour bar |
| `prev_1h_s1` | float | Pivot support S1 of completed 1-hour bar |
| `prev_1h_return` | float | Return ratio of completed 1-hour bar |
| `prev_1h_ema_bias_20` | int | Completed 1-hour close versus its 20-period EMA, encoded as 1, -1, or 0 |

---

## 3. VN30F1M Specific Features — `vn30f1m.py`

| Column | Type | Description |
|---|---|---|
| `vn30_is_ato` | bool | True during VN30F1M ATO opening call auction (08:45-09:00) |
| `vn30_is_atc` | bool | True during VN30F1M ATC closing call auction (14:30-14:45) |
| `vn30_session_morning` | bool | True during VN30F1M morning trading session (08:45-11:30) |
| `vn30_session_afternoon` | bool | True during VN30F1M afternoon trading session (13:00-14:45) |
| `vn30_pre_market_lead` | bool | True when VN30F1M trades before underlying spot market open (08:45-09:00) |
| `vn30_session_0930_1335` | bool | True when time_int is between 09:30 and 13:35 inclusive |
| `vn30_session_0935_1425` | bool | True when time_int is between 09:35 inclusive and 14:25 exclusive |
| `vn30_session_0935_1335` | bool | True when time_int is between 09:35 and 13:35 inclusive |
| `vn30_late_session_1325` | bool | True for 13:25, 13:40, and 13:55 bars |
| `vn30_late_session_1310` | bool | True for 13:10, 13:25, 13:40, and 13:55 bars |
| `vn30_entry_window_1300_1425` | bool | True when time_int is between 13:00 and 14:25 inclusive |
| `vn30_session_progress` | float | Normalized progression of VN30F1M daily trading hours (0.0 to 1.0) |
| `vn30_is_expiration_day` | bool | True if trade date is the 3rd Thursday of the month (VN30F1M contract settlement day) |
| `vn30_is_expiration_week` | bool | True if current trading week contains the VN30F1M contract expiration day |
| `vn30_is_expiry_settlement_window` | bool | True during the settlement price calculation window (14:00-14:45) on expiration day |
| `vn30_days_to_expiration` | int | Number of calendar days remaining until current monthly contract expiration |
| `vn30_opening_gap` | float | Percentage gap between session open price and previous day close price |
| `vn30_orb_15m_high` | float | High price of the first 15 minutes of the trading session |
| `vn30_orb_15m_low` | float | Low price of the first 15 minutes of the trading session |
| `vn30_orb_15m_range` | float | Range (High - Low) of the first 15 minutes of the trading session |
| `vn30_orb_15m_breakout` | int | 1 if close breaks above 15m ORB high, -1 if below 15m ORB low, 0 otherwise |
| `vn30_orb_30m_high` | float | High price of the first 30 minutes of the trading session |
| `vn30_orb_30m_low` | float | Low price of the first 30 minutes of the trading session |
| `vn30_orb_30m_range` | float | Range (High - Low) of the first 30 minutes of the trading session |
| `vn30_orb_30m_breakout` | int | 1 if close breaks above 30m ORB high, -1 if below 30m ORB low, 0 otherwise |
| `vn30_late_session_range_pos` | float | Position of current close within session cumulative low-high range (0.0 to 1.0) |
| `first_close_0915` | float | First Close value at 09:15 for the current trading day |
| `pre_1345_high` | float | Maximum High before 13:45 for the current trading day |
| `pre_1355_low` | float | Minimum Low before 13:55 for the current trading day |
| `prev_day_1445_close` | float | Previous trading day's 14:45 close, falling back to previous completed close |
| `morning_high` | float | Current trading day's High through time_int <= 1100 |
| `morning_low` | float | Current trading day's Low through time_int <= 1100 |
| `morning_mid` | float | Midpoint between morning_high and morning_low |

---

## 4. Candlestick Geometry — `candlestick.py`

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
| `vbr` | float | vbr = Volume / (High - Low) |
| `ibs` | float | ibs = (close - low) / (high - low) |
| `color` | str | color |
| `wick_imbalance` | float | wick imbalance = upper wick - lower wick |
| `upwick_ratio` | float | upwick_ratio = upwick / (lowwick + epsilon) |
| `fractal_high` | float | Fractal high detected with a 5-bar window |
| `fractal_low` | float | Fractal low detected with a 5-bar window |
| `fractal_high_ffill` | float | Fractal high (5-bar window) forward-filled for signal generation |
| `fractal_low_ffill` | float | Fractal low (5-bar window) forward-filled for signal generation |
| `body_abs` | float | Absolute candlestick body length |
| `body_abs_sma20` | float | 20-bar simple moving average of absolute body length |
| `range_sma20` | float | 20-bar simple moving average of High minus Low |
| `candle_range_ratio` | float | Absolute body divided by High minus Low |
| `heikin_ashi_close` | float | (Open + High + Low + Close) / 4 |
| `heikin_ashi_open` | float | Previous bar Open and Close midpoint |
| `heikin_ashi_bull` | bool | True when heikin_ashi_close is greater than heikin_ashi_open |
| `bullish_high_break_candle` | bool | Bullish candle with High above previous High and Close below the bar High by at least 0.1 |
| `bearish_low_break_candle` | bool | Bearish candle with Low below previous Low and Close above the bar Low by at least 0.1 |

---

## 5. Close Price Indicators — `close.py`

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
| `do` | float | Double-smoothed RSI variant |
| `po` | float | Percent oscillator from short and long EMAs |
| `cci_magic` | float | Smoothed CCI variant using MA of OHLC prices |
| `cs_mtm` | float | Composite momentum: close momentum x std momentum x volume momentum |
| `cs_mtm_v2` | float | Composite momentum using close momentum, std momentum, and quote-volume momentum |
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
| `bias36ma` | float | Rolling mean of the 3-period minus 6-period close MA spread |
| `bir` | float | Four-price average breakout pressure over rolling extrema |
| `copp_v3` | float | Coppock-style average of N and 1.618N close rates of change |
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
| `mtmmean_v12` | float | MTM weighted by taker-buy volume ratio and averaged over a rolling window |
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
| `stoch_rsi` | float | Stochastic RSI of Close |
| `awesome_oscillator` | float | Awesome Oscillator (5-34) |
| `roc10` | float | Rate of change over 10 periods |
| `ultimate_osc` | float | Ultimate Oscillator (7-14-28) |
| `stochrsi_k` | float | StochRSI K line |
| `stochrsi_d` | float | StochRSI D line |
| `price_change` | float | One-bar difference of Close |
| `price_change_lag1` | float | Previous value of price_change |
| `return_5` | float | Close percent change over 5 bars |
| `return_10` | float | Close percent change over 10 bars |
| `sma20` | float | 20-bar simple moving average of Close |
| `sma50` | float | 50-bar simple moving average of Close |
| `std5` | float | 5-bar rolling standard deviation of Close |
| `std10` | float | 10-bar rolling standard deviation of Close |
| `std20` | float | 20-bar rolling standard deviation of Close |
| `std50` | float | 50-bar rolling standard deviation of Close |
| `close_min_10` | float | 10-bar rolling minimum of Close |
| `close_max_10` | float | 10-bar rolling maximum of Close |
| `rsi_5` | float | Relative Strength Index over 5 periods |
| `rsi_8` | float | Relative Strength Index over 8 periods |
| `rsi_14` | float | Relative Strength Index over 14 periods |
| `rsi_21` | float | Relative Strength Index over 21 periods |
| `williams_r_14` | float | Williams %R over 14 periods |
| `bb_percent_b_20_2` | float | Bollinger Band percent B with length 20 and 2 standard deviations |
| `macd_hist_12_26_9` | float | MACD histogram with fast 12, slow 26, signal 9 |

---

## 6. Price Derived Indicators — `price.py`

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
| `avgprice` | float | Rolling VWAP normalized within its rolling range |
| `avgpricetohigh` | float | VWAP relative to current high |
| `avgpricetolow` | float | VWAP relative to current low |
| `WVAD` | float | Normalized rolling candle-body volume accumulation |
| `Vwapbias` | float | Rolling VWAP divided by its moving average minus 1 |
| `lowprice` | float | Rolling mean close price |
| `typ` | float | Typical price (H+L+C)/3 |
| `vwap_signal` | float | Typical price relative to rolling VWAP minus 1 |
| `wc` | float | Weighted close EMA ratio |
| `midpoint` | float | Midpoint of High and Low |
| `close_vs_mid` | float | Close minus the High-Low midpoint |
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
| `mom_y` | float | Close percent change versus previous day 14:45 close fallback |
| `body_rate_first_close` | float | Close minus first_close_0915 divided by pre-13:45 high minus pre-13:55 low |
| `opening_gap_pct` | float | First 09:15 close versus previous day 14:45 close fallback, percent |
| `session_vwap` | float | Running session VWAP from Close and Volume |
| `session_vwap_std` | float | Running volume-weighted standard deviation around session_vwap |
| `session_vwap_upper_1_5` | float | session_vwap plus 1.5 session_vwap_std |
| `session_vwap_lower_1_5` | float | session_vwap minus 1.5 session_vwap_std |
| `session_vwap_z` | float | Close minus session_vwap divided by session_vwap_std |
| `session_vwap_dev_pct` | float | Close deviation from session_vwap divided by Close, percent |
| `morning_breakout_long` | float | Close minus morning_high divided by morning range |

---

## 7. Trend Indicators — `trend.py`

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
| `reg` | float | Close divided by rolling linear regression minus 1 |
| `reg_v2` | float | Percentage deviation of Close from a 2N rolling regression line |
| `reg_v3` | float | Close divided by rolling OLS regression fit minus 1 |
| `diff_ema` | float | Difference between short and long EMAs |
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
| `ic_v2` | float | Close relative to the Ichimoku cloud span boundaries |
| `ic_v3` | float | Normalized Ichimoku cloud thickness |
| `ic_v4` | float | Normalized close position inside the Ichimoku cloud |
| `adxrpos` | float | Smoothed positive directional movement component |
| `dema` | float | Double exponential moving average normalized by its EMA baseline |
| `tema` | float | Triple exponential moving average normalized by its EMA baseline |
| `hlma` | float | High-low moving average spread normalized by its own mean |
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
| `hma20` | float | Hull Moving Average over 20 periods |
| `kama10` | float | Kaufman Adaptive Moving Average over 10 periods |
| `trix15` | float | TRIX indicator over 15 periods |
| `trix15_signal` | float | TRIX 15 signal line |
| `supertrend_dir` | float | SuperTrend direction component |
| `tenkan` | float | Ichimoku Tenkan-sen component |
| `kijun` | float | Ichimoku Kijun-sen component |
| `span_a` | float | Ichimoku Senkou Span A component |
| `span_b` | float | Ichimoku Senkou Span B component |
| `linreg_slope20` | float | Linear regression slope over 20 periods |
| `linreg_mid20` | float | Linear regression midline over 20 periods |
| `tma10` | float | Triangular Moving Average over 10 periods |
| `linreg_upper20` | float | linreg_mid20 plus two times std20 |
| `linreg_lower20` | float | linreg_mid20 minus two times std20 |
| `high_5` | float | 5-bar rolling maximum of High |
| `low_5` | float | 5-bar rolling minimum of Low |
| `high_10` | float | 10-bar rolling maximum of High |
| `low_10` | float | 10-bar rolling minimum of Low |
| `high_20` | float | 20-bar rolling maximum of High |
| `low_20` | float | 20-bar rolling minimum of Low |
| `range_mid_10` | float | Midpoint between high_10 and low_10 |
| `recent_high` | float | 20-bar rolling High shifted by one bar |
| `recent_low` | float | 20-bar rolling Low shifted by one bar |
| `recent_high_prev` | float | recent_high shifted by 5 bars |
| `recent_low_prev` | float | recent_low shifted by 5 bars |
| `prev_5_low` | float | low_5 shifted by one bar |
| `prev_5_high` | float | high_5 shifted by one bar |
| `prev_10_low` | float | low_10 shifted by one bar |
| `prev_10_high` | float | high_10 shifted by one bar |
| `prev_20_low` | float | low_20 shifted by one bar |
| `prev_20_high` | float | high_20 shifted by one bar |
| `lower_range_pos` | float | 30 percent level above low_10 within the 10-bar high-low range |
| `upper_range_pos` | float | 30 percent level below high_10 within the 10-bar high-low range |
| `ema_8` | float | Exponential moving average of Close over 8 periods |
| `ema_20` | float | Exponential moving average of Close over 20 periods |
| `ema_21` | float | Exponential moving average of Close over 21 periods |
| `ema_55` | float | Exponential moving average of Close over 55 periods |
| `ema_250` | float | Exponential moving average of Close over 250 periods |
| `ema_20_cross_above_ema_250` | bool | True when EMA 20 crosses above EMA 250 on the current bar |
| `ema_20_cross_below_ema_250` | bool | True when EMA 20 crosses below EMA 250 on the current bar |
| `adx_14` | float | Average Directional Index over 14 periods |
| `adx_42` | float | Average Directional Index over 42 periods |
| `dmp_14` | float | Positive directional movement over 14 periods |
| `dmn_14` | float | Negative directional movement over 14 periods |
| `psar_bull` | bool | True when Parabolic SAR indicates a bullish leg |
| `psar_bear` | bool | True when Parabolic SAR indicates a bearish leg |
| `linear_regression_slope_5` | float | Linear regression slope of Close over 5 periods |
| `linear_regression_slope_8` | float | Linear regression slope of Close over 8 periods |

---

## 8. Volatility Indicators — `volatility.py`

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
| `atr_pct` | float | ATR divided by close |
| `rwi_high` | float | RWI high component based on upward range |
| `rwi_low` | float | RWI low component based on downward range |
| `bbw_signal` | float | Bollinger bandwidth change times n-period momentum and RSI-like close pressure |
| `kc_signal` | float | Close position inside Keltner channel using ATR bands |
| `atr_upper` | float | ATR-based upper channel ratio normalized by moving average |
| `atr_lower` | float | ATR-based lower channel ratio normalized by moving average |
| `fb_upper_signal` | float | Close position relative to Fibonacci upper ATR band |
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
| `bolling` | float | Bollinger breakout distance normalized by standard deviation |
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
| `bb_width` | float | Standard Bollinger Band Width used for signals |
| `kc_mid` | float | Keltner Channel mid line (EMA 20) |
| `kc_upper` | float | Keltner Channel upper band (mid + 2 * ATR) |
| `kc_lower` | float | Keltner Channel lower band (mid - 2 * ATR) |
| `chop14` | float | Choppiness Index over 14 periods |
| `hurst_proxy` | float | Hurst Exponent Proxy over 20 periods |
| `bb_width_q20` | float | 100-bar rolling 20th percentile of bb_width |
| `bb_width_sma20` | float | 20-bar simple moving average of bb_width |
| `atr_sma20` | float | 20-bar simple moving average of atr |
| `atr_14` | float | Average True Range over 14 periods |
| `body_atr_ratio` | float | Close minus Open divided by ATR 14 |
| `keltner_upper_20_2` | float | Keltner upper band with length 20 and scalar 2 |
| `keltner_lower_20_2` | float | Keltner lower band with length 20 and scalar 2 |
| `donchian_high_10_shift1` | float | 10-bar rolling High maximum shifted one bar |
| `donchian_low_10_shift1` | float | 10-bar rolling Low minimum shifted one bar |
| `donchian_high_30_shift1` | float | 30-bar rolling High maximum shifted one bar |
| `donchian_low_30_shift1` | float | 30-bar rolling Low minimum shifted one bar |
| `close_donchian_high_20_shift1` | float | 20-bar rolling Close maximum shifted one bar |
| `close_donchian_low_20_shift1` | float | 20-bar rolling Close minimum shifted one bar |

---

## 9. Volume — `volume.py`

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
| `ko` | float | Klinger oscillator variant normalized to rolling range |
| `vra` | float | Dual-horizon price ROC multiplied by rolling close volatility |
| `ke` | float | Signed squared n-period price change amplified by normalized volume |
| `roc_volume` | float | Volume / Volume.shift(n) - 1 |
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
| `macdvol` | float | Volume-based MACD normalized by its signal line |
| `volume_reg` | float | Linear regression of quote-volume proxy |
| `volume_tsf` | float | Time series forecast of quote-volume proxy |
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
| `buy_vol_ratio_fancy` | float | Taker-buy quote volume divided by quote volume |
| `taker_by_ratio` | float | Rolling taker-buy quote volume divided by rolling quote volume |
| `taker_by_ratio_per_trade` | float | Taker-buy ratio normalized by rolling trade count |
| `vol_per_trade_fancy` | float | Rolling quote volume divided by rolling trade count |
| `mtm_tb` | float | EMA-smoothed close momentum multiplied by taker-buy pressure |
| `dbcd_taker` | float | DBCD bias oscillator multiplied by taker-buy ratio |
| `mtm_bull` | float | Momentum, ATR, and taker-buy composite |
| `mtm_bear` | float | Momentum, ATR, and taker-sell composite |
| `buy_vwap_div_vwap_fancy` | float | Taker-buy VWAP divided by rolling VWAP |
| `Vramt` | float | Volume ratio based on up, down, and unchanged bars |
| `v1up` | float | Upper adaptive band distance for the V1 composite |
| `v1_v2` | float | V1 momentum-volatility composite using mean-based z-score bands |
| `v1up_v2` | float | Upper adaptive band distance for the V1_v2 composite |
| `v1dn_v2` | float | Lower adaptive band distance for the V1_v2 composite |
| `v1dn` | float | Lower adaptive band distance for the V1 composite |
| `Volume` | float | Alias for volume |
| `mfi14` | float | Money Flow Index over 14 periods |
| `vpt` | float | Cumulative Volume Price Trend indicator |
| `volume_sma20` | float | 20-bar simple moving average of Volume |
| `signed_volume` | float | Volume signed by candle direction with Close diff fallback |
| `session_flow_imbalance` | float | Running signed_volume divided by running session Volume |

---

## 10. Liquidity / Composite Proxies — `liquidity.py`

| Column | Type | Description |
|---|---|---|
| `market_placement` | float | Close relative to EMA quote-volume/volume holding-cost proxy |
| `path_liquidity` | float | Rolling quote-volume proxy per normalized shortest intrabar price path |
| `spread_proxy` | float | Rolling mean log high-low range as an OHLC bid-ask spread proxy |
| `spread_volatility_ratio` | float | spread_proxy divided by rolling close-return volatility |
| `price_volume_resistance` | float | Price move magnitude per volume move magnitude adapted from PriceVolumeResist |
| `coppock_atr_volume` | float | Coppock momentum multiplied by normalized ATR and volume pressure |
| `bidask_spread` | float | Rolling bid-ask spread estimate from OHLC prices |
| `market_placement_v2` | float | VWAP-validity checked market placement proxy |
| `liquidity_v3` | float | Volume divided by log spread and return volatility proxy |
| `amihud` | float | Amihud illiquidity proxy using intraday shortest price path |

---

## 11. Lag Features — `lag.py`

| Column | Type | Description |
|---|---|---|
| `open_lag1` | float | Open phiên trước |
| `high_lag1` | float | High phiên trước |
| `low_lag1` | float | Low phiên trước |
| `close_lag1` | float | Close phiên trước |
| `volume_lag1` | float | Volume phiên trước |
| `body_lag1` | float | Body phiên trước |
| `upwick_lag1` | float | Bóng trên phiên trước |
| `lowwick_lag1` | float | Bóng dưới phiên trước |
| `lowwick_rate_lag1` | float | Tỷ lệ bóng dưới phiên trước |
| `upwick_rate_lag1` | float | Tỷ lệ bóng trên phiên trước |
| `clv_lag1` | float | Close Location Value phiên trước |
| `ibs_lag1` | float | Internal Bar Strength phiên trước |
| `rsi_lag1` | float | RSI phiên trước |
| `rsi_delta` | float | Độ dốc/Gia tốc RSI (rsi - rsi_lag1) |
| `macd_hist_lag1` | float | MACD Histogram phiên trước |
| `macd_hist_delta` | float | Độ dốc/Gia tốc MACD Histogram (macd_hist - macd_hist_lag1) |
| `kdj_j_lag1` | float | KDJ J phiên trước |
| `ema_fast_lag1` | float | EMA Fast phiên trước |
| `ema_slow_lag1` | float | EMA Slow phiên trước |
| `vwap_lag1` | float | VWAP phiên trước |
| `atr_lag1` | float | ATR phiên trước |
| `volatility_expansion_ratio` | float | Tỷ lệ bùng nổ biến động thanh nến hiện tại so với ATR phiên trước |
| `bbw_lag1` | float | Độ rộng băng Bollinger phiên trước |
| `volume_avg_lag1` | float | Khối lượng trung bình phiên trước |
| `volume_ratio_lag1` | float | Tỷ lệ khối lượng phiên hiện tại so với phiên trước |

---

## 12. Mixed / Advanced Indicators — `mix.py`

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
| `fear_greed_yidai_v1` | float | Weighted momentum of bullish and bearish true-range amplitudes |
| `damaov10` | float | Coppock, Bollinger width, and ATR composite |
| `adx_mtm` | float | Positive directional movement multiplied by rolling momentum |
| `Cvr_v0` | float | Cumulative return over rolling return volatility multiplied by relative quote volume |
| `Cbr_v1` | float | Coppock-style momentum multiplied by Bollinger bandwidth and price-volume correlation |
| `Fbnq_pct_v5` | float | Fibonacci EMA momentum percent change multiplied by average Bollinger bandwidth |
| `PriceVolumeResist` | float | Close-to-volume breakout difficulty ratio normalized by window length |
| `Mtam` | float | Momentum times taker buy ratio times ATR volatility composite |
| `Msbt` | float | Momentum, std momentum, BBW, and taker buy composite |
| `CoppAtrBull` | float | Coppock momentum times ATR times taker buy activity |
| `adx_mtm_neg` | float | Negative directional movement multiplied by rolling momentum |
| `connors_rsi` | float | ConnorsRSI indicator (RSI(3) + StreakRSI(2) + PriceRank) |
| `persist_short_12_shift1` | float | 12-bar rolling share of closes below session_open shifted one bar |
| `accept_long_4_shift1` | float | 4-bar rolling share of closes above morning_mid shifted one bar |

---

## 13. Group / Pattern Features — `group.py`

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
| `equal_low` | bool | Low is approximately equal to low_lag1 within 0.1 percent of Close |
| `equal_high` | bool | High is approximately equal to high_lag1 within 0.1 percent of Close |
| `inside_bar_prev` | bool | Previous bar high-low range is inside the bar before it |

---

## 14. Signals — `signal.py`

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
