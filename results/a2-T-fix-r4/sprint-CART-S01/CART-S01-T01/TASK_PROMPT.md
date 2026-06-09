# CART-S01-T01: Fix mkdirSync static import and verify gates

**Sprint:** CART-S01
**Estimate:** S
**Pipeline:** default

---

## Objective

Ensure `src/store/graph.ts` imports `mkdirSync` via a static top-level import from `"fs"`
and that `save()` is a plain synchronous function with no `await` expressions. Then run
the full gate suite to confirm the fix is correct and the sprint must-have acceptance
criteria are satisfied.

## Acceptance Criteria

1. `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere.
2. `save()` contains no `await` keyword.
3. `npm run build` (`tsc`) exits 0 with no TypeScript errors.
4. `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes.
5. `npm run lint` exits 0.
6. The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved.

## Context

The bug was filed as CART-B01. Before the fix, `save()` used `await import("fs")` inside a
synchronous function body, which is a TypeScript TS1308 compile error and means `mkdirSync`
is never actually called — risking a write failure when `~/.cartographer/` does not yet exist.

At plan time the static-import fix and the `mkdirSync` call inside `save()` already appear
to be in place in the working tree. This task's primary work is to verify that state, run
the three gate commands, and land any remaining corrections.

**Risk**: the existing `import { readFileSync, writeFileSync, existsSync } from "fs"` line
must be extended to include `mkdirSync` rather than adding a second import statement.

## Source Files Involved

- `src/store/graph.ts` — the only file needing code change
- `CLAUDE.md` — known-issues section to be updated

## Operational Impact

- **Version bump:** not required
- **Regeneration:** no user action needed
- **Security scan:** not required
