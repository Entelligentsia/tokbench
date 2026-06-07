# ARCHITECT APPROVAL — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Scope
Verification-only task confirming that the CART-B01 mkdirSync static import fix is correctly implemented and all regression guard tests are functioning. No source files were modified during this task — the fix was already in place.

## Architectural Review

### Implementation Alignment
- **Static import verified**: `src/store/graph.ts` line 2 declares `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"`. This is a module-level static import — no dynamic `await import("fs")` pattern exists anywhere in the file. ✅
- **Synchronous save() confirmed**: The `save()` function (lines 12–16) calls `mkdirSync(dir, { recursive: true })` on line 15, then `writeFileSync(DATA_PATH, ...)` on line 16. The function returns `void` with no `await` keyword. ✅
- **Correct call ordering**: `mkdirSync` is unconditionally called before `writeFileSync`, ensuring the directory `~/.cartographer/` exists before any file write is attempted. ✅

### Cross-Cutting Concerns
- **No module coupling impact**: The persistence layer (`load`/`save`) is self-contained within `graph.ts`. No other modules import `save` or `mkdirSync` directly.
- **No API surface change**: All public exports (`addNode`, `link`, `removeNode`, `exportMarkdown`, `graphStats`, `listNodeTitles`, `mostConnectedNode`) have unchanged signatures.
- **No schema change**: No modifications to `.forge/store/` or `.forge/config.json`.

### Operational Impact
- **Distribution**: No user action required — internal bug verification only.
- **Backwards compatibility**: Fully compatible. No configuration, data model, or CLI behaviour changes.
- **Deployment**: No special steps. The single-environment local CLI model is unaffected.
- **Data loss risk**: None. The `mkdirSync({ recursive: true })` pattern is idempotent and race-free for single-process CLI usage.

### Regression Prevention
- `src/store/graph.test.ts` — CART-B01 guard uses `invocationCallOrder` assertions (gold standard for call ordering verification).
- `src/__tests__/graph.test.ts` — 3 additional save() ordering tests covering mkdirSync call count, directory path, and call sequencing.
- Both test files include explanatory comments documenting the CART-B01 bug and fix rationale.

### Independent Verification Results
| Gate | Result |
|------|--------|
| `npm test` (vitest run) | ✅ 31/31 tests pass |
| `npm run build` (tsc) | ✅ Exit 0, no TS1308 errors |
| `npm run lint` (eslint src) | ✅ Exit 0, no warnings |

## Deployment Notes
No deployment action required. The fix is already in place in the codebase and verified correct. This task was purely confirmatory.

## Follow-Up Items
1. **Concurrency safety** — The known technical debt item "No concurrency safety on read-modify-write" remains open. The `load()` → mutate → `save()` pattern is safe for single-process CLI usage but would need locking for any future concurrent access. Recommend tracking in a future sprint if multi-process scenarios become relevant.
2. **enquirer dependency** — Listed in package.json but unused in source code. Recommend pruning in a future sprint to reduce attack surface.
3. **Weighted edges** — Edge weight is hardcoded to `1`. If weighted edges become a feature, a schema change will be required.

**Verdict:** Approved