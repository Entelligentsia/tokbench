# Task Prompt — `CART-S02-T03`

> **Nice-to-have.** Attempt only if the must-have tasks (CART-S02-T01 and
> CART-S02-T02) are complete and green.

## Title

Extend `carto stats` to also print the most-connected node title.

## Objective

Give the user a quick sense of their graph's "hub" — alongside the counts,
`carto stats` also names the node with the highest edge degree.

## Acceptance Criteria

1. A new **pure**, named export in `src/store/graph.ts` computes node degree from
   `graph.edges`, counting both `from` and `to` incidences per node, and returns
   the highest-degree node (or a defined sentinel — `null` — when there are no
   edges). No `console`, no `load`/`save`, no other I/O.
2. Node id → title resolution uses `graph.nodes`; the helper returns enough to let
   `cli.ts` print the node `title`.
3. Ties are broken deterministically (first-encountered wins); this behaviour is
   covered by a unit test.
4. The empty-graph / no-edges case returns the sentinel and `carto stats` omits or
   gracefully handles the most-connected line (no crash, no `undefined` printed).
5. The `stats` action in `src/cli.ts` is extended to print the most-connected node
   title in addition to the existing counts line. No new flags or options.
6. vitest unit tests cover degree counting, tie-break, and the empty-graph sentinel,
   importing the helper from `../store/graph.js`.
7. `npm run build` compiles cleanly; `npm test` passes; `npm run lint` reports no
   new violations. Pure helper stays in `graph.ts`; all formatting/printing stays
   in `cli.ts`; ESM `.js` import extensions respected.

## Context

Optional third task of CART-S02; gated behind the two must-haves. Preserves the
same pure/I-O seam as T01/T02: the degree computation is a pure helper in
`graph.ts`, the printing is in `cli.ts`. Watch the edge cases — ties, empty graph,
and id→title resolution are the only real complexity here.

- Related task(s): depends on `CART-S02-T02`
- Related bug(s): none

## Entities

- [x] **Graph** — read-only input to the degree helper
- [x] **Node** — title resolved from `id` for the most-connected result
- [x] **Edge** — degree computed from `from` / `to` references

## Data Model Changes

None. No change to `types.ts` or to the `graph.json` serialisation.

## CLI Changes

Extends the existing `carto stats` action with one additional output line naming
the most-connected node title. No new subcommand, no new flags. The line is
omitted (or shown as a defined empty state) when the graph has no edges.

## Operational Impact

Read-only over the graph — no data-corruption exposure. cli-ux surface: the extra
line must handle ties and the empty graph gracefully. Offline-only design holds —
no database or network dependency. No change to the on-disk `graph.json` format.
