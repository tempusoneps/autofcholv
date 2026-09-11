import pandas as pd
from typing import Callable
from autofcholv.pipeline.validation import validate_ohlcv_dataset
from autofcholv.pipeline.cleaning import clean_ohlcv
from autofcholv.pipeline.feature_engineering import FEATURE_STEPS, build_features, get_feature_steps
from autofcholv.pipeline.preprocessing import preprocess_data
from autofcholv.config.config import Config, ensure_config


EXTRACT_PROGRESS_STEPS = 3 + len(FEATURE_STEPS)


def get_extract_progress_steps(config: Config | None = None) -> int:
    """Calculate the total number of progress steps for extraction given a config."""
    steps = get_feature_steps(config)
    return 3 + len(steps)


def extract_features(
    df: pd.DataFrame,
    config: Config | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Perform simple feature extraction on OHLCV data.
        
    Returns:
        pd.DataFrame: A dataframe with added features.
    """
    config = ensure_config(config)
    # do step 1: validate data
    is_valid, error_details = validate_ohlcv_dataset(df)
    if not is_valid:
        raise ValueError(f"Invalid OHLCV data: {error_details}")
    if progress_callback:
        progress_callback("validation")

    # do step 2: Clean data
    df = clean_ohlcv(df)
    if progress_callback:
        progress_callback("cleaning")

    # do step 3: feature engineering
    df = build_features(df, config, progress_callback=progress_callback)

    # do step 4: feature preprocessing
    df = preprocess_data(df, config)
    if progress_callback:
        progress_callback("preprocessing")
        
    return df
