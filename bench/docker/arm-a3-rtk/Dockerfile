# arm-a3-rtk — tokbench arm A3: rtk (command-level interception)
# = canonical base + rtk binary + pi extension (tool_call event -> `rtk rewrite`
#   mutates bash commands in place; transparent, rewrite-only, never blocks)
# Registry is compiled into the binary and active by default — no config needed.
# Known coverage gaps on this harness (see notes/03): `node scripts/*.cjs`
# (forge store-cli) and `npm install` pass through unrewritten.

FROM tokbench-base:0.4

ENV PATH=/home/bench/.local/bin:$PATH
ENV RTK_TELEMETRY_DISABLED=1

# binary via the project's installer (pinned copy from the cloned repo);
# downloads the prebuilt musl release binary
COPY --chown=bench:bench rtk-install.sh /tmp/rtk-install.sh
RUN sh /tmp/rtk-install.sh && rm /tmp/rtk-install.sh \
 && rtk --version | tee /home/bench/rtk-version.txt \
 && rtk gain >/dev/null   # sanity: correct rtk (not "Rust Type Kit"), tracking works

# pi extension: project-local .pi/extensions/rtk.ts (re-applied per reset by arm-setup)
RUN cd /home/bench/forge-testbench/cartographer && rtk init --agent pi

# updated runner (arm-setup hook) + harvest + the a3 re-init hook
# (baked because base 0.4 is a committed image, not Dockerfile-rebuildable)
COPY --chown=bench:bench --chmod=755 run-task.sh harvest.sh arm-setup.sh /usr/local/bin/
