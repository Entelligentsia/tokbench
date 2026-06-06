# Architecture comparison: agent-loop vs phase-isolation on the cache-discounted rail

c0-T-fix-claude-r1 (Claude Code + forge plugin) vs a0c-T-fix-r1 (4ge native),
same task (CART-S01-T01), same model family (opus-4-8 / sonnet-4-6 / haiku-4-5),
same payment rail (Anthropic, prompt caching). Every number provider-reported
from the run transcripts; both dollar totals reproduce the billed amounts
exactly ($6.09 / $1.82).

## Headline

| | c0 Claude Code | a0c 4ge | Δ |
|---|---|---|---|
| Architecture | one agent-loop session + 17 subagents | 8 phase-isolated agents, artifact handoff | — |
| Messages / turns | 391 | 108 | 3.6× |
| Tokens fed (fresh+cacheRead+cacheWrite) | 8,685,243 | 1,672,470 | **5.2×** |
| Cache-read share | 93.0% | 92.1% | ≈ equal |
| Output tokens | 45,509 | 36,779 | 1.24× |
| Cost (verified vs bill) | $6.09 | $1.82 | **3.35×** |
| Wall time | ~18m | 11.1m | 1.6× |

Ratio bookkeeping: **3.8×** = c0 fed vs the glm NATIVE baseline (8.69M/2.28M,
cross-rail, ledger row 7). **5.2×** = c0 vs a0c (same-rail, clean architecture
comparison — use this one for architecture claims).

## Dollar anatomy

| Cost line | c0 | a0c |
|---|---:|---:|
| Fresh input | $0.21 | ~$0.001 |
| Cache reads | **$2.72** | $0.55 |
| Cache writes | $2.29 | $0.60 |
| Output | $0.86 | $0.67 |

Per-model (c0): opus-4-5 subagents $2.65 (43% of run, 136 msgs vs a 2.8M
cumulative cache) · opus-4-8 $1.76 · sonnet-4-6 $1.18 · haiku-4-5 $0.50.
Per-model (a0c): opus-4-8 $0.97 · sonnet-4-6 $0.81 · haiku-4-5 $0.04.

Findings:
1. **Caching equalizes hit-rate, not cost.** Both ~93% cache reads; cache reads
   are billed at 0.1× and are still c0's largest line ($2.72). Phase isolation
   doesn't cache better — it makes there be LESS TO CACHE (per-phase contexts
   ≤25K, die at phase end; the re-read prefix never compounds run-long).
2. **Output tokens are the tell.** 45.5K vs 36.8K (within 25%) for the same fix,
   gates, commit — the work is the same size; the 5.2× input delta is pure
   context carriage.
3. **Rail interaction (extends standing conclusions 5+6):** on the cached rail
   the architecture delta costs 3.35×; on a request-metered rail (no cache
   pricing) the same 5.2× volume delta would bill in full. Phase isolation is
   worth MORE exactly where caching doesn't exist.

## Per-phase cached / non-cached anatomy (the clean comparison)

Definitions: **cached** = cache-read tokens (billed 0.1×) · **non-cached** =
fresh input (1×) + cache writes (1.25×). Both tables sum to the billed totals.
c0 contexts identified from subagent prompts (`Phase: role="…"` + sidecar
eventIds in `subagent-tree/subagents/workflows/wf_f0cff343-f99/`).

### a0c — 4ge per phase ($1.8201 ✓)

| phase | model | cached | non-cached | cached-$ | noncach-$ | output-$ | total |
|---|---|---:|---:|---:|---:|---:|---:|
| plan | sonnet | 179,277 | 19,556 | 0.054 | 0.073 | 0.073 | 0.200 |
| review-plan | opus-4-8 | 162,570 | 23,482 | 0.081 | 0.147 | 0.134 | 0.362 |
| implement | sonnet | 200,119 | 10,820 | 0.060 | 0.041 | 0.056 | 0.157 |
| review-code | opus-4-8 | 210,757 | 14,620 | 0.105 | 0.091 | 0.135 | 0.332 |
| validate | sonnet | 275,428 | 20,693 | 0.083 | 0.078 | 0.082 | 0.243 |
| approve | opus-4-8 | 144,594 | 15,940 | 0.072 | 0.100 | 0.104 | 0.276 |
| writeback | haiku | 97,290 | 13,261 | 0.010 | 0.017 | 0.014 | 0.040 |
| commit | sonnet | 269,496 | 14,567 | 0.081 | 0.055 | 0.076 | 0.212 |
| **TOTAL** | | **1,539,531** | **132,939** | **0.546** | **0.600** | **0.674** | **1.820** |

### c0 — Claude Code per context, labeled ($6.0902 ✓)

| context | model | T | cached | non-cached | cached-$ | noncach-$ | output-$ | total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| orchestrator (main) | opus-4-8 | 23 | 732,287 | 71,493 | 0.366 | 0.427 | 0.289 | 1.082 |
| pipeline-resolver | opus-4-8 | 16 | 208,052 | 88,654 | 0.104 | 0.521 | 0.051 | 0.676 |
| plan | sonnet-4-6 | 49 | 1,183,465 | 62,610 | 0.355 | 0.235 | 0.075 | 0.665 |
| review-plan | opus-4-5 | 32 | 640,372 | 43,188 | 0.320 | 0.270 | 0.069 | 0.660 |
| implement | sonnet-4-6 | 42 | 924,333 | 42,659 | 0.277 | 0.160 | 0.079 | 0.516 |
| review-code | opus-4-5 | 40 | 886,858 | 41,334 | 0.443 | 0.258 | 0.104 | 0.806 |
| validate | opus-4-5 | 35 | 699,261 | 28,530 | 0.350 | 0.178 | 0.086 | 0.614 |
| approve | opus-4-5 | 29 | 570,438 | 34,891 | 0.285 | 0.218 | 0.064 | 0.568 |
| writeback | haiku-4-5 | 34 | 609,110 | 49,222 | 0.061 | 0.062 | 0.013 | 0.135 |
| commit | haiku-4-5 | 67 | 1,439,982 | 43,927 | 0.144 | 0.055 | 0.025 | 0.224 |
| 8× sidecar-merge (1/phase) | haiku | 3 ea | ~188K Σ | ~97K Σ | 0.017 | 0.121 | 0.005 | 0.144 |
| **TOTAL** | | 391 | **8,082,294** | **602,949** | **2.725** | **2.505** | **0.861** | **6.090** |

### Phase-for-phase totals (c0 phase = runner + its sidecar)

| phase | c0 | a0c | Δ |
|---|---:|---:|---:|
| plan | 0.697 | 0.200 | 3.5× |
| review-plan | 0.676 | 0.362 | 1.9× |
| implement | 0.532 | 0.157 | 3.4× |
| review-code | 0.822 | 0.332 | 2.5× |
| validate | 0.630 | 0.243 | 2.6× |
| approve | 0.584 | 0.276 | 2.1× |
| writeback | 0.151 | 0.040 | 3.8× |
| commit | 0.240 | 0.212 | 1.1× |
| **orchestration overhead** | **1.758** | **0** | — |
| **TOTAL** | **6.090** | **1.820** | 3.35× |

Findings (supersede the raw-carriage framing below):
- **a0c's bill splits into three even thirds** (cached $0.55 / non-cached $0.60 /
  output $0.67) — output, the actual work, is the largest line. **c0 is
  45/41/14** — output is a seventh of its bill. Per dollar of output: c0 pays
  $6.07 input-side, a0c $1.70.
- **29% of c0's bill is pure orchestration** (opus-4-8 main loop + opus-4-8
  pipeline-resolver, $1.76) — work 4ge does in-process for zero tokens. The
  phase-for-phase premium is ~2–3.5×; orchestration is most of the rest.
- **Model maps differ** (caveat on per-phase deltas): c0 ran reviews/validate/
  approve on opus-4-5 and writeback/commit on haiku; a0c used opus-4-8 for
  reviews and sonnet for commit. Commit near-parity ($0.24 vs $0.21): c0's
  haiku absorbed a 67-turn flail (forge-engineering#40 pattern, on this rail
  too) at haiku prices.
- **Worst line outside the main loop: pipeline-resolver $0.52 non-cached** —
  88.6K cache writes in a 16-turn life, never amortized. Write-heavy +
  short-lived + opus is the most expensive context shape on a cached rail.

## System-prompt weight (context boot cost)

Metric definition: **boot weight** = turn-1 prompt size of a fresh context
(fresh + cacheRead + cacheWrite of the first request) = system prompt + tool
schemas + injected context + kickoff. **Carriage** = Σ over contexts of
(boot × messages) — the preamble re-paid as prefix on every turn. Boot weight
is an upper bound on pure system-prompt weight (turn-1 includes the kickoff
message; later 4ge phases include handed-off artifacts, e.g. review-plan's
boot includes PLAN.md). Same definition both sides — comparison is fair.

| | c0 Claude Code | a0c 4ge |
|---|---:|---:|
| Main/orchestrator boot | **29,324** | — (no persistent orchestrator) |
| Sub-context boot range (mean) | 11,750–15,678 (~12.6K) | 8,071–12,573 (10,175) |
| Contexts opened | 18 | 8 |
| Mean boot, all contexts | 13,492 | 10,175 |
| **Carriage** (boot × turns) | **5,459,710** | **1,068,609** |
| Carriage share of fed tokens | **62.9%** | **63.9%** |

Findings:
4. **CC's main loop boots 2.9× heavier than a 4ge phase** (29.3K vs 10.2K —
   CC system prompt + full tool schemas + CLAUDE.md + plugin instructions vs
   forge's persona-scoped slice), and that prefix is re-paid 23×.
5. **Carriage share is an invariant: ~63% in BOTH harnesses.** Two-thirds of
   everything fed to the provider, in either architecture, is preamble
   carriage rather than conversation. The architectures differ in absolute
   volume (5.1× carriage), driven by turn count and boot size — not in the
   proportion of overhead. Candidate writeup line: middleware compresses the
   conversational third; harness architecture decides the size of the whole.
6. **Cache-adjusted, carriage is a COST share of 38% (c0: $2.34 of $6.09) /
   32% (a0c: $0.59 of $1.82)** — not 63%; that was token volume. Boot pays
   1.25× once (cache write) then 0.1× per re-read, so per-turn cost factor =
   (1.25+0.1(T−1))/T → 0.1 as contexts live longer. No-cache counterfactual:
   ~$18.6 (c0) / ~$3.78 (a0c) — the cache discounts carriage 8.0× / 6.4×.
   Long-lived contexts amortize better, so caching partially refunds the
   agent-loop architecture — the conclusion-5 mechanism; on the request-
   metered rail there is no refund and the full volume bills.

## Per-phase boot weights (a0c)

plan 8,071 · review-plan 11,626 · implement 8,841 · review-code 12,560 ·
validate 9,469 · approve 12,573 · writeback 9,109 · commit 9,152.
(Reviews/approve boot heavier: they carry the artifacts under review.)

## Method

- c0: per-message usage from `results/c0-T-fix-claude-r1/main-session/*.jsonl`
  (+ `subagent-tree/`), fields input_tokens / cache_read_input_tokens /
  cache_creation_input_tokens / output_tokens, grouped by .message.model.
- a0c: per-message usage from `results/a0c-T-fix-r1/transcripts/`, fields
  usage.input / cacheRead / cacheWrite / output per assistant message.
- Pricing: opus $5/$25 per 1M (cache read 0.1×, write 1.25×), sonnet $3/$15,
  haiku $1/$5. Totals reproduce billed $6.09 / $1.82.
