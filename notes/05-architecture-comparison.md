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
