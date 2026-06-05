# Sprint CART-S03 — Workflow Test: `rm` and `ls` Commands

## Goal

Add two fundamental CLI sub-commands to `carto` so users can **delete** a node and **list** all nodes in their knowledge graph. This is a small sprint intended to validate the Forge workflow end-to-end (plan → implement → review → approve → commit).

## Background

Cartographer currently supports `add` and `link` but lacks any way to remove a node or view a summary of all nodes. These are basic CRUD gaps that make local testing awkward and are ideal candidates for a workflow dry-run.

## Scope

| # | Task ID | Title | Description |
|---|---------|-------|-------------|
| 1 | CART-S03-T01 | Implement `carto rm` | Add a `rm <title>` command that removes the named node (and its edges) from the graph, then persists. Prints a confirmation message. Errors with `chalk.red` if node not found. |
| 2 | CART-S03-T02 | Implement `carto ls` | Add a `ls` command that prints every node title (one per line, `chalk.cyan`). Shows `No nodes yet.` if the graph is empty. |

## Non-Goals

- No fuzzy search / ID lookup (future roadmap item, out of scope).
- No interactive confirmation prompt for `rm` (keep it simple for this sprint).
- No sorting or filtering flags for `ls` — plain listing only.

## Acceptance Criteria

### CART-S03-T01 — `carto rm`

1. Running `carto rm "Some Node"` removes the node and all edges referencing it from the in-memory graph, then saves.
2. Prints `✓ Removed "Some Node" and N edge(s)` in `chalk.green`.
3. If the node title does not exist, prints `✗ Node not found: "Some Node"` in `chalk.red` and exits with code 1.
4. Unit tests cover: happy path, node-not-found, cascading edge removal.

### CART-S03-T02 — `carto ls`

1. Running `carto ls` prints all node titles, one per line, in `chalk.cyan`.
2. If the graph has no nodes, prints `No nodes yet.` in `chalk.yellow`.
3. Unit tests cover: populated listing, empty graph.

## Technical Notes

- Both commands register in `src/cli.ts` via `.command()` blocks (same pattern as `add` / `link`).
- Business logic lives in `src/store/graph.ts` as pure functions (`removeNode`, `listNodes`).
- Follow existing conventions: `const` / arrow functions, no classes, error output to `console.error` with `chalk.red`.
- All source imports use `.js` extensions (ESM requirement).

## Execution Mode

Sequential — T01 first, then T02.

## Out-of-Scope / Deferred

- `--force` flag for `rm`
- `--format json` for `ls`
- TUI (Ink) rendering