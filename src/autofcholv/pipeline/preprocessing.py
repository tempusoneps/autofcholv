import pandas as pd
from autofcholv.config.config import Config


def preprocess_data(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Preprocess the data by dropping the first n rows instead of using .dropna()."""
    null_cols = df.columns[df.isna().all()].tolist()
    if null_cols:
        raise ValueError(f"Found columns with all null values: {', '.join(null_cols)}")
        
    drop_n_rows = config.drop_first_rows
    if drop_n_rows > 0:
        df = df.iloc[drop_n_rows:]
    
    # Drop lakage data
    return df
