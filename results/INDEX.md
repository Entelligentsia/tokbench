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
| 12 | [a0-T-fix-r2](a0-T-fix-r2/) | 06-07 | A0 native baseline | base:1.0 | **2,183,153** | 159 | 19.5m wall | MATRIX · R01 | Gates green (build=test=lint=0), all 8 phases stop. −2.8% vs a0v validation; commit phase normal (581K). |
| 13 | [a1m-T-fix-r2](a1m-T-fix-r2/) | 06-07 | lean-ctx 3.7.5 stock (Amendment A2) | arm-a1m:1.2 | **3,015,055** (+38.1% vs R01) | 162 | 18.8m wall | MATRIX · R02 | Gates green, all 8 phases stop. Engage: 58 ctx_* calls (38 ctx_read, 9 ctx_find, 5 ctx_ls, 5 ctx_grep, 1 ctx_call) — 3.7.5 steering effective (5× adoption vs pilot). Commit phase anomaly: 32K/3t vs A0's 582K/29t (−94%); all other phases heavier (plan +76%, validate +184%). Gain metrics not harvested (XDG path miss). |
| 14 | [a2-T-fix-r2](a2-T-fix-r2/) | 06-07 | headroom v0.23 proxy (wire-level) | arm-a2:1.0 + sidecar | **1,944,790** (−10.9% vs R01 A0) | 158 | 11.1m wall | MATRIX · R03 | Gates green, all 8 phases stop. Engage: 132/158 requests_compressed ✓. Meters exact: 1,944,790 + 151,192 = 2,095,982 ✓. Headroom genuine: −151,192 (7.21% of counterfactual). Run path −4.0% vs A0 before compression (path variance). CCR: 0 entries/retrievals (no CCR active despite one headroom_retrieve call observed; proxy did not store entries). Commit phase tiny (23K/3t) — same as a1m; may be matrix-run-path pattern vs pilot. |
| 15 | [a3-T-fix-r2](a3-T-fix-r2/) | 06-07 | rtk 0.42.2 (pi tool_call rewrite) | arm-a3:1.0 | **2,147,541** (−1.6% vs R01 A0) | 162 | 6.9m wall | MATRIX · R04 | Gates green, all 8 phases stop. Engage: 54 rtk-rewritten commands ✓ (75.7% on touched = 30.3K saved; 1.4% of total spend). Implement phase: stopReason=stop but errorMessage=terminated (transient tool error, phase completed). Commit phase blew out (476K/34t) — path variance; contrast a1m/a2 where commit was tiny (23–32K/3t). |
| 16 | VOID-a0-T-fix-r3-plan-gate | 06-08 | A0 native baseline (R05 attempt 1) | base:1.0 | — (no harvest: /results permission denied) | ~17 | ~89s | VOID | Plan phase ran 17t/89s but did not write PLAN.md → postflight gate failed (output-missing). Harvest also failed: results dir not pre-created → bench user permission denied. No transcripts. Rerun as R05. |
| 17 | [a0-T-fix-r3](a0-T-fix-r3/) | 06-08 | A0 native baseline | base:1.0 | **2,705,356** (+23.9% vs R01) | 179 | 19.8m wall | MATRIX · R05 | Gates green, all 8 phases stop. Harvest rescued via docker cp (results dir chmod issue; data intact). Commit phase 694K/31t — largest commit phase yet; drives total up. |
| 18 | [a3-T-fix-r3](a3-T-fix-r3/) | 06-08 | a3 rtk 0.42.2 (R06 attempt 1) | arm-a3:1.0 | — (gate fail, ~215K burned) | 21+1 | ~4m | VOID | Plan gate failed: summaries.plan.verdict undefined (require-failed). Plan ran 21t/141s, stopReason=stop — rtk engaged (4 rewrites, 2 vitest). Same plan-gate failure pattern as VOID-a0-T-fix-r3-plan-gate (R05 attempt 1): 3 plan failures in 3 consecutive attempts across 2 arms. Rerun as R06. |
| 19 | [a3-T-fix-r3b](a3-T-fix-r3b/) | 06-08 | rtk 0.42.2 (pi tool_call rewrite) | arm-a3:1.0 | **2,839,459** (+30.1% vs R01 A0) | 186 | 20.7m wall | MATRIX · R06 | Gates green, all 8 phases stop. Engage: 79 rtk rewrites ✓ (67.3% on touched = 42K saved; ~1.5% of total). Review-code blew out: 887K/45t vs R04's 264K/18t (path variance). Commit normal (173K/18t). |
| 20 | [a1m-T-fix-r3](a1m-T-fix-r3/) | 06-08 | lean-ctx 3.7.5 stock (Amendment A2) | arm-a1m:1.2 | **2,699,832** (+23.7% vs R01 A0) | 170 | 20.7m wall | MATRIX · R07 | Gates green, all 8 phases stop. Harvest rescued via docker cp (harvest.sh not executable; fixed). Engage: 51 ctx_* calls (36 ctx_read, 5 ctx_find, 4 ctx_ls, 3 ctx_grep, 2 ctx_call, 1 ctx_shell). cep.sessions=0, total_cache_hits=0 (6th consecutive zero). Validate phase heavy: 582K/32t. |
| 21 | [a2-T-fix-r3](a2-T-fix-r3/) | 06-08 | headroom v0.23 (R08 attempt 1) | arm-a2:1.0 + sidecar | — (gate fail, ~1.49M billed; 144K removed) | 113+1 | ~14m | VOID | Validate gate: verdict missing after subagent completed (forge-engineering#41 pattern, now on validate phase — 3rd affected phase in 2 days). 5/8 phases complete. Headroom engaged: 77/114 compressed, 143,920 removed (8.79%). Rerun as R08. |
| 22 | [a2-T-fix-r3b](a2-T-fix-r3b/) | 06-08 | headroom v0.23 (R08 attempt 2) | arm-a2:1.0 + sidecar | — (provider hang, ~2.07M billed across 6 phase-txns) | 121+1 | ~19m | VOID | **Non-recovered provider hang (§5), NOT #41.** review-code (glm-5.1) upstream request hung 305s (proxy max_latency_ms=305409, err=none — proxy forwarded clean, ollama.com hung); pi timed out → stopReason=error / api_error empty. Pipeline looped implement→review-code ×2 then halted; 6/8 phase-txns, never reached validate. Rerun as R08. |
| 23 | [a2-T-fix-r3c](a2-T-fix-r3c/) | 06-09 | headroom v0.23 (R08 attempt 3) | arm-a2:1.0 + sidecar | **2,571,467** (+17.8% vs R01 A0) | 230 | 15.3m wall | MATRIX · R08 | Gates green, all 8 phases stop; engage-check pass. **Clean run — no sidecar intervention** (prior 2 attempts voided: R08a #41 validate gate, R08b provider hang). Headroom genuine: 177/230 requests_compressed, −238,074 removed (8.47% of 2,809,541 counterfactual; avg 8.6%, best 19.7%). prefix_cache cached=0 (no CCR storage — consistent across all a2 runs). Validate phase heavy (561K/39t). |
| 24 | [a0-T-fix-r4](a0-T-fix-r4/) | 06-09 | A0 native baseline | base:1.0 | **2,693,419** (+23.4% vs R01) | 159 | 18.4m wall | MATRIX · R09 | Gates green, all 8 phases stop; engage pass. Clean — no #41. 3rd A0 anchor (R01 2.18M · R05 2.71M · R09 2.69M; range 2.18–2.71M). Validate 679K/40t + commit 564K/39t are the heavy phases. Harvest stamped image=unknown (base run omits TOKBENCH_IMAGE); corrected in manifest. |
| 25 | [a2-T-fix-r4](a2-T-fix-r4/) | 06-09 | headroom v0.23 (R10) | arm-a2:1.0 + sidecar | **2,804,324** (+28.5% vs R01 A0) | 203 | 16.3m wall | MATRIX · R10 | Gates green, all 8 phases stop; engage pass. Clean — no #41, no intervention. Headroom genuine: 121/203 requests_compressed, −147,809 removed (5.01% of 2,952,133 counterfactual; avg 7.8%, best 19.7%). prefix_cache cached=0 (consistent). Commit phase 927K/53t = largest commit phase in matrix; drives total up. a2 series now R03 −10.9% · R08 +17.8% · R10 +28.5% (commit-phase path variance dominates). |
| 26 | [a3-T-fix-r4](a3-T-fix-r4/) | 06-09 | rtk 0.42.2 (pi tool_call rewrite) | arm-a3:1.0 | **2,959,227** (+35.5% vs R01 A0) | 188 | 20.2m wall | MATRIX · R11 | Gates green, all 8 phases stop; engage pass. Clean — no #41. rtk engaged: 47 commands rewritten, 32.1K saved (64.4% on touched, ~1.1% of total). rtk-gain.json empty (JSON export miss); stats from rtk-history.txt. Heavy review-code 545K + validate 537K + commit 531K. a3 series R04 −1.6% · R06 +30.1% · R11 +35.5% (path variance). image=unknown stamp corrected in manifest. |
| 27 | [a1m-T-fix-r4](a1m-T-fix-r4/) | 06-09 | lean-ctx 3.7.5 stock (Amendment A2) | arm-a1m:1.2 | **3,577,301** (+63.9% vs R01 A0) | 170 | 37.5m wall | MATRIX · R12 | Gates green, all 8 phases stop; engage pass (64 ctx_* calls, highest yet). Clean — no #41. **Matrix-max total.** lean-ctx gain: only 5.8K saved, cache 0% (7th consecutive zero-cache a1m run; CEP never engages). Heavy plan 593K + review-code 590K + commit 738K. a1m series R02 +38.1% · R07 +23.7% · R12 +63.9% (median +38.1%) — consistently large positive: injected MANDATORY rules inflate context far beyond lean-ctx's negligible savings. image=unknown stamp corrected. |
| 28 | [a0-T-fix-r5](a0-T-fix-r5/) | 06-09 | A0 native baseline | base:1.0 | **2,122,389** (−2.8% vs R01) | 159 | 14.1m wall | MATRIX · R13 | Gates green, all 8 phases stop; engage pass. Clean — no #41. 4th A0 anchor, lowest yet. A0 range now 2.12M–2.71M (R01 2.18M · R05 2.71M · R09 2.69M · R13 2.12M). Light writeback 74K + implement 222K. Provisional arm medians: a1m +38.1% (above), a3 2.84M (above), a2 2.57M (inside band). image=unknown corrected. |
| 29 | [a0-T-fix-r6](a0-T-fix-r6/) | 06-09 | A0 native (R14 attempt 1) | base:1.0 | — (provider quota 429, ~1.22M billed across 5 phase-txns) | 95+ | ~11m | VOID | **Non-recovered provider outage (§5), NOT #41.** validate (glm-4.7) returned 429 session-usage-limit (ollama.com quota exhausted mid-run; ref ded6251c). 4/8 phases stop (plan/review-plan/implement/review-code), validate stopReason=error. Rerun as R14 after ~1h quota reset. |
| 30 | — | 2nd weekly window | 1-run matrix remaining: R14 (A0, 5th anchor) rerun → a0-T-fix-r6b | 1.0-gen images | | | | MATRIX | Publication dataset. Frozen order in [PROTOCOL §3](../bench/PROTOCOL.md); claim rule: arm median outside A0×5 range |

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
   agent-loop harness (Claude Code) fed 3.8× the tokens (5.2× vs 4ge on the
   same Anthropic rail, at near-equal output tokens — the work is the same
   size; the delta is context carriage). System-prompt weight: CC main loop
   boots at 29.3K vs 10.2K mean for a 4ge phase, and preamble carriage is
   ~63% of all fed tokens in BOTH harnesses — architecture decides the
   absolute volume, not the overhead share. Full dollar anatomy (bill-exact
   $6.09 vs $1.82): [notes/05](../notes/05-architecture-comparison.md). The
   biggest context optimization in this study is the harness, not any
   middleware.
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
| lean-ctx | [#361](https://github.com/yvgude/lean-ctx/issues/361) | ACTIVE: mcp.json bug → 3.7.4 (A1); read-path finding confirmed "genuine bug" → **3.7.5** (~7h turnaround, bridge default-on, ctx_read→bridge) → **Amendment A2**, arm a1m:1.2 verified (re-reads 28/69 chars — cache mechanism real on pi for the first time); s375 shakedown run: 8/8 complete, 49% read adoption stock, gain still "0 saved" — cache per-server-process × phase-per-process harness = zero cache surface (probe-verified); s375 results + close-out posted (2026-06-06): fixes acknowledged working-as-designed, no further iteration requested — zero-savings is architecture–surface fit, not product failure; cep-meter + 4 still-CLI tools flagged as non-blocking FYIs; additive-vs-replace declared moot (matrix proceeds on stock additive per A2); maintainer invited to refresh quotable statement post-results |
| rtk | [#2292](https://github.com/rtk-ai/rtk/issues/2292) | filed, no response yet |
| headroom | [#645](https://github.com/chopratejas/headroom/issues/645) | filed, no response yet |
