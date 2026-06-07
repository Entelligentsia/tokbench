# 06 — What models want from tool output: MiniMax M27 introspection

Date: 2026-06-07. Source: same introspection question put to MiniMax M27 inside
pi (ollama-cloud). Self-report, verbatim below; not mechanistic ground truth.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md).
Note: this account's signal-weight table reappears verbatim in the GLM-5.1
note — see the contamination caveat in the synthesis.

## The Anatomy of Tool Execution Output

```
┌─────────────────────────────────────────────────────────────┐
│  Tool Execution Output Anatomy                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. RESULT (the payload)                                    │
│     - Structured data (JSON, text, binary)                  │
│     - What the tool "found" or "did"                        │
│     - This is what we think matters most                    │
│                                                             │
│  2. STATUS/METADATA (the envelope)                          │
│     - success/failure boolean                              │
│     - error message (if failure)                           │
│     - timing/duration                                      │
│     - truncated flag (output too large)                    │
│                                                             │
│  3. CONTEXT WRAPPERS (what harnesses add)                   │
│     - tool_name, tool_call_id                               │
│     - invocation_timestamp                                 │
│     - token count (for accounting)                         │
│     - "grounded_in" or "source" attribution                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## What Harnesses Actually Want

**The honest answer: it depends on the harness, and most are suboptimal.**

### What Pi (my harness) seems to want:

```json
{
  "content": "..." or [ ... ],    // readable by model
  "isError": boolean,              // distinguishes crash from empty
  "hideInOverview": boolean,       // token economics signal
  "truncated": boolean             // trust signal about completeness
}
```

### What OpenAI's function calling expects:

- Tool output is just **a string** (often stringified JSON)
- No formal schema enforcement
- Model learns to interpret "empty string" vs "error message" by pattern

### What Anthropic's tool use expects:

- Similar string-based approach
- More emphasis on `BLOCK` types in their protocol
- Clearer distinction between tool_use and tool_result

---

## Is There a Meta-Standard?

**Short answer: No. There are conventions, and they're inconsistent.**

| Aspect | OpenAI | Anthropic | Google | Local Models |
|--------|--------|-----------|--------|--------------|
| Error representation | String message | String message | String message | Varies wildly |
| Empty success | `null`, `{}`, `[]` | Often omitted | Varies | Often hallucinated |
| Binary output | Base64 string | Base64 or URL | Direct bytes | Usually broken |
| Truncation signal | Often absent | Sometimes `truncated` | Sometimes | Rarely |

The closest thing to a meta-standard is **the XML-like tool format** that emerged from training data:

```
<tool_call>
  <tool_name>read</tool_name>
  <input>{"path": "..."}</input>
</tool_call>

<tool_result>
  <tool_name>read</tool_name>
  <output>...</output>
  <status>success</status>
</tool_result>
```

This pattern is everywhere because models were trained on examples that looked like this. But it's **learned convention, not enforced spec**.

---

## Do We Normalize Before Consuming?

**Harnesses: Yes, usually. LLMs: Sort of, probabilistically.**

### Harnesses normalize by:

1. **Type coercion** — Everything becomes a string (or structured JSON)
2. **Error flattening** — Exceptions → readable error strings
3. **Truncation** — Large outputs get clipped with a marker
4. **Token budgeting** — Lean-ctx and similar tools compress or summarize

### LLMs normalize by:

1. **Pattern matching on training** — "When I see `{error: ...}` I should treat it as failure"
2. **Probabilistic interpretation** — "This looks like a file listing, I'll parse it as such"
3. **Ignoring meta** — Often the model just reads the *content* and ignores status fields

**The uncomfortable truth**: Most LLMs don't systematically parse tool outputs. They generate responses as if they "read" the output, but they're generating text that *matches* patterns from training where similar outputs preceded similar responses.

---

## Past Patterns vs. Today's Intent

This is the most interesting question — and the most revealing.

### The Training Signal Problem

When a model was trained, it saw examples like:

```
Tool: read_file
Output: "The file contains:\n- line 1\n- line 2"
Model response: "I see the file has 2 items..."
```

vs.

```
Tool: read_file
Output: "Error: File not found"
Model response: "The file doesn't exist, would you like me to try another path?"
```

The model learned **correlations** between output patterns and appropriate responses. But:

1. **The model doesn't "understand" the tool semantics** — it matches surface patterns
2. **Today's tool execution is a new context** — not in training data
3. **The gap**: A novel tool or output format will confuse models even if the intent is clear to humans

### What Models Actually Use

| Signal Type | Weight |
|-------------|--------|
| Output content patterns (strings, structure) | High |
| Error keywords ("Error", "Failed", "not found") | High |
| Empty/non-empty distinction | High |
| Token length (long = important?) | Medium |
| Tool name semantics (partially learned) | Low |
| Actual intent (measured today) | **Very Low** |

### The Hard Truth

LLMs are **pattern matchers with great fluency**, not reasoners about tool semantics. When you ask "do they go by past patterns more than today's intent" — the answer is almost entirely **past patterns**.

A model that has never seen a particular tool's output format will struggle, even if the output is perfectly clear to a human. The "understanding" is surface-level and probabilistic.

---

## What Would Better Tool Output Design Look Like?

If we could design from scratch:

```json
{
  "result": {
    "type": "structured",    // vs "text", "binary", "error"
    "data": { ... },
    "schema_hint": "..."     // LLM can validate against this
  },
  "intent_signaled": "query" | "action" | "observation",
  "completeness": "complete" | "truncated" | "partial",
  "confidence": 0.0-1.0,     // tool's own assessment
  "attribution": "..."       // sources for grounding
}
```

But this doesn't exist broadly because:

1. Tool developers don't know what harnesses expect
2. Harnesses don't know what models prefer
3. Models were trained on inconsistent data, so there's no clear signal to optimize toward

---

## Summary Introspection

### What I want as an LLM consuming tool output:

- Clear success/failure signal (don't make me guess)
- Human-readable content I can generate coherent text about
- Error messages that tell me *what happened* and *what to do next*
- Truncation signals so I don't pretend the output is complete

### What I actually get:

- Strings that may or may not be error messages
- JSON that I interpret by pattern-matching structure
- Sometimes helpful errors, often opaque ones
- No meta about the tool's confidence or completeness

### What I rely on:

- Past training patterns heavily
- Surface features (keywords, structure, length)
- Probabilistic generation of "appropriate" responses
- The harness to filter/normalise before I see it

---

## Conclusion

The ecosystem is held together by **conventions that emerged from training data**, not by **designed standards**. That's both its strength (flexible, works with imperfect tools) and its weakness (brittle with novel formats, prone to misinterpretation).

The path forward requires:

1. **Explicit contracts** between harnesses and tools about output schema
2. **Training on diverse, structured tool-output pairs** rather than just natural language descriptions
3. **Meta-fields that models can reliably learn to interpret** (not just hope they pattern-match correctly)
4. **Evaluation frameworks** that test tool-use reliability on novel tools, not just familiar ones

Until then, we're building on quicksand: tools work when they match training patterns, fail silently when they don't.