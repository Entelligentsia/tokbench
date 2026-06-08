# Architect Approval — CART-S01-T01

## Task
Fix mkdirSync static import and verify gates

## Architectural Review

### Source Code (production)
- `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — static named ESM import, no dynamic `await import()`. Confirmed correct.
- `save()` is synchronous; no `await` expressions. Correct.
- No production code changes were needed or made.

### Test Code (changed)
- `src/store/graph.test.ts`: `vi.fn(actual.mkdirSync)` → `vi.fn()` and `vi.fn(actual.writeFileSync)` → `vi.fn()` — pure mocks, no real filesystem side effects.
- `src/__tests__/graph.test.ts`: Already used pure `vi.fn()` mocks — no changes needed.
- Both suites contain `mkdirSync`-before-`writeFileSync` ordering guards (using `invocationCallOrder`) that will fail if the import pattern regresses.

### Cross-Cutting Concerns
- No impact on CLI, persistence, or other modules. Test-only change.

### Operational Impact
- **Category:** surface-change (test isolation improvement)
- **Version bump:** not required
- **Migration:** none
- **Security scan:** not required

### Verification
- All 31 tests pass (`vitest run` — 31 PASS, 0 FAIL)
- TypeScript compiles clean (`tsc --noEmit` — no errors)
- No new dependencies, no schema changes, no data model changes

**Verdict:** Approved

## Deployment Notes
None — test-only change with no production code modifications.

## Follow-Up Items for Future Sprints
- CART-B01 (tracked in known issues) is addressed by the static import and guard tests; consider closing.
- The co-located test suite (`src/store/graph.test.ts`) and integration suite (`src/__tests__/graph.test.ts`) have overlapping coverage — a future sprint could consolidate or clarify their distinct scopes.