# tokbench-base — common layer for all eval arms
# Everything identical across arms lives here; arm images add ONLY the product under test.
# See: entelligentsia.in/research/context-optimization-market/10-eval-experiment-design.md

# node:24-bookworm-slim — Node 24 to match the host environment (forgecli's
# undici needs util.markAsUncloneable, a Node >=23 API; Node 20 fails at runtime)
FROM node@sha256:242549cd46785b480c832479a730f4f2a20865d61ea2e404fdb2a5c3d3b73ecf

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates tar jq ripgrep procps python3 \
 && rm -rf /var/lib/apt/lists/*

# ── forge-cli (4ge) via the official installer ───────────────────────────────
# Installs latest @entelligentsia/forgecli from npm (self-contained publish).
# Installed version is recorded at build time and must be copied into pins.env.
RUN curl -fsSL https://4ge.sh | sh \
 && forge --version | tee /forge-version.txt

# ── non-root user: disposable $HOME per container (cold state by construction) ─
RUN useradd -m bench
USER bench
WORKDIR /home/bench
RUN git config --global user.name "Tokbench Runner" \
 && git config --global user.email "tokbench@bench.local" \
 && git config --global init.defaultBranch main

# ── forge-testbench from local git bundle ────────────────────────────────────
# Bundle (not GitHub clone): local repo is ahead of origin; bundle carries all
# refs incl. the testbench/cartographer-baseline tag that reset.sh requires.
COPY --chown=bench:bench testbench.bundle /tmp/testbench.bundle
RUN git clone /tmp/testbench.bundle /home/bench/forge-testbench \
 && cd /home/bench/forge-testbench && git checkout main \
 && rm /tmp/testbench.bundle

RUN cd /home/bench/forge-testbench/cartographer && npm ci

# ── .forge/ init scaffolding: copied from the host's live cartographer/.forge ─
# golden state.tgz carries only .forge/{store,cache}. Everything else is
# /forge:init-generated and required for project detection (run-task checks
# .forge/config.json): config.json, personas/, workflows/, schemas/, templates/,
# skills/, tools/, pi-settings.json, project-context.json, init-context.*.
# Host scaffolding is used verbatim (version-matched to forgecli 1.0.21; host
# tools differ from the npm payload: lib/validate.cjs, store-cli.cjs).
# forge-project.tgz = host .forge/ minus store/, cache/, transcripts/, *.log
COPY --chown=bench:bench forge-project.tgz /tmp/forge-project.tgz
RUN mkdir -p /home/bench/forge-testbench/cartographer/.forge \
 && cd /home/bench/forge-testbench/cartographer/.forge \
 && tar -xzf /tmp/forge-project.tgz && rm /tmp/forge-project.tgz

# ── build-time gate: golden restore must verify PRISTINE ─────────────────────
RUN cd /home/bench/forge-testbench && ./testbench/reset.sh cartographer

COPY --chown=bench:bench --chmod=755 run-task.sh harvest.sh /usr/local/bin/

ENV TERM=xterm-256color
WORKDIR /home/bench/forge-testbench/cartographer
ENTRYPOINT ["/usr/local/bin/run-task.sh"]
