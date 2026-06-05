# tokbench-arm-a3:1.0 — rtk on the reproducible base.
# Vendored binary (sha256-verified). Registry is compiled-in and active by default;
# pi extension is a transparent tool_call rewrite (.pi/extensions/rtk.ts, re-applied
# per reset by arm-setup since git clean wipes it).

FROM tokbench-base:1.0

ENV PATH=/home/bench/.local/bin:$PATH
ENV RTK_TELEMETRY_DISABLED=1

# binary: rtk v0.42.2, vendored + verified (hermetic build)
COPY --chown=bench:bench rtk-x86_64-unknown-linux-musl.tar.gz /tmp/rtk.tgz
RUN echo "17ae2592fe6dcfc62d0bc4faea89ce520d818801581ff0a8394335f72c91154d  /tmp/rtk.tgz" | sha256sum -c - \
 && mkdir -p /home/bench/.local/bin \
 && tar -xzf /tmp/rtk.tgz -C /home/bench/.local/bin \
 && rm /tmp/rtk.tgz \
 && rtk --version \
 && rtk gain >/dev/null   # sanity: correct rtk, tracking works

# pi extension (project-local; reset wipes it -> arm-setup re-applies)
RUN cd /home/bench/forge-testbench/cartographer && rtk init --agent pi

COPY --chown=bench:bench --chmod=755 arm-setup.sh /usr/local/bin/arm-setup.sh
