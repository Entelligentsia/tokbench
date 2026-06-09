# Architect Approval — CART-S01-T01: Fix mkdirSync static import and verify gates

## Verdict

**Verdict:** Approved

## Rationale

The CART-B01 bug fix — ensuring `mkdirSync` is statically imported from `"fs"` rather than used dynamically — has been verified at every gate:

1. **Source correctness**: `src/store/graph.ts` line 2 imports `mkdirSync` statically alongside `readFileSync`, `writeFileSync`, `existsSync` from `"fs"`. The `save()` function is fully synchronous with no `await` keyword present anywhere in the file.

2. **Ordering correctness**: `mkdirSync(dir, { recursive: true })` is called before `writeFileSync(DATA_PATH, ...)`, ensuring the directory exists before writing — the root cause of CART-B01 is addressed.

3. **All gate commands pass cleanly**:
   - `npm run build` → exit 0 (TypeScript compilation clean)
   - `npm test` → 31/31 tests pass, including CART-B01 regression guard
   - `npm run lint` → exit 0 (no ESLint warnings or errors)

4. **No cross-cutting concerns**: The fix is confined to `src/store/graph.ts` import and the `save()` function. No other modules are affected. No schema changes, no API changes, no behavioural changes beyond fixing the bug.

5. **Architectural alignment**: The project uses synchronous Node.js `fs` APIs for local JSON persistence (per `stack.md`). No async patterns belong in this module. The static import is the correct architectural choice for the project's ESM-only, offline-only runtime.

6. **CLAUDE.md**: No CART-B01 entry existed to remove — criterion vacuously satisfied.

## Deployment Notes

- **No version bump required** — bug fix with no breaking changes.
- **No migration required** — no schema or data model changes.
- **No user action required** — the fix is in source code only.
- **Fully backwards compatible** — no API or behavioral changes beyond fixing the original bug.

## Follow-Up Items

- Consider adding a lint rule or CI check that flags dynamic `require()` of Node built-ins in ESM modules to catch similar issues earlier in future sprints.
- The project's known technical debts (no node update method, title-only lookup, edge weight always 1, no concurrency safety) remain out of scope for this task but should be tracked for future sprints.