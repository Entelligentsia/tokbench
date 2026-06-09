#!/usr/bin/env python3
"""Render analysis/data.json into a single self-contained dashboard.html.
No external deps: data is inlined, charts are CSS, tables sort in vanilla JS."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "data.json")))
PAYLOAD = json.dumps(data, separators=(",", ":"))

HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>tokbench — 14-run analytics</title>
<style>
:root{
  --bg:#0d1117; --panel:#161b22; --panel2:#1c2230; --line:#2a3038; --ink:#e6edf3; --dim:#8b949e;
  --a0:#58a6ff; --a1m:#f778ba; --a2:#3fb950; --a3:#d29922; --band:#1f6feb22; --bad:#f85149; --ok:#3fb950;
  --mono:"SF Mono",ui-monospace,"Cascadia Code",Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--a0)}
header.top{padding:28px 32px 18px;border-bottom:1px solid var(--line);position:relative}
header.top h1{margin:0 0 4px;font-size:22px;letter-spacing:-.3px}
header.top .sub{color:var(--dim);font-size:13px}
nav{position:sticky;top:0;z-index:9;background:#0d1117ee;backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
  padding:8px 32px;display:flex;gap:18px;flex-wrap:wrap;font-size:13px}
nav a{color:var(--dim);text-decoration:none;white-space:nowrap}
nav a:hover{color:var(--ink)}
main{padding:24px 32px 80px;max-width:1280px}
section{margin:34px 0;scroll-margin-top:52px}
h2{font-size:17px;margin:0 0 4px;letter-spacing:-.2px}
.lede{color:var(--dim);font-size:13px;margin:0 0 16px;max-width:780px}
.mono{font-family:var(--mono)}
.grid{display:grid;gap:14px}
.cards{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.card h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:var(--dim)}
.big{font-family:var(--mono);font-size:26px;font-weight:600}
.tag{display:inline-block;font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:20px;border:1px solid var(--line)}
.tag.inside{color:#9be9a8;border-color:#2ea04366;background:#2ea04318}
.tag.outside{color:#ffb4b0;border-color:#f8514966;background:#f8514918}
.tag.void{color:#d8b56a;border-color:#d2992266;background:#d2992218}
.swatch{width:9px;height:9px;border-radius:2px;display:inline-block;margin-right:6px;vertical-align:middle}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--dim);font-weight:600;cursor:pointer;user-select:none;position:sticky;top:40px;background:var(--bg)}
th:hover{color:var(--ink)}
tbody tr:hover{background:#ffffff06}
td.num,th.num{font-family:var(--mono)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
.bar{height:13px;border-radius:3px;display:inline-block;vertical-align:middle}
.barwrap{position:relative;background:#ffffff08;border-radius:3px;height:13px;min-width:120px}
.bandline{position:absolute;top:-3px;bottom:-3px;background:var(--band);border-left:1px dashed #1f6feb88;border-right:1px dashed #1f6feb88}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--dim);margin:8px 0 14px}
.phasegrid{display:grid;grid-template-columns:auto repeat(8,1fr) auto;gap:3px;font-size:11px;font-family:var(--mono)}
.phasegrid .hd{color:var(--dim);text-align:center;padding:4px 2px}
.cell{padding:6px 4px;text-align:center;border-radius:3px;color:#0d1117;font-weight:600}
.rowlab{color:var(--ink);padding:6px 8px 6px 0;text-align:left;white-space:nowrap}
.note{color:var(--dim);font-size:12px;margin-top:8px}
.flex{display:flex;gap:24px;flex-wrap:wrap}
.metercard{flex:1;min-width:260px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.metercard .vs{display:flex;justify-content:space-between;align-items:baseline;margin:6px 0;padding:6px 0;border-bottom:1px dashed var(--line)}
.metercard .vs:last-child{border:0}
.pos{color:var(--bad)} .neg{color:var(--ok)}
.kv{display:flex;justify-content:space-between;font-size:12px;color:var(--dim);margin:3px 0}
.kv b{color:var(--ink);font-family:var(--mono);font-weight:600}
hr{border:0;border-top:1px solid var(--line);margin:0}
.pill-row{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 0}
details{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:6px 0}
summary{cursor:pointer;color:var(--dim);font-size:12px}
.warn{color:#d8b56a}
</style></head>
<body>
<header class="top">
  <h1>tokbench — context-middleware benchmark</h1>
  <div class="sub mono" id="hdrsub"></div>
</header>
<nav id="nav"></nav>
<main>
  <section id="verdict"><h2>Verdict</h2><p class="lede">Primary metric: total provider-billed input tokens per successful run (task CART-S01-T01, ollama-cloud, forge-cli 1.0.21). Claim rule §3: an arm's median outside the A0×5 native band is a real effect.</p><div id="verdict-body"></div></section>

  <section id="arms"><h2>Arm comparison — every matrix run</h2><p class="lede">Each bar is one confirmatory run's total billed input. Shaded column = the A0×5 native noise band (min–max). A middleware bar landing inside the band is indistinguishable from running nothing.</p><div id="arm-legend" class="legend"></div><div id="arm-bars" class="scroll" style="padding:14px"></div><div id="arm-stats" class="scroll" style="margin-top:14px"></div></section>

  <section id="runs"><h2>All 14 runs — full record</h2><p class="lede">Click any column to sort. Every comparable per-run datum: totals, turns, model-time, wall, gates, completion, engage-check.</p><div id="runs-table" class="scroll"></div></section>

  <section id="phases"><h2>Per-phase token profile</h2><p class="lede">The eight pipeline phases for every run. Cell brightness ∝ billed input for that phase. The commit and validate columns swing wildest — that run-path variance, not middleware, drives most of the spread.</p><div id="phase-grid" style="overflow-x:auto"></div><h3 style="margin-top:22px;font-size:13px;color:var(--dim)">Per-arm phase medians (input tokens)</h3><div id="phase-medians" class="scroll" style="padding:14px"></div></section>

  <section id="meters"><h2>The three meters never agree</h2><p class="lede">Each middleware reports savings on its own denominator at its own layer. The provider's bill is the only neutral meter — and it disagrees with all three.</p><div id="meter-cards" class="flex"></div></section>

  <section id="variance"><h2>Noise floor &amp; variance</h2><p class="lede">Across the five A0 anchors (run over several days) the native total spreads sharply, and per-phase swings are larger still — the commit phase alone moves ~40×. Single-run benchmarks cannot detect sub-5% effects; hence the A0×5 design and median-vs-band rule.</p><div id="variance-body"></div></section>

  <section id="voids"><h2>Voids (excluded per §5)</h2><p class="lede">Published but excluded from token comparison. None implicate the middleware — every failure is harness (#41) or provider (hang / quota).</p><div id="voids-table" class="scroll"></div></section>

  <section id="context"><h2>Context runs — pilots / exploratory / cross-rail</h2><p class="lede warn">Not part of the 14-run comparison. Pilots predate the frozen protocol; a0c runs on the Anthropic rail (cache economics) and is <b>not token-comparable</b> to the ollama runs.</p><div id="context-table" class="scroll"></div></section>
</main>
<script>const DATA = __PAYLOAD__;</script>
<script>
const D=DATA, P=D.phase_order, AGG=D.aggregates;
const ARMC={a0:'--a0',a1m:'--a1m',a2:'--a2',a3:'--a3',a1:'--a1m',a1f:'--a1m'};
const cssv=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt=n=>n==null?'—':n.toLocaleString('en-US');
const k=n=>n==null?'—':(n>=1e6?(n/1e6).toFixed(2)+'M':n>=1e3?(n/1e3).toFixed(0)+'K':n);
const pct=n=>n==null?'—':(n>0?'+':'')+n+'%';
const el=(t,a={},...c)=>{const e=document.createElement(t);for(const x in a){if(x=='class')e.className=a[x];else if(x=='html')e.innerHTML=a[x];else e.setAttribute(x,a[x]);}c.forEach(x=>e.append(x));return e;};
const matrix=D.runs.filter(r=>r.cls=='matrix');
const armColor=a=>cssv(ARMC[a]||'--dim');

// header
document.getElementById('hdrsub').textContent=`14/14 confirmatory · ${D.runs.length} runs on disk · task ${D.task} · parsed live from run-summary.tsv`;

// nav
const NAVS=[['verdict','Verdict'],['arms','Arms'],['runs','14 runs'],['phases','Phases'],['meters','Meters'],['variance','Variance'],['voids','Voids'],['context','Context']];
document.getElementById('nav').append(...NAVS.map(([h,t])=>el('a',{href:'#'+h},t)));

// ---- verdict ----
const band=AGG.a0_band;
const vb=document.getElementById('verdict-body');
const vcards=el('div',{class:'grid cards'});
vcards.append(el('div',{class:'card'},
  el('h3',{},'A0×5 native band'),
  el('div',{class:'big',html:`${k(band.min)} – ${k(band.max)}`}),
  el('div',{class:'note',html:`median <b class=mono>${fmt(band.median)}</b> · σ ${(band.std/band.median*100).toFixed(1)}% · n=5`})));
for(const a of ['a2','a3','a1m']){
  const s=AGG.arms[a]; if(!s)continue;
  const mw={a1m:'lean-ctx',a2:'headroom',a3:'rtk'}[a];
  vcards.append(el('div',{class:'card'},
    el('h3',{html:`<span class=swatch style="background:${armColor(a)}"></span>${mw}`}),
    el('div',{class:'big'},pct(s.vs_a0_median_pct)),
    el('div',{class:'note',html:`median <b class=mono>${fmt(s.median)}</b> vs A0`}),
    el('div',{class:'pill-row'},el('span',{class:'tag '+(s.inside_band?'inside':'outside')},s.inside_band?'INSIDE band':'OUTSIDE ↑'))));
}
vb.append(vcards);
vb.append(el('p',{class:'lede',style:'margin-top:16px',html:'<b>No middleware arm achieves a net token reduction that clears the native noise floor.</b> Headroom — the best case — only reaches parity with running nothing, despite genuine wire-level compression. rtk and lean-ctx land measurably above native: rule-injection and orchestration overhead exceed their own savings.'}));

// ---- arm bars ----
const allInputs=matrix.map(r=>r.total_input);
const maxIn=Math.max(...allInputs)*1.04;
const order=['a0','a1m','a2','a3'];
const leg=document.getElementById('arm-legend');
leg.append(...order.map(a=>el('span',{},el('span',{class:'swatch',style:`background:${armColor(a)}`}),D.arm_label[a])),
  el('span',{},el('span',{class:'swatch',style:`background:${cssv('--band')};border:1px dashed #1f6feb88`}),'A0 band'));
const barsHost=document.getElementById('arm-bars');
const bt=el('table');
const tb=el('tbody');
const bandL=band.min/maxIn*100, bandW=(band.max-band.min)/maxIn*100;
for(const a of order){
  for(const r of matrix.filter(x=>x.arm==a).sort((x,y)=>x.total_input-y.total_input)){
    const w=r.total_input/maxIn*100;
    const bw=el('div',{class:'barwrap',style:'width:min(640px,60vw)'});
    bw.append(el('div',{class:'bandline',style:`left:${bandL}%;width:${bandW}%`}));
    bw.append(el('div',{class:'bar',style:`width:${w}%;background:${armColor(a)}`}));
    tb.append(el('tr',{},
      el('td',{html:`<span class=mono style="color:var(--dim)">${r.run}</span> &nbsp;<span class=swatch style="background:${armColor(a)}"></span>${D.arm_label[a]}`}),
      el('td',{class:'num',style:`color:${armColor(a)}`},fmt(r.total_input)),
      el('td',{},bw)));
  }
}
bt.append(el('thead',{},el('tr',{},el('th',{},'run / arm'),el('th',{class:'num'},'billed input'),el('th',{},'')))); bt.append(tb);
barsHost.append(bt);

// arm stats table
const statRows=order.map(a=>{const s=AGG.arms[a];return {a,...s};});
const sCols=[['arm','arm',r=>`<span class=swatch style="background:${armColor(r.a)}"></span>${D.arm_label[r.a]}`],
 ['n','n',r=>r.n],['min','min',r=>fmt(r.min)],['median','median',r=>`<b>${fmt(r.median)}</b>`],['max','max',r=>fmt(r.max)],
 ['mean','mean',r=>fmt(r.mean)],['std','σ (spread)',r=>fmt(r.std)],['vs_a0_median_pct','vs A0 median',r=>r.a=='a0'?'—':pct(r.vs_a0_median_pct)],
 ['inside_band','§3 verdict',r=>r.a=='a0'?'<span class=tag>baseline</span>':`<span class="tag ${r.inside_band?'inside':'outside'}">${r.inside_band?'INSIDE':'OUTSIDE ↑'}</span>`]];
document.getElementById('arm-stats').append(buildTable(statRows,sCols,false));

// ---- 14 runs table ----
const runRows=matrix.map(r=>({
  run:r.run,arm:r.arm,arm_label:D.arm_label[r.arm],dir:r.dir,input:r.total_input,output:r.total_output,
  turns:r.total_turns,sec:r.total_seconds,wall:r.start&&r.end?Math.round((Date.parse(r.end)-Date.parse(r.start))/60000):null,
  stop:r.all_stop,gates:r.gates_green,engage:r.engage_check}));
const rCols=[
 ['run','run',r=>`<span class=mono>${r.run}</span>`],
 ['arm','arm',r=>`<span class=swatch style="background:${armColor(r.arm)}"></span>${r.arm_label}`],
 ['input','billed input',r=>`<b class=mono>${fmt(r.input)}</b>`],
 ['output','output',r=>fmt(r.output)],
 ['turns','turns',r=>fmt(r.turns)],
 ['sec','model s',r=>fmt(r.sec)],
 ['wall','wall min',r=>r.wall],
 ['stop','8/8 stop',r=>r.stop?'<span style="color:var(--ok)">✓</span>':'<span style="color:var(--bad)">✗</span>'],
 ['gates','gates',r=>r.gates?'<span style="color:var(--ok)">green</span>':'<span style="color:var(--bad)">fail</span>'],
 ['engage','engage-check',r=>`<span style="color:var(--dim);font-size:12px">${r.engage||'—'}</span>`],
];
document.getElementById('runs-table').append(buildTable(runRows,rCols,true,'input'));

// ---- phase grid ----
const pg=el('div',{class:'phasegrid',style:'min-width:760px'});
pg.append(el('div',{class:'hd'},''));
P.forEach(p=>pg.append(el('div',{class:'hd'},p)));
pg.append(el('div',{class:'hd'},'Σ input'));
// global max phase value across matrix for color scale
let pmax=0; matrix.forEach(r=>r.phases.forEach(ph=>{if(ph.input>pmax)pmax=ph.input;}));
const heat=(v,a)=>{const t=Math.sqrt(v/pmax);const c=armColor(a);return `background:color-mix(in srgb, ${c} ${Math.round(t*100)}%, #0d1117);color:${t>.55?'#0d1117':'#e6edf3'}`;};
for(const a of order)for(const r of matrix.filter(x=>x.arm==a).sort((x,y)=>x.run.localeCompare(y.run,undefined,{numeric:true}))){
  pg.append(el('div',{class:'rowlab',html:`<span class=mono style="color:var(--dim)">${r.run}</span> <span class=swatch style="background:${armColor(a)}"></span>${D.arm_label[a]}`}));
  P.forEach(p=>{const ph=r.phases.find(x=>x.phase==p);const v=ph?ph.input:0;
    pg.append(el('div',{class:'cell',title:`${r.run} ${p}: ${fmt(v)} in · ${ph?ph.turns:'?'}t · ${ph?ph.stopReason:''}`,style:heat(v,a)},k(v)));});
  pg.append(el('div',{class:'cell',style:'background:#21262d;color:#e6edf3'},k(r.total_input)));
}
document.getElementById('phase-grid').append(pg);

// phase medians per arm (grouped bars)
const pm=D.phase_compare;
let pmMax=0; for(const p in pm)for(const a in pm[p])if(pm[p][a].median>pmMax)pmMax=pm[p][a].median;
const pmt=el('table');const pmb=el('tbody');
pmt.append(el('thead',{},el('tr',{},el('th',{},'phase'),...order.map(a=>el('th',{class:'num',html:`<span class=swatch style="background:${armColor(a)}"></span>${a}`})),el('th',{},'spread'))));
for(const p of P){
  const cells=order.map(a=>{const m=pm[p][a]?pm[p][a].median:null;return el('td',{class:'num',style:m?`color:${armColor(a)}`:''},m?fmt(m):'—');});
  // mini spread bar showing min..max of all arms for this phase
  const vals=order.flatMap(a=>pm[p][a]?[pm[p][a].min,pm[p][a].max]:[]);
  const mn=Math.min(...vals),mx=Math.max(...vals);
  const sb=el('div',{class:'barwrap',style:'width:200px'});
  sb.append(el('div',{class:'bar',style:`margin-left:${mn/pmMax*100}%;width:${(mx-mn)/pmMax*100}%;background:#6e7681`}));
  pmb.append(el('tr',{},el('td',{},p),...cells,el('td',{},sb)));
}
pmt.append(pmb);document.getElementById('phase-medians').append(pmt);

// ---- meters ----
const mh=document.getElementById('meter-cards');
const meterInfo={
 a1m:{mw:'lean-ctx',layer:'tool layer',rows:r=>[['vendor meter (this run)',`${r.meter.saved} saved · ${r.meter.reduction_pct}% reduction`,'neg'],['cache hit rate',`${r.meter.cache}%`,r.meter.cache=='0'?'pos':''],['the bill says','+'+AGG.arms.a1m.vs_a0_median_pct+'% vs native','pos']],
   foot:'Cache mechanism works on pi (3.7.5) — but phase isolation zeroes its surface. “Flawless, 0 saved.”'},
 a3:{mw:'rtk',layer:'command layer',rows:r=>[['vendor meter (this run)',`${r.meter.commands} cmds · ${r.meter.saved_raw} on touched`,'neg'],['addressable surface','~1–2.5% of bill','pos'],['the bill says','+'+AGG.arms.a3.vs_a0_median_pct+'% vs native','pos']],
   foot:'Works exactly as designed; the slice it can touch is below the noise floor.'},
 a2:{mw:'headroom',layer:'wire layer',rows:r=>[['vendor meter (this run)',`${r.meter.requests_compressed}/${r.meter.requests_total} compressed · −${k(r.meter.tokens_removed)} (${r.meter.avg_pct}% avg)`,'neg'],['prefix cache stored',`${r.meter.cached}`,'pos'],['the bill says','+'+AGG.arms.a2.vs_a0_median_pct+'% vs native','pos']],
   foot:'Genuine on-wire compression (ledger-exact) — swamped by run-path variance; nets to parity, inside the band.'}
};
for(const a of ['a2','a3','a1m']){
  const reps=matrix.filter(r=>r.arm==a&&r.meter);
  const r=reps[reps.length-1]; const mi=meterInfo[a];
  const c=el('div',{class:'metercard'});
  c.append(el('h3',{style:`color:${armColor(a)};margin:0 0 2px`,html:`<span class=swatch style="background:${armColor(a)}"></span>${mi.mw}`}));
  c.append(el('div',{class:'note',style:'margin:0 0 10px'},mi.layer+' · meter from '+r.run));
  mi.rows(r).forEach(([lab,val,cl])=>c.append(el('div',{class:'vs'},el('span',{class:'note',style:'margin:0'},lab),el('b',{class:cl||'',style:'font-family:var(--mono)'},val))));
  c.append(el('div',{class:'note',style:'margin-top:10px;font-style:italic'},mi.foot));
  mh.append(c);
}

// ---- variance ----
const vbody=document.getElementById('variance-body');
const commit=pm['commit'], validate=pm['validate'];
const vcard=el('div',{class:'grid cards'});
function spreadCard(name,obj){
  const allv=order.flatMap(a=>obj[a]?[obj[a].min,obj[a].max]:[]);
  return el('div',{class:'card'},el('h3',{},name+' phase swing'),
    el('div',{class:'big'},`${k(Math.min(...allv))} – ${k(Math.max(...allv))}`),
    el('div',{class:'note'},`${(Math.max(...allv)/Math.min(...allv)).toFixed(0)}× range across all matrix runs`));
}
vcard.append(spreadCard('commit',commit));
vcard.append(spreadCard('validate',validate));
const mwMax=Math.max(AGG.arms.a1m.vs_a0_median_pct,AGG.arms.a2.vs_a0_median_pct,AGG.arms.a3.vs_a0_median_pct);
vcard.append(el('div',{class:'card'},el('h3',{},'A0 anchor spread (n=5)'),el('div',{class:'big'},'±'+(band.std/band.median*100).toFixed(1)+'%'),el('div',{class:'note'},'σ/median across the 5 native anchors, total level')));
vcard.append(el('div',{class:'card'},el('h3',{},'largest middleware effect'),el('div',{class:'big'},'+'+mwMax+'%'),el('div',{class:'note'},'commit-phase swing alone dwarfs every arm signal')));
vbody.append(vcard);
vbody.append(el('p',{class:'note',html:'The commit phase alone ranges <b class=mono>'+fmt(Math.min(...order.flatMap(a=>commit[a]?[commit[a].min]:[])))+'</b> – <b class=mono>'+fmt(Math.max(...order.flatMap(a=>commit[a]?[commit[a].max]:[])))+'</b> billed input across runs — about an order of magnitude larger than any middleware effect being measured. This is why the protocol compares <b>medians</b> against the A0 band, not single runs.'}));

// ---- voids ----
const voids=D.runs.filter(r=>r.cls=='void');
const vCols=[['run','run',r=>`<span class=mono>${r.run}</span>`],['arm','arm',r=>`<span class=swatch style="background:${armColor(r.arm)}"></span>${D.arm_label[r.arm]}`],
 ['why','void reason',r=>`<span class=tag void>${r.why}</span>`],['partial','partial billed',r=>fmt(r.total_input)],
 ['n_phases','phases ran',r=>r.n_phases],['err','error',r=>`<span class=note style="font-size:11px">${r.errors.length?r.errors[0].phase+': '+(r.errors[0].error.slice(0,60)):'—'}</span>`]];
document.getElementById('voids-table').append(buildTable(voids.map(r=>({...r,partial:r.total_input,err:r.errors})),vCols,false));

// ---- context runs ----
const ctx=D.runs.filter(r=>['pilot','exploratory','cross'].includes(r.cls));
const cCols=[['run','label',r=>`<span class=mono>${r.run}</span>`],['arm','arm',r=>`<span class=swatch style="background:${armColor(r.arm)}"></span>${D.arm_label[r.arm]}`],
 ['cls','class',r=>`<span class=tag>${r.cls}</span>`],['input','billed input',r=>`<b class=mono>${fmt(r.total_input)}</b>`],
 ['turns','turns',r=>fmt(r.total_turns)],['stop','8/8',r=>r.all_stop?'✓':'<span class=warn>✗</span>'],['why','note',r=>`<span class=note style="font-size:12px">${r.why||''}</span>`]];
document.getElementById('context-table').append(buildTable(ctx.map(r=>({...r,input:r.total_input,cls:r.cls})),cCols,true,'input'));

// ---- sortable table builder ----
function buildTable(rows,cols,sortable,defSort){
  const t=el('table');
  const thead=el('thead');const htr=el('tr');
  cols.forEach(([key,label],i)=>{const th=el('th',{class:i==0?'':'num'},label);if(sortable){th.onclick=()=>sortBy(key,th);}htr.append(th);});
  thead.append(htr);t.append(thead);
  const tbody=el('tbody');t.append(tbody);
  let dir=1,cur=defSort||null;
  function render(){
    tbody.innerHTML='';
    let rs=rows.slice();
    if(cur){rs.sort((a,b)=>{let x=a[cur],y=b[cur];if(typeof x=='boolean'){x=x?1:0;y=y?1:0;}if(x==null)x=-Infinity;if(y==null)y=-Infinity;return (x>y?1:x<y?-1:0)*dir;});}
    rs.forEach(r=>{const tr=el('tr');cols.forEach(([key,label,fn],i)=>tr.append(el('td',{class:i==0?'':'num',html:fn(r)})));tbody.append(tr);});
  }
  window.sortBy=window.sortBy||function(){};
  function sortBy(key,th){if(cur==key)dir*=-1;else{cur=key;dir=key==defSort?-1:1;}render();}
  t._sort=sortBy;
  if(sortable&&defSort){dir=-1;}
  render();
  return t;
}
</script>
</body></html>
"""
out = os.path.join(HERE, "dashboard.html")
open(out, "w").write(HTML.replace("__PAYLOAD__", PAYLOAD))
print("wrote", out, f"({os.path.getsize(out)//1024} KB, {len(data['runs'])} runs embedded)")
