# ARCHITECT APPROVAL — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Architectural Review

### Implementation Alignment
The fix is minimal and correct — `mkdirSync` was moved from a dynamic `await import()` call to a static ESM import on line 2 of `src/store/graph.ts`, alongside `readFileSync`, `writeFileSync`, and `existsSync`. This aligns with the project's ESM-only stack (`"type": "module"` in package.json, `module: ESNext` in tsconfig.json) where all `fs` functions are imported statically at the top of the module.

### Cross-Cutting Concerns
- **No new dependencies** introduced. The `fs` module was already a static import for other functions.
- **No API surface changes**. `save()`, `load()`, `addNode()`, `link()`, `removeNode()`, `exportMarkdown()` all retain identical signatures and behavior.
- **No data model changes**. The `~/.cartographer/graph.json` format is untouched.
- **No deployment changes**. No version bump required; the fix is transparent to users.

### Operational Impact
- **Category**: surface-change (internal only — no user-visible API change)
- **Deployment**: No action required. The fix is a compile-correctness and runtime-safety improvement only.
- **Migration**: None needed. Existing graph data files are fully compatible.

### Gate Verification (re-executed independently)
| Gate | Result |
|------|--------|
| `npm run build` (tsc) | ✅ Exit 0 — clean compilation |
| `npm test` (vitest run) | ✅ 31/31 tests pass including CART-B01 regression guard |
| `npm run lint` (eslint src) | ✅ Exit 0 — no errors |
| CART-B01 absent from CLAUDE.md known-issues | ✅ Confirmed |

### Technical Debt (pre-existing, not introduced)
- Node update method still absent (cannot edit existing nodes)
- Title-only lookup (no fuzzy/ID-based search)
- Edge weight always 1 (no weighted edges)
- No concurrency safety on read-modify-write cycles

None of these are introduced or worsened by this task.

**Verdict:** Approved

## Deployment Notes
- No version bump or migration required
- The fix is transparent: mkdirSync is now imported statically, eliminating the runtime error when saving graphs to directories that don't yet exist
- No user action needed post-deployment

## Follow-Up Items for Future Sprints
- Consider adding node update capability (most requested missing feature per technical debt list)
- Consider adding concurrency guards around load-modify-save cycles to prevent data loss under parallel CLI invocations