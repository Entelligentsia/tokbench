# CODE_REVIEW.md for CART-S01-T01

**Review type:** Standalone review  
**Reviewer:** 🌿 cartographer Supervisor  
**Task:** Fix mkdirSync static import and verify gates  

---

## Verdict: ✅ Approved

All six acceptance criteria are independently verified. The task is verification-only — no material code change beyond adding `save` to the module exports.

---

## 1. Correctness

| Criterion | Claim | Independent Verification | Result |
|-----------|-------|--------------------------|--------|
| AC1: `mkdirSync` in top-level import | Line 2: `import { …, mkdirSync } from "fs"` | Read `src/store/graph.ts` line 2 — single static import, `mkdirSync` present, no second import statement | ✅ PASS |
| AC2: `save()` contains no `await` | `save()` is synchronous | Grepped file for `await` — zero matches; function signature is `function save(graph: Graph): void` | ✅ PASS |
| AC3: `npm run build` exits 0 | Build succeeds | Ran `npm run build` → exit 0, no TS1308 errors | ✅ PASS |
| AC4: `npm test` exits 0 | 31 tests pass | Ran `npm test` → 31/31 pass including regression guard | ✅ PASS |
| AC5: `npm run lint` exits 0 | No lint findings | Ran `npm run lint src/` → "No issues found", exit 0 | ✅ PASS |
| AC6: CART-B01 known issue removed | CLAUDE.md cleaned | No `await import` reference remains in CLAUDE.md | ✅ PASS |

### Regression guard detail

Two test files exercise the ordering invariant:

1. **`src/store/graph.test.ts`** — dedicated CART-B01 describe block; uses `vi.mock("fs")` with `importOriginal` pattern; asserts `mkdirSync.mock.invocationCallOrder[0] < writeFileSync.mock.invocationCallOrder[0]`.
2. **`src/__tests__/graph.test.ts`** — `save()` tests verify `mkdirSync` called before `writeFileSync`, called with correct dir path, and called even when directory exists.

Both confirm the critical ordering invariant.

---

## 2. Security

No security concerns. The `save()` function writes to `~/.cartographer/graph.json` using `join(process.env.HOME ?? "~", ".cartographer")` — no user-controlled paths, no injection vectors. `mkdirSync` with `{ recursive: true }` is the correct pattern.

---

## 3. Architecture

- `graph.ts` exports pure functions only (`load`, `save`, `addNode`, `link`, `removeNode`, `exportMarkdown`, `graphStats`, `listNodeTitles`, `mostConnectedNode`) — no singleton state, no module-level side effects. ✅
- I/O is confined to `load()` and `save()`; remaining functions compose them. ✅
- `types.ts` is the single source of truth for `Node`, `Edge`, `Graph` — no class hierarchies. ✅

---

## 4. Conventions

- ESM imports reference `.js` extensions (e.g. `from "../types.js"`). ✅
- `const` and arrow functions throughout; no classes. ✅
- No `require()` / CommonJS patterns. ✅

---

## 5. Business Rules

- `link()` resolves nodes by case-sensitive `title` — unchanged, correct per existing design. ✅
- Edge `weight` hardcoded to `1` — known tech debt, not in scope. ✅
- No data model changes. ✅

---

## 6. Testing

- 31 tests across 2 test files, all passing. ✅
- Regression guard for CART-B01 explicitly tests call ordering. ✅
- `beforeEach(() => vi.clearAllMocks())` present in mock-using describe blocks. ✅

---

## Advisory Notes (non-blocking)

1. **Tech debt — `enquirer`**: The `enquirer` dependency remains declared but unused in `src/`. Per project context, this is tracked. Not in scope for this task.
2. **Tech debt — Edge weight**: `weight: 1` is hardcoded in `link()`. Not in scope.
3. **Tech debt — No node update method**: Nodes cannot be edited after creation. Not in scope.

---

## Summary

This is a verification-only task. The code change (`export { load, save }` instead of `export { load }`) is minimal and correct. All acceptance criteria are met with independent confirmation. The regression guard tests for CART-B01 are well-structured and pass. No security, architecture, or convention issues found.