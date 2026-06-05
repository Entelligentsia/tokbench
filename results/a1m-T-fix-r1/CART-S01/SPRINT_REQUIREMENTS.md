# Sprint Requirements — CART-S01

**Captured:** 2026-05-31
**Source:** sprint-intake interview

---

## Goals

1. Fix the known `save()` bug in `src/store/graph.ts` so that `mkdirSync` is imported at the top of the file and called correctly in the synchronous `save()` function.

## In Scope

### Fix `save()` import bug in graph.ts [must-have]

`save()` currently uses `await import("fs")` inside a synchronous function, which is a TypeScript TS1308 compile error and means `mkdirSync` is never called, risking a write failure when `~/.cartographer/` does not yet exist.

**Fix:** replace the dynamic import with a static top-level import of `mkdirSync` from `"fs"`.

**Acceptance criteria:**
- `src/store/graph.ts` imports `mkdirSync` at the top of the file (static import, not dynamic)
- `save()` is a synchronous function with no `await` calls
- `npm run build` (`tsc`) exits 0 with no TS errors
- `npm test` exits 0 — specifically the regression guard in `src/store/graph.test.ts` passes: `mkdirSync` is called before `writeFileSync` in `save()`
- `npm run lint` exits 0

## Out of Scope

- No new CLI commands
- No changes to the public API (`addNode`, `link`, `load`, `exportMarkdown` signatures stay identical)
- No removing `lowdb` from `package.json` (separate debt item, deferred)

## Nice-to-Have *(attempt if must-haves complete)*

- Add a `save()` unit test that verifies the directory path passed to `mkdirSync` matches `~/.cartographer`

## Constraints

- **TypeScript**: strict mode must remain enabled; no `// @ts-ignore` suppression
- **ESM**: static imports must use Node.js built-in specifier (`"fs"`) — no `.js` extension needed for built-ins
- **No new dependencies**: Node.js built-ins only

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Static import shadows existing `readFileSync`/`writeFileSync` imports | Low | Merge into the existing `import { ... } from "fs"` statement |

## Carry-Over

None — first sprint.
