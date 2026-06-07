# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that the mkdirSync static import fix is correctly implemented in `src/store/graph.ts` and validate that all project gates (TypeScript build, tests, and lint) pass successfully. This task ensures the CART-B01 bug fix is complete and the project meets all quality standards.

## Approach

The fix for the mkdirSync import bug appears to already be in the codebase based on code inspection. The `save()` function already uses synchronous imports correctly and calls `mkdirSync` before `writeFileSync`. The primary work for this task is verification through gate commands rather than implementing new functionality.

The approach involves:
1. Code inspection to confirm the current state matches the fix requirements
2. Running the TypeScript compiler to verify no build errors
3. Running the test suite, specifically the CART-B01 regression guard test
4. Running the linter to ensure code quality standards are met
5. Updating CLAUDE.md known-issues section to reflect resolution

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Verification only - confirm static import is correct | Current code shows `mkdirSync` already in top-level import |
| `src/store/graph.test.ts` | Verification only - regression guard test passes | Test already validates mkdirSync is called before writeFileSync |
| `CLAUDE.md` | Update known-issues section | Remove or mark resolved any entry for CART-B01 bug |

## Plugin Impact Assessment

- **Version bump required?** No — This is a verification task for an existing bug fix, no user-facing changes
- **Migration entry required?** No — No schema or data structure changes
- **Security scan required?** No — No changes to forge/ directory or security-sensitive code
- **Schema change?** No — No changes to Forge schemas or config

## Testing Strategy

- **Syntax check**: `vitest run` - Full test suite execution including CART-B01 regression guard
- **TypeScript compilation**: `npm run build` - Verify no TS1308 or other build errors
- **Lint verification**: `npm run lint` - Confirm code meets ESLint standards
- **Manual verification**: Inspect src/store/graph.ts to confirm:
  - `mkdirSync` is in the top-level import statement
  - `save()` contains no `await` keyword
  - `mkdirSync` is synchronously called before `writeFileSync`

## Acceptance Criteria

- [ ] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement — not via `await import(…)` anywhere
- [ ] `save()` contains no `await` keyword
- [ ] `npm run build` (`tsc`) exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — the regression guard (`mkdirSync` called before `writeFileSync`) in `src/store/graph.test.ts` passes
- [ ] `npm run lint` exits 0
- [ ] The CLAUDE.md known-issues section is reviewed and updated if necessary

## Operational Impact

- **Distribution:** No — This is an internal verification task with no user-facing changes
- **Backwards compatibility:** Fully compatible — No API changes, only internal fix verification
- **Runtime behavior:** Correct — Ensures `~/.cartographer/` directory is created before first write, preventing ENOENT errors