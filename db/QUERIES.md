# tokbench.db — 20 worked queries

Run any of these with `sqlite3 db/tokbench.db < query` or paste into `sqlite3 db/tokbench.db`.
For **median** cross-tabs, DuckDB is cleaner — `duckdb -c "INSTALL sqlite; LOAD sqlite; ATTACH 'db/tokbench.db' AS t (TYPE sqlite); SELECT median(total_input) ..."` — but every query below runs in plain `sqlite3` (medians use a window idiom).

Grains: `runs → phases → messages`, `tool_calls → tool_results` (forge_compress + lean-ctx compression), `meter_metrics`/`meters_raw`, `artifacts`. Filter the comparison set with `class='matrix'`.

---

### 1. Median & mean billed input per arm vs native, with band
```sql
WITH t AS (SELECT arm, total_input,
  ROW_NUMBER() OVER (PARTITION BY arm ORDER BY total_input) rn,
  COUNT(*) OVER (PARTITION BY arm) c FROM runs WHERE class='matrix')
SELECT arm, COUNT(*) n, ROUND(AVG(total_input)) mean,
  (SELECT AVG(total_input) FROM t t2 WHERE t2.arm=t.arm AND rn IN ((c+1)/2,(c+2)/2)) AS median
FROM t GROUP BY arm;
```

### 2. Phase × arm average input (the cross-tab)
```sql
SELECT phase, ordinal,
  ROUND(AVG(CASE WHEN arm='a0'  THEN input END)) native,
  ROUND(AVG(CASE WHEN arm='a1m' THEN input END)) leanctx,
  ROUND(AVG(CASE WHEN arm='a2'  THEN input END)) headroom,
  ROUND(AVG(CASE WHEN arm='a3'  THEN input END)) rtk
FROM phases p JOIN runs r USING(run_id) WHERE r.class='matrix'
GROUP BY phase, ordinal ORDER BY ordinal;
```

### 3. Is the work the same size? Output tokens per arm (≈constant ⇒ deltas are carriage)
```sql
SELECT arm, ROUND(AVG(total_output)) avg_output, MIN(total_output) lo, MAX(total_output) hi
FROM runs WHERE class='matrix' GROUP BY arm;
```

### 4. Which phase drives run-to-run variance (CoV) per arm
```sql
SELECT arm, phase,
  ROUND(AVG(input)) avg, ROUND(100.0*(MAX(input)-MIN(input))/AVG(input)) spread_pct
FROM phases p JOIN runs r USING(run_id) WHERE r.class='matrix'
GROUP BY arm, phase ORDER BY arm, spread_pct DESC;
```

### 5. Tokens-per-turn per arm (heavier turns vs more turns)
```sql
SELECT arm, COUNT(*) runs, ROUND(AVG(total_turns)) avg_turns,
  ROUND(AVG(1.0*total_input/total_turns)) avg_input_per_turn
FROM runs WHERE class='matrix' GROUP BY arm;
```

### 6. Per-turn input series within a phase (fixed-preamble re-carriage shape)
```sql
SELECT run_id, phase, idx, input, output, cache_read
FROM messages WHERE run_id='R12' AND phase='plan' AND input IS NOT NULL ORDER BY idx;
```

### 7. lean-ctx per-turn baseline injection vs native (per phase)
```sql
SELECT p.phase,
  ROUND(AVG(CASE WHEN r.arm='a0'  THEN 2.0*p.input/p.turns - p.context_tokens END)) native_baseline,
  ROUND(AVG(CASE WHEN r.arm='a1m' THEN 2.0*p.input/p.turns - p.context_tokens END)) leanctx_baseline
FROM phases p JOIN runs r USING(run_id) WHERE r.class='matrix' GROUP BY p.phase ORDER BY p.ordinal;
```

### 8. lean-ctx adoption vs outcome (does more ctx_* mean a higher bill?)
```sql
SELECT tc.run_id, r.total_input,
  SUM(CASE WHEN tc.tool_class='ctx' THEN 1 ELSE 0 END) ctx_calls, COUNT(*) total_calls
FROM tool_calls tc JOIN runs r USING(run_id) WHERE r.arm='a1m'
GROUP BY tc.run_id ORDER BY r.total_input;
```

### 9. Tool-call composition per arm (native / ctx / forge)
```sql
SELECT r.arm, tc.tool_class, COUNT(*) calls,
  ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (PARTITION BY r.arm)) pct
FROM tool_calls tc JOIN runs r USING(run_id) WHERE r.class='matrix'
GROUP BY r.arm, tc.tool_class ORDER BY r.arm, calls DESC;
```

### 10. Store access routing: forge_* MCP vs ctx_* (per run)
```sql
SELECT run_id,
  SUM(CASE WHEN tool_name LIKE 'forge_%' THEN 1 ELSE 0 END) via_forge_mcp,
  SUM(CASE WHEN tool_name LIKE 'ctx_%'   THEN 1 ELSE 0 END) via_ctx
FROM tool_calls WHERE run_id IN ('a1f.r1','R12') GROUP BY run_id;
```

### 11. Unique tool-result content vs forge-compressed (addressable decomposition)
```sql
SELECT run_id,
  SUM(content_tokens_est) unique_result_tokens,
  SUM(CASE WHEN tool_class='ctx'   THEN content_tokens_est ELSE 0 END) ctx_addressable,
  SUM(CASE WHEN tool_class='forge' THEN content_tokens_est ELSE 0 END) forge_store
FROM tool_results WHERE run_id='R12' GROUP BY run_id;
```

### 12. forge_compress total savings per run
```sql
SELECT run_id, COUNT(*) calls, SUM(comp_before) before_tok, SUM(comp_after) after_tok,
  ROUND(100.0*SUM(comp_before-comp_after)/SUM(comp_before),1) saved_pct
FROM tool_results WHERE comp_source='forge' GROUP BY run_id ORDER BY run_id;
```

### 13. Which forge tool compresses best/worst (matrix)
```sql
SELECT comp_subtool tool, COUNT(*) calls, SUM(comp_before) before_tok, SUM(comp_after) after_tok,
  ROUND(100.0*SUM(comp_before-comp_after)/SUM(comp_before),1) saved_pct
FROM tool_results tr JOIN runs r USING(run_id)
WHERE comp_source='forge' AND r.class='matrix' GROUP BY comp_subtool ORDER BY before_tok DESC;
```

### 14. forge_compress as a share of the bill (per arm)
```sql
SELECT r.arm, SUM(tr.comp_before-tr.comp_after) forge_saved_tok,
  ROUND(AVG(rr.total_input)) avg_bill,
  ROUND(100.0*SUM(tr.comp_before-tr.comp_after)/COUNT(DISTINCT tr.run_id)/AVG(rr.total_input),2) saved_pct_of_bill
FROM tool_results tr JOIN runs r USING(run_id) JOIN runs rr ON rr.run_id=tr.run_id
WHERE tr.comp_source='forge' AND r.class='matrix' GROUP BY r.arm;
```

### 15. forge_compress percentSaved by phase
```sql
SELECT phase, COUNT(*) calls, ROUND(AVG(comp_saved_pct),1) avg_saved_pct
FROM tool_results tr JOIN runs r USING(run_id)
WHERE comp_source='forge' AND r.class='matrix' GROUP BY phase ORDER BY avg_saved_pct DESC;
```

### 16. Cache usage by rail (ollama=0, Anthropic large)
```sql
SELECT r.run_id, r.class, r.arm,
  SUM(m.cache_read) cacheRead, SUM(m.cache_write) cacheWrite, SUM(m.input) fresh_input
FROM messages m JOIN runs r USING(run_id) WHERE r.run_id IN ('R01','a0c')
GROUP BY r.run_id;
```

### 17. Dollar cost per phase/run (where cost exists)
```sql
SELECT run_id, phase, ROUND(SUM(cost_total),4) phase_cost
FROM messages WHERE cost_total IS NOT NULL AND cost_total>0 AND run_id='a0c'
GROUP BY run_id, phase ORDER BY phase_cost DESC;
```

### 18. Headroom counterfactual reconciliation (flag non-reconciling runs)
```sql
SELECT r.run_id, r.total_input billed,
  mm1.num_value removed, mm2.num_value meter_before,
  r.total_input + mm1.num_value AS bill_plus_removed
FROM runs r
LEFT JOIN meter_metrics mm1 ON mm1.run_id=r.run_id AND mm1.source='headroom' AND mm1.metric='total_tokens_removed'
LEFT JOIN meter_metrics mm2 ON mm2.run_id=r.run_id AND mm2.source='headroom' AND mm2.metric='total_tokens_before_with_cli_filtering'
WHERE r.arm='a2' AND r.class='matrix';
```

### 19. Does lean-ctx's meter match measured ctx_* compression?
```sql
SELECT r.run_id,
  (SELECT num_value FROM meter_metrics WHERE run_id=r.run_id AND source='lean-ctx' AND metric LIKE '%tokens_saved%' LIMIT 1) meter_saved,
  SUM(CASE WHEN tr.comp_source='lean-ctx' THEN tr.comp_before-tr.comp_after ELSE 0 END) measured_ctx_saved
FROM runs r LEFT JOIN tool_results tr USING(run_id)
WHERE r.arm='a1m' AND r.class='matrix' GROUP BY r.run_id;
```

### 20. Void anatomy + completion-failure rate
```sql
SELECT r.run_id, r.arm, r.void_reason,
  (SELECT phase FROM phases WHERE run_id=r.run_id AND stop_reason!='stop' LIMIT 1) halt_phase,
  (SELECT error FROM phases WHERE run_id=r.run_id AND error IS NOT NULL LIMIT 1) err,
  r.total_input partial_billed
FROM runs r WHERE r.class='void' ORDER BY r.run_id;
```

---

## Rebuild

```sh
python3 db/build_db.py    # drops + rebuilds tokbench.db from results/
```

The DB is a derived artifact (regenerable from transcripts). Run registry (dir → run/arm/class) is at the top of `build_db.py`; add new runs there.
