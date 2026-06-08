# Fix mkdirSync static import and verify gates

**Sprint:** `CART-S01`  
**Task:** `CART-S01-T01`  
**Generated:** `2025-06-08`

---

## Objective

Remove static import of `mkdirSync` from `src/store/graph.ts` and verify that all pre-flight and post-phase gates function correctly across the Forge pipeline.

## Approach

### 1. Data Model Changes
None. The change affects only the import style; no GraphQL/RPC/DB schema is touched.

### 2. Files to Modify
- `src/store/graph.ts` — replace static import of `mkdirSync` with dynamic import from `node:fs` in the `save()` function.

### 3. Implementation Strategy
- Remove `mkdirSync` from the static import line in `src/store/graph.ts`
- In `save()`, add a dynamic import: `const { mkdirSync } = await import('node:fs')`
- Call `mkdirSync` immediately to maintain the same execution order (mkdir before write)
- Keep the `readFileSync`, `writeFileSync`, `existsSync` static imports untouched; they are consumed synchronously at module scope and are not problematic in .cjs tool execution.

### 4. Testing Strategy
- Verify existing tests pass: `npm test` (or `vitest run`) — all 31 tests should continue to pass
- Verify the mkdirSync-before-writeFileSync ordering still holds: the existing assertions in `src/store/graph.test.ts` will confirm this
- If new tests are added: ensure the dynamic import does not introduce an unexpected async shape somewhere not expecting promises

### 5. Acceptance Criteria
- `src/store/graph.ts` contains no static import of `mkdirSync`
- `src/store/graph.ts` imports `mkdirSync` via dynamic `'node:fs'` import in `save()`
- All existing tests pass (no regressions)
- `src/store/graph.ts` exports `save` synchronously (the dynamic import yields immediately because `node:fs` is built-in)

### 6. Operational Impact Categories
- **RISK CATEGORY:** `performance` (negligible impact — dynamic import of built-in `node:fs` is essentially zero overhead)
- **RISK CATEGORY:** `surface-change` (none; `save()` signature and behavior remain unchanged)
- **RISK CATEGORY:** `data-loss` (none; the change preserves the mkdir-sync-before-write order and idempotency)
- **RISK CATEGORY:** `breaking-change` (none; this is an internal implementation detail)

## Materials Used (Optional)
- `src/store/graph.ts` — current implementation
- `src/store/graph.test.ts` — existing regression guard and ordering tests