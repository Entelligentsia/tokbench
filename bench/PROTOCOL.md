# Pre-Registered Protocol — Token-Middleware Eval, Publication Runs

**Version:** 1.0-FROZEN (operator-approved 2026-06-06; changes only via numbered
amendments appended below, never edits)
**Drafted:** 2026-06-05
**Pilot disclosure:** an exploratory pilot (5 arms × 1 run, T-fix) ran 2026-06-05 on
pre-reproducibility infrastructure. Its results are KNOWN to the authors and are
disclosed as priors below. This protocol was written after the pilot and frozen
before any publication run.

## 1. Research question

On a context-frugal agentic harness (forge-cli/4ge on pi-coding-agent) with a
request-metered provider (ollama-cloud), do token-optimization middleware products
reduce provider-billed input tokens on identical, repeatable SDLC tasks — without
degrading task success — and at what latency cost?

## 2. Conditions (image IDs in bench/pins.env; all FROM tokbench-base:1.0)

| Arm | Condition | Image |
|---|---|---|
| A0 | native forge/pi (control) | tokbench-base:1.0 |
| a1m | lean-ctx 3.7.3, pi extension, embedded MCP bridge CONNECTED (gate-checked at session start) | tokbench-arm-a1m:1.0 |
| a2 | headroom proxy v0.23.0 sidecar, wire-level, defaults (CCR self-handling) | tokbench-arm-a2:1.0 + compose |
| a3 | rtk 0.42.2, transparent pi tool_call rewrite | tokbench-arm-a3:1.0 |

Dropped: lean-ctx CLI-default path (pilot showed its core feature disabled; not a
fair representation — pilot data stands as the integration-fragility evidence).

## 3. Task & runs

**Primary (confirmatory): T-fix = `/forge:run-task CART-S01-T01`** (8-phase pipeline,
objective gates: build/test/lint + acceptance criteria). State reset to golden
PRISTINE before every run (testbench/reset.sh; verified against MANIFEST checksum).

**Run matrix: 14 runs** — A0 ×5 (noise-floor anchor), a1m/a2/a3 ×3 each.
Execution order (fixed, interleaved to spread provider-load drift):

```
R01 A0   R02 a1m  R03 a2   R04 a3
R05 A0   R06 a3   R07 a1m  R08 a2
R09 A0   R10 a2   R11 a3   R12 a1m
R13 A0   R14 A0
```

**Secondary (exploratory, quota permitting): T-diagnose = `/forge:fix-bug CART-BUG-002`**
(read/diagnosis-heavy shape) — A0 ×2, each arm ×1; analyzed descriptively only.

## 4. Primary metric & secondaries

**Primary:** total provider-billed input tokens per successful run
(Σ usage.input across all phase transcripts, `.forge/transcripts/<task>/*__<phase>.json`).

Secondary: turns (=requests), output tokens, model seconds, sec/turn, per-phase
breakdowns, tool-error and provider-error (HTTP 5xx in errorMessage) counts,
product self-metrics audited against billed (lean-ctx gain --deep; rtk gain;
headroom /stats — incl. its within-run counterfactual tokens_removed, which is a2's
genuine-effect measure), a0/a2 contamination checks (rtk_tokens_avoided==0 in a2).

## 5. Validity & exclusion rules (pre-declared)

A run COUNTS iff: all phases stopReason=stop AND gates green (build=test=lint=0)
AND engage-check passes (a1m: bridge "embedded (connected)" at start + ≥1 ctx_* call;
a3: ≥1 rtk-rewritten command in history; a2: /stats requests_compressed ≥ 1;
A0: no product state/calls).
- Engage-check fail → VOID, rerun (logged).
- Gates fail / phase error-stop → reported separately, excluded from token comparison.
- Provider outage mid-run (non-recovered) → VOID, rerun (logged).
- Operator deviation from §6 → noted in manifest; run kept unless deviation is material
  (judged before unblinding the run's numbers — i.e., before harvest is read).
All voids and reruns are published.

## 6. Operator protocol

Interactive TUI runs, ONE session at a time, same operator throughout. Per run:

1. **quota-before**: `bench/scripts/record-quota.sh before results/<run-dir> <pct>`
2. **launch**: documented run command (1.0 images, runtime OLLAMA_API_KEY).
   For a1m/a1f runs: add `-v $(pwd)/bench/docker/base/harvest.sh:/usr/local/bin/harvest.sh:ro`
   until arm images are rebuilt with the fixed harvest (a1m/a1f case was missing; fixed 2026-06-07).
3. **type exactly one invocation** → observe only; any prompt answered with its documented default
4. **exit on completion** (harvest fires automatically)
5. **quota-after**: `bench/scripts/record-quota.sh after results/<run-dir> <pct>`
6. `docker compose stop` for a2 sidecar runs only

Containers kept (no --rm), named tokbench-<arm>-<task>-r<rep>.

Recording: asciinema is OPTIONAL (illustration only, not evidence). Operator
conduct is auditable from the transcripts themselves: the pipeline is autonomous
after the single invocation, and operator touchpoints go through recorded
channels (forge_ask_user tool calls, session message log). Any reader can render
any published run with the replay recipe in the README.

## 7. Analysis plan

Descriptive only (n too small for NHST): per-arm median ± min/max of the primary
metric; noise floor = A0 spread (n=5); a difference is CLAIMED only if the arm's
median lies outside A0's observed range. Per-phase medians for mechanism narrative.
a2's effect additionally measured by its on-wire counterfactual (billed + tokens_removed
vs billed). Vendor-meter audit table (self-reported vs billed) for all arms.
Latency: sec/turn (operator-independent, from transcript timestamps).
Pilot priors (disclosed): a1m +38%, a3 +27% (suspected variance), a2 −9.5%
counterfactual, A0 total-level reproducibility ±1.3% across bases.

## 8. Quota & scheduling

~2.5–3.5% weekly per run → 14 runs ≈ 40–50% of one weekly window. Runs begin after
the next weekly reset; projected post-run usage computed before each run; campaign
pauses if projection exceeds 90%.

## 9. Infrastructure (fixed, published)

bench/pins.env (image IDs, binary sha256s, scaffold artifact hash, testbench SHA,
model map: glm-5.1/4.7/4.6 persona tiers). Reproducible from bench/ + OLLAMA_API_KEY
only. Known environment notes: ollama-cloud reports no cache tokens (no caching
economics in scope); transient provider 500s are auto-retried by the runtime and
counted, not excluded.

## 10. Conflicts & scope (published verbatim with results)

The harness (forge-cli/4ge) and testbench are the operator-author's own products;
the author is a daily lean-ctx user. Findings are scoped to: this harness, this
provider (request-metered, no cache discounts), one small TypeScript codebase,
interactive operation. No claim is made that any product fails generally; claims
are about architecture–surface fit and as-shipped integration behavior on this stack.

## Amendments

### A1 — lean-ctx 3.7.4 for the a1m arm (2026-06-06, pre-replication)

**Trigger:** maintainer response in
[yvgude/lean-ctx#361](https://github.com/yvgude/lean-ctx/issues/361)
(2026-06-05/06). Maintainer confirmed the 3.7.3 behavior we worked around
(`init --agent pi` writes `~/.pi/agent/mcp.json`; extension treats it as an
external adapter and disables the embedded bridge even with
`LEAN_CTX_PI_ENABLE_MCP=1`) as a bug, fixed in **3.7.4** (explicit flag now
wins), released on all channels.

**Changes (a1m arm only):**
1. Pin lean-ctx **3.7.4** (was 3.7.3); vendored binary + sha256 updated in
   `bench/pins.env`; image rebuilt as `tokbench-arm-a1m:1.1`.
2. Drop the `rm ~/.pi/agent/mcp.json` workaround from the Dockerfile and
   `arm-setup.sh` (no longer needed per maintainer; 3.7.4 flag-wins behavior
   is the configuration under test).
3. Pre-run gate unchanged: `/lean-ctx` must report
   `MCP bridge: embedded (connected)` with a non-zero tool count before the
   task invocation; otherwise VOID per §5.

**Unchanged:** run matrix, order, metrics, validity rules, all other arms.
Mode question (additive vs replace) posed to maintainer in #361; if maintainer
designates replace mode as the savings-faithful configuration, that will enter
as a further numbered amendment before the affected runs.

### A2 — lean-ctx 3.7.5 for the a1m arm (2026-06-06, pre-replication; supersedes A1)

**Trigger:** maintainer response in
[yvgude/lean-ctx#361](https://github.com/yvgude/lean-ctx/issues/361)
(2026-06-06, v3.7.5 released 11:11 UTC). Maintainer confirmed our structural
finding — the pi extension's read tools (`ctx_read`/`ctx_shell`/`ctx_grep`/
`ctx_ls`/`ctx_find`) spawned one-shot CLI subprocesses on every call, bridge
or no bridge, so reads never touched the bridge-resident session cache and
`cep.sessions`/`total_cache_hits` stayed 0 in every bridge-connected run —
as a genuine bug, fixed in **3.7.5**: the embedded bridge is now **on by
default**, and every `ctx_read` (including line-range reads) routes through
it with a CLI fallback. The #168 "Prefer over native…" steering is now
carried by the pi extension's own tool descriptions.

**Changes (a1m arm only):**
1. Pin lean-ctx **3.7.5** (was 3.7.4); vendored binary + sha256 updated in
   `bench/pins.env` (verified against the release's published SHA256SUMS);
   pi-lean-ctx npm pin **3.7.5**; image rebuilt as `tokbench-arm-a1m:1.2`.
2. Drop `LEAN_CTX_PI_ENABLE_MCP=1` from the Dockerfile — the configuration
   under test is the **as-shipped 3.7.5 default** (bridge default-on),
   matching the maintainer's designated savings-faithful configuration.
3. Pre-run gate unchanged: `/lean-ctx` must report
   `MCP bridge: embedded (connected)` with a non-zero tool count before the
   task invocation; otherwise VOID per §5.
4. Post-run check added: `stats.json` is harvested as before; whether
   `cep.sessions` / `total_cache_hits` go non-zero is now a **finding**, not
   a validity condition (the maintainer's fix predicts non-zero on repeated
   reads).

**Unchanged:** run matrix, order, metrics, validity rules, all other arms.
The additive-vs-replace question remains open with the maintainer; the
exploratory a1f (adoption-ceiling) arm definition is unaffected and remains
exploratory, outside the confirmatory matrix.
