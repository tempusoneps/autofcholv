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
| `fractal_high` | float | Fractal high detected with a 5-bar window |
| `fractal_low` | float | Fractal low detected with a 5-bar window |
| `fractal_high_ffill` | float | Fractal high (5-bar window) forward-filled for signal generation |
| `fractal_low_ffill` | float | Fractal low (5-bar window) forward-filled for signal generation |
| `range` | float | High minus Low |
| `body_abs` | float | Absolute candlestick body length |
| `body_abs_sma20` | float | 20-bar simple moving average of absolute body length |
| `range_sma20` | float | 20-bar simple moving average of High minus Low |
| `candle_range_ratio` | float | Absolute body divided by High minus Low |

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
| `Fi` | float | Alias for fi |
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
| `avgprice` | float | Rolling VWAP normalized within its rolling range |
| `avgpricetohigh` | float | VWAP relative to current high |
| `avgpricetolow` | float | VWAP relative to current low |
| `AvgPrice` | float | Alias for avgprice |
| `AvgPriceToHigh` | float | Alias for avgpricetohigh |
| `AvgPriceToLow` | float | Alias for avgpricetolow |
| `LowPrice` | float | Alias for lowprice |
| `Typ` | float | Alias for typ |
| `VwapSignal` | float | Alias for vwap_signal |
| `WVAD` | float | Normalized rolling candle-body volume accumulation |
| `Vwapbias` | float | Rolling VWAP divided by its moving average minus 1 |
| `Vwap` | float | Alias for rolling_vwap |
| `Wc` | float | Alias for wc |
| `lowprice` | float | Rolling mean close price |
| `typ` | float | Typical price (H+L+C)/3 |
| `vwap_signal` | float | Typical price relative to rolling VWAP minus 1 |
| `wc` | float | Weighted close EMA ratio |
| `midpoint` | float | Midpoint of High and Low |
| `close_vs_mid` | float | Close minus the High-Low midpoint |

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
| `adxdip` | float | Source ADX DI+ alias |
| `adxdim` | float | Source ADX DI- alias |
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
| `Mac_v2` | float | Alias for mac_v2 |
| `Mac_v3` | float | Alias for mac_v3 |
| `Mac_v4` | float | Alias for mac_v4 |
| `Mac_v5` | float | Alias for mac_v5 |
| `Vidya_v2` | float | Alias for vidya_v2 |
| `Vidya_v3` | float | Alias for vidya_v3 |
| `Vidya_v4` | float | Alias for vidya_v4 |
| `Vidya_v5` | float | Alias for vidya_v5 |
| `Tma_v2` | float | Alias for tma_v2 |
| `Tma_v3` | float | Alias for tma_v3 |
| `Arron` | float | Alias for arron |
| `Acs` | float | Alias for acs |
| `Mac` | float | Alias for mac |
| `Vidya` | float | Alias for vidya |
| `Tma` | float | Alias for tma |
| `Ma` | float | Alias for ma |
| `Vma` | float | Alias for vma |
| `Mm` | float | Alias for mm |
| `Gap` | float | Alias for gap |
| `Dema` | float | Alias for dema |
| `Tema` | float | Alias for tema |
| `Hma` | float | Alias for hma |
| `Reg` | float | Alias for reg |
| `Reg_v2` | float | Alias for reg_v2 |
| `Reg_v3` | float | Alias for reg_v3 |
| `T3` | float | Alias for t3 |
| `DiffEma` | float | Alias for diff_ema |
| `Adxrpos` | float | Alias for adxr_pos |
| `Adxrneg` | float | Alias for adxr_neg |
| `Expma` | float | Alias for expma |
| `Vi` | float | Alias for vi |
| `Bbi` | float | Alias for bbi |
| `RegTema` | float | Alias for regtema |
| `Turtle` | float | Alias for turtle |
| `MaSignal` | float | Alias for ma_signal |
| `HmaSignal` | float | Alias for hma_signal |
| `HullmaSignal` | float | Alias for hullma_signal |
| `Ic` | float | Alias for ic |
| `Ic_v2` | float | Alias for ic_v2 |
| `Ic_v3` | float | Alias for ic_v3 |
| `Ic_v4` | float | Alias for ic_v4 |
| `Adxr` | float | Alias for adxr |
| `Regema` | float | Alias for regema |
| `Adx` | float | Alias for adx_strength |
| `Dma` | float | Alias for dma |
| `Vi+` | float | Alias for vi_plus |
| `Vi-` | float | Alias for vi_minus |
| `Mak` | float | Alias for mak |
| `Sgcz` | float | Alias for sgcz |
| `Cse` | float | Alias for cse |
| `Trrq` | float | Alias for trrq |
| `Mreg` | float | Alias for mreg |
| `Angle` | float | Alias for angle_reg |
| `AdxDi+` | float | Alias for adx_di_plus |
| `AdxDi-` | float | Alias for adx_di_minus |
| `BbiBias` | float | Alias for bbi_bias |
| `Trv` | float | Alias for trv |
| `PjcDistance` | float | Alias for pjc_distance |
| `Trrq_v3` | float | Alias for trrq_v3 |
| `TrTrix` | float | Alias for trtrix |
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
| `rwih` | float | Random Walk Index high-side measure |
| `rwil` | float | Random Walk Index low-side measure |
| `Bolling` | float | Alias for bolling |
| `Bolling_v2` | float | Alias for bolling_v2 |
| `Bolling_v3` | float | Alias for bolling_v3 |
| `Bolling_fancy` | float | Alias for bolling_fancy |
| `EnvSignal` | float | Alias for env_signal |
| `EnvUpper` | float | Alias for env_upper |
| `EnvLower` | float | Alias for env_lower |
| `KcSignal` | float | Alias for kc_signal |
| `KcUpperSignal` | float | Alias for kc_upper_signal |
| `KcLowerSignal` | float | Alias for kc_lower_signal |
| `VwapBbw` | float | Alias for vwap_bbw |
| `RetBoll_fancy` | float | Alias for ret_boll_fancy |
| `Lchc_fancy` | float | Alias for lchc_fancy |
| `AdaptBollingv3` | float | Alias for adapt_bollingv3 |
| `Bollcount_dem` | float | Alias for bollcount_dem |
| `DzcciLower` | float | Alias for dzcci_lower |
| `DzcciUpper` | float | Alias for dzcci_upper |
| `DzrsiLowerSignal` | float | Alias for dzrsi_lower_signal |
| `DzrsiUpperSignal` | float | Alias for dzrsi_upper_signal |
| `FbLower` | float | Alias for fb_lower |
| `FbUpper` | float | Alias for fb_upper |
| `DzcciLowerSignal` | float | Alias for dzcci_lower_signal |
| `DzcciLowerSignal_v2` | float | Alias for dzcci_lower_signal_v2 |
| `DzcciUpperSignal` | float | Alias for dzcci_upper_signal |
| `DzcciUpperSignal_v2` | float | Alias for dzcci_upper_signal_v2 |
| `FbLowerSignal` | float | Alias for fb_lower_signal |
| `FbLowerSignal_v2` | float | Alias for fb_lower_signal_v2 |
| `FbLowerSignal_v3` | float | Alias for fb_lower_signal_v3 |
| `FbUpperSignal` | float | Alias for fb_upper_signal |
| `FbUpperSignal_v2` | float | Alias for fb_upper_signal_v2 |
| `FbUpperSignal_v3` | float | Alias for fb_upper_signal_v3 |
| `VixBw` | float | Alias for vix_bw |
| `VolumeStd` | float | Alias for volume_std |
| `Grid` | float | Alias for grid |
| `Lcsd` | float | Alias for lcsd |
| `Apz` | float | Alias for apz |
| `ApzUpper` | float | Alias for apz_upper |
| `ApzLower` | float | Alias for apz_lower |
| `Bbw` | float | Alias for bbw |
| `Cv` | float | Alias for cv |
| `Dc` | float | Alias for dc |
| `DcSignal` | float | Alias for dc_signal |
| `Dc_v2` | float | Alias for dc_v2 |
| `EnvUpperSignal` | float | Alias for env_upper_signal |
| `EnvLowerSignal` | float | Alias for env_lower_signal |
| `Rwi` | float | Alias for rwi |
| `RwiH` | float | Alias for rwi_high |
| `RwiL` | float | Alias for rwi_low |
| `Atr` | float | Alias for atr |
| `AtrPct` | float | Alias for atr_pct |
| `AtrUpper` | float | Alias for atr_upper |
| `AtrLower` | float | Alias for atr_lower |
| `Pac` | float | Alias for pac |
| `PacUpper` | float | Alias for pacupper |
| `PacLower` | float | Alias for paclower |
| `PacUpper_v2` | float | Alias for pacupper_v2 |
| `PacLower_v2` | float | Alias for paclower_v2 |
| `Pfe` | float | Direction-signed price efficiency |
| `ChangeStd` | float | N-period return multiplied by rolling return std |
| `bb_width` | float | Standard Bollinger Band Width used for signals |
| `kc_mid` | float | Keltner Channel mid line (EMA 20) |
| `kc_upper` | float | Keltner Channel upper band (mid + 2 * ATR) |
| `kc_lower` | float | Keltner Channel lower band (mid - 2 * ATR) |
| `chop14` | float | Choppiness Index over 14 periods |
| `hurst_proxy` | float | Hurst Exponent Proxy over 20 periods |
| `bb_width_q20` | float | 100-bar rolling 20th percentile of bb_width |
| `bb_width_sma20` | float | 20-bar simple moving average of bb_width |
| `atr_sma20` | float | 20-bar simple moving average of atr |

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
| `Pvo` | float | Alias for pvo |
| `Vramt` | float | Volume ratio based on up, down, and unchanged bars |
| `v1up` | float | Upper adaptive band distance for the V1 composite |
| `v1_v2` | float | V1 momentum-volatility composite using mean-based z-score bands |
| `v1up_v2` | float | Upper adaptive band distance for the V1_v2 composite |
| `v1dn_v2` | float | Lower adaptive band distance for the V1_v2 composite |
| `v1dn` | float | Lower adaptive band distance for the V1 composite |
| `Volume_Bias` | float | Alias for volume_bias |
| `QuoteVolumeMean` | float | Alias for quote_volume_mean |
| `QuoteVolumeRatio` | float | Alias for quote_volume_ratio |
| `VolumeReg` | float | Alias for volume_reg |
| `VolumeTSF` | float | Alias for volume_tsf |
| `TradeNum` | float | Alias for trade_num |
| `BuyVolRatio_fancy` | float | Alias for buy_vol_ratio_fancy |
| `VolPerTrade_fancy` | float | Alias for vol_per_trade_fancy |
| `BuyVwapDivVwap_fancy` | float | Alias for buy_vwap_div_vwap_fancy |
| `TakerByRatio` | float | Alias for taker_by_ratio |
| `TakerByRatioPerTrade` | float | Alias for taker_by_ratio_per_trade |
| `V1` | float | Alias for v1 |
| `V1Up` | float | Alias for v1up |
| `V1Dn` | float | Alias for v1dn |
| `V1_v2` | float | Alias for v1_v2 |
| `V1Up_v2` | float | Alias for v1up_v2 |
| `V1Dn_v2` | float | Alias for v1dn_v2 |
| `Mfi` | float | Alias for mfi |
| `Vr` | float | Alias for vr |
| `Vao` | float | Alias for vao |
| `Vao_v2` | float | Alias for vao_v2 |
| `Volumechg` | float | Alias for volumechg |
| `Wvad` | float | Alias for wvad |
| `QuanlityPriceCorr` | float | Alias for price_volume_corr |
| `Volume` | float | Alias for volume |
| `Force` | float | Alias for force_index |
| `Cmf` | float | Alias for cmf |
| `Obv` | float | Alias for obv |
| `VRA` | float | Alias for vra |
| `Chla_fancy` | float | Alias for chla_fancy |
| `NetVol_fancy` | float | Alias for net_vol_fancy |
| `Amv` | float | Alias for amv |
| `mfi14` | float | Money Flow Index over 14 periods |
| `vpt` | float | Cumulative Volume Price Trend indicator |
| `volume_sma20` | float | 20-bar simple moving average of Volume |

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
| `bidask_spread` | float | Rolling bid-ask spread estimate from OHLC prices |
| `market_placement_v2` | float | VWAP-validity checked market placement proxy |
| `liquidity_v3` | float | Volume divided by log spread and return volatility proxy |
| `amihud` | float | Amihud illiquidity proxy using intraday shortest price path |
| `marketpl` | float | Market placement / average holding cost |
| `marketpl_v2` | float | Market placement with VWAP validity check |
| `MarketPl` | float | Alias for marketpl |
| `MarketPl_v2` | float | Alias for marketpl_v2 |
| `Liquidity_v3` | float | Alias for liquidity_v3 |
| `Amihud` | float | Alias for amihud |
| `BidaskSpread` | float | Alias for bidask_spread |

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
| `Damaov10` | float | Alias for damaov10 |
| `FearGreed_Yidai_v1` | float | Alias for fear_greed_yidai_v1 |
| `connors_rsi` | float | ConnorsRSI indicator (RSI(3) + StreakRSI(2) + PriceRank) |

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
| `equal_low` | bool | Low is approximately equal to low_lag1 within 0.1 percent of Close |
| `equal_high` | bool | High is approximately equal to high_lag1 within 0.1 percent of Close |
| `inside_bar_prev` | bool | Previous bar high-low range is inside the bar before it |

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
