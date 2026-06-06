# CODE_REVIEW.md: CART-S01-T01

**Task:** Fix mkdirSync static import and verify gates  
**Reviewer:** cartographer Supervisor (oracle)  
**Date:** 2026-06-06  
**Iteration:** standalone review

---

## Verdict: Approved

All six acceptance criteria independently verified. This was a verification-only task — no code changes were required. The fix (static top-level import of `mkdirSync`) was already present in the working tree.

---

## Acceptance Criteria Verification

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| 1 | `mkdirSync` in top-level `import { … } from "fs"` | ✅ Pass | Line 2 of `graph.ts` confirmed: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` |
| 2 | `save()` contains no `await` keyword | ✅ Pass | `save()` returns `void`, calls `mkdirSync` then `writeFileSync` synchronously — no `await` |
| 3 | `npm run build` exits 0 | ✅ Pass | Independently ran `npm run build` — `tsc` completed, no errors |
| 4 | `npm test` exits 0, regression guard passes | ✅ Pass | Independently ran `npm test` — 31/31 tests pass; CART-B01 guard asserts call order |
| 5 | `npm run lint` exits 0 | ✅ Pass | Independently ran `npm run lint` — no errors |
| 6 | CLAUDE.md known issues entry removed/resolved | ✅ Pass | No CART-B01 entry exists in CLAUDE.md; only a general `link` title-lookup note |

---

## Correctness

- **Static import confirmed**: `mkdirSync` is imported at the top level from `"fs"` — no dynamic `await import(...)` anywhere in the file.
- **Synchronous `save()` confirmed**: The function signature is `save(graph: Graph): void`. No `async`, no `Promise`, no `await`.
- **Call order is correct**: `mkdirSync(dir, { recursive: true })` is called before `writeFileSync(DATA_PATH, ...)` in the function body, ensuring the directory exists before writing.
- **Regression guard test is well-designed**: Uses `vi.mocked()` with `invocationCallOrder` to assert `mkdirSync` is called before `writeFileSync` — not just that both are called, but in the right sequence.

## Security

- No user-controlled input flows through `mkdirSync` or `writeFileSync`. `DATA_PATH` is derived from `process.env.HOME` plus a fixed path segment.
- No injection vectors introduced.

## Architecture

- Follows existing code patterns — no deviations.
- No new modules, no structural changes.

## Conventions

- TypeScript style consistent with the rest of the codebase.
- Test conventions match other test files in the project.

## Business Rules

- No data model changes. No breaking changes. No surface changes.

## Testing

- 31/31 tests pass, including the specific CART-B01 regression guard.
- The regression guard uses `invocationCallOrder` comparison, which is the correct technique for asserting call sequence in Vitest.

---

## Advisory Notes

None. The task is straightforward verification of an already-applied fix, and all evidence checks out independently.