# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

*(standalone review)*

---

**Verdict:** Approved

---

## Review Summary

The plan accurately describes a verification task for an already-correct codebase state. Independent inspection of `src/store/graph.ts` confirms all three core claims: `mkdirSync` is in the top-level static import, `save()` is synchronous with no `await`, and `mkdirSync` is called before `writeFileSync`. The gate suite (build, test, lint) steps are correctly specified. One minor gap: CLAUDE.md has no CART-B01 known-issues entry to remove, making step 3 a no-op.

## Feasibility

The approach is realistic and correctly scoped. The code changes (if any) are limited to a single file (`src/store/graph.ts`), and inspection confirms the fix is already in place. The plan correctly reclassifies this as a verification exercise rather than a modification task. The three gates — build, test, lint — are the standard verification steps for this project. The regression guard test in `src/store/graph.test.ts` properly validates call ordering of `mkdirSync` before `writeFileSync`.

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — no version bump required (internal verification + documentation only)
- **Migration entry targets correct?** N/A — no user-facing changes
- **Security scan requirement acknowledged?** Yes — correctly declared as not required

## Security

No security concerns. The changes are limited to verifying existing synchronous file I/O patterns and updating documentation. The `mkdirSync(dir, { recursive: true })` call with an environment-derived path (`process.env.HOME`) is the existing pattern and poses no new attack surface. No plugin hooks, no Markdown injection, no network calls.

## Architecture Alignment

- The plan follows established patterns: pure functions in `graph.ts`, no classes, no singleton state.
- `save()` remains a plain synchronous function as per project conventions.
- No schema changes to `.forge/store/` or `.forge/config.json`.
- The plan correctly scopes file impact to `src/store/graph.ts` and `CLAUDE.md`.

## Testing Strategy

Testing is adequate:
- **Syntax check**: Covered by `npm run build` (TypeScript compilation)
- **Regression guard**: The CART-B01 test in `src/store/graph.test.ts` verifies `mkdirSync` is called before `writeFileSync` with call-order assertions
- **Lint**: `npm run lint` for static analysis
- All three gates must exit 0 per acceptance criteria

---

## If Approved

### Advisory Notes

1. **No CART-B01 entry in CLAUDE.md**: The "Known issues" section of `CLAUDE.md` currently contains only a note about `link` resolving by title (no fuzzy/ID lookup). There is no CART-B01 entry to remove or mark resolved. The implementor should verify this and document that the entry was either never added or already removed, rather than searching for a nonexistent entry.
2. **"Files to Modify" table is slightly misleading**: `src/store/graph.ts` is listed but the "change" column says "Verify existing static import includes mkdirSync" — no actual code modification is needed. A "Files to Verify" label would be more precise, but this is cosmetic.
3. **Consider adding an explicit negative test**: The regression guard verifies `mkdirSync` is called before `writeFileSync`, but doesn't test what happens if the directory already exists (i.e., that `mkdirSync(dir, { recursive: true })` is idempotent). This is a non-blocking suggestion — `recursive: true` handles this correctly per Node.js semantics.