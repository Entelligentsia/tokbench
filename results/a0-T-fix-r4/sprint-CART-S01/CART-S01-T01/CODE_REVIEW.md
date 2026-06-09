# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor* — I review before things move forward. I read the actual code, not the report.

**Task:** CART-S01-T01

*(standalone review)*

---

**Verdict:** Approved

---

## Review Summary

This is a verification task confirming that `src/store/graph.ts` uses a static top-level import for `mkdirSync` from `"fs"` and that `save()` is fully synchronous — fixing the CART-B01 bug where `await import("fs")` inside a non-async function meant `mkdirSync` was never called. All six acceptance criteria have been independently verified: static import is present, no `await` in `save()`, and all three gate checks (build, test, lint) pass. The regression guard test using `invocationCallOrder` provides a strong guarantee against re-introduction.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | 〇 | No new packages added |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | Not a forge hook |
| Tool top-level try/catch + exit 1 on error | N/A | Not a forge tool |
| `--dry-run` supported where writes occur | N/A | Not a forge tool |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | Uses `process.env.HOME`, no forge paths |
| Version bumped if material change | N/A | Bug fix in `src/`, not a plugin |
| Migration entry present and correct | N/A | No schema changes |
| Security scan report committed | N/A | No `forge/` directory changes |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | N/A | TypeScript; verified via `tsc` build gate |
| `validate-store --dry-run` exits 0 | N/A | No store schema changes |
| No prompt injection in modified Markdown files | N/A | No modified Markdown files |

## Independent Verification Results

All checks performed by reading source files and running commands directly — not from reports.

### AC1: `mkdirSync` in top-level static import from `"fs"`
**✅ CONFIRMED.** Line 2 of `src/store/graph.ts`:
```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```
Single import statement, no duplicate, no dynamic `import()`.

### AC2: `save()` contains no `await` keyword
**✅ CONFIRMED.** `grep -n 'await' src/store/graph.ts` returns exit code 1 (no matches). The `save()` function (lines 11–14) is entirely synchronous.

### AC3: `npm run build` (`tsc`) exits 0
**✅ PASSED.** TypeScript compilation succeeds with zero errors.

### AC4: `npm test` — regression guard passes
**✅ PASSED.** 31/31 tests pass. The CART-B01 regression guard in `graph.test.ts` asserts `mkdirSyncSpy.mock.invocationCallOrder[0] < writeFileSyncSpy.mock.invocationCallOrder[0]`, which correctly enforces ordering at the mock-engine level.

### AC5: `npm run lint` exits 0
**✅ PASSED.** ESLint reports no issues.

### AC6: Document verification results in PROGRESS.md
**✅ COMPLETED.** PROGRESS.md artifact exists with all criteria marked confirmed.

## Code Quality Assessment

### Correctness
- `save()` calls `mkdirSync(dir, { recursive: true })` on line 13, then `writeFileSync(DATA_PATH, ...)` on line 14 — correct ordering. The `{ recursive: true }` option ensures parent directories are created as needed.
- No dynamic `import("fs")` anywhere in `graph.ts` — the original bug root cause is eliminated.

### Security
- No injection vectors in the change. `dir` and `DATA_PATH` are derived from `process.env.HOME`, not from user input.
- `JSON.parse(readFileSync(...))` on the app's own data file — acceptable for this offline-only CLI tool.

### Architecture
- Pattern (load-modify-save) is consistent with the project's established approach.
- `graph.ts` exports pure functions only — no singleton state, no module-level side effects. ✅
- Intra-project import uses `.js` extension (`from "../types.js"`) — follows ESM convention. ✅

### Conventions
- `const` and arrow functions throughout — no `class` definitions. ✅
- Node built-ins (`"fs"`, `"path"`, `"crypto"`) imported without `.js` extension — correct, they're not intra-project modules. ✅

### Testing
- CART-B01 regression guard uses `mock.invocationCallOrder` — this is a strong guarantee (stronger than just checking `toHaveBeenCalled`), because it asserts the call happened before the write at the engine level. ✅
- `vi.mock("fs", ...)` uses the `importOriginal` pattern for partial mocking — consistent with stack-checklist guidance. ✅
- `beforeEach(() => vi.clearAllMocks())` present in the CART-B01 describe block. ✅

## Issues Found

None.

---

## If Approved

### Advisory Notes

1. **`HOME ?? "~"` fallback (pre-existing):** The `"~"` string literal won't expand in Node.js — if `process.env.HOME` is ever undefined, `join("~", ".cartographer")` would create a literal `~` directory. This is not part of this fix but is worth tracking as technical debt.
2. **No concurrency safety (pre-existing):** The load-modify-save cycle has no locking — concurrent `carto` processes could cause data loss. This is known technical debt.
3. **Unused dependencies (pre-existing):** `enquirer` and `lowdb` are listed in `package.json` but not used in `src/`. Not related to this fix.