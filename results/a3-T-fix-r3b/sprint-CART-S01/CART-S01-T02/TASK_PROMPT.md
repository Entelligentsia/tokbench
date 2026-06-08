# CART-S01-T02: Add save() directory-path assertion test

**Sprint:** CART-S01
**Estimate:** S
**Pipeline:** default

---

## Objective

Extend the existing test suite with a unit test that confirms `mkdirSync` is called with
the correct directory path (`~/.cartographer`, i.e. `$HOME/.cartographer`) when `save()` is
invoked, closing the gap left by the CART-B01 regression guard.

## Acceptance Criteria

1. `src/store/graph.test.ts` contains a test that calls `addNode()` (or directly triggers `save()`) and then asserts `mkdirSyncSpy` was called with a path argument matching `path.join(process.env.HOME ?? "~", ".cartographer")`.
2. `npm test` exits 0 with the new test passing.
3. No existing tests are broken.
4. No new runtime dependencies are introduced.

## Context

The regression guard added for CART-B01 verifies ordering (mkdirSync before writeFileSync)
but does not verify the *argument* passed to `mkdirSync`. A typo or wrong path would pass
the existing guard but still result in a write failure. This nice-to-have test closes that
gap.

The `vi.mock("fs", …)` setup with spies for `mkdirSync` and `writeFileSync` is already
present in `src/store/graph.test.ts`. The new test can re-use that setup.

**Depends on:** CART-S01-T01 (gates must be green before adding tests).

## Source Files Involved

- `src/store/graph.test.ts` — add one `it(…)` block inside the existing `describe`

## Operational Impact

- **Version bump:** not required
- **Regeneration:** no user action needed
- **Security scan:** not required
