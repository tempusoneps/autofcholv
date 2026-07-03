# Usage

## Using the Command Line Interface (CLI)

After installing, the `autofcholv` command is immediately available in your terminal.

### `extract` - Extract features from a CSV file

```bash
autofcholv extract input.csv --output my_features.csv
```

Options:

* `input`: Path to your input OHLCV CSV file. It **must** contain `Date`, `Open`, `High`, `Low`, `Close`, and `Volume` columns.
* `--output`, `-o`: The path where the output features CSV will be saved (default: `output_features.csv`).
* `--no-progress`: Disable the extraction progress bar.

### `generate-config` - Generate a default configuration file

```bash
autofcholv generate-config --path config.json
```

Options:

* `--path`, `-p`: Path to save the generated JSON config file (default: `config.json`).

This creates a config file pre-filled with all default configuration values. Edit it to customise feature behaviour (e.g. `ONE_DAY_BARS=49`, `SELECTED_TIME_FRAME=15m`).

### Global Options

* `--version`, `-v`: Print library version.
* `--help`, `-h`: Show help message.

## Using the Python API

You can easily use `autofcholv` directly in Jupyter Notebooks or Python scripts:

```python
import pandas as pd
from autofcholv import extract_features, load_config

# 1. Load your OHLCV data into a Pandas DataFrame
# It is important that index is a DatetimeIndex and columns are correctly named
df = pd.read_csv("historic_data.csv", index_col="Date", parse_dates=True)

# 2. Run the extraction pipeline
config = load_config("config.json")
features_df = extract_features(df, config=config)

# 3. View the results
print(features_df.tail())
```
