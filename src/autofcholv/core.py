import pandas as pd
from autofcholv.pipeline.validating import validate_ohlcv_dataset
from autofcholv.pipeline.cleaning import clean_ohlcv
from autofcholv.pipeline.feature_engineering import feature_engineering
from autofcholv.pipeline.feature_preprocessing import feature_preprocessing

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform simple feature extraction on OHLCV data.
        
    Returns:
        pd.DataFrame: A dataframe with added features.
    """
    
    # do step 1: validate data

    # do step 2: Clean data

    # do step 3: feature engineering

    # do step 4: feature preprocessing
        
    return features
