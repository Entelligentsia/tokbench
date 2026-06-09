# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via static import from `"fs"` and that `save()` is a plain synchronous function with no `await` expressions. Run the full gate suite to confirm the fix is correct and the sprint must-have acceptance criteria are satisfied.

## Approach

The code changes for this bug fix appear to already be in place in the working tree. This task is primarily a verification task to run the three gate commands and confirm that:

1. The static import of `mkdirSync` is correct
2. No `await` expressions exist in the `save()` function
3. TypeScript compilation succeeds
4. All tests pass, including the regression guard
5. ESLint passes without errors

The verification approach is to run the three gate commands sequentially and document the results.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verify static import exists | Acceptance criterion requires `mkdirSync` in top-level import |
| `src/store/graph.test.ts` | Verify regression guard passes | Ensures mkdirSync is called before writeFileSync |
| `CLAUDE.md` | Document verification results | Note that CART-B01 entry management not applicable |

**Note**: The bug record CART-B01 mentioned in the task prompt does not exist in the Forge store or in CLAUDE.md's known issues section. This task accepts the code fix as the primary work item, with verification as the deliverable.

## Plugin Impact Assessment

- **Version bump required?** No — This is a bug fix to existing functionality in `src/` directory, not a plugin change
- **Migration entry required?** No — No schema changes or regeneration targets
- **Security scan required?** No — No changes to `forge/` directory
- **Schema change?** No — No Forge schemas affected

## Testing Strategy

- **Syntax check**: `npm run build` (runs `tsc`) to verify TypeScript compilation
- **Unit tests**: `npm test` (runs `vitest`) to verify all tests pass, including the CART-B01 regression guard
- **Lint check**: `npm run lint` (runs `eslint`) to verify code quality standards
- **Manual verification**: Inspect `src/store/graph.ts` to confirm static import and synchronous save()

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in top-level `import` statement from `"fs"`
- [ ] `save()` contains no `await` keyword  
- [ ] `npm run build` (`tsc`) exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — regression guard for `mkdirSync` called before `writeFileSync` passes
- [ ] `npm run lint` exits 0
- [ ] Document verification results in PROGRESS.md

## Operational Impact

- **Distribution:** No user action required — this is an internal code fix
- **Backwards compatibility:** No breaking changes — existing functionality is preserved
- **Performance:** No impact — synchronous behavior remains unchanged
- **Data loss risk:** None — fix prevents potential write failures when directory doesn't exist