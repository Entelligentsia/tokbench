# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

---

**Verdict:** Approved

---

## Review Summary

The plan correctly identifies the existing state of the codebase — `graph.ts` already uses a static named import and a synchronous `save()` function — and proposes verification and guard-hardening work rather than a primary fix. All three gate commands (`npm run build`, `npm test`, `npm run lint`) pass in the current working tree. The plan is realistic, well-scoped, and correctly targets the right files.

## Feasibility

The approach is realistic and correctly scoped. Independent verification confirms:

1. **Static named import already in place.** `src/store/graph.ts` line 2 reads `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"`. No `await import("fs")` pattern exists anywhere in the file. `save()` is a synchronous `void` function with zero `await` expressions.
2. **All 31 tests pass.** `vitest run` reports 31 PASS, 0 FAIL. `tsc --noEmit` exits clean. Lint exits 0 (one unrelated warning in `lib/schema-loader.cjs`).
3. **Both test files already have guard tests.** `src/store/graph.test.ts` has an explicit "mkdirSync called before writeFileSync" ordering test using `invocationCallOrder`. `src/__tests__/graph.test.ts` also has ordering tests in its `save()` describe block with the same `invocationCallOrder` pattern.

The plan correctly scopes changes to verification, mock standardization, and documentation — not a re-fix.

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — plan states "not required," which is correct for this surface-change-only task.
- **Migration entry targets correct?** N/A — no data model changes.
- **Security scan requirement acknowledged?** Yes — plan states no security scan required.

## Security

No security risk. The change is limited to import style and test mocks in an offline-only CLI. No new inputs, no network access, no prompt injection surface.

## Architecture Alignment

- **Import style:** The static named import pattern follows the ESM + `.js` extension convention established in `tsconfig.json` (moduleResolution: bundler) and the project style guide. ✅
- **No singleton state / module-level side effects:** `graph.ts` continues to export pure functions only. The `mkdirSync` call inside `save()` is an I/O side effect, but it is correctly encapsulated inside a synchronous function rather than at module top level. ✅
- **Data path convention:** `DATA_PATH` uses `process.env.HOME ?? "~"`, unchanged. ✅
- **`{ recursive: true }` on mkdirSync:** Both test files confirm `mkdirSync` is called with `{ recursive: true }`. ✅

## Testing Strategy

The plan's testing strategy is adequate but has one advisory note:

- **Positive verification:** Run `npm test` (31 tests) — confirmed passing.
- **Negative verification:** "Temporarily revert to a problematic import pattern" — this is a good manual check but is not persisted in the test suite. After verifying, the negative case is removed and not regression-guarded.
- **Mock standardization:** There is a meaningful difference between the two test suites' mock strategies that should be addressed during implementation:

  | Aspect | Co-located (`src/store/graph.test.ts`) | Integration (`src/__tests__/graph.test.ts`) |
  |--------|----------------------------------------|---------------------------------------------|
  | fs import | Dynamic `await import("fs")` per test | Top-level `import * as fs from "fs"` |
  | Module under test import | Dynamic `await import("./graph.js")` per test | Top-level static import |
  | mkdirSync mock | `vi.fn(actual.mkdirSync)` — **calls real filesystem** | `vi.fn()` — pure mock, no FS writes |
  | writeFileSync mock | `vi.fn(actual.writeFileSync)` — **writes to disk** | `vi.fn()` — pure mock |
  | State persistence | Mutable `mockGraph` module variable | Handcrafted fixtures via `mockReturnValueOnce` |

  The co-located test actually creates `~/.cartographer/` on disk because it delegates to the real `mkdirSync` and `writeFileSync`. This is a test isolation concern. The plan identifies "standardize mocks" as a deliverable, and the implementation phase should unify both suites to use pure mocks (`vi.fn()` without actual FS calls) to prevent filesystem side effects during test runs.

---

## If Approved

### Advisory Notes

1. **Mock isolation:** During implementation, prefer the `src/__tests__/graph.test.ts` pattern of `vi.fn()` (no actual implementation) for both `mkdirSync` and `writeFileSync`. The co-located test's `vi.fn(actual.mkdirSync)` pattern creates real directories on disk during test runs, which is a side-effect leak. Both suites should use pure mocks and handcrafted return values.
2. **Negative verification artifact:** Consider adding a comment in the guard test documenting the negative case that was verified (i.e., that reverting to `await import("fs")` causes the `invocationCallOrder` guard to fail), so future maintainers understand what regression the test prevents.
3. **CLAUDE.md known issues entry:** The task prompt mentions removing a "known issues" entry for CART-B01. The current `CLAUDE.md` does not contain such an entry — it only mentions the fuzzy/id lookup roadmap item. This item may already have been resolved or may never have been added. No action needed unless the entry appears elsewhere.
4. **Plan scope vs. task acceptance criteria alignment:** The task's acceptance criterion #6 ("Known issues entry in CLAUDE.md is removed or marked resolved") appears already satisfied. The plan does not call out this item explicitly, but no file change is needed.