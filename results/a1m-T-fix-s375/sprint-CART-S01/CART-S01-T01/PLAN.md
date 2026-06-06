# PLAN.md

## Objective

Verify that `src/store/graph.ts` correctly statically imports `mkdirSync` from `"fs"` and that the `save()` function is synchronous with no `await` expressions. Run the full gate suite (build, test, lint) to confirm the fix is correct and all sprint acceptance criteria are satisfied.

## Approach

This is a verification task. The code changes (static import of `mkdirSync` and the `mkdirSync` call inside `save()`) are already in place in the working tree. The primary work is to run three gate commands to verify correctness, and update documentation if any known-issues entries exist.

### Research Findings

**Current State Verification:**
- `src/store/graph.ts` line 2: Already includes `mkdirSync` in the static import: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
- `src/store/graph.ts` lines 7-11: The `save()` function is synchronous (returns `void`), contains no `await` keyword, and invokes `mkdirSync(dir, { recursive: true })` before `writeFileSync`
- No `await` keywords exist anywhere in `src/store/graph.ts`
- Regression guard test exists in `src/store/graph.test.ts` that validates `mkdirSync` is called before `writeFileSync`

**Gate Configuration:**
- Build gate: `npm run build` → runs `tsc` (TypeScript compiler)
- Test gate: `npm test` → runs `vitest run` (unit test framework)
- Lint gate: `npm run lint` → runs `eslint src` (static analysis)

**Documentation Status:**
- `CLAUDE.md` contains a general "Known issues / in-progress" section but has no specific entry for CART-B01 (the mkdirSync bug)
- The bug record `CART-B01` is not present in the Forge store

### Verification Strategy

1. **Gate Execution**: Run three commands in sequence:
   - `npm run build` - Verify TypeScript compilation succeeds with no errors
   - `npm test` - Verify all tests pass, especially the regression guard
   - `npm run lint` - Verify no ESLint violations

2. **Success Criteria**: All three commands must exit with code 0 and produce no errors.

3. **Documentation Update**: Since no known-issues entry exists in `CLAUDE.md` for this specific bug, no documentation update is required. The "Known issues / in-progress" section already contains unrelated content; adding a resolved entry would be inconsistent with current documentation practice.

### Risk Mitigation

- **Gate Ordering**: Run build first to catch TypeScript errors before testing. Run tests to catch runtime issues before linting.
- **Regression Guard**: The existing test in `src/store/graph.test.ts` specifically validates that `mkdirSync` is called before `writeFileSync`, ensuring the bug fix remains correct.
- **Static Import Verification**: No changes needed - `mkdirSync` is already statically imported. The risk mentioned in the task context (adding a second import statement) has been avoided.

## Files to Modify

**None** - The code is already in the correct state. This is a verification-only task.

**Potential Documentation Update** (if needed):
- `CLAUDE.md` - Update known-issues section if a CART-B01 entry exists (currently no such entry exists)

## Data Model Changes

No data model changes. The entity model (Graph, Node, Edge) is unchanged.

## Testing Strategy

### Gate Tests

1. **Build Gate** (`npm run build`):
   - Commands TypeScript compiler (`tsc`)
   - Expects exit code 0
   - No TypeScript errors allowed
   - Output: `dist/` directory with compiled JavaScript files

2. **Test Gate** (`npm test`):
   - Runs Vitest test suite
   - Expects exit code 0
   - All tests must pass, including:
     - Regression guard: `addNode() calls mkdirSync before writeFileSync`
     - Other existing tests for removeNode, listNodeTitles
   - Mocked `fs` module validates `mkdirSync` invocation order

3. **Lint Gate** (`npm run lint`):
   - Runs ESLint on `src` directory
   - Expects exit code 0
   - No linting violations allowed
   - Uses TypeScript ESLint recommended rules

### Test Coverage

Existing tests in `src/store/graph.test.ts` provide coverage for:
- The CART-B01 regression guard (mkdirSync called before writeFileSync)
- removeNode with orphan nodes
- removeNode with cascading edge deletion
- listNodeTitles with empty and populated graphs

No additional tests are required as the code is already in the correct state.

## Acceptance Criteria

1. ✅ `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — **VERIFIED** (line 2 already contains static import)
2. ✅ `save()` contains no `await` keyword — **VERIFIED** (no `await` exists in the file)
3. ⬜ `npm run build` (`tsc`) exits 0 with no TypeScript errors — **TO VERIFY** during implementation
4. ⬜ `npm test` exits 0 — regression guard passes — **TO VERIFY** during implementation
5. ⬜ `npm run lint` exits 0 — **TO VERIFY** during implementation
6. ⬜ Documentation update — **NOT APPLICABLE** (no known-issues entry exists)

## Operational Impact

- **Version bump**: Not required - verification-only task, no behavior changes
- **Regeneration**: No user action needed - CLI binary is not modified
- **Security scan**: Not required - no security-sensitive changes
- **Performance impact**: None - code behavior unchanged
- **Breaking changes**: None - existing functionality unchanged
- **Data migration**: Not required - data model unchanged

## Rollback Plan

No rollback needed. If any gate fails:
1. Investigate the failure (compilation error, test failure, or linting issue)
2. Apply corrective action if code changes are actually needed
3. Re-run the failing gate

Since the code is already correct with static imports and no await in save(), gate failures would indicate environment issues rather than code issues requiring rollback.

## Dependencies

- Node.js 20+ ESM runtime
- TypeScript 5.3.0+ compiler
- Vitest test framework
- ESLint with TypeScript parser

## Notes

- This task is part of sprint CART-S01 "Fix save() import bug in graph.ts"
- The bug was filed as CART-B01 but the bug record does not exist in the Forge store
- Task prompt indicates the fix is already in place; this is verification work
- The task is estimated as "S" (Small) due to verification-only nature
- Success of this task unblocks subsequent tasks in the sprint