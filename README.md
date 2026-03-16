# autofcholv

A modular Python library for Automatic extraction of relevant features from OHLCV time series.

## Features
- Modular architecture with clear separation between core logic, features, and CLI.
- Extensible feature extraction functions.
- Command-line interface for batch processing.
- Modern Python packaging using `pyproject.toml`.

## Installation

```bash
pip install .
```

## Quick Start

### Python API
```python
from autofcholv import extract_features
import pandas as pd

df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
features = extract_features(df)
print(features)
```

### CLI
```bash
autofcholv extract input.csv --output features.csv
```
