# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

(standalone review)

## 1. Spec Compliance — Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `mkdirSync` in top-level static import from `"fs"` | ✅ Pass | Line 2 of `src/store/graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single import statement containing all four fs operations |
| 2 | `save()` contains no `await` keyword | ✅ Pass | Lines 14–18: function is fully synchronous; `mkdirSync(dir, { recursive: true })` called before `writeFileSync(DATA_PATH, …)` |
| 3 | `npm run build` exits 0 | ✅ Pass | Verified `tsc --noEmit` — zero errors |
| 4 | `npm test` exits 0 with regression guard | ✅ Pass | All 31 tests pass; two independent regression guards confirm `mkdirSync` call order < `writeFileSync` call order via `invocationCallOrder` |
| 5 | `npm run lint` exits 0 | ✅ Pass | No output, exit 0 |
| 6 | CLAUDE.md has no unresolved CART-B01 entry | ✅ Pass | Known-issues section contains only the unrelated title-lookup item; CART-B01 entry is gone |

## 2. Code Quality

- **Single import statement** — The key risk noted in the task ("must be extended to include `mkdirSync` rather than adding a second import statement") is correctly addressed. Line 2 is one destructured import.
- **`save()` implementation** — `mkdirSync(dir, { recursive: true })` → `writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2))` is the correct sequence: ensure directory exists before writing.
- **No dead code** — No leftover `await import("fs")` patterns anywhere in the file.

## 3. Security

- Path derived from `process.env.HOME ?? "~"` — not from user input. No injection risk.
- `{ recursive: true }` is the correct Node.js idiom; no shell execution involved.

## 4. Architecture & Conventions

- Follows project pattern: pure functions in `graph.ts`, no module-level side effects, no singleton state.
- Import style matches project convention (destructured named imports).
- No new dependencies or interface changes.

## 5. Testing Assessment

Two independently authored test suites provide regression coverage:

1. **`src/store/graph.test.ts`** — Directly tests `save()` call ordering with `vi.mock("fs")` and `invocationCallOrder` assertions.
2. **`src/__tests__/graph.test.ts`** — Tests `save()` via `addNode()` and other high-level functions, also asserting `invocationCallOrder` ordering.

Both use `vi.clearAllMocks()` in `beforeEach`. Mocking pattern is consistent with project convention (async `importOriginal` factory).

## 6. Advisory Notes

- No code changes were made in this task — the fix was already in place. The task was purely a verification exercise, and all six acceptance criteria pass.
- Technical debt items (title-only lookup, hardcoded edge weight, unused `enquirer` dep) are pre-existing and out of scope for this task.

---

**Verdict: Approved**

All acceptance criteria verified independently against actual source code and test output. No issues found.