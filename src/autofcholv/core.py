import pandas as pd
from dotenv import load_dotenv
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
    load_dotenv()
    validate_env()
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


def validate_env():
    import os
    required_vars = load_required_vars()
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing env vars: {missing}")


def load_required_vars(file_path=".env.example"):
    """
    Load required variables from .env.example file.

    Args:
        file_path: Path to the .env.example file

    Returns:
        list: List of required variables
    """
    required_vars = []

    with open(file_path) as f:
        for line in f:
            line = line.strip()

            # bỏ comment và dòng rỗng
            if not line or line.startswith("#"):
                continue

            key = line.split("=")[0].strip()
            required_vars.append(key)

    return required_vars
