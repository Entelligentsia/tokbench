# Task Prompt — `CART-S02-T01`

## Title

Add a pure `graphStats(graph)` helper to `src/store/graph.ts` with unit tests.

## Objective

Give `cartographer` a single, pure way to count what is in the graph, so the
forthcoming `carto stats` command (CART-S02-T02) can report node and edge totals
without duplicating length logic or doing any I/O in the wrong layer.

## Acceptance Criteria

1. `graphStats` is a **named export** from `src/store/graph.ts` with signature
   `graphStats(graph: Graph): { nodes: number; edges: number }`.
2. It returns `{ nodes: graph.nodes.length, edges: graph.edges.length }` — `nodes`
   strictly equals `graph.nodes.length`, `edges` strictly equals `graph.edges.length`.
3. The function is pure: no `console`, no `load`/`save`, no other I/O or side
   effects; it operates solely on its `graph` argument.
4. A vitest case asserts `graphStats` returns `{ nodes: 2, edges: 1 }` for a graph
   built with 2 nodes and 1 edge, and `{ nodes: 0, edges: 0 }` for `{ nodes: [], edges: [] }`.
5. `npm run build` compiles cleanly with no TypeScript errors.
6. `npm test` passes (vitest); the new cases are included. `npm run lint` reports
   no new violations.
7. ESM conventions respected — the test imports `graphStats` from `../store/graph.js`
   (explicit `.js` extension). `graph.ts` changes stay pure functions; no class,
   no singleton state, no module-level side effects.

## Context

First task of CART-S02 and the root of the dependency graph. The pure/I-O seam is
the organising principle: counting lives in `graph.ts`, presentation will live in
`cli.ts` (CART-S02-T02). Keep `graphStats` count-only so pluralisation never leaks
into the pure layer.

- Related task(s): blocks `CART-S02-T02`; foundation for `CART-S02-T03`
- Related bug(s): none

## Entities

- [x] **Graph** — root container (`nodes: Node[]`, `edges: Edge[]`); read-only input to `graphStats`
- [x] **Node** — counted via `graph.nodes.length`
- [x] **Edge** — counted via `graph.edges.length`

## Data Model Changes

None. No change to the `Graph` / `Node` / `Edge` shapes in `types.ts` and no
change to the JSON serialisation. No migration needed.

## CLI Changes

None in this task — the `stats` command is added in CART-S02-T02.

## Operational Impact

None. `graphStats` is pure and read-only; offline-only design holds (no database
or network dependency). No impact on the on-disk `graph.json` format or backward
compatibility.
