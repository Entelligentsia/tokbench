# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01
**Review:** (standalone review)

---

**Verdict:** Approved

---

## Review Summary

This is a verification-only task — no code was modified (git diff is empty against origin/main). All six acceptance criteria were independently verified by reading actual source files and running all three gate commands. The CART-B01 bug fix (mkdirSync static import) is correctly in place, the regression guard is well-structured, and all gates pass cleanly.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | 〇 | No changes at all — verification task |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No hooks modified |
| Tool top-level try/catch + exit 1 on error | N/A | No tools modified |
| `--dry-run` supported where writes occur | N/A | No write-side changes |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | No path changes |
| Version bumped if material change | N/A | No material change |
| Migration entry present and correct | N/A | No migrations |
| Security scan report committed | N/A | Not required per acceptance criteria |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | 〇 | No JS/CJS files modified |
| `validate-store --dry-run` exits 0 | N/A | No store changes |
| No prompt injection in modified Markdown files | N/A | No markdown files modified |

## Acceptance Criteria Verification

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | `src/store/graph.ts` has `mkdirSync` in top-level `import { … } from "fs"` | ✅ | Line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` |
| 2 | `save()` contains no `await` keyword | ✅ | `save()` declared as `function save(graph: Graph): void`; grep for `await` returns no matches in entire file |
| 3 | `npm run build` exits 0 | ✅ | Independently ran `npm run build` — `tsc` completed with 0 errors |
| 4 | `npm test` exits 0 with regression guard | ✅ | Independently ran `npm test` — 31/31 tests pass; regression guard uses `invocationCallOrder` to verify `mkdirSync` called before `writeFileSync` |
| 5 | `npm run lint` exits 0 | ✅ | Independently ran `npm run lint` — 0 errors |
| 6 | CLAUDE.md CART-B01 entry removed or marked resolved | ✅ | No CART-B01 entry found in CLAUDE.md |

## Code Quality Assessment

### Import Statement (line 2 of `src/store/graph.ts`)
- **Correct**: `mkdirSync` is in a single, consolidated static import from `"fs"`. No duplicate imports, no dynamic `await import()`.
- **Pattern compliance**: Follows ESM + TypeScript conventions used in the project.

### `save()` Function (lines 13–17)
- **Correctly synchronous**: `void` return type, no `async` keyword, no `await` expressions.
- **Proper `mkdirSync` usage**: Uses `{ recursive: true }` option, ensuring `~/.cartographer/` and any parent directories are created if missing.
- **Call ordering**: `mkdirSync(dir, …)` on line 15, then `writeFileSync(DATA_PATH, …)` on line 16 — correct order guaranteed by synchronous execution.

### Regression Guard Test (`src/store/graph.test.ts`)
- **Well-structured**: Uses `vi.mock("fs")` with spy wrappers on `mkdirSync` and `writeFileSync`.
- **Ordering assertion**: Correctly uses `mock.invocationCallOrder` and `toBeLessThan` to enforce that `mkdirSync` is called before `writeFileSync` — this is the right Vitest pattern for call-order verification.
- **Comment explains the bug**: Lines 4–6 clearly document the CART-B01 context (TS1308 error, `await import("fs")` in non-async function).

## Issues Found

None. The verification task correctly confirms all acceptance criteria are met.

---

## If Approved

### Advisory Notes

1. **Unused dependencies**: `lowdb` and `enquirer` remain in `package.json` but are not used in source code — this is pre-existing technical debt outside the scope of this task.
2. **No concurrency safety**: The read-modify-write pattern in `addNode()` and `link()` (load → modify → save) has no locking. This is pre-existing technical debt noted in the project context.
3. **`eslint` not in devDependencies**: The `lint` script references `eslint` but it's not listed in `devDependencies` in `package.json` — pre-existing issue.