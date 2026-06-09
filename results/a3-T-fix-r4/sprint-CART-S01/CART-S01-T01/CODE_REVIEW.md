# CODE REVIEW — CART-S01-T01 (standalone review)

## Task: Fix mkdirSync static import and verify gates

## 1. Spec Compliance

| # | Acceptance Criterion | Plan Claims | Independent Verification | Status |
|---|----------------------|-------------|--------------------------|--------|
| 1 | `mkdirSync` in top-level static `import { … }` from `"fs"` | ✅ Met | Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single import, no duplicate, no dynamic import | ✅ Pass |
| 2 | `save()` contains no `await` keyword | ✅ Met | `grep -n 'await' src/store/graph.ts` returns nothing — zero `await` in file | ✅ Pass |
| 3 | `npm run build` exits 0 | ✅ Met | Ran `npm run build` → exit 0, no TypeScript errors | ✅ Pass |
| 4 | `npm test` exits 0 — regression guard passes | ✅ Met (6 tests) | Ran `npm test` → 31/31 pass, including CART-B01 `invocationCallOrder` guard in graph.test.ts | ✅ Pass |
| 5 | `npm run lint` exits 0 | ✅ Met | Ran `npm run lint` → exit 0 | ✅ Pass |
| 6 | CART-B01 known-issue entry removed/marked from CLAUDE.md | N/A | `grep -n 'CART-B01' CLAUDE.md` returns nothing — no entry exists | ✅ Pass |

All six acceptance criteria pass independent verification.

## 2. Code Quality

**`src/store/graph.ts`:**
- `save()` is a clean synchronous void function (lines 12–16). `mkdirSync(dir, { recursive: true })` correctly precedes `writeFileSync`. No issues.
- The `import` on line 2 is the only `from "fs"` import in the file — no duplicate or competing import.
- The function is well-scoped and minimal.

**`src/store/graph.test.ts`:**
- CART-B01 regression guard (lines 4–43) is well-structured. It mocks `fs`, spies on both `mkdirSync` and `writeFileSync`, and asserts `invocationCallOrder` ordering — a robust approach that catches the exact failure mode (mkdirSync not called or called after write).
- Test coverage for graph.ts is adequate: 6 tests in `src/store/graph.test.ts` covering addNode/save ordering, removeNode (orphan + cascade), and listNodeTitles.

**`CLAUDE.md`:**
- Known-issues section contains only the `link` fuzzy-lookup entry — no stale CART-B01 entry to clean up.

## 3. Security

- No security concerns. `dir` is derived from `process.env.HOME` with a `"~"` fallback and a hardcoded subpath. No user-controlled path injection vector in `save()`. Path traversal via `title` does not affect the file write (titles are stored in JSON content, not in file paths).

## 4. Architecture Alignment

- `graph.ts` exports pure functions only — consistent with project convention ("no singleton state, no classes").
- All functions are synchronous — aligned with the offline-only, no-network design constraint.

## 5. Conventions

- `.js` extension used in intra-project imports (e.g., `from "../types.js"`) — ESM convention followed correctly.
- Source style is consistent with the rest of the codebase.

## 6. Diff Assessment

`git diff $(git merge-base HEAD origin/main)..HEAD -- src/store/graph.ts src/store/graph.test.ts CLAUDE.md` produces no output — all changes match `origin/main`. This confirms the plan's conclusion: the fix was already present in the working tree at task creation time. No code modifications were made during the implement phase.

## 7. Findings Summary

- No issues found. The fix (static mkdirSync import, synchronous save) is correctly in place.
- The regression guard using `invocationCallOrder` is a sound technique for catching the original failure mode.
- The "no changes required" conclusion of the implementation is accurate — independently confirmed by the empty diff.

**Verdict:** Approved

### Advisory Notes

- `lowdb` is listed in `package.json` dependencies but is not used in source code. This is pre-existing tech debt unrelated to this task but worth noting for a future cleanup sprint.
- `eslint` is referenced in the `lint` script but not listed in `devDependencies` — also pre-existing and unrelated.