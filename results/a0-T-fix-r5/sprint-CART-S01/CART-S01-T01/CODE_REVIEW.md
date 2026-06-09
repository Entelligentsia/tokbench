# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

(standalone review)

---

**Verdict:** Approved

---

## Review Summary

The CART-B01 fix (static import of `mkdirSync` from `fs` instead of dynamic `await import`) is correctly in place in `src/store/graph.ts`. All six acceptance criteria are independently verified: static import confirmed on line 2, no `await` in `save()`, correct call ordering (`mkdirSync` before `writeFileSync`), and all three gate commands (`build`, `test`, `lint`) exit 0 with 31/31 tests passing including the regression guard.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | 〇 | No new dependencies |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No CLI hooks modified |
| Tool top-level try/catch + exit 1 on error | N/A | No Forge tool modifications |
| `--dry-run` supported where writes occur | N/A | Verification task only |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | No config reads modified |
| Version bumped if material change | N/A | No source changes to graph.ts |
| Migration entry present and correct | N/A | No schema changes |
| Security scan report committed | N/A | No security-sensitive changes |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | 〇 | No modified JS/CJS files |
| `validate-store --dry-run` exits 0 | 〇 | Store unchanged |
| No prompt injection in modified Markdown files | N/A | No markdown modifications |

## Acceptance Criteria Verification

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `src/store/graph.ts` has `mkdirSync` in top-level `import { … } from "fs"` | ✅ Pass | Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` |
| 2 | `save()` contains no `await` keyword | ✅ Pass | Entire file read — zero `await` occurrences |
| 3 | `npm run build` exits 0 | ✅ Pass | `tsc` compiled clean, exit 0 |
| 4 | `npm test` exits 0 — all 31 tests pass | ✅ Pass | 2 test files, 31 tests, all passing |
| 5 | `npm run lint` exits 0 | ✅ Pass | `eslint src` — exit 0 |
| 6 | CLAUDE.md known issues updated for CART-B01 | ✅ Pass | No CART-B01 entry exists — vacuously satisfied |

## Regression Guard Verification

The CART-B01 regression guard test at `src/store/graph.test.ts:22-42` confirms:
- `mkdirSync` is called (assertion: `expect(mkdirSyncSpy).toHaveBeenCalled()`)
- `mkdirSync` is called **before** `writeFileSync` (assertion: `expect(mkdirOrder).toBeLessThan(writeOrder)`)

This guard ran and passed in the full test suite.

## Issues Found

None. The fix is a simple static import correction that was already in place. This task confirmed the fix through independent verification.

---

## If Approved

### Advisory Notes

1. **PROGRESS.md has empty test evidence blocks** — The Build Output, Test Output, and Lint Output sections contain empty code blocks. While the verification is independently confirmed, future tasks should include actual command output for traceability.
2. **Unrelated test additions in diff** — The git diff (HEAD~5..HEAD) includes new tests in `src/__tests__/graph.test.ts` for `exportMarkdown` Links rendering and stats pluralisation. These are benign and pass, but are outside the scope of CART-B01. They appear to be from prior task commits.
3. **`lowdb` and `enquirer` remain unused** — Both are listed in `package.json` dependencies but are not imported anywhere in `src/`. This is pre-existing technical debt, not introduced by this task.