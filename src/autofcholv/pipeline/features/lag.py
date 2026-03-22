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
    df['body_lag1'] = df['body'].shift(1)
    df['upwick_lag1'] = df['upwick'].shift(1)
    df['lowwick_lag1'] = df['lowwick'].shift(1)
    df['ibs_lag1'] = df['ibs'].shift(1)
    df['rsi_lag1'] = df['rsi'].shift(1)
    df['ema_fast_lag1'] = df['ema_fast'].shift(1)
    df['ema_slow_lag1'] = df['ema_slow'].shift(1)
    return df