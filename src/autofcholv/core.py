import pandas as pd
from autofcholv.pipeline.validation import validate_ohlcv_dataset
from autofcholv.pipeline.cleaning import clean_ohlcv
from autofcholv.pipeline.feature_engineering import build_features
from autofcholv.pipeline.preprocessing import preprocess_data

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform simple feature extraction on OHLCV data.
        
    Returns:
        pd.DataFrame: A dataframe with added features.
    """
    
    # do step 1: validate data
    is_valid, error_details = validate_ohlcv_dataset(df)
    if not is_valid:
        raise ValueError(f"Invalid OHLCV data: {error_details}")

    # do step 2: Clean data
    df = clean_ohlcv(df)

    # do step 3: feature engineering
    df = build_features(df)

    # do step 4: feature preprocessing
    df = preprocess_data(df)
        
    return df
