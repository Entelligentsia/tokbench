#!/usr/bin/env bash
# a1m arm-setup — re-apply lean-ctx project rules after golden reset.
# Amendment A1: on 3.7.4 LEAN_CTX_PI_ENABLE_MCP=1 starts the embedded bridge
# regardless of mcp.json (flag wins), so the old rm-mcp.json workaround is gone.
# Gate at session start remains: /lean-ctx must show "MCP bridge: embedded (connected)".
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
lean-ctx init --agent pi >/dev/null 2>&1
echo "  ✓ arm-a1m: lean-ctx rules re-applied (3.7.4, embedded bridge via env flag)"
