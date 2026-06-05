# PROGRESS — CART-S01-T01: Fix mkdirSync static import and verify gates

## Summary of Changes

This task was a verification task rather than an implementation task. The fix for CART-B01 (mkdirSync static import) was already correctly implemented in the codebase. All acceptance criteria were verified and met.

### Files Verified

| File | Status | Notes |
|------|--------|-------|
| `src/store/graph.ts` | ✅ Verified | `mkdirSync` correctly imported via top-level `import { … } from "fs"` |
| `src/store/graph.test.ts` | ✅ Verified | Regression guard test validates mkdirSync call order before writeFileSync |
| `CLAUDE.md` | ✅ Verified | No CART-B01 entry exists in known issues section (criterion already met) |

### Key Findings

1. **Static Import Correct**: Line 2 of `src/store/graph.ts` contains:
   ```typescript
   import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
   ```
   This is the correct top-level static import pattern.

2. **save() is Synchronous**: The `save()` function (lines 12-16) contains no `await` keywords:
   ```typescript
   function save(graph: Graph): void {
     const dir = join(process.env.HOME ?? "~", ".cartographer");
     mkdirSync(dir, { recursive: true });
     writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
   }
   ```

3. **Regression Guard Present**: The test file `src/store/graph.test.ts` includes a comprehensive regression guard test that validates:
   - `mkdirSync` is called when `addNode()` is executed
   - `mkdirSync` is called BEFORE `writeFileSync` (order validation)

## Test Evidence

### Test Suite Results
```
> cartographer@0.1.0 test
> vitest run


 RUN  v1.6.1 /home/bench/forge-testbench/cartographer

 ✓ src/store/graph.test.ts  (6 tests) 9ms
 ✓ src/__tests__/graph.test.ts  (25 tests) 7ms

 Test Files  2 passed (2)
      Tests  31 passed (31)
   Start at  11:52:04
   Duration  221ms (transform 72ms, setup 0ms, collect 82ms, tests 16ms, environment 0ms, prepare 70ms)
```

### Build Results
```
> cartographer@0.1.0 build
> tsc
```
✅ Build completed successfully with no TypeScript errors.

### Lint Results
```
> cartographer@0.1.0 lint
> eslint src
```
✅ Lint completed successfully with no errors.

## Acceptance Criteria Status

- [x] `src/store/graph.ts` has `mkdirSync` in the top-level `import { … } from "fs"` statement
- [x] `save()` contains no `await` keyword
- [x] `npm run build` exits 0 with no TypeScript errors
- [x] `npm test` exits 0 — the regression guard passes (31 tests passed)
- [x] `npm run lint` exits 0
- [x] CLAUDE.md known issues section updated (no CART-B01 entry exists - criterion already met)

## Conclusion

All acceptance criteria have been verified and met. The fix for CART-B01 was already correctly implemented in the codebase. No code changes were required for this task - it was a verification task to ensure the fix was properly in place and all gates pass.

## Files Changed

No files were modified during this task. This was a verification-only task.