# Architect Approval — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Independent Verification

I have independently verified the implementation against the project architecture:

1. **Static import confirmed**: `mkdirSync` appears in the top-level import on line 2 of `src/store/graph.ts` — `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`. No dynamic import exists anywhere in the file. ✓
2. **Synchronous save() confirmed**: Zero `await` keywords in the entire file. `save()` calls `mkdirSync()` and `writeFileSync()` synchronously. ✓
3. **Import integrity**: Single import statement on line 2, `mkdirSync` added alongside other `fs` members — not duplicated. ✓
4. **All three gates pass**: Build (tsc), test (vitest — 31/31), and lint (eslint) all exit 0, as reported by implementation, code review, and validation phases. ✓
5. **CLAUDE.md**: No mkdirSync entry exists in known-issues — verification-of-absence confirmed. ✓

## Cross-Cutting Concerns

- **No impact on other modules**: `save()` writes only to `~/.cartographer/graph.json`. No other services, APIs, or modules consume this path at runtime.
- **No concurrency safety**: The existing `load()` → mutate → `save()` pattern has no lock or atomic write — this is a pre-existing technical debt item, not introduced by this task.
- **No breaking changes**: No API surface change; no data model change; no store schema change.

## Operational Impact

- **Version bump**: Not required — internal correctness fix, no API change.
- **Migration**: Not required — no data model or schema changes.
- **Security scan**: Not required — no changes to forge tools or security-sensitive code.
- **Deployment**: Standard — no user action required.

## Advisory Notes (out of scope)

- The `process.env.HOME ?? "~"` fallback (lines 6 and 14) is a latent bug: Node.js `path.join` does not expand `~`. If `HOME` is unset, the path resolves to a literal directory named `~`. This should be addressed in a future sprint.
- The `load()` → mutate → `save()` cycle has no concurrency guard — risk of data loss under concurrent CLI invocations. Also a future-sprint concern.

**Verdict:** Approved

## Deployment Notes
No deployment changes required. This is a verification-only task — no code was modified. The implementation was already correct.

## Follow-Up Items for Future Sprints
1. Fix the `~` fallback in `DATA_PATH` and `save()` — use `os.homedir()` or expand `~` properly when `HOME` is unset.
2. Add concurrency safety (file lock or atomic write) to the `load()`/`save()` cycle.