# Báo Cáo Các Feature Còn Fix Cứng Window Lookback (Hardcoded Windows Report)

Báo cáo này tổng hợp chi tiết tất cả các chỉ báo kỹ thuật và đặc trưng (features) trong pipeline `autofcholv` hiện vẫn đang sử dụng các hằng số (hardcoded integers) cho chu kỳ lookback (thay vì lấy từ cấu hình `Config`).

---

## 1. Tổng Quan Theo Từng Module

### 1.1. Module `close.py`
Nguồn: [`src/autofcholv/pipeline/features/close.py`](../src/autofcholv/pipeline/features/close.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L97** | `macd`, `macd_hist`, `macd_line` | `ta.macd(df["Close"], fast=12, slow=26, signal=9)` | `fast=12, slow=26, signal=9` | Chu kỳ MACD cổ điển |
| **L103** | `ppo`, `ppo_hist`, `ppo_line` | `ta.ppo(df["Close"], fast=12, slow=26, signal=9)` | `fast=12, slow=26, signal=9` | Chu kỳ PPO cổ điển |
| **L411, L550** | `bias36`, `bias36_raw` | `Close.rolling(3).mean() - Close.rolling(6).mean()` | `window=3, 6` | Bias MA3 vs MA6 |
| **L1098-1099** | `stoch_rsi` | `df["rsi_medium"].rolling(14).max()` / `.min()` | `window=14` | Rolling min/max cho Stoch RSI |
| **L1103** | `awesome_oscillator` | `typical_price.rolling(5).mean() - typical_price.rolling(34).mean()` | `fast=5, slow=34` | AO chuẩn Bill Williams |
| **L1110-1115** | `ultimate_osc` | `uo_buying_pressure.rolling(7/14/28).sum()` | `periods=7, 14, 28` | Ultimate Oscillator chuẩn Larry Williams |
| **L1118** | `stochrsi_k`, `stochrsi_d` | `ta.stochrsi(df["Close"], length=14, rsi_length=14, k=3, d=3)` | `length=14, k=3, d=3` | Stochastic RSI mặc định |
| **L1126** | `williams_r_14` | `ta.willr(df["High"], df["Low"], df["Close"], length=14)` | `length=14` | Williams %R 14 phiên |
| **L1134** | `macd_hist_12_26_9` | `ta.macd(df["Close"], fast=12, slow=26, signal=9)` | `fast=12, slow=26, signal=9` | Cột MACD histogram đặt tên theo số |

---

### 1.2. Module `trend.py`
Nguồn: [`src/autofcholv/pipeline/features/trend.py`](../src/autofcholv/pipeline/features/trend.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L717** | `trix` | `ta.trix(df["Close"], length=15, signal=9)` | `length=15, signal=9` | TRIX indicator |
| **L725** | `supertrend` | `ta.supertrend(..., length=10, multiplier=3.0)` | `length=10` | SuperTrend 10 phiên |
| **L786** | `ema_8` | `ta.ema(df["Close"], length=8)` | `length=8` | EMA 8 |
| **L787** | `ema_20` | `ta.ema(df["Close"], length=20)` | `length=20` | Tương đương `config.medium_lookback` |
| **L788** | `ema_21` | `ta.ema(df["Close"], length=21)` | `length=21` | EMA 21 |
| **L789** | `ema_55` | `ta.ema(df["Close"], length=55)` | `length=55` | Fibonacci EMA 55 |
| **L790** | `ema_250` | `ta.ema(df["Close"], length=250)` | `length=250` | EMA 250 phiên (hoặc `one_week_bars: 245`) |
| **L800** | `adx_14` | `ta.adx(..., length=14)` | `length=14` | ADX 14 phiên |
| **L810** | `adx_42` | `ta.adx(..., length=42)` | `length=42` | ADX 42 phiên |
| **L827** | `linear_regression_slope_8` | `ta.slope(df["Close"], length=8)` | `length=8` | Linear regression slope 8 phiên |

---

### 1.3. Module `volatility.py`
Nguồn: [`src/autofcholv/pipeline/features/volatility.py`](../src/autofcholv/pipeline/features/volatility.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L508** | `bb_width_q20` | `df["bb_width"].rolling(100).quantile(0.2)` | `window=100` | Tương đương `config.macro_lookback` |
| **L521-524** | Choppiness / Chaikin | `High.rolling(14).max()`, `atr.rolling(14).sum()` | `window=14` | Chu kỳ 14 nến |
| **L548-549** | `donchian_high/low_30_shift1` | `df["High"].rolling(30).max().shift(1)` | `window=30` | Tương đương `config.morning_bars` |

---

### 1.4. Module `volume.py`
Nguồn: [`src/autofcholv/pipeline/features/volume.py`](../src/autofcholv/pipeline/features/volume.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L545** | `mfi` | `ta.mfi(..., length=14)` | `length=14` | Money Flow Index 14 phiên |

---

### 1.5. Module `mix.py`
Nguồn: [`src/autofcholv/pipeline/features/mix.py`](../src/autofcholv/pipeline/features/mix.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L239** | `persist_short_12_shift1` | `below_open.rolling(12).mean().shift(1)` | `window=12` | Tương đương `config.one_hour_bars` |
| **L243** | `price_rank` (trong `custom_002`) | `df["roc_close"].rolling(100).rank(pct=True) * 100` | `window=100` | Tương đương `config.macro_lookback` |
| **L244** | `rsi3` (trong `custom_001`) | `ta.rsi(df["Close"], length=3)` | `length=3` | RSI cực ngắn (Ultra-short RSI) |
| **L245** | `streak_rsi2` (trong `custom_001`) | `ta.rsi(df["streak"].astype(float), length=2)` | `length=2` | RSI trên chuỗi streak tăng/giảm |

---

### 1.6. Module `resample.py`
Nguồn: [`src/autofcholv/pipeline/features/resample.py`](../src/autofcholv/pipeline/features/resample.py)

| Dòng | Feature Column / Biến | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L40** | `prev_day_ema_bias_20` | `daily_data["day_close"].ewm(span=20, adjust=False).mean()` | `span=20` | EMA 20 trên khung Daily |
| **L95** | `prev_15m/30m/1h_ema_bias_20` | `htf["Close"].ewm(span=20, adjust=False).mean()` | `span=20` | EMA 20 trên các khung HTF |

---

### 1.7. Module `signal.py`
Nguồn: [`src/autofcholv/pipeline/features/signal.py`](../src/autofcholv/pipeline/features/signal.py)

| Dòng | Signal / Rule | Code Hiện Tại | Tham Số Cố Định | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **L168-169** | `macd_histogram_reversal_signal` | `df["macd_hist"].rolling(10).max()` / `.min()` | `window=10` | Tương đương `config.short_lookback` |
| **L174, L180** | `macd_histogram_reversal_signal` | `df["macd_hist"].rolling(5).sum()` | `window=5` | Tương đương `config.micro_lookback` |

---

## 2. Phân Loại Theo Mục Đích Sử Dụng

1. **Nhóm Chỉ Báo Sách Giáo Khoa (Classic Indicators)**:
   - Các chỉ báo như **MACD (12, 26, 9)**, **PPO (12, 26, 9)**, **StochRSI (14)**, **Williams %R (14)**, **Awesome Oscillator (5, 34)**, **Ultimate Oscillator (7, 14, 28)**, **MFI (14)**, **SuperTrend (10)**, **TRIX (15)**.
   - *Đặc điểm*: Các chu kỳ này thường đi liền với công thức chuẩn của tác giả sáng tạo ra chỉ báo.
2. **Nhóm Trùng Khớp Với 5-Tiers & Session Bars (Có Thể Chuẩn Hóa Sang Config Ngay)**:
   - `rolling(5)` $\rightarrow$ `config.micro_lookback` (5)
   - `rolling(10)` $\rightarrow$ `config.short_lookback` (10)
   - `rolling(20)` / `ewm(span=20)` $\rightarrow$ `config.medium_lookback` (20)
   - `rolling(100)` $\rightarrow$ `config.macro_lookback` (100)
   - `rolling(12)` $\rightarrow$ `config.one_hour_bars` (12)
   - `rolling(30)` $\rightarrow$ `config.morning_bars` (30)
3. **Nhóm Các Feature Mang Tên Kèm Số Cố Định Cần Xem Xét**:
   - `ema_8`, `ema_20`, `ema_21`, `ema_55`, `ema_250`
   - `adx_14`, `adx_42`
   - `linear_regression_slope_8`
   - `macd_hist_12_26_9`
   - `williams_r_14`
   - `donchian_high/low_30_shift1`
   - `persist_short_12_shift1`
