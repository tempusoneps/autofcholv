import pandas as pd
import numpy as np
import pytest
from autofcholv.core import extract_features

def test_extract_features_basic():
    """Test standard feature extraction."""
    df = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500]
    })
    
    features = extract_features(df)
    
    assert 'close_pct_change' in features.columns
    assert 'close_sma_5' in features.columns
    assert 'volume_pct_change' in features.columns
    
    # Check simple calculation (SMA 5 of [100, 101, 102, 103, 104] is 102)
    assert features['close_sma_5'].iloc[4] == 102.0

def test_extract_features_empty():
    """Test with empty dataframe."""
    df = pd.DataFrame()
    features = extract_features(df)
    assert features.empty

def test_extract_features_missing_columns():
    """Test with missing columns."""
    df = pd.DataFrame({'open': [1, 2, 3]})
    features = extract_features(df)
    # Should return empty features df with same index if no close/volume found
    assert features.empty
    assert len(features.index) == 3
