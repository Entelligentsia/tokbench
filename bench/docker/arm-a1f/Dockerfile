# tokbench-arm-a1f:0.1 — lean-ctx 3.7.4 + project-routing addendum (EXPLORATORY).
# Tests the adoption ceiling: lean-ctx's own project rules file (LEAN-CTX.md,
# imported into context via AGENTS.md @-ref) carries a forge-specific routing
# table mapping the workflows' prescribed commands to ctx_* tools. ZERO changes
# to forge scaffolding — the harness is byte-identical to all other arms.
# Triplet: A0 (native) vs a1m (vendor-stock adoption) vs a1f (max legitimate adoption).

FROM tokbench-arm-a1m:1.1

COPY --chown=bench:bench leanctx-routing-addendum.md /usr/local/share/tokbench/leanctx-routing-addendum.md

# apply at build for parity with the per-reset hook
RUN cd /home/bench/forge-testbench/cartographer \
 && cat /usr/local/share/tokbench/leanctx-routing-addendum.md >> LEAN-CTX.md \
 && grep -q "project-routing: forge" LEAN-CTX.md

COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
