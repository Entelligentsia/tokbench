#!/usr/bin/env bash
# a1 arm-setup — re-apply lean-ctx project integration after golden reset
# (reset.sh's git restore/clean reverts AGENTS.md and removes LEAN-CTX.md)
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
lean-ctx init --agent pi >/dev/null 2>&1
echo "  ✓ arm-a1: lean-ctx project rules re-applied (AGENTS.md + LEAN-CTX.md)"
