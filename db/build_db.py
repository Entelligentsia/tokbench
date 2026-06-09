#!/usr/bin/env python3
"""Build tokbench.db — a queryable SQLite store of every run / phase / message /
tool-call / tool-result / meter in results/. Idempotent: drops and rebuilds from
disk each time. The DB is a DERIVED artifact; the transcripts remain source of truth.

Grains (one table per grain, FK-linked, raw JSON preserved on each):
  runs -> phases -> messages
                 -> tool_calls -> tool_results (forge_compress + lean-ctx compression)
  meter_metrics / meters_raw (per-run middleware meters)
  artifacts (summaries / reports)
"""
import csv, json, os, re, sqlite3, subprocess, glob
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES  = os.path.join(ROOT, "results")
DB   = os.path.join(os.path.dirname(__file__), "tokbench.db")

# ---- run registry (dir -> metadata), same frozen mapping as analysis/extract.py ----
REG = [
 ("a0-T-fix-r2","R01","a0","matrix",2,None),("a1m-T-fix-r2","R02","a1m","matrix",2,None),
 ("a2-T-fix-r2","R03","a2","matrix",2,None),("a3-T-fix-r2","R04","a3","matrix",2,None),
 ("a0-T-fix-r3","R05","a0","matrix",3,None),("a3-T-fix-r3b","R06","a3","matrix",3,None),
 ("a1m-T-fix-r3","R07","a1m","matrix",3,None),("a2-T-fix-r3c","R08","a2","matrix",3,None),
 ("a0-T-fix-r4","R09","a0","matrix",4,None),("a2-T-fix-r4","R10","a2","matrix",4,None),
 ("a3-T-fix-r4","R11","a3","matrix",4,None),("a1m-T-fix-r4","R12","a1m","matrix",4,None),
 ("a0-T-fix-r5","R13","a0","matrix",5,None),("a0-T-fix-r6b","R14","a0","matrix",6,None),
 ("a3-T-fix-r3","R06a","a3","void",3,"#41 plan gate"),("a2-T-fix-r3","R08a","a2","void",3,"#41 validate gate"),
 ("a2-T-fix-r3b","R08b","a2","void",3,"provider hang"),("a0-T-fix-r6","R14a","a0","void",6,"provider quota 429"),
 ("a0-T-fix-r1","pilot","a0","pilot",1,"anchor"),("a0v-T-fix-base1.0","a0v","a0","exploratory",0,"base1.0 validation"),
 ("a1-T-fix-r1","a1.r1","a1","pilot",1,None),("a1m-T-fix-r1","a1m.r1","a1m","pilot",1,None),
 ("a1f-T-fix-r1","a1f.r1","a1f","pilot",1,"max-adoption variant"),
 ("a1m-T-fix-s374","s374","a1m","exploratory",0,"shakedown void"),("a1m-T-fix-s375","s375","a1m","exploratory",0,"shakedown"),
 ("a2-T-fix-r1","a2.r1","a2","pilot",1,None),("a3-T-fix-r1","a3.r1","a3","pilot",1,None),
 ("a0c-T-fix-r1","a0c","a0","cross",1,"Anthropic rail / cache economics"),
]
MW = {"a1":"lean-ctx","a1m":"lean-ctx","a1f":"lean-ctx","a2":"headroom","a3":"rtk"}
PHASE_ORD = {p:i for i,p in enumerate(
    ["plan","review-plan","implement","review-code","validate","approve","writeback","commit"])}
NATIVE = {"read","write","edit","multiedit","bash","shell","grep","glob","ls","find","tree","cat"}

def num(x):
    if x in (None,"","-"): return None
    try: return int(x)
    except:
        try: return float(x)
        except: return None

def tool_class(name):
    if not name: return "other"
    if name.startswith("ctx_"): return "ctx"
    if name.startswith("forge_"): return "forge"
    if name.lower() in NATIVE: return "native"
    return "other"

def git_sha():
    try: return subprocess.check_output(["git","-C",ROOT,"rev-parse","--short","HEAD"],text=True).strip()
    except Exception: return None

# ---------------- schema ----------------
DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE meta(schema_version INT, generated_at TEXT, git_sha TEXT, source_root TEXT);
CREATE TABLE runs(
  run_id TEXT PRIMARY KEY, dir TEXT, arm TEXT, middleware TEXT, class TEXT, rep INT,
  task TEXT, status TEXT, void_reason TEXT, all_stop INT,
  gates_build INT, gates_test INT, gates_lint INT, gates_green INT,
  image TEXT, started_at TEXT, ended_at TEXT, wall_seconds INT, engage_check TEXT,
  total_input INT, total_output INT, total_turns INT, n_phases INT,
  operator_notes TEXT, raw_manifest TEXT);
CREATE TABLE phases(
  phase_id INTEGER PRIMARY KEY, run_id TEXT REFERENCES runs(run_id), phase TEXT, ordinal INT,
  provider TEXT, model TEXT, input INT, output INT, context_tokens INT,
  turns INT, messages INT, seconds INT, stop_reason TEXT, error TEXT,
  started_at TEXT, ended_at TEXT);
CREATE TABLE messages(
  message_id INTEGER PRIMARY KEY, phase_id INT REFERENCES phases(phase_id), run_id TEXT,
  phase TEXT, idx INT, role TEXT, has_toolcall INT,
  input INT, output INT, cache_read INT, cache_write INT, total_tokens INT, cost_total REAL,
  provider TEXT, model TEXT, raw_usage TEXT);
CREATE TABLE tool_calls(
  call_id INTEGER PRIMARY KEY, phase_id INT REFERENCES phases(phase_id), run_id TEXT, phase TEXT,
  idx INT, tool_call_uid TEXT, tool_name TEXT, tool_class TEXT, arguments TEXT);
CREATE TABLE tool_results(
  result_id INTEGER PRIMARY KEY, phase_id INT REFERENCES phases(phase_id), run_id TEXT, phase TEXT,
  tool_call_uid TEXT, tool_name TEXT, tool_class TEXT, is_error INT, content_tokens_est INT,
  comp_source TEXT, comp_subtool TEXT, comp_before INT, comp_after INT, comp_saved_pct REAL,
  raw_details TEXT);
CREATE TABLE meter_metrics(
  run_id TEXT REFERENCES runs(run_id), source TEXT, metric TEXT, num_value REAL, text_value TEXT);
CREATE TABLE meters_raw(run_id TEXT REFERENCES runs(run_id), source TEXT, raw TEXT);
CREATE TABLE artifacts(
  run_id TEXT REFERENCES runs(run_id), phase TEXT, name TEXT, kind TEXT, content TEXT);
CREATE INDEX ix_phase_run ON phases(run_id);
CREATE INDEX ix_msg_phase ON messages(phase_id);
CREATE INDEX ix_msg_run ON messages(run_id);
CREATE INDEX ix_tc_phase ON tool_calls(phase_id);
CREATE INDEX ix_tc_class ON tool_calls(tool_class);
CREATE INDEX ix_tr_phase ON tool_results(phase_id);
CREATE INDEX ix_tr_comp ON tool_results(comp_source);
CREATE INDEX ix_mm ON meter_metrics(run_id, source, metric);
"""

VIEWS = """
CREATE VIEW v_run_totals AS
  SELECT run_id, arm, middleware, class, status, total_input, total_output, total_turns,
         gates_green, all_stop,
         CAST(total_input AS REAL)/NULLIF(total_turns,0) AS input_per_turn
  FROM runs;
CREATE VIEW v_matrix AS SELECT * FROM runs WHERE class='matrix';
CREATE VIEW v_arm_phase_avg AS
  SELECT r.arm, p.phase, p.ordinal,
         COUNT(*) n, ROUND(AVG(p.input)) avg_input, MIN(p.input) min_input, MAX(p.input) max_input,
         ROUND(AVG(p.output)) avg_output, ROUND(AVG(p.turns),1) avg_turns
  FROM phases p JOIN runs r USING(run_id) WHERE r.class='matrix'
  GROUP BY r.arm, p.phase, p.ordinal ORDER BY p.ordinal,
    CASE r.arm WHEN 'a0' THEN 0 WHEN 'a1m' THEN 1 WHEN 'a2' THEN 2 ELSE 3 END;
CREATE VIEW v_forge_compress AS
  SELECT r.arm, tr.run_id, tr.comp_subtool AS tool, COUNT(*) calls,
         SUM(tr.comp_before) before_tok, SUM(tr.comp_after) after_tok,
         SUM(tr.comp_before-tr.comp_after) saved_tok,
         ROUND(100.0*SUM(tr.comp_before-tr.comp_after)/NULLIF(SUM(tr.comp_before),0),1) saved_pct
  FROM tool_results tr JOIN runs r USING(run_id)
  WHERE tr.comp_source='forge' GROUP BY r.arm, tr.run_id, tr.comp_subtool;
CREATE VIEW v_tool_class AS
  SELECT r.arm, tc.run_id, tc.tool_class, COUNT(*) calls
  FROM tool_calls tc JOIN runs r USING(run_id) GROUP BY r.arm, tc.run_id, tc.tool_class;
"""

# ---------------- parse helpers ----------------
def parse_gates(d):
    g={}; p=os.path.join(d,"gates.txt")
    if os.path.exists(p):
        for line in open(p):
            if "=" in line:
                k,v=line.strip().split("=",1); g[k]=num(v)
    return g

def short_phase(full):
    return full.split("__")[-1] if "__" in full else full

def flatten_metrics(obj, prefix=""):
    """yield (metric, num, text) for numeric/string leaves, one level deep into dicts."""
    out=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            key=f"{prefix}{k}"
            if isinstance(v,(int,float)) and not isinstance(v,bool): out.append((key,float(v),None))
            elif isinstance(v,str): out.append((key,None,v))
            elif isinstance(v,dict): out.extend(flatten_metrics(v,key+"."))
    return out

def parse_rtk_history(txt):
    m={}
    def g(rx):
        r=re.search(rx,txt); return r.group(1) if r else None
    if (v:=g(r"Total commands:\s*([\d,]+)")): m["total_commands"]=float(v.replace(",",""))
    if (v:=g(r"Tokens saved:\s*([\d.]+)K")): m["tokens_saved_k"]=float(v)
    if (v:=g(r"\(([\d.]+)%\)")): m["savings_pct"]=float(v)
    if (v:=g(r"avg ([\d.]+)ms")): m["avg_ms"]=float(v)
    return m

# ---------------- build ----------------
def build():
    if os.path.exists(DB): os.remove(DB)
    for ext in ("-wal","-shm"):
        if os.path.exists(DB+ext): os.remove(DB+ext)
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.executescript(DDL)
    cur.execute("INSERT INTO meta VALUES(?,?,?,?)",(1,datetime.now(timezone.utc).isoformat(),git_sha(),RES))

    counts={"runs":0,"phases":0,"messages":0,"tool_calls":0,"tool_results":0,"meter_metrics":0,"artifacts":0}
    for dname,run_id,arm,cls,rep,why in REG:
        d=os.path.join(RES,dname)
        tsv=os.path.join(d,"run-summary.tsv")
        if not os.path.exists(tsv): continue
        man=json.load(open(os.path.join(d,"run-manifest.json"))) if os.path.exists(os.path.join(d,"run-manifest.json")) else {}
        g=parse_gates(d)
        # phases
        prows=list(csv.DictReader(open(tsv),delimiter="\t"))
        ph_objs=[]
        for r in prows:
            ph=short_phase(r["phase"])
            ph_objs.append(dict(phase=ph,ordinal=PHASE_ORD.get(ph,99),provider=r.get("provider"),
                model=r.get("model"),input=num(r["input"]),output=num(r["output"]),
                context_tokens=num(r.get("contextTokens")),turns=num(r.get("turns")),
                messages=num(r.get("messages")),seconds=num(r.get("seconds")),
                stop_reason=r.get("stopReason"),error=(r.get("error") if r.get("error") not in (None,"-","") else None)))
        all_stop=all(p["stop_reason"]=="stop" for p in ph_objs)
        gg = 1 if (g.get("build")==0 and g.get("test")==0 and g.get("lint")==0) else 0
        status = "void" if cls=="void" else ("counts" if cls=="matrix" else cls)
        start,end=man.get("start"),man.get("end")
        wall=None
        try: wall=int((datetime.fromisoformat(end.replace("Z","+00:00"))-datetime.fromisoformat(start.replace("Z","+00:00"))).total_seconds())
        except Exception: pass
        cur.execute("""INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
            run_id,dname,arm,MW.get(arm),cls,rep,man.get("task","CART-S01-T01"),status,why,1 if all_stop else 0,
            g.get("build"),g.get("test"),g.get("lint"),gg,man.get("image"),start,end,wall,man.get("engage_check"),
            sum(p["input"] or 0 for p in ph_objs),sum(p["output"] or 0 for p in ph_objs),
            sum(p["turns"] or 0 for p in ph_objs),len(ph_objs),man.get("operator_notes"),json.dumps(man)))
        counts["runs"]+=1
        # phases + transcripts
        for p in ph_objs:
            cur.execute("""INSERT INTO phases(run_id,phase,ordinal,provider,model,input,output,context_tokens,
                turns,messages,seconds,stop_reason,error,started_at,ended_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                run_id,p["phase"],p["ordinal"],p["provider"],p["model"],p["input"],p["output"],p["context_tokens"],
                p["turns"],p["messages"],p["seconds"],p["stop_reason"],p["error"],None,None))
            phase_id=cur.lastrowid; counts["phases"]+=1
            tfs=glob.glob(os.path.join(d,"transcripts","*",f"*__{p['phase']}.json"))
            if not tfs: continue
            try: tj=json.load(open(tfs[0]))
            except Exception: continue
            for idx,m in enumerate(tj.get("messages",[])):
                if not isinstance(m,dict): continue
                role=m.get("role"); u=m.get("usage") if isinstance(m.get("usage"),dict) else None
                blocks=m.get("content") if isinstance(m.get("content"),list) else []
                has_tc=any(isinstance(b,dict) and b.get("type")=="toolCall" for b in blocks)
                if u or role=="assistant":
                    cost=u.get("cost") if u else None
                    cost_total=cost.get("total") if isinstance(cost,dict) else (cost if isinstance(cost,(int,float)) else None)
                    cur.execute("""INSERT INTO messages(phase_id,run_id,phase,idx,role,has_toolcall,input,output,
                        cache_read,cache_write,total_tokens,cost_total,provider,model,raw_usage) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                        phase_id,run_id,p["phase"],idx,role,1 if has_tc else 0,
                        (u or {}).get("input"),(u or {}).get("output"),(u or {}).get("cacheRead"),(u or {}).get("cacheWrite"),
                        (u or {}).get("totalTokens"),cost_total,m.get("provider"),m.get("model"),json.dumps(u) if u else None))
                    counts["messages"]+=1
                # tool calls
                for b in blocks:
                    if isinstance(b,dict) and b.get("type")=="toolCall":
                        nm=b.get("name")
                        cur.execute("""INSERT INTO tool_calls(phase_id,run_id,phase,idx,tool_call_uid,tool_name,tool_class,arguments)
                            VALUES(?,?,?,?,?,?,?,?)""",(phase_id,run_id,p["phase"],idx,b.get("id"),nm,tool_class(nm),
                            json.dumps(b.get("arguments") or b.get("input"))))
                        counts["tool_calls"]+=1
                # tool results
                if role=="toolResult":
                    nm=m.get("toolName"); det=m.get("details") if isinstance(m.get("details"),dict) else {}
                    comp=det.get("compression") if isinstance(det.get("compression"),dict) else None
                    cs=cb=ca=csp=csub=None
                    if comp:
                        if "before" in comp:   # forge native format
                            cs="forge"; cb=comp.get("before"); ca=comp.get("after"); csp=comp.get("saved"); csub=comp.get("tool")
                        elif "originalTokens" in comp:  # lean-ctx format
                            cs="lean-ctx"; cb=comp.get("originalTokens"); ca=comp.get("compressedTokens")
                            csp=comp.get("percentSaved"); csub=det.get("source","lean-ctx")
                    cont=m.get("content"); ctok=len(json.dumps(cont))//4 if cont is not None else None
                    cur.execute("""INSERT INTO tool_results(phase_id,run_id,phase,tool_call_uid,tool_name,tool_class,
                        is_error,content_tokens_est,comp_source,comp_subtool,comp_before,comp_after,comp_saved_pct,raw_details)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(phase_id,run_id,p["phase"],m.get("toolCallId"),nm,tool_class(nm),
                        1 if m.get("isError") else 0,ctok,cs,csub,cb,ca,
                        (float(csp) if csp is not None else None),json.dumps(det) if det else None))
                    counts["tool_results"]+=1
        # ---- meters ----
        meter_files=[("lean-ctx","leanctx-config/stats.json"),("lean-ctx","leanctx-config/mcp-live.json"),
                     ("headroom","headroom-stats.json"),("rtk","rtk-gain.json")]
        for src,rel in meter_files:
            fp=os.path.join(d,rel)
            if not os.path.exists(fp): continue
            try: obj=json.load(open(fp))
            except Exception: continue
            cur.execute("INSERT INTO meters_raw VALUES(?,?,?)",(run_id,src,json.dumps(obj)))
            scope = obj.get("summary",{}).get("compression",{}) if (src=="headroom" and isinstance(obj,dict)) else obj
            for metric,nv,tv in flatten_metrics(scope):
                cur.execute("INSERT INTO meter_metrics VALUES(?,?,?,?,?)",(run_id,src,metric,nv,tv)); counts["meter_metrics"]+=1
        # rtk history text
        rh=os.path.join(d,"rtk-history.txt")
        if os.path.exists(rh):
            txt=open(rh).read(); cur.execute("INSERT INTO meters_raw VALUES(?,?,?)",(run_id,"rtk",txt[:8000]))
            for metric,v in parse_rtk_history(txt).items():
                cur.execute("INSERT INTO meter_metrics VALUES(?,?,?,?,?)",(run_id,"rtk",metric,v,None)); counts["meter_metrics"]+=1
        # leanctx-gain.txt raw
        lg=os.path.join(d,"leanctx-gain.txt")
        if os.path.exists(lg):
            cur.execute("INSERT INTO meters_raw VALUES(?,?,?)",(run_id,"lean-ctx-gain",open(lg).read()[:8000]))
        # ---- artifacts: *-SUMMARY.json + COST_REPORT.md ----
        for fp in glob.glob(os.path.join(d,"sprint-*","**","*-SUMMARY.json"),recursive=True)+\
                  glob.glob(os.path.join(d,"sprint-*","COST_REPORT.md")):
            try:
                cur.execute("INSERT INTO artifacts VALUES(?,?,?,?,?)",
                    (run_id,None,os.path.basename(fp),"summary" if fp.endswith(".json") else "report",open(fp).read()[:20000]))
                counts["artifacts"]+=1
            except Exception: pass

    cur.executescript(VIEWS)
    con.commit()
    # summary
    print(f"built {DB}  ({os.path.getsize(DB)//1024} KB)")
    for t,n in counts.items(): print(f"  {t:14} {n:,}")
    print("rows by run class:")
    for cls,n in cur.execute("SELECT class,COUNT(*) FROM runs GROUP BY class ORDER BY 2 DESC"): print(f"  {cls:12} {n}")
    con.close()

if __name__=="__main__":
    build()
