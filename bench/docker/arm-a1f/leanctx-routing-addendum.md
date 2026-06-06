
<!-- project-routing: forge (tokbench arm-a1f) -->
## Forge Project Routing (project-specific)

This project runs forge workflows. When a workflow step prescribes a command,
execute it through lean-ctx — the routing changes ONLY which tool runs the
call, never the step itself, its order, or the artifacts it writes.

| Workflow prescribes | Execute as |
|---|---|
| `node .forge/tools/<tool>.cjs <args>` | `ctx_shell({ command: "node .forge/tools/<tool>.cjs <args>" })` |
| `npm run build` / `npm test` / `npm run lint` | `ctx_shell({ command: "<cmd>" })` |
| `git <args>` | `ctx_shell({ command: "git <args>" })` |
| Read a file (personas, docs, source) | `ctx_read({ path, mode: "auto" })` |
| Research: Glob / Grep / Read | `ctx_find` / `ctx_grep` / `ctx_read` |
| `forge_store` / `forge_artifact` / `forge_preflight` | **unchanged — never reroute** |
<!-- /project-routing -->
