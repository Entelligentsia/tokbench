# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that the CART-B01 mkdirSync static import fix is correctly implemented in `src/store/graph.ts` and ensure all regression guard tests are functioning properly to prevent the bug from reoccurring.

## Approach

This task is primarily verification and documentation of an already-completed fix. The approach involves:

1. **Code verification**: Confirm the static import pattern is correct and matches TypeScript best practices
2. **Test execution**: Run all existing tests to confirm the CART-B01 regression guard functions properly
3. **Build validation**: Ensure TypeScript compilation succeeds without TS1308 errors
4. **Gate documentation**: Document the existing safeguards and their purpose

The fix involves changing from a problematic `await import("fs")` pattern in a non-async function to a proper static `import { mkdirSync, writeFileSync } from "fs"` declaration at the module level. This ensures `mkdirSync` is synchronously available when `save()` executes.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | **No modification required** - code is already correct | The static import `import { mkdirSync, writeFileSync, existsSync, readFileSync } from "fs"` is properly implemented at the module level. The `save()` function correctly calls `mkdirSync(dir, { recursive: true })` before `writeFileSync()`. |
| `src/store/graph.test.ts` | **No modification required** - regression guard is in place | The CART-B01 test suite verifies mkdirSync calling order and invocation count. |
| `src/__tests__/graph.test.ts` | **No modification required** - additional guards present | Comprehensive test coverage ensures directory creation behavior is correct. |

## Plugin Impact Assessment

- **Version bump required?** No — This is a bug fix verification task, no new functionality added
- **Migration entry required?** No — No data model or schema changes
- **Security scan required?** No — Changes are only to existing source files, no Forge tool modifications
- **Schema change?** No — No changes to `.forge/store/` or `.forge/config.json`

This change is **NOT material** per the project conventions — it fixes an existing bug but does not alter tool behavior, command outputs, or user-facing functionality.

## Testing Strategy

- **Unit test verification**: Run `npm test` — confirm 31 tests pass, specifically the CART-B01 regression guard tests
- **Build validation**: Run `npm run build` — verify TypeScript compilation succeeds with no TS1308 errors
- **Lint verification**: Run `npm run lint` — ensure code style compliance
- **Smoke test**: Run `npm run dev -- add "Test Node"` — confirm the CLI can successfully create nodes and the directory structure is created properly

## Acceptance Criteria

- [ ] Static import `import { mkdirSync, writeFileSync, existsSync, readFileSync } from "fs"` is verified in `src/store/graph.ts`
- [ ] All 31 unit tests pass, including CART-B01 regression guard tests
- [ ] TypeScript build completes without errors (`npm run build`)
- [ ] Linting passes without warnings (`npm run lint`)
- [ ] CART-B01 test file includes explicit comments documenting the bug and fix rationale
- [ ] Manual smoke test confirms node creation works and directory is properly created
- [ ] `node --check` passes on all modified JS/CJS files (none modified in this case)
- [ ] `node .forge/tools/validate-store.cjs --dry-run` exits 0 (no schema changes)

## Operational Impact

- **Distribution:** No user action required — this is an internal bug verification
- **Backwards compatibility:** Fully compatible — the fix ensures existing functionality works correctly, no API changes
- **Deployment:** No special deployment steps needed; the fix is already in place and verified

## Regression Prevention

The following safeguards prevent the CART-B01 bug from reoccurring:

1. **Test Guard**: `src/store/graph.test.ts` contains explicit CART-B01 tests that verify mkdirSync is called before writeFileSync
2. **TypeScript Compilation**: The static import pattern eliminates TS1308 compile errors that would have caught the issue
3. **Code Review**: The fix is well-documented in code comments explaining the bug history
4. **Multiple Test Suites**: Both `src/store/graph.test.ts` and `src/__tests__/graph.test.ts` contain overlapping tests for directory creation behavior

This verification task confirms that all safeguards are functioning correctly.