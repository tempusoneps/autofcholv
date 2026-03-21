import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate lag features.

    Args:
        df: DataFrame

    Returns:
        DataFrame with new features.
    """
    df['close_lag1'] = df['Close'].shift(1)
    df['open_lag1'] = df['Open'].shift(1)
    df['high_lag1'] = df['High'].shift(1)
    df['low_lag1'] = df['Low'].shift(1)
    df['volume_lag1'] = df['Volume'].shift(1)
    df['ibs_lag1'] = df['ibs'].shift(1)
    return df