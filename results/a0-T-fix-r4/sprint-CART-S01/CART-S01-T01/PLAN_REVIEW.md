# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

**Reviewer:** cartographer Supervisor (Oracle)
**Date:** 2026-06-09
**(standalone review)**

---

## 1. Correctness

The plan correctly identifies this as a **verification task** — the code changes are already in place in the working tree and the primary work is running the gate suite and confirming acceptance criteria.

Independent verification of the plan's claims against the actual source code:

| Claim | Verified | Evidence |
|-------|----------|----------|
| `mkdirSync` is in top-level `import` from `"fs"` | ✅ | Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single import, no duplicates |
| `save()` contains no `await` | ✅ | `grep -n 'await' src/store/graph.ts` returns nothing |
| `mkdirSync` called before `writeFileSync` in `save()` | ✅ | Lines 14–15: `mkdirSync(dir, { recursive: true }); writeFileSync(DATA_PATH, ...)` |
| Regression guard test exists | ✅ | `graph.test.ts` CART-B01 test checks `mock.invocationCallOrder` to enforce ordering |

**Issue — AC6 silently rewritten:** The original task prompt specifies AC6 as "The 'Known issues' entry for this bug in `CLAUDE.md` is removed or marked resolved." The plan replaces this with "Document verification results in PROGRESS.md." While the change is justifiable (no CART-B01 entry exists in CLAUDE.md to remove), the plan does not explain the deviation. The original AC6 is implicitly already satisfied (the entry doesn't exist), but the plan should acknowledge the mapping explicitly rather than substituting a different criterion.

**Severity:** Low — no material impact; advisory only.

## 2. Security

No security concerns. The fix corrects a file I/O pattern (static import vs dynamic import). No new attack surface, no input validation changes, no auth boundary crossings.

## 3. Architecture

- The static import pattern correctly follows ESM conventions and the project's stack checklist requirement for `mkdirSync` before `writeFileSync`.
- Single import statement from `"fs"` — no duplicate or conflicting imports. ✅
- `DATA_PATH` uses `process.env.HOME ?? "~"` per architecture guardrails. ✅
- Pure function exports, no module-level side effects. ✅

## 4. Conventions

- ESM `.js` extensions on relative imports (`../types.js`) ✅
- No `require()` / CommonJS patterns ✅
- No `class` definitions — uses `const` and functions only ✅
- `tsconfig.json` strict mode retained ✅

## 5. Business Rules

No business rule violations. The fix ensures the persistence layer works correctly (directory created before file write), which is a prerequisite for all CRUD operations.

## 6. Testing

The test strategy is adequate:

- **Gate suite** (`build`, `test`, `lint`) covers all three verification dimensions. ✅
- **Regression guard** in `graph.test.ts` directly asserts call ordering via `mock.invocationCallOrder`, which is a strong guarantee against the original bug recurring. ✅
- **31 tests pass** across both test files, covering `addNode`, `link`, `removeNode`, `listNodeTitles`, and the CART-B01 regression guard.

**Minor note:** The "Files to Modify" table lists `src/store/graph.ts` and `src/store/graph.test.ts`, but the changes described are "Verify static import exists" and "Verify regression guard passes" — these are verification actions, not modifications. The table header is misleading for a verification task. Consider "Files to Verify" instead.

## Verdict

**Approved**

### Advisory Notes

1. **AC6 deviation should be acknowledged.** The plan substitutes "Document verification results in PROGRESS.md" for the original "Remove CART-B01 Known issues entry from CLAUDE.md" without explicitly noting the mapping. Since no CART-B01 entry exists in CLAUDE.md, the original AC6 is implicitly satisfied, but the plan should state this rather than silently replacing the criterion.
2. **"Files to Modify" table semantically mislabeled.** For a verification task where no code changes are needed, "Files to Verify" would be more accurate.