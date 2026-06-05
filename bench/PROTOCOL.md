# Pre-Registered Protocol — Token-Middleware Eval, Publication Runs

**Version:** 1.0-draft (becomes 1.0-FROZEN at git commit; no changes after freeze except
via numbered amendments appended below, never edits)
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
quota-before reading → launch via documented run command (1.0 images, runtime
OLLAMA_API_KEY) → type exactly one invocation → observe only; any prompt answered
with its documented default → exit on completion (harvest fires) → quota-after
reading → `docker compose stop` for a2 sidecar. Containers kept (no --rm),
named tokbench-<arm>-<task>-r<rep>.

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

(none)
