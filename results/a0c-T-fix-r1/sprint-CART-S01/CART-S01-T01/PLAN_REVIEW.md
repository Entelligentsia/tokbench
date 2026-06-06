# PLAN_REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

_(standalone review)_

**Verdict:** Approved

## Independent Verification

I read the actual files rather than relying on the plan's claims:

- **`src/store/graph.ts` line 2** — `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — confirmed single combined static import; no second import statement, no `await import("fs")`. ✓
- **`save()` body** — calls `mkdirSync(dir, { recursive: true })` before `writeFileSync`; `grep` for `await`/`async` across the file returns nothing. Function is plain synchronous. ✓
- **Regression guard** — `src/store/graph.test.ts` contains `describe("graph — CART-B01: mkdirSync called before writeFileSync in save()")` asserting both that `mkdirSync` was called and that its `invocationCallOrder` precedes `writeFileSync`. ✓
- **`CLAUDE.md` `## Known issues / in-progress`** — contains only the unrelated `link`/fuzzy-lookup bullet; no CART-B01/mkdirSync entry exists. Plan Step 2 is therefore a no-op, which the plan correctly anticipates ("If it is already absent, no change is needed"). ✓

## Assessment by Category

1. **Correctness** — The plan accurately characterizes the working-tree state as already-fixed and frames the implementation phase as a verification pass. This matches reality.
2. **Security** — N/A. Internal synchronous filesystem I/O fix; no auth, input, or injection surface. Correctly flagged not-material.
3. **Architecture** — No data-model or public-API change. `Graph`/`Node`/`Edge` types and `graph.json` schema untouched. Consistent with the offline-only, single-store design.
4. **Conventions** — The conditional "apply correction only if audit finds a violation" scoping is appropriate and avoids gratuitous edits.
5. **Testing** — Relies on the existing regression guard rather than authoring redundant tests. Sound; the guard already encodes the exact invariant (call + ordering).
6. **Completeness** — Three-gate suite (tsc / vitest / eslint) covers compile, behavior, and lint. Acceptance criteria are concrete and verifiable.

## Advisory Notes

- The plan correctly does not depend on CLAUDE.md edits being necessary; treat Step 2 as a confirmed no-op.
- Acceptance criterion #4 asserts "all 31 tests pass" — implementation should report the actual count from `vitest run` rather than hard-coding 31, in case the suite has grown.

No blocking issues. The plan is feasible, correctly scoped, and grounded in the actual tree state.
