# mkdirSync Static Import Fix and Gate Verification Guide

**Task:** CART-S01-T01 | **Sprint:** CART-S01  

This guide provides step-by-step instructions for verifying that the `fs` module functions (mkdirSync, readFileSync, writeFileSync, existsSync) are properly statically imported in `src/store/graph.ts`, confirming the `save()` function is synchronous, and running all quality gates to verify code health.

---

## Executive Summary

The bug `CART-B01` was a critical issue where `src/store/graph.ts` used `await import("fs")` in a non-async function, causing:
- TypeScript compilation error (TS1308)
- mkdirSync never being called before writeFileSync
- Runtime failures when `~/.cartographer` directory doesn't exist

The fix involves proper static ES module imports at the top of the file. This guide verifies the fix is in place and all quality gates pass.

---

## Background: Why This Matters

### The Original Bug

In the original broken code:
```typescript
// WRONG - This causes TS1308 error
async function load(): Promise<Graph> {
  const { readFileSync } = await import("fs");  // ← Top-level await
  // ...
}
```

But `load()` and `save()` were not declared async, so `await` caused:
1. TypeScript compilation failure (TS1308)
2. mkdirSync never executed because imports failed
3. Runtime crashes when `~/.cartographer` directory missing

### The Correct Approach

Static ES module imports:
```typescript
// CORRECT - Static import at top level
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";

function load(): Graph {
  // Can use readFileSync directly - no await needed
}

function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });  // ← This will execute
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```

---

## Prerequisites

- Node.js 20+ installed
- Project dependencies installed: `npm install`
- Read access to `src/store/graph.ts`
- Write access to `CLAUDE.md` (for documentation update)

---

## Verification Workflow

Follow these steps in order to verify the fix and document completion.

### Step 1: Verify Static Imports in `src/store/graph.ts`

**Action:** Inspect the imports at the top of `src/store/graph.ts`

**Command:**
```bash
head -5 src/store/graph.ts
```

**Expected Output:**
```typescript
import { randomUUID } from "crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import type { Graph, Node, Edge } from "../types.js";
```

**What to Verify:**
- ✅ Line 2 contains: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
- ✅ ALL fs functions are imported statically (no `await import("fs")`)
- ✅ Import is at module top level (not inside a function)
- ✅ No `await` keyword in the import statement

**If This Fails:**
The imports are incorrect. The file needs to be updated to use static imports. Follow the pattern above.

---

### Step 2: Verify `save()` Function is Synchronous

**Action:** Inspect the `save()` function implementation

**Command:**
```bash
grep -A 4 "^function save" src/store/graph.ts
```

**Expected Output:**
```typescript
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```

**What to Verify:**
- ✅ Function signature is `function save(graph: Graph): void` (returns void, not Promise)
- ✅ No `async` keyword in function declaration
- ✅ No `await` keyword anywhere in the function body
- ✅ `mkdirSync()` is called before `writeFileSync()` (line 3 before line 4)
- ✅ Synchronous fs functions are used (Sync variants)

**If This Fails:**
The function is not properly synchronous. It may be declared async or contain await statements.

---

### Step 3: Verify mkdirSync Executed Before WriteFileSync

**Action:** Confirm the call order in `save()` function

**Command:**
```bash
grep -n "mkdirSync\|writeFileSync" src/store/graph.ts | head -4
```

**Expected Output:**
```
2:import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
    (blank lines)
21:  mkdirSync(dir, { recursive: true });
22:  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
```

**What to Verify:**
- ✅ Line 21 contains `mkdirSync(dir, { recursive: true });`
- ✅ Line 22 contains `writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));`
- ✅ mkdirSync line number is GREATER THAN writeFileSync line number
- ✅ `recursive: true` option is passed to mkdirSync

**Why This Matters:**
If mkdirSync is not called before writeFileSync, the directory may not exist when writing the file, causing:
- `ENOENT: no such file or directory` error
- Data loss when first node is added
- Crash on first-time usage

**If This Fails:**
The directory creation logic is in the wrong order. mkdirSync must be called first.

---

### Step 4: Run TypeScript Build Gate

**Action:** Compile TypeScript to verify no compilation errors

**Command:**
```bash
npm run build
```

**Expected Output:**
```
> cartographer@0.1.0 build
> tsc

```

**What to Verify:**
- ✅ Command exits with code 0 (no error)
- ✅ Clean output (no error messages)
- ✅ `dist/` directory is created with compiled `.js` files

**If This Fails:**
There is a TypeScript compilation error. Common issues:
- TS1308: Top-level await issue (the original bug)
- Missing type annotations
- Import/export path errors

---

### Step 5: Run Test Suite Gate

**Action:** Execute all unit tests to verify behavior

**Command:**
```bash
npm test
```

**Expected Output:**
```
> cartographer@0.1.0 test
> vitest run


 RUN  v1.6.1 /home/bench/forge-testbench/cartographer

 ✓ src/store/graph.test.ts  (6 tests) 9ms
 ✓ src/__tests__/graph.test.ts (25 tests) 6ms

 Test Files  2 passed (2)
      Tests  31 passed (31)
   Start at  04:11:35
   Duration  233ms (transform 77ms, setup 0ms, collect 89ms, tests 15ms, environment 0ms, prepare 88ms)
```

**What to Verify:**
- ✅ All 31 tests pass (not fewer)
- ✅ Both test files succeed (`src/store/graph.test.ts` and `src/__tests__/graph.test.ts`)
- ✅ No tests skipped or failed
- ✅ Test duration completes (does not hang)

**Key Tests Related to This Fix:**
- `save() calls mkdirSync before writeFileSync`
- `addNode() calls mkdirSync before writeFileSync (regression guard)`
- `CART-B01: mkdirSync called before writeFileSync in save()`

**If This Fails:**
One or more tests are failing. Check:
- mkdirSync is being called at all
- Call order is correct
- Directory path is correct
- Mock functions in tests are properly configured

---

### Step 6: Run Lint Gate

**Action:** Execute ESLint static analysis

**Command:**
```bash
npm run lint
```

**Expected Output:**
```
> cartographer@0.1.0 lint
> eslint src

```

**What to Verify:**
- ✅ Command exits with code 0 (no errors)
- ✅ Clean output (no error messages or warnings)
- ✅ No files flagged for code quality issues

**If This Fails:**
ESLint found code quality issues. Common problems:
- Unused variables or imports
- Missing semicolons
- Inconsistent quotes
- Missing type annotations

---

### Step 7: Verify Implementation Details (Deep Dive)

**Action:** Complete inspection of the entire `save()` function context

**Command:**
```bash
sed -n '18,23p' src/store/graph.ts
```

**Expected Output:**
```typescript
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```

**What to Verify:**
- ✅ Function is NOT async
- ✅ Return type is `void` (not `Promise<void>`)
- ✅ Uses `join()` from "path" for directory path construction
- ✅ Directory path is `~/.cartographer` (with fallback for missing HOME env var)
- ✅ mkdirSync uses `recursive: true` to create parent directories if needed
- ✅ writeFileSync writes pretty-printed JSON (spacing: 2)

---

### Step 8: Update CLAUDE.md Documentation

**Action:** Update the known-issues section to reflect the fix

**Current CLAUDE.md known-issues section:**
```markdown
## Known issues / in-progress

- `link` resolves nodes by title; fuzzy/id lookup is on the roadmap but not yet started
```

**Action:** Add note about mkdirSync static import being correct

**Command to edit CLAUDE.md:**
```bash
# The known-issues section should now read:
```

**Expected Updated Section:**
```markdown
## Known issues / in-progress

- `link` resolves nodes by title; fuzzy/id lookup is on the roadmap but not yet started
- ~~mkdirSync static import issue~~ — Fixed: `fs` module functions are statically imported at top of `src/store/graph.ts`, `save()` is synchronous, all gates pass (build, test, lint)
```

**What to Verify:**
- ✅ The original known-issue (if present) is either removed or marked as fixed
- ✅ The note indicates all gates now pass
- ✅ The timeline of the fix is documented (if desired)

---

## Summary Checklist

Complete this checklist to confirm all verification steps:

- [ ] ✅ Static imports from "fs" at top of `src/store/graph.ts`
- [ ] ✅ No top-level await or dynamic import statements
- [ ] ✅ `save()` function is synchronous (no async/await)
- [ ] ✅ `mkdirSync()` called before `writeFileSync()` in correct order
- [ ] ✅ `npm run build` passes (TypeScript compiles)
- [ ] ✅ `npm test` passes (all 31 tests)
- [ ] ✅ `npm run lint` passes (ESLint clean)
- [ ] ✅ CLAUDE.md updated to reflect fix status
- [ ] ✅ No regression in test coverage
- [ ] ✅ Documentation accurately reflects current state

---

## Troubleshooting

### Build Fails with TS1308

**Symptom:** TypeScript reports await error like:
```
src/store/graph.ts(18,12): error TS1308: 'await' expression is only allowed within an async function.
```

**Cause:** Original bug - still using dynamic import

**Fix:** Replace `await import("fs")` with static import at top of file:
```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```

---

### Tests Fail with "mkdirSync not called"

**Symptom:** Test output shows mkdirSpy not called:

```
Expected mock function to have been called, but it was not called.
```

**Cause:** Directory creation logic not executing

**Fix:** Verify:
1.mkdirSync is part of static imports
2.mkdirSync is called in save() before writeFileSync
3.save() is not declared async (which would change return behavior)

---

### Test Suite Hangs Times Out

**Symptom:** `npm test` doesn't complete, appears frozen

**Cause:** Async function using await incorrectly

**Fix:** Check for await statements in non-async functions, especially in save() or load()

---

### Lint Reports Unused Imports

**Symptom:** ESLint flags imported fs functions as unused

**Cause:** Imports not being used or replaced with dynamic imports

**Fix:** Verify all fs functions are actually called in the code, not shadowed by dynamic imports

---

## Verification Commands Reference

Quick reference for all run-once verification commands:

```bash
# Step 1: Check static imports
head -5 src/store/graph.ts

# Step 2: Check save() signature
grep -A 4 "^function save" src/store/graph.ts

# Step 3: Verify call order
grep -n "mkdirSync\|writeFileSync" src/store/graph.ts | head -4

# Step 4: Build gate
npm run build

# Step 5: Test gate
npm test

# Step 6: Lint gate
npm run lint

# Step 7: Deep dive save() implementation
sed -n '18,23p' src/store/graph.ts

# Step 8: Update CLAUDE.md (manual edit)
```

---

## Related Files

- **Source:** `src/store/graph.ts` — Implementation file being verified
- **Tests:** `src/store/graph.test.ts` — Unit tests with mkdirSync call order checks
- **Tests:** `src/__tests__/graph.test.ts` — Integration tests with mock verification
- **Docs:** `CLAUDE.md` — Project documentation with known-issues section
- **Bug:** `CART-B01` — Original bug report about mkdirSync not being called

---

## Next Steps After Verification

Once all gates pass and documentation is updated:

1. Mark task as `completed` in the Forge store
2. Request Architect sign-off
3. Commit changes with message: "Fix CART-B01: Use static fs imports in graph.ts"
4. Update sprint progress
5. Close related bug in bug tracker

---

## Contact

For questions about this verification process or the original bug, refer to:
- Sprint CART-S01 task breakdown
- Bug CART-B01 details
- cartographer Architect persona guidance

---

**Last Updated:** During CART-S01-T01 execution  
**Status Verification:** All gates should pass after correct static import fix