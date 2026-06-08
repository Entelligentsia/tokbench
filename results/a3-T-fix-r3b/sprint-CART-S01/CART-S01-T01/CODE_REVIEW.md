# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

**Iteration:** standalone review

---

**Verdict:** Approved

---

## Review Summary

The implementation correctly standardizes fs module mocks in `src/store/graph.test.ts` to use pure `vi.fn()` instead of `vi.fn(actual.mkdirSync)` / `vi.fn(actual.writeFileSync)`, eliminating real filesystem side effects during test runs. The only source change is a 2-line diff in the co-located test file — `graph.ts` was already correct and required no modification. Both test suites now use consistent pure-mock patterns, both preserve the mkdirSync-before-writeFileSync ordering guard, and all 31 tests pass. No security, architecture, or convention issues found.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | N/A | No package.json changes |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No hooks modified |
| Tool top-level try/catch + exit 1 on error | N/A | No CLI tools modified |
| `--dry-run` supported where writes occur | N/A | No new write paths |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | No path changes |
| Version bumped if material change | N/A | Surface-change only, no version bump required |
| Migration entry present and correct | N/A | No data model changes |
| Security scan report committed | N/A | Not required per plan |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | N/A | No JS/CJS files modified |
| `validate-store --dry-run` exits 0 | ✓ | Store integrity unaffected |
| No prompt injection in modified Markdown files | N/A | No Markdown files modified |

## Issues Found

None. The change is correctly scoped and implemented.

---

## If Approved

### Advisory Notes

1. **Test count discrepancy in PROGRESS.md:** The PROGRESS.md claims "34 tests pass" but the actual count is 31 (6 in `src/store/graph.test.ts` + 25 in `src/__tests__/graph.test.ts`). The plan review correctly reported 31. This is a minor documentation inaccuracy in PROGRESS.md — not a code issue, but worth noting for future reference.

2. **Different import strategies between test suites remain:** The co-located test (`src/store/graph.test.ts`) uses dynamic `await import("fs")` and `await import("./graph.js")` per test, while the integration test (`src/__tests__/graph.test.ts`) uses top-level `import * as fs from "fs"` and static imports. This is a style difference, not an isolation issue — both approaches work correctly with vitest. Standardizing import strategy across suites was not in scope for this task.

3. **Negative verification not persisted:** The plan mentioned performing negative verification (temporarily breaking the import to prove the gate fails). This was done during implementation but not persisted as a committed test case. The existing `invocationCallOrder` guard tests serve this purpose, but a comment documenting the negative verification scenario would improve future maintainability.

4. **The `...actual` spread in the co-located test's mock factory remains appropriate:** The mock spread `...actual` then overrides `mkdirSync`/`writeFileSync`/`readFileSync`/`existsSync` with custom implementations. Since the overridden methods are all pure mocks or deterministic stubs, the `actual` spread only provides fallback for unmocked `fs` methods (none of which are called by the test), so there is no filesystem side-effect risk from this pattern.