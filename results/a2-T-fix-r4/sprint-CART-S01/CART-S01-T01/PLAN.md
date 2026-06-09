# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via static top-level import from `"fs"` and that `save()` is a plain synchronous function. Run the full gate suite (build, test, lint) to confirm the fix is correct, and update CLAUDE.md known-issues entry once all gates pass.

## Approach

This task focuses on verification rather than code modification. Based on preliminary inspection:

1. **Code verification**: Confirm that:
   - `mkdirSync` is included in the top-level `import { … } from "fs"` statement
   - `save()` contains no `await` keyword
   - `save()` calls `mkdirSync(dir, { recursive: true })` before `writeFileSync`

2. **Gate execution**: Run the three required gates:
   - `npm run build` — TypeScript compilation exits 0 with no errors
   - `npm test` — All tests pass, including CART-B01 regression guard
   - `npm run lint` — ESLint exits 0

3. **Documentation update**: Remove or mark as resolved any "Known issues" entry for CART-B01 in CLAUDE.md once gates are green

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verify existing static import includes `mkdirSync` | Ensure the TS1308 compile error is avoided and mkdirSync is available for synchronous use |
| `CLAUDE.md` | Remove or mark resolved CART-B01 known-issues entry | Complete the verification cycle by documenting resolution |

## Plugin Impact Assessment

- **Version bump required?** No — This is a internal verification and documentation update
- **Migration entry required?** No — No user-facing changes
- **Security scan required?** No — No changes to Forge plugin files
- **Schema change?** No — No changes to `.forge/store/` or `.forge/config.json`

## Testing Strategy

- **Syntax check**: Implicit via `npm run build` (TypeScript compilation)
- **Regression guard**: The existing test in `src/store/graph.test.ts` titled "CART-B01: mkdirSync called before writeFileSync in save()" verifies that `mkdirSync` is invoked before `writeFileSync` and in the correct order
- **Gate verification**: Run `npm run build`, `npm test`, and `npm run lint` sequentially — all must exit 0

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — confirmed via inspection
- [ ] `save()` contains no `await` keyword — confirmed via inspection
- [ ] `save()` calls `mkdirSync(dir, { recursive: true })` before `writeFileSync(DATA_PATH, …)` — confirmed via inspection and regression guard test
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 with all tests passing, including CART-B01 regression guard
- [ ] `npm run lint` exits 0 with no ESLint errors
- [ ] Any CART-B01 entry in CLAUDE.md "Known issues" section is removed or marked resolved

## Operational Impact

- **Distribution:** No user action required — this is internal verification only
- **Backwards compatibility:** No impact — no breaking changes introduced
- **Data loss risk:** None — this task only inspects and documents existing code