# 09 — Vendor right-of-reply (verbatim, for the writeup)

Per protocol §(right-of-reply): each maintainer was given the full results before publication
and their responses are quoted verbatim. Status as of 2026-06-09.

| Vendor | Issue | Responded? |
|---|---|---|
| lean-ctx (yvgude) | [#361](https://github.com/yvgude/lean-ctx/issues/361) | **YES — substantive, 2026-06-09; confirmed + shipped fixes** |
| rtk | [#2292](https://github.com/rtk-ai/rtk/issues/2292) | No human response (automated `wshm` triage only) |
| headroom | [#645](https://github.com/chopratejas/headroom/issues/645) | No response (0 comments) |

---

## lean-ctx — yvgude (OWNER), 2026-06-09

**Confirmed our read outright** ("on a phase-isolated harness running on a non-caching provider,
lean-ctx's tool layer cannot net-help, and our own dashboard overstated the net effect …
devasur's decomposition is correct") and **shipped changes to `main` in response:**

- `rules_injection = "off"` (new) — write no rules file, for hosts that supply their own workflow.
- `LEAN_CTX_MINIMAL=1` — trims the exposed `ctx_*` tool surface to a core set (+ a persona to slim further).
- `gain` dashboard now states its **Methodology** ("savings = compression on lean-ctx-touched
  traffic, not your full provider bill") and `gain --json` carries `injected_overhead_tokens_per_turn`,
  so net impact ≈ `tokens_saved − injected_overhead_per_turn × turns`. **Directly fixes the
  meter-overstatement we flagged** (the "25.4% on ~29.5K vs a 3.58M bill" gap).
- Documented the **proxy** (`lean-ctx proxy enable`) as the way to reach tool output the `ctx_*`
  tools can't wrap (incl. forge's `forge_*` store output) — wire-layer, file/source reads protected
  from lossy compression. Caveat: it shrinks what's *sent*, can't un-bill a re-sent fixed prefix.
- Persona `default_read_mode = "map"`/`"signatures"` documented as the **cold-read lever** for
  phase-isolated harnesses (the only lever with surface there; persistent cache would NOT help —
  the ~13-token stub is a same-context back-reference a fresh phase agent can't resolve).
- Confirmed per-process cache is intended; confirmed **our integration is faithful**.

### Quotable statement (verbatim, author-provided for the writeup)

> lean-ctx's savings come from cold-read compression and cached re-reads. On a long-lived context,
> and especially on cache-priced providers — where both the cached re-reads and the injected prefix
> ride the provider cache — it nets ahead. On a phase-isolated harness (fresh context per phase) on
> a non-caching, request-metered provider, the cached-re-read lever has no surface and the injected
> prefix is re-billed every turn, so it can cost tokens; its addressable share there is a few percent.
> devasur's decomposition is correct. In response we made the meter state its denominator and the
> per-turn overhead it injects, added `rules_injection = off` and a minimal surface for hosts that
> bring their own workflow, and documented the proxy as the way to reach tool output the `ctx_*`
> tools can't wrap.

### Re-run invitation (before June 17)

Build lean-ctx from `main`, then either (a) `lean-ctx proxy enable` in front of the ollama-cloud
endpoint (tests the store-output / wire path) or (b) `rules_injection = "off"` + `LEAN_CTX_MINIMAL=1`
(tests the no-injection floor). **Decision pending** — this is a NEW lean-ctx version, so any such run
is **exploratory** (outside the frozen 14-run matrix), like a1f. See "open decision" below.

### Significance for the writeup

- Second fast, substantive turnaround from this maintainer (after the #361 → 3.7.5 fix in ~7h).
- **Part 7 ("who audits the meter"):** the benchmark *caused* the vendor's meter to become honest
  (state its denominator + the overhead it injects). That's the strongest possible version of the
  meter-accountability beat — not "the meter lies," but "we showed it overstated and it was fixed."
- The proxy answer means lean-ctx is **not only tool-layer** — it has a wire-layer option that
  overlaps headroom's approach and *can* reach the store. The "store structurally unreachable"
  finding holds for the **tool layer**; state that precisely.

---

## Open decision (carry to Boni)

The frozen 14-run matrix stays as-is (held-constant: lean-ctx 3.7.5 stock, forge-cli 1.0.21). The
maintainer's suggested config is a **new lean-ctx build** → any run is **exploratory**, not matrix.
Option: one labeled exploratory run on the vendor-recommended config before the 17th (proxy, or
no-injection floor) to report "we tested the fix." Requires rebuilding the a1m arm image. Quota/time
call.

## rtk / headroom

No response yet. Right-of-reply results comments still to be posted before the 17th (drafts pending).
