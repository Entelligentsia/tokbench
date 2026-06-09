# Sprint Plan — CART-S01: Fix save() import bug in graph.ts

**Sprint:** CART-S01
**Status:** planning → active
**Exec Mode:** sequential
**Captured:** 2026-05-31

---

## Goals

Fix the `await import("fs")` bug in `src/store/graph.ts:save()` so that `mkdirSync` is
imported statically at the top of the file and called correctly before `writeFileSync`.

---

## Task Summary

| Task ID       | Title                                          | Estimate | Depends On | Pipeline | Status  |
|---------------|------------------------------------------------|----------|------------|----------|---------|
| CART-S01-T01  | Fix mkdirSync static import and verify gates   | S        | —          | default  | planned |
| CART-S01-T02  | Add save() directory-path assertion test       | S        | T01        | default  | planned |

---

## Dependency Graph

```
graph TD
  T01[T01: Fix mkdirSync static import and verify gates] --> T02[T02: Add save() directory-path assertion test]
```

---

## Critical Path

T01 → T02. Both tasks are small; total sprint is 2×S.

---

## Analysis Notes

At plan time the static-import fix and the `mkdirSync` call inside `save()` are already
present in `src/store/graph.ts`. The regression guard in `src/store/graph.test.ts`
(verifies `mkdirSync` is called before `writeFileSync`) also exists.

**T01** therefore focuses on confirming the fix is correct, running the full gate suite
(`tsc`, `npm test`, `npm run lint`), and updating the CLAUDE.md known-issues entry once
the gates pass.

**T02** (nice-to-have) adds the missing assertion that `mkdirSync` is called with the
`~/.cartographer` directory path, closing the gap the regression guard leaves open.

---

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Static import shadows existing `readFileSync`/`writeFileSync` imports | Low | Merge into existing `import { … } from "fs"` statement — already done |
| `npm test` isolates fs incorrectly, spy order not captured | Low | Test uses `invocationCallOrder` — works with Vitest mock internals |

---

## Out of Scope

- No new CLI commands
- No changes to `addNode`, `link`, `load`, `exportMarkdown` signatures
- `lowdb` remains in `package.json` (separate debt item)
