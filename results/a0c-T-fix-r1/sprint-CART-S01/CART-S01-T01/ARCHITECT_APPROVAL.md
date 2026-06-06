# Architect Approval — CART-S01-T01

**Verdict:** Approved

## Scope
Fix `src/store/graph.ts` to use a static top-level `mkdirSync` import with a synchronous `save()`, run the three gates (tsc / vitest / eslint) to exit 0, and clear any stale CART-B01 known-issue entry from CLAUDE.md.

## Architectural Review
- **Import style:** `graph.ts` line 2 is a single static import — `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"`. No dynamic `await import('fs')`, no async/await anywhere in the file. Consistent with the ESM, Node-20+ posture in `architecture/stack.md`.
- **Persistence contract:** `save()` remains synchronous and calls `mkdirSync(dir, { recursive: true })` before `writeFileSync` — the directory-creation ordering that the CART-B01 regression guard asserts via `invocationCallOrder`. The custom JSON load/save persistence model (`~/.cartographer/graph.json`) is unchanged.
- **Cross-cutting concerns:** None. Graph/Node/Edge types and the `graph.json` schema are untouched. No public API surface change; callers (`addNode`, `link`, `removeNode`) are unaffected. No new modules introduced.
- **Operational impact:** None of the impact categories apply (no data-loss, no breaking-change, no performance regression, no surface-change). Offline-only CLI; no deployment topology change.

## Approval Rationale
All five pipeline phases (plan → review-plan → implement → review-code → validate) converge on the same finding: the static-import correction was already in place, so the task resolved as a verification pass with all three gates green (31/31 vitest tests, tsc exit 0, eslint exit 0). The regression guard in `src/store/graph.test.ts` protects the fix going forward. Implementation is consistent with project architecture and deployment posture is understood.

## Deployment Notes
No build, migration, or release coordination required. Pure source-level correctness fix; ships with the next normal build.

## Follow-up Items (future sprints)
- Existing technical debt remains out of scope and untracked here: no node update method, title-only lookup (no fuzzy/ID lookup), fixed edge weight of 1, unused `enquirer` dependency, and no concurrency safety on the read-modify-write `load()`/`save()` cycle. The last item is worth a dedicated future task given the save() path was just under review.
