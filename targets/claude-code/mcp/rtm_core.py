#!/usr/bin/env python3
"""
rtm_core.py — the requirement/traceability graph, parsed from a spec folder.

The single stdlib-only core shared by:
  - validate_reqs.py  (CLI / CI gate / Claude Code hook)
  - mcp_server.py     (live MCP server: trace, coverage, list, decisions)

Dependency-free (Python 3 stdlib only). Read-only. It parses the conventions in
project_guides/BEST-PRACTICES.md: Req-IDs of the form <DOC>-<AREA>-<NUM>, the RTM.md table, and
ADR references — and exposes them as queryable structures.
"""
import json
import re
from pathlib import Path

# <DOC>-<AREA>-<NUM> — DOC/AREA are UPPER alnum, NUM is digits.
REQ_ID = re.compile(r"\b([A-Z][A-Z0-9]*)-([A-Z][A-Z0-9]*)-(\d{1,4})\b")
# ADR references are 2-part (ADR-0001) so REQ_ID does not catch them.
ADR_REF = re.compile(r"(?i)\bADR-(\d{1,4})\b")


def adr_file_num(relpath):
    """The ADR number a file *defines*, across the three naming forms — or None.
    Matches `adr-0001-*.md` / `08-adr-0001-*.md` (anywhere in the name), and the
    canonical `adr/0001-*.md` (a numbered file inside an `adr/` folder)."""
    p = str(relpath).replace("\\", "/")
    name = p.split("/")[-1]
    m = re.search(r"(?i)adr-(\d{1,4})", name)
    if m:
        return int(m.group(1))
    if "adr" in p.split("/")[:-1]:
        m2 = re.match(r"\s*(\d{1,4})", name)
        if m2:
            return int(m2.group(1))
    return None
# requirement-defining docs whose IDs must be covered by the RTM
# Coverage is enforced at every requirement altitude, not just FRD/SRS —
# a dropped BRD goal or PRD story must be as visible as a dropped FRD req.
COVERED_DOCS = {"FRD", "SR", "SRS", "BR", "PRD", "URS"}
RTM_NAME = "RTM.md"

# Tool machinery + content-location config (the .spindleloom / docs split).
# `.spindleloom/` is the ONE tool-state home (config, catalog, baselines, verifications,
# signoffs, context DB). `.shipwright/` is the pre-0.3 name — still readable so existing
# repos keep working; `scaffold.py migrate` renames it. New writes go where the project
# already keeps its state (legacy until migrated, canonical otherwise).
TOOL_DIR = ".spindleloom"
LEGACY_TOOL_DIR = ".shipwright"
SHIPWRIGHT_DIR = TOOL_DIR  # deprecated alias — importers should move to TOOL_DIR
CONFIG_NAME = "config.json"
DEFAULT_DOCS_ROOT = "docs"


def tool_dir(project_root):
    """The project's tool-state dir: `.spindleloom/` canonically; the legacy
    `.shipwright/` if that's what the repo has (until `scaffold.py migrate` renames it)."""
    project_root = Path(project_root)
    canonical = project_root / TOOL_DIR
    legacy = project_root / LEGACY_TOOL_DIR
    if not canonical.exists() and legacy.exists():
        return legacy
    return canonical


def load_config(project_root):
    """Read <tool-dir>/config.json if present (else {}) — canonical first, then legacy."""
    for d in (TOOL_DIR, LEGACY_TOOL_DIR):
        p = Path(project_root) / d / CONFIG_NAME
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
            except (ValueError, OSError):
                return {}
    return {}


def resolve_docs_root(project_root):
    """The folder that holds the spec artifacts, resolved from a project root.
    Order: .spindleloom/config.json `docs_root` -> ./docs -> the project root itself
    (flat layout, backward-compatible). Location is config, never hardcoded."""
    project_root = Path(project_root)
    dr = load_config(project_root).get("docs_root")
    if dr:
        return project_root / dr
    if (project_root / DEFAULT_DOCS_ROOT).is_dir():
        return project_root / DEFAULT_DOCS_ROOT
    return project_root


# The edition of project_guides/STANDARD.md this code implements (recorded in a project's config).
STANDARD_VERSION = "1.0"

# Layout knobs — defaults reproduce the canonical Standard tree; each is overridable
# in .spindleloom/config.json (the sanctioned exception). See project_guides/STANDARD.md §8.
LAYOUT_DEFAULTS = {
    "product_dir": "product",
    "specs_dir": "specs",
    "adr_dir": "adr",
    "rfc_dir": "rfc",
    "sprints_dir": "sprints",
    "baselines_dir": "baselines",
    "rtm_file": RTM_NAME,
}


def layout(project_root):
    """Resolve a project's layout: the Standard's defaults overlaid with any sanctioned
    deviations in .spindleloom/config.json, plus `profile` and `standard_version`. An
    absent config yields the canonical Standard layout (every knob defaulted)."""
    cfg = load_config(project_root)
    out = dict(LAYOUT_DEFAULTS)
    for k in out:
        if cfg.get(k):
            out[k] = cfg[k]
    out["docs_root"] = cfg.get("docs_root", DEFAULT_DOCS_ROOT)
    out["profile"] = cfg.get("profile") or cfg.get("tier") or "mid"
    out["standard_version"] = cfg.get("standard_version", STANDARD_VERSION)
    return out


def _read(f):
    try:
        return Path(f).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def markdown_files(root):
    """All .md under root, recursively — excluding any dotdir (.spindleloom, .git, …)
    so machinery is never mistaken for content. Flat folders behave as before."""
    root = Path(root)
    return sorted(
        p for p in root.rglob("*.md")
        if not any(part.startswith(".") for part in p.relative_to(root).parts)
    )


def _relname(f, root):
    if root is None:
        return Path(f).name
    try:
        return Path(f).relative_to(root).as_posix()
    except ValueError:
        return Path(f).name


def collect_ids(files, root=None):
    """{req_id: [files it appears in]} across the given markdown files. File keys are
    paths relative to `root` (so nested feature folders are unambiguous); falls back
    to the bare name when root is None or unrelated."""
    seen = {}
    for f in files:
        name = _relname(f, root)
        for m in REQ_ID.finditer(_read(f)):
            seen.setdefault(m.group(0), set()).add(name)
    return {k: sorted(v) for k, v in seen.items()}


def definition_files(id_files, rtm_name=RTM_NAME):
    """IDs are 'defined' where they appear outside the RTM (in a spec doc)."""
    return {rid: [f for f in files if f != rtm_name] for rid, files in id_files.items()}


def rtm_id_set(root):
    rtm = Path(root) / RTM_NAME
    return {m.group(0) for m in REQ_ID.finditer(_read(rtm))} if rtm.exists() else set()


# ---------------------------------------------------------------- audit (shared with the validator)

def audit(root):
    """Structured traceability audit. Same logic the CLI validator formats and
    the MCP `rtm_coverage` tool returns. Problem messages are kept byte-identical
    to the validator's historical output so it can format them directly."""
    root = Path(root)
    files = markdown_files(root)
    has_rtm = (root / RTM_NAME).exists()
    rtm_ids = rtm_id_set(root)
    all_ids = collect_ids(files, root)
    defined_in = definition_files(all_ids)

    problems = []

    def add(code, rid, message):
        problems.append({"code": code, "id": rid, "message": message})

    if has_rtm:
        # RTM coverage for requirement-defining docs
        for rid, fs in defined_in.items():
            if rid.split("-", 1)[0] in COVERED_DOCS and fs and rid not in rtm_ids:
                add("UNCOVERED", rid, f"UNCOVERED  {rid} (in {', '.join(fs)}) is not traced in {RTM_NAME}")
        # broken refs: cited in RTM but defined nowhere
        for rid in sorted(rtm_ids):
            if rid.split("-", 1)[0] in COVERED_DOCS and not defined_in.get(rid):
                add("BROKEN-REF", rid, f"BROKEN-REF {rid} appears in {RTM_NAME} but is defined in no spec doc")
        # PBI orphans (only when a backlog is present)
        if any("backlog" in f.name.lower() for f in files):
            for rid, fs in defined_in.items():
                if rid.split("-", 1)[0] == "PBI" and fs and rid not in rtm_ids:
                    add("PBI-ORPHAN", rid, f"PBI-ORPHAN {rid} (in {', '.join(fs)}) is not traced in {RTM_NAME}")
    else:
        add("NO-RTM", None, f"NO-RTM     {RTM_NAME} not found in {root} — traceability cannot be proven")

    # ADR reference integrity + collision detection (Standard: one global ADR sequence, one home)
    adr_def_files = {}
    for f in files:
        n = adr_file_num(_relname(f, root))
        if n is not None:
            adr_def_files.setdefault(n, []).append(_relname(f, root))
    adr_defined = set(adr_def_files)
    # DUP-ADR: one ADR number defined by more than one file
    for num in sorted(adr_def_files):
        if len(adr_def_files[num]) > 1:
            add("DUP-ADR", f"ADR-{num:04d}",
                f"DUP-ADR    ADR-{num:04d} defined by {len(adr_def_files[num])} files: "
                f"{', '.join(sorted(adr_def_files[num]))}")
    # MULTI-ADR-DIR: ADR-defining files spread across more than one directory
    adr_dirs = sorted({(d.rsplit('/', 1)[0] if '/' in d else '.')
                       for fs in adr_def_files.values() for d in fs})
    if len(adr_dirs) > 1:
        add("MULTI-ADR-DIR", None,
            f"MULTI-ADR-DIR ADR files live in {len(adr_dirs)} directories "
            f"({', '.join(adr_dirs)}); the Standard uses one ADR home")
    adr_refs = {}
    for f in files:
        for m in ADR_REF.finditer(_read(f)):
            adr_refs.setdefault(int(m.group(1)), set()).add(f.name)
    for num in sorted(adr_refs):
        if num not in adr_defined:
            fs = ", ".join(sorted(adr_refs[num]))
            add("BROKEN-ADR", f"ADR-{num:04d}",
                f"BROKEN-ADR ADR-{num:04d} cited in {fs} but no adr-*.md defines it")

    # ADVISORY: test coverage (only when a test plan is present)
    advisories = []
    test_cov_line = None
    test_plans = [f for f in files if "test-plan" in f.name.lower() or "test_plan" in f.name.lower()]
    if test_plans:
        tp_text = "\n".join(_read(f) for f in test_plans)
        req_ids = sorted({rid for rid, fs in defined_in.items()
                          if rid.split("-", 1)[0] in COVERED_DOCS and fs})
        covered = [r for r in req_ids if r in tp_text]
        uncovered = [r for r in req_ids if r not in covered]
        test_cov_line = (f"test coverage: {len(covered)}/{len(req_ids)} FRD/SR reqs referenced by a test plan "
                         f"({', '.join(f.name for f in test_plans)})")
        advisories = [f"TEST-GAP   {r} has no test case referencing it" for r in uncovered]

    return {
        "root": str(root),
        "has_rtm": has_rtm,
        "ok": not problems,
        "problems": problems,
        "advisories": advisories,
        "test_coverage_line": test_cov_line,
        "counts": {"req_ids": len(all_ids), "files": len(files)},
    }


# ---------------------------------------------------------------- RTM table queries (for the server)

def parse_tables(text):
    """Parse GitHub-flavored markdown tables -> [{'header': [...], 'rows': [[...]]}]."""
    blocks, cur = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cur.append(s)
        elif cur:
            blocks.append(cur); cur = []
    if cur:
        blocks.append(cur)

    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    out = []
    for block in blocks:
        if len(block) < 2:
            continue
        header = cells(block[0])
        sep = block[1].replace("|", "").replace(":", "").strip()
        rows_start = 2 if (sep and set(sep) <= {"-", " "}) else 1
        out.append({"header": header, "rows": [cells(r) for r in block[rows_start:]]})
    return out


def parse_rtm(root):
    """The RTM as structured data: the traceability matrix + the decisions table."""
    rtm = Path(root) / RTM_NAME
    if not rtm.exists():
        return {"exists": False, "columns": [], "rows": [], "decisions": []}
    matrix, decisions = None, []
    for t in parse_tables(_read(rtm)):
        h0 = (t["header"][0] if t["header"] else "").strip().lower()
        if h0 == "id" and len(t["header"]) >= 2:
            decisions = [dict(zip(t["header"], r)) for r in t["rows"]]
        elif matrix is None and len(t["header"]) >= 3:
            matrix = t
    cols = matrix["header"] if matrix else []
    rows = [dict(zip(cols, r)) for r in matrix["rows"]] if matrix else []
    return {"exists": True, "columns": cols, "rows": rows, "decisions": decisions}


def trace(root, req_id):
    """Full chain + blast radius for one Req-ID: where it's defined and the RTM
    row(s) that carry it across every altitude (business → story → … → test)."""
    req_id = req_id.strip()
    ids = collect_ids(markdown_files(root), root)
    rtm = parse_rtm(root)
    matched = [row for row in rtm["rows"] if any(req_id in (v or "") for v in row.values())]
    return {
        "id": req_id,
        "exists": req_id in ids,
        "defined_in": [f for f in ids.get(req_id, []) if f != RTM_NAME],
        "traced": bool(matched),
        "rtm_rows": matched,
    }


def list_requirements(root, doc=None):
    """All Req-IDs (optionally filtered by DOC, e.g. 'FRD'), with where each is defined."""
    out = []
    for rid, files in sorted(collect_ids(markdown_files(root), root).items()):
        d = rid.split("-", 1)[0]
        if doc and d.upper() != doc.upper():
            continue
        out.append({"id": rid, "doc": d, "defined_in": [f for f in files if f != RTM_NAME]})
    return out


def find_decision(root, adr):
    """Look up an ADR by number/id: its decisions-table row, defining file, and citations."""
    m = re.search(r"(\d{1,4})", str(adr))
    if not m:
        return {"error": f"no ADR number found in {adr!r}"}
    num = int(m.group(1))
    files = markdown_files(root)
    cited = sorted({f.name for f in files
                    if any(int(x.group(1)) == num for x in ADR_REF.finditer(_read(f)))})
    defined = any(adr_file_num(_relname(f, root)) == num for f in files)
    drow = None
    for d in parse_rtm(root)["decisions"]:
        idcell = next(iter(d.values()), "")
        dm = re.search(r"(\d{1,4})", idcell)
        if dm and int(dm.group(1)) == num:
            drow = d
            break
    return {"id": f"ADR-{num:04d}", "defined": defined, "cited_in": cited, "decision_row": drow}


# ---------------------------------------------------------------- artifact registry (the catalog)

# filename token -> artifact kind, matched specific-first (multi-word before prefixes).
KIND_TOKENS = [
    ("constitution", "constitution"), ("tech-debt", "tech-debt-register"),
    ("tech-radar", "tech-radar"), ("threat-model", "threat-model"),
    ("test-plan", "test-plan"), ("status-report", "status-report"), ("status", "status-report"),
    ("backlog", "backlog"), ("postmortem", "postmortem"), ("raid", "raid-log"),
    ("estimation", "estimation"), ("sprint", "sprint-plan"), ("retro", "retrospective"),
    ("adr", "adr"), ("rfc", "rfc"),
    ("mrd", "mrd"), ("brd", "brd"), ("prd", "prd"), ("frd", "frd"),
    ("urs", "urs"), ("srs", "srs"), ("sdd", "sdd"), ("tsd", "tsd"), ("rtm", "rtm"),
]
_SKIP_STEMS = {"readme", "index", "artifacts"}


def detect_kind(relpath):
    """Infer artifact kind from a file's path: an exact parent-folder match
    (docs/adr/0001.md -> adr) or a token in the filename stem (01-mrd.md -> mrd)."""
    p = str(relpath).lower().replace("\\", "/")
    segs = p.split("/")
    stem = segs[-1].rsplit(".", 1)[0]
    parents = segs[:-1]
    for tok, kind in KIND_TOKENS:
        if tok in parents or tok in stem:
            return kind
    return None


def artifact_id(kind, stem):
    if kind in ("adr", "rfc"):
        # the number after the kind token (adr-0001), or a leading number when the
        # kind came from the folder (adr/0001-*.md) — never a file-order prefix (08-)
        m = re.search(rf"(?i){kind}[-_ ]?(\d{{1,4}})", stem) or re.match(r"\s*(\d{1,4})", stem)
        if m:
            return f"{kind.upper()}-{int(m.group(1)):04d}"
    return stem if kind == "other" else kind.upper()


def _scan_kv(text):
    """Pull key->value pairs from a doc header in the three conventions agents emit:
    a Field/Value markdown table, bold `**Key:** value` lines, and YAML frontmatter."""
    head = text[:2000]
    kv = {}
    for m in re.finditer(r"(?m)^\|\s*([A-Za-z][^|]*?)\s*\|\s*([^|]+?)\s*\|\s*$", head):
        kv.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    for m in re.finditer(r"\*\*\s*([A-Za-z][^*:]*?)\s*:?\s*\*\*\s*:?\s*([^\n|*]+)", head):
        kv.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    fm = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if fm:
        for m in re.finditer(r"(?im)^\s*([A-Za-z][\w \-]*?)\s*:\s*(.+?)\s*$", fm.group(1)):
            kv.setdefault(m.group(1).strip().lower(), m.group(2).strip().strip('"').strip("'"))
    return kv


def parse_metadata(text):
    kv = _scan_kv(text)

    def pick(*keys):
        for k in keys:
            if kv.get(k):
                return kv[k]
        return None

    tm = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    return {
        "title": tm.group(1).strip() if tm else None,
        "owner": pick("owner", "author", "deciders", "participants"),
        "status": pick("status"),
        "version": pick("version", "target release", "release"),
        "updated": pick("last updated", "updated", "date"),
    }


def artifacts(root):
    """Catalog every artifact in the spec folder: id, kind, title, path, owner, status,
    version, last-updated, and the Req-IDs it defines. The 'how to get them' index."""
    files = markdown_files(root)
    by_file = {}
    for rid, fs in collect_ids(files, root).items():
        for f in fs:
            by_file.setdefault(f, []).append(rid)
    out = []
    for f in files:
        if f.stem.lower() in _SKIP_STEMS:
            continue
        rel = _relname(f, root)
        kind = detect_kind(rel) or "other"
        meta = parse_metadata(_read(f))
        defines = sorted(by_file.get(rel, []))
        out.append({
            "id": artifact_id(kind, f.stem),
            "kind": kind,
            "title": meta["title"] or f.stem,
            "path": rel,
            "owner": meta["owner"],
            "status": meta["status"],
            "version": meta["version"],
            "updated": meta["updated"],
            "defines_ids": defines,
            "id_count": len(defines),
        })
    return out


def find_artifact(root, query):
    """Find artifacts by id ('PRD', 'ADR-0001'), kind ('adr'), or title/path substring."""
    q = query.strip().lower()
    arts = artifacts(root)
    exact = [a for a in arts if a["id"].lower() == q or a["kind"].lower() == q]
    return exact or [a for a in arts
                     if q in a["id"].lower() or q in a["title"].lower() or q in a["path"].lower()]


# ---------------------------------------------------------------- extended queries (Tier-1 MCP additions)

# Upstream -> downstream order of the funnel doc kinds, for staleness comparison.
FUNNEL_ORDER = ["constitution", "mrd", "brd", "prd", "frd", "urs", "srs", "sdd", "tsd"]


def _iso_date(s):
    """Pull an ISO yyyy-mm-dd date out of a metadata value (sortable as a string), or None."""
    if not s:
        return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    return m.group(0) if m else None


def funnel_status(root, req_id=None):
    """How far each RTM row propagated down the funnel: which altitude columns are
    filled vs blank, the deepest filled altitude, and the first gap. Filtered to the
    row(s) carrying `req_id` when given. The RTM columns ARE the altitudes."""
    rtm = parse_rtm(root)
    cols, rows = rtm["columns"], rtm["rows"]
    if req_id:
        req_id = req_id.strip()
        rows = [r for r in rows if any(req_id in (v or "") for v in r.values())]

    def is_filled(v):
        v = (v or "").strip()
        return bool(v) and v not in ("—", "-", "_", "n/a", "N/A", "TBD", "TODO")

    altitudes = []
    for r in rows:
        filled = [c for c in cols if is_filled(r.get(c))]
        blank = [c for c in cols if c not in filled]
        first_gap, seen = None, False
        for c in cols:
            if c in filled:
                seen = True
            elif seen:
                first_gap = c
                break
        altitudes.append({
            "row": r,
            "filled": filled,
            "blank": blank,
            "deepest_altitude": filled[-1] if filled else None,
            "first_gap": first_gap,
            "complete": not blank,
        })
    return {"exists": rtm["exists"], "columns": cols,
            "filtered_by": req_id or None, "altitudes": altitudes}


def stale_artifacts(root):
    """Heuristic change-control check: funnel docs whose `updated` date is older than an
    upstream doc they derive from (e.g. the PRD changed but the FRD didn't follow).
    Compares by funnel kind order; artifacts without a parseable date are reported
    separately under 'undated' rather than judged."""
    order = {k: i for i, k in enumerate(FUNNEL_ORDER)}
    funnel = [a for a in artifacts(root) if a["kind"] in order]
    dated = [(a, _iso_date(a["updated"])) for a in funnel]
    stale, undated = [], []
    for a, d in dated:
        if d is None:
            undated.append({"id": a["id"], "kind": a["kind"], "path": a["path"]})
            continue
        newer = [u for u, ud in dated if ud and order[u["kind"]] < order[a["kind"]] and ud > d]
        if newer:
            stale.append({
                "id": a["id"], "kind": a["kind"], "path": a["path"], "updated": a["updated"],
                "stale_against": [{"id": u["id"], "kind": u["kind"], "updated": u["updated"]} for u in newer],
            })
    return {"checked": len(funnel), "ok": not stale, "stale": stale, "undated": undated}


def next_req_id(root, doc, area):
    """Suggest the next free Req-ID for a DOC+AREA (e.g. doc='PRD', area='AUTH' ->
    'PRD-AUTH-004'), so a newly authored requirement doesn't collide. Pad width follows
    the existing ids (min 3)."""
    doc, area = doc.strip().upper(), area.strip().upper()
    nums = []
    for rid in collect_ids(markdown_files(root), root):
        parts = rid.split("-")
        if len(parts) == 3 and parts[0] == doc and parts[1] == area and parts[2].isdigit():
            nums.append(int(parts[2]))
    width = max([len(str(n)) for n in nums] + [3])
    nxt = (max(nums) + 1) if nums else 1
    return {
        "doc": doc, "area": area,
        "next_id": f"{doc}-{area}-{nxt:0{width}d}",
        "existing": sorted(f"{doc}-{area}-{n:0{width}d}" for n in nums),
        "count": len(nums),
    }


def search_specs(root, query, max_results=50):
    """Full-text search across the spec docs (case-insensitive substring): returns
    path + line number + the trimmed matching line. Retrieval without dumping files."""
    q = (query or "").strip()
    if not q:
        return {"query": q, "count": 0, "matches": [], "truncated": False}
    ql = q.lower()
    matches = []
    for f in markdown_files(root):
        rel = _relname(f, root)
        for i, line in enumerate(_read(f).splitlines(), 1):
            if ql in line.lower():
                matches.append({"path": rel, "line": i, "text": line.strip()[:300]})
                if len(matches) >= max_results:
                    return {"query": q, "count": len(matches), "matches": matches, "truncated": True}
    return {"query": q, "count": len(matches), "matches": matches, "truncated": False}


def decisions(root):
    """The RTM decisions table (the ADR/RFC ledger linking decisions to where they live)."""
    return parse_rtm(root)["decisions"]


def conformance(project_root):
    """Standard-conformance for a project ROOT (not the docs_root): the declared
    profile/version vs the toolkit's, plus duplicate artifact IDs across the catalog
    (e.g. two RTMs, or two ADR files claiming one id). Complements audit(), which checks
    the RTM/Req-ID graph; together they answer 'does this repo match the Standard?'
    (project_guides/STANDARD.md §10)."""
    project_root = Path(project_root)
    lay = layout(project_root)
    docs = resolve_docs_root(project_root)
    problems, advisories = [], []

    declared = load_config(project_root).get("standard_version")
    if not declared:
        advisories.append("no standard_version in .spindleloom/config.json — "
                          "run scaffold/migrate to pin the Standard edition")
    elif str(declared) != STANDARD_VERSION:
        advisories.append(f"project declares Standard v{declared}; toolkit ships "
                          f"v{STANDARD_VERSION} — reconcile via migrate")

    by_id = {}
    for a in artifacts(docs):
        by_id.setdefault(a["id"], []).append(a["path"])
    for aid, paths in sorted(by_id.items()):
        if len(paths) > 1:
            problems.append(f"DUP-ARTIFACT-ID {aid} cataloged from {len(paths)} "
                            f"files: {', '.join(sorted(paths))}")

    return {
        "root": str(project_root),
        "profile": lay["profile"],
        "standard_version": declared,
        "ok": not problems,
        "problems": problems,
        "advisories": advisories,
    }
