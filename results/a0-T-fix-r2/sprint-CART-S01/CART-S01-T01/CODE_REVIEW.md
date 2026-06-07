# CODE REVIEW — CART-S01-T01 (standalone review)

## Verdict: ✅ Approved

Cartographer Supervisor — independent code review. All acceptance criteria verified by reading actual source files and re-running gate commands. No diff between origin/main and HEAD (fix was pre-committed); this task is verification-only.

---

## 1. Correctness

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `mkdirSync` is a top-level static import from `'fs'` | ✅ Pass | `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` (line 2 of graph.ts) — static, not dynamic |
| `save()` contains no `await` keyword | ✅ Pass | `save()` is `function save(graph: Graph): void` — synchronous, no `await` anywhere in the file |
| `mkdirSync(dir, { recursive: true })` called before `writeFileSync` | ✅ Pass | Lines 12–14: mkdirSync is called first, then writeFileSync — correct ordering |
| No `await import("fs")` in graph.ts | ✅ Pass | `grep -n "await import" src/store/graph.ts` returns nothing |
| CART-B01 regression guard present | ✅ Pass | `graph.test.ts` line 27: test asserts `mkdirSync` invocation call order < `writeFileSync` invocation call order |

## 2. Security

No security concerns. The `DATA_PATH` uses `process.env.HOME ?? "~"` which is safe for a local CLI tool. `{ recursive: true }` on `mkdirSync` is appropriate. No user input reaches `eval` or shell execution.

## 3. Architecture

The `load()`/`save()` pattern is consistent with the project's offline-first, JSON-file persistence model documented in `architecture/stack.md`. No architectural deviations introduced.

## 4. Conventions

- ESM-style static imports — consistent with project config (`"type": "module"`)
- Synchronous fs operations match the existing pattern — `load()` uses `readFileSync`, `save()` uses `writeFileSync`
- Test uses `vi.mock("fs")` + `invocationCallOrder` — strong assertion style, not just "was called"

## 5. Business Rules

No business rule violations. The fix preserves the knowledge-graph entity model (Node, Edge) without schema changes.

## 6. Testing

| Gate | Result |
|------|--------|
| `npm run build` (tsc) | ✅ Exit 0, no TS1308 errors |
| `npm test` (vitest run) | ✅ 31 tests pass across 2 files |
| `npm run lint` (eslint src) | ✅ Exit 0, no issues |

Regression guard test (`addNode() calls mkdirSync before writeFileSync`) uses `invocationCallOrder` — this is a strong guarantee that mkdirSync is called first, not just that both are called.

## 7. CLAUDE.md Known Issues

Reviewed — no CART-B01 entry exists in the known-issues section, so no update needed.

## Advisory Notes (non-blocking)

These were already noted in the plan review and remain non-blocking:

1. **Unused dependencies**: `enquirer` and `lowdb` are declared in `package.json` but not imported in any source file — tech debt, not a blocker.
2. **No concurrency safety**: `load()` → mutate → `save()` has no file locking — potential race under concurrent CLI invocations, but acceptable for a single-user CLI tool.
3. **Hardcoded edge weight**: `weight: 1` in `link()` — documented tech debt.

---

**All acceptance criteria satisfied. Code is production-ready.**