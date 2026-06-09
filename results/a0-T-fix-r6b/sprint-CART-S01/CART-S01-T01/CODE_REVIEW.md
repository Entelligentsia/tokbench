# CODE REVIEW — CART-S01-T01 (standalone review)

## Verdict: **Approved**

This is a verification-only task. No code changes were made. The entire scope was confirming that a pre-existing fix (mkdirSync static import) is in place and all gate commands pass. All findings are confirmatory.

---

## 1. Correctness

| Acceptance Criterion | Status | Evidence (independent) |
|---|---|---|
| `mkdirSync` in top-level import | ✅ | Line 2 of `graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` — single static import, no dynamic `await import()` |
| `save()` contains no `await` | ✅ | `grep -c "await" src/store/graph.ts` returns 0. Function is fully synchronous |
| `npm run build` exits 0 | ✅ | Ran independently — `tsc` completes with zero errors |
| `npm test` exits 0, regression guard passes | ✅ | 31/31 tests pass. Regression guard at `graph.test.ts:27-42` confirms `mkdirSync` invocation call order is before `writeFileSync` |
| `npm run lint` exits 0 | ✅ | `eslint src` — zero errors |
| Documentation reflects bug resolution | ✅ | `CLAUDE.md` contains no unresolved CART-B01 entries |

All six acceptance criteria independently verified with concrete evidence (not relying on PROGRESS.md claims).

## 2. Security

- No new code introduced. `mkdirSync(dir, { recursive: true })` with a path derived from `process.env.HOME ?? "~"` is the established pattern. No injection risk.

## 3. Architecture

- `graph.ts` continues to export pure functions only — no singleton state, no module-level side effects beyond the `DATA_PATH` constant. Consistent with stack-checklist.md guardrails.

## 4. Conventions

- `.js` extension in imports: ✅ (`import … from "../types.js"`)
- ESM `"type": "module"` in package.json: ✅
- `const` and arrow functions: ✅ throughout
- No database/network imports: ✅
- Node lookup by title (case-sensitive): ✅ unchanged

## 5. Business Rules

- Edge weight hardcoded to `1`: ✅ intentionally per checklist
- Node IDs via `randomUUID()`: ✅ from Node built-in `crypto`
- No fuzzy/ID-based lookup: ✅ unchanged (known technical debt)

## 6. Testing

The regression guard test (`CART-B01: mkdirSync called before writeFileSync in save()`) is well-structured:
- Uses `vi.mock("fs", async (importOriginal) => …)` pattern, consistent with project testing conventions
- Tests **call order** via `mock.invocationCallOrder`, not just call occurrence — this is the correct approach for ordering invariants
- All 31 tests pass including 6 in the co-located test file

## Advisory Notes

1. **No code change was made** — the fix was already in place on main before this task started. The task's value is confirming the fix is sound rather than introducing it.
2. **Unused dependencies** (`lowdb`, `enquirer`) noted in stack-checklist.md — these are pre-existing technical debt, not introduced by this task.
3. The git diff from `origin/main` to `HEAD` is empty, confirming no new commits were needed.

---

*Review conducted by cartographer Supervisor — independent verification of all claims.*