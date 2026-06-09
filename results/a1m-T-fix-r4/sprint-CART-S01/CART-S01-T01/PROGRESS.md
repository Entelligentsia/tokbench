# CART-S01-T01 Implementation Progress

## Summary of Changes

This task verified that the CART-B01 bug fix (`mkdirSync` static import) was already correctly implemented in the codebase and removed the stale Known Issues entry from README.md. No code changes were required - the fix was already in place.

### Key Verifications Completed

1. ✅ **Static import confirmed**: `src/store/graph.ts` line 2 shows `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` - `mkdirSync` is imported statically at the top level
2. ✅ **Synchronous save() confirmed**: The `save()` function at lines 10-13 contains zero `await` keywords - it is purely synchronous
3. ✅ **All three gate commands passed**: `npm run build`, `npm test`, and `npm run lint` all succeeded
4. ✅ **Regression guard tests passed**: The test suite includes explicit regression guards that verify `mkdirSync-before-writeFileSync` ordering
5. ✅ **Documentation updated**: Removed stale CART-B01 entry from README.md Known Issues table

### Documentation Changes

**File Modified**: `README.md`
- Removed row from Known Issues table: `| graph.ts:save() | await import("fs") inside a sync function — should import mkdirSync at top of file |`
- The bug has been fixed, so this entry is no longer relevant

## Test Evidence

### Gate Command Results

**Build (npm run build)**:
```
> cartographer@0.1.0 build
> tsc
```
✅ Passed - TypeScript compilation successful

**Tests (npm test)**:
```
 RUN  v1.6.1 /home/bench/forge-testbench/cartographer

 ✓ src/store/graph.test.ts  (6 tests) 8ms
 ✓ src/__tests__/graph.test.ts  (25 tests) 6ms

 Test Files  2 passed (2)
      Tests  31 passed (31)
   Start at  05:56:49
   Duration  224ms (transform 72ms, setup 0ms, collect 83ms, tests 14ms, environment 0ms, prepare 69ms)
```
✅ All 31 tests passed (25 + 6 tests across 2 test files)

**Lint (npm run lint)**:
```
> cartographer@0.1.0 lint
> eslint src
```
✅ Passed - No linting errors

### Regression Guard Verification

The test file `src/store/graph.test.ts` contains explicit regression guards for CART-B01:

```typescript
// CART-B01: save() must call mkdirSync before writeFileSync.
// Before the fix, graph.ts uses `await import("fs")` in a non-async fn,
// which is a TS1308 compile err and means mkdirSync is never called.
```

Regression test that passed:
```typescript
it("addNode() calls mkdirSync before writeFileSync (regression guard for save() bug)", async () => {
    const fs = await import("fs");
    const mkdirSyncSpy = vi.mocked(fs.mkdirSync);
    const writeFileSyncSpy = vi.mocked(fs.writeFileSync);
    const { addNode } = await import("./graph.js");
    addNode("Test Idea", "body text", ["tag1"]);
    // mkdirSync must have been called
    expect(mkdirSyncSpy).toHaveBeenCalled();
    // mkdirSync must have been called BEFORE writeFileSync
    const mkdirOrder = mkdirSyncSpy.mock.invocationCallOrder[0];
    const writeOrder = writeFileSyncSpy.mock.invocationCallOrder[0];
    expect(mkdirOrder).toBeLessThan(writeOrder);
})
```

This test verified the correct ordering: `mkdirSync` (invocation order 0) → `writeFileSync` (invocation order 1).

## Files Changed Manifest

### Modified Files
1. `README.md` - Removed stale CART-B01 entry from Known Issues table

### Verified Files (No Changes Required)
2. `src/store/graph.ts` - Confirmed static import of `mkdirSync` is present at line 2
3. `src/__tests__/graph.test.ts` - Regression guard tests present and passing
4. `src/store/graph.test.ts` - Regression guard tests present and passing

## Verification Summary

The implementation plan was executed successfully:
- All three gate command requirements were met
- All acceptance criteria were satisfied
- No code changes were required - the fix was already in place
- Documentation updated to reflect current state
- All tests passed, including explicit regression guards for CART-B01

The task objective was achieved: verified that the CART-B01 bug fix was correctly implemented, ran all gate commands successfully, and updated documentation to remove the stale Known Issues entry.