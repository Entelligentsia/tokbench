# ARCHITECT_APPROVAL — CART-S01-T01: Fix mkdirSync static import and verify gates

## Architectural Review

This is a verification-only task. The fix (`mkdirSync` static import, synchronous `save()`) was already present in the working tree before this sprint. All three gates (build, test, lint) have been independently re-verified during the approval phase and pass with exit code 0.

### Alignment with Architecture
- **Persistence model**: `save()` uses `mkdirSync(dir, { recursive: true })` followed by `writeFileSync(DATA_PATH, ...)`. This matches the project's synchronous, offline-only, local-file persistence contract defined in `engineering/architecture/stack.md`.
- **No async contamination**: `save()` returns `void` with zero `await` keywords, which is correct for this CLI tool — no server, no network I/O, no need for async filesystem operations.
- **Import style**: `mkdirSync` is statically imported at the top of the module (`import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` on line 2), consistent with the project's ESM style and TypeScript strict mode.

### Cross-Cutting Concerns
- **No cross-module impact**: `graph.ts` is the sole persistence module. The `load`/`save` functions are only consumed internally within `src/store/`. No CLI commands or other modules are affected.
- **No data model changes**: The `Graph`, `Node`, and `Edge` types are untouched.
- **No dependency changes**: No packages added or removed.

### Operational Impact
- **Version bump**: Not required — no behavior changes.
- **Deployment**: No container or CI/CD changes (project has neither).
- **Security**: No security-sensitive changes.
- **Performance**: No performance impact.

### Working-Tree Note
A pre-existing diff exists in `src/__tests__/graph.test.ts` (removal of "stats pluralisation logic" test block) and several prior sprint artifact files. These are NOT part of CART-S01-T01 and do not affect the mkdirSync verification. The 31 remaining tests all pass, including the CART-B01 regression guard for mkdirSync ordering.

**Verdict:** Approved