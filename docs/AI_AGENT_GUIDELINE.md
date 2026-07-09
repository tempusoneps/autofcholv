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
- For TDD and debugging, first run the smallest relevant test selection, such as `uv run pytest tests/test_core.py::test_name -q`, then run a focused file, and run `uv run pytest` only before final handoff or when the change touches shared pipeline behavior.
- For CLI tests, avoid exercising the complete wide feature catalog unless the test is explicitly checking end-to-end extraction. Prefer mocking or a minimal configuration path when testing argument parsing, logging, validation errors, or file handling.
- Treat performance regressions in tests as maintenance issues. If a new test adds another full-pipeline extraction, consider whether it can reuse an existing fixture or test the owning feature module directly.

#### Commit & Pull Request Guidelines

Recent commits use short, imperative messages such as `add quanlify signal features` and `remove leakage features`. Keep commits focused and describe the behavior changed. Pull requests should include a concise summary, test results, linked issues when relevant, and sample CLI output or screenshots only when user-facing behavior changes.

#### Agent-Specific Instructions

For Codex work in this repository, prefix shell commands with `rtk` as required by the local instructions, for example `rtk git status` or `rtk pytest -q`. Before editing, check `git status --short` and avoid overwriting unrelated user changes.
