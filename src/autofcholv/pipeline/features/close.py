import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán các features dựa trên cột Close (và High, Low cho ATR/ADX).

    Features (theo close.json):
        - EMA20   : Exponential Moving Average 20
        - EMA250  : Exponential Moving Average 250
        - ATR14   : Average True Range 14
        - ADX14   : Average Directional Index 14
        - RSI20   : Relative Strength Index 20
        - RSI10   : Relative Strength Index 10

    Args:
        df: DataFrame

    Returns:
        DataFrame gốc được bổ sung 6 cột features mới.
    """
    # EMA20 – Exponential Moving Average 20
    df["EMA20"] = ta.ema(df["Close"], length=20)

    # EMA250 – Exponential Moving Average 250
    df["EMA250"] = ta.ema(df["Close"], length=250)
    df["MB"] = df["Close"].rolling(20).mean()
    df["STD"] = df["Close"].rolling(20).std()
    df["UB"] = df["MB"] + 1.5 * df["STD"]
    df["LB"] = df["MB"] - 1.5 * df["STD"]

    # RSI20 – Relative Strength Index 20
    df["RSI20"] = ta.rsi(df["Close"], length=20)

    # RSI10 – Relative Strength Index 10
    df["RSI10"] = ta.rsi(df["Close"], length=10)

    return df