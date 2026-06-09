# CART-S01-T01 — Plan Review (standalone review)

## Verdict: ✅ Approved

## Summary

The plan correctly identifies that the CART-B01 fix (static `mkdirSync` import, removal of `await import("fs")` from synchronous `save()`) is already in place in the working tree, and proposes verification-only work (running the three gates). All claims in the plan were independently confirmed by reading the actual source code and running the gate commands.

## Independent Verification

| # | Acceptance Criterion | Plan Claim | Verified | Evidence |
|---|----------------------|------------|----------|----------|
| 1 | `mkdirSync` in top-level static `import { … } from "fs"` | ✅ Met | ✅ | Line 2 of `src/store/graph.ts`: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — single static import, no dynamic import anywhere in file |
| 2 | `save()` contains no `await` keyword | ✅ Met | ✅ | `grep -n 'await' src/store/graph.ts` returns exit 1 (no matches). `save()` is a plain synchronous `void` function |
| 3 | `npm run build` exits 0 | ✅ Met | ✅ | Ran independently — exit 0, no TypeScript errors |
| 4 | `npm test` exits 0 | ✅ Met | ✅ | 31/31 tests pass. CART-B01 regression guard in `graph.test.ts` verifies `mkdirSync` invocation order < `writeFileSync` |
| 5 | `npm run lint` exits 0 | ✅ Met | ✅ | Ran independently — exit 0, no ESLint errors |
| 6 | CART-B01 known-issue entry removed from CLAUDE.md | N/A | ✅ | CLAUDE.md contains no CART-B01 entry; only the `link` title-resolution item. No change needed |

## Security Review

- `mkdirSync(dir, { recursive: true })` — standard Node.js pattern, no path traversal risk (fixed `.cartographer` directory under `HOME`)
- `HOME` env var fallback to `"~"` is acceptable for a CLI tool; `~` expansion is handled by the shell, not Node, but this is a benign cosmetic fallback since `process.env.HOME` is practically always set on Linux/macOS
- No user-controlled input reaches `mkdirSync` or `writeFileSync` paths — the directory path is hardcoded

## Architecture Alignment

- Pure-function export pattern preserved (no classes, singletons, or side effects in module scope)
- Offline-only constraint maintained — no network or database dependency introduced
- Single-extend of existing import line is correct; avoids duplicate import statements
- Consistent with stack.md: ESM module, explicit `.js` extensions in imports, `fs` module used directly

## Advisory Notes

1. **`lowdb` is listed as a dependency but unused** — the stack.md already flags this. Not in scope for this task, but worth tracking for future cleanup.
2. **CART-B01 bug record is absent from the store** — the task prompt references CART-B01 but no bug record with that ID exists in `.forge/store/bugs/` (only CART-BUG-001 and CART-BUG-002). This is a minor bookkeeping discrepancy but does not affect the technical correctness of the plan.
3. **`process.env.HOME ?? "~"` fallback** — if `HOME` is unset (rare on Unix, possible in some CI environments), `join("~", ".cartographer")` will create a literal `~/.cartographer` directory rather than expanding to the user's home. Not a bug (this is pre-existing behavior), but worth noting for future hardening.