# PLAN REVIEW — CART-S01-T01 (standalone review)

**Reviewer:** cartographer Supervisor (ORACLE)
**Date:** 2026-06-09

## Verdict: ✅ Approved

The plan is well-scoped, achievable, and directly addresses the CART-B01 bug fix verification. All acceptance criteria are independently verified against the actual source code.

---

## Correctness

- **Static import verified**: `src/store/graph.ts` line 2 reads `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"`. This is the correct static import form — the bug (dynamic `await import("fs")` inside a sync function) is absent.
- **No `await` in graph.ts**: `grep -rn 'await' src/store/graph.ts` returns zero matches. The `save()` function is fully synchronous as required.
- **`mkdirSync` called before `writeFileSync`**: The `save()` function calls `mkdirSync(dir, { recursive: true })` on line 14, then `writeFileSync(DATA_PATH, ...)` on line 15. Order is correct.
- **Regression guard exists**: `src/store/graph.test.ts` contains a dedicated test (`addNode() calls mkdirSync before writeFileSync`) that verifies call ordering via `mock.invocationCallOrder`, which would catch any regression of the CART-B01 bug.

## Security

- No security concerns. This is a local-only CLI tool with no network surface, no user input passed to shell commands, and no dynamic imports. The fix eliminates a pattern (`await import("fs")` inside a synchronous function) that was a compile-time error, not a runtime vulnerability.

## Architecture

- The fix aligns with the stack checklist guardrail: *"`save()` must call `mkdirSync(dir, { recursive: true })` before `writeFileSync`"*.
- `graph.ts` continues to export pure functions only — no singleton state, no module-level side effects.
- Import style is consistent with ESM conventions and the project's `.js` extension policy.

## Conventions

- All intra-project imports use `.js` extensions as required by ESM.
- No `class` definitions introduced.
- No database or network imports added.
- The regression guard test follows the established `vi.mock("fs", async (importOriginal) => { ... })` pattern from the testing checklist.

## Business Rules

- Node lookup remains case-sensitive by title — no change.
- Edge weight remains hardcoded to `1` — no change.
- Data path pattern (`process.env.HOME ?? "~"`) unchanged.

## Testing

- **Build gate**: `npm run build` → exit 0, no TypeScript errors. ✅
- **Test gate**: `npm test` → 31/31 tests pass, including the CART-B01 regression guard. ✅
- **Lint gate**: `npm run lint` → exit 0, no warnings. ✅
- Regression guard explicitly tests call ordering (`mkdirSync` before `writeFileSync`) using `mock.invocationCallOrder`. ✅

## CLAUDE.md Known Issues

- The plan's acceptance criterion asks for CART-B01 entry to be "removed or marked resolved" in CLAUDE.md. No CART-B01 entry exists in the current known issues section — it lists only the title-lookup limitation. This criterion is vacuously satisfied (no incorrect entry to remove).

## Advisory Notes

1. **Unused dependencies**: `lowdb` and `enquirer` remain in `package.json` as declared but unused. This is pre-existing technical debt, not introduced by this task, but worth noting.
2. **The plan's Objective and Approach sections are empty** — they contain no prose. This is a minor formatting issue that doesn't affect the substance, but for future plans, these sections should contain a brief description.
3. **No concurrency safety**: The read-modify-write pattern in `addNode()`, `link()`, and `removeNode()` remains unprotected. This is acknowledged in the project's technical debt list and is not in scope for this task.