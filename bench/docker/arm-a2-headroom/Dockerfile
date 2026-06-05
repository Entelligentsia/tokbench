# arm-a2-headroom runner — base + scripts only; interception is wire-level
# (OLLAMA_API_BASE -> headroom sidecar, set by compose). No project files, no arm-setup.
FROM tokbench-base:0.4
COPY --chown=bench:bench --chmod=755 run-task.sh harvest.sh /usr/local/bin/
