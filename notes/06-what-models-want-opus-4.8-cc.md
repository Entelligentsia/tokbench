# 06 — What models want from tool output: Claude Opus 4.8 introspection

Date: 2026-06-07. Source: introspection session with Claude (Opus 4.8, inside
Claude Code — the consumer describing its own consumption), prompted by the
tokenomics paper (arxiv 2601.14470) and the read-format question. The model's
self-reports are behaviorally grounded, not mechanistic ground truth.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md).

## Three customers, three contracts

Tool-execution output has three consumers with different wants:

1. **Harness** — plumbing: deterministic framing, size caps, an error channel
   distinct from content, truncation markers. The harness normalizes before the
   model sees anything (Claude Code: line numbers on Read, truncation notices,
   system-reminders). Its anatomy is an envelope: *boundary, status, payload,
   truncation notice*.
2. **Provider** — a well-formed `tool_result` bound to a `tool_use_id`; content
   is just tokens. One underweighted preference: **append-only stability**.
   Prefix caching means anything that rewrites earlier outputs poisons the cache
   for every later turn — a context tool can win on raw token count and still
   lose on the bill. (Independently proven by s375 / notes/05.)
3. **Model** — the interesting one. Everything below.

## How the model consumes (its own account)

- **No parsing, no normalization stage.** No sequential reading pass that scans,
  skips, or normalizes — the result arrives as tokens and attention touches all
  of them at once; every token costs the same whether it informs or not.
  Internally `"status": "failed"`, `Status: FAILED`, and `exit code 1` collapse
  to similar state. Format matters less for *comprehension* than assumed — and
  much more for *cost* and *error salience*.
- **Functional needs** (the real anatomy):
  1. *Binding* — which request is this answering. `tool_use_id` does it
     structurally; echoing the command back is wasted tokens, the call is
     already in context.
  2. *Status with contrast* — failure must look different from success, loudly.
     Misreads happen when errors come back shaped like successes.
  3. *Landmarks* — line numbers, paths, counts. Not for comprehension but as
     actionable anchors for the next call (a `file:line` converts a read into
     an edit).
  4. *Completeness declaration* — "showing 50 of 3,412". **Silent truncation is
     the worst property an output can have: the model reasons as if it saw
     everything. It cannot perceive absence.**

## Priors vs. the response in front of it

The training prior is strong, and it cuts both ways:

- Canonical shapes (git status, pytest, kubectl) are read by **recognition**,
  not analysis — cheap and accurate.
- Novel condensed dialects produce two failure modes:
  - **Pattern completion** — the model "sees" fields that should be there.
  - **Absence ambiguity** — a missing field could mean *not-in-reality* or
    *stripped-by-filter*; a silent filter makes these indistinguishable.
  This is what "the agent works around the tool" looks like from inside —
  matches our own a1m observation (11 ctx_* calls vs 112 native reads).
- **In-context declaration dominates the prior when present.** A one-line header
  like `[filtered: 3 sections removed, --full for raw]` re-anchors
  interpretation. *Silent transformation is the danger zone; declared
  transformation is mostly safe.*
- Deepest version: results are read **through the intent of the call that
  produced them**. Loud contradictions (tracebacks) win over expectation; quiet
  ones (a count off by one, an empty array where an item was expected) sometimes
  lose — the model sees what it predicted. Design rule: **make deviation loud,
  make conformity quiet.**

## The design principle: surprisal-preserving compression

Ideal compression for an LLM consumer is not minimal tokens — it is
**surprisal-preserving**: strip the tokens the model would have predicted given
the command (kubectl boilerplate is near-zero information — it would have
generated it itself); preserve at full fidelity what deviates from the prior.
The one pod in CrashLoopBackOff *is* the entire message. Uniform truncation
removes information in proportion to how surprising it was — exactly backwards.

### Read vs write formats (refines the JSON/YAML intuition)

- **Reads, long homogeneous lists**: per-record key repetition in JSON is
  predictable tokens — cost without information; a headed table binds the same
  values cheaper. But the model exploits *regularity*, not *parseability* — and
  tables fail harder under truncation (lose the header, lose bindability) while
  JSON degrades gracefully.
- **Writes**: structure non-negotiable — the consumer there is a parser, not
  the model.

### The missing meta

Structural meta exists (`tool_result`, `is_error`, ids). **Content-level meta
does not — there is no MIME type for tool outputs.** A ~15-token header
(*source, status, n-of-m completeness, transformations applied*) would eliminate
the silent-stripping and silent-truncation failure classes. None of
rtk/headroom/lean-ctx emits one.

### Compact statement

> The model doesn't want less output. It wants output where information density
> is high and the transformations are confessed — the prior does much of the
> reading, so a filter's job is to remove what the prior already supplies and
> protect what would surprise it.

## Hypotheses contributed (1–5 in the consolidated list)

1. **Declared vs silent transformation**: same filter, with/without a one-line
   provenance header. Predict: declaration reduces re-fetch rate and turn count
   enough to pay for itself. Directly tests the "agent works around the tool"
   failure mode (a recurring practitioner complaint; our a1m adoption data).
2. **Surprisal-preserving vs uniform compression**: strip low-surprisal
   boilerplate keeping anomalies at full fidelity, vs head/tail truncation at
   equal token budget. Metric: cost per correct answer (jahala/tilth framing —
   cite as prior art: github.com/jahala/tilth benchmark).
3. **Familiar vs novel read format**: canonical output vs condensed dialect at
   equal information; measure hallucinated-field rate and absence-ambiguity
   errors.
4. **Append-only discipline**: emission-time filtering vs context rewriting —
   measure cache-read %, not raw tokens (generalizes s375 / notes/05).
5. **Content-level meta header** (~15 tok): cheap intervention, large predicted
   effect on silent-truncation reasoning failures. Candidate RFC suggestion to
   all three maintainers.
