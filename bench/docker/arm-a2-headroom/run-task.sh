#!/usr/bin/env bash
# tokbench run-task.sh — interactive run entrypoint
# reset to PRISTINE -> launch interactive forge session -> harvest on exit
set -euo pipefail

ARM="${ARM:-a0}"
TASK="${TASK:-}"
REP="${REP:-1}"

cd /home/bench/forge-testbench
./testbench/reset.sh cartographer

# arm-specific project re-integration (reset wipes project-level rules files);
# no-op unless the arm image installed a hook
if [ -x /usr/local/bin/arm-setup.sh ]; then
  /usr/local/bin/arm-setup.sh
fi

cd cartographer

echo
echo "┌──────────────────────────────────────────────────────────"
echo "│ tokbench  arm=${ARM}  task=${TASK:-<choose in session>}  rep=${REP}"
echo "│ Operator protocol: type the single /forge:run-task invocation,"
echo "│ then observe only. Prompts -> documented defaults."
echo "└──────────────────────────────────────────────────────────"
echo

START_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# interactive TUI session — operator drives; harvest runs when forge exits
forge || true

END_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
export ARM TASK REP START_TS END_TS

harvest.sh "${RESULTS_DIR:-/results}"
