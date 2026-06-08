# CART-S01-T01: Fix mkdirSync static import and verify gates

## Objective
Ensure `src/store/graph.ts` uses a static named import for `mkdirSync` (ESM) and verify that the guard tests (`mkdirSync` called before `writeFileSync`) are correctly mounted and validate the actual call path and ordering, not just runtime behavior. Fix and verify both sets of test mocks to ensure they pass consistently and protect against regressions.

## Approach
- Confirm and document that src/store/graph.ts uses `import { mkdirSync } from "fs"` (static named import, ESM) and does NOT contain any `await import("fs")` pattern.
- Validate that src/store/graph.test.ts mocks static named imports correctly so `vi.mocked(fs.mkdirSync)` works reliably; remove or simplify any fallback mocks that do not call the real implementation, if present.
- Validate that src/__tests__/graph.test.ts mocks static named imports correctly; remove or simplify any non-functional mocks if present.
- Run a negative verification (temporarily revert to a problematic import pattern) to prove that the gates fail when the staticNamed import is incorrect or the mocks are misconfigured, confirming the gates are effective.
- If any mismatches are found between the two test mocks or their assertions, standardize them to maintain consistent guard behavior across both suites.

## Files to Modify
- src/store/graph.ts (verify only; confirm static named import)
- src/store/graph.test.ts (verify and fix mocks if needed)
- src/__tests__/graph.test.ts (verify and fix mocks if needed)

## Data Model Changes
None. No schema or entity changes involved.

## Testing Strategy
- Run the full test suite (`npm test`) to ensure all tests pass.
- Run targeted tests for both suites: `npm test -- src/store/graph.test.ts` and `npm test -- src/__tests__/graph.test.ts`.
- Perform negative verification by temporarily changing the import pattern (e.g., using `await import("fs")`) or breaking the `mkdirSync` call and confirm that the gates fail and clearly indicate the regression.
- Restore correct static import and mocks; re-run tests to confirm all gates pass.
- Add a brief inline comment (if not already present) in src/store/graph.test.ts and src/__tests__/graph.test.ts to document the static import guard and ordering check.

## Acceptance Criteria
- src/store/graph.ts uses static named import: `import { mkdirSync } from "fs"`.
- Node tests run (`vitest run`) and all 31 tests pass.
- The guard test in src/store/graph.test.ts explicitly verifies `mkdirSync` is called before `writeFileSync` and correctly mounts static mocks for `mkdirSync`.
- The guard tests in src/__tests__/graph.test.ts also verify the `mkdirSync` call and ordering consistently.
- Negative verification confirms the gates fail when the import pattern is incorrect or mocks are misconfigured.
- No changes required to `package.json` or configuration; version bump not required.

## Operational Impact
- Not material: this is a code-only fix and verification to ensure correct static imports and prevent regressions. No user actions, regeneration, or security scans needed.
- Impact category: surface-change (guard improvements for existing behavior).

## Security/Safety Considerations
- Ensure `mkdirSync` is called with `{ recursive: true }`. The tests verify this is present.
- Avoid any dynamic imports in the save path to prevent TS1308/TS1378 errors and ensure reliability of static mocks.