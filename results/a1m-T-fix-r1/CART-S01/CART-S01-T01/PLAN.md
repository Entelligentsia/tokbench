# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via static top-level import from `"fs"` and that `save()` is a synchronous function with no `await` expressions. Run the full gate suite (build, test, lint) to confirm all acceptance criteria are satisfied and update documentation.

## Approach

The code changes for this task appear to already be in place in the working tree. The primary work is verification:

1. **Code verification**: Confirm that `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement and that `save()` contains no `await` keyword
2. **Gate execution**: Run the three required gate commands (`npm run build`, `npm test`, `npm run lint`) to verify the fix is correct
3. **Documentation update**: Update or remove the "Known issues" entry in `CLAUDE.md` once all gates are green

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verification only | Already has correct static import and synchronous save() implementation |
| `CLAUDE.md` | Update known-issues section | Remove or mark resolved any entry related to this bug once gates are green |

## Data Model Changes

None. This task does not modify the entity model, data structures, or persistence format.

## Testing Strategy

- **Syntax check**: `npm run build` (TypeScript compilation) — must exit 0 with no errors
- **Unit tests**: `npm test` (vitest) — must exit 0 with all 31 tests passing, including the regression guard for mkdirSync call order
- **Lint check**: `npm run lint` (eslint) — must exit 0 with no linting errors
- **Regression guard**: The existing test in `src/store/graph.test.ts` verifies that `mkdirSync` is called before `writeFileSync` in the `save()` function

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere
- [ ] `save()` contains no `await` keyword
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes
- [ ] `npm run lint` exits 0
- [ ] The "Known issues" entry for this bug in `CLAUDE.md` is removed or marked resolved

## Operational Impact

- **Version bump required:** No — this is a bug fix to existing functionality with no API changes
- **Migration entry required:** No — no data model or schema changes
- **Security scan required:** No — no changes to forge tools or security-sensitive code
- **Schema change:** No — no changes to `.forge/store/` or `.forge/config.json`
- **Distribution:** No user action required — this is an internal code fix
- **Backwards compatibility:** Fully compatible — no breaking changes to existing functionality