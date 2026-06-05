# arm-a1m — A1 + lean-ctx embedded MCP bridge ENABLED and able to engage
# (removes the init-written mcp.json that otherwise makes the extension defer
# to a nonexistent pi MCP adapter and silently fall back to one-shot CLI)
FROM tokbench-arm-a1:0.3
ENV LEAN_CTX_PI_ENABLE_MCP=1
COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
RUN rm -f /home/bench/.pi/agent/mcp.json
