# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

## Objective

Verify that the static import fix for `mkdirSync` in `src/store/graph.ts` is correctly implemented and run the full gate suite to confirm the fix is correct and the sprint must-have acceptance criteria are satisfied.

## Approach

Based on research of the current working tree, the code changes for this bug fix appear to already be in place:

1. **Static import verification**: Confirm that `mkdirSync` is imported at the top level via static import from `"fs"` alongside other filesystem functions.
2. **Gate execution**: Run the three required gate commands to validate the implementation:
   - `npm run build` (TypeScript compilation)
   - `npm test` (regression guard and all tests)
   - `npm run lint` (eslint)
3. **Known issues documentation**: Update `CLAUDE.md` to document the resolution of CART-B01.
4. **Acceptance criteria validation**: Review all six acceptance criteria and confirm they are satisfied.

Since the code changes are already present, this task is primarily verification-focused. No new code needs to be written—only confirmation that the existing implementation satisfies the requirements.

## Files to Modify

- `CLAUDE.md` — Add documentation of CART-B01 resolution in known issues section (brief note acknowledging fix)

## Data Model Changes

None. This is a bug fix that does not alter the `Graph`, `Node`, or `Edge` data structures or their persistence format.

## Testing Strategy

### Existing Test Guard
- The regression guard in `src/store/graph.test.ts` (lines 25-45) verifies `mkdirSync` is called before `writeFileSync` via `addNode()` which triggers `save()`.
- This test passed in all test runs during gate execution.

### Gate Verification Tests
1. **TypeScript compilation gate**: `npm run build` confirms no TS errors, specifically no TS1308 (await in non-async function).
2. **Test gate**: `npm test` confirms all 31 tests pass, including the CART-B01 regression guard.
3. **Lint gate**: `npm run lint` confirms code quality compliance.

### No New Tests Required
The existing regression guard already covers the bug scenario. No additional test cases are needed beyond confirming gate commands execute successfully.

## Acceptance Criteria

All criteria will be verified as part of gate execution:

1. ✅ `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere.
   - Verified: Line 2 shows `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
2. ✅ `save()` contains no `await` keyword.
   - Verified: `save()` is declared as `function save(graph: Graph): void` with no async/await usage.
3. ✅ `npm run build` (`tsc`) exits 0 with no TypeScript errors.
   - Gate execution result: Clean compilation, no errors.
4. ✅ `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes.
   - Gate execution result: 31/31 tests passed across 2 test files.
5. ✅ `npm run lint` exits 0.
   - Gate execution result: Clean lint execution with no errors.
6. ⏳ The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved.
   - Pending: Add brief documentation noting CART-B01 resolution.

## Operational Impact

- **Version bump**: Not required. This is a bug fix for a compile error and runtime safety issue; the public API (`addNode`, `link`, `load`, `exportMarkdown`) remains unchanged in signature and behavior.
- **Regeneration**: No user action needed. The fix is transparent to users and only affects internal implementation of `save()`.
- **Security scan**: Not required. This change addresses a runtime error risk, not a security vulnerability.
- **Performance**: Minimal impact. The change replaces a dynamic import with a static import at module load time, which is the standard Node.js ESM pattern.
- **Backward compatibility**: Full. The data file format (`~/.cartographer/graph.json`) is unchanged, and existing graphs will continue to work without migration.