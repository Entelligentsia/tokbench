# VALIDATION REPORT — CART-S01-T01
## Fix mkdirSync static import and verify gates

*(standalone review — not orchestrated)*

**Validator:** cartographer QA Engineer  
**Date:** 2026-06-06  
**Verdict:** ✅ **Approved**

---

## Acceptance Criteria Verdicts

### AC1 — `src/store/graph.ts` imports `mkdirSync` via a static top-level `import { … } from "fs"` — not via `await import(…)` anywhere.

**PASS**

Evidence — line 2 of `src/store/graph.ts`:

```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
```

Checked the full file: no `await import(` expression appears anywhere. There is exactly one `import … from "fs"` statement and it includes `mkdirSync`. No second `import "fs"` statement.

---

### AC2 — `save()` body contains no `await` keyword.

**PASS**

Evidence — `save()` as observed in source:

```typescript
function save(graph: Graph): void {
  const dir = join(process.env.HOME ?? "~", ".cartographer");
  mkdirSync(dir, { recursive: true });
  writeFileSync(DATA_PATH, JSON.stringify(graph, null, 2));
}
```

The function carries no `async` qualifier; no `await` appears in the body. `mkdirSync` is called **before** `writeFileSync` — correct ordering.

---

### AC3 — `npm run build` (`tsc`) exits 0 with no TypeScript errors.

**PASS**

```
$ npm run build
> cartographer@0.1.0 build
> tsc
[exit 0, zero output]
```

---

### AC4 — `npm test` exits 0 — all 31 tests pass, including the CART-B01 regression guard.

**PASS**

```
$ npm test
> cartographer@0.1.0 test
> vitest run

 ✓ src/store/graph.test.ts  (6 tests) 8ms
 ✓ src/__tests__/graph.test.ts  (25 tests) 6ms

 Test Files  2 passed (2)
      Tests  31 passed (31)
   Duration  218ms
```

CART-B01 regression guard (`addNode() calls mkdirSync before writeFileSync`) is in `src/store/graph.test.ts` and passes. The guard:
- Asserts `mkdirSyncSpy` was called (not zero invocations).
- Asserts `mkdirSyncSpy.mock.invocationCallOrder[0] < writeFileSyncSpy.mock.invocationCallOrder[0]`.

Both assertions green.

---

### AC5 — `npm run lint` exits 0 — zero ESLint violations.

**PASS**

```
$ npm run lint
> cartographer@0.1.0 lint
> eslint src
[exit 0, zero output]
```

---

### AC6 — `CLAUDE.md` `## Known issues / in-progress` section has no bullet for the `save()` / mkdirSync bug.

**PASS**

`CLAUDE.md` Known issues section contains exactly one bullet:

```
- `link` resolves nodes by title; fuzzy/id lookup is on the roadmap but not yet started
```

No mention of `save()`, `mkdirSync`, `await import`, or `CART-B01`. Criterion satisfied.

---

## Regression Check

All 31 pre-existing tests pass. No regressions introduced (task was a pure verification pass; no source files were modified).

---

## Nice-to-Have Coverage

The sprint requirements include an optional criterion: *"Add a `save()` unit test that verifies the directory path passed to `mkdirSync` matches `~/.cartographer`"*. This is **not implemented** — no test asserts the exact path argument. Per sprint requirements, this is a "nice-to-have" and does not affect the must-have verdict.

---

## Summary

All 6 must-have acceptance criteria confirmed passing by direct source inspection and live gate execution. The CART-B01 regression guard is present, specific, and green. No source modifications were required — the fix was already in place. Verdict: **Approved**.
