# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via static top-level import from `"fs"` and that `save()` is a plain synchronous function with no `await` expressions. Ensure all build, test, and lint gates pass.

## Approach

This is a verification task rather than a feature implementation. The current codebase already contains the correct implementation:

1. **Static import verification**: Confirm that `mkdirSync` is imported at the top level from `"fs"` module
2. **Synchronous function verification**: Confirm that `save()` function has no `await` expressions and is purely synchronous
3. **Gate verification**: Run all three gates (build, test, lint) and ensure they pass
4. **Export verification**: Ensure `save()` is properly exported for test access

The approach is to inspect the current implementation, run the verification gates, and document the findings.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | No changes needed - verification only | Code already has correct static import and synchronous implementation |
| `package.json` | No changes needed - verification only | Dependencies already include required packages |
| `eslint.config.js` | No changes needed - verification only | ESLint config already present |

## Plugin Impact Assessment

- **Version bump required?** No — This is a verification task with no functional changes
- **Migration entry required?** No — No data model or schema changes
- **Security scan required?** No — No changes to `forge/` directory
- **Schema change?** No — No changes to `.forge/store/` or `.forge/config.json`

## Testing Strategy

- **Syntax check**: `npm run build` — Verify TypeScript compilation succeeds
- **Unit tests**: `npm test` — Verify all tests pass, including `save()` regression tests
- **Lint check**: `npm run lint` — Verify no ESLint violations
- **Manual verification**: Inspect `src/store/graph.ts` to confirm:
  - Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
  - Line 12-15: `save()` function has no `await` keywords
  - Line 67: `export { load, save };` includes `save`

## Acceptance Criteria

- [ ] `src/store/graph.ts` imports `mkdirSync` via static top-level import from `"fs"`
- [ ] `save()` function contains no `await` expressions
- [ ] `save()` is exported from `src/store/graph.ts`
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 with all tests passing
- [ ] `npm run lint` exits 0 with no ESLint violations

## Operational Impact

- **Distribution:** No user action required — this is a verification task with no functional changes
- **Backwards compatibility:** No impact — no breaking changes to existing functionality