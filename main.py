import pandas as pd
import numpy as np
from autofcholv import extract_features

def main():
    # Create simple mock data
    print("Generating mock data...")
    df = pd.DataFrame({
        'open': np.random.randn(50).cumsum() + 100,
        'high': np.random.randn(50).cumsum() + 105,
        'low': np.random.randn(50).cumsum() + 95,
        'close': np.random.randn(50).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 50)
    })
    
    print("Extracting features...")
    features = extract_features(df)
    
    print("\nResult Sample:")
    print(features.tail())

if __name__ == "__main__":
    main()
