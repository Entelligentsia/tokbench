# Task Prompt — `CART-S02-T02`

## Title

Add a read-only `carto stats` command to `src/cli.ts`.

## Objective

Let a user run `carto stats` and immediately see how big their graph is — the
node and edge counts — in one readable, correctly pluralised line.

## Acceptance Criteria

1. A `stats` command is registered in `src/cli.ts` via the existing `commander`
   `.command("stats").description(...).action(...)` pattern, modelled on the
   read-only `list` command.
2. The action loads the graph via `load()` and derives counts via
   `graphStats(graph)` (imported from `./store/graph.js`) — it does **not**
   recompute `.length` inline.
3. For a graph with 2 nodes and 1 edge, the command prints exactly
   `2 nodes, 1 edge` via `console.log`.
4. Pluralisation is handled independently for both counts (e.g. `1 node, 0 edges`;
   `0 nodes, 0 edges`) — singular only when the count is exactly 1.
5. The command is **read-only**: no `save()` call, no mutation of the graph. No
   new flags or options are added.
6. Success output uses `chalk` per project convention (`chalk.green`/`chalk.cyan`).
7. `npm run build` compiles cleanly; `npm test` passes; `npm run lint` reports no
   new violations. ESM `.js` import extensions respected. All I/O stays in `cli.ts`;
   `graph.ts` is not given any side effects.

## Context

Second task of CART-S02; depends on the `graphStats` helper from CART-S02-T01.
This task owns the I/O and presentation layer — including the pluralisation logic,
which must not leak back into `graph.ts`. Two independent singular/plural ternaries
are sufficient.

- Related task(s): depends on `CART-S02-T01`; precedes `CART-S02-T03`
- Related bug(s): none

## Entities

- [x] **Graph** — loaded via `load()` and passed to `graphStats`
- [x] **Node** — count reported in output
- [x] **Edge** — count reported in output

## Data Model Changes

None. No change to `types.ts` or to the `graph.json` serialisation.

## CLI Changes

New read-only `carto stats` subcommand — one `.command()` block in `cli.ts`. No
arguments, no flags. Output: a single `console.log` line of the form
`<n> node(s), <m> edge(s)` with `chalk` colour for success. No error path beyond
the existing `load()` behaviour (an empty graph prints `0 nodes, 0 edges`).

## Operational Impact

cli-ux is the primary surface: pluralisation must be correct. No data-corruption
exposure (read-only, no `save()`). Offline-only design holds — no database or
network dependency. No change to the on-disk `graph.json` format or backward
compatibility.
