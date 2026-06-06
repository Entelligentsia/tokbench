# PLAN_REVIEW.md

**Task:** CART-S01-T01 — Fix mkdirSync static import and verify gates  
**Phase:** review-plan (standalone review)

## Summary

The plan describes a verification-only task: confirm that `src/store/graph.ts` already has the correct static `mkdirSync` import and synchronous `save()`, then run three gates. Independent code reading and gate execution confirms every claim in the plan is accurate.

## Independent Verification

| # | Acceptance Criterion | Plan Claim | Independent Finding | Status |
|---|----------------------|-----------|---------------------|--------|
| 1 | `mkdirSync` in top-level static import | Line 2 already has it | `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";` — confirmed | ✅ |
| 2 | `save()` contains no `await` | No `await` in file | grep confirms zero matches for `await` or `import(` | ✅ |
| 3 | `npm run build` exits 0 | TO VERIFY | Independently ran — exit 0, no TypeScript errors | ✅ |
| 4 | `npm test` exits 0 | TO VERIFY | 31/31 tests pass, CART-B01 regression guard included | ✅ |
| 5 | `npm run lint` exits 0 | TO VERIFY | Independently ran — exit 0, no violations | ✅ |
| 6 | CLAUDE.md known-issues entry removed | N/A — no entry exists | Confirmed: only entry is about fuzzy/id lookup, unrelated to CART-B01 | ✅ |

## Correctness

- The plan correctly identifies this as a verification-only task. No code changes are needed.
- The plan correctly identifies all six acceptance criteria and their current status.
- Gate ordering (build → test → lint) is sound: build catches compile errors before tests run.
- The regression guard in `src/store/graph.test.ts` verifies `mkdirSync` is called before `writeFileSync` using `mock.invocationCallOrder` — this is a robust ordering check.

## Security

- No security concerns. The task involves no input validation changes, no auth changes, no data sanitisation changes. The `mkdirSync` call ensures directory creation before file write, which is correct defensive behaviour.

## Architecture

- `mkdirSync(dir, { recursive: true })` before `writeFileSync` is the appropriate pattern for ensuring the directory exists before writing.
- The static import on line 2 correctly consolidates all `fs` named imports into a single statement — no duplicate import was added (the risk mentioned in the task context is avoided).
- `save()` returning `void` with no `async`/`await` is architecturally consistent with `graph.ts`'s pure-function, no-singleton-state design.

## Conventions

- ESM-compatible static import ✅
- `.js` extension in type import (`from "../types.js"`) ✅
- Pure function exports, no classes ✅

## Business Rules

- No business rule violations. Node/Edge data model unchanged.

## Testing

- Existing test suite (31 tests) provides adequate coverage for this verification task.
- The CART-B01 regression guard specifically validates the ordering invariant that was broken (mkdirSync never called).

## Advisory Notes

1. **AC6 marking**: The plan marks AC6 as ⬜ "NOT APPLICABLE" but it is actually already satisfied — there is no CART-B01 known-issues entry to remove, so the criterion is met. Recommend marking it ✅ (already satisfied) to avoid an implementer treating it as an open item.
2. **CART-B01 bug record**: The Forge store has no `CART-B01` bug record. This is consistent with the plan's claim. If this sprint expects bug lifecycle tracking, the bug record should be created separately.
3. **Concurrency**: The known technical debt item ("No concurrency safety on read-modify-write") applies to `save()` — `load()` then `save()` is not atomic. This is pre-existing and out of scope for this task, but worth noting.

---

**Verdict:** Approved