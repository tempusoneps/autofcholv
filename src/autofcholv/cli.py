import argparse
import sys
import time
import pandas as pd
from pathlib import Path
from autofcholv import __version__, extract_features
from autofcholv.core import EXTRACT_PROGRESS_STEPS, get_extract_progress_steps
from autofcholv.config.config import generate_default_config_file, load_config


SUPPORTED_OUTPUT_FORMATS = {
    ".csv": "CSV",
    ".parquet": "Parquet",
}


def _get_output_format(output_path: str) -> tuple[str, str]:
    suffix = Path(output_path).suffix.lower()
    if suffix not in SUPPORTED_OUTPUT_FORMATS:
        display_suffix = suffix or "<none>"
        supported = ", ".join(SUPPORTED_OUTPUT_FORMATS)
        raise ValueError(
            f"Unsupported output format {display_suffix}. "
            f"Supported output formats: {supported}."
        )
    return suffix, SUPPORTED_OUTPUT_FORMATS[suffix]


def _write_features(features: pd.DataFrame, output_path: str, output_format: str) -> None:
    if output_format == ".csv":
        features.to_csv(output_path)
        return
    if output_format == ".parquet":
        features.to_parquet(output_path)
        return
    raise ValueError(f"Unsupported output format {output_format!r}.")


class ProgressBar:
    def __init__(self, total: int, enabled: bool = True) -> None:
        self.total = total
        self.enabled = enabled
        self.current = 0
        self.last_line_len = 0

    def update(self, label: str) -> None:
        if not self.enabled:
            return
        self.current += 1
        width = 28
        filled = int(width * self.current / self.total)
        bar = "#" * filled + "-" * (width - filled)
        percent = int(100 * self.current / self.total)
        line = f"Extracting features [{bar}] {self.current}/{self.total} {percent:3d}% {label}"
        padding = " " * max(0, self.last_line_len - len(line))
        sys.stderr.write(f"\r{line}{padding}")
        sys.stderr.flush()
        self.last_line_len = len(line)

    def close(self) -> None:
        if self.enabled:
            sys.stderr.write("\n")
            sys.stderr.flush()

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
        help="Path to save the extracted features as CSV or Parquet (default: output_features.csv)"
    )
    parser_extract.add_argument(
        "--config", "-c",
        help="Path to a custom configuration file (JSON/YAML)"
    )
    parser_extract.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable the extraction progress bar"
    )

    # Subcommand: generate-config
    parser_config = subparsers.add_parser("generate-config", help="Generate default configuration file")
    parser_config.add_argument(
        "--path", "-p",
        default="config.json",
        help="Path to save the config file (default: config.json)"
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

        try:
            output_format, output_format_label = _get_output_format(args.output)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            config = load_config(args.config)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        print(f"Reading data from {args.input}...")
        df = pd.read_csv(args.input, parse_dates=['Date'], index_col='Date')
        print(f"Input CSV length: {len(df)} rows")
        
        print("Extracting features...")
        start_time = time.time()
        progress = ProgressBar(
            get_extract_progress_steps(config),
            enabled=not args.no_progress and sys.stderr.isatty(),
        )
        try:
            features = extract_features(df, config=config, progress_callback=progress.update)
        finally:
            progress.close()
        elapsed = time.time() - start_time
        
        _write_features(features, args.output, output_format)
        print(f"Features successfully extracted and saved to {args.output}")
        print(f"Total extracting time: {elapsed:.2f}s")
        print(f"Output {output_format_label} length: {len(features)} rows")
        print(f"Output {output_format_label} columns: {len(features.columns)} columns")
        print("\nResult Sample:")
        print(features.tail())
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
