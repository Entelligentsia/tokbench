# VALIDATION REPORT — CART-S01-T01 (standalone review)

**Task:** Fix mkdirSync static import and verify gates  
**Validator:** qa-engineer  
**Date:** 2026-06-05

---

## Verdict: **Approved**

All six acceptance criteria pass. No gaps identified.

---

## Acceptance Criteria Checklist

| # | Criterion | Evidence | Result |
|---|-----------|----------|--------|
| 1 | `mkdirSync` in top-level static `import { … }` from `"fs"` | `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single import, no dynamic import, no duplicate | ✅ Pass |
| 2 | `save()` contains no `await` keyword | `save()` (lines 12-16) is a plain `function save(graph: Graph): void` — zero `await` expressions in `graph.ts` | ✅ Pass |
| 3 | `npm run build` exits 0 | Ran `npm run build` → exit 0, no TypeScript errors | ✅ Pass |
| 4 | `npm test` exits 0 — regression guard passes | Ran `npm test` → 31/31 tests pass. `src/store/graph.test.ts` contains CART-B01 regression guard: `invocationCallOrder` assertion confirms `mkdirSync` called before `writeFileSync` within `save()`. Six tests in `graph.test.ts` cover the invariant. | ✅ Pass |
| 5 | `npm run lint` exits 0 | Ran `npm run lint` → exit 0, no ESLint errors | ✅ Pass |
| 6 | CART-B01 known-issue entry removed/marked from CLAUDE.md | `grep -n 'CART-B01' CLAUDE.md` returns no match — no entry exists to remove. Criterion is N/A. | ✅ Pass (N/A) |

---

## Validation Categories

### 1. Acceptance Criteria Coverage
All six criteria addressed. No unmapped requirements.

### 2. Happy Path
- `addNode()` → calls `save()` → `mkdirSync` called before `writeFileSync` — verified by regression guard.
- TypeScript compiles without errors — static import resolves at compile time.
- All 31 tests pass including `addNode()` regression guard.

### 3. Edge Cases
- `mkdirSync(dir, { recursive: true })` handles the case where the directory already exists — safe to call multiple times.
- `save()` returns `void`; callers do not depend on a return value.
- No async paths exist in `graph.ts` that could trigger the CART-B01 defect.

### 4. Regression
- CART-B01 regression guard in `src/store/graph.test.ts` (describe block: "CART-B01: mkdirSync called before writeFileSync in save()") specifically asserts the `invocationCallOrder` invariant via vitest spies on `fs.mkdirSync` and `fs.writeFileSync`.
- The guard covers `addNode()` path; other `save()` callers (`link()`, `removeNode()`) use the same `save()` function, so the invariant holds for all callers.
- 25 additional tests in `src/__tests__/graph.test.ts` cover graph operations — all pass.

### 5. Test Quality
- The regression guard uses `vi.mocked(fs.mkdirSync).mock.invocationCallOrder` — a specific, non-trivial assertion that would fail if the call order were reversed. This is not a trivially-passing test.
- `vi.clearAllMocks()` in `beforeEach` ensures clean state per test.
- Test describes the CART-B01 bug by name and by expected fix, making the intent self-documenting.

---

## Findings Summary

- **`mkdirSync` import:** Static, top-level, singular — no dynamic `await import()` anywhere.
- **`save()` async status:** Plain synchronous `void` function — zero `await` keywords in file.
- **Gate suite:** All three gates pass (`build`, `test`, `lint`) with independent verification.
- **Regression guard:** Present and specific — `invocationCallOrder` assertion, not just "was called".
- **CLAUDE.md:** No CART-B01 entry exists — no cleanup action needed.

---

## Conclusion

Task CART-S01-T01 requires no code changes. The CART-B01 fix is already correctly implemented: `mkdirSync` is statically imported on line 2 of `graph.ts`, `save()` is a synchronous void function, and all gates pass. The regression guard in `graph.test.ts` validates the fix end-to-end.