import os
import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    momentum_n = int(os.getenv("MOMENTUM_LOOKBACK", 24))
    df['volume_avg'] = df['Volume'].rolling(momentum_n).mean()
    df['volume_zscore'] = (df['Volume'] - df['volume_avg']) / df['Volume'].rolling(momentum_n).std()
    return df