# tokbench analytics

Self-contained dashboard over the full run collection.

- **`dashboard.html`** — open in any browser (`file://`, no server, no network). Every comparable datum across the 14 confirmatory runs: arm comparison vs the A0×5 band, full per-run record, per-phase token heatmap, the three-meter disagreement, variance/noise-floor, voids, and pilot/cross-rail context runs.
- **`extract.py`** — parses every `results/*/run-summary.tsv` (+ gates, manifest, middleware meters) into `data.json`. No numbers are hand-entered.
- **`build_dashboard.py`** — renders `data.json` into `dashboard.html` (data inlined, charts are CSS, tables sort in vanilla JS).

## Regenerate after new runs

```sh
python3 analysis/extract.py        # re-parse results/ -> data.json
python3 analysis/build_dashboard.py # data.json -> dashboard.html
```

The run registry (dir → run-id / arm / class) lives at the top of `extract.py`; add new rows there.
