# Architect Approval — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Verdict

**Verdict:** Approved

## Rationale

The mkdirSync fix in `src/store/graph.ts` is architecturally sound:

1. **Correct import pattern**: `mkdirSync` is a top-level static import from `'fs'`, consistent with the ESM-only module system. No dynamic `await import()` pattern is used anywhere in the file — CART-B01 is fully resolved.

2. **Synchronous persistence model**: `save()` returns `void` with no `await`, matching the project's custom JSON load/save architecture. No async patterns are introduced.

3. **Correct ordering**: `mkdirSync(dir, { recursive: true })` is called before `writeFileSync(DATA_PATH, ...)`, preventing ENOENT errors on first write.

4. **Zero cross-cutting impact**: The change is entirely localized to the `save()` function in `graph.ts`. No CLI surface, data format, or module interface changes.

5. **All gates pass**: Build (0 errors), tests (31 pass including CART-B01 regression guard), lint (clean).

6. **Regression guard**: The test suite asserts `invocationCallOrder` to guarantee mkdirSync is called before writeFileSync — a strong assertion that will catch any future regression.

## Deployment Notes

- No version bump, migration, or deployment changes required.
- Fully backwards compatible — no API surface changes.
- This is a verification task; the fix was already in place.

## Follow-up Items for Future Sprints

- **Unused dependencies**: `lowdb` and `enquirer` are declared in `package.json` but not imported in source code. Consider removing in a cleanup sprint.
- **Concurrency safety**: The read-modify-write pattern (load → mutate → save) has no locking mechanism. Safe for single-user CLI but would need attention if multi-process access were ever introduced.
- **Hardcoded edge weight**: `link()` always creates edges with `weight: 1`. Weighted edges are not supported.
- **Node lookup**: Only title-based lookup exists — no fuzzy search or ID-based lookup.