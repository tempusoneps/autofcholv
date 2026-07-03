# Project Rules

## Keep Structure Documentation In Sync

Any change that affects the repository layout must update `docs/STRUCTURE.md` in the same change set.

This includes adding, deleting, moving, or renaming files and directories.

## Keep Feature Metadata In Sync

Any change that adds, removes, or renames generated feature columns in `src/autofcholv/pipeline/features/*.py` must update the matching `src/autofcholv/pipeline/features/*.json` file.

## Keep Signal And Strategy Modules Signal-Only

Do not write code that creates new indicators or non-signal features in `src/autofcholv/pipeline/features/signal.py` or `src/autofcholv/pipeline/features/strategy.py`.

These files must only create signal columns and signal-calculation helpers derived from features or indicators that were already created by earlier pipeline modules.

## Regenerate Generated Documentation

When feature metadata changes, regenerate the feature catalog:

```bash
python3 scripts/generate_feature_md_from_json.py
```

When files used by the root README change, regenerate the root README:

```bash
scripts/generate_root_readme.sh
```

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

When changing pipeline, feature, preprocessing, validation, config, or CLI behavior, run the relevant tests.

If tests cannot be run, note the reason in the final change summary.

## Keep Documentation Links Valid

When moving, renaming, adding, or deleting documentation/source files, update all affected links in `README.md`, `docs/*.md`, and pipeline docs.
