# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

*(standalone review)*

---

**Verdict:** Approved

---

## Review Summary

The plan is straightforward and correctly scoped: verify that the CART-B01 bug fix (mkdirSync static import in graph.ts) is in place and that all project gates pass. I independently confirmed every claim in the plan by reading the actual source and running the gate commands.

## Feasibility

The plan is realistic and minimal — it correctly identifies the two lines of code that constitute the fix (top-level import of `mkdirSync` from `fs`, and synchronous `save()` with no `await`). The scope is verification-only; no code changes are required. Independent verification confirms:

- `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` — `mkdirSync` is a static top-level import, not a dynamic `await import()`. ✅
- `save()` function (line 12): synchronous, no `await` keyword anywhere in the body. ✅
- `mkdirSync(dir, { recursive: true })` is called before `writeFileSync(DATA_PATH, ...)` in the same function. ✅

The regression guard test in `src/store/graph.test.ts` uses `invocationCallOrder` to assert `mkdirSync` is called before `writeFileSync`. ✅

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — no version bump required, correctly declared as "not required".
- **Migration entry targets correct?** N/A — no schema or data structure changes.
- **Security scan requirement acknowledged?** Yes — correctly declared as not required (no changes to forge/ directory or security-sensitive code).

## Security

No security concerns. This is a verification-only task with no code changes. The fix itself (synchronous `mkdirSync` before `writeFileSync`) is the correct security posture — it eliminates the race condition where `await import("fs")` inside a sync function could fail to create the directory before writing, causing an unhandled ENOENT. No prompt injection risk, no data exfiltration risk.

## Architecture Alignment

- **Established patterns followed?** Yes — `graph.ts` exports pure functions only, `save()` remains synchronous, no singleton state introduced, no module-level side effects beyond the import.
- **`additionalProperties: false` preserved?** N/A — no schema changes.
- **ESM import style correct?** Yes — all imports use the correct `.js` extension pattern for ESM runtime resolution.
- **No new dependencies?** Correct — no new imports or dependencies added.

## Testing Strategy

Adequate. The plan specifies three gate commands, all of which I ran independently:

| Gate | Command | Result |
|------|---------|--------|
| TypeScript build | `npm run build` | ✅ Exit 0, no errors |
| Test suite | `npm test` | ✅ 31 tests pass (2 files) |
| Lint | `npm run lint` | ✅ Exit 0, no warnings |

The regression guard test (`mkdirSync` called before `writeFileSync` per `invocationCallOrder`) directly prevents re-introduction of the CART-B01 bug.

**Note on test coverage:** The test file covers the ordering guarantee via `invocationCallOrder`, which is the most reliable way to verify call ordering in Vitest. This is a strong regression guard.

## CLAUDE.md Review

The known-issues section in `CLAUDE.md` does not contain a CART-B01 entry — it only mentions the title-only lookup limitation. Since the bug fix is already in the codebase and verified, there is nothing to update. The plan correctly said "review and update if necessary" — reviewed, no update necessary.

---

## If Approved

### Advisory Notes

1. **Unused dependencies** (non-blocking, tracked as existing tech debt): `lowdb` and `enquirer` remain unused in `src/`. The stack checklist flags both. This is outside the scope of this verification task but worth tracking for a future cleanup sprint.
2. **Edge weight hardcoding** (non-blocking): `link()` still hardcodes `weight: 1`. The stack checklist notes this. Not in scope.
3. **No concurrency safety on read-modify-write** (non-blocking): The plan acknowledges this as existing tech debt. The `load()` → mutate → `save()` pattern has a TOCTOU race if two processes write concurrently. Not in scope for this verification task.