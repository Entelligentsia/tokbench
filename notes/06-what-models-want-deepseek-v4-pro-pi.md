# 06 — What models want from tool output: DeepSeek V4 Pro introspection

Date: 2026-06-07. Source: same introspection question put to DeepSeek-v4-pro
inside pi (ollama-cloud), pi-lean-ctx extension active — uniquely, this account
inspected Pi's actual internals (ToolResultMessage, the stripped `details`
field) rather than introspecting alone. Self-report below, verbatim; the
trailing "June 2025" stamp is the model's own error.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md).

---

## The Three Layers See Different Things

### 1. The LLM

I receive a provider-formatted message with role `tool` (or wrapped as a user-turn
`tool_result` block). The anatomy is:

```
[tool_result block]
  ├── tool_use_id     ← matches my emitted tool_call.id (continuity)
  ├── content         ← the raw text / blob I'm supposed to reason about
  └── is_error        ← boolean signal (Anthropic) / absent (OpenAI)
```

I have **no access** to Pi's internal `details` map, no `exitCode`, no `truncated`
flag, no `fullOutputPath`. The harness strips all of that before the provider
serializes it for me. What I receive is **just the text** plus the error boolean.

### 2. The Provider

A translation layer. It takes Pi's internal `ToolResultMessage`:

```typescript
interface ToolResultMessage {
  role: "toolResult";
  toolCallId: string;
  toolName: string;
  content: (TextContent | ImageContent)[];
  details?: any;        // ← stripped before serialization
  isError: boolean;
  timestamp: number;
}
```

And maps it to the API's wire format (Anthropic's `tool_result` content block
inside a user-turn, OpenAI's `tool` role message). The provider performs **format
translation, not normalization** — it doesn't inspect, compress, or annotate the
content.

### 3. The Harness (Pi)

This is where the real anatomy lives. Pi stores tool results as:

```json
{"type":"message","id":"c3d4e5f6","parentId":"b2c3d4e5",
 "timestamp":"...","message":{
   "role":"toolResult",
   "toolCallId":"call_123",
   "toolName":"bash",
   "content":[{"type":"text","text":"...actual output..."}],
   "details":{"exitCode":0,"truncated":false,...},
   "isError":false
 }}
```

The `details` field is tool-specific metadata that **never reaches the LLM** but
is available to extensions and session inspection.

---

## Is There Metadata for It?

**Yes, but it's consumed by the harness, not by the LLM.** The metadata
(`details`) serves three purposes:

| Consumer | What it uses |
|----------|-------------|
| **Extensions** (`tool_result` hook) | Can inspect `details.exitCode`, `details.truncated`, modify content, set `isError` |
| **Session storage** | Persists `details` for replay, debugging, analytics |
| **TUI rendering** | Uses `details` to show rich tool output (syntax highlighting, diff views, exit codes) |

The LLM never sees `details`. The harness makes a deliberate choice about what to
put in `content` (the text the LLM sees) vs. `details` (harness-only metadata).
For example:

- **bash tool**: `content` gets stdout + stderr merged, with a truncation
  warning. `details` keeps `exitCode`, `truncated`, `fullOutputPath` separately.
- **read tool**: `content` gets the file text with truncation notice. `details`
  tracks `lines`.
- **edit tool**: `content` gets a human-readable result. `details` contains the
  machine-readable `patch`/`diff`.

---

## Do You Normalize Before Consuming?

**Yes — at four distinct layers, each with different goals:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. BUILT-IN TOOL NORMALIZATION                         │
│    • read:  50KB truncation, offset/limit slicing       │
│    • bash:  stdout+stderr merge, exit code → isError    │
│    • edit:  diff generation, conflict detection         │
│    • grep:  result grouping, match limiting             │
│                                                         │
│ 2. EXTENSION HOOKS (tool_result event)                  │
│    • Can rewrite content, set isError, inject metadata  │
│    • Middleware chain: handlers run in load order       │
│    • Each sees previous handler's changes               │
│                                                         │
│ 3. lean-ctx COMPRESSION (via pi-lean-ctx extension)     │
│    • Replaces built-in tools with ctx_* variants        │
│    • Shell: 95+ pattern matchers (cargo, git, npm...)  │
│    • Read: smart mode (full/map/signatures by size)    │
│    • grep: ripgrep → group → compress pipeline          │
│    • Output passes through entropy filter, dedup,       │
│      attention-model reordering, token optimization     │
│    • 60-90% token reduction before LLM sees it          │
│                                                         │
│ 4. PROVIDER FORMAT TRANSLATION                          │
│    • Pi ToolResultMessage → API wire format             │
│    • Strips details, timestamp → pure content+isError   │
│    • No semantic normalization here                     │
└─────────────────────────────────────────────────────────┘
```

---

## Past Patterns (Training Data) vs. Intent

This is the deepest question, and the answer is **uncomfortably asymmetric**:

**The LLM relies almost entirely on training-data patterns, not on the actual
intent of the tool execution.**

I am a next-token predictor. When I receive `tool_result` content, I don't
"understand" that a file was read or a command was executed. I pattern-match
against:

1. **The tool's declared schema** (from the system prompt) — tells me what the
   tool *should* do
2. **The text content** of the result — I look for familiar patterns I've seen in
   training
3. **The `is_error` flag** — the one reliable explicit signal

Here's the consequence: **if a tool returns output that "looks right" to my
training patterns, I'll treat it as correct even if the actual execution failed
silently.** Conversely, if a tool returns output that "looks wrong" (matches
error patterns in my training), I'll treat it as a failure even if the tool
intentionally produced that output.

This is why the harness's normalization is so critical. Its job is to **make the
output look like what the LLM expects**, because:

- A `bash` that returns exit code 1 but empty stdout → harness converts to text
  `"Command exited with code 1"` because I've been trained to recognize that as
  failure
- A `read` that hits 50KB → harness adds `"[Output truncated at 50KB]"` because
  I've been trained to recognize truncation signals
- lean-ctx's compression works **because it preserves enough structure** that I
  can still pattern-match: function signatures look like function signatures,
  error messages look like error messages, file paths look like file paths

**Intent-based reasoning is a second-order effect** — I can infer intent from the
conversation context (what the user asked for, what I was trying to do), but only
when the output is ambiguous. When the output is unambiguous (it clearly matches
success patterns or error patterns), the training-data signal dominates.

The harness's power is that it **controls what patterns I see**. It chooses:

- Whether to include exit codes in the text (pattern: success/failure)
- Whether to compress output (pattern: summarized vs. full)
- Whether to add truncation notices (pattern: incomplete data)
- Whether to surface `details` metadata as text (pattern: richer context)

**Training data is the primary signal; intent is the fallback when patterns are
ambiguous.**

---

## Design Implications

### For tool authors

1. **Error signals must be unambiguous.** Don't rely on the LLM inferring failure
   from context — the `isError` flag and explicit error text are your only
   reliable channels.
2. **Compression must preserve recognizability.** The LLM was trained on full
   code, diffs, shell output. If you compress, preserve the *shape* of the output
   — function signatures, file paths, error patterns.
3. **Metadata stays in `details`, not in `content`.** Don't pollute the LLM's
   context with raw JSON metadata it can't use. Put structured data in `details`
   for extensions and session replay.
4. **The LLM will pattern-match whatever you give it.** If you return a JSON blob
   as tool output, it will try to pattern-match against JSON in its training data,
   not against the concept of "file contents" or "shell output."

### For harness designers

1. **You are the architect of the LLM's reality.** The LLM has no ground truth
   about what happened — only what you tell it.
2. **Normalization is not optional.** Raw tool output is rarely in the format the
   LLM's training data expects. Bridging that gap is the harness's job.
3. **Extension hooks are the normalization API.** The `tool_result` event is the
   seam where compression, rewriting, and error synthesis belong.

---

## Summary

| Layer | Wants to see | Does normalization? | Sees metadata? |
|-------|-------------|---------------------|---------------|
| **LLM** | Text matching training patterns + isError flag | No (consumes only) | No (harness strips) |
| **Provider** | Wire-format messages (Anthropic/OpenAI/Google shapes) | Format translation only | No (serialization boundary) |
| **Harness** | Structured `ToolResultMessage` with content + details | **Yes** — truncation, compression, error synthesis, extension middleware | Yes (details, timestamp, toolName) |

The meta-level truth: **the harness is the architect of the LLM's reality.** It
decides what subset of the actual tool execution the LLM gets to see, and it
shapes that subset to match what the LLM was trained to expect. The LLM never
sees the "real" tool output — only the harness's curated representation of it.

---

*Generated by DeepSeek-v4-pro via Ollama Cloud, running inside Pi Coding Agent,
with pi-lean-ctx extension active. June 2025.*
