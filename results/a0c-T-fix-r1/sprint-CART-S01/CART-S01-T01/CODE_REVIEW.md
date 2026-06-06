# Code Review — CART-S01-T01 (standalone review)

**Verdict:** Approved

## Scope
Verification-only task: confirm `src/store/graph.ts` uses a static `mkdirSync` import with a synchronous `save()`, ensure `CLAUDE.md` has no stale CART-B01 known-issue entry, and prove the three gates (tsc, vitest, eslint) exit 0.

## Independent Verification

1. **Static import (correctness).** Confirmed `graph.ts` line 2:
   `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";`
   — a single static, top-level import. `grep` for `async`/`await` across the file returns nothing; there is no `await import('fs')` anywhere.

2. **Synchronous `save()` with correct ordering.** `save()` is a plain `void` function. `mkdirSync(dir, { recursive: true })` is called before `writeFileSync(DATA_PATH, ...)`. Verified by reading the actual source, not the report.

3. **Regression guard intact.** `src/store/graph.test.ts` retains the CART-B01 guard asserting `mkdirSync` was called and that its `invocationCallOrder` precedes `writeFileSync`'s. Test ran green.

4. **CLAUDE.md clean.** `grep` for `CART-B01` and `mkdirSync` in `CLAUDE.md` returns no matches — no stale Known-issues bullet. Step 2 was correctly anticipated as a no-op.

5. **Gates (independently re-run by me):**
   - `tsc --noEmit` → exit 0, zero TypeScript errors.
   - `vitest run` → **31 tests passing** across 2 files (`src/store/graph.test.ts` 6, `src/__tests__/graph.test.ts` 25).
   - `eslint src` → exit 0, zero violations.

6. **No data-model change.** `Graph`, `Node`, `Edge` types and the `graph.json` schema are untouched. No source files modified — consistent with a pure-verification task.

## Advisory Notes
- The plan-review advisory about hard-coding "31 tests" as an acceptance number was honoured in spirit — the count was reported from the actual vitest run, which matches (31). If tests are added later, the acceptance criterion should reference the live count rather than a frozen number.
- Pre-existing tech debt (no node update method, title-only lookup, fixed edge weight, unused `enquirer`, no read-modify-write concurrency safety) is out of scope for this task and remains untracked here.

No blocking findings. Plan steps fully executed and independently confirmed.
