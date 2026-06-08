# PLAN REVIEW — CART-S01-T01: Fix mkdirSync static import and verify gates

🔍 Reviewer: cartographer Supervisor (standalone review)

---

## Verdict: **Approved** (with advisory notes)

The plan is sound in its verification approach, though its diagnosis overstates the severity of the issue given the current codebase state.

---

## 1. Correctness

**The plan correctly identifies the verification steps needed**, but its framing of the problem is inaccurate:

- **Claim**: "Fix the incomplete `import type` statement for Graph/Node/Edge" and "malformed static import statements"
- **Reality**: As of the current working tree, ALL imports in `src/store/graph.ts` are already syntactically correct:
  ```typescript
  import { randomUUID } from "crypto";
  import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
  import { join } from "path";
  import type { Graph, Node, Edge } from "../types.js";
  ```
  These are well-formed. `mkdirSync` is already in the named import list on line 2. The `import type` statement on line 4 is complete with `{ Graph, Node, Edge }` and the `"../types.js"` module specifier.

- **The task prompt is more honest**: "At plan time the static-import fix and the mkdirSync call inside `save()` already appear to be in place in the working tree. This task's primary work is to verify that state." This is accurate.

- **The only actual code change needed** was adding `save` to the re-export line (`export { load }` → `export { load, save }`), which is already in place per commit `beb4f9d`.

**Impact on plan quality**: The verification steps (run `tsc`, run tests, confirm build) remain valid and necessary even though the imports don't need fixing. The plan would be stronger if it acknowledged that the primary work is verification rather than repair.

## 2. Security

No concerns. This is a pure import-fix/verification task:
- No auth, input validation, or data sanitization changes
- No network or external I/O introduced
- The `DATA_PATH` and `mkdirSync(dir, { recursive: true })` pattern is correct per architecture guardrails

## 3. Architecture

**Aligned with established patterns:**
- Named imports from Node built-ins (`fs`, `path`, `crypto`) ✅
- ESM style with `.js` extensions in type imports ✅
- `types.ts` as single source of truth ✅
- `save()` is synchronous — no `await` — correct per CART-B01 regression guard ✅
- `mkdirSync` called before `writeFileSync` ✅

## 4. Conventions

**Checklist compliance (per stack-checklist.md):**
- [x] ESM imports use `.js` extensions → `import type { … } from "../types.js"` is correct
- [x] `"type": "module"` in `package.json` — no CommonJS mixing
- [x] `tsconfig.json` `strict: true` — not modified, retained
- [x] Test framework is vitest — no Jest/Mocha introduced
- [x] `fs` mock pattern uses `importOriginal` async — consistent
- [x] `save()` regression guard (mkdirSync before writeFileSync) — present in `src/store/graph.test.ts`

**Minor gap**: The plan does not mention lint (`npm run lint`) as an acceptance criterion, though the task prompt's AC5 requires it. This is a small omission.

## 5. Business Rules

No data model changes. Node/Edge/Graph interfaces untouched. No breaking changes to persistence format.

## 6. Testing Strategy

The plan calls for:
- `npx tsc --noEmit` — **good**, would catch import/syntax errors
- `npm test` (31 tests) — **good**, covers regression guard
- `npm run build` — **good**, end-to-end build verification

**Missing from plan** (present in task prompt AC5): `npm run lint` should be listed as a gate to verify. Currently lint passes (`eslint src` exits 0), but it should be in the acceptance checklist.

## Advisory Notes

1. **The plan overstates the bug.** Describing the imports as "malformed" and "incomplete" is inaccurate given the current codebase. The PLAN should be updated to reflect that the primary deliverable is *verification* that the imports are correct, not *repair* of broken imports. The task prompt gets this right; the plan does not.

2. **Acceptance criterion AC6** (remove/clear the known-issues entry in `CLAUDE.md`) is mentioned in the task prompt but absent from the plan's acceptance criteria. This should be included.

3. **The plan misses the `export { load, save }` change.** The actual code delta was extending the re-export line. While this is trivial, the plan should document all intended changes, no matter how small.

4. **No concurrency safety concern addressed.** The project's known technical debt lists "No concurrency safety on read-modify-write." While this is out of scope for this task, the plan should acknowledge it as known debt that this fix does not address.

---

## Summary

The verification approach is correct. The actual imports are already fixed. The plan would benefit from more honest framing (verification vs. repair) and should include all task acceptance criteria (lint gate, CLAUDE.md cleanup, export change). These are advisory — the plan is implementable as-is because the verification steps will confirm the current correct state.