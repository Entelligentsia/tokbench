# PLAN REVIEW — CART-S01-T01 (standalone review)

**Verdict: Approved**

## Summary

The plan verifies that the mkdirSync static import fix in `src/store/graph.ts` is correctly implemented and all gate checks pass. Independent verification confirms every claim in the plan is accurate.

## Detailed Findings

### 1. Correctness — ✅ Confirmed

**Actual code verified (not just the plan report):**

- **Line 2 of `src/store/graph.ts`:** `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — static import, single import statement, all four `fs` operations on one line.
- **`save()` function:** Fully synchronous — no `await` keywords present. `mkdirSync(dir, { recursive: true })` is called **before** `writeFileSync(DATA_PATH, ...)`, satisfying the CART-B01 regression requirement.
- **No dynamic `import()`** anywhere in the file — the previous bug (where `await import("fs")` appeared in a non-async function) is completely absent.

### 2. Testing — ✅ Confirmed

- **31/31 tests pass** (independently verified).
- **Two independent CART-B01 regression guards** exist:
  - `src/store/graph.test.ts` — `addNode() calls mkdirSync before writeFileSync` test using `invocationCallOrder` spy.
  - `src/__tests__/graph.test.ts` — `save()` → `calls mkdirSync before writeFileSync` + `always calls mkdirSync even when directory exists` + `calls mkdirSync with the correct directory path`.
- Mock patterns follow the required `vi.mock("fs", async (importOriginal) => { ... })` convention.

### 3. Build & Lint — ✅ Confirmed

- `npm run build` → exit 0, no TypeScript errors.
- `npm run lint` → exit 0, no linting errors.

### 4. Architecture Alignment — ✅

- Pure function exports from `graph.ts`; no class hierarchies, no singleton state.
- Flat `types.ts` interfaces (`Node`, `Edge`, `Graph`) are the single source of truth.
- `DATA_PATH` derived from `process.env.HOME ?? "~"` — consistent with architecture guardrails.
- `randomUUID()` from Node built-in `crypto` — no third-party UUID library.

### 5. Conventions — ✅

- ESM `.js` extension on relative import: `from "../types.js"` ✅
- No `.js` extensions on Node built-in imports (`"crypto"`, `"fs"`, `"path"`) — correct convention.
- `const` and arrow functions throughout; no `class` definitions.
- `strict: true` in tsconfig; no type-safety escapes.

### 6. Business Rules — ✅

- Edge `weight` hardcoded to `1` in `link()` — matches documented intent.
- Node lookup uses case-sensitive `title` matching — unchanged, per architecture decision.
- CLAUDE.md has no unresolved CART-B01 entry — confirmed.

### 7. Security — ✅ (no concerns for this scope)

- No auth changes, no input validation changes, no new surface area.

## Advisory Notes

- **Technical debt reminder:** The project has known debt items (no node update method, title-only lookup, no concurrency safety on read-modify-write). These are out of scope for this bug-fix task but should be tracked for future sprints.
- The PLAN.md was somewhat fragmented in its Markdown structure but the substance was correct and complete.

## Conclusion

The mkdirSync static import fix is correctly implemented, all tests pass, build and lint are clean, and the CART-B01 regression is properly guarded. No revision required.