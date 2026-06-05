# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that the static import fix for `mkdirSync` is correctly implemented in `src/store/graph.ts`, confirm that `save()` is a synchronous function with no `await` expressions, and run the full gate suite to validate the fix and satisfy sprint acceptance criteria.

## Approach

This task is primarily a verification task rather than implementation. The code changes for the CART-B01 bug fix appear to already be in place in the working tree. The approach is to:

1. Verify the current state of `src/store/graph.ts` confirms the static import pattern
2. Confirm `save()` contains no `await` keywords
3. Run the three gate commands (`npm run build`, `npm test`, `npm run lint`)
4. Verify the regression guard test passes
5. Update CLAUDE.md to reflect the resolved issue (if a known issues entry exists)

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verify static import of `mkdirSync` | Ensure `mkdirSync` is imported via top-level `import { … } from "fs"` |
| `src/store/graph.test.ts` | Verify regression guard test exists | Confirm test validates `mkdirSync` is called before `writeFileSync` |
| `CLAUDE.md` | Update known issues section | Remove or mark resolved any entry for CART-B01 |

## Plugin Impact Assessment

- **Version bump required?** No — This is a bug fix to existing code, not a feature change
- **Migration entry required?** No — No schema or data structure changes
- **Security scan required?** No — No changes to forge/ directory or security-sensitive code
- **Schema change?** No — No changes to `.forge/store/` or `.forge/config.json`

## Testing Strategy

- Syntax check: `npm run build` (TypeScript compilation)
- Unit tests: `npm test` (vitest run — includes CART-B01 regression guard)
- Lint: `npm run lint` (eslint src)
- Manual verification: Inspect `src/store/graph.ts` to confirm static import pattern

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement
- [ ] `save()` contains no `await` keyword
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — the regression guard passes
- [ ] `npm run lint` exits 0
- [ ] CLAUDE.md known issues section updated (entry removed or marked resolved)

## Operational Impact

- **Distribution:** No user action required — this is an internal bug fix
- **Backwards compatibility:** Fully compatible — no breaking changes to data structures or CLI behavior