# tokbench-arm-a1m:1.0 — lean-ctx with embedded MCP bridge, on the reproducible base.
# Vendored binary (sha256-verified), exact-pinned pi extension, bridge enabled,
# init-written mcp.json removed (it would defer the bridge to a nonexistent pi
# MCP adapter — see notes/03). Single image; the a1-default arm is dropped.

FROM tokbench-base:1.0

ENV PATH=/home/bench/.local/bin:$PATH
ENV LEAN_CTX_NO_UPDATE_CHECK=1
ENV LEAN_CTX_PI_ENABLE_MCP=1

# binary: lean-ctx v3.7.3, vendored + verified (hermetic build)
COPY --chown=bench:bench lean-ctx-x86_64-unknown-linux-gnu.tar.gz /tmp/leanctx.tgz
RUN echo "d034a6d1345db39057f9dc54c4a2536ed3f5805aa2ef6ec080f685190b014a47  /tmp/leanctx.tgz" | sha256sum -c - \
 && mkdir -p /home/bench/.local/bin \
 && tar -xzf /tmp/leanctx.tgz -C /home/bench/.local/bin \
 && rm /tmp/leanctx.tgz \
 && lean-ctx --version

# pi extension: exact pin + register in pi settings packages
RUN cd /home/bench/.pi/agent/npm \
 && npm install --legacy-peer-deps --no-audit --no-fund pi-lean-ctx@3.7.3 \
 && jq '.packages += ["npm:pi-lean-ctx"]' /home/bench/.pi/agent/settings.json > /tmp/s.json \
 && mv /tmp/s.json /home/bench/.pi/agent/settings.json

# project rules + REMOVE the bridge-defeating mcp.json (re-done per reset by arm-setup)
RUN cd /home/bench/forge-testbench/cartographer && lean-ctx init --agent pi \
 && rm -f /home/bench/.pi/agent/mcp.json .pi/mcp.json

COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
