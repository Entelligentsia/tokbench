#!/usr/bin/env bash
# tokbench harvest.sh — copy run evidence to the mounted results volume
# PRIMARY DATA: .forge/transcripts/ per-phase JSON (usage, model, timings, full
# message log). COST_REPORT is a collate-time summary — not relied upon here.
set -uo pipefail

DEST="${1:-/results}"
[ -d "$DEST" ] || { echo "harvest: no results volume mounted at $DEST — skipping" >&2; exit 0; }

PROJ=/home/bench/forge-testbench/cartographer

# 1. PRIMARY: raw transcripts — every data file, verbatim
mkdir -p "$DEST/transcripts"
cp -r "$PROJ/.forge/transcripts/." "$DEST/transcripts/" 2>/dev/null

# 2. per-run summary table from transcript usage blocks (TSV: phase, provider,
#    model, input, output, contextTokens, turns, messages, seconds, stopReason, error)
SUMMARY="$DEST/run-summary.tsv"
printf 'phase\tprovider\tmodel\tinput\toutput\tcontextTokens\tturns\tmessages\tseconds\tstopReason\terror\n' > "$SUMMARY"
find "$PROJ/.forge/transcripts" -name '*__*.json' ! -name '*writeback*SUMMARY*' 2>/dev/null | sort | while read -r f; do
  jq -r '[(.tag // "?"), .provider, .model, .usage.input, .usage.output,
          .usage.contextTokens, .usage.turns, .messageCount,
          (((.finishedAt | sub("\\.[0-9]+Z$";"Z") | fromdateiso8601)
          - (.startedAt  | sub("\\.[0-9]+Z$";"Z") | fromdateiso8601))),
          .stopReason, (.errorMessage // "-")] | @tsv' "$f" 2>/dev/null
done >> "$SUMMARY"

# 3. supporting state: store + THIS TASK's sprint artifacts only (other sprints are
#    untouched golden fixtures — copying them just duplicates identical noise per run)
cp -r "$PROJ/.forge/store"  "$DEST/forge-store"  2>/dev/null
TASK_SPRINT="${TASK%-T*}"
[ -n "$TASK_SPRINT" ] && cp -r "$PROJ/engineering/sprints/$TASK_SPRINT" "$DEST/sprint-$TASK_SPRINT" 2>/dev/null
[ -d "$HOME/.pi/agent/sessions" ] && cp -r "$HOME/.pi/agent/sessions" "$DEST/pi-sessions" 2>/dev/null

# 4. product self-metrics + engage-checks (per-arm; absent files are fine)
ENGAGE="unknown"
# count ctx_* tool calls across this run's transcripts (transcript = ground truth)
CTX_CALLS=$(find "$PROJ/.forge/transcripts" -name '*__*.json' -exec jq -r '.messages[]? | select(.role=="assistant") | .content[]? | select(.type=="toolCall") | .name' {} + 2>/dev/null | grep -c '^ctx_' || true)
case "${ARM:-a0}" in
  a0)
    if [ ! -d "$HOME/.config/lean-ctx" ] && [ ! -d "$HOME/.local/share/rtk" ] && [ ! -d "$HOME/.headroom" ] && [ "${CTX_CALLS:-0}" -eq 0 ]; then
      ENGAGE="pass"; else ENGAGE="FAIL: product state/calls present in control arm"; fi ;;
  a1)
    # vendor self-metrics (v3.7.3 XDG paths) + gain snapshot — capture-all, judge from transcripts
    cp -r "$HOME/.config/lean-ctx"      "$DEST/leanctx-config" 2>/dev/null
    cp -r "$HOME/.local/share/lean-ctx" "$DEST/leanctx-share"  2>/dev/null
    lean-ctx gain --deep > "$DEST/leanctx-gain.txt" 2>&1
    [ "${CTX_CALLS:-0}" -gt 0 ] && ENGAGE="pass (${CTX_CALLS} ctx_* calls)" || ENGAGE="FAIL: no ctx_* tool calls in transcripts" ;;
  a2)
    curl -fsS "${HEADROOM_URL:-http://headroom:8787}/stats" -o "$DEST/headroom-stats.json" 2>/dev/null \
      && ENGAGE="pass" || ENGAGE="FAIL: headroom /stats unreachable or empty" ;;
  a3)
    rtk gain --json > "$DEST/rtk-gain.json" 2>/dev/null
    rtk gain --history > "$DEST/rtk-history.txt" 2>/dev/null
    grep -q 'rtk' "$DEST/rtk-history.txt" 2>/dev/null && ENGAGE="pass" || ENGAGE="FAIL: no rtk-prefixed commands"
    ;;
esac

# 5. gate results: run the suite once more, record exit codes
( cd "$PROJ" \
  && { npm run build >/dev/null 2>&1; echo "build=$?"; } \
  && { npm test      >/dev/null 2>&1; echo "test=$?";  } \
  && { npm run lint  >/dev/null 2>&1; echo "lint=$?";  } ) > "$DEST/gates.txt" 2>&1

# 6. self-describing manifest
cat > "$DEST/run-manifest.json" <<EOF
{
  "arm": "${ARM:-a0}",
  "task": "${TASK:-}",
  "rep": "${REP:-1}",
  "engage_check": "$ENGAGE",
  "start": "${START_TS:-}",
  "end": "${END_TS:-}",
  "image": "${TOKBENCH_IMAGE:-unknown}",
  "model": "${TOKBENCH_MODEL:-unset}",
  "operator_notes": ""
}
EOF

echo
echo "harvest → $DEST  (engage-check: $ENGAGE)"
column -t "$SUMMARY" 2>/dev/null | head -15
[ "${ENGAGE#FAIL}" = "$ENGAGE" ] || echo "⚠ ENGAGE-CHECK FAILED — this run must be voided and re-run" >&2
