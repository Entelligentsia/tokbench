# Architect Approval — CART-S01-T01

## Task: Fix mkdirSync static import and verify gates

## Architectural Review

### Implementation Alignment

The fix is architecturally sound. `mkdirSync` is imported as a single, top-level static import alongside the other `fs` functions on line 2 of `src/store/graph.ts`. There is no dynamic `import()` for `mkdirSync` and no duplicate import anywhere in the file. The `save()` function remains a plain synchronous void function — zero `await` keywords exist in graph.ts — which is consistent with the project's offline-only, synchronous persistence model documented in `engineering/architecture/stack.md`.

### Cross-Cutting Concerns

- **No cross-module impact.** The `graph.ts` module is self-contained; its `load`/`save` functions are the only touchpoints with the filesystem. No other module re-exports or wraps these imports.
- **No deployment changes.** The fix was already in place at task creation (git diff from origin/main is empty). No version bump, no migration, no containerization change required.
- **No security surface.** `mkdirSync` with `{ recursive: true }` on a user-home path is the existing, safe pattern. No new paths are introduced.

### Operational Impact

- **Deployment:** None — no new dependencies, no config changes, no data format changes.
- **Regeneration:** No user action needed.
- **Security scan:** Not required.

### Independent Verification (Architect)

| Check | Command | Result |
|-------|---------|--------|
| Static import | `grep -n 'mkdirSync' src/store/graph.ts` | Line 2 only (import) + line 15 (call) — no duplicate, no dynamic |
| No await | `grep -c 'await' src/store/graph.ts` | 0 matches |
| Build | `npm run build` | Exit 0 |
| Tests | `npm test` | 31/31 pass including CART-B01 regression guard |
| Lint | `npm run lint` | Exit 0 |

**Verdict:** Approved

## Deployment Notes

No deployment action required. The fix was pre-existing; this task was a verification guard.

## Follow-Up Items

- None. The CART-B01 regression guard in `src/store/graph.test.ts` (using `invocationCallOrder`) will prevent re-introduction of the dynamic-import regression.