# ARCHITECT APPROVAL — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Architectural Review

### Implementation Alignment
The fix converts `mkdirSync` from a broken dynamic `await import("fs")` inside a non-async function (TS1308 compile error) to a correct top-level static import alongside `readFileSync`, `writeFileSync`, and `existsSync`. This is fully consistent with:

- **ESM import conventions** — the project is ESM-only (`"type": "module"`) with explicit `.js` extensions for intra-project imports. Static imports from Node built-ins (`fs`, `crypto`, `path`) are the canonical pattern.
- **Synchronous persistence model** — `save()` is a synchronous function; `mkdirSync` called before `writeFileSync` preserves the atomic write semantics of the custom JSON store.
- **Project stack** — no new dependencies, no dependency changes. The persistence layer remains the custom `load`/`save` pair backed by `~/.cartographer/graph.json`.

### Cross-Cutting Concerns
- **Single consumer**: `src/cli.ts` is the only module that imports from `src/store/graph.ts`. It uses `load`, `addNode`, `link`, `removeNode`, `exportMarkdown`, `graphStats`, `mostConnectedNode`, and `listNodeTitles` — none of which changed API shape.
- **No surface change**: The public exports and their signatures are unchanged. All downstream callers function identically.
- **No data format change**: The graph.json schema is unchanged.
- **Test coverage**: Regression guard exists in both `src/store/graph.test.ts` (CART-B01-specific) and `src/__tests__/graph.test.ts` (order-verification). Two independent test files provide defense-in-depth.

### Operational Impact
| Category | Assessment |
|----------|------------|
| data-loss | None — save() writes the same JSON format |
| breaking-change | None — no API signature changes |
| performance | None — static import is faster than dynamic import |
| surface-change | None — no new exports, no CLI changes |

### Deployment Notes
- No version bump required — this is a bug fix, not a feature change.
- No migration needed — data file format is unchanged.
- No security scan required — standard synchronous file I/O with no injection vectors.
- No containerization or CI/CD implications — the project has no Docker/CI pipeline.

### Follow-Up Items for Future Sprints
1. **Concurrency safety** — The known technical debt "no concurrency safety on read-modify-write" in `save()`/`load()` remains. The `addNode`, `link`, and `removeNode` functions do a load-modify-save cycle without file locking, which is unsafe for concurrent invocations of `carto`. This should be addressed in a future sprint.
2. **Unused dependencies** — `lowdb` and `enquirer` are listed as production dependencies but are not used in source code. Consider removing them.
3. **Missing eslint devDependency** — `eslint` is referenced in the lint script but not declared in devDependencies.

**Verdict:** Approved