# 07 — Can it be fixed? Source-grounded levers (forge side & product side)

Written 2026-06-09, after the 14-run matrix closed. Driving question: the bill says
no product nets a token reduction on forge-cli/ollama — but *why*, in the code, and
what concrete change (forge-side or product-side) would change that? Grounded in a
parallel read of all four source trees (`../lean-ctx`, `../rtk`, `../headroom`,
`~/src/forge-cli`). Every claim cites `file:line`. Companion to standing-conclusions
1–8 in [../results/INDEX.md](../results/INDEX.md).

## TL;DR

- **forge can capture each product's *philosophy* natively, and mostly already has.**
  rtk's philosophy (command→recipe rewriting) *is* forge's identity. lean-ctx's
  (compressed reads) is half-captured (store reads yes, source-code reads no) — but the
  AST-free win there is *format* (drop JSON noise), not a code parser. headroom's (wire
  compression) is unbuilt and low-yield. The biggest dollar lever — prompt caching — is
  **already captured**: forge caches diligently on cache-priced rails (verified, §Q1c).
- **The products mostly can't help a forge-cli user much** — rtk is architecturally
  capped at a ~2.5% surface; lean-ctx can only help via cold-read modes (which forge
  could do itself without paying the injected-rule tax); **headroom is the one product
  worth integrating**, ideally as an embedded library, not the proxy.
- **Two corrections to our priors** (see end): (1) headroom does NOT break prompt
  caching — it is engineered to protect it; (2) forge's and headroom's biggest lever
  are the *same* one (prompt caching), and the request-metered rail made it
  structurally invisible.

## Framing fact: forge's "governor" is design vocabulary, not code

There is no runtime context-governor object and no `forge-compress` library in
`~/src/forge-cli`. forge governs context **upfront by construction**:

- **Phase isolation** — each of the 8 phases is a fresh process (`runAgents` →
  `pi.runAgent`, sequential; `packages/forge-core/src/orchestrator/sub-agent.ts:33`).
- **Projected store reads** — `store-query` returns id/title/status/relationships/
  fileRefs only, not full JSON (`tools/lib/store-query-exec.cjs:30`); INDEX.md clamped
  to a 4-sentence excerpt (`tools/lib/store-facade.cjs:86`); context-pack hard-capped
  at 400 lines (`tools/build-context-pack.cjs:24`); project context truncated to 12k
  chars (`orchestrator/runner.ts:236`).
- The only **runtime interception** surface is Claude Code hooks
  (`packages/forge-core-assets/hooks/hooks.json`). Critically, **PostToolUse hooks only
  log/triage — none rewrite the tool result — and there is no PostToolUse hook on
  `Read`/`Grep` at all.** That gap is where most of the forge-side answer lives.

This squares with the benchmark's "~74% governed away": isolation + projection + clamps
remove most context *before the model sees it*, which is exactly why only ~26% remains
addressable by any downstream middleware.

---

## Q1 — Can forge capture each philosophy without butchering its identity?

Identity to preserve: phase isolation · artifact handoffs · governed/audited state
tools · phase/persona-aware policy · cache-respecting (prefix-stable) · open/pluggable ·
audit-trailed.

### (a) lean-ctx — tool-layer compressed reads → **half-captured; closing the gap is the real win**
- Already captured for forge's own state: projected store record + 4-sentence excerpt +
  "use store results directly, skip reading full index files"
  (`store-query-exec.cjs:30`, `store-facade.cjs:86`, `init/base-pack/workflows/plan_task.md:40`).
  This *is* lean-ctx's philosophy applied to the KB/store, default-on.
- **Not** captured for source code: workflows tell the agent to `Glob/Grep/Read`
  (`plan_task.md:46`) — plain Claude Code `Read`, full file, uncompressed.
- **The obvious "fix" carries a real cost:** signatures/outline mode = a per-language
  parser/AST to build and maintain (this is exactly what lean-ctx owns). Given the
  benchmark's ~26% addressable surface and run-path variance ~10× the effect, **owning an
  AST for marginal read-compression is probably not worth it.** Downgraded.
- **The AST-free, identity-true lever is format, not parsing.** forge already returns
  *less* data from its store — but it returns it as **projected JSON, which is itself
  noise** (per `06-what-models-want.md`: models don't need to parse JSON; structural
  scaffolding is dead weight). forge controls this output format completely, so the real
  lean-ctx-philosophy win is **denser, non-JSON store/tool returns** (tabular / minimal
  prose) at `store-query-exec.cjs:30` — no parser, no AST, fully auditable, doesn't touch
  isolation or artifacts. **Verdict: the gap is real but the win is format, not code-AST.**

### (b) rtk — command-layer recipe rewriting → **already forge's core identity**
forge's whole asset layer is recipe-rewriting: deterministic CLIs (`store-cli`,
`build-context-pack`, `preflight-gate`) replace ad-hoc model exploration; workflows tell
the agent to run one `store-cli nlp` and skip manual MASTER_INDEX navigation
(`plan_task.md:36`, `architect_sprint_plan.md:30`). Extension point for *more* =
workflows under `init/base-pack/workflows/` + tools under `tools/`. **Verdict:
already-captured; remaining headroom marginal; load-bearing to forge identity.**

### (c) headroom — wire-layer compression → **capturable but low-yield; the cache version is the prize**
- In-process choke point exists at the provider boundary
  (`packages/forge-pi-adapter/src/claude-agent-sdk-runtime.ts:204`). A decorator
  `PiRuntime` could compress the volatile prompt tail there — but it works on the
  residual ~26% and must never touch the system-prompt prefix (cache-respect).
- **forge already captures the cache lever — VERIFIED in transcripts, 2026-06-09.** Prompt
  caching is ON: pi / the Claude Agent SDK enables it by default and forge adds cache
  boundary markers. Proof from a0c (forge on the Anthropic rail), plan phase usage:
  `{"input": 17, "output": 4835, "cacheRead": 179277, "cacheWrite": 19539}` — raw uncached
  input **17 tokens**, **179,277 cache reads**, with `cacheWrite`→growing-`cacheRead` every
  turn. (An earlier subagent read forge's TS, saw no explicit `cache_control` construction,
  and wrongly concluded "dead flag" — it diagnosed the wrong layer; caching is the
  runtime's default, not forge's to construct. Field names are pi's `cacheRead`/`cacheWrite`,
  not Anthropic's raw `cache_*_input_tokens`.)
- So wire compression is the only *un*captured headroom-style lever, and it's low-yield
  (residual ~26%, must not touch the cached prefix). **Verdict: cache lever already
  captured; wire-compression capturable but low-yield.**

**Q1 answer:** Yes — and the highest-value forge-native move is **denser (non-JSON)
store/tool returns**, not adopting any product (see (a) note on AST cost + JSON noise).
The cache lever — the biggest dollar lever — is **already captured** on cache-priced
rails. This is the Part-8 thesis confirmed: the governor belongs in the harness, and
forge already lives there.

---

## Q2 — Can each product change (code/config) to save forge-cli users tokens?

### lean-ctx — yes, modestly; one change makes its headline claim true
Cache is strictly in-process/in-RAM — `SessionCache` rebuilt empty every phase
(`lean-ctx/rust/src/tools/server_lifecycle.rs:116`); the ~13-token stub needs three
in-RAM pieces (`F#` label, `is_full_delivered`, the `CacheEntry`) that a fresh process
lacks (`src/tools/ctx_read/mod.rs:335`). No persistent/content-addressed read cache
exists (the md5 hash at `src/core/cache.rs:756` is RAM-only). Injected MANDATORY rules
cost ~0.5–1.5k tokens/phase fixed (`src/instructions.rs:11` cap 1200 + dedicated rule
file). Levers:
1. **(easy, no infra)** Bias `auto` to cold-compressed modes (`signatures`/`map`) for
   large code files — content-derived, so cheaper *even on a cold first read in a fresh
   process* (`src/tools/ctx_read/render.rs:103`). The only lean-ctx saving that survives
   phase isolation. Today `auto` falls back to `full` too often (`core/auto_mode_resolver.rs`).
2. **(principled)** Add a content-addressed disk cache so stubs survive process
   boundaries; load it in `SessionCache::new()` instead of starting empty; emit a
   self-contained back-reference (path+hash), not the in-RAM `F#`. The single change that
   makes "re-read = 13 tokens" true on a phase-isolated harness.
3. **(easy)** Make the rule-file injection optional when the host supplies its own
   workflow (already branches on `client_name`, `server_handler.rs:216`). Kills the
   fixed overhead behind the +38%.

### rtk — structurally capped; levers real but can't reach forge's spend
A `PreToolUse:Bash` command rewriter with a **compiled-in** recipe table
(`rtk/src/discover/rules.rs:13`); dispatch at `registry.rs:148`. It only ever sees
`tool_input.command` — **no PostToolUse, no tool-output handler anywhere** — so it cannot
touch `Read` output or structured-store responses (they aren't Bash commands). That's the
whole reason its surface was ~1–2.5%. Levers:
1. Ship static recipes for the exact shell commands forge agents run (`rules.rs:13`) —
   raises the ceiling on a tiny surface.
2. Wire the hook to consult the user-TOML registry (`core/toml_filter.rs:188`, currently
   a disjoint code path) so forge commands register without a recompile.
3. The only lever reaching the real tokens — a PostToolUse output-compactor — **breaks
   rtk's command-layer philosophy entirely** (it's a different product). rtk's design
   forecloses it. **Honest verdict: rtk did exactly what it's built to do; its ceiling is
   architectural, not a bug.**

### headroom — yes, the most; the one product worth integrating
Genuinely compresses (only verified on-wire saving, std-conclusion 2). Compressors are a
clean library crate with zero server coupling (`headroom/crates/headroom-core/`), already
embeddable in-process (PyO3 binding `crates/headroom-py/src/lib.rs:21`). Levers:
1. **(trivial, highest value)** Add a streaming idle/read timeout. The 305s hang's root
   cause: only guard is a 600s end-to-end ceiling (`crates/headroom-proxy/src/config.rs:202`),
   no idle timeout — a provider that stalls mid-stream hangs the whole pipeline
   (`proxy.rs:889`, single `.send().await`, no retry/circuit-breaker).
2. **(high feasibility, no headroom code change)** Embed `headroom-core` in-process —
   kills the proxy hop, the latency, and the hang risk. The PyO3 binding proves it works.
3. **(moderate)** Expose compressor aggressiveness as config — today hardcoded
   `*Config::default()` behind a `OnceLock` (`crates/headroom-core/src/transforms/live_zone.rs:532`);
   the per-auth-mode `max_lossy_ratio` is plumbed-but-dead (`compression_policy.rs:166`).
   Tool output is CCR-recoverable, so a forge user could safely push harder.
4. **(moderate)** Wire the not-yet-shipped lossless paths (Kompress prose, json_minifier)
   into the live-zone dispatcher (`live_zone.rs:1366`, currently no-ops) — free, cache-safe.
5. **(biggest untested upside)** The cache-stabilization suite
   (`crates/headroom-proxy/src/cache_stabilization/`) — on a cache-priced rail, the
   dominant dollar lever; our ollama-cloud rail made it structurally invisible.

---

## Two corrections to our priors (fold into the writeup)

1. **headroom does NOT break prompt caching — it is engineered to protect it.** The worry
   "a wire compressor mutates early tokens and torches the cache" is false for headroom
   specifically: it computes a frozen prefix from `cache_control` markers and never
   touches it (`crates/headroom-core/src/cache_control.rs:11`), splices compressed blocks
   via byte-range surgery so the prefix is byte-identical (`live_zone.rs:64`), and
   disables the historic cache-destabilizing aligner for subscription users
   (`compression_policy.rs:44`). Its risk on a priced rail is *under*-compressing, not
   cache-busting. Honest "I checked and was wrong" beat for Part 3.

2. **forge's and headroom's biggest lever is the same one — prompt caching — and the
   benchmark rail couldn't price it.** forge **already caches diligently** on cache-priced
   rails (a0c plan phase: 17 raw input vs 179,277 cacheRead; pi default + forge's boundary
   markers — VERIFIED, corrects an earlier wrong "dead flag" claim). headroom has a whole
   cache-stabilization suite ollama can't trigger. The benchmark ran on request-metered
   ollama-cloud where caching isn't priced, so this (already-working) win was **invisible
   by rail choice, not absent**. This *reinforces* the thesis: the request-metered rail
   measured the token-count game (where the harness already wins); the dollar game is
   played at the cache layer — which forge already exploits and middleware mostly can't
   add to.

## How this maps to the series

- Q2 (product-side levers) → Part 3 "what each maintainer could do" / right-of-reply.
- Correction 1 → Part 3 honest-correction beat (headroom & caching).
- Q1 (forge captures the philosophies natively) + correction 2 → Parts 5, 7, 8
  (governor-in-the-harness; forge already caches diligently on cache-priced rails — the
  benchmark rail just didn't price it).
