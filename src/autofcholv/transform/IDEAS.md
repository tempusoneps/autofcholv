
Feature set mẫu cho M5
features = [
    # regime
    adx,
    adx_slope,
    hurst,
    session_flag,

    # volatility
    atr_norm,
    parkinson_vol,
    rolling_std,

    # momentum
    rsi7,
    rsi_slope,
    macd_hist_deriv,
    ema20_slope,
    roc_3,
    roc_6,

    # mean reversion
    zscore_20,
    dist_vwap,

    # microstructure
    body_ratio,
    wick_ratio,
    consecutive_candles,
]

-----------------------------------------------------------------------------------------------------------------
Ngoài 5 nhóm bạn đang có:

regime

volatility

momentum

mean reversion

microstructure

Mình suggest thêm 7 nhóm feature nâng cao mà nhiều retail algo không khai thác hết 👇

1️⃣ 🧠 Market Structure Features

Không phải indicator, mà là cấu trúc giá.

🔹 Swing structure

Higher High / Lower Low flag

Distance tới swing high gần nhất

Break of structure (BOS)

🔹 Liquidity sweep detection

High phá đỉnh nhưng close dưới đỉnh

Low phá đáy nhưng close trên đáy

Rất hữu ích M5 London session.

2️⃣ ⏱️ Time & Seasonality Encoding (edge lớn trong FX)

Forex không random theo thời gian.

🔹 Cyclical time encoding
sin_hour = sin(2π * hour / 24)
cos_hour = cos(2π * hour / 24)
🔹 Day-of-week effect

Thứ 2 & thứ 6 behavior khác nhau.

🔹 Minutes-from-session-open

London open + 15 phút đầu rất khác.

3️⃣ 📈 Multi-Timeframe Context (cực mạnh)

Đây là thứ nhiều model thiếu.

Ví dụ M5:

H1 trend direction

H1 ADX

H1 RSI

M15 structure bias

Model sẽ học:

Trade M5 mean reversion nhưng theo hướng H1 trend

4️⃣ 🧮 Statistical Distribution Features
🔹 Rolling skewness
🔹 Rolling kurtosis
🔹 Entropy (Shannon entropy)

M5 chop thường có entropy cao.

5️⃣ 🔄 Order Flow Proxy nâng cao

Forex không có real orderbook, nhưng có thể proxy:

🔹 Volume imbalance proxy

Up volume vs down volume ratio.

🔹 Delta candle proxy

(close-open) * tick_volume

🔹 Volume acceleration

Volume_t − rolling_mean_volume

6️⃣ 🧬 Non-linear Transform Features

Model tree-based thích feature phi tuyến:

RSI²

ATR × ADX

Zscore × Volume

Momentum / Volatility ratio

Ví dụ:

momentum_vol_ratio = roc_3 / atr
7️⃣ 🛑 Risk State Features (ít ai thêm nhưng cực quan trọng)

Model cần biết khi nào KHÔNG trade.

🔹 Spread filter

spread / atr

🔹 News proximity flag

within 30m of high-impact event

🔹 Drawdown state

Equity drawdown hiện tại bao nhiêu %

Bạn có thể feed equity state vào model → adaptive risk.

8️⃣ 🔬 Meta Features (rất advanced)
🔹 Prediction uncertainty

Nếu dùng probabilistic model:

entropy của prediction

variance bootstrap

🔹 Feature regime clustering

Dùng k-means clustering để xác định market regime trước khi train model riêng cho từng regime.
-----------------------------------------------------------------------------------------------------------------

Đừng label kiểu:

next_bar_return > 0

Thay vào đó:

Triple Barrier Method

Take profit = 1.5 ATR

Stop loss = 1 ATR

Max holding = 10 bars

Label:

1 = TP hit

-1 = SL hit

0 = timeout
-----------------------------------------------------------------------------------------------------------------

df['volatility_spike'] = df['ATR'] > df['ATR'].rolling(20).mean()
-----------------------------------------------------------------------------------------------------------------

Trend filter
df['strong_trend'] = df['ADX_14'] > 25
Kết hợp tín hiệu vào lệnh
df['long_signal'] = (
    (df['DMP_14'] > df['DMN_14']) &
    (df['ADX_14'] > 25)
)


-----------------------------------------------------------------------------------------------------------------

def hurst_exponent(series, max_lag=100):
    lags = range(2, max_lag)
    tau = []

    for lag in lags:
        diff = series.diff(lag).dropna()
        tau.append(np.sqrt(np.std(diff)))

    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0]


df['hurst_100'] = (
    df['Close']
    .rolling(100)
    .apply(lambda x: hurst_exponent(x), raw=False)
)

Detect regime
df['regime'] = np.where(
    df['hurst_100'] > 0.55, 
    'trend',
    'mean_revert'
)
-----------------------------------------------------------------------------------------------------------------

def calculate_vwap(df):
    df = df.copy()
    
    # Typical price
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    
    df['cum_vol'] = df['Volume'].cumsum()
    df['cum_pv'] = (tp * df['Volume']).cumsum()
    
    df['VWAP'] = df['cum_pv'] / df['cum_vol']
    
    return df
or
df['date'] = df.index.date

tp = (df['High'] + df['Low'] + df['Close']) / 3

df['VWAP'] = (
    (tp * df['Volume'])
    .groupby(df['date']).cumsum()
    /
    df['Volume'].groupby(df['date']).cumsum()
)
or
df.ta.vwap(append=True)
df['long_bias'] = df['Close'] > df['VWAP']
-----------------------------------------------------------------------------------------------------------------

def rolling_slope(series, window=5):
    slopes = []
    x = np.arange(window)

    for i in range(len(series)):
        if i < window:
            slopes.append(np.nan)
        else:
            y = series[i-window:i]
            slope = np.polyfit(x, y, 1)[0]
            slopes.append(slope)
    
    return pd.Series(slopes, index=series.index)

df['RSI_slope_5'] = rolling_slope(df['RSI'], window=5)

df.ta.rsi(length=14, append=True)
df.ta.slope(close='RSI_14', length=5, append=True)
df['momentum_build'] = df['RSI_slope'] > df['RSI_slope'].rolling(10).mean()
-----------------------------------------------------------------------------------------------------------------
🔹 Đếm số nến tăng liên tiếp
import pandas as pd
import numpy as np

up = df['Close'] > df['Close'].shift(1)

df['up_streak'] = (
    up.groupby((up != up.shift()).cumsum())
      .cumcount() + 1
)

df.loc[~up, 'up_streak'] = 0
🔹 Đếm số nến giảm liên tiếp
down = df['Close'] < df['Close'].shift(1)

df['down_streak'] = (
    down.groupby((down != down.shift()).cumsum())
        .cumcount() + 1
)

df.loc[~down, 'down_streak'] = 0
Cách gọn hơn (clean version)
def consecutive_count(condition):
    return (
        condition.groupby((condition != condition.shift()).cumsum())
                 .cumcount() + 1
    ) * condition

df['up_streak'] = consecutive_count(df['Close'] > df['Close'].shift())
df['down_streak'] = consecutive_count(df['Close'] < df['Close'].shift())
-----------------------------------------------------------------------------------------------------------------

df['ROC_3']  = df['Close'].pct_change(3) * 100
df['ROC_6']  = df['Close'].pct_change(6) * 100
df['ROC_12'] = df['Close'].pct_change(12) * 100

🔹 Momentum alignment
df['bullish_momentum'] = (
    (df['ROC_3'] > 0) &
    (df['ROC_6'] > 0) &
    (df['ROC_12'] > 0)
)
🔹 Acceleration breakout
df['momentum_accel'] = (
    (df['ROC_3'] > df['ROC_6']) &
    (df['ROC_6'] > df['ROC_12'])
)
-----------------------------------------------------------------------------------------------------------------

def parkinson_vol(df, window=20):
    hl_log = np.log(df['High'] / df['Low'])
    rs = (hl_log ** 2).rolling(window).sum()
    
    factor = 1 / (4 * window * np.log(2))
    return np.sqrt(factor * rs)

df['parkinson_vol_20'] = parkinson_vol(df, window=20)

df['high_vol_regime'] = df['parkinson_vol_20'] > df['parkinson_vol_20'].rolling(100).mean()

-----------------------------------------------------------------------------------------------------------------
df['return'] = df['Close'].pct_change()
df['skew_100'] = df['return'].rolling(100).skew()
df['kurt_100'] = df['return'].rolling(100).kurt()
df['crash_risk'] = (
    (df['skew_100'] < -1) &
    (df['kurt_100'] > 3)
)

-----------------------------------------------------------------------------------------------------------------
