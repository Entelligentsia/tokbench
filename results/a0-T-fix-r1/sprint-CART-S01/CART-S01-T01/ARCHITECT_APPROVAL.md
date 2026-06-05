# ARCHITECT APPROVAL — CART-S01-T01

## Verdict: Approved

## Rationale

All six acceptance criteria have been independently verified across plan, implementation, code review, and validation phases:

1. **Static import confirmed** — `mkdirSync` is imported via top-level `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` on line 2 of `src/store/graph.ts`. No dynamic `await import()` remains.
2. **`save()` is fully synchronous** — Zero `await` keywords in the entire file (`grep -c 'await'` → 0). The function calls `mkdirSync(dir, { recursive: true })` then `writeFileSync(DATA_PATH, ...)` in correct order — no async hazard.
3. **Build gate passes** — `npm run build` exits 0; TypeScript compiles cleanly with no errors.
4. **Test gate passes** — All 31 tests pass, including the CART-B01 regression guard that validates `mkdirSync` is called before `writeFileSync` via `invocationCallOrder`.
5. **Lint gate passes** — `npm run lint` exits 0 with no errors.
6. **CLAUDE.md** — No CART-B01 entry exists in known issues; criterion is already met.

## Architecture Assessment

- **No cross-cutting impact** — The fix is localised to `src/store/graph.ts` (a single file, one import change). No other modules import `graph.ts` in a way that would be affected by this change.
- **No deployment changes** — No version bump, no migration, no schema change, no new dependencies. Pure internal bug fix.
- **Synchronous I/O contract preserved** — The `save()` function's synchronous API contract is maintained, which is consistent with the CLI architecture (offline-only, single-threaded Node.js runtime, no HTTP listener).
- **Regression guard is well-scoped** — The test uses `vi.mock("fs")` to verify call order via `invocationCallOrder`, which is specific enough to catch future regressions of this exact bug.

## Deployment Notes

- No user action required — the fix is to an internal module and requires no migration or configuration change.
- No version bump is required for this bug fix.

## Follow-Up Items for Future Sprints

1. **Concurrency gap in `save()` read-modify-write** — `save()` does a `load()` → mutate → `save()` cycle without locking. Under concurrent `carto` invocations, data loss is possible. This is a pre-existing issue, not introduced by this fix. Consider a file-lock mechanism (e.g., `proper-lockfile`) for a future sprint.
2. **Unused dependencies** — `enquirer` and `lowdb` remain in `package.json` but are not used in source code. These should be removed in a future hygiene sprint.
3. **Node update method missing** — Nodes cannot be edited after creation. This is a known limitation per the architecture docs.
4. **Edge weight always 1** — Weighted edges not yet supported.