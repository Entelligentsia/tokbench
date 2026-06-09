# CART-S01-T01: Fix mkdirSync static import and verify gates — Plan

## Objective

Verify that `src/store/graph.ts` correctly imports `mkdirSync` via a static top-level import and that `save()` is a plain synchronous function with no `await`. Then run the full gate suite to confirm the sprint must-have acceptance criteria are satisfied.

## Current State (Verified)

**`src/store/graph.ts` — line 2:**
```ts
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```
`mkdirSync` is already in the static `fs` import — no dynamic `await import()` anywhere.

**`save()` — lines 12-16:**
```ts
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```
Plain synchronous function; no `await` keyword present.

## Gate Verification Results

| Gate | Command | Result |
|------|---------|--------|
| TypeScript compile | `npm run build` | ✅ Exit 0 |
| Regression test | `npm test` | ✅ 31/31 tests pass (2 files) |
| Lint | `npm run lint` | ✅ Exit 0 |

## CLAUDE.md — Known Issues

The current `CLAUDE.md` "Known issues / in-progress" section contains only one entry:
> `link` resolves nodes by title; fuzzy/id lookup is on the roadmap but not yet started

There is no CART-B01 entry to remove or mark resolved. No CLAUDE.md change is required.

## Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `mkdirSync` in top-level static `import { … }` from `"fs"` | ✅ Met |
| 2 | `save()` contains no `await` keyword | ✅ Met |
| 3 | `npm run build` exits 0 | ✅ Met |
| 4 | `npm test` exits 0 — regression guard passes | ✅ Met (6 tests in `src/store/graph.test.ts`) |
| 5 | `npm run lint` exits 0 | ✅ Met |
| 6 | CART-B01 known-issue entry removed/marked from CLAUDE.md | N/A — no such entry exists |

## Conclusion

The fix for CART-B01 is already in place in the working tree. All six acceptance criteria are satisfied. No further code changes are required.