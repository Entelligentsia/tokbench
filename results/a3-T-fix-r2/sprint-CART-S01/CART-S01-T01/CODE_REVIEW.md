# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

---

**Verdict:** Approved

---

## Review Summary

This is a verification-only task confirming that the CART-B01 fix (static import of `mkdirSync` from `"fs"`) is correctly implemented. All six acceptance criteria were independently verified against actual source code and gate execution — every claim in PROGRESS.md matches reality. No code changes were made; the fix was already in place.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | 〇 | N/A — no code changes |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No hooks modified |
| Tool top-level try/catch + exit 1 on error | N/A | No tools modified |
| `--dry-run` supported where writes occur | N/A | No new write paths |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | No config changes |
| Version bumped if material change | N/A | Bug fix verification only |
| Migration entry present and correct | N/A | No migration needed |
| Security scan report committed | N/A | No surface change |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | N/A | No JS/CJS files modified |
| `validate-store --dry-run` exits 0 | N/A | No store changes |
| No prompt injection in modified Markdown files | N/A | No markdown changes |

## Issues Found

None. All acceptance criteria independently verified:

1. **Static import** — `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — correct.
2. **No `await import("fs")` in production code** — confirmed via `grep -rn "await import" src/ --include="*.ts" | grep -v ".test.ts"` returning no results. The `await import("fs")` pattern in test files is the standard `vi.mock` async import pattern — correct and expected.
3. **Synchronous `save()`** — `function save(graph: Graph): void` (line 11) — no `async`, no `await`. Confirmed.
4. **Call order** — `mkdirSync(dir, { recursive: true })` on line 14, then `writeFileSync(DATA_PATH, ...)` on line 15. Correct order ensures directory exists before write.
5. **Build gate** — `npm run build` (tsc) exits 0 independently verified.
6. **Test gate** — `npm test` — 31/31 tests pass, including the CART-B01 regression guard (`expect(mkdirOrder).toBeLessThan(writeOrder)`). Independently verified.
7. **Lint gate** — `npm run lint` — 0 errors, 1 unrelated warning in `lib/schema-loader.cjs`. Independently verified.
8. **Known issues** — No CART-B01 entry in CLAUDE.md. Verified.

---

## If Approved

### Advisory Notes

- The regression guard test in `src/store/graph.test.ts` is well-constructed: it uses `vi.mock` invocation call order tracking to assert `mkdirSync` is called before `writeFileSync`, which directly tests the CART-B01 root cause.
- The `save()` function has no concurrency safety (noted in project technical debt). This is pre-existing and out of scope for this verification task.
- The `fs` mock pattern `vi.mock("fs", async (importOriginal) => { ... })` correctly preserves actual implementations via `importOriginal` while selectively mocking the four needed functions.