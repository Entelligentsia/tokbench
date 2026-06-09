# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

(standalone review)

---

**Verdict:** Approved

---

## Review Summary

The plan is sound and correctly scoped. The code fix is already in place — `mkdirSync` is imported statically from `"fs"`, `save()` is synchronous with no `await`, and all three gate commands pass. The plan's primary remaining deliverable is removing the stale Known Issues entry from `README.md`, which is correctly identified.

## Feasibility

The approach is realistic and well-scoped. The plan correctly identifies that no code changes are needed — only a documentation update to `README.md`. All verification has been independently confirmed:

- `src/store/graph.ts` line 2: `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` ✅
- `save()` contains zero `await` keywords ✅
- `mkdirSync(dir, { recursive: true })` is called before `writeFileSync` ✅
- `npm run build` exits 0 ✅
- `npm test` passes (31 tests, 2 files) ✅
- `npm run lint` exits 0 ✅
- Regression guards exist in both `src/store/graph.test.ts` (CART-B01-specific) and `src/__tests__/graph.test.ts` (broader coverage) ✅

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — plan states "not required", which matches the task spec.
- **Migration entry targets correct?** N/A — no data model changes.
- **Security scan requirement acknowledged?** Yes — plan states "not required", correctly noting no new dependencies or security-sensitive code paths.

## Security

No security concerns. The change is a bug fix replacing a broken dynamic import with a correct static import. No new attack surface, no input validation changes, no network-facing code.

## Architecture Alignment

- The static import pattern follows Node.js ESM best practices — all `fs` functions used synchronously are imported at module top level, exactly as the project conventions require.
- `save()` remains a pure synchronous function with no side-effect coupling beyond file I/O.
- No schema changes, no `additionalProperties` concerns.

## Testing Strategy

Adequate. Two test files provide regression coverage:

1. **`src/store/graph.test.ts`** — CART-B01-specific guard verifying `mkdirSync` is called AND called before `writeFileSync` (using `invocationCallOrder`).
2. **`src/__tests__/graph.test.ts`** — Broader coverage: `save()` calls `mkdirSync` before `writeFileSync`, `mkdirSync` called even when dir exists, correct directory path, plus full coverage of `addNode`, `link`, `removeNode`, `load`, `exportMarkdown`, `graphStats`, `mostConnectedNode`.

The plan correctly identifies the gate suite (`build + test + lint`) as sufficient verification for this change.

---

## If Approved

### Advisory Notes

1. **File reference discrepancy**: The task prompt's acceptance criterion #6 references `CLAUDE.md` ("The 'Known issues' entry for this bug in `CLAUDE.md` is removed or marked resolved"), but the actual Known Issues table containing the bug description is in `README.md` (line 64). `CLAUDE.md` has no CART-B01 entry — its only known issue is about title-based lookup. The plan correctly targets `README.md`. During implementation, update `README.md` and consider whether `CLAUDE.md` should also gain a resolution note for completeness, though it's not required by the current state of the file.

2. **Test count**: The plan states "31 tests (6 in `graph.test.ts`, 25 in `graph.test.ts`)" — the actual breakdown is 6 in `src/store/graph.test.ts` and 25 in `src/__tests__/graph.test.ts`. This is a minor wording issue in the plan's success metrics, not a functional concern.

3. **Both test files should be re-run** after the README.md change to confirm no regressions, as the plan correctly notes in its "Verification Re-run" step.