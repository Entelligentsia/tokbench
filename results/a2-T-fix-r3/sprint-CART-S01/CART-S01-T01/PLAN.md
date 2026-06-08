# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Confirm that "fs" module functions (mkdirSync, readFileSync, writeFileSync, existsSync) are statically imported at the top of `src/store/graph.ts` without top-level await, verify that the `save()` function is synchronous (no await), and run all gates (build, test, lint) to verify they pass. Update CLAUDE.md known-issues entry once gates are green.

## Approach

1. **Verify current code state**: Inspect `src/store/graph.ts` imports and `save()` function to confirm:
   - Static imports from "fs" at module top level
   - No top-level await or dynamic import statements
   - `save()` function signature is `function save(graph: Graph): void` (synchronous)
   - `save()` calls `mkdirSync()` before `writeFileSync()` in the correct order

2. **Run all gates**: Execute the standard project gate commands to verify green status:
   - `npm run build` → TypeScript compilation succeeds
   - `npm test` → All 31 tests pass (both test suites)
   - `npm run lint` → ESLint passes with no errors

3. **Update CLAUDE.md**: Remove or update the known-issues entry related to this bug once all gates pass. The existing CLAUDE.md contains minimal known-issues content; we will ensure it accurately reflects current state.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `CLAUDE.md` | Remove/update known-issues entry (if any exists for this bug) | Reflect that mkdirSync static import and save() gates are now green |

**No changes to `src/store/graph.ts` are required** — the expected static imports are already in place and the `save()` function is correctly synchronous.

## Plugin Impact Assessment

- **Version bump required?** No — Documentation-only change to CLAUDE.md
- **Migration entry required?** No — No schema changes
- **Security scan required?** No — No changes to `.forge/` tooling
- **Schema change?** No — No data model changes

## Testing Strategy

- **Syntax check**: `node --check src/store/graph.ts` (already covered by `npm run build`)
- **Gate verification**: Run all three gates sequentially and capture output
- **Test suite verification**: Confirm 31 tests pass across both test files
- **Lint verification**: Confirm ESLint exits with no errors
- **Manual verification**: Inspect `src/store/graph.ts` to verify:
  - Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
  - Line 20-23 in `save()`: `mkdirSync()` called before `writeFileSync()`
  - No `await` keyword anywhere in `save()` function

## Acceptance Criteria

- [ ] `npm run build` completes successfully with no TypeScript errors
- [ ] `npm test` reports "31 passed" across both test files
- [ ] `npm run lint` completes with no errors
- [ ] `src/store/graph.ts` contains static import: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
- [ ] `save()` function is synchronous: `function save(graph: Graph): void` with no await
- [ ] CLAUDE.md is updated to reflect that mkdirSync static import is correct and gates are green
- [ ] No regression in existing test coverage

## Operational Impact

- **Distribution:** None — This is a documentation update confirming existing correct behavior
- **Backwards compatibility:** No impact — No code behavior changes