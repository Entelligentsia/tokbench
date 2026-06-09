#!/usr/bin/env python3
"""Extract every comparable datum from the tokbench run collection into one JSON.
Source of truth = each run's run-summary.tsv / gates.txt / run-manifest.json / middleware meters.
No numbers are hand-entered; everything is parsed from disk."""
import csv, json, os, re, sys
from statistics import median, mean, pstdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

# --- run registry: dir -> metadata. Frozen mapping from results/INDEX.md ---
# class: matrix (the 14 confirmatory) | void | pilot | exploratory | cross (different rail/harness)
REGISTRY = [
    # 14 confirmatory matrix runs (ollama-cloud, base 1.0 / arm 1.x)
    ("a0-T-fix-r2",   dict(run="R01", arm="a0",  cls="matrix", rep=2)),
    ("a1m-T-fix-r2",  dict(run="R02", arm="a1m", cls="matrix", rep=2)),
    ("a2-T-fix-r2",   dict(run="R03", arm="a2",  cls="matrix", rep=2)),
    ("a3-T-fix-r2",   dict(run="R04", arm="a3",  cls="matrix", rep=2)),
    ("a0-T-fix-r3",   dict(run="R05", arm="a0",  cls="matrix", rep=3)),
    ("a3-T-fix-r3b",  dict(run="R06", arm="a3",  cls="matrix", rep=3)),
    ("a1m-T-fix-r3",  dict(run="R07", arm="a1m", cls="matrix", rep=3)),
    ("a2-T-fix-r3c",  dict(run="R08", arm="a2",  cls="matrix", rep=3)),
    ("a0-T-fix-r4",   dict(run="R09", arm="a0",  cls="matrix", rep=4)),
    ("a2-T-fix-r4",   dict(run="R10", arm="a2",  cls="matrix", rep=4)),
    ("a3-T-fix-r4",   dict(run="R11", arm="a3",  cls="matrix", rep=4)),
    ("a1m-T-fix-r4",  dict(run="R12", arm="a1m", cls="matrix", rep=4)),
    ("a0-T-fix-r5",   dict(run="R13", arm="a0",  cls="matrix", rep=5)),
    ("a0-T-fix-r6b",  dict(run="R14", arm="a0",  cls="matrix", rep=6)),
    # voids in the matrix window (excluded from comparison per protocol §5)
    ("a3-T-fix-r3",   dict(run="R06a", arm="a3",  cls="void", rep=3, why="#41 plan gate")),
    ("a2-T-fix-r3",   dict(run="R08a", arm="a2",  cls="void", rep=3, why="#41 validate gate")),
    ("a2-T-fix-r3b",  dict(run="R08b", arm="a2",  cls="void", rep=3, why="provider hang")),
    ("a0-T-fix-r6",   dict(run="R14a", arm="a0",  cls="void", rep=6, why="provider quota 429")),
    # pilots / exploratory (same rail, pre-matrix; context only)
    ("a0-T-fix-r1",   dict(run="pilot", arm="a0",  cls="pilot", rep=1, why="anchor")),
    ("a0v-T-fix-base1.0", dict(run="a0v", arm="a0", cls="exploratory", rep=0, why="base1.0 validation")),
    ("a1-T-fix-r1",   dict(run="a1.r1", arm="a1",  cls="pilot", rep=1)),
    ("a1m-T-fix-r1",  dict(run="a1m.r1", arm="a1m", cls="pilot", rep=1)),
    ("a1f-T-fix-r1",  dict(run="a1f.r1", arm="a1f", cls="pilot", rep=1, why="max-adoption variant")),
    ("a1m-T-fix-s374",dict(run="s374", arm="a1m", cls="exploratory", rep=0, why="shakedown (void)")),
    ("a1m-T-fix-s375",dict(run="s375", arm="a1m", cls="exploratory", rep=0, why="shakedown")),
    ("a2-T-fix-r1",   dict(run="a2.r1", arm="a2",  cls="pilot", rep=1)),
    ("a3-T-fix-r1",   dict(run="a3.r1", arm="a3",  cls="pilot", rep=1)),
    # cross-rail (Anthropic pricing) — NOT token-comparable to ollama runs
    ("a0c-T-fix-r1",  dict(run="a0c", arm="a0",  cls="cross", rep=1, why="Anthropic rail / cache economics")),
]

ARM_LABEL = {"a0":"A0 native","a1":"lean-ctx (early)","a1m":"lean-ctx (a1m)","a1f":"lean-ctx (a1f max)","a2":"headroom","a3":"rtk"}
ARM_MW = {"a1m":"lean-ctx","a1f":"lean-ctx","a1":"lean-ctx","a2":"headroom","a3":"rtk"}
PHASE_ORDER = ["plan","review-plan","implement","review-code","validate","approve","writeback","commit"]

def num(x):
    try: return int(x)
    except:
        try: return float(x)
        except: return None

def parse_tsv(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            ph = r.get("phase","")
            # phase name like CART-S01-T01__plan -> plan
            short = ph.split("__")[-1] if "__" in ph else ph
            rows.append(dict(
                phase=short, full_phase=ph,
                provider=r.get("provider"), model=r.get("model"),
                input=num(r.get("input")), output=num(r.get("output")),
                contextTokens=num(r.get("contextTokens")), turns=num(r.get("turns")),
                messages=num(r.get("messages")), seconds=num(r.get("seconds")),
                stopReason=r.get("stopReason"), error=(r.get("error") if r.get("error") not in (None,"-","") else None),
            ))
    return rows

def parse_gates(path):
    g = {}
    if os.path.exists(path):
        for line in open(path):
            if "=" in line:
                k,v = line.strip().split("=",1); g[k]=num(v)
    return g

def parse_manifest(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def parse_headroom(d):
    p = os.path.join(d,"headroom-stats.json")
    if not os.path.exists(p): return None
    h = json.load(open(p)); c = h["summary"]["compression"]; req = h.get("requests",{})
    return dict(meter="headroom", requests_total=req.get("total"), requests_compressed=c.get("requests_compressed"),
        cached=req.get("cached"), tokens_removed=c.get("total_tokens_removed"),
        avg_pct=c.get("avg_compression_pct"), best_pct=c.get("best_compression_pct"),
        before=c.get("total_tokens_before_with_cli_filtering"))

def parse_rtk(d):
    p = os.path.join(d,"rtk-history.txt")
    if not os.path.exists(p): return None
    t = open(p).read()
    def g(rx):
        m = re.search(rx, t); return m.group(1) if m else None
    return dict(meter="rtk", commands=num(g(r"Total commands:\s*([\d,]+)".replace(",",""))) or num((g(r"Total commands:\s*([\d,]+)") or "").replace(",","")),
        saved_raw=g(r"Tokens saved:\s*([\d.]+K?\s*\([\d.]+%\))"),
        savings_pct=g(r"\(([\d.]+)%\)"))

def parse_leanctx(d):
    p = os.path.join(d,"leanctx-gain.txt")
    if not os.path.exists(p): return None
    t = open(p).read()
    def g(rx):
        m = re.search(rx, t); return m.group(1) if m else None
    return dict(meter="lean-ctx",
        saved=g(r"([\d.]+K?)\s*\n?\s*tokens saved") or g(r"saved\s+([\d.]+K)\s*tokens"),
        reduction_pct=g(r"([\d.]+)%\s*reduction"),
        cache=g(r"cache\s+\S*\s*([\d.]+)%") or "0",
        usd=g(r"\$([\d.]+)\b"))

runs = []
for dname, meta in REGISTRY:
    d = os.path.join(RES, dname)
    tsv = os.path.join(d,"run-summary.tsv")
    if not os.path.exists(tsv):
        continue
    phases = parse_tsv(tsv)
    gates = parse_gates(os.path.join(d,"gates.txt"))
    man = parse_manifest(os.path.join(d,"run-manifest.json"))
    arm = meta["arm"]
    meter = None
    if arm.startswith("a1"): meter = parse_leanctx(d)
    elif arm=="a2": meter = parse_headroom(d)
    elif arm=="a3": meter = parse_rtk(d)
    total_in = sum(p["input"] for p in phases if p["input"])
    total_out = sum(p["output"] for p in phases if p["output"])
    total_turns = sum(p["turns"] for p in phases if p["turns"])
    total_sec = sum(p["seconds"] for p in phases if p["seconds"])
    all_stop = all(p["stopReason"]=="stop" for p in phases)
    gates_green = gates.get("build")==0 and gates.get("test")==0 and gates.get("lint")==0
    errs = [p for p in phases if p["error"]]
    runs.append(dict(
        dir=dname, run=meta["run"], arm=arm, arm_label=ARM_LABEL.get(arm,arm),
        middleware=ARM_MW.get(arm), cls=meta["cls"], rep=meta.get("rep"), why=meta.get("why"),
        total_input=total_in, total_output=total_out, total_turns=total_turns, total_seconds=total_sec,
        n_phases=len(phases), all_stop=all_stop, gates=gates, gates_green=gates_green,
        engage_check=man.get("engage_check"), start=man.get("start"), end=man.get("end"),
        image=man.get("image"), errors=[dict(phase=e["phase"], error=e["error"]) for e in errs],
        phases=phases, meter=meter,
    ))

# --- comparative aggregates over the 14 matrix runs ---
matrix = [r for r in runs if r["cls"]=="matrix"]
a0 = sorted([r["total_input"] for r in matrix if r["arm"]=="a0"])
a0_med = median(a0) if a0 else None
def arm_stats(arm):
    vals = sorted([r["total_input"] for r in matrix if r["arm"]==arm])
    if not vals: return None
    m = median(vals)
    return dict(arm=arm, n=len(vals), values=vals, min=min(vals), max=max(vals),
        median=m, mean=round(mean(vals)), std=round(pstdev(vals)),
        vs_a0_median_pct=round((m/a0_med-1)*100,1) if a0_med else None,
        inside_band=(min(a0)<=m<=max(a0)) if a0 else None)

agg = dict(
    a0_band=dict(min=min(a0), max=max(a0), median=a0_med, mean=round(mean(a0)), std=round(pstdev(a0)), values=a0) if a0 else None,
    arms={a: arm_stats(a) for a in ["a0","a1m","a2","a3"]},
)

# per-phase comparative: median input per phase per arm (matrix only)
phase_cmp = {}
for ph in PHASE_ORDER:
    phase_cmp[ph] = {}
    for arm in ["a0","a1m","a2","a3"]:
        vals = [next((p["input"] for p in r["phases"] if p["phase"]==ph), None) for r in matrix if r["arm"]==arm]
        vals = [v for v in vals if v]
        if vals:
            phase_cmp[ph][arm] = dict(median=round(median(vals)), min=min(vals), max=max(vals), n=len(vals))

out = dict(
    generated_note="parsed from results/*/run-summary.tsv — no hand-entered numbers",
    task="CART-S01-T01", phase_order=PHASE_ORDER, arm_label=ARM_LABEL,
    runs=runs, aggregates=agg, phase_compare=phase_cmp,
)
json.dump(out, open(os.path.join(os.path.dirname(__file__),"data.json"),"w"), indent=2)
print(f"runs parsed: {len(runs)} (matrix={len(matrix)}, void={sum(1 for r in runs if r['cls']=='void')}, other={sum(1 for r in runs if r['cls'] not in ('matrix','void'))})")
print(f"A0 band: {min(a0):,} - {max(a0):,}  median {a0_med:,}")
for a in ["a1m","a2","a3"]:
    s = agg["arms"][a]; print(f"  {a}: median {s['median']:,}  {s['vs_a0_median_pct']:+}%  {'INSIDE' if s['inside_band'] else 'OUTSIDE'}  (n={s['n']}, runs {s['values']})")
