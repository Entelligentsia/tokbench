# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates 🌱
*cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

This plan verifies that the `mkdirSync` static import issue is resolved in `src/store/graph.ts` and confirms that all required gate checks pass, ensuring the bug fix for CART-B01 is complete and the sprint acceptance criteria are satisfied.

## Approach

1. **Verify code state**: Confirm that `src/store/graph.ts` has the corrected static import including `mkdirSync` and that `save()` is a plain synchronous function without `await` expressions.

2. **Run gate checks**: Execute the three required gates:
   - TypeScript compilation (`npm run build`)
   - Test suite (`npm test`) including the regression guard for `mkdirSync` call order
   - Linting (`npm run lint`)

3. **Update documentation**: Check and update `CLAUDE.md` known issues section if any reference to CART-B01 exists.

4. **Validate acceptance criteria**: Ensure all six acceptance criteria are satisfied before considering the task complete.

## Files to Modify

| File | Change | Reason |
|------|--------|--------|
| `src/store/graph.ts` | Verify existing static import includes `mkdirSync` | Ensure bug fix is present as specified |
| `CLAUDE.md` | Remove or mark CART-B01 entry as resolved (if present) | Update known issues documentation |

## Data Model Changes

None - this task is a verification task with no data model changes. The entities (Graph, Node, Edge) remain unchanged.

## Testing Strategy

- **Test suite execution**: Run `npm test` to verify all 31 tests pass, including the specific regression guard in `src/store/graph.test.ts` that confirms `mkdirSync` is called before `writeFileSync`
- **TypeScript compilation**: Run `npm run build` to verify no TS1308 errors and no `await` usage in synchronous contexts
- **Lint verification**: Run `npm run lint` to ensure code style compliance
- **Manual verification**: Inspect `src/store/graph.ts` to confirm the import statement and `save()` function implementation meet requirements

## Acceptance Criteria

1. ✅ `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement
2. ✅ `save()` contains no `await` keyword
3. ✅ `npm run build` (`tsc`) exits 0 with no TypeScript errors
4. ✅ `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes
5. ✅ `npm run lint` exits 0
6. ✅ The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved

## Operational Impact

- **Distribution**: No user action required - this is an internal bug fix verification
- **Backwards compatibility**: No impact - the fix corrects an existing bug that would have failed on first use when `~/.cartographer/` directory does not exist
- **Version bump**: Not required per task acceptance criteria
- **Regeneration**: No user action needed
- **Security scan**: Not required per task acceptance criteria