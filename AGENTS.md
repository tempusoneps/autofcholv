# Agent Guide

This file is generated from project documentation. Do not edit it directly.


## Repository Guidelines

#### Project Structure & Module Organization

`autofcholv` is a Python 3.12 package for OHLCV feature extraction. Source code lives in `src/autofcholv/`: `core.py` coordinates validation, cleaning, feature engineering, and preprocessing; `cli.py` provides the `autofcholv` command; `config/` handles defaults and config files; `pipeline/` contains the processing stages; `pipeline/features/` contains feature modules and matching JSON metadata. Tests are in `tests/`, examples in `examples/`, generated/reference docs in `docs/`, and utility scripts in `scripts/`. Root CSV files such as `input.csv` and `my_features.csv` are sample data/output.

#### Build, Test, and Development Commands

- `uv sync --dev`: install runtime and development dependencies from `pyproject.toml` and `uv.lock`.
- `uv run pytest`: run the full test suite.
- `uv run pytest tests/test_cli.py`: run only CLI tests.
- `uv run autofcholv extract input.csv --output my_features.csv`: run local feature extraction through the console entry point.
- `uv run python -m build`: build source and wheel distributions into `dist/`.
- `uv run python scripts/generate_feature_markdown_doc.py`: regenerate feature documentation when feature metadata changes.

#### Coding Style & Naming Conventions

Use standard Python style with 4-space indentation, explicit imports, and small functions that keep pipeline stages readable. Public modules and functions use `snake_case`; tests use `test_*` names. Feature columns include both legacy mixed-case names and newer `snake_case` names, so preserve existing output names unless intentionally changing the public feature contract. Keep feature implementation files paired with their JSON metadata when adding or renaming features.

#### Testing Guidelines

The project uses `pytest`. Add or update tests in `tests/test_core.py` for feature output behavior and `tests/test_cli.py` for command-line behavior. Tests should use synthetic OHLCV data with `Date`, `Open`, `High`, `Low`, `Close`, and `Volume` columns. When changing feature generation, include assertions for expected columns and guard against leakage from current-day aggregates.

#### Test Performance Guidelines

Feature extraction is intentionally wide and expensive, so avoid running the full pipeline repeatedly during normal development. Prefer a layered test strategy:

- Put fast, narrow tests around individual feature modules when changing one module. Call `src/autofcholv/pipeline/features/<module>.py::extract_features` directly with a small DataFrame instead of calling the public `extract_features()` pipeline.
- Reserve full `extract_features()` pipeline tests for contract coverage, pipeline wiring, CLI behavior, and cross-module leakage checks.
- When a test needs the full pipeline, compute it once per test module with a pytest fixture, for example a `@pytest.fixture(scope="module")` or `@pytest.fixture(scope="session")`, and return `result.copy()` to each test that mutates the DataFrame.
- Do not call `extract_features(make_ohlcv(...))` independently in many tests for column-presence assertions. Combine broad column-contract assertions into a small number of tests, or reuse the cached full-pipeline fixture.
- Keep synthetic datasets as small as the feature under test allows. Only use long datasets for features that truly need long lookbacks such as slow trend windows; document the lookback reason in the fixture name or test comment.
- For TDD and debugging, first run the smallest relevant test selection, such as `uv run pytest tests/test_core.py::test_name -q`. Do NOT run the full test suite (`uv run pytest`) automatically without asking and receiving explicit user confirmation.
- For CLI tests, avoid exercising the complete wide feature catalog unless the test is explicitly checking end-to-end extraction. Prefer mocking or a minimal configuration path when testing argument parsing, logging, validation errors, or file handling.
- Treat performance regressions in tests as maintenance issues. If a new test adds another full-pipeline extraction, consider whether it can reuse an existing fixture or test the owning feature module directly.

#### Commit & Pull Request Guidelines

Recent commits use short, imperative messages such as `add quanlify signal features` and `remove leakage features`. Keep commits focused and describe the behavior changed. Pull requests should include a concise summary, test results, linked issues when relevant, and sample CLI output or screenshots only when user-facing behavior changes.

#### Agent-Specific Instructions

For Codex work in this repository, prefix shell commands with `rtk` as required by the local instructions, for example `rtk git status` or `rtk pytest -q`. Before editing, check `git status --short` and avoid overwriting unrelated user changes.

# Project Rules

## Keep Structure Documentation In Sync

Any change that affects the repository layout must update `docs/STRUCTURE.md` in the same change set.

This includes adding, deleting, moving, or renaming files and directories.

## Keep Feature Metadata In Sync

Any change that adds, removes, or renames generated feature columns in `src/autofcholv/pipeline/features/*.py` must update the matching `src/autofcholv/pipeline/features/*.json` file.

## Regenerate Generated Documentation

When feature metadata changes, regenerate the feature catalog:

```bash
python3 scripts/generate_feature_md_from_json.py
```

When files used by the root README change, regenerate the root README:

```bash
scripts/generate_root_readme.sh
```

## Update README Through Source Docs

Do not update the root `README.md` directly. To change README content, update one of the source files in `docs/` that feeds the README, then regenerate the root README with `scripts/generate_root_readme.sh`.

## Do Not Hand-Edit Generated Files

Do not manually edit generated documentation when a source file or generator exists.

For example, update feature JSON metadata and regenerate `docs/FEATURES.md` instead of editing the generated table directly.

## Keep Pipeline Wiring Explicit

When adding a new feature module, update all relevant places in the same change set:

* `src/autofcholv/pipeline/feature_engineering.py`
* the module's feature metadata JSON file
* `docs/STRUCTURE.md`
* regenerated `docs/FEATURES.md`

## Run Relevant Tests

When changing pipeline, feature, preprocessing, validation, config, or CLI behavior, prefer running only specific, targeted tests (e.g. `uv run pytest tests/test_core.py::test_name -q`).

**Do NOT run the full pytest test suite automatically.** Because full feature extraction tests are expensive in time and resources, AI agents must ask the user for confirmation and get explicit approval before executing the complete test suite (`uv run pytest` without targeted filters).

If tests cannot be run or are skipped per user instruction, note the reason in the final change summary.

## Keep Documentation Links Valid

When moving, renaming, adding, or deleting documentation/source files, update all affected links in `README.md`, `docs/*.md`, and pipeline docs.

# Project Structure

```text
.
├── README.md                         # Root README generated from selected docs files.
├── CHANGELOG.md                      # Release notes and project change history.
├── LICENSE                           # Project license.
├── pyproject.toml                    # Package metadata, dependencies, and CLI entry point.
├── uv.lock                           # Locked dependency versions for uv.
├── AGENTS.md                         # Local agent/development instructions.
│
├── docs/                             # Human-facing project documentation.
│   ├── AI_AGENT_GUIDELINE.md         # Source guideline text for generated AGENTS.md.
│   ├── CONFIGURATION.md              # Configuration loading and priority rules.
│   ├── FEATURES.md                   # Generated catalog of feature columns from JSON metadata.
│   ├── FEATURES_OVERVIEW.md          # High-level feature set overview.
│   ├── GIT_CONVENTIONS.md            # Git workflow and structured commit conventions.
│   ├── INSTALLATION.md               # Install instructions for pip, uv, and source installs.
│   ├── PLAN_v0.4.0.md                # Implementation plan for version 0.4.0 features.
│   ├── REF.md                        # Short project references and notes.
│   ├── RESOURCES.md                  # Links to related project docs.
│   ├── RULE.md                       # Project rules or conventions.
│   ├── STRUCTURE.md                  # This repository structure guide.
│   ├── TODO.md                       # Pending documentation and implementation notes.
│   ├── USAGE.md                      # CLI and Python API usage examples.
│
├── examples/                         # Small examples for users.
│   └── simple_usage.py               # Minimal Python API usage example.
│
├── scripts/                          # Maintenance and documentation scripts.
│   ├── generate_agents_markdown.sh   # Rebuilds AGENTS.md from agent-facing docs.
│   ├── generate_feature_md_from_json.py
│   │                                   # Generates docs/FEATURES.md from feature JSON metadata.
│   └── generate_root_readme.sh        # Rebuilds README.md from selected docs files.
│
├── src/                              # Python source root.
│   └── autofcholv/                   # Main package.
│       ├── __init__.py               # Package exports.
│       ├── cli.py                    # Command line interface.
│       ├── core.py                   # Public extract_features(df) API.
│       │
│       ├── config/                   # Configuration support.
│       │   ├── config.default.json   # Packaged default configuration.
│       │   └── config.py             # Default config values and config loading.
│       │
│       ├── pipeline/                 # OHLCV processing pipeline.
│       │   ├── README.md             # Pipeline overview and processing stages.
│       │   ├── cleaning.py           # Cleans and normalizes raw OHLCV data.
│       │   ├── validation.py         # Validates OHLCV schema and price logic.
│       │   ├── feature_engineering.py
│       │   │                           # Runs feature modules in the configured order.
│       │   ├── preprocessing.py      # Final cleanup before returning features.
│       │   │
│       │   └── features/             # Feature modules and their metadata.
│       │       ├── __init__.py       # Feature package marker.
│       │       ├── agglomerative.py  # Agglomerative hierarchical clustering features.
│       │       ├── agglomerative.json# Agglomerative feature metadata.
│       │       ├── birch.py          # BIRCH hierarchical clustering features.
│       │       ├── birch.json        # BIRCH feature metadata.
│       │       ├── candlestick.py    # Candlestick geometry features.
│       │       ├── candlestick.json  # Candlestick feature metadata.
│       │       ├── close.py          # Close-price momentum and oscillator features.
│       │       ├── close.json        # Close-price feature metadata.
│       │       ├── dbscan.py         # DBSCAN density-based clustering features.
│       │       ├── dbscan.json       # DBSCAN feature metadata.
│       │       ├── gmm.py            # Gaussian Mixture Model clustering and probabilistic regimes.
│       │       ├── gmm.json          # Gaussian Mixture Model feature metadata.
│       │       ├── group.py          # Grouped pattern/category features.
│       │       ├── group.json        # Group feature metadata.
│       │       ├── hdbscan.py        # HDBSCAN density clustering and noise detection.
│       │       ├── hdbscan.json      # HDBSCAN feature metadata.
│       │       ├── kmeans.py         # K-Means clustering features and market regimes.
│       │       ├── kmeans.json       # K-Means clustering feature metadata.
│       │       ├── lag.py            # Lagged OHLCV and indicator features.
│       │       ├── lag.json          # Lag feature metadata.
│       │       ├── liquidity.py      # Liquidity and market placement features.
│       │       ├── liquidity.json    # Liquidity feature metadata.
│       │       ├── mix.py            # Mixed and advanced composite features.
│       │       ├── mix.json          # Mixed feature metadata.
│       │       ├── optics.py         # OPTICS density-based clustering features.
│       │       ├── optics.json       # OPTICS feature metadata.
│       │       ├── price.py          # Price-derived features such as VWAP and typical price.
│       │       ├── price.json        # Price feature metadata.
│       │       ├── resample.py       # Daily resample and previous-day features.
│       │       ├── resample.json     # Resample feature metadata.
<<<<<<< HEAD
=======
│       │       ├── signal.py         # Signal/idea features.
│       │       ├── signal.json       # Signal feature metadata.
│       │       ├── spectral.py       # Spectral graph-based clustering features.
│       │       ├── spectral.json     # Spectral clustering feature metadata.
>>>>>>> b490e87 (develop(v0.4.0): update some clustering features)
│       │       ├── time.py           # Time/session features.
│       │       ├── time.json         # Time feature metadata.
│       │       ├── trend.py          # Trend and moving-average features.
│       │       ├── trend.json        # Trend feature metadata.
│       │       ├── volatility.py     # Volatility, bands, ATR, and channel features.
│       │       ├── volatility.json   # Volatility feature metadata.
│       │       ├── volume.py         # Volume and money-flow features.
│       │       └── volume.json       # Volume feature metadata.
│       │
│       └── utils/                    # Shared utilities.
│           ├── indicators.py         # Cached basic indicator calculation helpers.
│           └── timing.py             # Timing helpers for pipeline steps.
│
└── tests/                            # Automated tests.
    ├── test_cli.py                   # CLI tests.
    ├── test_core.py                  # Core extraction and feature coverage tests.
    ├── test_liquidity_proxies.py     # Fast isolated tests for liquidity and microstructure proxies.
    ├── test_regime_squeeze.py        # Fast isolated tests for TTM Squeeze and regime features.
    ├── test_smc_structure.py         # Fast isolated tests for SMC and price action structure features.
    └── test_volatility_estimators.py # Fast isolated tests for range-based volatility estimators.
```

## Notes

* Feature modules are wired into the pipeline in `src/autofcholv/pipeline/feature_engineering.py`.
* Feature metadata JSON files are used to generate `docs/FEATURES.md`.
* `README.md` is generated from selected files in `docs/` by `scripts/generate_root_readme.sh`.
* `AGENTS.md` is generated from agent-facing docs by `scripts/generate_agents_markdown.sh`.

# Autofcholv Git & Commit Conventions

This document establishes the Git workflow, commit message standards, branch naming rules, and pull request conventions for the `autofcholv` repository.

---

## 1. Commit Message Format

`autofcholv` enforces the following structured commit message format:

```
<branch>(v<version>): <short summary in lowercase>

[optional body providing detailed context, rationale, or breaking changes]

[optional footer(s) such as Closes #123, Refs #456]
```

### Components
1. **`<branch>`**: The current working branch name (e.g. `develop`, `feature/kmeans-clustering`, `main`).
2. **`v<version>`**: The exact project version defined in `pyproject.toml` (under `[project].version`, prefixed with `v`, e.g. `version = "0.3.0"` $\rightarrow$ `v0.3.0`).
   - **Source of Truth**: Always extract directly from `pyproject.toml`.
   - **No Version Guessing**: Do not calculate or predict future release versions (no `next_tag` or `next_version`). Always use the active version currently declared in `pyproject.toml`.
3. **`<short summary in lowercase>`**: Concise imperative description of the change starting with a lowercase letter (no trailing period).

### Examples
- `develop(v0.3.0): add kmeans clustering feature module with 10 default clusters`
- `feature/entropy-features(v0.3.0): implement rolling hurst exponent and shannon entropy`
- `fix/resample-leakage(v0.3.0): resolve lookahead bias in htf resample`
- `main(v0.3.0): release autofcholv 0.3.0 version`

### Rules & Formatting
- **Subject line length**: Maximum 72 characters.
- **Tense & Mood**: Use imperative present tense ("add", "fix", "update", NOT "added", "fixing").
- **Case**: Summary starts with a lowercase letter.
- **No trailing period**: Do not end the subject line with a period `.`.

---

## 2. Branch Naming Conventions

All branch names must be lowercase, hyphen-separated, and prefixed with the category:

```
<prefix>/<short-description>
```

### Branch Prefixes:
- `feature/<name>`: New features or indicators (e.g. `feature/kmeans-clustering`, `feature/entropy-dynamics`)
- `fix/<issue>`: Bug fixes (e.g. `fix/resample-nan-handling`, `fix/cli-empty-df`)
- `perf/<target>`: Performance optimizations (e.g. `perf/vectorize-indicators`)
- `docs/<topic>`: Documentation enhancements (e.g. `docs/update-feature-catalog`)
- `refactor/<scope>`: Code refactoring (e.g. `refactor/modularize-feature-steps`)

---

## 3. Workflow & Invariants

1. **Atomic Commits**: Each commit should represent a single logical change that passes all tests and linter checks.
2. **Pre-Commit Verification**:
   Before committing, always run relevant targeted tests:
   ```bash
   uv run pytest tests/test_core.py::<test_name> -q
   uv run pytest tests/test_cli.py -q
   ```
   *(Note: Do NOT run the full test suite `uv run pytest` automatically without explicit user approval due to heavy computation time).*
3. **Documentation Sync**:
   - When feature metadata changes, regenerate the feature catalog:
     ```bash
     uv run python scripts/generate_feature_md_from_json.py
     ```
   - When source docs for root README change, regenerate:
     ```bash
     bash scripts/generate_root_readme.sh
     ```
   - When agent-facing docs change, recompile:
     ```bash
     bash scripts/generate_agents_markdown.sh
     ```
4. **Gitignore Verification Before Commits**:
   Always check all `.gitignore` files (root `.gitignore` and any subfolder `.gitignore`) before staging or committing any file. Never force-add (`git add -f`) or commit files and directories that match `.gitignore` rules (such as `.venv`, `__pycache__`, cached data, or scratch files).
