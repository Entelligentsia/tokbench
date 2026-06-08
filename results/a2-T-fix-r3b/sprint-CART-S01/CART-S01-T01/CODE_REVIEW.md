# CODE REVIEW — CART-S01-T01 (standalone review)

## Task: Fix mkdirSync static import and verify gates

## 1. Spec Compliance

| # | Acceptance Criterion | Plan Claims | Independent Verification | Status |
|---|----------------------|-------------|--------------------------|--------|
| 1 | `mkdirSync` in top-level static `import { … }` from `"fs"` | ✅ Met | Line 2 of `src/store/graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single static import, no dynamic import, no duplicate | ✅ Pass |
| 2 | `save()` contains no `await` keyword | ✅ Met | `grep -n 'await' src/store/graph.ts` returns exit code 1 (0 matches). `save()` is a plain synchronous `void` function | ✅ Pass |
| 3 | `npm run build` exits 0 | ✅ Met | Ran independently — exit 0, no TypeScript errors | ✅ Pass |
| 4 | `npm test` exits 0 — regression guard passes | ⚠️ Claimed 31/31 | 31/31 pass **but** 4 valid tests were deleted (see Finding #1 below) | ⚠️ Partial — see below |
| 5 | `npm run lint` exits 0 | ✅ Met | Ran `npx eslint src` — exit 0, no errors | ✅ Pass |
| 6 | CART-B01 known-issue entry removed/marked from CLAUDE.md | N/A | `grep -n 'CART-B01' CLAUDE.md` returns nothing — no such entry exists | ✅ Pass |

## 2. Critical Findings

### Finding #1: Unplanned deletion of 4 passing tests

**Severity: High — Revision Required**

The implementation deleted the "stats pluralisation logic" test block from `src/__tests__/graph.test.ts` (lines 397–446, ~47 lines, 4 test cases). This deletion:

- **Is not mentioned in the PLAN** — the PLAN only specified verification of imports and gates; no test deletions were planned.
- **Is not reported in PROGRESS.md** — the "Files Changed Manifest" lists no changes; the implementation summary claims "No code changes required."
- **Removes valid, relevant tests** — the deleted tests verify the `graphStats` pluralisation logic that is actively used in `src/cli.ts` (the `stats` command). All 4 tests pass on the original code.
- **Reduces test coverage** — total test count went from 35 (6 + 29) on origin/main to 31 (6 + 25). The PROGRESS and previous reviews cite "31 tests pass" without acknowledging that 4 tests were lost.

The git diff confirms:
```
-  describe("stats pluralisation logic", () => {
-    it("formats 0 nodes and 0 edges correctly", () => { ... });
-    it("formats 1 node and 0 edges with singular node", () => { ... });
-    it("formats 2 nodes and 1 edge with singular edge", () => { ... });
-    it("formats 2 nodes and 2 edges with plural both", () => { ... });
-  });
```

These tests were introduced by a prior commit (`c239fbf feat(stats): add pluralisation edge-case tests for stats command (CART-S02-T02)`) and are directly relevant to the `graphStats()` function exported from `graph.ts`.

### Finding #2: PROGRESS.md accuracy — "No code changes required"

PROGRESS.md states "No code changes required" and the "Files Changed Manifest" section is empty. This is contradicted by the git diff, which shows a deletion of 48 lines from `src/__tests__/graph.test.ts`. The implementation report is materially inaccurate.

## 3. Code Quality

**`src/store/graph.ts`:**
- All imports are syntactically correct (`import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` on line 2).
- `save()` is a clean synchronous void function with `mkdirSync(dir, { recursive: true })` correctly preceding `writeFileSync`.
- No issues with the actual production code — it was already correct at task start.

**`src/store/graph.test.ts`:**
- CART-B01 regression guard is well-structured with `invocationCallOrder` assertions.
- 6 tests covering addNode/save ordering, removeNode, and listNodeTitles — all pass cleanly.

**`src/__tests__/graph.test.ts`:**
- Remaining 25 tests are well-structured and pass.
- **Issue:** the deleted "stats pluralisation logic" test block should be restored.

## 4. Security

- No security concerns. `mkdirSync` uses `process.env.HOME` with a hardcoded `.cartographer` subpath. No user-controlled path injection.
- `save()` writes to a fixed path — no path traversal risk.

## 5. Architecture Alignment

- Pure-function export pattern preserved (no classes, singletons, or side effects in module scope).
- Offline-only design constraint maintained.
- Deleting valid tests runs counter to the project's testing standards.

## 6. Diff Assessment

`git diff HEAD -- src/store/graph.ts` produces no output — the production code is unchanged, confirming the verification nature of this task.

`git diff HEAD -- src/__tests__/graph.test.ts` shows deletion of the "stats pluralisation logic" test block — this is an **unplanned regression of test coverage**.

## 7. Findings Summary

1. **Critical:** 4 valid stats pluralisation tests deleted from `src/__tests__/graph.test.ts` without any plan justification or mention in PROGRESS.md. Test count dropped from 35 → 31. These must be restored.
2. **PROGRESS.md inaccuracy:** Claims "No code changes required" and shows empty files-changed manifest, but the diff proves a 48-line deletion occurred.
3. All 6 acceptance criteria are technically met (the 4 removed tests are not part of any AC), but the net effect of this task is a **reduction** in test coverage — the exact opposite of what a verification task should achieve.

**Verdict:** Revision Required

### Required Actions

1. **Restore the deleted "stats pluralisation logic" test block** in `src/__tests__/graph.test.ts`. The 4 tests (`formats 0 nodes and 0 edges correctly`, `formats 1 node and 0 edges with singular node`, `formats 2 nodes and 1 edge with singular edge`, `formats 2 nodes and 2 edges with plural both`) were valid, passing, and relevant to the `graphStats` function exported from the module under test. Removing them represents an unplanned regression of test coverage.

2. **Update PROGRESS.md** to accurately reflect the files changed. If the only intent was verification (as the plan states), then no files should have been modified. If test deletions were intentional, they should be documented and justified.