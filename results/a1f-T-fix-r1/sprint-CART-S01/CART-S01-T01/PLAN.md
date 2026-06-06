# PLAN.md: Fix mkdirSync static import and verify gates

**Task ID:** CART-S01-T01  
**Sprint:** CART-S01  
**Status:** planned

---

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via static top-level import from `"fs"` and that `save()` is a synchronous function with no `await` expressions. Confirm all gate commands pass to validate the fix and satisfy sprint acceptance criteria.

---

## Approach

This task is primarily verification work. The code changes for the CART-B01 bug fix have already been applied to the working tree. The plan focuses on:

1. **Code verification**: Confirm the current state of `src/store/graph.ts` matches the fix requirements
2. **Gate execution**: Run the three required gate commands to validate the fix
3. **Test validation**: Ensure the regression guard test passes
4. **Documentation update**: Check if CLAUDE.md needs updates for known issues

---

## Files to Modify

**None** - The fix has already been applied. This task is verification-only.

**Files examined:**
- `src/store/graph.ts` - Verified to have correct static import and synchronous `save()` function
- `src/store/graph.test.ts` - Contains regression guard test for CART-B01
- `CLAUDE.md` - No specific CART-B01 entry to update (only general known issue about `link` command)

---

## Data Model Changes

**None** - This task does not modify the entity model, data structures, or persistence layer.

---

## Testing Strategy

### Existing Tests
The regression guard test in `src/store/graph.test.ts` already validates the fix:
- Verifies `mkdirSync` is called before `writeFileSync` in `save()`
- Uses `vi.mocked()` to track invocation order
- Covers the `addNode()` function which internally calls `save()`

### Gate Verification
Run the three required gate commands:
1. **TypeScript compilation**: `npm run build` - Must exit 0 with no TS1308 errors
2. **Unit tests**: `npm test` - Must exit 0 with all 31 tests passing
3. **Linting**: `npm run lint` - Must exit 0 with no lint errors

### Acceptance Criteria Validation
Each acceptance criterion maps to a verification step:
1. ✓ Static import verified in code review
2. ✓ No `await` in `save()` verified in code review
3. ✓ Build gate passes
4. ✓ Test gate passes (including regression guard)
5. ✓ Lint gate passes
6. ✓ CLAUDE.md reviewed (no CART-B01 entry exists to update)

---

## Acceptance Criteria

1. `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere.
2. `save()` contains no `await` keyword.
3. `npm run build` (`tsc`) exits 0 with no TypeScript errors.
4. `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes.
5. `npm run lint` exits 0.
6. The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved.

---

## Operational Impact

- **Version bump:** Not required - This is a bug fix verification, not a feature change
- **Regeneration:** No user action needed - No generated code or templates affected
- **Security scan:** Not required - No security-related changes
- **Breaking changes:** None - This is a bug fix that maintains existing behavior
- **Performance impact:** None - No performance-related changes
- **Data migration:** None - No schema or data structure changes

---

## Risk Assessment

**Low Risk** - This is verification work for a fix that has already been applied. The code changes are minimal and well-tested:

- **Code change risk**: Low - The fix is a simple import statement change
- **Test coverage**: High - Regression guard test specifically validates the fix
- **Rollback plan**: Not applicable - No changes to roll back
- **Dependencies**: None - No external dependencies affected

---

## Implementation Notes

### Current State Verification

**Line 2 of `src/store/graph.ts`:**
```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```
✓ Correct - `mkdirSync` is statically imported at top level

**Lines 12-16 of `src/store/graph.ts`:**
```typescript
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```
✓ Correct - Function is synchronous (returns `void`), no `await`, calls `mkdirSync` before `writeFileSync`

### Test Coverage

The regression guard test in `src/store/graph.test.ts` (lines 8-28) validates:
- `mkdirSync` is called when `addNode()` is invoked
- `mkdirSync` is called BEFORE `writeFileSync` (invocation order check)

This test passed in the verification run, confirming the fix is correct.

### Documentation Review

`CLAUDE.md` contains a "Known issues / in-progress" section with one entry:
- `link` resolves nodes by title; fuzzy/id lookup is on the roadmap but not yet started

There is no specific entry for CART-B01 (mkdirSync bug), so no documentation update is required for acceptance criterion #6.

---

## Success Metrics

- All three gate commands exit with status 0
- All 31 unit tests pass, including the CART-B01 regression guard
- No TypeScript compilation errors
- No lint errors
- Code review confirms static import and synchronous function implementation

---

## Next Steps

After plan approval:
1. Run gate commands to produce verification evidence
2. Document results in PROGRESS.md
3. Confirm all acceptance criteria are met
4. Mark task as complete