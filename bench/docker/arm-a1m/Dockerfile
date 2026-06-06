# tokbench-arm-a1m:1.1 — lean-ctx with embedded MCP bridge, on the reproducible base.
# Protocol Amendment A1: lean-ctx 3.7.4 (maintainer fix for the mcp.json bridge-defeat
# bug we reported in yvgude/lean-ctx#361); the rm-mcp.json workaround is DROPPED —
# on 3.7.4 LEAN_CTX_PI_ENABLE_MCP=1 wins regardless of mcp.json (flag-wins behavior
# is the configuration under test). History: 1.0 = 3.7.3 + workaround (pilot config).

FROM tokbench-base:1.0

ENV PATH=/home/bench/.local/bin:$PATH
ENV LEAN_CTX_NO_UPDATE_CHECK=1
ENV LEAN_CTX_PI_ENABLE_MCP=1

# binary: lean-ctx v3.7.4, vendored + verified (hermetic build)
COPY --chown=bench:bench lean-ctx-3.7.4-x86_64-unknown-linux-gnu.tar.gz /tmp/leanctx.tgz
RUN echo "878dff4b243f7022bf27485ae2808a160390c30286502859305e658aad173b51  /tmp/leanctx.tgz" | sha256sum -c - \
 && mkdir -p /home/bench/.local/bin \
 && tar -xzf /tmp/leanctx.tgz -C /home/bench/.local/bin \
 && rm /tmp/leanctx.tgz \
 && lean-ctx --version

# pi extension: exact pin + register in pi settings packages
RUN cd /home/bench/.pi/agent/npm \
 && npm install --legacy-peer-deps --no-audit --no-fund pi-lean-ctx@3.7.4 \
 && jq '.packages += ["npm:pi-lean-ctx"]' /home/bench/.pi/agent/settings.json > /tmp/s.json \
 && mv /tmp/s.json /home/bench/.pi/agent/settings.json

# project rules (re-done per reset by arm-setup); mcp.json left as init writes it —
# 3.7.4 explicit-flag-wins makes the old removal workaround unnecessary (A1)
RUN cd /home/bench/forge-testbench/cartographer && lean-ctx init --agent pi

COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
