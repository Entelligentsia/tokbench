# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

(standalone review)

---

**Verdict:** Approved

---

## Review Summary

The implementation is verified correct. The CART-B01 bug fix (`mkdirSync` static import instead of broken `await import("fs")`) was already in place in the codebase; no source code changes were needed. The only material change was removing the stale Known Issues table entry from `README.md`. All six acceptance criteria are independently confirmed.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | 〇 | No package.json changes |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No hooks modified |
| Tool top-level try/catch + exit 1 on error | N/A | No CLI tools modified |
| `--dry-run` supported where writes occur | N/A | No new write paths |
| Reads `.forge/config.json` for paths (no hardcoded paths) | 〇 | No config path changes |
| Version bumped if material change | N/A | No material code change — bug fix verification only |
| Migration entry present and correct | N/A | No data model changes |
| Security scan report committed | N/A | No new dependencies or security-sensitive paths |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | 〇 | No JS/CJS files modified |
| `validate-store --dry-run` exits 0 | 〇 | Store untouched |
| No prompt injection in modified Markdown files | 〇 | README.md only — no user-controlled content introduced |

## Issues Found

None.

## Verification Evidence (Independent)

All verifications performed by reading actual source files, not agent reports:

1. **Static import confirmed** — `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — `mkdirSync` is a top-level static import. No `await import("fs")` anywhere in the file.
2. **`save()` is purely synchronous** — `grep -n 'await' src/store/graph.ts` returns zero matches. The `save()` function at lines 12–16 is `void`, not `async`, with no `await` expressions.
3. **`mkdirSync`-before-`writeFileSync` ordering** — Line 15 calls `mkdirSync(dir, { recursive: true })` before line 16 calls `writeFileSync(DATA_PATH, ...)`.
4. **Regression guards** — Both test files contain ordering assertions:
   - `src/store/graph.test.ts`: uses `invocationCallOrder` to assert `mkdirOrder < writeOrder`
   - `src/__tests__/graph.test.ts`: identical `invocationCallOrder` assertion in "calls mkdirSync before writeFileSync" test
5. **All three gate commands pass** — Independently re-run:
   - `npm run build` → exit 0 (tsc clean)
   - `npm test` → 31/31 tests pass (6 in `graph.test.ts`, 25 in `__tests__/graph.test.ts`)
   - `npm run lint` → exit 0 (no ESLint errors)
6. **README.md Known Issues table** — CART-B01 row removed. Table now contains only the "Node lookup" entry. Confirmed by reading lines 60–64 directly.

---

## If Approved

### Advisory Notes

1. **CLAUDE.md has no CART-B01 entry** — The task prompt's acceptance criterion #6 referenced `CLAUDE.md`, but the actual stale entry was in `README.md`. The plan correctly targeted `README.md` and the implementation removed it. No action needed on `CLAUDE.md`.

2. **No source code changes were made** — The entire task was a verification + documentation update. The git commit (`eb77aaf`) only added task artifacts, confirming the fix was pre-existing.

3. **Dual regression guard coverage** — The CART-B01 regression guard exists in both `src/store/graph.test.ts` (CART-B01-specific) and `src/__tests__/graph.test.ts` (broader `save()` tests). This is good defense-in-depth.