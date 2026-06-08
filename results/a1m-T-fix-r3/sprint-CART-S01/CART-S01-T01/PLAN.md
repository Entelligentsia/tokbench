# PLAN.md

## Objective

Verify that the CART-B01 save() bug fix is correctly implemented by confirming that `mkdirSync` is statically imported from `"fs"` at the top of `src/store/graph.ts`, the `save()` function has no `await` statements, and all quality gates (build, test, lint) pass. Update CLAUDE.md known-issues entry once verification is complete.

## Approach

This is a verification-focused task with no code modifications. The approach is:

1. **Manual Code Review**: Examine `src/store/graph.ts` to confirm:
   - Line 2 contains `import { mkdirSync } from "fs";` (static import at module top level)
   - The `save()` function declaration explicitly uses `fn save(graph: Graph): void` (non-async)
   - The function body contains no `await` keywords before `mkdirSync` or `writeFileSync`

2. **Automated Verification**: Execute the three quality gates:
   - `npm run build` — TypeScript compilation must complete without errors
   - `npm test` — All 31 tests must pass, including the CART-B01 regression guard in `src/store/graph.test.ts`
   - `npm run lint` — ESLint must report no errors or warnings

3. **Documentation Update**: Update CLAUDE.md to reflect successful verification

## Files to Modify

| File | Modification Type | Rationale |
|------|-------------------|-----------|
| `CLAUDE.md` | Documentation update | Add note about CART-S01-T01 successful verification |

**Note**: `src/store/graph.ts` requires no modifications — the static import and absence of `await` are already correctly implemented.

## Data Model Changes

None. This is a verification task with no data model changes.

## Testing Strategy

### Pre-Existing Tests to Maintain

- **CART-B01 Regression Guard** (`src/store/graph.test.ts`):
  - Test suite: `graph — CART-B01: mkdirSync called before writeFileSync in save()`
  - Test case: `addNode() calls mkdirSync before writeFileSync (regression guard for save() bug)`
  - Purpose: Ensures `mkdirSync` is called before `writeFileSync` and in the correct order
  - Current status: Passing (verified via `npm test`)

### Test Execution matrix

| Gate | Command | Expected Result |
|------|---------|-----------------|
| Build | `npm run build` | TypeScript compiles to `dist/` without errors |
| Test | `npm test` | All 31 tests pass (6 from `graph.ts`, 25 from `graph.test.ts`) |
| Lint | `npm run lint` | ESLint reports no errors or warnings |

## Acceptance Criteria

1. ✓ `src/store/graph.ts` line 2 contains: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
2. ✓ The `save()` function signature is: `fn save(graph: Graph): void` (not `async`)
3. ✓ No `await` keywords appear in the `save()` function body
4. ✓ `npm run build` completes with exit code 0
5. ✓ `npm test` reports 31 tests passing with 0 failures
6. ✓ `npm run lint` completes with exit code 0 (no errors, no warnings)
7. CLAUDE.md is updated to reflect successful verification

## Operational Impact

### Material Change Assessment

This task is **NOT material**:
- No bug fixes to command/hook/tool spec/workflow
- No changes to generated tool behaviour
- No command file behaviour changes
- No hook changes
- No schema changes to `.forge/store/` or `.forge/config.json`
- Documentation-only changes (CLAUDE.md update)

Impact category: None (verification-only task)

### Deployment Considerations

- No deployment required (verification task)
- Binary `carto` in `dist/` remains unchanged
- No runtime impact

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CI/CD pipeline may fail if configured differently than local test run | Low | Manual verification of all three gates locally |
| CLAUDE.md update may conflict with concurrent edits | Low | This is a single-sprint task; no concurrent activity expected |
| Awaiting gates may time out | Very Low | Gates run quickly (<1 second combined) |

## References

- **Bug Report**: CART-B01 (implicitly referenced in test comments)
- **Regression Guard**: `src/store/graph.test.ts` lines 13-23
- **Code Under Verification**: `src/store/graph.ts` lines 1-13
- **CART-S01 Sprint Manifest**: `engineering/sprints/CART-S01/INDEX.md`