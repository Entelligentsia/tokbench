# CODE REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

*(standalone review)*

---

**Verdict:** Approved

---

## Review Summary

This is a verification-only task with no code modifications. All three core claims were independently confirmed by reading the actual source code and re-running all gate checks. The codebase correctly implements `mkdirSync` import and usage as specified, and all quality gates pass cleanly.

## Checklist Results

| Item | Result | Notes |
|---|---|---|
| No npm dependencies introduced | N/A | No code changes |
| Hook exit discipline (exit 0 on error, not non-zero) | N/A | No code changes |
| Tool top-level try/catch + exit 1 on error | N/A | No code changes |
| `--dry-run` supported where writes occur | N/A | No code changes |
| Reads `.forge/config.json` for paths (no hardcoded paths) | N/A | No code changes |
| Version bumped if material change | N/A | No material change |
| Migration entry present and correct | N/A | No user-facing change |
| Security scan report committed | N/A | No security-affecting change |
| `additionalProperties: false` preserved in schemas | N/A | No schema changes |
| `node --check` passes on modified JS/CJS files | 〇 | No modified JS/CJS files; `npm run build` confirms TypeScript compiles cleanly |
| `validate-store --dry-run` exits 0 | N/A | No store schema changes |
| No prompt injection in modified Markdown files | N/A | No Markdown changes |

## Verification Results (Independent — Not from PROGRESS.md)

### Claim 1: `mkdirSync` in top-level static import ✅

Line 2 of `src/store/graph.ts`:
```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```
Confirmed: `mkdirSync` is a named import in the static top-level import statement. No dynamic `await import()` is used.

### Claim 2: `save()` is synchronous with no `await` ✅

```typescript
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```
Confirmed: No `async` keyword on the function signature, no `await` anywhere in the file (`grep -n "await\|async" src/store/graph.ts` returns no results).

### Claim 3: `mkdirSync` called before `writeFileSync` in `save()` ✅

Lines 14-17 of `src/store/graph.ts`: `mkdirSync(dir, { recursive: true })` on line 15, then `writeFileSync(DATA_PATH, ...)` on line 16. Call ordering confirmed both by inspection and by the CART-B01 regression guard test.

### Gate Re-verification ✅

| Gate | Command | Result |
|------|---------|--------|
| Build | `npm run build` | ✅ Exit 0, no TypeScript errors |
| Test | `npm test` | ✅ 31/31 passed (including CART-B01 regression guard) |
| Lint | `npm run lint` | ✅ Exit 0, no ESLint errors |

### CLAUDE.md Verification ✅

No CART-B01 entry exists in the Known issues / in-progress section. Only a single bullet about `link` title-based lookup. The plan's step 3 (removing a CART-B01 entry) correctly evaluated to a no-op.

### Git Diff Verification ✅

Commit `eb77aaf` contains only artifact files (PLAN.md, PROGRESS.md, etc.) — no changes to `src/store/graph.ts` or any source code. This confirms the task was truly verification-only.

## Issues Found

None. All claims verified, all gates pass, no security or architecture concerns.

---

## If Approved

### Advisory Notes

1. **Verification-only scope is appropriate**: The task was correctly scoped as verification rather than modification. No code changes were needed because the fix was already in place.
2. **Regression guard is solid**: The CART-B01 test uses `mock.invocationCallOrder` to assert call ordering, which is a robust approach.
3. **No negative test for idempotent mkdirSync**: The regression guard verifies `mkdirSync` is called before `writeFileSync` but doesn't test that `mkdirSync(dir, { recursive: true })` is idempotent when the directory already exists. This is non-blocking — `recursive: true` handles this per Node.js semantics.
4. **Project technical debt unchanged**: The known-issues section still documents the title-only lookup limitation for `link()`. This was not in scope for this task but remains an area for future improvement.