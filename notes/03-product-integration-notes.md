# Product Integration Notes (for fully-effective arm runs)

Lesson driving this file: lean-ctx's as-shipped pi default silently ran a degraded
path. Each product was audited for equivalent gotchas BEFORE its arm runs.

## lean-ctx 3.7.3 on pi (a1 / a1m) — three-layer integration

1. Binary `~/.local/bin/lean-ctx` (release via repo install.sh --download).
2. `pi install npm:pi-lean-ctx` → native pi ExtensionAPI extension (NOT MCP):
   registers ctx_shell/ctx_read/ctx_ls/ctx_find/ctx_grep + lean_ctx meta-tool,
   each call = one-shot CLI subprocess by default.
   - Modes: `additive` (default; pi builtins kept alongside) | `replace` (builtins off).
     Config: ~/.pi/agent/extensions/pi-lean-ctx/config.json or LEAN_CTX_PI_* env.
   - **Embedded MCP bridge** (persistent server, session cache, the ~13-tok re-read
     value prop): OPT-IN — `enableMcp: true` or `LEAN_CTX_PI_ENABLE_MCP=1`
     (config.ts:97-100). When connected: +9 MCP tools (ctx_call/edit/expand/graph/
     knowledge/overview/provider/session/shell). Status line must read
     "MCP bridge: embedded (connected)".
   - **TRAP:** `lean-ctx init --agent pi` writes ~/.pi/agent/mcp.json (mcpServers.lean-ctx).
     isMcpAdapterConfigured() (index.ts:277-292) sees it → extension defers to a pi MCP
     adapter THAT DOESN'T EXIST (pi has no MCP) → bridge disabled even with env set
     ("adapter-configured"). Fix: rm ~/.pi/agent/mcp.json (+ project .pi/mcp.json) after
     every init — baked into a1m arm-setup.sh.
3. `lean-ctx init --agent pi` project rules: rewrites AGENTS.md (tracked!) + LEAN-CTX.md
   (untracked) + ~/.pi/rules/lean-ctx.md (global). reset.sh wipes the project two →
   arm-setup re-init required every reset.

State paths (v3.7.3, XDG — research notes saying ~/.lean-ctx are STALE):
~/.config/lean-ctx/ (stats.json) · ~/.local/share/lean-ctx/.

### Maintainer response → 3.7.4 (Amendment A1, 2026-06-06)

lean-ctx#361: maintainer (yvgude) confirmed the mcp.json TRAP as a bug, fixed in
**3.7.4** (released all channels within ~2h): explicit LEAN_CTX_PI_ENABLE_MCP=1 now
wins over init-written mcp.json; /lean-ctx warns about duplicates only when
pi-mcp-adapter actually runs. Confirmed by-design: one-shot CLI default has no
cross-call cache (points 1+3 of our report stand). Asked for a confirmed-connected
re-run before June 17; offered maintainer statement.

Our counter-evidence posted (issuecomment-4636817950): pilot a1m WAS gate-confirmed
connected, yet transcripts show only **11 ctx_* calls vs 43 read + 69 bash (~9%
adoption; 3 ctx_reads, zero re-reads)** → "0 saved" is arithmetically honest; binding
constraint = voluntary adoption in additive mode, not bridge function. Open puzzle
handed to maintainer: stats.json logged those 11 calls as `cli_*` types with
cep.sessions=0/cache_hits=0 despite "connected" status — meter mislabeling or
CLI-path fallback? Also flagged: a1 (one-shot) got 46 ctx_* calls vs a1m's 11 —
bridge-on REDUCED adoption (no explanation yet). Asked maintainer to designate
additive vs replace as the savings-faithful mode; their answer → further amendment.

**Replication arm: tokbench-arm-a1m:1.1** (lean-ctx 3.7.4 + pi-lean-ctx@3.7.4,
rm-mcp.json workaround DROPPED — flag-wins is the config under test). Pre-run
connected gate unchanged.

### ⚠ 3.7.4 is a major release, not a one-line fix — version confound (writeup MUST state)

v3.7.3..v3.7.4 = 132 files, +7,667/−2,135. The #361 fix (pi ext index.ts, 21 lines)
rides a release already in flight. On our measurement path:
- **94643ed9 (#168): tool-description steering** — front-loads "Prefer over native
  Read/cat…" in line 1 of every native-competing tool description. Commit message
  names the exact failure mode our pilot measured (agents defaulting to native tools,
  9% adoption). Built to move our binding constraint.
- **cc5ea741/5369cea1: ctx_read session-cache rework + lazy-startup perf pass** —
  latency + cache path of the a1m arm.
- never-inflate fix (5dfd861d) is NOT a fix for our envelope finding — it repairs a
  within-cycle regression (task-conditioned entropy refactor). Header tax on small
  files stands; maintainer conceded by design.
- rules_injection=dedicated (#343): default stays `shared` → our arm-setup unchanged.
  Verified: injected rules byte-identical 1.0 vs 1.1 (AGENTS.md 166B, LEAN-CTX.md 2,530B).

**Inference rule:** pilot-a1m (3.7.3) vs rep-a1m (3.7.4) deltas are VERSION deltas —
bridge fix, adoption steering, and perf changes move together; no per-cause attribution.
Research question unaffected (we test the current maintainer-blessed product); rep-vs-rep
internal comparisons clean (all a1m reps on 3.7.4). Harness-side structure (≈26%
addressable surface, forge-tool invisibility, phase isolation) unchanged by any of this.

## rtk 0.40.0 on pi (a3 — image not yet built)

**No degraded-path risk:** filter registry (~70 command patterns, src/discover/rules.rs)
compiled into binary, active by default, no off-switch, stateless per command, nothing
to warm. Pi extension (hooks/pi/rtk.ts) = thin delegator: tool_call event → `rtk rewrite`
→ mutates event.input.command. Exit 0/3=rewrite, 1=passthrough, never blocks.
Version guard ≥0.23.0 at load (0.40.0 ok). RTK_DISABLED=1 = builtin passthrough toggle.

**Coverage vs OUR harness's bash traffic** (A0: git, npm run/test, node store-cli):
- ✅ git (70% claimed), npm run/exec (70%), npx (70%), tsc (83%), vitest (99%)
- ❌ `node scripts/*.cjs` (forge store-cli!) → passthrough, 0%
- ❌ `npm install` → passthrough (pattern only covers run/exec)
- Heredocs and $(( )) never rewritten; `find` skipped in pipes; compound cmds rewritten per-segment.

**a3 build checklist:** binary (musl, pinned) → `rtk init --agent pi` (project-local
.pi/extensions/rtk.ts — WIPED BY RESET → needs arm-setup re-init hook like a1) →
RTK_TELEMETRY_DISABLED=1 → sanity: `rtk gain --history` non-empty after run
(also guards against name-collision with "Rust Type Kit").
State: ~/.local/share/rtk/history.db (tracking, default on), tee/ (full output on failure),
~/.cache/rtk-hook-version-ok.

## headroom on pi+ollama-cloud (a2 — BUILT + SMOKE-TESTED 2026-06-05)

**CHAIN VERIFIED end-to-end:** runner → http://headroom:8787/v1/chat/completions →
https://ollama.com → 200 with usage; STREAMING (SSE) verified flowing through proxy.
(Earlier 400/502s were a bad test-side key extraction — auth.json field is
`.["ollama-cloud"].key`, not .apiKey.)

**CCR "trap" CORRECTION — earlier research was wrong for the proxy path:**
ccr_handle_responses=True (default) → the PROXY ITSELF intercepts the model's
headroom_retrieve tool calls, retrieves from its store, re-calls upstream (≤3 rounds),
returns only the final clean response (headroom/ccr/response_handler.py:65-77).
Fully wire-level; pi never sees the tool. DEFAULTS ARE CORRECT for a2.
Residual unknown: does retrieve-interception work mid-STREAM? (watch in run 1).

Defaults audit (headroom/config.py):
- SmartCrusher ON (min 200 tok/result, ≥5-item arrays, ≤15 items kept, relevance ≥0.25)
- ReadLifecycle ON. CodeCompressor OFF (--code-aware). CacheAligner OFF.
- Kompress model: image SELF-WARMS at startup (observed HF download in logs at boot,
  not first-request) — no pre-bake needed; proxy-data volume persists HF cache anyway.
- Threshold reality: our tool outputs median 1–3KB (≈250–750 tok), mostly prose/code
  not JSON arrays → much traffic may never trigger SmartCrusher.
- Chat handler: --backend default "anthropic" → anthropic_backend=None → DIRECT httpx
  forward to --openai-api-url (registry.py:145-146). litellm red banners in logs are
  incidental (model-info lookups), non-fatal.
- /v1/models = passthrough route ✓; /api/show NOT routed (404) — pi-ollama-cloud
  model discovery survives via its on-disk cache (~/.pi/agent/cache/, warm in base 0.4).

**a2 artifacts:** bench/docker/arm-a2-headroom/{compose.yml,Dockerfile,run-task.sh,harvest.sh}
- sidecar: official image (digest in pins.env), ENTRYPOINT is ["headroom","proxy"] so
  compose `command` = flags only: --host 0.0.0.0 --port 8787 --openai-api-url
  https://ollama.com --no-rate-limit --log-file /data/proxy.jsonl; HEADROOM_TELEMETRY=off;
  /readyz healthcheck gates runner.
- runner: tokbench-arm-a2:0.1 = base 0.4 + scripts; OLLAMA_API_BASE=http://headroom:8787
  (pi-ollama-cloud models.ts:13 env override). No project files → no arm-setup hook.
- run: cd bench/docker/arm-a2-headroom && TASK=CART-S01-T01 REP=1 docker compose run runner
  (then docker compose down after harvest; proxy /stats captured by harvest a2 case).
- Smoke test cost: ~4 ollama-cloud requests.

## headroom BUNDLES rtk (and lean-ctx) — market-structure finding

`headroom wrap` auto-downloads the rtk binary from rtk's GitHub releases
(headroom/rtk/installer.py) and registers its hooks; `HEADROOM_CONTEXT_TOOL` env
accepts "rtk" or "lean-ctx" as pluggable context tools (cli/wrap.py:86-89); rtk
savings are tracked in headroom's own /stats (rtk_tokens_avoided). The wire-level
player absorbs the command-level players as features — fractal of the platform-
absorption thesis (article #6 + 01/08 market story).
OUR ARMS UNAFFECTED: a2 runs `headroom proxy` only (not wrap) → no rtk inside a2;
verify at harvest: /stats rtk_tokens_avoided == 0 (no cross-arm contamination).

## Cross-product pattern (article material)

Three different default-path failure classes:
- lean-ctx: core feature OFF by default + vendor's own init writes config that disables
  the enable flag.
- headroom: a feature ON by default that is actively harmful without MCP (lossy + fake tool).
- rtk: everything on and un-degradable, but registry doesn't know the harness's actual
  command vocabulary (node store-cli = forge's hottest bash path → passthrough).
"Installed" ≠ "running as designed" for every product, each for a different reason.

## forge-cli bugs found (to report upstream, Entelligentsia/forge-cli)

1. npm tgz declares file:./vendor-pi/*.tgz deps but doesn't contain them → npm i -g tgz fails.
2. /forge:init materializes .forge/tools/ without its package.json ({"type":"commonjs"})
   → lib/result.js (CJS .js) crashes all tools under "type":"module" projects; collate
   silently broken during runs. One-line fix per project.
