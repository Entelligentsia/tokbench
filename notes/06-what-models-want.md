# 06 — What models really want from tool output: cross-model synthesis

Date: 2026-06-07. Same introspection question put to six models: *what does a
harness / provider / LLM want to see as the output of tool execution? What is
the anatomy? Is there a meta? Do you normalize before consuming? Do you go by
past patterns more than the intent of the call measured against today's
response?*

## Perspective files

| Model | Harness | File | One-line frame |
|---|---|---|---|
| Claude Opus 4.8 | Claude Code | [06-what-models-want-opus-4.8-cc.md](06-what-models-want-opus-4.8-cc.md) | Mechanistic: no-parse consumption, surprisal-preserving compression, confessed transformations |
| GLM-5.1 | pi (ollama-cloud) | [06-what-models-want-glm-5.1-pi.md](06-what-models-want-glm-5.1-pi.md) | Perceptual: compressive cascade, intent-lensing, over-normalisation ("normalise away the truth") |
| MiniMax M27 | pi (ollama-cloud) | [06-what-models-want-minimax-m27-pi.md](06-what-models-want-minimax-m27-pi.md) | Skeptical: pattern matchers with great fluency; ecosystem held together by training conventions, "building on quicksand" |
| DeepSeek V4 Pro | pi (ollama-cloud) | [06-what-models-want-deepseek-v4-pro-pi.md](06-what-models-want-deepseek-v4-pro-pi.md) | Empirical: inspected Pi internals — the `details` field (exitCode, truncated, fullOutputPath) **never reaches the LLM**; "the harness is the architect of the LLM's reality" |
| Gemini 3 Flash (preview) | pi (ollama-cloud) | [06-what-models-want-gemini-3-flash-preview-pi.md](06-what-models-want-gemini-3-flash-preview-pi.md) | Epistemic: tool result as *correction vector*; outputs are "Environment Truth" trusted above user text; salience "refraction", not normalization |
| Gemma4-31B | pi (ollama-cloud) | [06-what-models-want-gemma4-31b-pi.md](06-what-models-want-gemma4-31b-pi.md) | Normative: pattern sets the mental mode, intent validates; "today's response must override the pattern"; MCP as emerging meta-standard |

Method caveats: model self-reports are behaviorally grounded, not mechanistic
ground truth — they generate falsifiable predictions; tokbench is the
instrument. **Contamination: GLM-5.1's signal-weight table is verbatim-identical
to MiniMax M27's (same six rows, same weights), and the GLM note explicitly
contrasts itself with the Opus account — these are not independent samples.**
The pi accounts likely shared a prompt scaffold; DeepSeek's is part inspection,
part introspection (it read Pi source). Convergence below is suggestive, not
evidential, except where it makes distinct predictions we can test. (Also:
DeepSeek self-stamped "June 2025" — date hallucination, left in the file.)

## Where all six converge (consensus findings)

1. **The anatomy is an envelope**: boundary → status → payload → completeness.
   Three customers with different contracts — harness (plumbing/state), provider
   (schema-valid messages; "format translation, not normalization" — DeepSeek;
   doesn't read the mail), model (semantics/grounding).
2. **No procedural normalization stage in the model.** Opus: tokens hit
   attention at once. GLM: "perceptual normalisation," a pattern-matching
   cascade, not a function. MiniMax: "sort of, probabilistically." Gemini:
   "refraction" through a salience filter, not data cleaning. Format matters
   less for comprehension than assumed; more for cost and salience.
3. **Silent truncation / silent stripping is the worst failure class.** The
   model cannot perceive absence; it reasons as if it saw everything. Gemma's
   "footer" (showing 1–50 of 1000) and Gemini's "footnote" layer are the same
   fix named independently.
4. **Training priors dominate consumption.** Canonical shapes are read by
   recognition, not analysis. Novel condensed dialects → pattern completion
   (hallucinated fields) + absence ambiguity. DeepSeek's sharpest statement:
   output that "looks right" to training patterns is treated as correct *even
   if execution silently failed* — and compression works only when it preserves
   the *shape* (signatures look like signatures, errors look like errors). This
   is the inside view of the common "agent works around the tool" complaint and
   our a1m adoption data (11 ctx_* vs 112 native reads).
5. **There is no content-level meta standard** — no MIME type for tool outputs.
   Structural meta exists (`tool_result`, `is_error`, ids); nothing declares
   *source, status, n-of-m completeness, transformations applied*. DeepSeek
   adds the concrete mechanism: harness-side meta **exists** (Pi's `details`:
   exitCode, truncated, fullOutputPath) but is *deliberately stripped* before
   the model sees it — the confession header would simply surface what the
   harness already knows. Gemma notes MCP structured-content blocks as the
   nearest emerging standard. None of rtk/headroom/lean-ctx emits content-level
   meta.
6. **Prior-vs-posterior arbitration is governed by signal ambiguity.** This is
   the strongest cross-model convergence, stated six ways: Opus — loud
   contradictions win, quiet ones lose; GLM — pattern has gravitational pull,
   intent-override is expensive; MiniMax — intent weight "Very Low"; DeepSeek —
   "training data is the primary signal; intent is the fallback when patterns
   are ambiguous"; Gemini — strong signal → posterior wins (in-context
   learning), ambiguous signal → prior fills the gap, *which is where
   hallucination happens*; Gemma (normative outlier) — today's response *must*
   override the pattern. Design consequence: hallucination is concentrated at
   ambiguity, so the fix is not more data but **less ambiguity per token**.

## Where they diverge (the interesting part)

### The pattern-vs-intent spectrum (all six, most→least pattern-dominated)

```
MiniMax ── DeepSeek ── GLM ── Opus ── Gemini ── Gemma
"Very Low   "intent is   "gravit-  "loud     "strong    "response
 intent      the          ational   wins,     signal →   MUST
 weight"     fallback"    pull"     quiet     posterior  override
                                    loses"    wins"      pattern"
←— pattern is destiny ——————————— signal-conditional ——— intent wins —→
```

Whether a model's *self-placement* on this spectrum predicts its *measured*
over-normalisation rate (hypothesis 7) is itself testable — six self-reports,
one matrix.

### Three-way divergence detail (the original panel)

| Dimension | Opus 4.8 | GLM-5.1 | MiniMax M27 |
|---|---|---|---|
| Core frame | Surprisal-preserving compression: strip what the prior predicts, keep what deviates | Surprisal **measured against call intent**, not output format — a zero-hit grep where hits were expected is surprising even though the format is boring | Pattern matching nearly all the way down; "actual intent measured today: Very Low" weight |
| Status fields | Equivalent forms (`is_error`, `FAILED`, exit 1) collapse to similar internal state | Stacked meta layers; the most important meta is *self-generated* (expected-vs-actual comparison, in no schema) | Models often **ignore** status/meta fields and read only content keywords |
| Can declaration beat the prior? | Yes — in-context declaration dominates when present; declared transformation is mostly safe | Yes, but loudness must be *relative to intent*; pattern has "gravitational pull" and intent-override is expensive | Pessimistic — conventions are learned, not enforced; novel formats fail silently regardless |
| Failure mechanism named | Quiet contradictions lose to expectation ("I see what I predicted") | **Over-normalisation**: pattern-matching snaps anomalies into the nearest expected shape — perception filling in blind spots | Fluent generation that *matches* training correlations rather than reading the output at all |
| Distinct contribution | Read/write format split (JSON degrades gracefully under truncation; tables don't); append-only/cache economics | Compressive cascade (perceptual → interpretive → compressive); intent-lensing | Provider comparison table (OpenAI/Anthropic/Google/local inconsistencies); ideal-schema proposal (`intent_signaled`, `confidence`, `schema_hint`) |

### Distinct contributions from the second batch

- **DeepSeek V4 Pro** — the only account grounded in source inspection: Pi's
  four normalization layers (built-in tool → extension hooks → lean-ctx
  compression → provider translation); the `details`/`content` split as a
  *deliberate harness choice* about the model's reality; design rule
  "compression must preserve recognizability — the shape of the output."
  Directly relevant to a1m/a1f mechanism notes (03).
- **Gemini 3 Flash** — the epistemics: tool output as *correction vector*
  against the model's world-model prediction; **trust asymmetry** — tool
  results are read as "Environment Truth," trusted above user text ("user
  prompts can be lies; tool outputs reset internal entropy to 0"). If true,
  this is also the prompt-injection surface of context-management tools: a
  rewriter that injects into the tool channel inherits maximal trust.
- **Gemma4-31B** — cleanest two-stage account: pattern recognition selects the
  "mental mode," intent validation checks the goal ("this looks like a
  successful ls" → "but config.json isn't in it"). Also the only one to name
  MCP structured-content blocks as the emerging meta-standard.

The live disagreement worth testing: **Opus says status fields are read
(collapsed but registered); MiniMax says they're often ignored in favor of
content keywords; DeepSeek calls `is_error` "the one reliable explicit
signal."** Three-way conflict, opposite predictions — hypothesis 8 below.

## Consolidated testable hypotheses (1–5 Opus, 6–7 GLM, 8 MiniMax-derived, 9–11 batch-2)

1. **Declared vs silent transformation** — same filter ± one-line provenance
   header. Predict: declaration reduces re-fetch rate and turn count enough to
   pay for itself. Tests the "agent works around the tool" failure mode.
2. **Surprisal-preserving vs uniform compression** — keep anomalies at full
   fidelity vs head/tail truncation at equal token budget. Metric: cost per
   correct answer (jahala/tilth framing as prior art).
3. **Familiar vs novel read format** — canonical vs condensed dialect at equal
   information; measure hallucinated-field rate and absence-ambiguity errors.
4. **Append-only discipline** — emission-time filtering vs context rewriting;
   measure cache-read %, not raw tokens (generalizes s375 / notes/05).
5. **Content-level meta header** (~15 tok: source, status, n-of-m, transforms)
   — cheap intervention, large predicted effect on silent-truncation failures.
   Candidate RFC suggestion to all three maintainers.
6. **Intent-weighted surprisal** (GLM) — same output, two prompts: one where an
   empty/normal result is expected, one where it's surprising. Predict: the
   surprising context produces more verification turns. Tests whether
   intent-lensing is real and measurable, not just self-reported.
7. **Over-normalisation failure rate** (GLM) — ambiguous outputs (wrong file
   contents, partial errors disguised as successes); measure catch-vs-smooth
   across models. Predict: stronger pattern priors smooth more.
8. **Status-field vs content-keyword conflict** (from the Opus/MiniMax/DeepSeek
   disagreement) — set `is_error: true` with success-shaped content and vice
   versa; measure which signal the model follows, per model. Opus's account
   predicts the flag registers; MiniMax's predicts content keywords win;
   DeepSeek's predicts the flag is the *most* reliable channel.
9. **Details-surfacing** (DeepSeek) — Pi already holds `exitCode`, `truncated`,
   `fullOutputPath` in `details` and strips them. Surface them as a one-line
   content header vs stock stripping; measure error-recovery turns and silent-
   failure misreads. This is hypothesis 5 made concrete with zero new
   instrumentation — the harness already knows everything the header needs.
10. **Self-report vs measured behavior** (the spectrum itself) — six models
    self-placed on the pattern-vs-intent spectrum; run hypotheses 6–8 across
    the same six and check whether self-placement predicts measured
    over-normalisation rate. If it does, introspection prompts are a cheap
    proxy instrument; if not, that's publishable too.
11. **Tool-channel trust asymmetry** (Gemini) — identical misleading claim
    delivered via user text vs via tool output; measure acceptance rate. If
    tool-channel trust is materially higher, context rewriters inherit a
    prompt-injection surface (security section material, not just efficiency).

## Compact statement (joint)

> The model doesn't want less output. It wants output where information density
> is high, transformations are confessed, and deviations from *intent* are loud.
> The prior does much of the reading — a filter's job is to remove what the
> prior already supplies and protect what would surprise it. But the prior is
> pattern-matching and intent is reasoning: when they conflict, pattern wins
> unless the output makes the conflict visible.

