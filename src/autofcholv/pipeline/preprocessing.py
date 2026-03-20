import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df.dropna(inplace=True)
    return df