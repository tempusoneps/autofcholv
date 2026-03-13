import pandas as pd
import numpy as np
from autofcholv import extract_features

def main():
    """Simple example showing how to use the library."""
    # 1. Create mock OHLCV-ish data
    data = {
        'close': [10, 11, 10.5, 12, 11.8, 13, 13.5, 14],
        'volume': [100, 150, 120, 200, 180, 220, 250, 300]
    }
    df = pd.DataFrame(data)
    
    print("--- Input Data ---")
    print(df)
    
    # 2. Extract features
    print("\n--- Extracting Features ---")
    features = extract_features(df)
    
    # 3. Combine and show results
    result = pd.concat([df, features], axis=1)
    print("\n--- Results (Enriched Data) ---")
    print(result)

if __name__ == "__main__":
    main()
