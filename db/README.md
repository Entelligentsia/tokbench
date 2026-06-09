# tokbench analytics database

`tokbench.db` — a single-file SQLite store of **every run / phase / message / tool-call / tool-result / meter** in `results/`. Built to replace one-off scripts against transcript JSON with plain SQL.

- **`build_db.py`** — idempotent builder. `python3 db/build_db.py` drops and rebuilds `tokbench.db` from `results/`. The DB is a *derived* artifact; transcripts remain source of truth.
- **`QUERIES.md`** — 20 worked queries (arm comparison, variance, per-turn series, tool composition, **forge_compress per call**, cache-by-rail, meter reconciliation, void anatomy).
- **`tokbench.db`** — the database. Open with `sqlite3 db/tokbench.db` or attach from DuckDB for fast median/PIVOT analytics.

## Grains (one table per grain, FK-linked, raw JSON preserved on each)

```
runs ─┬─ phases ─┬─ messages          (per-turn usage: input/output/cacheRead/cacheWrite/cost)
      │          ├─ tool_calls         (native / ctx_* / forge_* classification)
      │          └─ tool_results       (forge_compress AND lean-ctx compression, normalized)
      ├─ meter_metrics / meters_raw    (lean-ctx / rtk / headroom meters)
      └─ artifacts                     (*-SUMMARY.json, COST_REPORT.md)
```

Filter the 14-run comparison set with `class='matrix'` (other classes: void, pilot, exploratory, cross).

## DuckDB lens (optional, for medians / pivots)

```sh
duckdb -c "INSTALL sqlite; LOAD sqlite; ATTACH 'db/tokbench.db' AS t (TYPE sqlite);
           SELECT arm, median(total_input) FROM t.runs WHERE class='matrix' GROUP BY arm;"
```
