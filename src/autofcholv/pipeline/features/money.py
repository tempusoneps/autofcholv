import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df["MF"] = df.apply(lambda r: get_mfm(r), axis=1)
    df["MF3d_direction"] = df["MF"].rolling(150).sum()
    df["MF5d_direction"] = df["MF"].rolling(250).sum()
    df["MFI_1d"] = ta.mfi(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        volume=df["Volume"],
        length=50
    )
    return df


def get_mfm(r):
    if r['High'] == r['Low']:
        return 0
    direction = 1 if r['Close'] > r['Open'] else (-1 if r['Close'] < r['Open'] else 0)
    MFM = ((r['Close'] - r['Low']) - (r['High'] - r['Close'])) / (r['High'] - r['Low'])
    MoneyFlow = MFM * r['Volume'] * direction
    return MoneyFlow