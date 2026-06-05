# Run-1 Results — CART-S01-T01 (T-fix), rep 1, 2026-06-05

Task: small bug-fix through the full forge pipeline (8 phases). Persona map:
glm-5.1 (review-plan, review-code, approve) / glm-4.7 (plan, implement, validate, commit) / glm-4.6 (writeback).
Both runs: all acceptance gates green (build=0 test=0 lint=0), all phases stopReason=stop.

## A0 — native forge/pi (tokbench-base:0.4, run 11:49–12:02 UTC, wall 12m50s)

| phase | model | input | output | ctxTok | turns | sec |
|---|---|---:|---:|---:|---:|---:|
| plan | glm-4.7 | 471,364 | 4,404 | 19,743 | 35 | 55 |
| review-plan | glm-5.1 | 191,802 | 2,913 | 16,357 | 15 | 74 |
| implement | glm-4.7 | 280,585 | 3,951 | 17,058 | 22 | 37 |
| review-code | glm-5.1 | 305,218 | 3,604 | 18,204 | 22 | 78 |
| validate | glm-4.7 | 330,824 | 4,010 | 18,034 | 27 | 65 |
| approve | glm-5.1 | 126,931 | 2,352 | 15,155 | 11 | 51 |
| commit | glm-4.7 | 344,743 | 4,657 | 19,916 | 25 | 62 |
| writeback | glm-4.6 | 224,838 | 2,681 | 13,048 | 23 | 89 |
| **TOTAL** | | **2,276,305** | **28,572** | | **180** | **511** |

cacheRead/cacheWrite = 0 everywhere (ollama-cloud: no prompt caching). ~5 tool errors.

A0 tool traffic (calls / result chars): read 37/100,096 · bash 76/43,931 ·
forge_artifact 38/29,097 · forge_store 37/14,386 · write 4/257 · misc ~16/~1,400.
→ tool output total ≈189k chars ≈47k tok. Σ final contexts ≈137.5k tok →
**tool output ≈26% of context; read+bash (the middleware-addressable slice) ≈36k tok**.
**Structural savings ceiling for tool-output middleware on this harness ≈ 18–23% of input.**

## A1 — lean-ctx as-shipped default (tokbench-arm-a1:0.2, run 12:25–12:52 UTC, wall ~27m)

| phase | model | input | output | ctxTok | turns | sec |
|---|---|---:|---:|---:|---:|---:|
| plan | glm-4.7 | 431,059 | 4,557 | 21,426 | 30 | 288 |
| review-plan | glm-5.1 | 374,413 | 3,886 | 20,500 | 25 | 102 |
| implement | glm-4.7 | 213,665 | 2,992 | 14,050 | 19 | 216 |
| review-code | glm-5.1 | 334,743 | 3,134 | 18,302 | 23 | 78 |
| validate | glm-4.7 | 354,184 | 4,540 | 19,247 | 26 | 251 |
| approve | glm-5.1 | 141,236 | 2,197 | 14,530 | 12 | 61 |
| writeback | glm-4.6 | 633,197 | 5,280 | 20,015 | 44 | 184 |
| commit | glm-4.7 | 1,140,187 | 5,455 | 38,003 | 46 | 357 |
| **TOTAL** | | **3,622,684** | **32,041** | | **225** | **1,537** |

## Head-to-head

| metric | A0 | A1 | Δ |
|---|---:|---:|---|
| input tokens | 2,276,305 | 3,622,684 | **+59%** |
| output tokens | 28,572 | 32,041 | +12% |
| turns (=requests) | 180 | 225 | +25% |
| model time | 8.5 min | 25.6 min | **3.0×** |
| tool errors | ~5 | 16 | 3.2× |
| task success | ✅ | ✅ | = |

Blowouts concentrated in commit (1.14M, ctx 38k vs 19.9k) and writeback (633k) —
git/store-heavy phases that ran essentially uncompressed + error retries.

## Mechanism (from transcripts — the real story)

1. **Voluntary adoption was partial & lopsided** (additive mode):
   ctx_read 25 vs read 29 (46%); ctx_shell 10 vs bash 83 (**11%**).
   ctx_ls 6, ctx_grep 2, ctx_find 3 (all 3 errored).
2. **Negative compression where adopted.** ctx_read payload vs file on disk:
   graph.ts 3,674 vs 3,627 (+1.3%); graph.test.ts +1.1%; CLAUDE.md +0.6%;
   SPRINT_REQUIREMENTS +2.8%; personas/architect.md **+21.6%**; supervisor.md **+13%**.
   Auto mode on small files = full content + metadata envelope. EVERY ctx_read net-negative.
3. **Flagship feature absent:** graph.ts ctx_read 4× — identical 3,674-char payload every
   time. No ~13-token cached re-read. Cause: pi-lean-ctx DEFAULT runs one-shot CLI
   subprocesses; MCP bridge (persistent server/session cache) is opt-in and was OFF.
4. **Tool-definition bloat:** additive mode = ctx_* + pi builtins + forge tools re-sent
   every turn; commit phase final context doubled (38k vs 19.9k).
5. **New error class:** model typos/misuse of ctx_* args (SPRITE_REQUIREMENTS.md, dir
   reads) → retries at full-context price.
6. **forge custom tools invisible to middleware:** forge_store/forge_artifact (75 calls)
   not interceptable; forge's own bash usage already lean (store-cli output small).
7. **No vendor self-metering written** via the extension path in this run
   (stats at ~/.config/lean-ctx/stats.json — wrong path harvested, container --rm'd;
   fresh-container CLI test: `gain` claimed "27 tokens saved, 3%" while transcripts
   measure payloads LARGER than source → metering-accountability data point for
   research thread 09).

## Quota cross-check

A0: session glm went 137→~317 requests ≈ transcript 180 turns ✓.
A1: session glm-4.7 +109 vs transcript 121 glm-4.7 turns ✓ (window rolled).
A1 whole run moved weekly +2.7%. Dashboard surfaces top-model per window; saw
kimi-k2.5 13 req appear that we never invoked → dashboard unreliable as per-run meter.

## Caveats

N=1 per arm; smallest task shape; tiny codebase (files 1.5–5.6KB — nothing to compress);
additive mode as-shipped; host anchor (1.34M, 2026-06-04) not comparable (different
models incl. minimax, possibly lean-ctx-mediated host env).

## a1m — lean-ctx + embedded MCP bridge (tokbench-arm-a1m:0.2, run 13:11–13:27 UTC, wall 16m09s)

Gate passed at session start: "MCP bridge: embedded (connected)", 9 MCP tools (total
active ctx surface = 14 tools). Dead-end en route: env var alone insufficient —
`lean-ctx init --agent pi` writes ~/.pi/agent/mcp.json; pi HAS no MCP adapter; extension
sees it and disables its own bridge ("adapter-configured"). a1m:0.2 rm's mcp.json at
build AND per-reset in arm-setup.

| phase | model | input | output | ctxTok | turns | sec |
|---|---|---:|---:|---:|---:|---:|
| plan | glm-4.7 | 445,355 | 4,043 | 22,961 | 27 | 54 |
| review-plan | glm-5.1 | 210,844 | 4,964 | 21,483 | 13 | 175 |
| implement | glm-4.7 | 280,686 | 3,320 | 17,748 | 20 | 48 |
| review-code | glm-5.1 | 305,256 | 3,527 | 20,794 | 19 | 130 |
| validate | glm-4.7 | 269,497 | 3,652 | 20,227 | 17 | 40 |
| approve | glm-5.1 | 141,737 | 2,244 | 16,723 | 10 | 28 |
| writeback | glm-4.6 | 498,658 | 4,200 | 19,196 | 35 | 197 |
| commit | glm-4.7 | 983,278 | 5,057 | 37,272 | 38 | 86 |
| **TOTAL** | | **3,135,311** | **31,007** | | **179** | **758** |

Gates green. Engage: 11 ctx_* calls (vs a1's 46 — model used ctx tools LESS with bridge on).

### Three-way verdict (T-fix, rep 1)

| metric | A0 | A1 (CLI) | a1m (MCP) |
|---|---:|---:|---:|
| input | 2,276,305 | 3,622,684 (+59%) | 3,135,311 (+38%) |
| turns | 180 | 225 | 179 (=A0) |
| model time | 8.5m | 25.6m (3.0×) | 12.6m (1.5×) |
| ctx_* calls | — | 46 | 11 |

**Vendor's own meter (leanctx-gain.txt, captured): "0 tokens saved · 0.0% compression ·
11 commands · $-0.001 USD saved" — zero savings, NEGATIVE dollars, by its own accounting.**

Per-phase: early/middle phases returned to ≈baseline (implement 281k =A0; review-code
305k =A0; validate 269k < A0's 331k; plan 445k < 471k). The ENTIRE excess concentrates
in writeback (+122%) and commit (+185%): a1m commit bash = 30 calls/68.7k chars/4 err
vs A0 commit 19/22.6k/1 — more fumbling, more errors, each extra turn re-paying an
inflated context (37k vs 20k; 14 ctx tool defs + rules + fatter history).
N=1 caveat: can't yet separate "lean-ctx rules destabilize the commit persona" from
stochastic variance — reps needed. Both lean-ctx runs blew up the same two phases.

### lean-ctx family verdict so far
Best case measured (proper MCP bridge, vendor's intended config): +38% input, 1.5×
time, vendor meter itself reports zero savings. The as-shipped default was strictly
worse. On a lean harness + small codebase, lean-ctx provided no measurable value in
any configuration tested, per its own dashboard and per the provider-billed meter.

## a3 — rtk 0.42.2 (tokbench-arm-a3:0.1, run ended 13:48 UTC, wall ~22m incl. operator hold)

| phase | model | input | output | ctxTok | turns | sec |
|---|---|---:|---:|---:|---:|---:|
| plan | glm-4.7 | 423,622 | 4,357 | 19,227 | 32 | 137 |
| review-plan | glm-5.1 | 340,499 | 3,378 | 19,234 | 24 | 132 |
| implement | glm-4.7 | 212,790 | 2,834 | 13,909 | 20 | 38 |
| review-code | glm-5.1 | 571,740 | 4,934 | 23,058 | 34 | 148 |
| validate | glm-4.7 | 301,617 | 4,024 | 17,044 | 25 | 77 |
| approve | glm-5.1 | 136,451 | 2,654 | 14,325 | 12 | 75 |
| writeback | glm-4.6 | 258,970 | 3,256 | 13,184 | 26 | 93 |
| commit | glm-4.7 | 642,838 | 4,397 | 39,850 | 28 | 153 |
| **TOTAL** | | **2,888,527** | **29,834** | | **201** | **853** |

Gates green. Engage pass (rtk-history: 39 entries).

**rtk's own meter: 74 commands rewritten, 58.4K tokens saved (74.7% of touched),
avg 152ms overhead; top win `rtk lint eslint` 54.0K @ 99.7%.** The product worked
exactly as designed — transparent, cheap, effective on covered commands, zero
caused failures (a3's 11 bash errors audited: grep no-matches, failing lint runs
(compressed by rtk, agent recovered), the all-arms forge tools package.json bug,
gitignored-path git friction — none rtk-induced).

**Both meters true simultaneously: rtk saved 74.7% of what it touched; what it
touched was ~2.5% of total input.** Billed input still +27% vs A0 — dominated by
stochastic path variance (review-code 572k/34 turns vs A0's 305k/22; 103 bash calls
vs 76), NOT by rtk (whose max addressable effect ≤58K is far below the noise floor).
(rtk gain --json unsupported → empty file; use text output in harvest.)

## a2 — headroom proxy (tokbench-arm-a2:0.1 + sidecar, run 14:00–14:16 UTC, wall 16m08s)

| phase | model | input | output | ctxTok | turns | sec |
|---|---|---:|---:|---:|---:|---:|
| plan | glm-4.7 | 592,570 | 4,102 | 26,436 | 36 | 148 |
| review-plan | glm-5.1 | 452,541 | 4,090 | 24,613 | 27 | 128 |
| implement | glm-4.7 | 250,490 | 2,992 | 14,999 | 22 | 43 |
| review-code | glm-5.1 | 478,954 | 3,469 | 17,579 | 39 | 138 |
| validate | glm-4.7 | 377,130 | 3,856 | 16,802 | 32 | 112 |
| approve | glm-5.1 | 149,942 | 2,369 | 13,324 | 14 | 62 |
| writeback | glm-4.6 | 239,827 | 3,330 | 14,693 | 23 | 82 |
| commit | glm-4.7 | 703,006 | 4,477 | 24,124 | 44 | 158 |
| **TOTAL (billed = post-compression)** | | **3,244,460** | **28,685** | | **237** | **871** |

Gates green. Engage pass. **Proxy /stats: api_requests=237 == transcript turns (meters
agree to the digit). 194/237 compressed (82%), avg 10.2%, best 25.1%,
total_tokens_removed=342,174 → counterfactual uncompressed ≈ 3.59M → genuine −9.5%.**
rtk_tokens_avoided=0 (no a2/a3 contamination). proxy.jsonl (239 req) in results.
Latency: 3.7s/turn vs A0 2.8 (+0.9s/turn ≈ proxy pipeline; operator: "like running a
local model"). Billed total still +43% vs A0 — that's turns (237 vs 180, path variance),
NOT headroom; the defensible effect is the within-run counterfactual −9.5%.
Mid-run reading was 5.8% avg — close to headroom's own production fleet median 4.8%,
final 10.2% — both far below 47–92% benchmark claims; independent confirmation of the
benchmark-vs-production gap.

## FIVE-WAY VERDICT — T-fix rep 1 (all N=1)

| | A0 | a3 rtk | a1m lean-ctx+MCP | a1 lean-ctx default | a2 headroom |
|---|---:|---:|---:|---:|---:|
| billed input | 2.276M | 2.889M | 3.135M | 3.623M | 3.244M |
| genuine product effect | — | −58K self-rep (2.5% of touched-slice) | ~0 (own meter) | negative | **−342K measured on wire (−9.5%)** |
| turns | 180 | 201 | 179 | 225 | 237 |
| sec/turn | 2.8 | 4.2 | 4.2 | 6.8 | 3.7 |
| caused failures | — | none | none clear | misuse errors | none; streaming clean |

**Headroom is the only product that measurably reduced billed tokens** (wire-level
counterfactual). Interception architecture ranking on this harness:
wire (−9.5%, transparent, +0.9s/turn) > command (works, surface too small) >
tool/cooperative (net negative in both configs).

## FOUR-WAY VERDICT (superseded by five-way above) — T-fix rep 1 (all N=1)

| | A0 native | a3 rtk | a1m lean-ctx+MCP | a1 lean-ctx default |
|---|---:|---:|---:|---:|
| input | 2,276,305 | 2,888,527 (+27%) | 3,135,311 (+38%) | 3,622,684 (+59%) |
| turns | 180 | 201 | 179 | 225 |
| model time | 8.5m | 14.2m | 12.6m | 25.6m |
| self-reported savings | — | 58.4K (74.7% of touched) | 0 (-$0.001) | (lost; CLI test ~0) |
| caused failures | — | none | errors↑ via misuse | 16 errors, 3 ctx typos |

**No middleware arm beat native.** The only product that demonstrably did its job
(rtk) had an effect size (≤58K, ~2.5%) below the run-to-run noise floor (same-config
phase swings of ±250k observed: review-code 305/335/305/572k across runs).
NOISE FLOOR IS THE KEY METHODOLOGICAL FINDING FOR REPS: single runs cannot detect
sub-5% effects; reps + per-phase medians required. The lean-ctx deltas (+38/+59%)
have identified causal mechanisms (tool-def bloat, envelope tax, adoption errors)
and exceed the noise floor; rtk's +27% does not have a causal mechanism and is
attributable to path variance.

## a0v — base:1.0 validation run (A0 condition on the REPRODUCIBLE base, 2026-06-05 ~14:45Z)

Launched --entrypoint forge --rm (data docker-cp'd out pre-exit). Pristine by image
construction. Gates green. env-key auth (OLLAMA_API_KEY) certified end-to-end incl.
fresh model discovery.

TOTALS: input 2,246,787 · output 28,630 · turns 172 · model time 646s
vs pilot A0 (base 0.4): input −1.3%, output +0.2%, turns −4.4% — **A0 condition
REPRODUCES at total level despite large per-phase swings (plan 471k→313k,
review-code 305k→424k). Phase variance redistributes; totals converge.**
→ Total-level noise floor ≈ low single digits %, much tighter than per-phase.
  Strengthens pilot total-level claims; rtk's +27% deserves rep scrutiny (less
  attributable to noise than first judged).

tools-fix effect measured: writeback 85k/11 turns vs pilot 225k/23 — store-cli no
longer crashing saves ~100–140k/run (the forge package.json bug's cost, quantified).

Provider health: ollama-cloud transient 500s recorded in 5 phases' errorMessage
(all retried, phases completed). REP PROTOCOL ADDITION: record provider-error
counts per run.

## a2 ledger verification (2026-06-06, prompted by operator challenge)

Challenge: "why do you say headroom saved tokens" — the −342K had been taken from
headroom's own /stats (same class of self-report we dismissed for rtk/lean-ctx).
Audit performed against proxy.jsonl per-request ledger:
1. Σ input_tokens_optimized = 3,244,474 vs provider-billed 3,244,460 → 0.0004% —
   headroom's accounting basis IS the billed basis.
2. Untouched requests (no transforms): original==optimized exactly in 43/45 —
   calibrates the "original" (counterfactual) measure on the same basis. (2
   mismatches unexplained — inspect; likely retried requests.)
3. All 194 compressed requests: original−optimized==tokens_saved exactly.
VERDICT: per-request compression of 342K billed-basis tokens is VERIFIED, not
self-reported. PROPERLY SCOPED CLAIM: headroom compressed what it forwarded;
the a2 RUN still billed +43% vs A0 because the run path was longer (237 vs 180
turns, N=1). Whether per-request compression translates to cheaper RUNS is an
open question the reps answer. (Hypothesis to watch: compressed contexts may
alter model behavior → longer paths.)
METHOD NOTE for the article: judge every product's self-meter against the bill —
rtk's meter (chars/4 heuristic) and lean-ctx's gain were not verifiable this way;
headroom's was, and passed. That asymmetry is itself a finding (thread 09).

## c0 — Claude Code + forge plugin (apples-to-ORANGE reference, 2026-06-05 19:20–19:38 UTC)

Same task, same golden state, forge PLUGIN pipeline via /carto:run-task on the HOST
(clean MCP config: --strict-mcp-config, no lean-ctx server; global CLAUDE.md ctx_*
instructions present but toolless — documented caveat). Subscription billing.
First attempt SHORT-CIRCUITED: Opus checked git history, found the baseline's prior
commit (eb77aaf) and declared the task already done — none of the 9 glm pipeline
runs ever did this. Documented operator nudge ("store is source of truth, status=
draft") → full pipeline ran: Workflow tool, 17 agents, commit fd2577e, store
committed, gates green. Aborted attempt banked separately (results/c0.../aborted-attempt).

TOTALS (main run, orchestrator + 17 workflow agents, 391 API messages):
fresh input 42,614 (0.5%) · cache_read 8,082,294 (93%) · cache_write 560,335 ·
output 45,509 · TOTAL fed 8,685,243 = 3.8× A0's volume.
Model mix (plugin's own tiering): opus-4-8 39 / opus-4-5 136 / sonnet-4-6 91 /
haiku-4-5 125 msgs.

COST-WEIGHTED (Anthropic: cache read 0.1×, write 1.25×): effective input
≈ 1.55M full-price-equivalent < A0's raw 2.28M despite 3.8× volume.
**THE CACHING-TRAP THESIS, MEASURED:** cache-discounted providers make raw token
counts meaningless; Claude Code's architecture MAXIMIZES stable-prefix re-reads
(93% of tokens at 10% price). Corollary for middleware: a context rewriter that
breaks prefix stability here would convert 10%-price reads into full-price tokens —
"savings" could multiply cost. (Research series 08's prediction, now anchored.)
Scope caveats: different models, different pipeline shape (workflow subagents),
subscription billing, N=1, operator nudge required.

Data: results/c0-T-fix-claude-r1/ (main session jsonl + full subagent tree + aborted attempt).
