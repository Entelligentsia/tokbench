# tokbench Run Ledger

One row per run, chronological. Every number from provider-reported usage in the
harness transcripts (`<run>/transcripts/`). Deep analysis: [`notes/02-run1-results.md`](../notes/02-run1-results.md).
Status legend: **PILOT** (pre-protocol exploratory, disclosed as priors) ·
**EXPLORATORY** (post-protocol, outside the 14-run matrix) · **VOID** (failed
validity, published per protocol §5) · **MATRIX** (publication dataset — not yet run).

| # | Run | Date (UTC) | Arm / condition | Image | Input tokens | Turns | Model time | Status | Headline |
|---|---|---|---|---|---:|---:|---:|---|---|
| 0 | [VOID-a0-T-fix-r1-failed-0.2](VOID-a0-T-fix-r1-failed-0.2/) | 06-05 | A0 native (aborted) | base:0.2 | — | — | — | VOID | tools/package.json bug aborted collate; led to base-image fix worth ~100–140K/run |
| 1 | [a0-T-fix-r1](a0-T-fix-r1/) | 06-05 | A0 native baseline | base:0.4 | **2,276,305** | 180 | 8.5m | PILOT | The anchor. 5 errs, gates green. Tool output ≈26% of context = middleware ceiling |
| 2 | [a1-T-fix-r1](a1-T-fix-r1/) | 06-05 | lean-ctx 3.7.3 as-shipped (CLI one-shot) | arm-a1:0.2 | **3,622,684** (+59%) | 225 | 25.6m (3.0×) | PILOT | Core feature (cache) disabled by default; ctx_read payloads LARGER than source. Dropped from matrix |
| 3 | [a1m-T-fix-r1](a1m-T-fix-r1/) | 06-05 | lean-ctx 3.7.3 + MCP bridge (vendor-intended) | arm-a1m:0.2 | **3,135,311** (+38%) | 179 | 12.6m (1.5×) | PILOT | Bridge gate-confirmed connected; vendor's own meter: "0 saved · $-0.001"; 11 ctx_* calls (~9% adoption) |
| 4 | [a3-T-fix-r1](a3-T-fix-r1/) | 06-05 | rtk 0.42.2 (pi tool_call rewrite) | arm-a3:0.1 | **2,888,527** (+27%) | 201 | 14.2m | PILOT | rtk worked as designed (74 rewrites, 74.7% saved on touched) — but touched slice ≈2.5% of spend; +27% = path variance |
| 5 | [a2-T-fix-r1](a2-T-fix-r1/) | 06-05 | headroom v0.23 proxy (wire-level) | arm-a2:0.1 + sidecar | **3,244,460** (+43%) | 237 | 14.5m | PILOT | ONLY genuine on-wire saver: −342K verified against bill to 0.0004%; run path longer (237 turns) ate the saving |
| 6 | [a0v-T-fix-base1.0](a0v-T-fix-base1.0/) | 06-05 | A0 on reproducible base (validation) | base:1.0 | **2,246,787** (−1.3%) | 172 | 10.8m | PILOT | Certifies base:1.0 + env-key auth; total-level reproducibility ±1.3%, per-phase swings ±50% |
| 7 | [c0-T-fix-claude-r1](c0-T-fix-claude-r1/) | 06-05 | Claude Code + forge plugin (apples-to-ORANGE) | host CC | **8,685,243 fed** (93% cache reads) | 391 msgs | ~18m | EXPLORATORY | $6.09 measured. Same task, agent-loop architecture: 3.8× token volume vs 4ge |
| 8 | [a0c-T-fix-r1](a0c-T-fix-r1/) | 06-06 | 4ge native on Anthropic models (cache economics) | arm-a0c:1.0-auth | **1,672,470 input-side** (92.1% cache reads, 261 fresh) | 108 | 11.1m wall | EXPLORATORY | **$1.82 actual vs $1.81 projected.** 3.3× cheaper than Claude Code; caching saved ~72% (~$4.80) — ~14× the best middleware effect |
| 9 | [a1m-T-fix-s374](a1m-T-fix-s374/) | 06-06 | lean-ctx 3.7.4 stock shakedown | arm-a1m:1.1 | (2 aborted attempts, ~437K burned) | 31 | — | VOID | Plan phase 0-for-2, two distinct workflow-compliance failures (plan-as-chat-"article"; set-summary skipped). Steering delta ruled out (surface byte-identical) |
| 10 | [a1f-T-fix-r1](a1f-T-fix-r1/) | 06-06 | lean-ctx 3.7.4 + forge-routing addendum (adoption ceiling) | arm-a1f:0.1 | **2,607,368** (+14.5%) | 163 | 8.1m | EXPLORATORY | Adoption 3× (37% of reads); gain meter first-nonzero: "921 saved · $0.02". **ctx_read runs one-shot CLI even with bridge connected (cep.sessions=0, 3rd run) → cached re-read structurally unreachable on pi** |
| 11 | [a1m-T-fix-s375](a1m-T-fix-s375/) | 06-06 | lean-ctx 3.7.5 stock shakedown (Amendment A2) | arm-a1m:1.2 | **4,018,335** (+76%)* | 223 | 14.9m | EXPLORATORY | 8/8 phases, gates green (s374 halt did NOT recur). Read adoption 49% on stock config (steering works: 23 ctx_read vs 24 native) — gain meter still "0 saved": zero cache hits. **All repeats cross-phase; cache is per-server-process (probe-verified) → phase isolation structurally zeroes the cache surface.** cep.sessions=0 (5th time, now with 23 bridge-routed reads). *commit phase ballooned (1.22M/55t); N=1 |
| 12–25 | — | post weekly reset | 14-run matrix: A0×5, a1m×3 (arm-a1m:1.2), a2×3, a3×3 | 1.0-gen images | | | | MATRIX | Publication dataset. Frozen order in [PROTOCOL §3](../bench/PROTOCOL.md); claim rule: arm median outside A0×5 range |

## Standing conclusions (as of 2026-06-06, pre-matrix)

1. **No middleware beat native on billed tokens** in any pilot or exploratory run.
   Best case (a1f, maximum legitimate adoption): still +14.5%.
2. **Headroom is the only product with verified genuine on-wire compression**
   (−342K, ledger-exact vs the bill) — whether it nets out per-run is what the
   matrix answers.
3. **rtk works exactly as designed; its addressable surface here (~2.5%) is below
   the noise floor.** Architecture–surface fit, not product quality.
4. **lean-ctx's cache mechanism now works on pi (3.7.5) — and the harness
   structurally removes its surface.** The maintainer fixed everything we
   reported (bridge default-on, ctx_read bridge-routed, steering agent-visible —
   probe-verified: re-reads collapse to ~13-token stubs within a server
   process). But the session cache is per-process, each forge phase is a fresh
   process, and phase isolation means repeat reads happen only ACROSS phases
   (s375: 5 cross-phase graph.ts reads, 0 within-phase, 0 cache hits, gain
   meter "0 saved" at 49% read adoption). The product's cache and the harness's
   phase isolation monetize the same redundancy; the harness gets there first.
   This is not fixable client-side: the ~13-token stub is a back-reference into
   the conversation, valid only when the model already holds the file in the
   same context — a fresh phase context must be sent the full payload, and the
   provider bills what is sent. Only provider-side prompt caching saves tokens
   across contexts (see conclusion 5).
   Residual product bugs: cep.sessions=0 with confirmed cache hits (meter
   attribution); ctx_shell/grep/ls/find still one-shot CLI. Maintainer engaged
   in [lean-ctx#361](https://github.com/yvgude/lean-ctx/issues/361); fixes
   enter via numbered protocol amendments.
5. **The payment rail decides which optimizations matter**: on Anthropic pricing,
   caching saved ~$4.80/run (a0c measured) — ~14× the largest middleware effect.
   Prefix stability is the dominant economic lever; on request-metered
   ollama-cloud, none of the cache-side effects exist.
6. **Harness architecture dominates middleware**: 4ge's phase isolation +
   governed tools leave ~26% of context addressable; the same task on an
   agent-loop harness (Claude Code) fed 3.8× the tokens. The biggest context
   optimization in this study is the harness, not any middleware.
7. **Noise floor**: identical native runs reproduce within ±1.3% at total level
   but ±50% per phase → single-run benchmarks cannot detect sub-5% effects.
   Hence the A0×5 matrix design.
8. **Completion reliability is a cost dimension of its own.** Orchestration runs
   complete 6/6 without lean-ctx in context; with lean-ctx loaded, 2 of 6
   plan-phase executions halted on workflow-compliance failures (s374: agent did
   the engineering but dropped the artifact choreography — plan emitted as chat
   text; `set-summary` skipped). NOT attributable to version 3.7.4: the
   model-visible surface was proven byte-identical to the 3.7.3 pilot that
   passed. The mechanism is structural — injected MANDATORY rules compete with
   the harness's own workflow for the model's compliance budget, and the gates
   correctly halt when the harness's choreography loses. The a1f addendum
   (routing + explicit "never alter the step" guard) completed 1/1; s375 (3.7.5
   stock) completed 8/8 with gates green — first stock-config completion since
   the pilot, consistent with s374-as-stochastic but n remains too small. The
   a1m×3 matrix reps decide whether stock completion failure is systematic — if
   it recurs, completion rate becomes a headline metric; if not, s374 is demoted
   to stochastic and this row will say so.

## Vendor engagement log

| Vendor | Issue | State |
|---|---|---|
| lean-ctx | [#361](https://github.com/yvgude/lean-ctx/issues/361) | ACTIVE: mcp.json bug → 3.7.4 (A1); read-path finding confirmed "genuine bug" → **3.7.5** (~7h turnaround, bridge default-on, ctx_read→bridge) → **Amendment A2**, arm a1m:1.2 verified (re-reads 28/69 chars — cache mechanism real on pi for the first time); s375 shakedown run: 8/8 complete, 49% read adoption stock, gain still "0 saved" — cache per-server-process × phase-per-process harness = zero cache surface (probe-verified); residuals: cep.sessions=0 persists (meter attribution), ctx_shell/grep/ls/find still one-shot CLI, additive-vs-replace undesignated; run findings NOT yet posted to thread; maintainer offered quotable statement |
| rtk | [#2292](https://github.com/rtk-ai/rtk/issues/2292) | filed, no response yet |
| headroom | [#645](https://github.com/chopratejas/headroom/issues/645) | filed, no response yet |
