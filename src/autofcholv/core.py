import pandas as pd

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform simple feature extraction on OHLCV data.
    
    Args:
        df (pd.DataFrame): Dataframe with at least a 'close' column.
        
    Returns:
        pd.DataFrame: A dataframe with added features.
    """
    if df.empty:
        return pd.DataFrame()
    
    features = pd.DataFrame(index=df.index)
    
    if 'close' in df.columns:
        features['close_pct_change'] = df['close'].pct_change()
        features['close_sma_5'] = df['close'].rolling(window=5).mean()
        features['close_sma_20'] = df['close'].rolling(window=20).mean()
        
    if 'volume' in df.columns:
        features['volume_pct_change'] = df['volume'].pct_change()
        
    return features
