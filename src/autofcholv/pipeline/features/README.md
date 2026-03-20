## 📊 Extracted Features Catalog

The extraction pipeline runs through several stages. Below is a comprehensive list of the features added to your DataFrame:

### 1. Time Features (`time.py`)
*   `hour`, `minute`, `day_of_month`, `month`, `year`: Extracted directly from the DatetimeIndex.
*   `session_progress`: Tracks the percentage progress of the intraday trading session.

### 2. Daily Resampling Features (`resample.py`)
*If your data is intraday (e.g. 5-minute), these aggregate the day's total behavior and align them to the current bar.*
*   `day_high`, `day_low`, `day_close`, `day_open`, `day_vol`, `day_pivot`
*   `prev_day_close`, `prev_day_open`, `prev_day_high`, `prev_day_low`, `prev_day_vol`, `prev_day_pivot`: Yesterday's daily aggregate stats mapped to today's bars.

### 3. Candlestick Geometry (`candlestick.py`)
*   `cs_body`: Close - Open (positive for green, negative for red).
*   `cs_height`: High - Low (total span).
*   `cs_upwick`, `cs_lowwick`: Absolute sizes of the upper and lower shadows.
*   `cs_upwick_rate`, `cs_lowwick_rate`: Wick sizes expressed as a percentage of the total candlestick height.
*   `cs_ibs`: Internal Bar Strength, measures where the close sits relative to the High/Low range.
*   `cs_color`: Categorical marking (`'green'`, `'red'`, `'doji'`).

### 4. Close Price Indicators (`close.py`)
*   `EMA20`, `EMA250`: Exponential Moving Average for 20 and 250 periods.
*   `MB`, `STD`, `UB`, `LB`: Standard Bollinger Bands (length 20, multiplier 1.5).
*   `RSI10`, `RSI20`: Relative Strength Indexes.

### 5. Mixed & Advanced Indicators (`mix.py`)
*   **Patterns**: 
    *   `is_fvg`: Boolean for Fair Value Gaps.
    *   `is_lower_low_higher_volume`: Bearish distribution warning flag.
    *   `up_streak`, `down_streak`: Consecutive monotonic runs.
*   **Momentum & Volatility**: 
    *   `VWAP`: Volume Weighted Average Price (resets daily).
    *   `ATR14`: Average True Range.
    *   `ADX14`: Average Directional Index.
    *   `z_score`: Close relative to Bollinger Bands.
    *   `typical_price`: Typical pivot price `(H+L+C)/3`.
    *   `DM`, `VBR`, `EOM`: Distance Moved, Volume Box Ratio, and Ease of Movement.
    *   `keltner_channel`: Upper Keltner limit (`EMA20 + ATR14`).
    *   `parkinson_vol_20`: High/Low based variance estimation.
*   **Advanced Mathematics**:
    *   `hurst_exponent` (10 window), `hurst_exponent_100` (100 window): Uses rescaled range (R/S) analysis to measure the long-term memory/mean-reversion property of the time series.
*   **Custom Formulations**:
    *   `cs_ibs_n`: Internal Bar Strength calculated over a custom time lookback `n` (`ONE_DAY_BARS`).
    *   `fea_g1_001`: Percentage change relative to the previous day's close.
    *   `fea_g1_002`: Specialized momentum metric spanning 49 periods.
