import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables required by the pipeline
# The .env.example should be present in the root of the project
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.example")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("Warning: .env.example not found, please ensure required environment variables are set.")

from autofcholv.core import extract_features

def make_sample_ohlcv(n_bars: int = 500) -> pd.DataFrame:
    """Generate synthetic 5-minute OHLCV data."""
    # Create datetime index excluding lunch breaks to mimic real market data
    idx = pd.date_range(start="2024-01-02 09:00:00", periods=n_bars, freq="5min")
    idx = idx[(idx.hour * 100 + idx.minute != 1130) & (idx.hour * 100 + idx.minute != 1430)]
    
    rng = np.random.default_rng(42)
    
    # Generate random walk with drift for Close prices
    returns = rng.normal(0.0001, 0.002, len(idx))
    close = 100.0 * np.exp(np.cumsum(returns))
    
    # Generate accompanying Open, High, Low
    open_ = close * (1 + rng.normal(0, 0.001, len(idx)))
    high  = close * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    low   = close * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    
    # Generate Volume
    volume = rng.integers(1000, 50000, len(idx)).astype(float)
    
    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
    df.index.name = "Date"
    
    # Fix High/Low to be truly highest/lowest
    df["High"] = df[["Open", "Close", "High"]].max(axis=1)
    df["Low"]  = df[["Open", "Close", "Low"]].min(axis=1)
    
    return df

def main():
    """Simple example showing how to use the autofcholv library."""
    
    print("1. Generating sample OHLCV dataset...")
    # Generate 500 bars of synthetic data to cover long lookback windows
    df = make_sample_ohlcv(n_bars=500)
    
    print("\n--- Input Data Head ---")
    print(df.head())
    print("\nTotal rows:", len(df))
    
    print("\n2. Extracting Features using the Pipeline...")
    try:
        enriched_df = extract_features(df)
        
        print("\n--- Results (Enriched Data Tail) ---")
        # Show some of the newly generated feature columns
        demo_cols = ["Close", "Volume", "rsi", "macd", "atr", "body_rate", "volume_group"]
        cols_to_show = [c for c in demo_cols if c in enriched_df.columns]
        
        print(enriched_df[cols_to_show].tail())
        print(f"\nSuccessfully generated {len(enriched_df.columns)} features!")
        
    except Exception as e:
        print(f"\nError running pipeline: {e}")

if __name__ == "__main__":
    main()
