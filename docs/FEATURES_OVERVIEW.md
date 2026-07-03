# Key Features

* **Automated Validation & Cleaning**: Built-in verification processes that ensure input OHLCV records don't contain logical errors, missing records, or erroneous overlaps (such as incorrect High/Low bounds).
* **Vectorized Execution**: Under the hood, feature extraction heavily uses vectorized `pandas` and `numpy` functions alongside `pandas-ta` to ensure lightning-fast execution times, even when handling millions of rows.
* **Broad Feature Sets**: Automatically extracts everything from time signatures and candlestick geometries to advanced fractal mathematics like the Hurst Exponent.
* **CLI Included**: Ships with an easy-to-use Command Line Interface (`autofcholv`) for users who want to run extractions in a terminal.
