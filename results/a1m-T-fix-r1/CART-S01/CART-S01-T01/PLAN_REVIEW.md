# PLAN REVIEW — CART-S01-T01

**Task:** Fix mkdirSync static import and verify gates
**Reviewer:** 🌿 cartographer Supervisor
**Date:** 2026-06-05
**Mode:** Standalone review

---

## 1. Spec Compliance

The task requires six acceptance criteria. The plan addresses all six:

| # | Acceptance Criterion | Plan Coverage | Verified in Code |
|---|---|---|---|
| 1 | `mkdirSync` in top-level `import { … } from "fs"` | ✅ Step 1 of Approach | ✅ Line 2 of `graph.ts` — single import includes `mkdirSync` |
| 2 | `save()` contains no `await` | ✅ Step 1 of Approach | ✅ `save()` is `function save(graph: Graph): void` — fully synchronous, zero `await` |
| 3 | `npm run build` exits 0 | ✅ Gate execution step | Not yet run — correctly deferred to implementation |
| 4 | `npm test` exits 0 with regression guard | ✅ Gate execution step | Not yet run — correctly deferred |
| 5 | `npm run lint` exits 0 | ✅ Gate execution step | Not yet run — correctly deferred |
| 6 | CLAUDE.md known-issues entry removed/resolved | ✅ Documentation update step | ⚠️ See note below |

**Note on AC-6:** The current `CLAUDE.md` known-issues section contains only the title-lookup entry (`link resolves nodes by title; fuzzy/id lookup is on the roadmap`). There is no mkdirSync-related entry to remove. The plan's wording ("Remove or mark resolved any entry related to this bug") handles this correctly — if no such entry exists, the step is a no-op verification rather than a write. The engineer should confirm the absence rather than assuming it.

## 2. Correctness

- The plan correctly identifies that the fix is already in place and the primary work is verification. My independent code read confirms this — `mkdirSync` is in the static import, `save()` is synchronous, and call order is correct.
- The task's risk note states the import must be extended on the existing line rather than adding a second import. The code already satisfies this — there is exactly one `import … from "fs"` statement, and `mkdirSync` is in it.
- The "Files to Modify" table accurately labels `graph.ts` as "Verification only" and `CLAUDE.md` as "Update known-issues section" — correct scope.

## 3. Security

No security concerns. This task changes no auth, input validation, or data-sanitisation paths. The `mkdirSync`/`writeFileSync` calls use a fixed path derived from `process.env.HOME` with `join()` — no user-injectable path components.

## 4. Architecture

- Maintains the existing architectural pattern: pure functions, no singletons, no classes.
- No new dependencies introduced.
- No data model changes.
- Consistent with the project's offline-only design goal.

## 5. Conventions

- `.ts` extension with `.js` imports (ESM) — maintained.
- Pure functions in `graph.ts` — maintained.
- No new `class` usage — maintained.
- Error handling conventions unchanged.

## 6. Testing

- The three-gate strategy (build, test, lint) is complete for this scope.
- The existing regression guard in `graph.test.ts` (`invocationCallOrder` check) directly covers the core bug (mkdirSync called before writeFileSync).
- No new tests are proposed — appropriate since no code changes are needed; the existing test suite provides adequate regression coverage.

## 7. Edge Cases and Failure Modes

- **Concurrent access:** The project has documented tech debt ("No concurrency safety on read-modify-write"). This task does not address it, and correctly scopes out of it.
- **Missing HOME env var:** `process.env.HOME ?? "~"` fallback to literal `"~"` would cause `mkdirSync` to attempt creating a `~` directory. This is a pre-existing issue outside this task's scope, but worth noting.
- **CLAUDE.md entry absence:** As noted in AC-6, the known-issues section lacks a mkdirSync entry, so the "remove or mark resolved" step becomes a verification-of-absence step. The plan should be explicit about this to avoid implementation confusion.

## Advisory Notes

1. **Verification is not passive.** The plan lists `graph.ts` as "Verification only" — the engineer should treat verification as an active step: read the file, confirm the import statement includes `mkdirSync`, confirm `save()` has zero `await` keywords, and confirm call order. Do not assume the gate commands alone prove the fix.
2. **CLAUDE.md step may be a no-op.** If the known-issues section has no mkdirSync entry, the correct action is to confirm its absence and move on — not to add-and-then-remove an entry.
3. **The `~` fallback for HOME** is a latent bug (`mkdirSync("~", { recursive: true })` will create a literal `~` directory), but it is out of scope for this task.

---

**Verdict: Approved**

The plan is thorough, correctly scoped, and aligned with all six acceptance criteria. The fix is already in place in the working tree, the testing strategy is adequate, and no security, architecture, or convention issues exist. The advisory notes above are informational, not blockers.