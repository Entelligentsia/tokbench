# ARCHITECT APPROVAL — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Summary
Verification-only task confirming three core claims about `src/store/graph.ts`:
1. `mkdirSync` is a top-level static import from `"fs"` — no dynamic import, no lazy require.
2. `save()` is fully synchronous (`void` return, no `async`/`await`) — no event-loop yield on write.
3. `mkdirSync(dir, { recursive: true })` is called before `writeFileSync`, guaranteeing directory creation precedes file write.

No source code changes were required or made.

## Architectural Assessment
- **Architecture alignment**: ✅ The verified behavior aligns with the project's offline-only, synchronous persistence model documented in `engineering/architecture/stack.md`.
- **Cross-cutting concerns**: ✅ None — no modules were modified.
- **Operational impact**: ✅ None — no deployment changes, no migrations, no breaking changes.
- **Data safety**: ✅ The `mkdirSync` → `writeFileSync` ordering prevents the directory-not-found failure mode that CART-B01 originally addressed. The regression guard test (`CART-B01`) uses `mock.invocationCallOrder` to enforce strict ordering.
- **Technical debt note**: The `save()` function lacks error handling for write failures (disk full, permission denied). This is a pre-existing concern and out of scope for this task, but worth noting for a future sprint.

## Deployment Notes
No deployment action required. No code was changed.

## Follow-up Items
1. **Error handling in `save()`**: Add try/catch or error propagation for `writeFileSync` failures (disk full, permission denied).
2. **Concurrency safety**: The known-issue "no concurrency safety on read-modify-write" remains — concurrent `addNode`/`link` calls could corrupt `graph.json`.
3. **Unused dependencies**: `enquirer` and `lowdb` remain in `package.json` but are unused in source code.

**Verdict:** Approved