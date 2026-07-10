#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_guides_site.py -- render knowledge_hub/ (the MD sources) into
spindleloom_website/ (the browsable static site).

Browsers don't render .md, so the folder's guide documents get a generated,
styled HTML *reading twin* each (BEST-PRACTICES.md -> best-practices.html, ...),
with intra-folder .md links rewritten to their twins so navigation never drops
out of the browser. GOVERNANCE.md is skipped -- its reading view is the
governance handbook (build_governance_handbook.py); one reading view per doc.
archive/ is skipped -- non-load-bearing history stays history.

The site home, spindleloom_website/index.html, is a GENERATED end-to-end homepage:
the Woven Loop hero, the six-stage journey, a manifest of every site page (PAGES --
register new pages there), and fleet counts computed live from the folders.

Markdown conversion and the brand mark are reused from
build_governance_handbook.py; same derive-then-check contract as every other
generator here.

Usage:
    python hooks/build_guides_site.py            # (re)generate twins + index
    python hooks/build_guides_site.py --check     # exit 1 if anything is stale

Stdlib-only.
"""
import html as H
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_governance_handbook as gh  # md2html / inline / slug / MARK reuse
import validate_counts as vc            # live fleet counts for the homepage

ROOT = HERE.parent
HUB = ROOT / "knowledge_hub"          # sources (MD)
SITE = ROOT / "spindleloom_website"   # output (the browsable site)

# .md -> twin .html (GOVERNANCE handled by the handbook; archive/ excluded)
# root-level user docs also get reading twins (rendered from the repo root)
ROOT_SOURCES = ["INSTALL.md", "CHANGELOG.md", "CONTRIBUTING.md", "ONBOARDING.md"]

SOURCES = [
    "README.md",
    "BEST-PRACTICES.md",
    "AGENT-AUTHORING.md",
    "LOOPWRIGHT.md",
    "HARNESS-MATRIX.md",
    "FLEET-EVAL.md",
    "IMPROVEMENTS.md",
    "claude-prompt-library.md",
]

def twin_name(md_name):
    return md_name[:-3].lower() + ".html"

# how intra-folder .md hrefs rewrite inside rendered twins
LINK_MAP = {name: twin_name(name) for name in SOURCES}
LINK_MAP["GOVERNANCE.md"] = "governance-handbook.html"
for _r in ROOT_SOURCES:
    LINK_MAP[_r] = twin_name(_r)            # bare refs inside root docs
    LINK_MAP["../" + _r] = twin_name(_r)    # ../INSTALL.md refs inside hub docs

TWIN_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ -- Spindleloom Guides</title>
<style>
:root{
  --ground:#0E1524; --panel:#141E2E; --panel-2:#18263A;
  --ink:#DBE5F1; --ink-mid:#93A6BC; --ink-dim:#8497AE; --hair:#1E2E45; --hair-2:#2A3E5C;
  --gold:#CFA23A; --gold-hi:#E7BE58; --weft:#5C90BE;
  --shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34);
  --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root{
  --ground:#E9EAE5; --panel:#FFFFFF; --panel-2:#F3F3EF;
  --ink:#16202E; --ink-mid:#47586B; --ink-dim:#556575; --hair:#DEDFD8; --hair-2:#C9CBC1;
  --gold:#8A6816; --gold-hi:#7C5D12; --weft:#3C6C93;
  --shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07);
}}
:root[data-theme="light"]{--ground:#E9EAE5;--panel:#FFFFFF;--panel-2:#F3F3EF;--ink:#16202E;--ink-mid:#47586B;--ink-dim:#556575;--hair:#DEDFD8;--hair-2:#C9CBC1;--gold:#8A6816;--gold-hi:#7C5D12;--weft:#3C6C93;--shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07)}
:root[data-theme="dark"]{--ground:#0E1524;--panel:#141E2E;--panel-2:#18263A;--ink:#DBE5F1;--ink-mid:#93A6BC;--ink-dim:#8497AE;--hair:#1E2E45;--hair-2:#2A3E5C;--gold:#CFA23A;--gold-hi:#E7BE58;--weft:#5C90BE;--shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}a:hover{text-decoration:underline}
b,strong{color:var(--ink)}
::selection{background:color-mix(in srgb,var(--gold) 30%,transparent)}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:2px}
.bar{position:sticky;top:0;z-index:80;display:flex;align-items:center;gap:14px;padding:11px 26px;
  background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(9px);border-bottom:1px solid var(--hair)}
.bar .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--ink-mid);white-space:nowrap}
.bar .brand b{color:var(--gold)}
.bar nav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
.bar nav a{font-family:var(--mono);font-size:11px;color:var(--ink-mid);padding:6px 10px;border-radius:8px}
.bar nav a:hover{color:var(--gold);text-decoration:none}
.toggle{font-family:var(--mono);font-size:11px;color:var(--ink-mid);background:transparent;border:1px solid var(--hair-2);
  border-radius:20px;padding:6px 13px;cursor:pointer;white-space:nowrap}
.toggle:hover{border-color:var(--gold);color:var(--gold)}
.hero{border-bottom:1px solid var(--hair)}
.hero .in{max-width:1120px;margin:0 auto;padding:44px 30px 34px}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:var(--ink-mid)}
.hero h1{font-family:var(--serif);font-weight:600;font-size:clamp(30px,4.4vw,46px);line-height:1.05;letter-spacing:-.02em;margin:12px 0 0;text-wrap:balance}
.hero .note{font-family:var(--mono);font-size:11.5px;color:var(--ink-mid);margin-top:14px}
.layout{max-width:1120px;margin:0 auto;padding:34px 30px 80px;display:grid;grid-template-columns:250px minmax(0,1fr);gap:44px}
@media(max-width:960px){.layout{grid-template-columns:1fr}.spine{display:none}}
.spine{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 90px);overflow:auto;font-size:12.5px}
.spine .sp-part{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;margin:18px 0 6px;color:var(--gold)}
.spine ol{list-style:none}
.spine li a{display:block;color:var(--ink-mid);padding:3px 0 3px 12px;border-left:2px solid var(--hair)}
.spine li a:hover{color:var(--ink);text-decoration:none}
.spine li.on a{color:var(--gold);border-left-color:var(--gold)}
article h3{font-family:var(--serif);font-weight:600;font-size:23px;letter-spacing:-.01em;margin:40px 0 12px;scroll-margin-top:72px}
article h4{font-size:15.5px;margin:26px 0 8px;scroll-margin-top:72px}
article p{margin:0 0 13px;max-width:76ch;color:var(--ink-mid)}
article li{margin:0 0 7px;color:var(--ink-mid)}
article ul,article ol{margin:0 0 14px;padding-left:22px}
article blockquote{border-left:3px solid var(--gold);background:var(--panel);border-radius:0 10px 10px 0;
  padding:12px 18px;margin:0 0 16px}
article blockquote p{margin:0}
article hr{border:0;height:1px;background:var(--hair);margin:34px 0}
article code{font-family:var(--mono);font-size:.86em;background:var(--panel-2);border:1px solid var(--hair);border-radius:5px;padding:1px 6px;color:var(--gold-hi)}
article pre{font-family:var(--mono);font-size:12.5px;line-height:1.55;background:var(--panel);border:1px solid var(--hair);
  border-radius:12px;padding:16px 18px;overflow-x:auto;margin:0 0 16px;color:var(--ink-mid)}
.tw{overflow-x:auto;margin:0 0 18px;border:1px solid var(--hair);border-radius:12px;box-shadow:var(--shadow)}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--panel)}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mid);
  text-align:left;padding:10px 14px;border-bottom:1px solid var(--hair-2);background:var(--panel-2)}
td{padding:10px 14px;border-bottom:1px solid var(--hair);vertical-align:top;color:var(--ink-mid)}
tr:last-child td{border-bottom:0}
footer{border-top:1px solid var(--hair)}
footer .in{max-width:1120px;margin:0 auto;padding:22px 30px;font-size:12.5px;color:var(--ink-mid)}
</style>
</head>
<body>
<div class="bar">
  <span class="brand">__MARK__ Spindleloom &middot; <b>Guides</b></span>
  <nav aria-label="Site">
    <a href="index.html">Home</a>
    <a href="personas/index.html">Hub</a>
    <a href="project-overview.html">Overview</a>
    <a href="governance-handbook.html">Governance</a>
    <a href="readme.html">All guides</a>
  </nav>
  <button class="toggle" id="themeToggle" aria-label="Toggle light or dark theme">&#9681; theme</button>
</div>
<header class="hero"><div class="in">
  <div class="kicker">Spindleloom &middot; knowledge hub</div>
  <h1>__TITLE__</h1>
  <p class="note">Generated reading view. Source of truth: <a href="__SRC__"><code>__SRCLABEL__</code></a> --
  edit the MD, then run <code>python hooks/build_guides_site.py</code>.</p>
</div></header>
<div class="layout">
  <nav class="spine" aria-label="Contents"><div class="sp-part">On this page</div><ol>__SPINE__</ol></nav>
  <main><article>__BODY__</article></main>
</div>
<footer><div class="in">
  Part of the <a href="readme.html">Spindleloom website</a> &middot; front door: the
  <a href="personas/index.html">Persona Field Handbook</a>.
</div></footer>
<script>
const root=document.documentElement;
try{const _st=localStorage.getItem("sl-theme");if(_st)root.setAttribute("data-theme",_st);}catch(e){}
document.getElementById("themeToggle").addEventListener("click",()=>{
  const dark=matchMedia("(prefers-color-scheme:dark)").matches;
  const cur=root.getAttribute("data-theme")||(dark?"dark":"light");
  const next=cur==="dark"?"light":"dark";
  root.setAttribute("data-theme",next);
  try{localStorage.setItem("sl-theme",next);}catch(e){}
});
const items=[...document.querySelectorAll(".spine li")];
const map={};items.forEach(li=>{const a=li.querySelector("a");if(a)map[a.getAttribute("href").slice(1)]=li;});
const spy=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){
  items.forEach(l=>l.classList.remove("on"));const li=map[e.target.id];if(li)li.classList.add("on");}}),
  {rootMargin:"-20% 0px -70% 0px"});
document.querySelectorAll("article h3[id]").forEach(h=>spy.observe(h));
</script>
</body>
</html>
"""

# ---------------------------------------------------------------- the homepage
# index.html is the site's front door: the end-to-end story + a manifest of every
# page. PAGES is the single place a new site page gets registered; counts are
# computed from the folders at render time, so the numbers can never go stale
# (--check re-renders and goes red if the folder counts moved).

PAGES = [
    ("Understand", "what is this project?", [
        ("project-overview.html", "Project overview", "the deep dive",
         "Exec summary, the lifecycle, all 52 agents by phase, the PBI journey, traceability, the worked run."),
        ("for-everyone.html", "For everyone", "plain language",
         "The wheel, the eight stages, the three moves -- share this with non-technical folks."),
        ("spindleloom-agent-fleet.html", "Fleet map", "interactive",
         "Every agent and every delegation edge, filterable by phase and role."),
    ]),
    ("Operate", "what do I run?", [
        ("personas/index.html", "Persona Field Handbook", "the tabbed front door",
         "15 role playbooks + Start here, the 10-phase rail, and the filterable 54-prompt library."),
        ("get-started.html", "Get started", "guided",
         "One page: install into your tool, verify, scaffold, first run, daily driving."),
        ("install.html", "Install reference", "generated",
         "The long form: per-tool detail, MCP wiring, tracker setup, enterprise rollout."),
    ]),
    ("Govern", "the standards, readable", [
        ("governance-handbook.html", "Governance Handbook", "generated",
         "The layout standard, story craft, and the team + Azure DevOps fit -- one navigable page."),
        ("best-practices.html", "Best practices", "generated", "The documentation funnel, quality standard, gates and delivery patterns."),
        ("agent-authoring.html", "Agent authoring", "generated", "The contract-block schema and prompting conventions."),
        ("loopwright.html", "Loopwright", "generated", "The delivery-loop discipline and the loop taxonomy on every agent."),
        ("harness-matrix.html", "Harness matrix", "generated", "The 7-surface x 4-tool distribution spec -- four tools, six bundles."),
        ("fleet-eval.html", "Fleet eval", "generated", "The behavioral E2E regression protocol: golden brief + judge rubric."),
        ("improvements.html", "Improvement register", "generated", "The toolkit's own deferred backlog, tiered and cut-ready."),
        ("claude-prompt-library.html", "Claude prompt library", "generated", "Generic power-prompts, each mapped to the fleet specialist that does it better."),
        ("readme.html", "The guide map", "generated", "What lives where across the knowledge hub and this site."),
    ]),
    ("Project", "the repo itself", [
        ("changelog.html", "Changelog", "generated", "Every release, most recent first -- what shipped and why."),
        ("contributing.html", "Contributing", "generated", "How to add an agent/skill/command and keep the graph valid."),
        ("onboarding.html", "Onboarding", "generated", "The new-teammate orientation: layers, loops, first commands."),
    ]),
    ("Brand", "the Woven Loop", [
        ("brand/woven-loop-stages.html", "Woven Loop study", "brand", "The lemniscate mark, the stage system, and the logo scales."),
        ("brand/loop-widget.html", "Live run widget", "brand", "The loop driven by a real run ledger -- stages fill as a run advances."),
    ]),
]

JOURNEY = [
    ("PLAN", "make", "Discovery &middot; Requirements &middot; Design &middot; Planning",
     "Is it worth building, what must it do, and how -- MRD to sprint plan, every requirement traced, each phase accepted by a named role.", "project-overview.html"),
    ("BUILD", "make", "Build",
     "Recon-first implementation: reuse before rewrite, minimal diffs, maker/checker verified before anything is called done.", "personas/developer.html"),
    ("TEST", "make", "Test",
     "Test plans traced to requirements, automation in CI, exploratory passes, and an evidence-backed QA verdict.", "personas/qa.html"),
    ("SHIP", "run", "Review &middot; Release",
     "Code, security, performance and accessibility reviews; the go/no-go is computed as the AND over sign-off tokens.", "personas/sre-release.html"),
    ("OPERATE", "run", "Operate",
     "SLOs and symptom alerts; incidents end in blameless postmortems whose actions land back in the backlog.", "personas/sre-release.html"),
    ("LEARN", "run", "Process",
     "Retros, delivery metrics, the debt register, living docs -- the loop learns and re-enters PLAN.", "personas/delivery-lead.html"),
]

HOME_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Spindleloom -- the agent fleet for the whole SDLC</title>
<style>
:root{
  --ground:#0E1524; --panel:#141E2E; --panel-2:#18263A;
  --ink:#DBE5F1; --ink-mid:#93A6BC; --ink-dim:#8497AE; --hair:#1E2E45; --hair-2:#2A3E5C;
  --gold:#CFA23A; --gold-hi:#E7BE58; --weft:#5C90BE; --weft-dim:#3A5E80;
  --shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34);
  --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root{
  --ground:#E9EAE5; --panel:#FFFFFF; --panel-2:#F3F3EF;
  --ink:#16202E; --ink-mid:#47586B; --ink-dim:#556575; --hair:#DEDFD8; --hair-2:#C9CBC1;
  --gold:#8A6816; --gold-hi:#7C5D12; --weft:#3C6C93; --weft-dim:#A9B9C7;
  --shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07);
}}
:root[data-theme="light"]{--ground:#E9EAE5;--panel:#FFFFFF;--panel-2:#F3F3EF;--ink:#16202E;--ink-mid:#47586B;--ink-dim:#556575;--hair:#DEDFD8;--hair-2:#C9CBC1;--gold:#8A6816;--gold-hi:#7C5D12;--weft:#3C6C93;--weft-dim:#A9B9C7;--shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07)}
:root[data-theme="dark"]{--ground:#0E1524;--panel:#141E2E;--panel-2:#18263A;--ink:#DBE5F1;--ink-mid:#93A6BC;--ink-dim:#8497AE;--hair:#1E2E45;--hair-2:#2A3E5C;--gold:#CFA23A;--gold-hi:#E7BE58;--weft:#5C90BE;--weft-dim:#3A5E80;--shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}a:hover{text-decoration:underline}
b,strong{color:var(--ink)}
::selection{background:color-mix(in srgb,var(--gold) 30%,transparent)}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:2px}
.bar{position:sticky;top:0;z-index:80;display:flex;align-items:center;gap:14px;padding:11px 26px;
  background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(9px);border-bottom:1px solid var(--hair)}
.bar .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--ink-mid);white-space:nowrap}
.bar .brand b{color:var(--gold)}
.bar nav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
.bar nav a{font-family:var(--mono);font-size:11px;color:var(--ink-mid);padding:6px 10px;border-radius:8px}
.bar nav a:hover{color:var(--gold);text-decoration:none}
.toggle{font-family:var(--mono);font-size:11px;color:var(--ink-mid);background:transparent;border:1px solid var(--hair-2);
  border-radius:20px;padding:6px 13px;cursor:pointer;white-space:nowrap}
.toggle:hover{border-color:var(--gold);color:var(--gold)}
.hero{border-bottom:1px solid var(--hair)}
.hero .in{max-width:1180px;margin:0 auto;padding:56px 30px 44px;display:block}
@media(min-width:1024px){.hero .in{display:flex;align-items:center;gap:clamp(24px,4vw,64px)}.hero .htext{flex:1;min-width:0}}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:var(--ink-mid)}
.hero h1{font-family:var(--serif);font-weight:600;font-size:clamp(34px,4.8vw,58px);line-height:1.03;letter-spacing:-.02em;margin:14px 0 0;text-wrap:balance}
.hero h1 em{font-style:italic;color:var(--gold)}
.hero .dek{color:var(--ink-mid);max-width:58ch;margin:18px 0 0;font-size:17px}
.ctas{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}
.cta{font-family:var(--mono);font-size:12.5px;letter-spacing:.04em;border-radius:10px;padding:11px 20px;text-decoration:none}
.cta.primary{background:var(--gold);color:var(--ground);font-weight:700}
.cta.primary:hover{background:var(--gold-hi);text-decoration:none}
.cta.ghost{color:var(--ink);border:1px solid var(--hair-2)}
.cta.ghost:hover{border-color:var(--gold);color:var(--gold);text-decoration:none}
.loopwrap{display:flex;flex-direction:column;align-items:center;gap:12px;margin:34px auto 6px;width:min(480px,92vw)}
@media(min-width:1024px){.loopwrap{flex:0 0 auto;margin:0}}
.loopcanvas{display:block;width:100%;height:auto;max-width:480px;cursor:pointer}
.loopread{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;color:var(--ink-mid);display:flex;align-items:center;gap:8px;text-transform:uppercase}
.loopread b{color:var(--gold);font-weight:600}
.loopread .pip{width:8px;height:8px;border-radius:50%;background:var(--gold);box-shadow:0 0 8px var(--gold)}
@media (prefers-reduced-motion:reduce){.loopread .pip{box-shadow:none}}
.sec{max-width:1180px;margin:0 auto;padding:44px 30px 10px}
.sec .shead{font-family:var(--mono);font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:var(--gold);margin:0 0 6px}
.sec h2{font-family:var(--serif);font-weight:600;font-size:clamp(24px,3.2vw,34px);letter-spacing:-.015em;margin:0 0 8px}
.sec .slede{color:var(--ink-mid);max-width:70ch;margin:0 0 22px;font-size:14.5px}
.journey{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;padding-bottom:14px}
.jstage{background:var(--panel);border:1px solid var(--hair);border-radius:14px;padding:20px 22px;box-shadow:var(--shadow);display:flex;flex-direction:column}
.jstage .jn{display:flex;align-items:baseline;gap:10px}
.jstage .jn b{font-family:var(--mono);font-size:15px;letter-spacing:.14em}
.jstage.make .jn b{color:var(--weft)}
.jstage.run .jn b{color:var(--gold)}
.jstage .side{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-dim);border:1px solid var(--hair-2);border-radius:5px;padding:1px 7px}
.jstage .ph{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;color:var(--ink-dim);margin:8px 0 8px}
.jstage p{font-size:13.5px;color:var(--ink-mid);margin:0 0 12px;flex:1}
.jstage a{font-family:var(--mono);font-size:11px}
.gsec{font-family:var(--mono);font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin:26px 0 4px}
.gwhy{font-size:13px;color:var(--ink-dim);margin:0 0 12px}
.ggrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.gcard{display:block;background:var(--panel);border:1px solid var(--hair);border-radius:12px;padding:16px 18px;
  box-shadow:var(--shadow);color:inherit;text-decoration:none}
.gcard:hover{border-color:var(--gold);text-decoration:none}
.gcard h3{font-family:var(--serif);font-size:17.5px;font-weight:600;margin:0 0 4px;color:var(--ink)}
.gcard h3 .ext{font-family:var(--mono);font-size:9.5px;color:var(--ink-dim);letter-spacing:.08em;text-transform:uppercase}
.gcard p{font-size:12.5px;color:var(--ink-mid);margin:0}
.mach{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:14px;padding-bottom:8px}
.mcard{background:var(--panel);border:1px solid var(--hair);border-radius:14px;padding:20px 22px;box-shadow:var(--shadow);display:flex;flex-direction:column}
.mcard h3{font-family:var(--serif);font-size:19px;font-weight:600;margin:0 0 8px}
.mcard p{font-size:13.5px;color:var(--ink-mid);margin:0 0 12px;flex:1}
.mcard .inside{list-style:none;margin:0 0 14px;padding:0;border-top:1px solid var(--hair)}
.mcard .inside li{display:grid;grid-template-columns:150px minmax(0,1fr);gap:10px;padding:8px 0;border-bottom:1px solid var(--hair);font-size:12.5px}
.mcard .inside li b{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--gold);font-weight:700}
.mcard .inside li span{color:var(--ink-mid)}
@media(max-width:480px){.mcard .inside li{grid-template-columns:1fr}}
.mcard .verbs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.mcard .verbs code{font-family:var(--mono);font-size:10.5px;background:var(--panel-2);border:1px solid var(--hair);border-radius:6px;padding:2px 8px;color:var(--gold-hi)}
.mcard a{font-family:var(--mono);font-size:11px}
.harness{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;padding-bottom:8px}
.hcard{background:var(--panel);border:1px solid var(--hair);border-radius:12px;padding:16px 18px;box-shadow:var(--shadow)}
.hcard b{font-family:var(--serif);font-size:16.5px;font-weight:600;display:block;margin-bottom:4px}
.hcard .surf{font-family:var(--mono);font-size:10px;letter-spacing:.04em;color:var(--gold-hi);display:block;margin-bottom:6px}
.hcard p{font-size:12px;color:var(--ink-mid);margin:0}
.numbers{display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 30px}
.num{background:var(--panel);border:1px solid var(--hair);border-radius:12px;padding:16px 24px;box-shadow:var(--shadow);min-width:150px}
.num b{display:block;font-family:var(--serif);font-size:30px;font-weight:600;color:var(--gold);font-variant-numeric:tabular-nums}
.num span{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mid)}
footer{border-top:1px solid var(--hair);margin-top:36px}
footer .in{max-width:1180px;margin:0 auto;padding:22px 30px;font-size:12.5px;color:var(--ink-mid)}
</style>
</head>
<body>
<div class="bar">
  <span class="brand">__MARK__ <b>Spindleloom</b></span>
  <nav aria-label="Site">
    <a href="personas/index.html">Personas</a>
    <a href="project-overview.html">Overview</a>
    <a href="for-everyone.html">Story</a>
    <a href="spindleloom-agent-fleet.html">Fleet map</a>
    <a href="governance-handbook.html">Governance</a>
  </nav>
  <button class="toggle" id="themeToggle" aria-label="Toggle light or dark theme">&#9681; theme</button>
</div>
<header class="hero"><div class="in">
  <div class="htext">
    <div class="kicker">52 role-specialist agents &middot; one traceable chain</div>
    <h1>From a market problem to a <em>running product</em> -- and around the loop again.</h1>
    <p class="dek">Spindleloom is an AI agent fleet that carries software across the whole lifecycle --
    market &rarr; spec &rarr; design &rarr; build &rarr; test &rarr; ship &rarr; operate &rarr; learn --
    with every hand-off contracted, every requirement traced, and every gate a file a validator can check.</p>
    <div class="ctas">
      <a class="cta primary" href="get-started.html">&#9656; Get started</a>
      <a class="cta ghost" href="personas/index.html#/start">Your role&#39;s playbook</a>
      <a class="cta ghost" href="project-overview.html">The deep dive</a>
    </div>
  </div>
  <div class="loopwrap">
    <canvas class="loopcanvas" id="loop" width="520" height="520" role="button" tabindex="0"
      aria-label="Woven Loop - activate to open the Phases view"></canvas>
    <div class="loopread"><span class="pip"></span> working&nbsp;<b id="loopnow">PLAN</b></div>
  </div>
</div></header>

<section class="sec" aria-labelledby="j-h">
  <div class="shead">End to end</div>
  <h2 id="j-h">One loop, six stages</h2>
  <p class="slede">The left lobe makes, the right lobe runs; the hand-off in the middle is where evidence
  changes hands. Ten phases fold into six stages -- click any stage on the loop above to see who is active in it.</p>
  <div class="journey">__JOURNEY__</div>
</section>

<section class="sec" aria-labelledby="m-h">
  <div class="shead">Under the hood</div>
  <h2 id="m-h">The machinery</h2>
  <p class="slede">Four pillars make the loop trustworthy: agents only ever read the right context,
  every requirement is traceable end to end, every gate is a file a validator can check, and the
  whole fleet answers to a typed surface. All of it is stdlib Python -- nothing to install, nothing hidden.</p>
  <div class="mach">__MACHINERY__</div>
</section>

<section class="sec" aria-labelledby="t-h">
  <div class="shead">Target environments</div>
  <h2 id="t-h">Runs in your tools</h2>
  <p class="slede">Authored once as Markdown-with-contracts, generated into <b>__NBUNDLES__ native bundles</b>
  by <code>hooks/build_harness_artifacts.py</code> \u2014 same agents, same skills, each tool&#39;s own format.
  The full 7-surface support matrix: <a href="harness-matrix.html">harness-matrix.html</a>.</p>
  <div class="harness">__HARNESS__</div>
</section>

<section class="sec" aria-labelledby="x-h">
  <div class="shead">The site</div>
  <h2 id="x-h">Explore</h2>
  <p class="slede">Everything on this site, by what you came to do. The Markdown sources of truth live in
  <a href="../knowledge_hub/README.md"><code>knowledge_hub/</code></a>; pages marked <i>generated</i> are derived from them and drift-gated.</p>
  __GROUPS__
</section>

<section class="sec" aria-labelledby="n-h">
  <div class="shead">By the numbers</div>
  <h2 id="n-h">The fleet, counted from the folders</h2>
  <div class="numbers">__NUMBERS__</div>
</section>

<footer><div class="in">
  Generated by <code>hooks/build_guides_site.py</code> -- edit sources in <a href="../knowledge_hub/README.md"><code>knowledge_hub/</code></a>,
  never this page &middot; repo <a href="../README.md">README</a> &middot; install via <a href="install.html">the install guide</a>.
</div></footer>
<noscript><div style="max-width:760px;margin:0 auto;padding:10px 30px 40px"><p>JavaScript is off -- the loop stays still, everything else works. Jump to:
<a href="personas/index.html">Personas</a> &middot; <a href="project-overview.html">Overview</a> &middot; <a href="governance-handbook.html">Governance</a>.</p></div></noscript>
<script>
const root=document.documentElement;
try{const _st=localStorage.getItem("sl-theme");if(_st)root.setAttribute("data-theme",_st);}catch(e){}
document.getElementById("themeToggle").addEventListener("click",()=>{
  const dark=matchMedia("(prefers-color-scheme:dark)").matches;
  const cur=root.getAttribute("data-theme")||(dark?"dark":"light");
  const next=cur==="dark"?"light":"dark";
  root.setAttribute("data-theme",next);
  try{localStorage.setItem("sl-theme",next);}catch(e){}
  if(window.__loopPal)window.__loopPal();
});
(function(){
  const cv=document.getElementById("loop"); if(!cv||!cv.getContext) return;
  const reduce=matchMedia("(prefers-reduced-motion:reduce)").matches;
  const dpr=Math.min(window.devicePixelRatio||1,2.5),S=520;
  cv.width=S*dpr;cv.height=S*dpr;
  const c=cv.getContext("2d");c.setTransform(dpr,0,0,dpr,0,0);c.lineJoin="round";
  const pal=()=>{const g=getComputedStyle(root),v=n=>g.getPropertyValue(n).trim();
    return {amber:v("--gold"),amberLt:v("--gold-hi"),blue:v("--weft-dim"),blueLt:v("--weft"),
      ink:v("--ground"),on:v("--ink"),off:v("--ink-dim")};};
  let PAL=pal();
  const STAGES=[{d:60,l:"LEARN",s:"run"},{d:120,l:"PLAN",s:"make"},{d:180,l:"BUILD",s:"make"},
    {d:240,l:"TEST",s:"make"},{d:300,l:"SHIP",s:"run"},{d:360,l:"OPERATE",s:"run"}]
    .map(x=>({t:x.d*Math.PI/180,l:x.l,s:x.s}));
  const af=0.22,ys=1.34,cx=S/2,cy=S/2,w=S*0.048,n=600,q=n/4;
  const PTS=[];for(let i=0;i<=n;i++){const tt=i/n*2*Math.PI,s=Math.sin(tt),cc=Math.cos(tt),d=1+s*s;
    PTS.push([cx+S*af*cc/d,cy+(S*af*s*cc/d)*ys]);}
  const pt=tt=>{const s=Math.sin(tt),cc=Math.cos(tt),d=1+s*s;return [cx+S*af*cc/d,cy+(S*af*s*cc/d)*ys];};
  const seg=(i0,i1,col,ww)=>{c.lineCap="round";c.beginPath();
    for(let i=i0;i<=i1;i++){const pp=PTS[i];i===i0?c.moveTo(pp[0],pp[1]):c.lineTo(pp[0],pp[1]);}
    c.strokeStyle=col;c.lineWidth=ww;c.stroke();};
  const act=hT=>{let b=0,bd=1e9;for(let i=0;i<STAGES.length;i++){
    const d=((hT-STAGES[i].t)%(2*Math.PI)+2*Math.PI)%(2*Math.PI);if(d<bd){bd=d;b=i;}}return b;};
  function draw(hT){
    const P=PAL,ai=act(hT);
    c.clearRect(0,0,S,S);
    c.globalAlpha=.16;seg(0,n,P.off,w);c.globalAlpha=1;
    c.globalAlpha=.5;seg(0,q,P.amber,w);seg(3*q,n,P.amber,w);seg(q,3*q,P.blue,w);c.globalAlpha=1;
    const hi=Math.round(hT/(2*Math.PI)*n),L=72;
    for(let k=L;k>=0;k--){const idx=((hi-k)%n+n)%n,p0=PTS[idx],p1=PTS[(idx+1)%n];
      c.globalAlpha=(1-k/L)*(1-k/L);c.lineCap="round";c.beginPath();
      c.moveTo(p0[0],p0[1]);c.lineTo(p1[0],p1[1]);
      c.strokeStyle=(idx<=q||idx>=3*q)?P.amberLt:P.blueLt;c.lineWidth=w*1.15;c.stroke();}
    c.globalAlpha=1;
    const hp=PTS[hi%n],rg=c.createRadialGradient(hp[0],hp[1],0,hp[0],hp[1],w*3);
    rg.addColorStop(0,"rgba(255,247,228,.95)");rg.addColorStop(1,"rgba(255,247,228,0)");
    c.fillStyle=rg;c.beginPath();c.arc(hp[0],hp[1],w*3,0,7);c.fill();
    STAGES.forEach((st,i)=>{const pp=pt(st.t),isA=i===ai,col=st.s==="run"?P.amberLt:P.blueLt,rr=isA?w*1.5:w*0.9;
      if(isA){const gg=c.createRadialGradient(pp[0],pp[1],0,pp[0],pp[1],w*3.4);
        gg.addColorStop(0,st.s==="run"?"rgba(231,190,88,.55)":"rgba(127,176,230,.5)");
        gg.addColorStop(1,"rgba(0,0,0,0)");c.fillStyle=gg;c.beginPath();c.arc(pp[0],pp[1],w*3.4,0,7);c.fill();}
      c.beginPath();c.arc(pp[0],pp[1],rr+w*0.5,0,7);c.fillStyle=P.ink;c.fill();
      c.beginPath();c.arc(pp[0],pp[1],rr,0,7);c.fillStyle=col;c.fill();
      const dx=pp[0]-cx,dy=pp[1]-cy,m=Math.sqrt(dx*dx+dy*dy)||1,off=w*2.4;
      c.textBaseline="middle";c.textAlign=dx<-S*0.04?"right":dx>S*0.04?"left":"center";
      c.fillStyle=isA?P.on:P.off;c.font=(isA?"700 ":"500 ")+(S*0.03)+"px ui-monospace,Menlo,Consolas,monospace";
      c.fillText(st.l,pp[0]+dx/m*off,pp[1]+dy/m*off);});
    c.beginPath();c.arc(cx,cy,w*1.7,0,7);c.fillStyle=P.ink;c.fill();
    c.beginPath();c.arc(cx,cy,w,0,7);c.fillStyle=P.amber;c.fill();
    c.beginPath();c.arc(cx,cy,w*0.42,0,7);c.fillStyle=P.ink;c.fill();
    const el=document.getElementById("loopnow");
    if(el&&el.textContent!==STAGES[ai].l)el.textContent=STAGES[ai].l;
  }
  let head=0;
  const frame=()=>{draw(head/n*2*Math.PI);head=(head+1.0)%n;requestAnimationFrame(frame);};
  if(reduce)draw(1.6);else frame();
  window.__loopPal=()=>{PAL=pal();if(reduce)draw(1.6);};
  const go=()=>{location.href="personas/index.html#/phases";};
  cv.addEventListener("click",go);
  cv.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();go();}});
})();
</script>
</body>
</html>
"""


MACHINERY = [
    ("Context engineering",
     "An agent is only as good as what it reads -- and nothing here reads \"the whole repo\". "
     "Each step receives exactly what the contract graph routes to it, compressed and cited.",
     [("Context packs", "a per-agent manifest: its phase-bounded transitive upstream chain, digests before full documents"),
      ("Shared memory", "save/recall over MCP; the committed context log crosses machines on a plain git pull"),
      ("Handoff compression", "decisions, outputs, blockers and constraints in five bullets or fewer -- read in one call"),
      ("Stale-context handling", "an upstream edit after a downstream read is surfaced, never silently trusted")],
     ["sloom pack", "sloom context --import", "save_context / recall_context"],
     "governance-handbook.html#pi-14-how-to-find-anything-retrieval", "how anything is found"),
    ("The golden thread",
     "Every requirement carries an immutable ID from business goal to the test that proves it. "
     "Coverage is provable and the blast radius of any change is one query away.",
     [("Req-IDs", "&lt;DOC&gt;-&lt;AREA&gt;-&lt;NUM&gt; (FRD-AUTH-012) -- immutable once assigned, never renumbered"),
      ("The living RTM", "one traceability matrix per initiative threads goal &rarr; story &rarr; requirement &rarr; design &rarr; test"),
      ("Live queries", "trace_requirement, rtm_coverage and stale_artifacts answer from any MCP-connected tool"),
      ("The CI gate", "validate_reqs fails the build on an untraced requirement or a duplicate ID")],
     ["/spec-check", "sloom reqs", "trace_requirement()"],
     "governance-handbook.html#pi-5-naming-traceability", "naming &amp; traceability"),
    ("Gates as files",
     "Acceptance, sign-offs, verifications and flags are files in the repo -- a human teammate and an "
     "autonomous run hit the same gates, CI proves they ran, and __NTOOLS__ stdlib-only tools enforce them.",
     [("Phase acceptance", "a named role signs approvals/&lt;phase&gt;.md; a run cannot cross an unaccepted boundary"),
      ("The release AND", "six sign-off tokens (qa, security, perf, a11y, raid, dod); an unevidenced GO is refused"),
      ("Verification", "change-verifier must record a PASS per PBI -- \"looks right\" is not evidence"),
      ("The re-work queue", "a writer that hits a gap leaves FLAG(owner); flags re-open done steps instead of shipping")],
     ["sloom check", "sloom approve / signoff", "sloom run advance", "sloom flags"],
     "governance-handbook.html#pi-9-concurrency-ownership-multiple-teammates-one-repo", "concurrency &amp; ownership"),
    ("The typed surface",
     "__NCMDS__ slash commands inside the assistant, one CLI front door outside it -- the same fleet "
     "either way, and a whole run is resumable from a ledger on disk.",
     [("/spec-*", "authors the funnel: constitution, MRD&rarr;TSD, ADR/RFC, the traceability check"),
      ("/plan-* and /build-*", "cadence (estimate, sprint, retro) and the recon &rarr; implement &rarr; verify loop"),
      ("/ship-* and /ops-*", "release go/no-go over the token AND; status, RAID, incidents, metrics"),
      ("/run + sloom", "drives a resumable multi-agent run with a stop contract; sloom forwards to every tool")],
     ["/spec-new", "/plan-sprint", "/build-verify", "/ship-release", "/run"],
     "personas/index.html#/prompts", "all 54 prompts, filterable"),
]

HARNESSES = [
    ("Claude Code", ".claude/ plugin", "One command: /plugin install sloom@spindleloom \u2014 agents, skills, commands, hooks and MCP, wired."),
    ("Cursor", ".cursor/agents + commands", "Native subagents and commands, an always-on conventions rule, mcp.json included."),
    ("GitHub Copilot", ".github/ chatmodes + prompts", "Chat modes per agent, prompt files per command, copilot-instructions for the conventions."),
    ("Windsurf", ".windsurf/ rules + workflows", "Rules with trigger frontmatter (12k-aware) and manual workflows per command."),
    ("Any tool", "AGENTS.md router", "The lowest-common-denominator instruction file every assistant reads \u2014 one file, whole fleet."),
]


def render_home():
    counts = vc.real_counts()
    ntools = len(list((ROOT / "hooks").glob("build_*.py"))) + len(list((ROOT / "hooks").glob("validate_*.py")))
    nbundles = len([d for d in (ROOT / "targets").iterdir() if d.is_dir()]) if (ROOT / "targets").is_dir() else 6
    machinery = "".join(
        '<div class="mcard"><h3>%s</h3><p>%s</p>'
        '<ul class="inside">%s</ul>'
        '<div class="verbs">%s</div><a href="%s">%s &rarr;</a></div>'
        % (title, desc,
           "".join('<li><b>%s</b><span>%s</span></li>' % (k, v) for k, v in inside),
           "".join("<code>%s</code>" % v for v in verbs), href, label)
        for title, desc, inside, verbs, href, label in MACHINERY
    ).replace("__NTOOLS__", str(ntools)).replace("__NCMDS__", str(counts["commands"]))
    harness = "".join(
        '<div class="hcard"><b>%s</b><span class="surf">%s</span><p>%s</p></div>' % (name, surf, desc)
        for name, surf, desc in HARNESSES)
    journey = "".join(
        '<div class="jstage %s"><div class="jn"><b>%s</b><span class="side">%s side</span></div>'
        '<div class="ph">%s</div><p>%s</p><a href="%s">open &rarr;</a></div>'
        % (side, name, "make" if side == "make" else "run", phases, desc, href)
        for name, side, phases, desc, href in JOURNEY)
    groups = []
    for gname, gwhy, cards in PAGES:
        cs = "".join(
            '<a class="gcard" href="%s"><h3>%s <span class="ext">%s</span></h3><p>%s</p></a>'
            % (href, title, tag, desc) for href, title, tag, desc in cards)
        groups.append('<div class="gsec">%s</div><p class="gwhy">%s</p><div class="ggrid">%s</div>'
                      % (gname, gwhy, cs))
    numbers = "".join(
        '<div class="num"><b>%d</b><span>%s</span></div>' % (counts[k], label)
        for k, label in [("agents", "agents"), ("templates", "templates"),
                          ("skills", "skills"), ("commands", "slash commands")])
    return (HOME_SHELL.replace("__MARK__", gh.MARK)
                      .replace("__MACHINERY__", machinery)
                      .replace("__HARNESS__", harness)
                      .replace("__NBUNDLES__", str(nbundles))
                      .replace("__JOURNEY__", journey)
                      .replace("__GROUPS__", "".join(groups))
                      .replace("__NUMBERS__", numbers))


def rewrite_links(html_body):
    """Intra-folder .md hrefs -> their reading twins; everything else untouched."""
    def sub(m):
        href = m.group(1)
        if href.startswith("../spindleloom_website/"):
            return 'href="%s"' % href[len("../spindleloom_website/"):]   # site-internal in a twin
        if href.startswith("spindleloom_website/"):
            return 'href="%s"' % href[len("spindleloom_website/"):]      # root-doc link into the site
        base = href.split("#")[0]
        if base in LINK_MAP:
            frag = href[len(base):]
            return 'href="%s%s"' % (LINK_MAP[base], frag)
        if base.startswith("knowledge_hub/"):
            inner = base[len("knowledge_hub/"):]
            if inner in LINK_MAP:                                        # hub doc -> its reading view
                return 'href="%s%s"' % (LINK_MAP[inner], href[len(base):])
            return 'href="../%s"' % href                                 # e.g. archive/ history
        for d in ("hooks/", "agents/", "templates/", "skills/", "commands/", "targets/", "examples/", "assets/", "docs/"):
            if base.startswith(d):
                return 'href="../%s"' % href                             # repo dirs, one level up
        return m.group(0)
    return re.sub(r'href="([^"]+)"', sub, html_body)


def render_twin(md_name, src_dir=None, src_href=None, src_label=None):
    src_dir = src_dir or HUB
    src_href = src_href or ("../knowledge_hub/" + md_name)
    src_label = src_label or ("knowledge_hub/" + md_name)
    text = (src_dir / md_name).read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    title = md_name
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        text = "\n".join(lines[1:])
    toc = []
    body = gh.md2html(text, "g", toc)
    body = rewrite_links(body)
    spine = "\n".join('<li><a href="#%s">%s</a></li>' % (sid, H.escape(txt)) for sid, txt in toc)
    # title may contain markdown-ish em-dashes etc.; escape for <title>/<h1>
    safe_title = H.escape(title, quote=False)
    return (TWIN_SHELL.replace("__MARK__", gh.MARK)
                      .replace("__TITLE__", safe_title)
                      .replace("__SRC__", src_href)
                      .replace("__SRCLABEL__", src_label)
                      .replace("__SPINE__", spine)
                      .replace("__BODY__", body))


GETSTARTED_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Get started -- Spindleloom</title>
<style>
:root{
  --ground:#0E1524; --panel:#141E2E; --panel-2:#18263A;
  --ink:#DBE5F1; --ink-mid:#93A6BC; --ink-dim:#8497AE; --hair:#1E2E45; --hair-2:#2A3E5C;
  --gold:#CFA23A; --gold-hi:#E7BE58; --weft:#5C90BE;
  --shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34);
  --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root{
  --ground:#E9EAE5; --panel:#FFFFFF; --panel-2:#F3F3EF;
  --ink:#16202E; --ink-mid:#47586B; --ink-dim:#556575; --hair:#DEDFD8; --hair-2:#C9CBC1;
  --gold:#8A6816; --gold-hi:#7C5D12; --weft:#3C6C93;
  --shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07);
}}
:root[data-theme="light"]{--ground:#E9EAE5;--panel:#FFFFFF;--panel-2:#F3F3EF;--ink:#16202E;--ink-mid:#47586B;--ink-dim:#556575;--hair:#DEDFD8;--hair-2:#C9CBC1;--gold:#8A6816;--gold-hi:#7C5D12;--weft:#3C6C93;--shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07)}
:root[data-theme="dark"]{--ground:#0E1524;--panel:#141E2E;--panel-2:#18263A;--ink:#DBE5F1;--ink-mid:#93A6BC;--ink-dim:#8497AE;--hair:#1E2E45;--hair-2:#2A3E5C;--gold:#CFA23A;--gold-hi:#E7BE58;--weft:#5C90BE;--shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}a:hover{text-decoration:underline}
b,strong{color:var(--ink)}
::selection{background:color-mix(in srgb,var(--gold) 30%,transparent)}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:2px}
.bar{position:sticky;top:0;z-index:80;display:flex;align-items:center;gap:14px;padding:11px 26px;
  background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(9px);border-bottom:1px solid var(--hair)}
.bar .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--ink-mid);white-space:nowrap}
.bar .brand b{color:var(--gold)}
.bar nav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
.bar nav a{font-family:var(--mono);font-size:11px;color:var(--ink-mid);padding:6px 10px;border-radius:8px}
.bar nav a:hover{color:var(--gold);text-decoration:none}
.toggle{font-family:var(--mono);font-size:11px;color:var(--ink-mid);background:transparent;border:1px solid var(--hair-2);
  border-radius:20px;padding:6px 13px;cursor:pointer;white-space:nowrap}
.toggle:hover{border-color:var(--gold);color:var(--gold)}
.hero{border-bottom:1px solid var(--hair)}
.hero .in{max-width:980px;margin:0 auto;padding:48px 30px 36px}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:var(--ink-mid)}
.hero h1{font-family:var(--serif);font-weight:600;font-size:clamp(32px,4.4vw,50px);line-height:1.04;letter-spacing:-.02em;margin:12px 0 0;text-wrap:balance}
.hero h1 em{font-style:italic;color:var(--gold)}
.hero .dek{color:var(--ink-mid);max-width:62ch;margin:16px 0 0;font-size:16px}
.wrap{max-width:980px;margin:0 auto;padding:10px 30px 70px}
.step{margin:38px 0 0}
.step .sh{display:flex;align-items:baseline;gap:14px;margin-bottom:10px}
.step .n{font-family:var(--mono);font-size:12px;font-weight:700;color:var(--ground);background:var(--gold);border-radius:7px;padding:2px 10px}
.step h2{font-family:var(--serif);font-weight:600;font-size:clamp(21px,2.8vw,28px);letter-spacing:-.01em}
.step p{color:var(--ink-mid);font-size:14px;max-width:74ch;margin:0 0 12px}
.cmd{position:relative;background:var(--panel);border:1px solid var(--hair);border-radius:12px;margin:0 0 12px;box-shadow:var(--shadow)}
.cmd pre{font-family:var(--mono);font-size:12.5px;line-height:1.6;padding:14px 90px 14px 18px;overflow-x:auto;color:var(--ink);white-space:pre}
.cmd .lbl{position:absolute;top:10px;right:76px;font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-dim)}
.copy{position:absolute;top:8px;right:10px;font-family:var(--mono);font-size:10.5px;color:var(--ink-mid);
  background:var(--panel-2);border:1px solid var(--hair-2);border-radius:7px;padding:4px 10px;cursor:pointer}
.copy:hover{border-color:var(--gold);color:var(--gold)}
.copy.done{color:var(--gold);border-color:var(--gold)}
.tools{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin:0 0 6px}
.tool{background:var(--panel);border:1px solid var(--hair);border-radius:12px;padding:16px 18px;box-shadow:var(--shadow)}
.tool b{font-family:var(--serif);font-size:16px;display:block;margin-bottom:6px}
.tool p{font-size:12.5px;margin:0 0 8px}
.tool code{font-family:var(--mono);font-size:11px;background:var(--panel-2);border:1px solid var(--hair);border-radius:5px;padding:1px 6px;color:var(--gold-hi)}
.next{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:8px}
.next a{display:block;background:var(--panel);border:1px solid var(--hair);border-radius:12px;padding:14px 18px;color:inherit;box-shadow:var(--shadow)}
.next a:hover{border-color:var(--gold);text-decoration:none}
.next b{font-family:var(--serif);font-size:15.5px;color:var(--ink);display:block;margin-bottom:3px}
.next span{font-size:12px;color:var(--ink-mid)}
footer{border-top:1px solid var(--hair)}
footer .in{max-width:980px;margin:0 auto;padding:20px 30px;font-size:12.5px;color:var(--ink-mid)}
</style>
</head>
<body>
<div class="bar">
  <span class="brand">__MARK__ Spindleloom &middot; <b>Get started</b></span>
  <nav aria-label="Site">
    <a href="index.html">Home</a>
    <a href="install.html">Full install reference</a>
    <a href="personas/index.html">Personas</a>
    <a href="project-overview.html">Overview</a>
  </nav>
  <button class="toggle" id="themeToggle" aria-label="Toggle light or dark theme">&#9681; theme</button>
</div>
<header class="hero"><div class="in">
  <div class="kicker">Install &rarr; first run &rarr; daily driving</div>
  <h1>Get started in <em>ten minutes</em></h1>
  <p class="dek">One page from a fresh clone to your first agent hand-off. The long tail
  (enterprise rollout, MCP details, troubleshooting) lives in the
  <a href="install.html">full install reference</a>.</p>
</div></header>
<div class="wrap">

<div class="step"><div class="sh"><span class="n">1</span><h2>Get the source</h2></div>
<p>Clone next to (or inside) the project you want the fleet to work on. Prerequisites: Git + Python 3.10+.</p>
<div class="cmd"><span class="lbl">any OS</span><button class="copy">Copy</button>
<pre>git clone https://github.com/&lt;your-org&gt;/spindleloom.git</pre></div>
</div>

<div class="step"><div class="sh"><span class="n">2</span><h2>Install into your tool</h2></div>
<p>Pick one. Claude Code gets the one-command plugin; the others get native bundles emitted by the harness generator.</p>
<div class="tools">
<div class="tool"><b>Claude Code (recommended)</b><p>The plugin bundles agents + commands + skills + hooks + MCP:</p>
<div class="cmd"><button class="copy">Copy</button><pre>/plugin marketplace add ./spindleloom
/plugin install sloom@spindleloom</pre></div></div>
<div class="tool"><b>Cursor / Copilot / Windsurf</b><p>The installer copies that tool&#39;s native bundle into your repo:</p>
<div class="cmd"><span class="lbl">Windows</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\install.py --target cursor --repo .</pre></div>
<p style="margin:0"><code>--target copilot</code> or <code>--target windsurf</code> for the others; <code>--dry-run</code> previews.</p></div>
<div class="tool"><b>Any other assistant</b><p>One file every tool reads:</p>
<div class="cmd"><button class="copy">Copy</button><pre>Copy-Item spindleloom\\targets\\agents-md\\AGENTS.md .</pre></div></div>
</div></div>

<div class="step"><div class="sh"><span class="n">3</span><h2>Verify it is healthy</h2></div>
<p>The validator prints the live fleet counts and exits 0 when the contract graph is sound.</p>
<div class="cmd"><span class="lbl">Windows</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\validate_graph.py</pre></div>
<div class="cmd"><span class="lbl">macOS / Linux</span><button class="copy">Copy</button><pre>python3 spindleloom/hooks/validate_graph.py</pre></div>
</div>

<div class="step"><div class="sh"><span class="n">4</span><h2>Scaffold your project</h2></div>
<p>Lays down the governed tree (<code>docs/</code> + <code>.spindleloom/</code>) any tool can work in.
In Claude Code, <code>/spec-new &lt;feature&gt;</code> does the same and starts the spec funnel.</p>
<div class="cmd"><span class="lbl">greenfield</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\scaffold.py . --profile mid</pre></div>
<div class="cmd"><span class="lbl">existing repo</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\scaffold.py . migrate</pre></div>
</div>

<div class="step"><div class="sh"><span class="n">5</span><h2>First run &mdash; describe the work</h2></div>
<p>You do not memorize 52 agents. Say what you want; the right specialist triggers and hands off down the chain.</p>
<div class="cmd"><span class="lbl">in your assistant</span><button class="copy">Copy</button><pre>Write a BRD for prescription refill reminders for a pharmacy chain.</pre></div>
<p>Watch it hand off (BRD &rarr; PRD &rarr; FRD &rarr; ...), then prove nothing was dropped:</p>
<div class="cmd"><span class="lbl">Claude Code</span><button class="copy">Copy</button><pre>/spec-check</pre></div>
</div>

<div class="step"><div class="sh"><span class="n">6</span><h2>Daily driving</h2></div>
<p>The typed surface, end to end: <code>/spec-*</code> authors the funnel &middot; <code>/plan-*</code> runs the cadence
&middot; <code>/build-*</code> and <code>/test-*</code> verify &middot; <code>/ship-*</code> and <code>/ops-*</code> release and operate
&middot; <code>/run</code> drives a whole resumable run. Outside the assistant, one CLI front door:</p>
<div class="cmd"><span class="lbl">the gate battery</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\sloom.py check</pre></div>
<div class="cmd"><span class="lbl">the concurrency layer</span><button class="copy">Copy</button><pre>py -3 spindleloom\\hooks\\sloom.py run status &lt;run-id&gt;
py -3 spindleloom\\hooks\\sloom.py approve requirements --feature &lt;slug&gt; --role po --by "&lt;name&gt;"
py -3 spindleloom\\hooks\\sloom.py signoff qa --verdict GO --by "&lt;name&gt;" --evidence &lt;path&gt;</pre></div>
<p><b>Where next:</b></p>
<div class="next">
<a href="personas/index.html#/start"><b>Start here (by role)</b><span>Pick your persona: the agents you drive, copy-ready prompts, the gates you own.</span></a>
<a href="personas/index.html#/prompts"><b>The prompt library</b><span>All 54 prompts, filterable by role, phase and MCP.</span></a>
<a href="install.html"><b>Full install reference</b><span>Per-tool detail, MCP wiring, tracker setup, the enterprise rollout checklist.</span></a>
</div></div>

</div>
<footer><div class="in">
  Generated by <code>hooks/build_guides_site.py</code> &middot; source of truth for the long form:
  <a href="../INSTALL.md"><code>INSTALL.md</code></a> &middot; back to the <a href="index.html">homepage</a>.
</div></footer>
<script>
const root=document.documentElement;
try{const _st=localStorage.getItem("sl-theme");if(_st)root.setAttribute("data-theme",_st);}catch(e){}
document.getElementById("themeToggle").addEventListener("click",()=>{
  const dark=matchMedia("(prefers-color-scheme:dark)").matches;
  const cur=root.getAttribute("data-theme")||(dark?"dark":"light");
  const next=cur==="dark"?"light":"dark";
  root.setAttribute("data-theme",next);
  try{localStorage.setItem("sl-theme",next);}catch(e){}
});
document.querySelectorAll(".cmd").forEach(card=>{
  const btn=card.querySelector(".copy"),pre=card.querySelector("pre");if(!btn)return;
  btn.addEventListener("click",async()=>{const txt=pre.textContent;
    try{await navigator.clipboard.writeText(txt);}catch(e){
      const r=document.createRange();r.selectNodeContents(pre);const s=getSelection();
      s.removeAllRanges();s.addRange(r);try{document.execCommand("copy");}catch(_){}}
    btn.textContent="Copied";btn.classList.add("done");
    setTimeout(()=>{btn.textContent="Copy";btn.classList.remove("done");},1400);});
});
</script>
</body>
</html>
"""


def render_get_started():
    return GETSTARTED_SHELL.replace("__MARK__", gh.MARK)


def outputs():
    out = {twin_name(n): render_twin(n) for n in SOURCES}
    for n in ROOT_SOURCES:
        out[twin_name(n)] = render_twin(n, src_dir=ROOT, src_href="../" + n, src_label=n)
    out["get-started.html"] = render_get_started()
    out["index.html"] = render_home()
    return out


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for name, page in outputs().items():
        dest = SITE / name
        if check:
            if not dest.exists():
                stale.append(name + " (missing)")
            elif dest.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").strip() != page.strip():
                stale.append(name)
        else:
            crlf = dest.exists() and b"\r\n" in dest.read_bytes()
            dest.write_bytes((page.replace("\n", "\r\n") if crlf else page).encode("utf-8"))
    if check:
        if stale:
            print("build_guides_site: STALE -- %s; run `python hooks/build_guides_site.py`" % ", ".join(stale))
            return 1
        print("build_guides_site: in sync (%d twins + index)" % (len(SOURCES) + len(ROOT_SOURCES)))
        return 0
    print("build_guides_site: wrote %d reading twins + index.html into spindleloom_website/" % (len(SOURCES) + len(ROOT_SOURCES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
