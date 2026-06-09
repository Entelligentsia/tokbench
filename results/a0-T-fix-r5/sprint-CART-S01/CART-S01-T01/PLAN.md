# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that the static import fix for `mkdirSync` in `src/store/graph.ts` is correctly implemented and that all gate commands pass, confirming the bug fix for CART-B01 is complete and the sprint acceptance criteria are satisfied.

## Approach

The fix has already been applied to the working tree. This task focuses on verification and validation:

1. **Code verification**: Confirm that `src/store/graph.ts` has `mkdirSync` in the top-level static import from `"fs"` and that `save()` is a plain synchronous function with no `await` expressions.

2. **Gate execution**: Run the three required gate commands to validate the fix:
   - `npm run build` (TypeScript compilation)
   - `npm test` (Vitest test suite, including regression guard)
   - `npm run lint` (ESLint static analysis)

3. **Documentation update**: Remove or mark as resolved any "Known issues" entry for this bug in `CLAUDE.md`.

4. **Acceptance validation**: Confirm all acceptance criteria from the task prompt are met.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verify existing fix | Ensure `mkdirSync` is statically imported and `save()` has no `await` |
| `CLAUDE.md` | Update known issues | Remove or mark resolved any entry for CART-B01 |

## Data Model Changes

None. This is a bug fix to existing code with no schema or data model changes.

## Testing Strategy

- **Syntax check**: `npm run build` — TypeScript compilation must exit 0 with no errors
- **Unit tests**: `npm test` — All 31 tests must pass, including the CART-B01 regression guard
- **Lint check**: `npm run lint` — ESLint must exit 0 with no warnings or errors
- **Regression guard**: The test in `src/store/graph.test.ts` verifies that `mkdirSync` is called before `writeFileSync` in the `save()` function

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement
- [ ] `save()` contains no `await` keyword
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — all 31 tests pass, including the regression guard
- [ ] `npm run lint` exits 0
- [ ] CLAUDE.md known issues section is updated (CART-B01 entry removed or marked resolved)

## Operational Impact

- **Version bump required:** No — This is a bug fix with no breaking changes
- **Migration entry required:** No — No schema or data model changes
- **Security scan required:** No — No changes to Forge tooling or security-sensitive code
- **Schema change:** No — No changes to `.forge/store/` or `.forge/config.json`

- **Distribution:** No user action required — fix is in source code only
- **Backwards compatibility:** Fully backwards compatible — no API or behavior changes beyond fixing the bug