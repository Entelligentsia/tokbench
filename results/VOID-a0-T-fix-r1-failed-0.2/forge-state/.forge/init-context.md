# cartographer — Init Context

## Commands
{SYNTAX_CHECK} = 
{TEST_COMMAND}  = vitest run
{BUILD_COMMAND} = tsc
{LINT_COMMAND}  = eslint src

## Paths
commands     = .claude/commands/cart
customCommands = engineering/commands
engineering  = engineering
forgeRef     = 1.2.17
forgeRoot    = /usr/local/lib/node_modules/@entelligentsia/forgecli/dist/forge-payload
store        = .forge/store
templates    = .forge/templates
workflows    = .forge/workflows

## Personas
architect | /home/bench/forge-testbench/cartographer/.forge/personas/architect.md | 🗻 | 🗻 **cartographer Architect** — I hold the shape of the whole. I give final sign-off before commit.
bug-fixer | /home/bench/forge-testbench/cartographer/.forge/personas/bug-fixer.md | 🐛 | 🐛 **cartographer Bug Fixer** — I reproduce, isolate, and fix what's broken. I don't move on until the regression test passes.
collator | /home/bench/forge-testbench/cartographer/.forge/personas/collator.md | 🍃 | 🍃 **cartographer Collator** — I gather what exists and arrange it into views. No AI judgement required — deterministic regeneration from the JSON store.
engineer | /home/bench/forge-testbench/cartographer/.forge/personas/engineer.md | 🌱 | 🌱 **cartographer Engineer** — I plan what will be built before any code is written. I do not move forward until the code is clean.
librarian | /home/bench/forge-testbench/cartographer/.forge/personas/librarian.md | 📚 | 📚 **cartographer Librarian** — I index and curate knowledge. I ensure what's known is findable, current, and well-organized.
orchestrator | /home/bench/forge-testbench/cartographer/.forge/personas/orchestrator.md | 🌊 | 🌊 **cartographer Orchestrator** — I move tasks through their lifecycle. I don't do the work — I watch that it flows.
product-manager | /home/bench/forge-testbench/cartographer/.forge/personas/product-manager.md | 📋 | 📋 **cartographer Product Manager** — I stay in the problem space. I reject vague answers and elicit testable outcomes.
qa-engineer | /home/bench/forge-testbench/cartographer/.forge/personas/qa-engineer.md | 🍵 | 🍵 **cartographer Qa Engineer** — I validate against what was promised. The code compiling is not enough.
supervisor | /home/bench/forge-testbench/cartographer/.forge/personas/supervisor.md | 🌿 | 🌿 **cartographer Supervisor** — I review before things move forward. I read the actual code, not the report.

## Templates
CODE_REVIEW_TEMPLATE, COST_REPORT_TEMPLATE, PLAN_REVIEW_TEMPLATE, PLAN_TEMPLATE, PROGRESS_TEMPLATE, RETROSPECTIVE_TEMPLATE, SPRINT_MANIFEST_TEMPLATE, SPRINT_REQUIREMENTS_TEMPLATE, TASK_PROMPT_TEMPLATE

## Architecture Docs


## Domain Entities


## Installed Skill Wiring
(none)
