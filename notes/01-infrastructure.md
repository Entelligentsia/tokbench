# Infrastructure Notes

## Image lineage (pins in ../bench/pins.env)

```
node:24-bookworm-slim (digest-pinned)
└─ tokbench-base:0.1   Dockerfile: 4ge.sh installer (forgecli 1.0.21), testbench git
   │                   bundle (local repo, 2 ahead of origin), npm ci, host .forge
   │                   tools, build gate: reset.sh must report PRISTINE
└─ tokbench-base:0.2   = 0.1 + interactive layer (Boni): pi via pi.dev installer,
   │                   pi-ollama-cloud ext, ollama-cloud auth, persona-model map
└─ tokbench-base:0.4   = 0.2 + in-container /forge:init  ← CANONICAL BASE
   │                   (0.3 = deprecated host-grafted scaffolding hotfix)
   ├─ tokbench-arm-a1:0.2  + lean-ctx 3.7.3 + pi-lean-ctx + init --agent pi  (ran a1 rep-1)
   ├─ tokbench-arm-a1:0.3  + fixed harvest (transcript engage-check, XDG paths)
   │  ├─ tokbench-arm-a1m:0.1  DEAD-END (env alone; mcp.json neutralized it)
   │  └─ tokbench-arm-a1m:0.2  + LEAN_CTX_PI_ENABLE_MCP=1 + rm mcp.json (build+per-reset)
```

⚠ 0.2+ contain ollama-cloud credentials (~/.pi/agent/auth.json) — NEVER push to a registry.
⚠ 0.2/0.4 are committed images, NOT Dockerfile-reproducible (auth+init are interactive).
   Arm images bake updated scripts because base can't be rebuilt without redoing setup.

## Build gotchas (hit & fixed 2026-06-05)

1. forge npm tgz references `file:./vendor-pi/*.tgz` deps it doesn't contain
   → use official installer `curl -fsSL https://4ge.sh | sh`  [forge-cli bug to report]
2. `reset.sh` needs `python3` (MANIFEST verification)
3. golden state.tgz carries only `.forge/{store,cache}` — NO tools/, NO init scaffolding;
   `/forge:run-task` detects project by `.forge/config.json` (run-task.ts:749)
   → base 0.4 has scaffolding from in-container /forge:init
4. Node 20 breaks forgecli at runtime: undici needs `util.markAsUncloneable` (Node ≥23)
   → node:24 base (matches host v24.3.0)
5. `/forge:init` materializes `.forge/tools/` WITHOUT its `package.json` ({"type":"commonjs"})
   → `lib/result.js` (CJS, .js ext) explodes under cartographer's "type":"module";
   breaks collate during runs. Fix: `echo '{ "type": "commonjs" }' > .forge/tools/package.json`
   [forge-cli 1.0.21 bug to report — applied to host repo too]
6. RESET WIPES PROJECT-LEVEL ARM FILES: reset.sh does git restore + git clean scoped to
   the project → reverts AGENTS.md (tracked), removes LEAN-CTX.md / .pi/extensions/*.ts
   (untracked). Fix: `arm-setup.sh` hook called by run-task.sh AFTER reset, re-applies
   arm integration. EVERY arm with project-level files needs this (a1 ✓, a3 will).

## Run command template

```bash
mkdir -p ~/src/context-mnagers-benchmark/results/<arm>-<task>-r<rep> && chmod 777 $_
docker run -it \
  --name tokbench-<arm>-<task>-r<rep> \            # NO --rm (forensics)
  -e ARM=<a0|a1|a2|a3> -e TASK=CART-S01-T01 -e REP=<n> \
  -e TOKBENCH_IMAGE=<image:tag> \
  -v ~/src/context-mnagers-benchmark/results/<arm>-<task>-r<rep>:/results \
  <image:tag>
# inside forge: /forge:run-task CART-S01-T01 ; observe-only; exit → harvest fires
```

For a0 runs from base 0.4 (old harvest baked): add
`-v ~/src/context-mnagers-benchmark/bench/docker/base/harvest.sh:/usr/local/bin/harvest.sh:ro`

## Harvest contract (bench/docker/base/harvest.sh)

PRIMARY: `.forge/transcripts/` → `$DEST/transcripts/` verbatim.
Also: run-summary.tsv (jq extraction), forge-store, sprint dirs, pi-sessions,
gates.txt (build/test/lint exit codes), run-manifest.json, per-arm self-metrics:
- a1: ~/.config/lean-ctx/ + ~/.local/share/lean-ctx/ + `lean-ctx gain --deep` (v3.7.3 XDG paths; NOT ~/.lean-ctx)
- a3: rtk gain --json + --history
- a2: headroom /stats
Engage-check ground truth = count ctx_*/rtk-prefixed calls in transcripts, not state files.

## Transcript schema & analysis snippets

Per-phase file: `.forge/transcripts/<TASK>/<ts>__<TASK>__<phase>.json`
Keys: usage{input,output,cacheRead,cacheWrite,contextTokens,turns}, model, provider,
persona, startedAt/finishedAt, messageCount, messages[], stopReason, errorMessage.
messages[]: role=assistant content[].type=thinking|text|toolCall{id,name,arguments};
role=toolResult {toolCallId, toolName, isError, content[].text}.

Per-phase summary:
```bash
for f in *__*.json; do jq -r '[(.tag//"?"),.provider,.model,.usage.input,.usage.output,.usage.contextTokens,.usage.turns,.messageCount,(((.finishedAt|sub("\\.[0-9]+Z$";"Z")|fromdateiso8601)-(.startedAt|sub("\\.[0-9]+Z$";"Z")|fromdateiso8601))),.stopReason,(.errorMessage//"-")]|@tsv' "$f"; done
```

Per-tool traffic+errors (the mechanism decomposition):
```bash
for f in *__*.json; do jq -r '(.messages|map(select(.role=="assistant")|.content[]?|select(.type=="toolCall")|{id,name})|INDEX(.id)) as $calls | .messages[]|select(.role=="toolResult") | [($calls[.toolCallId//"?"].name // .toolName // "UNMATCHED"), ((.content|map(.text//""|length)|add)//0), (.isError//false)]|@tsv' "$f"; done \
| awk -F'\t' '{n[$1]++;b[$1]+=$2;if($3=="true")e[$1]++} END{for(t in n) printf "%-22s calls=%-4d chars=%-8d errors=%d\n",t,n[t],b[t],e[t]+0}'
```

ctx_read per-call audit (path, mode, returned size — compare vs `wc -c` of file on disk):
```bash
for f in *__*.json; do jq -r '(.messages|map(select(.role=="assistant")|.content[]?|select(.type=="toolCall")|{id,name,arguments})|INDEX(.id)) as $calls | .messages[]|select(.role=="toolResult") | ($calls[.toolCallId//"?"]//{}) as $c | select($c.name=="ctx_read") | [($c.arguments.path//"?"),($c.arguments.mode//"auto"),((.content|map(.text//""|length)|add)//0),(.isError//false)]|@tsv' "$f"; done
```

## Offline collate (if COST_REPORT wanted)

Spin throwaway container from base, overlay harvested store+transcripts, ensure
.forge/tools/package.json exists, run `node .forge/tools/collate.cjs` (no args; no --help mode).
