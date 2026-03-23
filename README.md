# autofcholv

A Python library for Automated extraction of relevant features from OHLCV time series data. Designed to help quantitative researchers and traders quickly generate a massive set of highly predictive features from basic pricing and volume data.

## 🚀 Key Features

*   **Automated Validation & Cleaning**: Built-in verification processes that ensure input OHLCV records don't contain logical errors, missing records, or erroneous overlaps (such as incorrect High/Low bounds).
*   **Vectorized Execution**: Under the hood, feature extraction heavily uses vectorized `pandas` and `numpy` functions alongside `pandas-ta` to ensure lightning-fast execution times, even when handling millions of rows.
*   **Broad Feature Sets**: Automatically extracts everything from time signatures and candlestick geometries to advanced fractal mathematics like the Hurst Exponent.
*   **CLI Included**: Ships with an easy-to-use Command Line Interface (`autofcholv`) for users who want to run extractions in a terminal.

---

## 📦 Installation

To install `autofcholv` into your environment, use `pip`. It is recommended to use a virtual environment (`venv`).

```bash
# Clone the repository
git clone https://github.com/tempusoneps/autofcholv.git
cd autofcholv

# Install via pip
pip install .

# For development mode
pip install -e .[dev]
```

### Requirements
*   Python >= 3.12
*   `pandas`
*   `numpy`
*   `pandas_ta`
*   `python-dotenv`

---

## 🛠️ Usage

### Using the Command Line Interface (CLI)

After installing, the `autofcholv` command is immediately available in your terminal.

#### `extract` — Extract features from a CSV file

```bash
autofcholv extract input.csv --output my_features.csv
```

**Options:**
*   `input`: Path to your input OHLCV CSV file. It **must** contain `Date`, `Open`, `High`, `Low`, `Close`, and `Volume` columns.
*   `--output`, `-o`: The path where the output features CSV will be saved (default: `output_features.csv`).

#### `generate-config` — Generate a default configuration file

```bash
autofcholv generate-config --path .env
```

**Options:**
*   `--path`, `-p`: Path to save the generated config file (default: `.env`).

This creates a `.env` file pre-filled with all default configuration values. Edit it to customise feature behaviour (e.g. `ONE_DAY_BARS=49`, `SELECTED_TIME_FRAME=15m`).

#### Global options

*   `--version`, `-v`: Print library version.
*   `--help`, `-h`: Show help message.

#### Configuration loading priority

`autofcholv` resolves configuration in the following order (first match wins):

1. **Environment variables** — all required keys must be present in the environment.
2. **Config file** — a JSON or YAML file passed explicitly via the API (`load_config(path)`).
3. **Built-in defaults** — sensible defaults are applied automatically if neither of the above is available.

### Using the Python API

You can easily use `autofcholv` directly in Jupyter Notebooks or Python scripts:

```python
import pandas as pd
from autofcholv import extract_features

# 1. Load your OHLCV data into a Pandas DataFrame
# It is important that index is a DatetimeIndex and columns are correctly named
df = pd.read_csv("historic_data.csv", index_col="Date", parse_dates=True)

# 2. Run the extraction pipeline
features_df = extract_features(df)

# 3. View the results
print(features_df.tail())
```

---
## Other Resources

Please refer to the [Pipeline Overview](src/autofcholv/pipeline/README.md) for a comprehensive list of all generated features.

Please refer to the [Extracted Features Catalog](src/autofcholv/pipeline/features/README.md) for a comprehensive list of all generated features.

