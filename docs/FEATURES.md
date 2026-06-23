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

---

## 5. Volume — `volume.py`

| Column | Type | Description |
|---|---|---|
| `volume_avg` | float | Trung bình khối lượng n phiên |
| `volume_zscore` | float | Z-score khối lượng |

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
| `upwick_lag1` | numerical |  |
| `lowwick_lag1` | numerical |  |
| `prev_ema_fast` | numerical |  |
| `prev_ema_slow` | numerical |  |
| `ibs_lag1` | numerical |  |
| `rsi_lag1` | numerical |  |

---

## 7. Mixed / Advanced Indicators — `mix.py`

| Column | Type | Description |
|---|---|---|
| `ibs_n` | float | ibs_n = (close - lowest(n)) / (highest(n) - lowest(n)) with n = IBS_LOOKBACK |
| `is_fvg` | bool | is_fvg = True if (high_prev > low_curr) or (low_prev < high_curr) else False |
| `ulti_osci` | float | Ultimate Oscillator = ta.ultimate_oscillator(high, low, close, length=n) with n = VOLATILITY_LOOKBACK |
| `vwap` | float | vwap = ta.vwap(high, low, close, volume) |
| `atr` | float | atr = ta.atr(high, low, close, length=n) with n = VOLATILITY_LOOKBACK |
| `adx` | float | adx = ta.adx(high, low, close, length=n) with n = ADX_VOLATILITY_LOOKBACKLOOKBACK |
| `dm` | float | dm = (High + Low) / 2 - (high_lag1 + low_lag1) / 2 |
| `eom` | float | eom = dm / vbr |
| `direction` | int | direction = 1 if close > open else -1 |
| `streak` | int | up_streak = 0 if direction != direction_lag1 else direction + up_streak_lag1 |
| `custom_001` | float | 100 * (Close - prev_day_close) / prev_day_close |
| `custom_002` | float | (Close - close.shift(n)) / (High.rolling(n).max() - Low.rolling(n).min()) with n = ONE_DAY_BARS |

---

## 8. Group / Pattern Features — `group.py`

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

## 9. Signals — `signal.py`

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
