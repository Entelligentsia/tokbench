# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

---

**Verdict:** Approved

---

## Review Summary

The plan correctly identifies all six acceptance criteria and proposes a straightforward verification approach: inspect the code, run the three gate commands, and update documentation. Independent verification confirms the fix is already in place and all gates pass. The plan is well-scoped and complete.

## Feasibility

The approach is realistic and correctly scoped. The only code file (`src/store/graph.ts`) already contains the fix — `mkdirSync` is in the single top-level `import { … } from "fs"` statement, and `save()` is a plain synchronous function with no `await` or dynamic import. The plan correctly identifies that the work is primarily verification, not implementation. Files to modify are accurate: `src/store/graph.ts` (verify, not change) and `CLAUDE.md` (check for stale CART-B01 entry — none exists).

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — correctly declared as not required.
- **Migration entry targets correct?** N/A — no data model changes.
- **Security scan requirement acknowledged?** Yes — correctly declared as not required (offline-only, no auth surface change).

## Security

No security concerns. The fix corrects a bug in a purely offline, local-file persistence layer. No network calls, no user input sanitisation changes, no auth surface. The `DATA_PATH` derivation from `process.env.HOME` is pre-existing behaviour, not in scope.

## Architecture Alignment

- ✅ Single `import { … } from "fs"` statement — no duplicate imports. Matches the task prompt's explicit risk warning.
- ✅ `graph.ts` exports pure functions only — `save()` remains synchronous, consistent with stack checklist.
- ✅ No class hierarchies introduced.
- ✅ No database or network imports.
- ✅ ESM `.js` extensions in imports maintained.
- ✅ `tsconfig.json` strict mode retained.

## Testing Strategy

The plan's testing strategy is adequate:

- **Gate 1 (build):** Verified independently — `npm run build` exits 0, no TS1308 errors.
- **Gate 2 (tests):** Verified independently — 31/31 tests pass. The CART-B01 regression guard in `src/store/graph.test.ts` correctly asserts `mkdirSync` invocation order before `writeFileSync` using `mock.invocationCallOrder`.
- **Gate 3 (lint):** Verified independently — `npm run lint` exits 0.
- **Manual verification:** The plan includes code inspection, which I've independently confirmed.

No syntax-check or validate-store steps are required by this plan type (no Forge store schema changes).

---

## If Approved

### Advisory Notes

1. **CLAUDE.md CART-B01 entry**: No entry for CART-B01 currently exists in the "Known issues" section, so there is nothing to remove or mark resolved. Criterion 6 is trivially satisfied. The engineer should simply confirm this absence rather than searching for something to change.

2. **`lowdb` and `enquirer` unused deps**: The stack checklist flags these as technical debt. Not in scope for this task, but worth noting for a future cleanup task.

3. **No `DATA_PATH` edge-case testing**: The test suite mocks `fs` and doesn't test the actual directory-creation behaviour when `~/.cartographer/` doesn't exist. This is acceptable for a unit test (and the regression guard confirms call order), but an integration test with a temp directory could provide additional confidence. Non-blocking suggestion.