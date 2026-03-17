import argparse
import sys
import pandas as pd
from pathlib import Path
from autofcholv import extract_features
from autofcholv import __version__

def main():
    """Entry point for the console script."""
    parser = argparse.ArgumentParser(
        description="autofcholv: Automated Feature Extraction Tool for OHLCV data"
    )
    parser.add_argument(
        "input", 
        nargs="?", 
        help="Path to the input CSV file"
    )
    parser.add_argument(
        "--output", "-o", 
        default="output_features.csv",
        help="Path to save the extracted features (default: output_features.csv)"
    )
    parser.add_argument(
        "--version", "-v", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Reading data from {args.input}...")
        df = pd.read_csv(args.input, parse_dates=['Date'], index_col='Date')
        
        print("Extracting features...")
        features = extract_features(df)
        
        features.to_csv(args.output)
        print(f"Features successfully extracted and saved to {args.output}")
        print("\nResult Sample:")
        print(features.tail())
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
