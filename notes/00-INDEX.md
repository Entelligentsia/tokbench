# tokbench Lab Notebook — Index

Experiment: independent token-reduction eval of lean-ctx / rtk / headroom on the
forge-cli (4ge) harness, pi-coding-agent runtime, ollama-cloud models.
Design doc: `~/src/entelligentsia.in/research/context-optimization-market/10-eval-experiment-design.md`
Pins: `../bench/pins.env` · Results: `../results/` · Arm Dockerfiles: `../bench/docker/`

| Note | Contents |
|---|---|
| [01-infrastructure.md](01-infrastructure.md) | Image lineage, build gotchas, run commands, harvest contract, analysis jq snippets |
| [02-run1-results.md](02-run1-results.md) | A0 vs A1 full data + mechanism analysis (the +59%/3× finding) |
| [03-product-integration-notes.md](03-product-integration-notes.md) | lean-ctx pi internals; rtk + headroom efficient-setup research; per-product gotchas |
| [04-publication-readiness.md](04-publication-readiness.md) | Research-grade requirements: reproducible base:1.0, pre-registered protocol, COI/scope/right-of-reply, honest-results discipline. **Run-1 = pilot; reps = publication dataset.** |

## State as of 2026-06-05 evening

- ✅ A0 (native) rep-1 complete — banked
- ✅ A1 (lean-ctx as-shipped default) rep-1 complete — banked, net-negative (+59% input, 3× time)
- ✅ a1m (lean-ctx + MCP bridge) rep-1 complete — banked: +38% input vs A0, 1.5× time, vendor's own gain meter reports "0 tokens saved, $-0.001" (see 02)
- ✅ a3 (rtk) rep-1 complete — banked: rtk worked as designed (74 rewrites, 74.7% saved on touched, zero caused failures) but effect ≤58K ≈ 2.5% of input, below noise floor; billed +27% vs A0 = path variance (see 02 four-way verdict)
- ✅ a2 (headroom) rep-1 complete — banked: ONLY product with measured genuine savings (−342K = −9.5%% wire counterfactual, avg 10.2%%, meters agree 237==237); +0.9s/turn latency (see 02 five-way verdict)
- ✅ base:1.0 BUILT + CERTIFIED (reproducible, credential-free; a0v validation run: A0 reproduces within 1.3% across bases; tools-fix worth ~100–140k/run)
- ✅ 1.0 arm images built + verified: a1m:1.0, a3:1.0, a2:1.0 (binaries vendored + sha256-pinned; compose on 1.0 with runtime OLLAMA_API_KEY)
- ✅ **lean-ctx maintainer RESPONDED** (#361, 2026-06-05/06): mcp.json trap confirmed as bug, **3.7.4 shipped** (flag-wins); re-run requested pre-June-17; maintainer statement offered. Our reply posted with adoption decomposition (11 ctx_* vs 112 native; cep.sessions=0 puzzle) + additive-vs-replace question. See 03.
- ✅ **Protocol Amendment A1** committed: a1m replication arm = lean-ctx 3.7.4, workaround dropped → **tokbench-arm-a1m:1.1** (276576ce0a27) built + verified credential-free
- ⬜ NEXT MORNING: a0c run (4ge on Anthropic — image built, command in chat/notes; measures real cache economics + dollars vs $1.81 projection and c0 $6.09)
- ⬜ THEN (post weekly reset): 14-run rep matrix — **a1m runs use arm-a1m:1.1** (A0×5, a1m×3, a2×3, a3×3)
- ⬜ WATCH: #361 maintainer answer on additive-vs-replace mode → possible Amendment A2; rtk#2292 + headroom#645 still unanswered
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
