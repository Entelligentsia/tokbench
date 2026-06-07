# tokbench Lab Notebook — Index

Experiment: independent token-reduction eval of lean-ctx / rtk / headroom on the
forge-cli (4ge) harness, pi-coding-agent runtime, ollama-cloud models.
Design doc: `~/src/entelligentsia.in/research/context-optimization-market/10-eval-experiment-design.md`
Pins: `../bench/pins.env` · Results: `../results/` · Arm Dockerfiles: `../bench/docker/`

| Note | Contents |
|---|---|
| [../results/INDEX.md](../results/INDEX.md) | **RUN LEDGER — one row per run: image, numbers, status, headline; standing conclusions; vendor log. Start here.** |
| [01-infrastructure.md](01-infrastructure.md) | Image lineage, build gotchas, run commands, harvest contract, analysis jq snippets |
| [02-run1-results.md](02-run1-results.md) | A0 vs A1 full data + mechanism analysis (the +59%/3× finding) |
| [03-product-integration-notes.md](03-product-integration-notes.md) | lean-ctx pi internals; rtk + headroom efficient-setup research; per-product gotchas |
| [04-publication-readiness.md](04-publication-readiness.md) | Research-grade requirements: reproducible base:1.0, pre-registered protocol, COI/scope/right-of-reply, honest-results discipline. **Run-1 = pilot; reps = publication dataset.** |
| [05-architecture-comparison.md](05-architecture-comparison.md) | c0 (Claude Code) vs a0c (4ge) on Anthropic rail: dollar anatomy ($6.09 vs $1.82, both bill-exact), 5.2× fed-token delta at equal output, **system-prompt weight metric** (boot 29.3K vs 10.2K; carriage ≈63% of fed tokens in BOTH harnesses) |
| [06-what-models-want.md](06-what-models-want.md) | **What models really want from tool output — 6-model SYNTHESIS** (Opus 4.8 / GLM-5.1 / MiniMax M27 / DeepSeek V4 Pro / Gemini 3 Flash / Gemma4-31B): 6 consensus findings (incl. *ambiguity governs prior-vs-posterior*), pattern-vs-intent spectrum, **11 consolidated testable hypotheses**, contamination caveats |
| ├ [06-…-opus-4.8-cc.md](06-what-models-want-opus-4.8-cc.md) | Opus 4.8 (Claude Code): no-parse consumption, surprisal-preserving compression, read/write format split, confessed transformations → hypotheses 1–5 |
| ├ [06-…-glm-5.1-pi.md](06-what-models-want-glm-5.1-pi.md) | GLM-5.1 (pi): perceptual compressive cascade, intent-lensing, over-normalisation ("normalise away the truth"), pragmatic meta → hypotheses 6–7 |
| ├ [06-…-minimax-m27-pi.md](06-what-models-want-minimax-m27-pi.md) | MiniMax M27 (pi): provider comparison table, "pattern matchers with great fluency", status fields often ignored, ideal-schema proposal → hypothesis 8 (via 3-way disagreement) |
| ├ [06-…-deepseek-v4-pro-pi.md](06-what-models-want-deepseek-v4-pro-pi.md) | DeepSeek V4 Pro (pi): **inspected Pi internals** — `details` (exitCode/truncated) stripped before model; 4 normalization layers incl. lean-ctx pipeline; "harness is the architect of the LLM's reality" → hypothesis 9 |
| ├ [06-…-gemini-3-flash-preview-pi.md](06-what-models-want-gemini-3-flash-preview-pi.md) | Gemini 3 Flash (pi): tool result as correction vector; **trust asymmetry** (tool channel = "Environment Truth") → hypothesis 11; salience refraction |
| └ [06-…-gemma4-31b-pi.md](06-what-models-want-gemma4-31b-pi.md) | Gemma4-31B (pi): pattern→mode, intent→validation two-stage; "today's response must override the pattern"; MCP as emerging meta-standard |

## State as of 2026-06-07 evening (post matrix R01–R04)

- ✅ **Matrix R01 (A0)**: 2,183,153 input, 159 turns — first publication anchor; −2.8% vs a0v validation, within noise
- ✅ **Matrix R02 (a1m 3.7.5)**: 3,015,055 (+38.1% vs R01 A0), 162 turns — 3.7.5 steering effective (58 ctx_* calls, 5× pilot); overhead consistent with pilot; gain metrics not harvested (XDG path miss — fix harvest before r3)
- ✅ **Matrix R03 (a2 headroom)**: **1,944,790 (−10.9% vs R01 A0)** — FIRST NEGATIVE; headroom genuine −151,192 (7.21%); meters exact; CCR 0 entries (no CCR active despite one headroom_retrieve call observed)
- ✅ **Matrix R04 (a3 rtk)**: 2,147,541 (−1.6% vs R01 A0), 162 turns — 54 rewrites, 75.7% on touched = 1.4% of total; within noise floor; consistent with pilot
- ⬜ 10 matrix runs remain: A0×4, a1m×2, a2×2, a3×2 — next R05=A0 after weekly reset
- ⚠ **Commit phase variance observed**: A0 commit 581K/29t, a1m 32K/3t, a2 23K/3t, a3 476K/34t — lean-ctx and headroom arms had trivially short commits; N=1, watch in reps
- ⚠ **pi-headroom npm pkg found** (npmjs `pi-headroom` by mslavov) — third-party pi extension using context-hook architecture (not wire proxy); NOT the original maintainer's integration model; current a2 proxy setup is the intended approach; headroom#645 still open
- ⚠ **lean-ctx gain harvest missing** in a1m-T-fix-r2 — XDG paths (~/.config/lean-ctx/, ~/.local/share/lean-ctx/) not landing in results; check harvest.sh before next a1m run
- ✅ **Amendment A2** committed and arm-a1m:1.2 verified (3.7.5, bridge default-on, ctx_read→bridge) — replication arm for all remaining a1m runs. Full matrix results in INDEX.md.

## State as of 2026-06-05 evening (archived)

- ✅ A0 (native) rep-1 complete — banked
- ✅ A1 (lean-ctx as-shipped default) rep-1 complete — banked, net-negative (+59% input, 3× time)
- ✅ a1m (lean-ctx + MCP bridge) rep-1 complete — banked: +38% input vs A0, 1.5× time, vendor's own gain meter reports "0 tokens saved, $-0.001" (see 02)
- ✅ a3 (rtk) rep-1 complete — banked: rtk worked as designed (74 rewrites, 74.7% saved on touched, zero caused failures) but effect ≤58K ≈ 2.5% of input, below noise floor; billed +27% vs A0 = path variance (see 02 four-way verdict)
- ✅ a2 (headroom) rep-1 complete — banked: ONLY product with measured genuine savings (−342K = −9.5%% wire counterfactual, avg 10.2%%, meters agree 237==237); +0.9s/turn latency (see 02 five-way verdict)
- ✅ base:1.0 BUILT + CERTIFIED (reproducible, credential-free; a0v validation run: A0 reproduces within 1.3% across bases; tools-fix worth ~100–140k/run)
- ✅ 1.0 arm images built + verified: a1m:1.0, a3:1.0, a2:1.0 (binaries vendored + sha256-pinned; compose on 1.0 with runtime OLLAMA_API_KEY)
- ✅ **lean-ctx maintainer RESPONDED** (#361, 2026-06-05/06): mcp.json trap confirmed as bug, **3.7.4 shipped** (flag-wins); re-run requested pre-June-17; maintainer statement offered. Our reply posted with adoption decomposition (11 ctx_* vs 112 native; cep.sessions=0 puzzle) + additive-vs-replace question. See 03.
- ✅ **Protocol Amendment A1** committed: a1m replication arm = lean-ctx 3.7.4, workaround dropped → **tokbench-arm-a1m:1.1** (276576ce0a27) built + verified credential-free
- ✅ **a0c run COMPLETE** (2026-06-06): **$1.82 actual vs $1.81 projected** — exact to the cent; 92.1% cache reads, 261 fresh input tokens whole run, 108 turns (glm: 180), 3.3× cheaper than Claude Code's $6.09. Full table + 5 findings in 02. Deviation logged (bash entrypoint → manual launch + post-hoc harvest; run counts, exploratory)
- ⬜ THEN (post weekly reset): 14-run rep matrix — **a1m runs use arm-a1m:1.1** (A0×5, a1m×3, a2×3, a3×3)
- ⬜ WATCH: #361 — follow-up POSTED (issuecomment-4637299015): 3.7.4 verified; read-path-outside-bridge-cache mechanism (cep=0 ×3 runs) + steering-inert-on-pi + a1f ceiling test delivered; flagged that stock reps will mechanically reproduce "0 saved" unless reads reach the bridge session. Awaiting: read-path answer, additive-vs-replace → possible Amendment A2. rtk#2292 + headroom#645 still unanswered
- ⚠ **s374 shakedown (3.7.4): plan phase 0-for-2** — two distinct workflow-compliance failures (attempt 1: plan emitted as chat "article", zero artifact writes; attempt 2: artifacts written but `set-summary` skipped → store verdict undefined). Steering hypothesis ELIMINATED: agent-visible instruction surface proven byte-identical 3.7.3↔3.7.4 (rules hashed; extension descs unchanged; bridge's 9 registered schemas diffed identical; the 4 steered MCP descs are deduped off the pi path — #168 fix INERT on pi). Third attempt pending. Data: results/a1m-T-fix-s374
- ✅ **a1f run COMPLETE** (2026-06-06): adoption 3× (31 ctx calls, 37% of reads), gain meter first-nonzero (921 tok/$0.02), but still +14.5% billed vs A0; sec/turn back to ~native. **STRUCTURAL: ctx_read runs one-shot CLI even with bridge connected (cli_full in stats, cep.sessions=0, 3rd consecutive run) → ~13-tok cached re-read unreachable on pi.** Full table + verdict in 02. Quota: 78.7→81.7%
- ✅ a3 (rtk) image built: `tokbench-arm-a3:0.1` — rtk 0.42.2, pi ext, arm-setup re-init hook; rewrite sanity verified (git→rewrite exit 3; node store-cli→passthrough exit 1 as predicted)
- ✅ a2 (headroom) BUILT + SMOKE-TESTED — proxy chain to ollama-cloud verified incl. streaming; CCR self-handles retrieves at wire level (earlier "trap" was wrong — defaults correct); compose pair in bench/docker/arm-a2-headroom (see 03)
- ⬜ reps 2-3, other task shapes (T-feature, T-explore)

## Standing operator directives

- Runs are INTERACTIVE, one at a time; observe-only, defaults on prompts
- NO `--rm` on run containers — keep for forensics (`tokbench-<arm>-<task>-r<rep>` naming)
- Transcripts (`.forge/transcripts/` per-phase JSON) are the PRIMARY dataset; COST_REPORT/collate is optional reporting
- Ollama dashboard = fuzzy meter; transcript `turns` counts are authoritative for requests
- Quota: ~2.7% weekly per run → full matrix needs 2+ weekly windows
- Record quota dashboard reading before/after each run (quota-before/after.json in results dir)
