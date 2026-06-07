# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

🗻 *cartographer Architect*

**Task:** CART-S01-T01
**Sprint:** CART-S01
**Estimate:** S

---

## Objective

Verify that the static import fix for `mkdirSync` is correctly implemented in `src/store/graph.ts` and confirm that all gate checks (build, test, lint) pass, ensuring the CART-B01 bug is resolved without requiring additional code changes.

## Approach

This task is primarily a verification task rather than an implementation task. The fix for the CART-B01 bug (static import of `mkdirSync` from `"fs"`) appears to already be in place in the working tree. The approach is:

1. Verify that `src/store/graph.ts` uses the correct static import pattern
2. Confirm that the `save()` function is synchronous with no `await` keywords
3. Execute the three gate commands sequentially:
   - `npm run build` (TypeScript compilation)
   - `npm test` (vitest tests including CART-B01 regression guard)
   - `npm run lint` (eslint checks)
4. Confirm that CLAUDE.md has no unresolved CART-B01 entry

No code changes are required if all verification steps pass.

## Files to Modify

| File | Change | Rationale |
|---|---|---|
| `src/store/graph.ts` | None (verification only) | Already contains correct static import and synchronous `save()` function |
| `CLAUDE.md` | None (verification only) | No CART-B01 entry currently exists; document if required |

 **Current State Verification** (from research):

- **Line 2** of `graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
  - `mkdirSync` is correctly imported via static top-level import
- **Lines 11-15** (the `save()` function):
  ```ts
  function save(graph: Graph): void {
    const dir = join(process.env.HOME ?? "~", ".cartographer");
    mkdirSync(dir, { recursive: true });
    writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
  }
  ```
  - Function signature is void (not async)
  - No `await` keywords present
  - `mkdirSync` is called before `writeFileSync`

## Testing Strategy

- **Syntax verification**: `npm run build` — confirms TypeScript compilation succeeds with no errors
- **Functional tests**: `npm test` — runs vitest suite; confirms CART-B01 regression guard passes (mkdirSync called before writeFileSync)
- **Code quality**: `npm run lint` — runs eslint to confirm code style compliance

## Acceptance Criteria

- [ ] `mkdirSync` is imported via static top-level `import { … } from "fs"` in `src/store/graph.ts`
- [ ] `save()` function contains no `await` keyword and is properly synchronous
- [ ] `npm run build` exits 0 with no TypeScript errors
- [ ] `npm test` exits 0 — all 31 tests pass, including the CART-B01 regression guard
- [ ] `npm run lint` exits 0 with no linting errors
- [ ] CLAUDE.md has no unresolved CART-B01 entry in "Known issues / in-progress" section

## Operational Impact

- **Version bump:** Not required — this is a bug fix that maintains the existing API and behavior
- **Regeneration:** No user action needed — no schema or interface changes
- **Security scan:** Not required — no changes to Forge's internal tooling or store schemas
- **Backwards compatibility:** Fully compatible — fixes a bug in the synchronous save behavior without changing the public API

## Notes

The risk noted in the task context — "the existing `import { readFileSync, writeFileSync, existsSync } from "fs"` line must be extended to include `mkdirSync` rather than adding a second import statement" — has been correctly addressed. The code uses a single import statement at line 2 that includes all required fs operations: `readFileSync`, `writeFileSync`, `existsSync`, and `mkdirSync`.

All three gate commands were successfully executed during planning, confirming the fix is already correct and the task can proceed to approval.