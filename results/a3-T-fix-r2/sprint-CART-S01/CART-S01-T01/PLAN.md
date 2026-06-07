# PLAN.md — CART-S01-T01: Fix mkdirSync static import and verify gates

## Objective

Verify that the static import fix for `mkdirSync` is correctly implemented in `src/store/graph.ts` and run the full gate suite to confirm the fix resolves CART-B01 and satisfies sprint acceptance criteria.

## Approach

This task is primarily a verification task. The code fix has already been applied:

1. **Verify static import**: Confirm that `mkdirSync` is imported at the top level from `"fs"` alongside other fs functions
2. **Verify synchronous save()**: Confirm that `save()` is a plain synchronous function with no `await` expressions
3. **Verify mkdirSync call order**: Confirm that `mkdirSync` is called before `writeFileSync` in the `save()` function
4. **Run gate suite**: Execute the three gate commands (build, test, lint) to verify the fix
5. **Update documentation**: Remove or mark resolved any known issues entry for CART-B01 in CLAUDE.md

## Files to Modify

**None** — The fix has already been applied. This task is verification-only.

Files verified:
- `src/store/graph.ts` — Contains the static import and synchronous save() implementation
- `src/store/graph.test.ts` — Contains the regression guard test
- `CLAUDE.md` — Checked for known issues entry (none found for CART-B01)

## Data Model Changes

**None** — This task does not modify the data model.

## Testing Strategy

The verification strategy relies on the existing regression guard test and gate suite:

1. **Regression guard test** (`src/store/graph.test.ts`):
   - Verifies that `mkdirSync` is called before `writeFileSync` when `addNode()` is invoked
   - Uses Vitest mocks to track invocation order
   - This test already exists and passes

2. **Build gate** (`npm run build`):
   - Runs TypeScript compiler (`tsc`)
   - Verifies no TS1308 errors (await import in non-async function)
   - Confirms type safety across the codebase

3. **Test gate** (`npm test`):
   - Runs all 31 tests in the test suite
   - Confirms the regression guard passes
   - Validates no regressions in other functionality

4. **Lint gate** (`npm run lint`):
   - Runs ESLint on the source code
   - Confirms code quality standards are met

## Acceptance Criteria

1. ✅ `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere.
   - **Status**: Verified — `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`

2. ✅ `save()` contains no `await` keyword.
   - **Status**: Verified — `save()` is a synchronous function with no async/await

3. ✅ `npm run build` (`tsc`) exits 0 with no TypeScript errors.
   - **Status**: Verified — Build completed successfully with no errors

4. ✅ `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes.
   - **Status**: Verified — All 31 tests passed, including the regression guard

5. ✅ `npm run lint` exits 0.
   - **Status**: Verified — Lint passed with only an unrelated warning in lib/schema-loader.cjs

6. ✅ The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved.
   - **Status**: Verified — No specific known issues entry for CART-B01 exists in CLAUDE.md

## Operational Impact

- **Version bump**: Not required — This is a bug fix verification, not a feature change
- **Regeneration**: No user action needed — The fix is already in place
- **Security scan**: Not required — No security implications

## Risk Assessment

**Low risk** — This is a verification task for a fix that has already been applied:

- The static import pattern is correct and follows TypeScript best practices
- The synchronous `save()` function is properly implemented
- The regression guard test provides ongoing protection against future regressions
- All gate commands pass successfully

## Notes

- The fix addresses CART-B01, which was a critical bug where `await import("fs")` was used inside a synchronous function, causing a TypeScript compile error and preventing `mkdirSync` from being called
- The existing `import { readFileSync, writeFileSync, existsSync } from "fs"` line was correctly extended to include `mkdirSync` rather than adding a second import statement
- The regression guard test in `src/store/graph.test.ts` ensures this bug cannot reoccur