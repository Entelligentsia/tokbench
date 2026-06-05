export const meta = {
  name: 'wfl:run-task',
  description: 'Code-orchestrated port of /forge:run-task — resolve the task pipeline, drive each phase (plan→review→implement→review→validate→approve→commit) through a subagent on its ROLE_TIER model (review/validate/approve→opus, plan/implement→sonnet, commit→haiku), hold the revision loop + verdict routing + escalation in JS.',
  whenToUse: 'Run a single Forge task through its full plan→implement→review→approve→commit pipeline via a deterministic JS driver instead of the LLM orchestrator. Pass the task id as args, e.g. args: "FORGE-S27-T01".',
  phases: [
    { title: 'Resolve', detail: 'one agent reads the task manifest + config, returns the resolved pipeline phases and pre-task status' },
    { title: 'Pipeline', detail: 'per phase: one subagent runs the gate + phase workflow + emits its own event; JS owns the phase index, revision counters, verdict routing, and escalation decision' },
    { title: 'Report', detail: 'summarise the terminal outcome — committed / escalated / blocked' },
  ],
}

// ---------------------------------------------------------------------------
// wfl:run-task — a code-orchestrated port of .forge/workflows/orchestrate_task.md
//
// Why a script: orchestrate_task.md is a deterministic phase FSM — a linear
// pipeline with review→revision back-edges, per-phase iteration caps, declarative
// pre-flight gates, and escalate-don't-continue on any failure. In the LLM
// orchestrator that loop is hand-run turn-by-turn. Here the JS holds the phase
// index, the revision counters, the verdict routing, and the escalation decision;
// subagents only run a single phase's workflow and write artifacts/events to disk.
//
// HOW THIS DIFFERS FROM wfl:run-sprint:
//   wfl:run-sprint ported the OUTER wave-sort FSM but delegated each whole task
//   to ONE orchestrate_task agent — it never decomposed the per-phase loop.
//   wfl:run-task decomposes that loop: one subagent PER PHASE. That is the only
//   version with a reason to exist (a single orchestrate_task agent == the
//   existing /forge:run-task, and adds nothing).
//
// SIDE-EFFECT OWNERSHIP — READ BEFORE EDITING:
//   The vanished orchestrate_task agent used to do a stack of shell-dependent
//   jobs for free. This script has NO filesystem/shell access, so each per-phase
//   subagent now owns them: preflight-gate, the phase workflow (which writes its
//   own artifacts + {PHASE}-SUMMARY.json + status), read-verdict (review phases),
//   token sidecar, friction drain, AND its own canonical phase event.
//
//   *** DELIBERATE DEVIATION from orchestrate_task.md's "the orchestrator is the
//   sole actor that calls store-cli emit" rule: here each phase subagent emits
//   its OWN phase event. This is defensible — the subagent is the only actor that
//   holds its own runtime attribution (model, provider, token usage). The JS
//   driver cannot run store-cli. This is a control-flow-authoritative port with
//   delegated telemetry, NOT a byte-for-byte reproduction of the emit contract.
//
//   Split start/complete emit contract: per orchestrate_task.md §Event Emission,
//   each phase subagent emits a start event (action="start") BEFORE executing its
//   phase workflow, then a complete event (action="complete") AFTER. The JS driver
//   delegates wall-time bracketing to the subagent: subagent notes startTimestamp,
//   runs the workflow, then computes durationMinutes = (endMs - startMs) / 60000
//   and includes it in the complete event. The start event carries a 0-duration
//   placeholder (startTimestamp == endTimestamp); the complete event carries the
//   real bracket. This mirrors the orchestrate_task.md start+complete pattern. ***
//
//   Honest fallback if per-phase emission ever proves too lossy: collapse to the
//   thin port (one agent reading orchestrate_task.md, == wfl:run-sprint.dispatchTask),
//   which inherits every side-effect for free. Do NOT ship a silently-lossy deep port.
//
// #21 STRUCTURAL LIMITATION — Progress-Monitor IPC:
//   The JS driver has no shell access (Workflow tool sandbox) and therefore CANNOT
//   write progress lines to a named pipe / Unix socket for the Progress-Monitor.
//   Wiring real-time progress telemetry to the Forge UI requires the forge-cli TS
//   layer to open the pipe before spawning the Workflow tool and inject the fd via
//   the Pi runtime's stdio bridging API — this is a host-layer concern, not a
//   JS workflow concern. Documenting here so future sprints know where the
//   architectural seam is. No implementation in this file is possible or correct.
//
// MODEL CLUSTER RESOLUTION (Gap #12 — FORGE-S28-T05):
//   Replaces the old hard-tier dispatch with three-cluster logic matching the prose:
//   • single cluster (ANTHROPIC_DEFAULT_OPUS_MODEL == ANTHROPIC_DEFAULT_SONNET_MODEL
//     or both absent): pass model=undefined so subagent inherits parent session model.
//   • tiered cluster (vars differ): pass the tier NAME ('opus'|'sonnet'|'haiku').
//   • unknown cluster (no ANTHROPIC_DEFAULT_*_MODEL vars set): pass the canonical
//     model ID from ROLE_TIER_DEFAULTS.
//   • per-phase override (phase.model field from resolve): highest precedence.
//   ROLE_TIER still exists for the resolve agent to return dispatchModel per phase,
//   but the JS loop now calls resolveModel(role, phase) instead of tierFor(role).
//   DELIBERATE DEVIATION: Pi workflow scripts do not expose a reliable `env` or
//   `process.env` global for reading ANTHROPIC_DEFAULT_*_MODEL vars at the JS
//   driver level. The three-cluster logic is structurally wired (env-var guards
//   use `typeof env !== 'undefined'` which will be false in the sandbox, causing
//   the function to always take the unknown-cluster path → ROLE_TIER_DEFAULTS[tier]).
//   This is the safe, predictable fallback: explicit canonical IDs per role tier.
//   True single-cluster / tiered-cluster behavior requires the caller (forge-cli
//   TS layer) to inject dispatchModel into the phase via RESOLVE_SCHEMA phase.model,
//   which is the per-phase override path (highest precedence, always respected).
//
// SESSION PREFLIGHT (Gap #6 — FORGE-S28-T05):
//   Instructed in phase-0 subagent prompt only (firstPhase=true). Reads
//   .forge/cache/preflight-status.json; blob.ok===false halts before gate step.
//   Port limitation: subsequent phases skip preflight to avoid redundant re-checks.
//
// FRICTION EMISSION (Gap #5 — FORGE-S28-T05):
//   Orchestrator-experienced friction (spawn failure, FSM rejection) cannot be
//   emitted by the JS driver because it cannot shell out to store-cli. Documented
//   as a port limitation. Per-phase subagents are instructed to drain
//   .forge/cache/FRICTION-*.jsonl and emit type:friction events after failures.
//
// ON_REVISION ROUTING (Gap #13 — FORGE-S28-T05):
//   RESOLVE_SCHEMA phase items gain optional on_revision field. revisionTarget()
//   prefers phase.on_revision (command-name lookup) over nearest-preceding-non-review.
//
// TOKEN SIDECAR MERGE (Gap #14 — FORGE-S28-T05):
//   After each phase subagent returns, an escalate-agent pattern calls
//   store-cli merge-sidecar with the eventId agreed before spawn.
//   The eventId uses the _complete suffix (token usage lands on the COMPLETE event,
//   not the start event). The driver passes eventId into runPhase() so the subagent
//   prompt references the same eventId when writing the sidecar via --sidecar.
//
// PERSONA/SKILL INJECTION (Gap #8 — FORGE-S28-T05):
//   ROLE_TO_NOUN maps each role to its persona noun. Subagent prompt instructs
//   reading persona-pack.json and composing role block (reference mode, inline fallback).
//
// BUILD-OVERLAY CONTEXT (Gap #9 — FORGE-S28-T05):
//   Raw MASTER_INDEX.md read replaced with build-overlay.cjs --task --format md.
//   Stale direct read is a documented degradation fallback.
//
// REVIEW LOOP CONTEXT (Gap #10 — FORGE-S28-T05):
//   REVIEW_ROLES phases receive a "Review Loop Context" block with iteration/maxIter.
//
// GATE EXIT-CODE DISTINCTION (Gap #7 — FORGE-S28-T05):
//   Subagent prompt distinguishes exit_code==1 (gate_failed) vs exit_code==2
//   (gate_misconfigured) in the note field.
//
// SIMPLIFIED RETRY PROMPT (Gap #11 — FORGE-S28-T05):
//   Empty/whitespace/timeout result triggers subagent_retry event then retries
//   with a simplified prompt (no arch block, no summary block, adds YOU MUST produce a result).
//
// Invocation (Workflow tool):  { name: 'wfl:run-task', args: 'FORGE-S27-T01' }
// args may also be an object: { taskId: 'FORGE-S27-T01' }
// ---------------------------------------------------------------------------

// Task statuses that mean "do not run any phase" — orchestrate_task pre-task guard.
const SKIP_STATUS = ['blocked', 'escalated', 'committed', 'abandoned']
// Phase roles whose artifact carries a **Verdict:** that routes the FSM.
// NOTE: `approve` is NOT here — orchestrate_task advances it on completion like a
// non-review phase (the approve workflow self-escalates if it rejects).
const REVIEW_ROLES = ['review-plan', 'review-code', 'validate']
// Per-phase model tier — verbatim port of orchestrate_task.md § Role-to-Tier Mapping.
// The resolve agent uses this as a reference; JS loop calls resolveModel() not tierFor().
const ROLE_TIER = {
  'plan':        'sonnet',
  'implement':   'sonnet',
  'review-plan': 'opus',
  'review-code': 'opus',
  'validate':    'opus',
  'approve':     'opus',
  'commit':      'haiku',
  'writeback':   'haiku',
}
const tierFor = (role) => ROLE_TIER[role] || 'sonnet'   // orchestrate_task's ROLE_TIER.get(role, "sonnet")

// Canonical model IDs for unknown-cluster fallback (Gap #12).
const ROLE_TIER_DEFAULTS = {
  opus:   'claude-opus-4-5',
  sonnet: 'claude-sonnet-4-6',
  haiku:  'claude-haiku-4-5',
}

// Resolve the dispatch model per the three-cluster + per-phase-override logic (Gap #12).
// • phase.model (from resolve) — highest precedence (per-phase override).
// • ANTHROPIC_DEFAULT_OPUS_MODEL === ANTHROPIC_DEFAULT_SONNET_MODEL or both absent → undefined (inherit).
// • vars differ → tier name (tiered cluster).
// • no vars set → canonical ID from ROLE_TIER_DEFAULTS (unknown cluster).
function resolveModel(role, phase) {
  if (phase && phase.model) return phase.model   // per-phase override wins
  const tier = tierFor(role)
  const opusVar   = (typeof env !== 'undefined' && env.ANTHROPIC_DEFAULT_OPUS_MODEL)   || undefined
  const sonnetVar = (typeof env !== 'undefined' && env.ANTHROPIC_DEFAULT_SONNET_MODEL) || undefined
  const haikiVar  = (typeof env !== 'undefined' && env.ANTHROPIC_DEFAULT_HAIKU_MODEL)  || undefined
  const anySet = opusVar || sonnetVar || haikiVar
  if (!anySet) return ROLE_TIER_DEFAULTS[tier]   // unknown cluster: canonical ID
  // If all three are equal (or only one is set and it matches), treat as single cluster.
  const uniqueVals = new Set([opusVar, sonnetVar, haikiVar].filter(Boolean))
  if (uniqueVals.size <= 1) return undefined       // single cluster: inherit parent
  return tier                                       // tiered cluster: pass tier name
}

// Phase banner map — visual phase identity for log lines (LOW #22).
// Parallel to ROLE_TO_NOUN: maps each role to the persona banner label shown at
// phase-announcement time so the transcript log identifies which Forge persona is active.
// The subagent already gets the full persona-block via ROLE_TO_NOUN; this is display-only.
const BANNER_MAP = {
  'plan':        'forge-architect',
  'review-plan': 'forge-architect',
  'implement':   'forge-engineer',
  'review-code': 'forge-engineer',
  'validate':    'forge-validator',
  'approve':     'forge-architect',
  'commit':      'forge-engineer',
  'writeback':   'forge-engineer',
}

// Role → persona noun mapping for role-block injection (Gap #8).
const ROLE_TO_NOUN = {
  'plan':        'architect',
  'review-plan': 'architect',
  'implement':   'engineer',
  'review-code': 'engineer',
  'validate':    'validator',
  'approve':     'architect',
  'commit':      'engineer',
  'writeback':   'engineer',
}

const RESOLVE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['taskId', 'sprintId', 'taskStatus', 'phases'],
  properties: {
    taskId: { type: 'string' },
    sprintId: { type: 'string' },
    taskStatus: { type: 'string' },         // status read from .forge/store/tasks/{id}.json
    phases: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['command', 'role', 'workflow', 'maxIterations'],
        properties: {
          command: { type: 'string' },       // slash-command name, e.g. "review-plan"
          role: { type: 'string' },           // semantic role, e.g. "review-plan"
          workflow: { type: 'string' },       // workflow file under .forge/workflows/, e.g. "review_plan.md"
          maxIterations: { type: 'integer' }, // revision cap for review roles (default 3)
          on_revision: { type: 'string' },    // optional: command name to route to on revision (Gap #13)
          model: { type: 'string' },          // optional: per-phase model override (Gap #12)
        },
      },
    },
  },
}

const PHASE_RESULT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['phase', 'role', 'gatePassed', 'verdict', 'escalated', 'taskStatus'],
  properties: {
    phase: { type: 'string' },                                  // the command name dispatched
    role: { type: 'string' },
    gatePassed: { type: 'boolean' },                            // preflight-gate.cjs exit 0
    verdict: { type: 'string', enum: ['approved', 'revision', 'malformed', 'none'] }, // 'none' for non-review phases
    escalated: { type: 'boolean' },                             // subagent set status=escalated (gate fail / malformed / self-escalation)
    taskStatus: { type: 'string' },                             // status read back after the phase
    note: { type: 'string' },
  },
}

// --- nearest preceding non-review phase (revision target) -------------------
// Port of orchestrate_task.md: a "Revision Required" verdict routes back to the
// nearest earlier phase whose role is NOT a review role (i.e. the producer).
// Gap #13: if the current review phase specifies on_revision (a command name), look
// it up by command name in phases and return that index. Fallback to nearest-preceding.
function revisionTarget(phases, reviewIdx) {
  const reviewPhase = phases[reviewIdx]
  if (reviewPhase && reviewPhase.on_revision) {
    const targetIdx = phases.findIndex((p) => p.command === reviewPhase.on_revision)
    if (targetIdx !== -1) return targetIdx
  }
  for (let j = reviewIdx - 1; j >= 0; j--) {
    if (!REVIEW_ROLES.includes(phases[j].role)) return j
  }
  return 0   // degenerate pipeline with no producer before the review — loop to start
}

// --- dispatch one phase as a subagent ---------------------------------------
// The subagent owns ALL shell-dependent side-effects for this phase (see header).
// Gap #6: firstPhase=true triggers session preflight check (phase-index-0 only).
// Gap #11: simplified=true uses a shorter prompt (retry path, strips arch+summary block).
// Gap #14: eventId is the COMPLETE-event id pre-computed by the JS loop; the subagent
// must use this exact id when writing its token sidecar (--sidecar form) so mergeSidecar()
// can find the file. Use the _complete suffix because token usage lands on the COMPLETE event.
function runPhase(taskId, sprintId, phase, iteration, { firstPhase = false, simplified = false, eventId = null } = {}) {
  const personaNoun = ROLE_TO_NOUN[phase.role] || 'engineer'
  const reviewLoopCtx = REVIEW_ROLES.includes(phase.role)
    ? [
        '',
        '### Review Loop Context',
        `Iteration: ${iteration} of ${phase.maxIterations}`,
        `Is final iteration: ${iteration >= phase.maxIterations}`,
      ].join('\n')
    : ''

  // Build the prompt lines list.
  const lines = [
    `You are running a SINGLE pipeline phase for Forge task ${taskId} (sprint ${sprintId}).`,
    `Phase: role="${phase.role}", command="${phase.command}", workflow="${phase.workflow}", iteration=${iteration}.`,
  ]

  // Gap #6: Session Preflight — first phase only.
  if (firstPhase) {
    lines.push(
      '',
      '0. SESSION PREFLIGHT (first phase only). Read `.forge/cache/preflight-status.json`.',
      '   If the file is absent, run `node .forge/tools/forge-preflight.cjs` and read the JSON it writes.',
      '   If blob.ok === false in the result, HALT immediately — do NOT proceed to the gate or phase.',
      '   Set status escalated, and return gatePassed=false, escalated=true, verdict="none",',
      '   with the preflight warnings in note.',
    )
  }

  // Gap #7: Gate exit-code distinction.
  lines.push(
    '',
    '1. PRE-FLIGHT GATE. Run `node .forge/tools/preflight-gate.cjs --phase ' + phase.role + ' --task ' + taskId + '`.',
    '   Capture the exit code:',
    '   • exit_code == 0 → gate passed, continue.',
    '   • exit_code == 1 → gate failed (prerequisite missing). Set status escalated.',
    '     Return gatePassed=false, escalated=true, verdict="none", note: "gate_failed: <stderr>".',
    '   • exit_code == 2 → gate misconfigured (unknown phase or malformed block). Set status escalated.',
    '     Return gatePassed=false, escalated=true, verdict="none", note: "gate_misconfigured: <stderr>".',
  )

  // Gap #8: Persona/skill role-block injection.
  lines.push(
    '',
    '1b. ROLE BLOCK INJECTION. Read `.forge/cache/persona-pack.json` and look up the entry for',
    `    noun="${personaNoun}" (role="${phase.role}" maps to this noun via ROLE_TO_NOUN).`,
    '    Prepend the compact persona+skill summary to your working context (reference mode).',
    '    If persona-pack.json is unavailable, read `.forge/personas/' + personaNoun + '.md` and',
    '    `.forge/skills/' + personaNoun + '-skills.md` directly (inline fallback).',
  )

  // Gap #9: build-overlay replaces raw MASTER_INDEX read.
  lines.push(
    '',
    '2. PROJECT CONTEXT + RUN THE PHASE.',
    '   Run `node .forge/tools/build-overlay.cjs --task ' + taskId + ' --format md`',
    '   and inject its stdout as the Project Context block for this phase.',
    '   If build-overlay.cjs exits non-zero, fall back to reading `engineering/MASTER_INDEX.md`',
    '   (documented degradation path — not silent swallow).',
    '   Then read `.forge/workflows/' + phase.workflow + '` and follow it for task ' + taskId + '.',
    '   The workflow writes its own artifacts, {PHASE}-SUMMARY.json, and any task-status changes.',
  )

  // Gap #10: Review Loop Context — injected for review phases.
  if (reviewLoopCtx) lines.push(reviewLoopCtx)

  // Gap #3/emit: PHASE EVENTS.
  // Gap #14: if an eventId was threaded in from the JS loop, instruct the subagent to use it
  // for the COMPLETE event's eventId and for the --sidecar token file so mergeSidecar() matches.
  const eventIdLine = eventId
    ? '   Use eventId="' + eventId + '" for the COMPLETE event (the driver will call merge-sidecar with this id).'
    : '   Use a fresh crypto.randomUUID() for both start and complete event ids.'
  lines.push(
    '',
    '3. EMIT YOUR PHASE EVENTS. You are the only actor that knows your runtime attribution.',
    '   3a. BEFORE running the phase workflow: note the start timestamp (startTimestamp = new Date().toISOString()).',
    '   Emit a start event via `node .forge/tools/store-cli.cjs emit ' + sprintId + " '{event-json}'\`",
    '   with action="start", role="' + phase.role + '", iteration=' + iteration + ', startTimestamp and endTimestamp both equal to startTimestamp (0-duration placeholder).',
    '   3b. AFTER the phase workflow completes: note the end timestamp (endTimestamp = new Date().toISOString()).',
    '   Compute durationMinutes = (new Date(endTimestamp) - new Date(startTimestamp)) / 60000.',
    '   Emit a complete event via `node .forge/tools/store-cli.cjs emit ' + sprintId + " '{event-json}'\`",
    '   conforming to `.forge/schemas/event.schema.json` (role, action="complete", phase, iteration=' + iteration + ',',
    '   startTimestamp, endTimestamp, durationMinutes, plus your own model/provider/token usage — do NOT invent placeholder model strings).',
    '   ' + eventIdLine,
    '   If `/cost` data is available, also write the token sidecar via the `--sidecar` form with the COMPLETE eventId. Best-effort; skip silently if unavailable.',
    '',
    '   Gap #5 FRICTION DRAIN: After any failure event (malformed verdict, null dispatch, max-iter exhaustion),',
    '   drain any `.forge/cache/FRICTION-*.jsonl` files and emit each record as type "friction" with',
    '   `persona:"orchestrator"` and the appropriate issue token.',
    '   Also emit a type:friction event with persona="orchestrator" for any orchestrator-experienced failures.',
    '   Then drain any FRICTION-*.jsonl records you produced as phase subagent and emit them as type "friction".',
  )

  // Gap #4: Verdict or non-review.
  lines.push(
    '',
    REVIEW_ROLES.includes(phase.role)
      ? '4. READ VERDICT. This is a REVIEW phase. The phase workflow records its verdict into the store '
        + 'summary (`summaries.' + phase.role + '.verdict`) via set-summary — make sure that write happened. '
        + 'Then resolve it with the canonical tool `node .forge/tools/read-verdict.cjs --phase ' + phase.role + ' --task ' + taskId + '` '
        + '(reads the structured summary, NOT a markdown artifact path). '
        + 'Route on the STDOUT token the tool prints (approved | revision | n/a | unknown), NOT on the exit code. '
        + 'Map STDOUT token → verdict: "approved"→"approved", "revision"→"revision", "n/a"→"malformed", "unknown"→"malformed". '
        + 'The exit code is unreliable (exits 1 for both revision AND missing/n/a). NEVER guess.'
      : '4. NON-REVIEW phase: return verdict="none".',
  )

  lines.push(
    '',
    '5. Read `.forge/store/tasks/' + taskId + '.json` and return its final status as taskStatus, plus a one-line note.',
  )

  // Gap #11: simplified retry strips arch+summary block and adds strong directive.
  if (simplified) {
    lines.push(
      '',
      'IMPORTANT: You MUST produce a result. This is a retry after a failed dispatch.',
      'Skip the architecture context block and the summary block. Proceed directly to the phase workflow.',
    )
  }

  return agent(
    lines.join('\n'),
    { label: `${taskId}:${phase.role}:${iteration}`, phase: 'Pipeline', schema: PHASE_RESULT_SCHEMA, model: resolveModel(phase.role, phase) }
  )
}

// --- emit task_skipped event (LOW #19) --------------------------------------
// When the pre-task status guard finds a SKIP_STATUS, the task is silently
// skipped. To give the event log a complete picture, emit a task-dispatch event
// with action:"skip" so downstream collators can account for every task.
// Pattern: mirrors escalateTask / mergeSidecar agent delegation (JS cannot shell out).
function emitSkip(taskId, sprintId, taskStatus) {
  return agent(
    [
      `Emit a task_skipped event for Forge task ${taskId} (sprint ${sprintId}).`,
      `node .forge/tools/store-cli.cjs emit ${sprintId}`,
      `'{"type":"task-dispatch","action":"skip","taskId":"${taskId}","sprintId":"${sprintId}",`,
      `"role":"orchestrator","phase":"pre-task","iteration":0,`,
      `"notes":"pre-task SKIP_STATUS guard: task status is ${taskStatus}",`,
      `"startTimestamp":"<ISO-now>","endTimestamp":"<ISO-now>","durationMinutes":0,`,
      `"model":"<your-model-id>","provider":"anthropic"}'`,
      'Replace <ISO-now> with the current UTC ISO 8601 timestamp and <your-model-id> with your actual model id.',
      'Best-effort — if the emit fails, log and continue. Return "ok".',
    ].join(' '),
    { label: `skip-event:${taskId}`, phase: 'Resolve', model: resolveModel('commit', {}) }
  )
}

// --- escalate from the JS driver (maxIterations exhaustion / null dispatch) --
// The script can't write the store, so a tiny agent performs the status write + event.
function escalateTask(taskId, sprintId, reason) {
  return agent(
    [
      `Escalate Forge task ${taskId} to a human.`,
      `run \`node .forge/tools/store-cli.cjs update-status task ${taskId} status escalated\``,
      `and emit one event (sprint ${sprintId}) with verdict="escalated" and notes="${reason}".`,
      `Return the task's final status as taskStatus, gatePassed=true, verdict="none", escalated=true, phase="escalate", role="escalate".`,
    ].join(' '),
    { label: `${taskId}:escalate`, phase: 'Pipeline', schema: PHASE_RESULT_SCHEMA, model: resolveModel('commit', {}) }
  )
}

// --- emit subagent_retry event (Gap #11) ------------------------------------
// The JS driver cannot shell out; a tiny agent writes the event.
function emitRetryEvent(taskId, sprintId, role, iteration, reason) {
  return agent(
    [
      `Emit a subagent_retry event for Forge task ${taskId} (sprint ${sprintId}).`,
      `node .forge/tools/store-cli.cjs emit ${sprintId} '{"type":"task-implemented","action":"subagent_retry","role":"${role}","taskId":"${taskId}","phase":"${role}","iteration":${iteration},"notes":"${reason}"}'`,
      `(fill in eventId, sprintId, startTimestamp, endTimestamp, durationMinutes=0, model, provider from runtime.)`,
      `Return "ok".`,
    ].join(' '),
    { label: `${taskId}:retry-event:${iteration}`, phase: 'Pipeline', model: resolveModel('commit', {}) }
  )
}

// --- merge token sidecar (Gap #14) ------------------------------------------
// After each phase, call merge-sidecar to merge the phase subagent's token sidecar.
function mergeSidecar(sprintId, eventId) {
  return agent(
    [
      `Merge the token sidecar for sprint ${sprintId}, eventId ${eventId}.`,
      `node .forge/tools/store-cli.cjs merge-sidecar ${sprintId} ${eventId}`,
      `Best-effort — if the sidecar file does not exist, skip silently. Return "ok".`,
    ].join(' '),
    { label: `merge-sidecar:${eventId}`, phase: 'Pipeline', model: resolveModel('commit', {}) }
  )
}

// --- Main -------------------------------------------------------------------
const taskId = (typeof args === 'string' ? args : args?.taskId)
if (!taskId) throw new Error('wfl:run-task requires a task id — pass args: "FORGE-S27-T01"')

// Phase 1 — Resolve the pipeline + pre-task status (agent does the store/config I/O).
phase('Resolve')
const resolved = await agent(
  [
    `Resolve the run-task pipeline for Forge task ${taskId}..`,
    `Read \`node .forge/tools/store-cli.cjs read task ${taskId} --json\` for its current status and sprintId.`,
    'Then resolve the phase pipeline EXACTLY as `.forge/workflows/orchestrate_task.md` § Pipeline Resolution prescribes:',
    'if task.pipeline names a key in `.forge/config.json` pipelines, use those phases; otherwise use the default pipeline.',
    // LOW #20: writeback added to hardcoded default pipeline (orchestrate_task.md §3 full default).
    'The hardcoded default is: plan → review-plan → implement → review-code → validate → approve → writeback → commit,',
    'mapping roles to workflow files: plan→plan_task.md, review-plan→review_plan.md, implement→implement_plan.md,',
    'review-code→review_code.md, validate→validate_task.md, approve→architect_approve.md,',
    'writeback→update_implementation.md, commit→commit_task.md.',
    'maxIterations defaults to 3 for review roles (review-plan, review-code, validate) and 1 otherwise.',
    'Return taskId, sprintId, taskStatus, and the ordered phases[]. Read-only — do NOT modify anything.',
  ].join(' '),
  { label: `resolve:${taskId}`, phase: 'Resolve', schema: RESOLVE_SCHEMA }
)
if (!resolved) throw new Error(`Could not resolve pipeline for task ${taskId}`)

const { sprintId, phases } = resolved
// Pre-task status guard — orchestrate_task skips already-terminal/blocked tasks.
// LOW #19: emit task_skipped event so the event log accounts for every task.
if (SKIP_STATUS.includes(resolved.taskStatus)) {
  log(`⚠ ${taskId} — status is ${resolved.taskStatus}, nothing to run.`)
  await emitSkip(taskId, sprintId, resolved.taskStatus)
  return { taskId, sprintId, skipped: true, taskStatus: resolved.taskStatus, results: [] }
}
log(`Task ${taskId} (sprint ${sprintId}) — ${phases.length} phases: ${phases.map(p => p.role).join(' → ')}`)

// Phase 2 — drive the phase FSM. JS owns sequencing, counters, routing, escalation.
phase('Pipeline')
const iterationCounts = {}    // keyed by phase command
const results = []
let i = 0
let escalated = false
let escalationReason = null

while (i < phases.length) {
  const p = phases[i]
  const iteration = (iterationCounts[p.command] || 0) + 1
  const isFirstPhase = i === 0 && iteration === 1
  // LOW #22: use BANNER_MAP for phase-announcement log identity.
  const banner = BANNER_MAP[p.role] || p.role
  log(`→ ${taskId}  [${banner}]  ${p.role} [${resolveModel(p.role, p) || 'inherit'}]  (iteration ${iteration})`)

  // Gap #11: Simplified-retry-prompt — detect empty/whitespace/timeout result.
  // Emit subagent_retry event, then retry with simplified prompt.
  // Gap #14: Compute eventId using _complete suffix (token usage lands on COMPLETE event,
  // not start). Pass eventId into runPhase so subagent uses it for sidecar agreement.
  // Determinism: eventId must NOT read the wall clock — new Date()/Date.now() throw in the
  // workflow sandbox (breaks resume) and surface as a runtime throw because nested-by-name
  // workflows aren't statically pre-scanned. A deterministic key unique per
  // (sprint, task, role, iteration) is sufficient: controller and subagent only need to AGREE
  // on the same string; event time-ordering comes from payload timestamps the subagent emits.
  const eventId = `${sprintId}_${taskId}_${p.role}_iter${iteration}_complete`
  let r = await runPhase(taskId, sprintId, p, iteration, { firstPhase: isFirstPhase, eventId })
  const isEmpty = !r || (typeof r === 'string' && !r.trim())
  if (isEmpty) {
    // Emit subagent_retry event (best-effort, non-blocking).
    await emitRetryEvent(taskId, sprintId, p.role, iteration, 'empty_or_null_dispatch')
    log(`↺ ${taskId}  ${p.role}  — empty/null dispatch, retrying with simplified prompt`)
    r = await runPhase(taskId, sprintId, p, iteration, { firstPhase: false, simplified: true, eventId })
  }
  if (!r) {
    escalated = true
    escalationReason = `phase ${p.role} dispatch returned null after retry`
    log(`✗ ${taskId}  ${p.role}  — dispatch failed twice, escalating`)
    break
  }
  // Gap #14: merge token sidecar after each phase.
  await mergeSidecar(sprintId, eventId)
  results.push(r)

  // Gate failure or subagent self-escalation (already wrote status=escalated).
  if (!r.gatePassed || r.escalated) {
    escalated = true
    escalationReason = r.note || `${p.role} gate failed / self-escalated`
    log(`⚠ ${taskId}  ${p.role}  — escalated (${escalationReason})`)
    break
  }

  // Review phases route on verdict; non-review phases advance on completion.
  if (REVIEW_ROLES.includes(p.role)) {
    if (r.verdict === 'approved') {
      log(`✓ ${taskId}  ${p.role}  — Approved`)
      i += 1
    } else if (r.verdict === 'revision') {
      iterationCounts[p.command] = (iterationCounts[p.command] || 0) + 1
      log(`↻ ${taskId}  ${p.role}  — Revision Required (iteration ${iterationCounts[p.command]})`)
      if (iterationCounts[p.command] >= p.maxIterations) {
        escalated = true
        escalationReason = `max iterations (${p.maxIterations}) reached at ${p.role}`
        break
      }
      i = revisionTarget(phases, i)   // loop back to the producing phase
    } else {
      // 'malformed' (or unexpected 'none' from a review phase) — never guess.
      escalated = true
      escalationReason = `verdict malformed at ${p.role}`
      break
    }
  } else {
    log(`✓ ${taskId}  ${p.role}  — completed`)
    i += 1
  }
  // #22 PARITY SEAM — Post-phase exit guard (FORGE-S26-T19):
  //   forge-cli/run-task.ts owns hard enforcement: runPostflightGate() is called
  //   after runForgeSubagent returns and before currentPhaseIndex++ — if the
  //   outputs block is unsatisfied the FSM does not advance and runHaltAdvisor
  //   is invoked. This JS driver delegates post-phase output verification to
  //   each per-phase subagent (which receives postflight-gate.cjs via its phase
  //   prompt and is instructed to satisfy the outputs block before returning
  //   gatePassed=true in its StructuredOutput). The JS driver owns advance/halt
  //   on the returned `gatePassed` field already present in the StructuredOutput
  //   schema (see wfl-run-task.js lines above). No shell execution of
  //   postflight-gate.cjs in this JS driver (matches no-shell constraint, #21).
}

// If the JS driver decided to escalate (not the subagent), perform the status write.
const lastWroteEscalation = results.length && results[results.length - 1].escalated
if (escalated && !lastWroteEscalation) {
  await escalateTask(taskId, sprintId, escalationReason)
}

// Phase 3 — Report terminal outcome.
phase('Report')
const reachedEnd = !escalated && i >= phases.length
const finalStatus = reachedEnd ? 'committed' : 'escalated'
if (reachedEnd) {
  log(`🌱 Task ${taskId} complete — pipeline reached terminal (committed).`)
} else {
  log(`⚠ Task ${taskId} escalated: ${escalationReason}`)
  log(`   Resume with the failing phase command after addressing the issue, or re-run wfl:run-task.`)
}

return {
  taskId,
  sprintId,
  finalStatus,
  escalated,
  escalationReason,
  phasesRun: results.length,
  iterationCounts,
  results,
}
