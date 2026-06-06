#!/usr/bin/env bash
# a1f arm-setup — lean-ctx rules + forge-routing addendum after golden reset.
# reset.sh wipes LEAN-CTX.md (untracked) -> re-init recreates the stock rules,
# then we append the project-routing addendum (lean-ctx preserves user content
# outside its markers on re-init; verified on 3.7.4).
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
lean-ctx init --agent pi >/dev/null 2>&1
if ! grep -q "project-routing: forge" LEAN-CTX.md 2>/dev/null; then
  cat /usr/local/share/tokbench/leanctx-routing-addendum.md >> LEAN-CTX.md
fi
echo "  ✓ arm-a1f: lean-ctx rules + forge-routing addendum applied (3.7.4, embedded bridge via env flag)"
