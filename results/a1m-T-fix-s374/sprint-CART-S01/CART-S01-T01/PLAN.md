# CART-S01-T01: Fix mkdirSync static import and verify gates

## Objective
Confirm mkdirSync is statically imported from "fs" at the top of src/store/graph.ts, verify save() is synchronous and has no await, then run npm run build, npm test, and npm run lint to verify all gates pass. Update the CLAUDE.md known-issues entry once gates are green.

## Approach

### Verify and fix mkdirSync static import
- Inspect src/store/graph.ts to locate uses of mkdirSync
- Verify that mkdirSync is statically imported from "fs" at the top of the file
- If any await mkdirSync(...) calls exist, remove the await keyword
- Ensure no dynamic require/import of mkdirSync remains

### Verify save() method is synchronous
- Review src/store/graph.ts save() method implementation
- Confirm that save() does not have any await keywords
- Verify no async operations are embedded in save()

### Run verification commands
- Execute `npm run build` and verify build completes successfully
- Execute `npm test` and verify all tests pass
- Execute `npm run lint` and verify no linting errors

### Update known-issues entry
- If all gates pass, update the known-issues entry in CLAUDE.md to reflect the fix
- Document the issue and resolution

## Files to Modify

- src/store/graph.ts — ensure mkdirSync static import and synchronous save()
- CLAUDE.md — update known-issues entry after gates pass

## Data Model Changes

None. This task is focused on code hygiene and gate verification, not entity model changes.

## Testing Strategy

### Build verification
- Run `npm run build`
- Verify zero build errors

### Test verification
- Run `npm test`
- Verify all tests pass (no failures or skipped tests due to this change)

### Lint verification
- Run `npm run lint`
- Verify zero linting errors

### Regression testing
- All existing test suites should continue to pass
- No new functional behavior is introduced

## Acceptance Criteria

1. mkdirSync is statically imported from "fs" at the top of src/store/graph.ts
2. No await mkdirSync(...) calls exist
3. save() method is synchronous (no await keyword, no async operations)
4. `npm run build` completes successfully with zero errors
5. `npm test` passes all tests
6. `npm run lint` passes with zero errors
7. CLAUDE.md known-issues entry is updated to reflect resolution

## Operational Impact

- **Version bump:** not required
- **Regeneration:** no user action needed
- **Security scan:** not required
- ** Breaking-change** risk: low (import refactoring only)
- **Performance impact:** none
- **Data-loss risk:** none
- **Surface-change:** none (no API changes)