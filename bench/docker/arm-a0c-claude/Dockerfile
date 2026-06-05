# tokbench-arm-a0c — 4ge NATIVE on ANTHROPIC models (no middleware).
# Same harness, same task, same pipeline as A0; only the provider + persona
# tier map change: glm-5.1->opus-4-8, glm-4.7->sonnet-4-6, glm-4.6->haiku-4-5.
# Anthropic is a pi-ai builtin provider; auth = runtime -e ANTHROPIC_API_KEY.
# Measures: cache economics on the lean harness (cacheRead/Write in transcripts)
# and the real dollar cost vs the $1.81 projection / c0's $6.09.
FROM tokbench-base:1.0
COPY --chown=bench:bench config/pi-agent-settings.json /home/bench/.pi/agent/settings.json
COPY --chown=bench:bench config/forge-cli-config.json  /home/bench/.pi/forge-cli/config.json
