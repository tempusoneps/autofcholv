# Installation

## Using `pip`

It is recommended to use a virtual environment (`venv`).

```bash
pip install autofcholv
```

## Using `uv` (recommended)

[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package manager. Install it first if you haven't:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the library:

```bash
uv add autofcholv
```

Or run it in an isolated environment without installing:

```bash
uvx autofcholv
```

## From source

```bash
# Clone the repository
git clone https://github.com/tempusoneps/autofcholv.git
cd autofcholv

# Install via pip
pip install .

# Or via uv
uv sync

# For development mode (pip)
pip install -e .[dev]

# For development mode (uv)
uv sync --dev
```

## Requirements

* Python >= 3.12
* `pandas`
* `numpy`
* `pandas_ta`
* `python-dotenv`
