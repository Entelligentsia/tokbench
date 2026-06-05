# PLAN_REVIEW.md for CART-S01-T01

**Review type:** Plan review (standalone review)
**Reviewer:** cartographer Supervisor (Oracle)

---

## Verdict: ✅ Approved

The plan is straightforward and correct. The fix for CART-B01 (static import of `mkdirSync` and synchronous `save()`) is already in place in the working tree. The plan correctly identifies this as a verification task and defines clear, testable acceptance criteria.

---

## Detailed Review

### 1. Correctness

- ✅ **AC1 verified independently**: `src/store/graph.ts` line 2 contains `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — `mkdirSync` is statically imported at the top level, not via `await import()`.
- ✅ **AC2 verified independently**: `save()` (lines 12–16) is a plain synchronous `function save(graph: Graph): void` with zero `await` expressions.
- ✅ **AC3 verified independently**: `npm run build` exits 0 with no TypeScript errors.
- ✅ **AC4 verified independently**: `npm test` exits 0 — 31 tests pass, including the CART-B01 regression guard confirming `mkdirSync` is called before `writeFileSync` in `save()`.
- ✅ **AC5 verified independently**: `npm run lint` exits 0.
- ✅ **AC6 verified independently**: CLAUDE.md "Known issues" section contains no CART-B01 entry. The only listed issue is about title-based node lookup, which is unrelated.

### 2. Security

No concerns. `mkdirSync(dir, { recursive: true })` is the correct, safe pattern for ensuring the data directory exists. No injection vectors introduced.

### 3. Architecture

The fix follows established project patterns:
- Single top-level ESM import from `"fs"` (extended, not duplicated) — matches task context guidance.
- `save()` remains a pure synchronous function — consistent with project convention of pure functions in `graph.ts`.

### 4. Conventions

All project conventions are followed:
- `.js` extensions in ESM imports ✅
- `const` / arrow function preference ✅
- No new classes or singletons ✅
- No database or network dependencies ✅

### 5. Business Rules

Offline-only design is preserved. No network or database dependencies introduced.

### 6. Testing

- The regression guard in `src/store/graph.test.ts` correctly verifies ordering: `mkdirSync` must be called before `writeFileSync`, using `mock.invocationCallOrder` — this is the right Vitest API for call-order assertions.
- All 6 tests in the CART-B01 suite pass, plus 25 more in the general graph test suite.

---

## Advisory Notes

1. **Plan confidence notation**: The PLAN.md marks all acceptance criteria as ✓ pre-verification. While this turned out to be accurate, it's slightly premature notation for a plan that hasn't been executed yet. Non-blocking.
2. **Bug record**: No bug record for CART-B01 was found in the Forge store (only CART-BUG-001 and CART-BUG-002 exist). This may be a pre-store bug or a naming convention difference. Non-blocking, but worth noting for traceability.