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
5. **No Automatic Commits by AI Agents**:
   AI agents must **NEVER** create git commits automatically (`git commit`). Always ask the user for confirmation and get explicit approval before executing any commit command.
