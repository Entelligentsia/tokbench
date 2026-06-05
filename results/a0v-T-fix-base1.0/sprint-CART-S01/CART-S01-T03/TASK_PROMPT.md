# Task: CART-S01-T03 — Add comprehensive tests for exportMarkdown, link success, and load with data

## Context

Sprint CART-S01 addresses quality gaps in `src/store/graph.ts`. Tasks T01 and T02 fixed the `mkdirSync` static import bug and added directory-path assertion tests for `save()`. This task expands test coverage to the remaining untested code paths.

## Current coverage gaps

| Function | Missing coverage |
|----------|-----------------|
| `exportMarkdown()` | Zero tests — full feature untested |
| `link()` | Success path: creating an edge between two existing nodes, with and without label |
| `load()` | Parsing an existing graph file (only missing-file case is tested) |
| `save()` | Content verification: does written JSON contain the correct graph structure? |

## Scope

Add new `describe` blocks and test cases to `src/__tests__/graph.test.ts` covering:

1. **`exportMarkdown()`** — at minimum:
   - Produces well-formed markdown with `# Knowledge Map` header
   - Lists each node with its title, tags, and body
   - Renders outgoing links section when edges exist
   - Omits links section when a node has no outgoing edges
   - Handles label on edges

2. **`link()` success path**:
   - Returns an `Edge` with correct `from`, `to`, and `label` when both nodes exist
   - Edge without label has `label: undefined` and `weight: 1`

3. **`load()` with data**:
   - Returns a populated `Graph` when the file exists and contains valid JSON

4. **`save()` content verification**:
   - `writeFileSync` receives JSON string containing the serialized graph (nodes + edges)

## Acceptance criteria

- `npm test` passes with all new tests green (no regressions)
- `npm run lint` passes clean
- No production code changes — only `src/__tests__/graph.test.ts` is modified
- Each new `describe` block has ≥ 1 `it` case
- All mocks are reset between tests via `beforeEach`

## Constraints

- Offline-only: no network or database dependencies
- Use existing `vi.mock("fs")` and `vi.mock("crypto")` patterns already in the file
- Keep test bodies small and focused — one assertion per `it` where practical