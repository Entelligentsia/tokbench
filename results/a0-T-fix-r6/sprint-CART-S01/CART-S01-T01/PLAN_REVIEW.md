# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01 *(standalone review)*

---

**Verdict:** Approved

---

## Review Summary

The plan is a straightforward verification task for an already-applied code fix. Independent verification of `src/store/graph.ts` confirms `mkdirSync` is in the static top-level import, `save()` is synchronous with no `await`, and all three gate commands (build, test, lint) pass cleanly. The plan is correctly scoped and realistic.

## Feasibility

The approach is realistic and correctly scoped. The plan identifies the single file (`src/store/graph.ts`) as the code target and `CLAUDE.md` as the documentation target. The verification steps (three gate commands) are appropriate and sufficient. The existing CART-B01 regression guard in `graph.test.ts` directly validates the key property (mkdirSync called before writeFileSync).

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — plan states "not required" which is correct (this is a bug fix + docs update, no API change).
- **Migration entry targets correct?** N/A — no migration involved.
- **Security scan requirement acknowledged?** Yes — "not required" is correct; this is a local filesystem import fix with no surface change.

## Security

No security concerns. The change replaces a dynamic `await import("fs")` with a static `import { mkdirSync } from "fs"`. This reduces, not increases, attack surface. No plugin shipping, no network dependency, no prompt injection vectors.

## Architecture Alignment

- The approach follows established patterns: single static import from `"fs"`, pure functions in `graph.ts`, no classes or singletons.
- The fix preserves the existing import line structure — `mkdirSync` was added to the existing `import { readFileSync, writeFileSync, existsSync } from "fs"` rather than creating a second import statement. Confirmed: only one `from "fs"` import exists in the file.
- No schema changes, so `additionalProperties: false` concern is N/A.

## Testing Strategy

The testing strategy is adequate and well-targeted:

1. **CART-B01 regression guard**: The test in `src/store/graph.test.ts` uses `vi.mock("fs")` with invocation-order spies to assert `mkdirSync` is called before `writeFileSync` — this directly validates the core bug fix property.
2. **Gate commands**: `npm run build` (TypeScript compilation), `npm test` (unit tests including regression guard), `npm run lint` (style checks) — all three pass (verified independently).
3. **Manual verification**: The plan calls for code inspection to confirm the static import and absence of `await`, which I verified independently.

---

## If Approved

### Advisory Notes

1. **CLAUDE.md status**: The plan says "Update CLAUDE.md known-issues section to reflect resolved state," but the current CLAUDE.md has no CART-B01/mkdirSync entry. This is already satisfied — either it was already removed or was never there. The acceptance criterion says "removed or marked resolved" and the current state meets it. The Engineer should confirm during implementation that no docs change is actually needed rather than attempting a non-existent edit.
2. **Minor observation**: The `save()` function uses `mkdirSync(dir, { recursive: true })` which is the correct approach — it creates the `.cartographer` directory if it doesn't exist and doesn't throw if it does. This is the right pattern for the fix.