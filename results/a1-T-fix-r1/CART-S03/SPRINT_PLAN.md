# Sprint Plan — CART-S03

**Workflow test – add node delete + list commands**

**Status:** planning
**Execution mode:** sequential (T01 → T02)

---

## Overview

This sprint fills two basic CRUD gaps in the `carto` CLI: removing a node (and its edges) and listing all node titles. Both are small, independent tasks exercised sequentially to validate the Forge workflow end-to-end.

---

## Task Breakdown

| # | Task ID | Title | Estimate | Dependencies |
|---|---------|-------|----------|--------------|
| 1 | CART-S03-T01 | Implement `carto rm` command to delete a node | S | — |
| 2 | CART-S03-T02 | Implement `carto ls` command to list all nodes | S | — |

---

## Dependency Graph

```
T01 ──(none)     T02 ──(none)
```

Both tasks are independent. Sequential execution (T01 first) follows the convention that the destructive command should land before the read-only one so `ls` output can be verified manually after deletions.

---

## Critical Path

T01 → T02 (sequential policy, not a hard data dependency)

---

## Acceptance Criteria (Sprint-level)

- [ ] `carto rm "Some Node"` removes the node and all edges referencing it
- [ ] `carto rm` prints a `chalk.red` error when the node is not found
- [ ] `carto ls` prints all node titles in `chalk.cyan`; shows `No nodes yet.` in `chalk.yellow` for an empty graph
- [ ] `npm run build`, `npm test`, `npm run lint` all pass after each task
- [ ] Pure-function/CLI separation maintained (`graph.ts` pure, `cli.ts` I/O)