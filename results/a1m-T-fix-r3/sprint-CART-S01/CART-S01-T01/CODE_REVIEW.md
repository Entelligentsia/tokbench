# CODE_REVIEW.md — CART-S01-T01 (standalone review)

## Task
CART-S01-T01: Fix mkdirSync static import and verify gates

## Verdict: **Approved**

All six acceptance criteria independently verified against actual source code and live gate runs. No source changes were required — the fix was already in place; this task confirmed correctness.

---

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| AC1: `mkdirSync` in static top-level import | ✅ Passed | `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` — single import statement, `mkdirSync` included |
| AC2: `save()` contains no `await` keyword | ✅ Passed | `fn save(graph: Graph): void` — synchronous signature, zero `await` expressions in body |
| AC3: `npm run build` exits 0 | ✅ Passed | Independently re-run: `tsc` compiles cleanly to `dist/` with no errors |
| AC4: `npm test` exits 0 with regression guard | ✅ Passed | Independently re-run: 31/31 tests pass; CART-B01 regression guard asserts `mkdirSync` call order < `writeFileSync` call order |
| AC5: `npm run lint` exits 0 | ✅ Passed | Independently re-run: ESLint reports zero errors and zero warnings |
| AC6: CLAUDE.md known-issues cleaned | ✅ Passed | No CART-B01 entry in `## Known issues / in-progress` section |

---

## Correctness

- `save()` calls `mkdirSync(dir, { recursive: true })` on line 11 before `writeFileSync(DATA_PATH, ...)` on line 12 — the exact ordering the CART-B01 regression guard validates.
- `mkdirSync` uses `{ recursive: true }` which correctly handles nested directory creation, preventing write failures when `~/.cartographer/` doesn't exist.
- No second `import` statement for `fs` — the existing import was extended as required by the task prompt's risk note.

## Security

- Synchronous `fs` operations (`mkdirSync`, `writeFileSync`, `readFileSync`) are appropriate for an offline CLI tool. No async/await complexity, no TOCTOU race conditions (single-process tool).
- No user input reaches `DATA_PATH` or directory paths unsanitised — `DATA_PATH` is derived from `process.env.HOME` + constant suffix.
- No injection vectors identified.

## Architecture

- `save()` is a pure-ish function (`fn save(graph: Graph): void`) with no singleton, no global mutable state, no side channels. Aligned with project patterns.
- ESM import pattern is correct: `import { … } from "fs"` at module top level.
- The regression guard using `vi.mock` + `mock.invocationCallOrder` is a good pattern for asserting call ordering.

## Conventions

- Code style consistent with the rest of `graph.ts` — `fn` shorthand, `ret` shorthand, no semicolons.
- Test file follows the project's `vitest` + `vi.mock` pattern used elsewhere.
- No lint violations.

## Testing

- **Regression guard** (`src/store/graph.test.ts`): Tests that `mkdirSync` is called before `writeFileSync` using Vitest `mock.invocationCallOrder`. This is the correct way to assert temporal ordering in Vitest.
- The guard is in the `addNode()` test because `addNode()` calls `save()`, which is the production code path that needs `mkdirSync`.
- All 31 tests pass (6 in `src/store/graph.test.ts` + 25 in `src/__tests__/graph.test.ts`).

## Business Rules

- No domain rules violated. The fix is a low-level fs-correctness concern, not a business-logic change.

## Advisory Notes

1. **Technical debt reminder**: The project's known issues list `link` resolves by exact title match only — no fuzzy or ID-based lookup. This is not part of this task but worth tracking.
2. **Edge weight**: `Edge.weight` is always hardcoded to `1`. Not in scope for this task.