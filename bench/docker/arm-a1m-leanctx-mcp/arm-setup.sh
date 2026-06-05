#!/usr/bin/env bash
# a1m arm-setup — lean-ctx project rules + ensure embedded MCP bridge engages:
# init writes ~/.pi/agent/mcp.json (an MCP adapter config); pi has NO mcp adapter,
# yet its presence makes the extension disable its own bridge. Remove it so
# LEAN_CTX_PI_ENABLE_MCP=1 starts the embedded bridge (persistent server).
set -euo pipefail
cd /home/bench/forge-testbench/cartographer
lean-ctx init --agent pi >/dev/null 2>&1
rm -f ~/.pi/agent/mcp.json .pi/mcp.json
echo "  ✓ arm-a1m: lean-ctx rules re-applied; stale mcp.json removed (embedded bridge will engage)"
