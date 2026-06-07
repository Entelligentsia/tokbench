# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🌿 *cartographer Supervisor*

**Task:** CART-S01-T01

---

**Verdict:** Approved

---

## Review Summary

The plan accurately describes a verification-only task: confirming that the `mkdirSync` static import fix in `src/store/graph.ts` is correctly in place and that all gate commands pass. Independent verification of the actual source code and gate execution confirms every acceptance criterion is met. The plan is correctly scoped, realistic, and complete.

## Feasibility

The approach is entirely realistic and correctly scoped. The plan correctly identifies that no code changes are needed — the fix is already in place. It targets the right file (`src/store/graph.ts`) and the right verification steps (build, test, lint). The risk noted in the task prompt about extending the existing `import { … } from "fs"` rather than adding a second import statement is addressed — the actual source code confirms a single import statement with `mkdirSync` included.

## Plugin Impact Assessment

- **Version bump declared correctly?** Yes — N/A, this is a bug fix verification, not a feature change
- **Migration entry targets correct?** N/A — no migration needed
- **Security scan requirement acknowledged?** Yes — correctly noted as not required (no security implications)

## Security

No security risks introduced. This is a bug fix that corrects a static import pattern. The `save()` function writes to `~/.cartographer/graph.json` using `mkdirSync` with `{ recursive: true }` — this is standard Node.js file I/O with no injection vectors. The data path uses `process.env.HOME ?? "~"` which matches the established project pattern.

## Architecture Alignment

- The plan preserves the established pattern: `graph.ts` exports pure functions only, no singleton state, no module-level side effects beyond the `DATA_PATH` constant.
- `mkdirSync` is correctly placed inside the `save()` function as a synchronous call before `writeFileSync`, maintaining the project's synchronous persistence model.
- The single static import line `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` follows the project's ESM + TypeScript conventions.
- No `additionalProperties: false` schema changes involved.

## Testing Strategy

The testing strategy is adequate and well-structured:

1. **Regression guard test** in `src/store/graph.test.ts` uses `vi.mock` with `importOriginal` pattern (matching stack checklist) and verifies `mkdirSync.mock.invocationCallOrder[0] < writeFileSync.mock.invocationCallOrder[0]` — a proper ordering assertion.
2. **Complementary test** in `src/__tests__/graph.test.ts` adds three more `save()` tests (call order, always-calls-even-when-exists, correct directory path), providing defense-in-depth.
3. **Gate suite** (build + test + lint) provides full coverage. All 31 tests pass, `tsc` compiles cleanly, and ESLint reports 0 errors.

The plan correctly identifies that no additional tests are needed — the existing regression guard and gate suite provide sufficient verification.

---

## If Approved

### Advisory Notes

1. The lint warning in `lib/schema-loader.cjs` is unrelated to this task but should be tracked as tech debt for cleanup.
2. The `lowdb` and `enquirer` dependencies listed in `package.json` remain unused — per stack checklist, these should either be removed or integrated intentionally.
3. The concurrency safety concern noted in technical debt (read-modify-write without locking on `save()`) is not addressed by this task and remains a pre-existing risk, especially for the `load() → modify → save()` pattern in `addNode()`, `link()`, and `removeNode()`.