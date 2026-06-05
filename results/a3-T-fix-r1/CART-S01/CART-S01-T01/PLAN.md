# PLAN.md for CART-S01-T01

## Objective

Verify that the `mkdirSync` static import fix in `src/store/graph.ts` is correctly implemented and that all gate commands pass. The fix ensures `save()` is a synchronous function with proper directory creation before file write.

## Approach

This task is primarily a verification task. The code changes have already been applied to the working tree:

1. **Verify current state**: Confirm that `src/store/graph.ts` has the correct static import and synchronous `save()` implementation
2. **Run gate commands**: Execute the three required gate commands to validate the fix
3. **Address any remaining issues**: Fix any failures discovered during gate verification
4. **Update documentation**: Remove or mark resolved the known issue entry (if present)

## Files to Modify

Based on current investigation:

- `src/store/graph.ts` — **NO CHANGES NEEDED** (already correctly implemented)
- `CLAUDE.md` — **NO CHANGES NEEDED** (no known issue entry exists for CART-B01)

## Data Model Changes

None. The data model (Graph, Node, Edge) remains unchanged.

## Testing Strategy

The verification strategy relies on the three gate commands:

1. **TypeScript compilation**: `npm run build` — ensures no TS1308 errors and correct static imports
2. **Unit tests**: `npm test` — validates the regression guard for CART-B01 (mkdirSync called before writeFileSync)
3. **Linting**: `npm run lint` — ensures code quality standards are met

All three gates must pass with exit code 0.

## Acceptance Criteria

1. `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — **VERIFIED**
2. `save()` contains no `await` keyword — **VERIFIED**
3. `npm run build` exits 0 with no TypeScript errors — **VERIFIED**
4. `npm test` exits 0 — regression guard passes — **VERIFIED**
5. `npm run lint` exits 0 for `src/` directory — **VERIFIED**
6. Known issues entry for CART-B01 is removed or marked resolved — **N/A** (no entry exists)

## Operational Impact

- **Version bump**: not required (per task prompt)
- **Regeneration**: no user action needed
- **Security scan**: not required

## Implementation Notes

The fix has already been correctly implemented in the working tree:

- Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
- Lines 11-14: `save()` function is synchronous with `mkdirSync(dir, { recursive: true });` called before `writeFileSync()`

The regression guard test in `src/store/graph.test.ts` confirms the correct behavior by verifying that `mkdirSync` is called before `writeFileSync`.

## Risk Assessment

**Low risk**: This is a verification task for already-implemented fixes. The code changes are minimal and well-tested.

## Material Change Classification

**Not material**: This is a verification task for bug fixes that have already been applied. No new behavior changes are being introduced. The task prompt explicitly states "Version bump: not required".