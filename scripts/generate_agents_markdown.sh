#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS="$ROOT_DIR/AGENTS.md"

DOCS=(
  "docs/AI_AGENT_GUIDELINE.md"
  "docs/RULE.md"
  "docs/STRUCTURE.md"
)

cat > "$AGENTS" <<'EOF'
# Agent Guide

This file is generated from project documentation. Do not edit it directly.

EOF

for doc in "${DOCS[@]}"; do
  echo "" >> "$AGENTS"
  cat "$ROOT_DIR/$doc" >> "$AGENTS"
done

echo "Generated AGENTS.md"
