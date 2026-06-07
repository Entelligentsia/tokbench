# PLAN REVIEW — CART-S01-T01

**Reviewer:** cartographer Supervisor (standalone review)
**Date:** 2026-06-07

---

## Verdict: Approved

---

## 1. Correctness

The plan accurately describes the current state of the code. I verified independently:

- **Line 2 of `src/store/graph.ts`**: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — `mkdirSync` is in the single top-level static import, not a separate statement. ✅
- **`save()` function**: Calls `mkdirSync(dir, { recursive: true })` before `writeFileSync(DATA_PATH, ...)`. No `await` keyword present. ✅
- **Regression guard in `src/store/graph.test.ts`**: Uses `invocationCallOrder` to assert `mkdirSync` is called before `writeFileSync`. ✅
- **Additional guards in `src/__tests__/graph.test.ts`**: Three tests for `save()` `mkdirSync` behaviour (ordering, always-called, correct-path). ✅
- **All gates pass**: `npm test` (31/31), `npm run build` (exit 0), `npm run lint` (exit 0). ✅

The plan correctly identifies no code modification is required — the fix is already in place.

## 2. Security

No security concerns. The task is a verification-only activity with no code changes. The existing `mkdirSync` with `{ recursive: true }` is the correct pattern for ensuring the directory exists before writing.

## 3. Architecture

The static import pattern follows the stack-checklist requirement: `graph.ts` exports pure functions only, no module-level side effects. The `mkdirSync` call is inside `save()` (a function scope), not a module-level side effect. Aligns with project architecture.

## 4. Conventions

- ESM import with `.js` extension in re-exports — consistent with project conventions. ✅
- Test files use `vi.mock("fs", async (importOriginal) => { ... })` pattern — matches stack-checklist. ✅
- `beforeEach(() => vi.clearAllMocks())` present in test files. ✅

## 5. Business Rules

No business rule violations. The fix ensures data persistence (saving the graph JSON) works correctly when the `~/.cartographer/` directory doesn't yet exist.

## 6. Testing

Testing strategy is sound:
- 6 tests in `src/store/graph.test.ts` (including the CART-B01 regression guard)
- 25 tests in `src/__tests__/graph.test.ts` (including 3 additional `save()` guards)
- Total 31 tests all passing

The regression guard uses `invocationCallOrder` comparison, which is the correct vitest mechanism for asserting call ordering — more reliable than checking call counts alone.

## Advisory Notes

1. **Task prompt criterion #6 (CLAUDE.md known-issues entry)**: The task prompt requires "The 'Known issues' entry for this bug in CLAUDE.md is removed or marked resolved." The PLAN.md does not explicitly address this criterion. My independent review of `CLAUDE.md` shows no CART-B01 entry currently exists, so the criterion is effectively satisfied. However, the PLAN should have explicitly acknowledged this rather than silently omitting it. **Not a blocker**, but a documentation gap in the plan.

2. **PLAN acceptance criteria expansion**: The PLAN adds criteria not in the task prompt (smoke test, `node --check`, `validate-store.cjs --dry-run`, test-file comments). These are reasonable quality gates but represent scope creep from the original task prompt. Not harmful, but worth noting for future task fidelity.

3. **"No modification required" confidence**: The plan correctly identifies this as a verification-only task. The code is already fixed, and all gates pass. The task's value is in confirming and documenting that the CART-B01 fix landed correctly.