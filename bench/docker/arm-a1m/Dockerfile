# tokbench-arm-a1m:1.2 — lean-ctx with embedded MCP bridge, on the reproducible base.
# Protocol Amendment A2: lean-ctx 3.7.5 (maintainer fix for the structural read-path
# finding we reported in yvgude/lean-ctx#361 — extension read tools spawned one-shot
# CLI subprocesses even with the bridge connected, so reads never touched the session
# cache). On 3.7.5 the bridge is ON BY DEFAULT and every ctx_read routes through it;
# the LEAN_CTX_PI_ENABLE_MCP=1 env var is DROPPED — the configuration under test is
# the as-shipped default. History: 1.0 = 3.7.3 + rm-mcp.json workaround (pilot);
# 1.1 = 3.7.4 + env flag (Amendment A1).

FROM tokbench-base:1.0

ENV PATH=/home/bench/.local/bin:$PATH
ENV LEAN_CTX_NO_UPDATE_CHECK=1

# binary: lean-ctx v3.7.5, vendored + verified (hermetic build)
COPY --chown=bench:bench lean-ctx-3.7.5-x86_64-unknown-linux-gnu.tar.gz /tmp/leanctx.tgz
RUN echo "c586afe64114142bae360b5c27f3618d2fbe4f82ba4b3e0642096f33b268e4d3  /tmp/leanctx.tgz" | sha256sum -c - \
 && mkdir -p /home/bench/.local/bin \
 && tar -xzf /tmp/leanctx.tgz -C /home/bench/.local/bin \
 && rm /tmp/leanctx.tgz \
 && lean-ctx --version

# pi extension: exact pin + register in pi settings packages
RUN cd /home/bench/.pi/agent/npm \
 && npm install --legacy-peer-deps --no-audit --no-fund pi-lean-ctx@3.7.5 \
 && jq '.packages += ["npm:pi-lean-ctx"]' /home/bench/.pi/agent/settings.json > /tmp/s.json \
 && mv /tmp/s.json /home/bench/.pi/agent/settings.json

# project rules (re-done per reset by arm-setup); mcp.json left as init writes it —
# 3.7.5 bridge-default-on makes both the removal workaround (pilot) and the env
# flag (A1) unnecessary (A2)
RUN cd /home/bench/forge-testbench/cartographer && lean-ctx init --agent pi

COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
