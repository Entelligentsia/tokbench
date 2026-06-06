# PROGRESS — CART-S01-T01: Fix mkdirSync static import and verify gates

## Summary of Changes

This task was primarily a **verification pass** — the static-import fix and synchronous `save()` were already present in the working tree. The implementation phase confirmed correctness of the fix and ran all acceptance gates.

### Step 1 — Static-import audit (`src/store/graph.ts`)

Verified that `src/store/graph.ts` already satisfies all acceptance criteria:

- **Line 2:** `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
  — single static top-level import; no `await import("fs")` anywhere in the file.
- **`save()` body:** Synchronous function (no `async`, no `await`); calls `mkdirSync(dir, { recursive: true })` before `writeFileSync(DATA_PATH, …)`.

No code changes required.

### Step 2 — CLAUDE.md cleanup

Inspected the `## Known issues / in-progress` section of `CLAUDE.md`.  
No CART-B01 / `mkdirSync` / `save()` bullet was present — confirmed no-op as anticipated by the plan.

### Step 3 — Gate suite

All three gates exited 0 with zero errors or violations:

```
npm run build   → tsc → exit 0 (zero TypeScript errors)
npm test        → vitest run → exit 0 (31 tests, 2 test files)
npm run lint    → eslint src → exit 0 (zero ESLint violations)
```

---

## Test Evidence

### `npm run build` (tsc)

```
> cartographer@0.1.0 build
> tsc
```

Exit 0. No output = no errors.

### `npm test` (vitest run)

```
> cartographer@0.1.0 test
> vitest run

 RUN  v1.6.1 /home/bench/forge-testbench/cartographer

 ✓ src/store/graph.test.ts  (6 tests) 9ms
 ✓ src/__tests__/graph.test.ts  (25 tests) 6ms

 Test Files  2 passed (2)
      Tests  31 passed (31)
   Start at  01:52:33
   Duration  226ms (transform 76ms, setup 0ms, collect 87ms, tests 15ms, environment 0ms, prepare 72ms)
```

The CART-B01 regression guard in `src/store/graph.test.ts` passed — `mkdirSync` called before `writeFileSync` confirmed.

### `npm run lint` (eslint src)

```
> cartographer@0.1.0 lint
> eslint src
```

Exit 0. No output = zero violations.

---

## Files Changed

| File | Change |
|------|--------|
| `src/store/graph.ts` | No changes — already correct (static import + synchronous `save()`) |
| `CLAUDE.md` | No changes — no stale CART-B01 bullet present |

No source files were modified during this implementation phase.

---

## Acceptance Criteria Verification

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `graph.ts` imports `mkdirSync` in static top-level `import { … } from "fs"` | ✅ confirmed |
| 2 | `save()` body contains no `await` keyword | ✅ confirmed |
| 3 | `npm run build` exits 0 — zero TypeScript errors | ✅ passed |
| 4 | `npm test` exits 0 — all 31 tests pass incl. CART-B01 guard | ✅ passed |
| 5 | `npm run lint` exits 0 — zero ESLint violations | ✅ passed |
| 6 | `CLAUDE.md` has no bullet for `save()` / mkdirSync bug | ✅ confirmed |
