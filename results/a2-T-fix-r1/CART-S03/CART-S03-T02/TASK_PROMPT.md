# Task Prompt — CART-S03-T02

## Title

Implement `carto ls` command to list all nodes

## Objective

Add an `ls` sub-command to `carto` that prints every node title (one per line) in `chalk.cyan`. Shows `No nodes yet.` in `chalk.yellow` if the graph is empty. This provides quick visibility into the knowledge graph from the terminal.

## Acceptance Criteria

1. Running `carto ls` prints all node titles, one per line, in `chalk.cyan`.
2. If the graph has no nodes, prints `No nodes yet.` in `chalk.yellow`.
3. `npm run build` compiles cleanly with no TypeScript errors.
4. `npm test` passes (vitest); new behaviour is covered by tests.
5. `npm run lint` reports no new violations.
6. ESM conventions are respected — relative imports use explicit `.js` extensions.
7. `graph.ts` changes remain pure functions (no singleton state, no classes); all I/O side-effects stay in `cli.ts`.

## Context

- A `list` command already exists in `src/cli.ts` that prints node titles with IDs and tags. The new `ls` command is a simpler, focused variant that prints just titles — one per line, no extra metadata. Where `list` shows `Title [id8] #tag1`, `ls` shows just `Title`.
- The `listNodes()` pure function in `graph.ts` should return the array of titles (or formatted strings) for the `ls` command to consume.
- After T01 (`rm`) lands, `ls` can be used to verify node removal manually.

- Related task(s): CART-S03-T01 (rm command — independent)
- Related bug(s): none

## Entities

- [x] **Graph** — root container (`nodes: Node[]`, `edges: Edge[]`), persisted at `~/.cartographer/graph.json`
- [x] **Node** — concept/idea (`id`, `title`, `body`, `tags`, `createdAt`, `updatedAt`); `ls` reads only `title`

## Data Model Changes

None — read-only operation on the existing `Graph` shape.

## CLI Changes

New sub-command in `src/cli.ts`:

```ts
program
  .command("ls")
  .description("List all node titles")
  .action(() => { /* load graph, call listNodes, print */ });
```

- Populated graph: `console.log(chalk.cyan(title))` for each node title
- Empty graph: `console.log(chalk.yellow("No nodes yet."))`

Note: the existing `list` command remains unchanged — `ls` is a separate, simpler listing.

## Operational Impact

- **Graph file compatibility:** None — read-only, no mutation.
- **Backwards compatibility:** No existing commands change behaviour.
- **Offline-only design:** Unaffected — no network or external dependency introduced.