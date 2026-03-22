import pandas as pd
import os


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the data by dropping the first n rows instead of using .dropna()."""
    drop_n_rows = int(os.getenv("DROP_FIRST_ROWS", 0))
    if drop_n_rows > 0:
        df = df.iloc[drop_n_rows:]
    return df