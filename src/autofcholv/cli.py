import argparse
import sys
import time
import pandas as pd
from pathlib import Path
from autofcholv import extract_features
from autofcholv import __version__
from autofcholv.config.config import generate_default_config_file

def main():
    """Entry point for the console script."""
    parser = argparse.ArgumentParser(
        description="autofcholv: Automated Feature Extraction Tool for OHLCV data"
    )
    parser.add_argument(
        "--version", "-v", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Subcommand: extract
    parser_extract = subparsers.add_parser("extract", help="Extract features from input data")
    parser_extract.add_argument(
        "input", 
        help="Path to the input CSV file"
    )
    parser_extract.add_argument(
        "--output", "-o", 
        default="output_features.csv",
        help="Path to save the extracted features (default: output_features.csv)"
    )
    parser_extract.add_argument(
        "--config", "-c",
        help="Path to a custom configuration file (JSON/YAML)"
    )

    # Subcommand: generate-config
    parser_config = subparsers.add_parser("generate-config", help="Generate default configuration .env file")
    parser_config.add_argument(
        "--path", "-p",
        default=".env",
        help="Path to save the config file (default: .env)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "generate-config":
        print(f"Generating default config at {args.path}...")
        success = generate_default_config_file(args.path)
        if success:
            print("Successfully generated configuration file.")
        else:
            print("Failed to generate configuration file.", file=sys.stderr)
            sys.exit(1)
        return

    if args.command == "extract":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
            sys.exit(1)
        
        # Load custom config if provided
        if args.config:
            from autofcholv.config.config import load_config
            try:
                load_config(args.config)
            except Exception as e:
                print(f"Error loading config: {e}", file=sys.stderr)
                sys.exit(1)

    try:
        print(f"Reading data from {args.input}...")
        df = pd.read_csv(args.input, parse_dates=['Date'], index_col='Date')
        print(f"Input CSV length: {len(df)} rows")
        
        print("Extracting features...")
        start_time = time.time()
        features = extract_features(df)
        elapsed = time.time() - start_time
        
        features.to_csv(args.output)
        print(f"Features successfully extracted and saved to {args.output}")
        print(f"Total extracting time: {elapsed:.2f}s")
        print(f"Output CSV length: {len(features)} rows")
        print(f"Output CSV columns: {len(features.columns)} columns")
        print("\nResult Sample:")
        print(features.tail())
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
