#!/usr/bin/env bash
# a1m arm-setup — re-apply lean-ctx project rules after golden reset.
# Amendment A2: on 3.7.5 the embedded bridge is ON BY DEFAULT (no env var, mcp.json
# harmless), and all ctx_read variants route through the bridge session cache.
# Gate at session start remains: /lean-ctx must show "MCP bridge: embedded (connected)".
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
lean-ctx init --agent pi >/dev/null 2>&1
echo "  ✓ arm-a1m: lean-ctx rules re-applied (3.7.5, embedded bridge default-on)"
