#!/usr/bin/env bash
# a3 arm-setup — re-install rtk pi extension after golden reset
# (rtk init --agent pi writes .pi/extensions/rtk.ts, untracked -> git clean wipes it)
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
rtk init --agent pi >/dev/null 2>&1
echo "  ✓ arm-a3: rtk pi extension re-applied (.pi/extensions/rtk.ts)"
