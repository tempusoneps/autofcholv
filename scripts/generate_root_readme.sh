#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
README="$ROOT_DIR/README.md"

DOCS=(
  "docs/FEATURES_OVERVIEW.md"
  "docs/INSTALLATION.md"
  "docs/USAGE.md"
  "docs/CONFIGURATION.md"
  "docs/RESOURCES.md"
)

cat > "$README" <<'EOF'
# autofcholv

A Python library for Automated extraction of relevant features from OHLCV time series data. Designed to help quantitative researchers and traders quickly generate a massive set of highly predictive features from basic pricing and volume data.
EOF

for doc in "${DOCS[@]}"; do
  echo "" >> "$README"
  cat "$ROOT_DIR/$doc" >> "$README"
done

echo "Generated README.md"
