#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_fleet_page.py -- generate the DATA section of
spindleloom_website/spindleloom-agent-fleet.html from the agent contracts.

Everything derivable is derived: the node list (id / phase / description from each
agent's frontmatter), the delegation edges (from the downstream lists), and the
skills map. Three thin layers are curated HERE (single place, completeness-checked):

  EDGE_TYPE_OVERRIDES  the p/s/f taxonomy where it differs from the default
                       (default: backward-in-phase = feedback 'f', else primary 'p')
                       -- a stale override (edge no longer in the contracts) FAILS.
  INDEX_SOURCES        the wiki-curator 'indexes' overlay (t:'i'; exempt from check 12).
  LABELS / LANE_ORDER  presentation: node line-breaks and within-lane ordering
                       (new agents fall back to a break-at-middle-hyphen rule,
                       appended at their lane's end).

The rendering shell (CSS + layout + interaction JS) stays hand-authored; this tool
owns only the region between the GEN-DATA markers. validate_graph checks 12/12b/13
independently verify the result -- generator writes, validator proves.

Usage:
    python hooks/build_fleet_page.py            # regenerate the data region
    python hooks/build_fleet_page.py --check     # exit 1 if stale (CI/pre-commit)

Stdlib-only.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate_graph import frontmatter, inline_list  # noqa: E402  (shared parsers)

ROOT = HERE.parent
AGENTS_DIR = ROOT / "agents"
PAGE = ROOT / "spindleloom_website" / "spindleloom-agent-fleet.html"

GEN_START = "// >>> GENERATED DATA -- build_fleet_page.py (edit contracts, not this block) >>>"
GEN_END = "// <<< GENERATED DATA <<<"

PHASE_ORDER = ['discovery', 'requirements', 'design', 'planning', 'build', 'test', 'review', 'release', 'operate', 'process']
PHASE_META = [
    ("discovery", "DISCOVERY", "01", "#3B7DC4"), ("requirements", "REQUIREMENTS", "02", "#3A9E6A"),
    ("design", "DESIGN", "03", "#6B50B0"), ("planning", "PLANNING", "04", "#B08030"),
    ("build", "BUILD", "05", "#3A6BA0"), ("test", "TEST", "06", "#984040"),
    ("review", "REVIEW", "07", "#307A6A"), ("release", "RELEASE", "08", "#906040"),
    ("operate", "OPERATE", "09", "#7A5030"), ("process", "PROCESS", "10", "#4040A0"),
]

EDGE_TYPE_OVERRIDES = {
    ('accessibility-auditor', 'release-manager'): 's',
    ('adr-writer', 'tech-radar-curator'): 's',
    ('ai-eval', 'pipeline-engineer'): 's',
    ('api-designer', 'test-automation-engineer'): 's',
    ('architect', 'backend-developer'): 's',
    ('architect', 'frontend-developer'): 's',
    ('architect', 'raid-keeper'): 's',
    ('backend-developer', 'change-verifier'): 's',
    ('backend-developer', 'performance-engineer'): 's',
    ('backlog-manager', 'sprint-planner'): 's',
    ('backlog-manager', 'status-reporter'): 's',
    ('backlog-manager', 'test-author'): 's',
    ('brd-writer', 'urs-writer'): 's',
    ('change-verifier', 'debugger'): 'f',
    ('change-verifier', 'pr-author'): 'p',
    ('code-reviewer', 'release-manager'): 's',
    ('code-reviewer', 'tech-debt-keeper'): 's',
    ('coding-standards-writer', 'backend-developer'): 's',
    ('coding-standards-writer', 'frontend-developer'): 's',
    ('coding-standards-writer', 'pipeline-engineer'): 's',
    ('debugger', 'test-author'): 'f',
    ('dev-onboarding', 'backend-developer'): 's',
    ('dev-onboarding', 'flaky-test-detective'): 's',
    ('dev-onboarding', 'frontend-developer'): 's',
    ('doc-strategy-advisor', 'prd-writer'): 's',
    ('doc-strategy-advisor', 'solution-recon'): 's',
    ('doc-strategy-advisor', 'urs-writer'): 's',
    ('doc-strategy-advisor', 'wiki-curator'): 's',
    ('flaky-test-detective', 'test-automation-engineer'): 'f',
    ('frd-writer', 'architect'): 's',
    ('frd-writer', 'backlog-manager'): 's',
    ('frd-writer', 'feature-docs-writer'): 's',
    ('frd-writer', 'product-analytics'): 's',
    ('frd-writer', 'sdd-writer'): 's',
    ('frd-writer', 'solution-recon'): 's',
    ('frd-writer', 'ux-ui-designer'): 's',
    ('frontend-developer', 'change-verifier'): 's',
    ('frontend-developer', 'performance-engineer'): 's',
    ('incident-responder', 'raid-keeper'): 's',
    ('incident-responder', 'retrospective-facilitator'): 'f',
    ('incident-responder', 'tech-debt-keeper'): 's',
    ('performance-engineer', 'release-manager'): 's',
    ('performance-engineer', 'sre'): 's',
    ('pipeline-engineer', 'flaky-test-detective'): 's',
    ('pipeline-engineer', 'sre'): 's',
    ('pipeline-engineer', 'status-reporter'): 's',
    ('prd-writer', 'ai-eval'): 's',
    ('prd-writer', 'backlog-manager'): 's',
    ('prd-writer', 'product-analytics'): 's',
    ('prd-writer', 'solution-recon'): 's',
    ('product-analytics', 'backlog-manager'): 's',
    ('product-analytics', 'status-reporter'): 's',
    ('qa-tester', 'debugger'): 's',
    ('qa-tester', 'release-manager'): 's',
    ('release-manager', 'incident-responder'): 's',
    ('release-manager', 'wiki-curator'): 's',
    ('retrospective-facilitator', 'tech-debt-keeper'): 's',
    ('rfc-facilitator', 'sdd-writer'): 's',
    ('sdd-writer', 'adr-writer'): 's',
    ('sdd-writer', 'api-designer'): 's',
    ('sdd-writer', 'architect'): 'f',
    ('sdd-writer', 'data-modeler'): 's',
    ('sdd-writer', 'rfc-facilitator'): 's',
    ('sdd-writer', 'sre'): 's',
    ('security-reviewer', 'pipeline-engineer'): 's',
    ('solution-recon', 'adr-writer'): 's',
    ('solution-recon', 'architect'): 's',
    ('solution-recon', 'backend-developer'): 's',
    ('solution-recon', 'backlog-manager'): 's',
    ('solution-recon', 'estimation-facilitator'): 's',
    ('solution-recon', 'frd-writer'): 's',
    ('solution-recon', 'frontend-developer'): 's',
    ('solution-recon', 'raid-keeper'): 's',
    ('solution-recon', 'srs-writer'): 's',
    ('sprint-planner', 'raid-keeper'): 's',
    ('sprint-planner', 'retrospective-facilitator'): 's',
    ('sre', 'release-manager'): 's',
    ('srs-writer', 'backlog-manager'): 's',
    ('srs-writer', 'performance-engineer'): 's',
    ('srs-writer', 'rfc-facilitator'): 's',
    ('srs-writer', 'security-reviewer'): 's',
    ('srs-writer', 'sre'): 's',
    ('srs-writer', 'test-plan-writer'): 's',
    ('test-author', 'change-verifier'): 's',
    ('tsd-writer', 'pipeline-engineer'): 's',
    ('urs-writer', 'frd-writer'): 's',
    ('urs-writer', 'prd-writer'): 's',
    ('ux-ui-designer', 'accessibility-auditor'): 's',
}

INDEX_SOURCES = ['adr-writer', 'api-designer', 'backlog-manager', 'brd-writer', 'coding-standards-writer', 'data-modeler', 'dev-onboarding', 'frd-writer', 'incident-responder', 'mrd-writer', 'pipeline-engineer', 'prd-writer', 'qa-tester', 'raid-keeper', 'sdd-writer', 'sre', 'status-reporter', 'test-plan-writer', 'tsd-writer', 'urs-writer', 'ux-ui-designer']

LABELS = {
    'accessibility-auditor': 'accessibility\\nauditor',
    'adr-writer': 'adr-writer',
    'ai-eval': 'ai-eval',
    'ai-orchestrator': 'ai-orchestrator',
    'api-designer': 'api-designer',
    'architect': 'architect',
    'backend-developer': 'backend-developer',
    'backlog-manager': 'backlog-manager',
    'brd-writer': 'brd-writer',
    'bug-triager': 'bug-triager',
    'change-verifier': 'change-verifier',
    'code-reviewer': 'code-reviewer',
    'coding-standards-writer': 'coding-standards-writer',
    'data-modeler': 'data-modeler',
    'debugger': 'debugger',
    'dev-onboarding': 'dev-onboarding',
    'doc-strategy-advisor': 'doc-strategy\\nadvisor',
    'estimation-facilitator': 'estimation\\nfacilitator',
    'feature-docs-writer': 'feature-docs\\nwriter',
    'flaky-test-detective': 'flaky-test\\ndetective',
    'frd-writer': 'frd-writer',
    'frontend-developer': 'frontend-developer',
    'incident-responder': 'incident\\nresponder',
    'mrd-writer': 'mrd-writer',
    'performance-engineer': 'performance\\nengineer',
    'pipeline-engineer': 'pipeline-engineer',
    'pr-author': 'pr-author',
    'prd-writer': 'prd-writer',
    'product-analytics': 'product-analytics',
    'qa-tester': 'qa-tester',
    'raid-keeper': 'raid-keeper',
    'release-manager': 'release-manager',
    'retrospective-facilitator': 'retrospective\\nfacilitator',
    'rfc-facilitator': 'rfc-facilitator',
    'run-orchestrator': 'run-orchestrator',
    'sdd-writer': 'sdd-writer',
    'security-reviewer': 'security-reviewer',
    'solution-recon': 'solution-recon',
    'spec-steward': 'spec-steward',
    'sprint-planner': 'sprint-planner',
    'sre': 'sre',
    'srs-writer': 'srs-writer',
    'status-reporter': 'status-reporter',
    'tech-debt-keeper': 'tech-debt\\nkeeper',
    'tech-radar-curator': 'tech-radar-curator',
    'test-author': 'test-author',
    'test-automation-engineer': 'test-auto\\nengineer',
    'test-plan-writer': 'test-plan-writer',
    'tsd-writer': 'tsd-writer',
    'urs-writer': 'urs-writer',
    'ux-ui-designer': 'ux-ui-designer',
    'wiki-curator': 'wiki-curator',
}

LANE_ORDER = ['doc-strategy-advisor', 'mrd-writer', 'brd-writer', 'prd-writer', 'frd-writer', 'srs-writer', 'urs-writer', 'solution-recon', 'architect', 'rfc-facilitator', 'adr-writer', 'sdd-writer', 'api-designer', 'data-modeler', 'ux-ui-designer', 'tsd-writer', 'backlog-manager', 'estimation-facilitator', 'sprint-planner', 'dev-onboarding', 'coding-standards-writer', 'ai-orchestrator', 'pr-author', 'backend-developer', 'frontend-developer', 'test-plan-writer', 'test-author', 'qa-tester', 'test-automation-engineer', 'accessibility-auditor', 'ai-eval', 'bug-triager', 'flaky-test-detective', 'debugger', 'change-verifier', 'code-reviewer', 'security-reviewer', 'performance-engineer', 'raid-keeper', 'status-reporter', 'pipeline-engineer', 'release-manager', 'sre', 'incident-responder', 'feature-docs-writer', 'product-analytics', 'retrospective-facilitator', 'spec-steward', 'tech-debt-keeper', 'tech-radar-curator', 'wiki-curator', 'run-orchestrator']


def default_label(aid):
    if len(aid) <= 14:
        return aid
    hy = [i for i, c in enumerate(aid) if c == "-"]
    if not hy:
        return aid
    mid = min(hy, key=lambda i: abs(i - len(aid) / 2))
    return aid[:mid] + "\\n" + aid[mid + 1:]


def read_contracts():
    agents = {}
    for p in sorted(AGENTS_DIR.glob("*.md")):
        if p.name in ("INDEX.md", "HELP.md"):
            continue
        fm = frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        phase = (re.search(r"(?m)^phase:\s*(\S+)", fm) or [None, ""])[1].strip().strip('"')
        desc = (re.search(r"(?m)^description:\s*(.+)$", fm) or [None, ""])[1].strip().strip('"')
        agents[p.stem] = {
            "phase": phase,
            "desc": desc,
            "downstream": inline_list(fm, "downstream"),
            "skills": inline_list(fm, "skills"),
        }
    return agents


def js_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_data():
    agents = read_contracts()
    problems = []
    oidx = {p: i for i, p in enumerate(PHASE_ORDER)}

    # completeness: curated layers may not go stale
    real_edges = {(a, d) for a, meta in agents.items() for d in meta["downstream"]}
    for k in EDGE_TYPE_OVERRIDES:
        if k not in real_edges:
            problems.append("stale EDGE_TYPE_OVERRIDES entry (edge gone from contracts): %s -> %s" % k)
    for s in INDEX_SOURCES:
        if s not in agents:
            problems.append("stale INDEX_SOURCES entry (no such agent): %s" % s)
    for a, meta in agents.items():
        if meta["phase"] not in oidx:
            problems.append("agent %s has unknown phase %r" % (a, meta["phase"]))
        if "{" in meta["desc"] or "}" in meta["desc"]:
            problems.append("agent %s description contains braces (breaks the page parser)" % a)
    if problems:
        raise SystemExit("build_fleet_page: " + "; ".join(problems))

    # node order: curated lane order first, new agents appended per lane
    known = [a for a in LANE_ORDER if a in agents]
    new = sorted(a for a in agents if a not in LANE_ORDER)
    ordered = known + new

    out = [GEN_START, ""]
    out.append("const PHASES = [")
    for pid, label, n, color in PHASE_META:
        out.append("  {id:'%s',    label:'%s',    n:'%s', color:'%s'}," % (pid, label, n, color))
    out.append("];")
    out.append("")
    out.append("const AGENTS = [")
    cur = None
    for a in ordered:
        meta = agents[a]
        if meta["phase"] != cur:
            cur = meta["phase"]
            out.append("  // %s %s" % (dict((p, n) for p, _, n, _ in PHASE_META)[cur], cur.upper()))
        label = LABELS.get(a, default_label(a))
        out.append("  {id:'%s', label:'%s', phase:'%s',\n   desc:%s}," % (a, label, meta["phase"], js_str(meta["desc"])))
    out.append("];")
    out.append("")
    out.append("const EDGES = [")
    for a in ordered:
        for d in agents[a]["downstream"]:
            tt = EDGE_TYPE_OVERRIDES.get((a, d)) or ("f" if oidx[agents[d]["phase"]] < oidx[agents[a]["phase"]] else "p")
            out.append("  {from:'%s', to:'%s', t:'%s'}," % (a, d, tt))
    out.append("  // wiki-curator index overlay (t:'i' -- exempt from check 12, curated above)")
    for s in sorted(set(INDEX_SOURCES)):
        out.append("  {from:'%s', to:'wiki-curator', t:'i'}," % s)
    out.append("];")
    out.append("")
    out.append("const AGENT_SKILLS = {")
    for a in sorted(agents):
        out.append("  '%s':[%s]," % (a, ",".join("'%s'" % s for s in agents[a]["skills"])))
    out.append("};")
    out.append("// reverse index: skill -> agents that arm it (derived, never drifts)")
    out.append("const SKILL_AGENTS = {};")
    out.append("Object.entries(AGENT_SKILLS).forEach(([a, ss]) => ss.forEach(s => { (SKILL_AGENTS[s] = SKILL_AGENTS[s] || []).push(a); }));")
    out.append("const SKILLS = Object.keys(SKILL_AGENTS).sort();")
    out.append("")
    out.append(GEN_END)
    return "\n".join(out)


def splice(page_text, data):
    if GEN_START in page_text and GEN_END in page_text:
        a = page_text.index(GEN_START)
        b = page_text.index(GEN_END) + len(GEN_END)
        return page_text[:a] + data + page_text[b:]
    # first run: replace the original hand-authored data span
    m1 = re.search(r"// ─── PHASES.*?\n", page_text)
    m2 = re.search(r"const SKILLS = Object\.keys\(SKILL_AGENTS\)\.sort\(\);\n", page_text)
    if not (m1 and m2):
        raise SystemExit("build_fleet_page: cannot locate the data region to take ownership of")
    return page_text[:m1.start()] + data + "\n" + page_text[m2.end():]


def main():
    check = "--check" in sys.argv[1:]
    raw = PAGE.read_bytes()
    crlf = b"\r\n" in raw
    current = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    fresh = splice(current, render_data())
    if check:
        if current.strip() != fresh.strip():
            print("build_fleet_page: STALE -- fleet page data out of sync with the contracts; run `python hooks/build_fleet_page.py`")
            return 1
        print("build_fleet_page: in sync")
        return 0
    PAGE.write_bytes((fresh.replace("\n", "\r\n") if crlf else fresh).encode("utf-8"))
    print("build_fleet_page: wrote the generated data region (%d agents)" % len(read_contracts()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
