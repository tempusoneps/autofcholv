import os
import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate features based on Close column.
    Feature definitions follow close.json.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    fast_n     = int(os.getenv("FAST_TREND_LOOKBACK", 24))
    slow_n     = int(os.getenv("SLOW_TREND_LOOKBACK", 245))
    momentum_n = int(os.getenv("MOMENTUM_LOOKBACK", 24))

    df["ema_fast"] = ta.ema(df["Close"], length=fast_n)
    df["ema_slow"] = ta.ema(df["Close"], length=slow_n)

    df["rsi"] = ta.rsi(df["Close"], length=momentum_n)
    df["rsi_slope"] = df["rsi"].diff()

    tsi_result = ta.tsi(df["Close"])
    if tsi_result is not None and not tsi_result.empty:
        df["tsi"] = tsi_result.iloc[:, 0]

    df["roc_close"] = ta.roc(df["Close"], length=1)

    df["close_zscore"] = ta.zscore(df["Close"], length=momentum_n)

    change     = df["Close"].diff(1).abs()
    net_change = (df["Close"] - df["Close"].shift(momentum_n)).abs()
    volatility = change.rolling(momentum_n).sum()
    df["efficiency_ratio"] = net_change / volatility

    macd_result = ta.macd(df["Close"], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        df["macd"]        = macd_result.iloc[:, 0]
        df["macd_hist"]   = macd_result.iloc[:, 1]
        df["macd_signal"] = macd_result.iloc[:, 2]

    ppo_result = ta.ppo(df["Close"], fast=12, slow=26, signal=9)
    if ppo_result is not None and not ppo_result.empty:
        df["ppo"]        = ppo_result.iloc[:, 0]
        df["ppo_hist"]   = ppo_result.iloc[:, 1]
        df["ppo_signal"] = ppo_result.iloc[:, 2]

    df["ulcer_index"] = ta.ui(df["Close"], length=momentum_n)
    df["cmo"]         = ta.cmo(df["Close"], length=momentum_n)

    df["roc_skew"] = df["roc_close"].rolling(momentum_n).skew()
    df["roc_kurt"] = df["roc_close"].rolling(momentum_n).kurt()

    df['mb'] = df['Close'].rolling(fast_n).mean()
    df['std'] = df['Close'].rolling(fast_n).std()

    df['ub'] = df['mb'] + 2 * df['std']
    df['lb'] = df['mb'] - 2 * df['std']

    return df