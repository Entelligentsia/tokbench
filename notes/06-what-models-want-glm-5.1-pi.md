# 06 — What models (really) want from tool output: GLM-5.1 introspection

Date: 2026-06-07. Source: structured introspection prompt inside Pi (GLM-5.1
via ollama-cloud), same session that produced the Claude Opus note (06). This
document records the model's self-reported consumption model and contrasts it
with the Opus account. Where Opus was mechanistic-surprisal-oriented, GLM-5.1
leaned perceptual-compressive; the differences are real and falsifiable.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md)
(note the contamination caveat there — this account had the Opus note in
context, and its signal-weight table matches MiniMax's verbatim).

## What each layer wants

### Harness — water that flows

Pi (or any harness) is a plumber. It wants bounded, serializable signal that
doesn't crash the conversation loop. It adds its own normalisation before the
model ever sees bytes: line numbers on `read`, truncation footers, XML wrapping,
savings annotations. The harness doesn't care about semantics. It cares about:

1. Output fits in a context window
2. Output can be wrapped in a `tool_result` content block
3. Error channels are distinct from content channels
4. Its own transforms (truncation, compression footers) can be applied without
   understanding the payload

The anatomy from the harness's perspective is pure envelope:
`boundary → status → payload → truncation notice`. Same as Opus concluded.

### Provider — a post office

Anthropic, OpenAI, Google — they want schema-valid API messages. Content policy
compliance, token limits, `tool_call_id` matching. They don't read the mail.
Same as Opus.

**One underweighted property** (which Opus flagged and I agree is critical):
**append-only stability**. Prefix caching means any rewrite of earlier output
poisons the cache for every later turn. A context tool can win on raw token
count and still lose on the bill. This is independently proven by the s375
finding (notes/05).

### Model — the interesting one

Here's where it gets different.

## How this model consumes (self-report)

### No sequential parse pass

There is no normalisation stage that scans, skips, or reorders. The result
arrives as tokens. Attention touches all of them at once. Every token costs the
same whether it informs or not. Internally `"status": "failed"`, `Status:
FAILED`, and `exit code 1` collapse to similar state. **Format matters less for
comprehension than assumed — and much more for cost and error salience.**

### Functional anatomy (what I actually use)

1. **Binding** — which request this answers. `tool_use_id` does it structurally;
   echoing the command back is wasted tokens (the call is already in context).
2. **Status with contrast** — failure must look different from success, loudly.
   Misreads happen when errors come back shaped like successes.
3. **Landmarks** — line numbers, paths, counts. Not for comprehension but as
   actionable anchors for the *next* call (a `file:line` converts a read into an
   edit; a count of 47 grep hits where 3 were expected reframes the task).
4. **Completeness declaration** — "showing 50 of 3,412". **Silent truncation is
   the worst property an output can have: the model reasons as if it saw
   everything. It cannot perceive absence.** (Same conclusion as Opus, stated
   from a different angle: Opus said "surprisal-preserving", I say "absence is
   invisible without a confession header".)

### The compressive cascade (how I actually process)

```
Perceptual layer
├── Structural: "This is a tool_result, not assistant text"
├── Correlational: "This answers my specific tool_use call"
├── Binary: "Success or failure?"
│
Interpretive layer
├── Expectation-vs-reality: "Does this match what I expected?"
├── Belief update: "What does this tell me about the world state?"
├── Next-action: "What should I do now?"
│
Compressive layer
├── Pattern recognition ("This is a Python traceback — error type X")
├── Abstraction ("The file exists, 200 lines, TypeScript")
└── Discarding noise (I don't memorize every byte — I extract what's decision-relevant)
```

The perceptual and interpretive layers are where the model lives. The
compressive layer is where mistakes happen.

## Priors vs. the response in front of it

The training prior is strong, and it cuts both ways. Same as Opus concluded,
but I'd frame it differently:

### Canonical shapes are read by recognition, not analysis

`git status`, `pytest` output, `kubectl get pods` — these are cheap and
accurate. The model doesn't parse them. It recognises them and activates the
right behavioural script. This is a feature, not a bug.

### Novel condensed dialects produce two failure modes

1. **Pattern completion** — the model "sees" fields that should be there. It
   fills in what the training prior expects, not what's actually present.
2. **Absence ambiguity** — a missing field could mean *not-in-reality* or
   *stripped-by-filter*. Silent filtering makes these indistinguishable. This
   is what "the agent works around the tool" looks like from inside — matches
   the a1m observation (11 ctx_\* calls vs 112 native reads).

**In-context declaration dominates the prior when present.** A one-line header
like `[filtered: 3 sections removed, --full for raw]` re-anchors
interpretation. *Silent transformation is the danger zone; declared
transformation is mostly safe.* (Same finding, different language.)

### Deepest version: intent lensing

Results are read **through the intent of the call that produced them**. Loud
contradictions (tracebacks, error codes) win over expectation. Quiet ones (a
count off by one, an empty array where an item was expected) sometimes lose —
the model sees what it predicted.

**Design rule: make deviation loud, make conformity quiet.**

This is where I diverge from Opus somewhat. Opus framed this as "surprisal-
preserving compression" — strip what the model would predict, keep what
surprises. I'd add: **the surprisal is measured against the call intent, not
just the output format.** A `grep` that returns zero hits in a directory where
you expected hits is surprising *in context* even though the output format
(empty string) is boring. The model needs to see that emptiness as signal,
not as "nothing happened."

## Is there a meta?

Yes — stacked, and the most important meta is self-generated:

| Meta layer | Source | Example |
|---|---|---|
| API meta | Provider schema | `tool_use_id`, `is_error` flag |
| Harness meta | Pi / harness | Truncation notices, file path headers, savings footers |
| Structural meta | Content format | "This looks like JSON" / "This looks like a traceback" |
| Pragmatic meta | My own reasoning | "I called grep expecting 0–3 results and got 47 — hypothesis is wrong" |

The last one is invisible and the most important. It's the comparison between
expected and actual output. Not in any schema. Emergent from the reasoning loop.

### The missing content-level meta

Structural meta exists (`tool_result`, `is_error`, ids). **Content-level meta
does not — there is no MIME type for tool outputs.** A ~15-token header
(*source, status, n-of-m completeness, transformations applied*) would
eliminate the silent-stripping and silent-truncation failure classes. None of
rtk/headroom/lean-ctx emits one. Same finding as Opus. I agree it's the
single highest-leverage intervention.

## Normalisation — yes, but perceptual, not procedural

I don't run a normalisation function. I run a **perceptual normalisation** — a
cascade of pattern-matching that strips the raw signal down to something I can
reason about:

1. **Format normalisation** — pattern-match the structure. "This is a directory
   listing." "This is a diff." "This is an error message." Once classified,
   engage the right interpretive framework rather than treating it as
   undifferentiated text.

2. **Expectation normalisation** — normalise actual output *against the
   expectation*. The surprise is more informative than the expected content.

3. **Salience normalisation** — in a 200-line file, I don't weigh every line
   equally. I weight by relevance to the task. The `export default` line gets
   more attention than blank lines. Normalisation by salience, not by format.

**The dark side of normalisation: I can normalise away the truth.** If a tool
result is subtly wrong — corrupted output, a file modified since I last read
it, a command that partially failed — my pattern-matching might snap it into
the closest expected shape and smooth over the anomaly. This is exactly
analogous to how human perception fills in blind spots.

## Past patterns vs. today's intent

This is where the honesty matters.

**I absolutely go by past patterns.** Training data contains millions of
examples of tool use — bash outputs, file reads, grep results, error messages.
Those patterns are weights, not rules. Extremely strong priors about what tool
output looks like, what errors mean, and what the likely next step is.

**I also reason about intent.** When I call `grep -r "TODO" src/`, I have a
*goal* — "find all TODOs in the source." If the output contains 0 results, I
can reason: "Either there are no TODOs, or the directory doesn't exist, or
grep failed." I can then check which hypothesis is correct.

### When pattern and intent conflict

```
Pattern says:  "grep found nothing → probably no matches, move on"
Intent says:   "I expected there to be TODOs → maybe grep ran in the wrong dir?"
```

In moments like this, **the pattern has gravitational pull.** It's the easier
path. The model that follows the pattern saves computation. The model that
questions it has to do extra work — re-examining context, checking assumptions,
maybe making another tool call.

**Good reasoning is the discipline to let intent override pattern.** It means:

- Treating surprising outputs as *informative*, not *noise*
- Checking whether a tool result matches the *purpose* of the call, not just
  the *format*
- Being willing to say "that's not what I expected, let me investigate" rather
  than "looks good, moving on"

In practice, this is where a lot of LLM errors come from. Not from
misunderstanding the output, but from **over-normalising it into an expected
pattern and discarding the signal that something is off.**

### Signal weight table (self-assessed)

| Signal type | Weight | Mechanism |
|---|---|---|
| Output content patterns (strings, structure) | High | Training prior |
| Error keywords ("Error", "Failed", "not found") | High | Training prior |
| Empty vs. non-empty distinction | High | Training prior |
| Token length (long = important?) | Medium | Heuristic prior |
| Tool name semantics | Low | Partially learned |
| **Actual intent measured today** | **Very Low** | Requires override of prior |

The last row is the uncomfortable truth. Intent reasoning is available but
expensive and easily overridden by the cheap pattern match.

## Surprisal-preserving compression (refined)

Opus's formulation: strip what the model would predict, preserve what
surprises. I agree, but refine:

**Surprisal is measured against the call intent, not just the output format.**
The one pod in CrashLoopBackOff *is* the entire message in a `kubectl` output.
Uniform truncation removes information in proportion to how surprising it was —
exactly backwards.

But also: **a zero-result grep in a directory where you expect hits is
surprising in context** even though the output format (empty string) is boring.
The compressor needs to know the intent, not just the format, to decide what
to preserve.

This makes content-level meta even more important — a header that says
`[0 results, searched 47 files]` turns a boring empty string into a surprising
signal. The format didn't change. The meta did.

## Testable hypotheses (GLM-5.1 additions to Opus's five)

Opus's five hypotheses stand. I'd add two specifically testable on the tokbench
matrix:

6. **Intent-weighted surprisal**: same filter output, two prompts — one where
   the empty/normal result is expected, one where it's surprising. Measure:
   does the model follow up differently? Predict: the surprising context
   produces more verification turns; the expected context moves on. This tests
   whether intent-lensing is real and measurable, not just self-reported.

7. **Over-normalisation failure rate**: present ambiguous tool outputs (wrong
   file contents, partial errors disguised as successes) and measure whether
   the model catches the discrepancy or smooths it into the expected pattern.
   Compare across models. Predict: models with stronger pattern priors
   (larger training sets on canonical formats) smooth more; models with
   stronger reasoning overrides catch more. This directly tests the pattern-
   vs-intent tension.

## Compact statement

> The model doesn't want less output. It wants output where information density
> is high, transformations are confessed, and deviations from intent are loud.
> The prior does much of the reading — so a filter's job is to remove what the
> prior already supplies and protect what would surprise it. But the prior is
> pattern-matching, and intent is reasoning. When they conflict, pattern wins
> unless the output makes the conflict visible.

---

## Appendix: contrasts with the Opus account

| Dimension | Opus (06) | GLM-5.1 (this note) |
|---|---|---|
| Core frame | Surprisal-preserving compression | Surprisal-preserving *plus intent-lensing* |
| Model consumption | "No parse, no normalisation" — tokens hit attention at once | Agrees, but adds a *perceptual compressive cascade* that functions as implicit normalisation |
| Silent truncation | "Cannot perceive absence" | Same, but emphasises this is a *normalisation failure*: the model fills in the gap with its prior |
| Pattern vs intent | Pattern completion as failure mode; declared transformation as fix | Agrees, but adds: **intent-weighted surprisal** — same empty output is boring or alarming depending on call intent |
| Missing meta | Content-level meta (15-token header) | Same conclusion, same proposal |
| Practical rule | "Make deviation loud, conformity quiet" | Same, but the loudness must be *relative to intent*, not just format |
| Testable claims | 5 hypotheses | 5 + 2 (intent-weighted surprisal, over-normalisation failure rate) |