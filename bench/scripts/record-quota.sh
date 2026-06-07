#!/usr/bin/env bash
# Record a quota snapshot (before or after a run) to the results directory.
# Usage:
#   record-quota.sh before <results-dir> <pct-used>
#   record-quota.sh after  <results-dir> <pct-used>
# Example:
#   record-quota.sh before ~/src/context-mnagers-benchmark/results/a0-T-fix-r3 72.1
#   record-quota.sh after  ~/src/context-mnagers-benchmark/results/a0-T-fix-r3 75.3
set -euo pipefail

WHEN="${1:?usage: $0 before|after <results-dir> <pct-used>}"
DEST="${2:?usage: $0 before|after <results-dir> <pct-used>}"
PCT="${3:?usage: $0 before|after <results-dir> <pct-used>}"

mkdir -p "$DEST"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

FILE="$DEST/quota-${WHEN}.json"
cat > "$FILE" <<EOF
{
  "when": "$WHEN",
  "timestamp": "$TS",
  "pct_used": $PCT,
  "pct_remaining": $(echo "100 - $PCT" | bc -l | xargs printf "%.1f"),
  "source": "ollama-cloud dashboard (operator reading)"
}
EOF

echo "quota-${WHEN}: ${PCT}% used ($(echo "100 - $PCT" | bc -l | xargs printf "%.1f")% remaining) → $FILE"
