# Feature Data Leakage (Lookahead Bias) Evaluation Report

This report evaluates the feature engineering pipeline in `autofcholv` to identify features that use future data (lookahead bias/leakage) for current calculations.

We programmatically simulated real-time inference by mutating OHLCV data at a specific future timestamp and observing which past feature values changed. This isolated **true lookahead leakages** and categorized them below.

---

## Summary of Leakage Categories

| Category | Leakage Type | Affected Features | Root Cause |
| :--- | :--- | :--- | :--- |
| **1. Session & Morning Ranges** | Intra-day Lookahead | `pre_1345_high`, `pre_1355_low`, `morning_high`, `morning_low`, `morning_mid`, `body_rate_first_close`, `morning_breakout_long`, `accept_long_4_shift1` | Mapping daily aggregated values (e.g. highs before 13:45 or up to 11:00) backward to earlier times in the day before they are finalized. |
| **2. Global Percentiles** | Dataset-wide Lookahead | `vbr`, `eom` | Using `.quantile(0.99)` on the entire dataset's `Volume` series, making historical features depend on future volume extremes. |
| **3. Bill Williams Fractals** | Future Window Lookahead | `fractal_low`, `fractal_low_ffill`, `fractal_high`, `fractal_high_ffill`, `zig_zag_reversal_signal`, `fractal_channel_signal`, `signal_pro4` | Using future shifts (`shift(-1)` and `shift(-2)`) to identify fractals at the current bar without a corresponding delay shift. |
| **4. Negative Shifts** | Explicit Lookahead | `volume_tsf` | Using `.shift(-1)` to shift a rolling average backward into the past. |

---

## Detailed Analysis & Remediation Strategies

### 1. Session & Morning Ranges (Intra-day Lookahead)
* **Files**: 
  * [resample.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/resample.py#L84-L107)
  * [price.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/price.py#L117-L138)
  * [mix.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/mix.py#L280)
* **Mechanism**:
  `_daily_time_value` groups by date and computes a single daily statistic (such as first close at 09:15, or highest high before 13:45). It then maps this value to the entire day's bars:
  ```python
  daily = data[column].groupby(trade_date).agg(aggregate)
  return pd.Series(trade_date, index=data.index).map(daily)
  ```
  This means that at `09:05:00`, the model already has the value of `first_close_0915` (which occurs 10 minutes later) and `pre_1345_high` (which occurs up to 4.5 hours later).
  Similarly, `morning_high` and `morning_low` (high/low before 11:00) are mapped to all bars from 09:00 onwards.
  *Downstream features* like `body_rate_first_close`, `morning_breakout_long`, and `accept_long_4_shift1` inherit this lookahead bias.

* **Remediation**:
  To prevent lookahead bias, these daily values must only be populated/known **after** the time window has closed. Before the window closes, they should remain `NaN`.
  * **Fix for morning high/low** in `resample.py`:
    ```python
    morning_high_val = merged_data["High"].where(time_int <= 1100).groupby(trade_date).transform("max")
    merged_data["morning_high"] = np.where(time_int > 1100, morning_high_val, np.nan)
    ```
  * **Fix for `_daily_time_value`** in `resample.py`:
    ```python
    # Ensure value is only mapped to timestamps strictly greater than or equal to the hhmm cutoff
    mapped_daily = pd.Series(trade_date, index=data.index).map(daily)
    return np.where(time_int >= hhmm, mapped_daily, np.nan)
    ```

---

### 2. Global Percentiles (Dataset-wide Lookahead)
* **Files**: 
  * [candlestick.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/candlestick.py#L58-L60)
  * [mix.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/mix.py#L67)
* **Mechanism**:
  `vbr` is clipped using a quantile calculated across the *entire* dataset:
  ```python
  df['vbr'] = (df['Volume'] / (height_safe + epsilon)).clip(0, df['Volume'].quantile(0.99))
  ```
  Since `df['Volume'].quantile(0.99)` is a single scalar computed globally, changing a volume spike in the future (e.g. at bar 4000) changes the 99th percentile, which changes the clipped value of `vbr` at bar 0. `eom` is calculated from `vbr` and thus also leaks.

* **Remediation**:
  Use a rolling quantile instead of a global quantile, or use a pre-calculated constant:
  ```python
  # Clip using a rolling 200-bar quantile
  rolling_q99 = df['Volume'].rolling(window=200, min_periods=1).quantile(0.99)
  df['vbr'] = (df['Volume'] / (height_safe + epsilon)).clip(0, rolling_q99)
  ```

---

### 3. Bill Williams Fractals (Future Window Lookahead)
* **Files**: 
  * [candlestick.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/candlestick.py#L84-L103)
  * [signal.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/signal.py#L284)
  * [signal.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/signal.py#L297)
* **Mechanism**:
  `fractal_high` and `fractal_low` look at `shift(-1)` and `shift(-2)` to check if the current bar is higher/lower than the next two bars:
  ```python
  & (df["High"] > df["High"].shift(-1))
  & (df["High"] > df["High"].shift(-2))
  ```
  A fractal at bar `t` is only physically confirmed at bar `t+2`. However, the raw `fractal_high` and `fractal_low` are exposed in `candlestick.py` at bar `t`. 
  In `signal.py`, `zig_zag_reversal_signal` and `fractal_channel_signal` use these features directly without a delay, leaking future data.

* **Remediation**:
  * For raw fractal indicators, they should either be documented as lookahead targets (if intended for target labeling) or shifted by 2 bars to be non-leaking.
  * In `signal.py`, the signals must be computed on the shifted versions:
    ```python
    df["zig_zag_reversal_signal"] = _signal_from_conditions(
        df["fractal_low"].shift(2).notna(), 
        df["fractal_high"].shift(2).notna()
    )
    df["fractal_channel_signal"] = _signal_from_conditions(
        df["Close"] > df["fractal_high_ffill"].shift(2), 
        df["Close"] < df["fractal_low_ffill"].shift(2)
    )
    ```

---

### 4. Negative Shifts (Explicit Lookahead)
* **Files**: 
  * [volume.py](file:///mnt/Shares/GIT/the-new-algo/autofcholv/src/autofcholv/pipeline/features/volume.py#L329)
* **Mechanism**:
  `volume_tsf` uses `.shift(-1)`, which explicitly pulls the next bar's rolling average into the current bar:
  ```python
  df["volume_tsf"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean().shift(-1)
  ```

* **Remediation**:
  Replace `shift(-1)` with a forward shift `shift(1)` or remove the shift entirely, depending on the original prediction window intended:
  ```python
  df["volume_tsf"] = quote_volume_proxy.rolling(momentum_n, min_periods=1).mean()
  ```
