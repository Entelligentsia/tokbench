# PLAN.md — CART-S01-T01

## Objective

Verify that the static import fix for `mkdirSync` in `src/store/graph.ts` is correctly implemented and that all gate commands (build, test, lint) pass. Update documentation to reflect the resolved state.

## Approach

This task is primarily a verification task. The code changes for the static import fix appear to already be in place in the working tree. The work consists of:

1. **Code verification**: Confirm that `src/store/graph.ts` has the correct static import and synchronous `save()` function
2. **Gate execution**: Run the three gate commands to verify the fix is correct
3. **Documentation update**: Update CLAUDE.md to reflect the resolved state

## Files to Modify

- `CLAUDE.md` — Update the "Known issues / in-progress" section to reflect that the mkdirSync static import issue has been resolved

## Data Model Changes

None. This task does not modify the entity model or data structures.

## Testing Strategy

The existing test suite already includes a regression guard for this bug (CART-B01) in `src/store/graph.test.ts`:

- The test verifies that `mkdirSync` is called before `writeFileSync` in the `save()` function
- This test was added as part of the bug fix and serves as the primary verification mechanism

The gate commands will be executed in order:

1. `npm run build` — Verify TypeScript compilation succeeds with no errors
2. `npm test` — Verify all tests pass, including the CART-B01 regression guard
3. `npm run lint` — Verify code passes ESLint checks

## Acceptance Criteria

1. `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere
2. `save()` contains no `await` keyword
3. `npm run build` exits 0 with no TypeScript errors
4. `npm test` exits 0 — the regression guard passes
5. `npm run lint` exits 0
6. CLAUDE.md is updated to reflect the resolved state

## Operational Impact

- **Version bump**: Not required (docs-only change)
- **Regeneration**: No user action needed
- **Security scan**: Not required

## Risk Assessment

**Low risk** — The code changes appear to already be in place. This task is primarily about verification and documentation. The main risk is if any of the gate commands fail, which would indicate that the fix is incomplete or incorrect.

## Dependencies

None. This task has no dependencies on other tasks or features.