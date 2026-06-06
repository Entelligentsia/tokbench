# PLAN — CART-S01-T01: Fix mkdirSync static import and verify gates

## Objective

Confirm that `src/store/graph.ts` uses a correct static top-level `import { mkdirSync }` from `"fs"` (replacing the prior `await import("fs")` inside a synchronous function), then run the full gate suite (`tsc`, `vitest run`, `eslint src`) and ensure `CLAUDE.md` carries no stale known-issue entry for this bug.

---

## Background

Bug CART-B01 was filed because `save()` in `graph.ts` used a dynamic `await import("fs")` inside a synchronous function body. This caused two problems:

1. **TypeScript TS1308 compile error** — `await` is illegal in a non-async function.
2. **Runtime failure** — `mkdirSync` was never actually called, so the `~/.cartographer/` directory was never guaranteed to exist before `writeFileSync`, risking ENOENT on first write.

At plan time the static-import fix and the synchronous `mkdirSync` call are **already present** in the working tree. The implementation phase for this task is therefore a verification pass, not a net-new code authoring pass. Any remaining corrections (e.g. a stale CLAUDE.md entry) are minor text edits only.

---

## Approach

### Step 1 — Static-import audit (`src/store/graph.ts`)

Confirm by reading the file:
- Line 2 (or equivalent): `import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"` — a single combined import, not a second `import` statement and not a dynamic `import()` call.
- `save()` body: contains `mkdirSync(dir, { recursive: true })` called before `writeFileSync`, with **no** `await` keyword anywhere in the function.

If either condition is violated:
- Merge `mkdirSync` into the existing `import { … } from "fs"` line (do not add a second import statement).
- Remove any `await import("fs")` expression.
- Remove any `async` qualifier from `save()`.

### Step 2 — CLAUDE.md cleanup

Inspect the `## Known issues / in-progress` section of `CLAUDE.md`.  
- If a bullet for the `save()` / `mkdirSync` / CART-B01 bug exists, remove it.  
- If it is already absent, no change is needed.

### Step 3 — Gate suite

Run all three gates in sequence and confirm each exits 0:

```
npm run build    # tsc — zero TypeScript errors
npm test         # vitest run — regression guard in graph.test.ts must pass
npm run lint     # eslint src — zero lint violations
```

If any gate fails, fix the root cause before proceeding (see Files to Modify below for scope).

---

## Files to Modify

| File | Change | Required? |
|------|--------|-----------|
| `src/store/graph.ts` | Verify static import + synchronous `mkdirSync` call; apply correction only if still wrong | Only if audit finds a violation |
| `CLAUDE.md` | Remove CART-B01 known-issue bullet if present | Only if bullet exists |

No other files require modification. All other acceptance criteria are satisfied by running the gate commands.

---

## Data Model Changes

None. This fix does not alter the `Graph`, `Node`, or `Edge` types, the JSON schema of `~/.cartographer/graph.json`, or any public API of `graph.ts`.

---

## Testing Strategy

The regression guard already exists in `src/store/graph.test.ts`:

```
describe("graph — CART-B01: mkdirSync called before writeFileSync in save()", ...)
  it("addNode() calls mkdirSync before writeFileSync ...")
```

This test:
- Mocks `fs.mkdirSync` and `fs.writeFileSync` via `vi.mock`.
- Calls `addNode()`.
- Asserts `mkdirSync` was called.
- Asserts `mkdirSync.invocationCallOrder[0] < writeFileSync.invocationCallOrder[0]`.

No new tests are required. The implementation phase must confirm this test passes under `vitest run`.

---

## Acceptance Criteria

1. `src/store/graph.ts` line imports `mkdirSync` in the static top-level `import { … } from "fs"` — no `await import(…)` present.
2. `save()` body contains no `await` keyword.
3. `npm run build` exits 0 — zero TypeScript errors.
4. `npm test` exits 0 — all 31 tests pass, including the CART-B01 regression guard.
5. `npm run lint` exits 0 — zero ESLint violations.
6. `CLAUDE.md` `## Known issues / in-progress` section has no bullet for the `save()` / mkdirSync bug.

---

## Operational Impact

- **Version bump:** not required — internal implementation correction, no public API change.
- **Regeneration:** no user action needed.
- **Security scan:** not required.
- **Materiality:** NOT material — docs and internal synchronous I/O fix only; no command surface or schema change.
