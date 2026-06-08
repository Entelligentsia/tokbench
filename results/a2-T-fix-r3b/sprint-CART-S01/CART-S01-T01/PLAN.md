# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🌱 *cartographer Engineer*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Fix the malformed static import statements in `src/store/graph.ts` that are preventing compilation and verify that the save() function's mkdirSync usage is correct according to existing tests and gate validation.

## Approach

1. Fix the incomplete `import type` statement for Graph, Node, Edge interfaces by adding the correct module reference (`from "../types.js"`)
2. Verify all other import statements follow proper TypeScript ESM syntax
3. Ensure mkdirSync is correctly imported as a named import from "fs" 
4. Run all tests to confirm the fix resolves the syntax error without breaking existing functionality
5. Validate that build succeeds and test suite passes

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | Fix the `import type` statement to include proper module reference: `import type { Graph, Node, Edge } from "../types.js"` | The current import is incomplete, causing compilation failure |
| `src/store/graph.ts` | Verify mkdirSync import syntax is consistent with other fs imports | Ensure all fs module imports follow the same named import pattern |

## Data Model Changes

None. This is a syntax fix that does not alter the Graph, Node, or Edge data structures or their persistence schema.

## Testing Strategy

- Syntax check: `npx tsc --noEmit` to verify TypeScript compilation succeeds
- Test suite: `npm test` to run all existing tests (31 tests) and verify they pass
- Manual verification: Check that build completes successfully with `npm run build`
- Gate verification: Run preflight gate check to ensure no configuration issues block the workflow

## Acceptance Criteria

- [ ] TypeScript compilation succeeds without import/syntax errors
- [ ] All 31 existing tests pass (src/store/graph.test.ts and src/__tests__/graph.test.ts)
- [ ] Build succeeds: `npm run build` completes without errors
- [ ] save() function correctly imports and uses mkdirSync with recursive option
- [ ] Preflight gate check passes for subsequent phases

## Operational Impact

- **Distribution:** No distribution impact — this is an internal build fix only
- **Backwards compatibility:** Fully backwards compatible — no API or data format changes
- **Deployment:** Users will need to rebuild from source via `npm run build` after the fix is applied