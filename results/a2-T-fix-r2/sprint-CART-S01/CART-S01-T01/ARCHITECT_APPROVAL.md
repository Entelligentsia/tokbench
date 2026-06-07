# ARCHITECT APPROVAL — CART-S01-T01

## Task: Fix mkdirSync static import and verify gates

### Review Summary

This task addressed CART-B01 — a regression where `mkdirSync` was dynamically imported (`await import('fs')`) instead of statically imported at the top of `src/store/graph.ts`. The fix was already in place: line 2 now reads:

```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```

All five phases — plan, review-plan, implementation, code-review, and validation — confirmed the fix without requiring any code changes. All gate checks pass:

| Gate | Result |
|------|--------|
| TypeScript build (`tsc`) | ✅ Zero errors |
| Test suite (31 tests) | ✅ All pass, including two independent CART-B01 regression guards |
| Lint (`eslint src`) | ✅ Zero errors/warnings |

### Architectural Assessment

- **Alignment with architecture**: The fix is consistent with project architecture. All `fs` operations use static imports on a single line, matching the project's ESM + strict TypeScript posture per `engineering/architecture/stack.md`.
- **Cross-cutting concerns**: None. The change is isolated to `src/store/graph.ts` line 2. No other modules import `fs` dynamically for `mkdirSync`.
- **Operational impact**: None. The `save()` function is synchronous — no async/dynamic import side effects. No deployment or migration changes required.
- **Data safety**: `mkdirSync` with `{ recursive: true }` ensures idempotent directory creation. Call order (`mkdirSync` before `writeFileSync`) is verified by two independent regression guards using `invocationCallOrder`.

### Deployment Notes

- No deployment changes. Binary entrypoint, data file path, and runtime constraints are unchanged.
- The fix is a source-level correction only — no new dependencies, no config changes.

### Follow-up Items

1. **Pre-existing technical debt remains out of scope**: no node update method, title-only lookup, edge weight always 1, enquirer declared but unused, no concurrency safety on read-modify-write. These should be tracked for future sprints.
2. `lowdb` is listed as a dependency but not used — consider removing in a housekeeping sprint.

**Verdict:** Approved