# Task Prompt — CART-S03-T01

## Title

Implement `carto rm` command to delete a node

## Objective

Add a `rm <title>` sub-command to `carto` that removes the named node and all edges referencing it from the knowledge graph, then persists the change. This fills a basic CRUD gap — users can currently `add` and `link` nodes but cannot remove them.

## Acceptance Criteria

1. Running `carto rm "Some Node"` removes the node and all edges where the node appears as `from` or `to`, then saves the graph.
2. Prints `✓ Removed "Some Node" and N edge(s)` in `chalk.green` (N is the count of removed edges; if 0, print `and 0 edges`).
3. If the node title does not exist, prints `✗ Node not found: "Some Node"` in `chalk.red` to `console.error` and exits with code 1.
4. `npm run build` compiles cleanly with no TypeScript errors.
5. `npm test` passes (vitest); new behaviour is covered by tests.
6. `npm run lint` reports no new violations.
7. ESM conventions are respected — relative imports use explicit `.js` extensions.
8. `graph.ts` changes remain pure functions (no singleton state, no classes); all I/O side-effects stay in `cli.ts`.

## Context

- The existing `addNode()` and `link()` pure functions in `src/store/graph.ts` follow the load → mutate → save pattern. `removeNode()` should follow the same pattern.
- Node lookup is by `title` (case-sensitive) — consistent with `link()`.
- The existing `list` command in `cli.ts` provides a formatting reference for node output.

- Related task(s): CART-S03-T02 (ls command — independent, no shared files outside `types.ts`)
- Related bug(s): none

## Entities

- [x] **Graph** — root container (`nodes: Node[]`, `edges: Edge[]`), persisted at `~/.cartographer/graph.json`
- [x] **Node** — concept/idea (`id`, `title`, `body`, `tags`, `createdAt`, `updatedAt`); lookup by `title` (case-sensitive)
- [x] **Edge** — directed relationship (`from`, `to`, `label?`, `weight`); cascading delete when either endpoint is removed

## Data Model Changes

None — the existing `Graph`, `Node`, and `Edge` shapes in `types.ts` are sufficient. The `removeNode` function filters `nodes` and `edges` arrays in memory before calling `save()`.

## CLI Changes

New sub-command in `src/cli.ts`:

```ts
program
  .command("rm <title>")
  .description("Remove a node and its edges from the map")
  .action((title: string) => { /* call removeNode, print result */ });
```

- Success: `console.log(chalk.green(`✓ Removed "${title}" and ${edgeCount} edge(s)`))`
- Not found: `console.error(chalk.red(`✗ Node not found: "${title}"`))`, `process.exit(1)`

## Operational Impact

- **Graph file compatibility:** No format change — removal simply deletes entries from the existing `nodes` and `edges` arrays.
- **Backwards compatibility:** No existing commands change behaviour.
- **Offline-only design:** Unaffected — no network or external dependency introduced.