# arm-a1-leanctx — tokbench arm A1: lean-ctx (tool-level interception)
# = canonical base + lean-ctx binary + pi integration (vendor-shipped paths only)
# Attach mechanism: `lean-ctx init --agent pi` (rules) + `pi install npm:pi-lean-ctx` (extension)

FROM tokbench-base:0.4

ENV PATH=/home/bench/.local/bin:$PATH
ENV LEAN_CTX_NO_UPDATE_CHECK=1

# binary via the project's installer (pinned copy from the cloned repo);
# --download fetches the prebuilt release binary (no Rust toolchain needed)
COPY --chown=bench:bench install.sh /tmp/leanctx-install.sh
RUN sh /tmp/leanctx-install.sh --download \
 && rm /tmp/leanctx-install.sh \
 && lean-ctx --version | tee /home/bench/leanctx-version.txt

# pi extension (vendor's first-class pi integration)
RUN pi install npm:pi-lean-ctx

# project-level integration: writes the vendor's canonical agent rules
RUN cd /home/bench/forge-testbench/cartographer && lean-ctx init --agent pi

# updated runner (arm-setup hook support) + harvest + the a1 re-integration hook
# (baked here because base 0.4 is a committed image, not Dockerfile-rebuildable)
COPY --chown=bench:bench --chmod=755 run-task.sh harvest.sh arm-setup.sh /usr/local/bin/
