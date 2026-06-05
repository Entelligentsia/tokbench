# PLAN REVIEW — CART-S01-T01 (standalone review)

**Reviewer:** cartographer Supervisor (oracle persona)

## Verdict: ✅ Approved

The plan is correct, complete, and achievable. The fix it describes is already in place and all gates pass.

---

## 1. Correctness

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `mkdirSync` is a top-level static import | ✅ Verified | Line 2 of `src/store/graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` |
| `save()` is synchronous — no `await` | ✅ Verified | `save()` uses `mkdirSync` and `writeFileSync`; no `await` keyword anywhere in the function |
| No vestigial `await import("fs")` in production code | ✅ Verified | `grep -n "await import" src/store/graph.ts` returns nothing |
| `npm run build` exits 0 | ✅ Verified | Build completes cleanly |
| `npm test` exits 0 | ✅ Verified | 31 tests pass (6 in graph.test.ts, 25 in __tests__/graph.test.ts) |
| `npm run lint` exits 0 | ✅ Verified | Lint passes cleanly |
| CLAUDE.md known issues updated for CART-B01 | ✅ N/A | No CART-B01 entry exists in CLAUDE.md to mark resolved; no tracked bug CART-B01 in the store |

## 2. Security

- No security concerns. `save()` uses `mkdirSync(dir, { recursive: true })` which is safe against path traversal given the `HOME`-based path. No user input reaches `mkdirSync` arguments directly.

## 3. Architecture

- The fix aligns with the project's stated architecture: `graph.ts` exports pure functions, no classes, no singleton state. Static imports are the correct pattern for ESM modules with synchronous consumers.

## 4. Conventions

- Import style matches project convention: top-level `import { … } from "fs"` with explicit `.js` extensions for intra-project imports.
- The regression guard test in `src/store/graph.test.ts` follows vitest conventions correctly (vi.mock, vi.fn, mock.invocationCallOrder).

## 5. Business Rules

- No business domain rules affected. This is a pure infrastructural bug fix (import method).

## 6. Testing

- The regression guard test (`mkdirOrder < writeOrder`) directly validates the core bug: that `mkdirSync` runs before `writeFileSync`. This is a targeted, effective test.
- Additional tests for `removeNode`, `listNodeTitles` provide coverage for the data flow through `save()`.

## 7. Advisory Notes

1. **CART-B01 reference**: The task and test comments reference a bug `CART-B01`, but no such bug exists in the Forge store. Consider adding a bug record for traceability, or updating the test comment to reference the task ID instead.
2. **CLAUDE.md stale reference**: The known issues section says persistence is "via `lowdb`" but the actual implementation uses custom `load`/`save` functions. This is a pre-existing inaccuracy, not part of this plan, but worth noting.
3. The plan's acceptance criteria are all verifiable via automated commands (`build`, `test`, `lint`) plus a single file inspection — this is a well-scoped, easy-to-validate plan.