# 08 — forge_compress: the harness's own compressor (mined 2026-06-09)

A metric we never looked at until the SQLite store made it queryable: forge records its
**own** compression on every store/artifact/query call, inline in each tool result under
`details.compression`. Standard format, two variants:

- forge tools (`forge_store`/`forge_artifact`/`forge_store_query`): `{tool, before, after, saved}`
- lean-ctx tools (`ctx_*`): `{originalTokens, compressedTokens, percentSaved}`

Both are captured in `tool_results` (`comp_source`, `comp_before`, `comp_after`,
`comp_saved_pct`). Numbers below are from `db/tokbench.db`, `class='matrix'` (14 runs).

## Headline

**forge compresses its store I/O 72% per call.** Across the matrix, 406 forge store/artifact/
query calls: **335,313 → 93,252 tokens, saving 242,061 (72.2%)** — entered-once, before
re-carriage. And it runs in **every arm, including native** — it's a harness constant.

| forge tool | calls | before | after | saved % |
|---|--:|--:|--:|--:|
| `store:read` | 147 | 130,614 | 25,489 | **80.5%** |
| `query` | 17 | 7,220 | 1,863 | 74.2% |
| `artifact:read` | 230 | 193,755 | 64,460 | 66.7% |
| `store:list` | 12 | 3,724 | 1,440 | 61.3% |

## It's a harness constant (arm-independent)

| arm | runs | forge_compress saved | per run | avg % |
|---|--:|--:|--:|--:|
| a0 native | 5 | 86,680 | 17,336 | 67.4% |
| a1m lean-ctx | 3 | 48,360 | 16,120 | 71.9% |
| a2 headroom | 3 | 47,983 | 15,994 | 65.9% |
| a3 rtk | 3 | 59,038 | 19,679 | 74.3% |

~16–20K saved/run regardless of which middleware is loaded. The native baseline already
gets this compression; it is not something a middleware adds.

## The thesis, with numbers: the harness out-compresses the middleware

Measured the **same way** (the `details.compression` metric), in the same a1m runs:

| run | forge_compress saved | lean-ctx (`ctx_*`) saved | ratio |
|---|--:|--:|--:|
| R02 | 15,666 | 12,161 | 1.3× |
| R07 | 12,901 | 4,436 | 2.9× |
| R12 | 19,793 | 4,413 | 4.5× |

**forge's own compressor out-saved lean-ctx ~2.3× per run** — and it did so on the *exact*
surface (`forge_*` MCP store tools) that lean-ctx structurally cannot reach (`ctx_*` can't
wrap another server's MCP tools — verified 0% store routing in a1f, see note 07). Across the
whole matrix: forge_compress **242,061** saved vs lean-ctx **21,010**. The middleware finds
almost nothing left to compress because **the harness already compressed the biggest chunk 72%.**

This is "the governor belongs in the harness" (Part 8) as a measured fact, not an argument.

## By phase

Artifact/store-heavy phases save most: approve 70,810 · review-code 50,394 · validate 31,149 ·
review-plan 29,429 · commit 27,081. writeback compresses least (39%) — it writes more than reads.

## Why it matters more than the raw 242K suggests (re-carriage)

These are **entered-once** savings. Because compressed content is re-carried every turn, the
bill impact is a multiple of 242K — the same re-carriage that *taxed* lean-ctx (+3K/turn ×
turns) works in forge's *favor*: compress the store payload once, save it on every subsequent
turn. Without forge_compress, the store content entering context would be ~3.6× larger
(335K vs 93K) and re-billed every turn — the native baseline would be dramatically heavier.
**This is a primary reason the native bill is already lean and the middleware has little surface.**

It also refines the earlier "store JSON is noise" point (note 07 / the dashboard discussion):
forge has *already* removed ~72% of that JSON noise. The residual ~93K that still enters is
the remaining lever — real, but much smaller than the gross store I/O implied.

## Integrity / caveats (symmetric meter scrutiny — Part 7)

- **The "after" is verified, the "before" is forge's claim.** forge's reported `after` matches
  the content that actually entered context (ratio 1.02–1.17 across tools) — so the compressed
  output is real. But `before` (what forge says it *would* have sent uncompressed) is forge's
  self-reported counterfactual — the **same epistemic status as lean-ctx's dashboard** we put on
  trial. We credit forge's meter and scrutinize it on the same terms: the 93K it *sent* is
  measured; the 72% it *avoided* is forge's number.
- forge_compress covers only `forge_*` MCP tools. Native `read`/`bash` output is **un**compressed
  (the gap a read-compressor or denser-format return would fill — note 07 lever).
- Entered-once metric; the re-carriage multiplier is real but not precisely computed here.

## Series mapping

- **Part 4 (forge-compress: boring heuristics beat clever architecture)** — this is the data:
  a plain "compress the store JSON 72%" heuristic does the heavy lifting, out-saving three
  funded middleware products on the surface they can't reach.
- **Parts 5 / 8 (governor in the harness)** — measured proof the harness is the compressor.
- **Part 7 (who audits the meter)** — we audit forge's meter on the same terms as the vendors'.
