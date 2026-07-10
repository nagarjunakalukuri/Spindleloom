#!/usr/bin/env python3
"""
test_standard.py — stdlib-only tests for the Spindleloom Standard tooling: config-driven
scaffold, collision detection, conformance, and the brownfield converter (scaffold.py
migrate). No external deps (does not need the MCP SDK).

    py hooks/test_standard.py        (or: uv run python hooks/test_standard.py)

Exit 0 = all pass, 1 = a failure.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402
import scaffold  # noqa: E402

_fails = []


def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        _fails.append(msg)


def _w(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_scaffold_default():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        scaffold.scaffold(root)  # default profile = mid
        check((root / "docs/product/prd.md").exists(), "scaffold(mid): docs/product/prd.md")
        check((root / "docs/specs/feature-1/frd.md").exists(), "scaffold(mid): docs/specs/feature-1/frd.md")
        check((root / "docs/sprints").is_dir(), "scaffold(mid): cyclic docs/sprints/ created")
        cfg = (root / ".spindleloom/config.json").read_text(encoding="utf-8")
        check('"standard_version"' in cfg and '"profile"' in cfg,
              "scaffold writes standard_version + profile to config")
        gi = root / ".spindleloom/.gitignore"
        check(gi.exists() and "context.db" in gi.read_text(encoding="utf-8"),
              "scaffold gitignores the local context indexes (context.db, chroma/)")
        ci = root / ".github/workflows/sloom-gate.yml"
        check(ci.exists() and "sloom.py" in ci.read_text(encoding="utf-8"),
              "scaffold writes the sloom-gate PR workflow")


def test_scaffold_config_override():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / ".spindleloom/config.json",
           '{"profile":"enterprise","specs_dir":"features","sprints_dir":"iterations"}')
        scaffold.scaffold(root)
        check((root / "docs/product/constitution.md").exists(), "config override: enterprise -> constitution")
        check((root / "docs/features/feature-1/srs.md").exists(), "config override: specs_dir=features honored")
        check((root / "docs/iterations").is_dir(), "config override: sprints_dir=iterations honored")


def test_collisions():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "docs/adr/adr-0004-a.md", "# ADR-0004: a\n\n- **Status:** Accepted\n")
        _w(root / "docs/decisions/adr-0004-b.md", "# ADR-0004: b\n\n- **Status:** Accepted\n")
        _w(root / "docs/RTM.md", "# RTM\n\n| g | p | f |\n|---|---|---|\n| x | y | z |\n")
        _w(root / "docs/specs/auth/frd.md",
           "# FRD auth\n| FRD-AUTH-004 | The system shall log in |\n")
        _w(root / "docs/specs/profile/frd.md",
           "# FRD profile\n| FRD-AUTH-004 | The system shall edit avatar |\n")
        # same ID cited downstream (different kind) — must NOT count as a collision
        _w(root / "docs/specs/auth/sdd.md", "# SDD\nImplements FRD-AUTH-004.\n")
        a = rtm_core.audit(rtm_core.resolve_docs_root(root))
        codes = {p["code"] for p in a["problems"]}
        check("DUP-ADR" in codes, "audit flags DUP-ADR")
        check("MULTI-ADR-DIR" in codes, "audit flags MULTI-ADR-DIR")
        dup = [p for p in a["problems"] if p["code"] == "DUP-REQID"]
        check(len(dup) == 1 and dup[0]["id"] == "FRD-AUTH-004",
              "audit flags DUP-REQID for a two-frd mint collision")
        check(all("sdd.md" not in p["message"] for p in dup),
              "a downstream SDD citation is not counted as a defining file")
        c = rtm_core.conformance(root)
        check(any("DUP-ARTIFACT-ID" in p for p in c["problems"]), "conformance flags DUP-ARTIFACT-ID")
        check(c["ok"] is False, "conformance not ok on collisions")


def test_conformance_clean():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        scaffold.scaffold(root)
        c = rtm_core.conformance(root)
        check(c["ok"], "conformance ok on a freshly scaffolded repo")
        check(c["standard_version"] == rtm_core.STANDARD_VERSION,
              "scaffolded repo pins the current standard_version")


def test_migrate():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "prd.md", "# PRD\n\nPRD-A-001 the system shall ship.\nSee [mrd](docs/01-mrd.md).\n")
        _w(root / "docs/01-mrd.md", "# MRD\n\nmarket.\n")
        _w(root / "docs/decisions/adr-0001-x.md", "# ADR-0001: x\n\n- **Status:** Accepted\n")
        _w(root / "docs/backlog.md", "# Backlog\n\n| PBI |\n|---|\n| PBI-A-001 |\n")

        dry = scaffold.migrate(root)
        froms = {m["from"] for m in dry["moves"]}
        check("prd.md" in froms and "docs/01-mrd.md" in froms, "migrate dry-run plans the funnel moves")
        check(any(lv["kind"] == "backlog" for lv in dry["leave_in_place"]), "migrate leaves backlog in place")
        check(not (root / "docs/product/prd.md").exists(), "dry-run writes nothing")

        applied = scaffold.migrate(root, apply=True, force=True)
        check(applied.get("applied"), "migrate --apply --force applies")
        check((root / "docs/product/prd.md").exists(), "migrate relocates prd into docs/product")
        prd = (root / "docs/product/prd.md").read_text(encoding="utf-8")
        check("](01-mrd.md)" in prd, "migrate rewrites the cross-link to the new location")

        again = scaffold.migrate(root)
        check(again["moved_count"] == 0, "migrate is idempotent (0 moves on re-run)")


def test_migrate_refuses_on_collision():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "docs/adr/adr-0004-a.md", "# ADR-0004: a\n\n- **Status:** Accepted\n")
        _w(root / "docs/decisions/adr-0004-b.md", "# ADR-0004: b\n\n- **Status:** Accepted\n")
        res = scaffold.migrate(root, apply=True, force=True)
        check("error" in res and not res.get("applied"),
              "migrate refuses to apply while ADR collisions exist")


def test_migrate_self_exemption():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "prd.md", "# PRD\n\nPRD-A-001 the system shall ship.\n")          # real project doc
        _w(root / "vendor_toolkit/knowledge_hub/GOVERNANCE.md", "# Spindleloom Governance\n")      # copied-in distribution
        _w(root / "vendor_toolkit/agents/adr-writer.md", "---\nname: adr-writer\n---\nbody\n")
        _w(root / "vendor_toolkit/examples/x/01-mrd.md", "# MRD\n")
        _w(root / "templates/prd-template.md", "# PRD template\n")                   # toolkit-shaped file
        froms = {m["from"] for m in scaffold.migrate(root)["moves"]}
        check("prd.md" in froms, "self-exemption: a real project doc is still planned")
        check(not any(f.startswith("vendor_toolkit/") for f in froms),
              "self-exemption: a nested distribution subtree (knowledge_hub/GOVERNANCE.md) is excluded wholesale")
        check("templates/prd-template.md" not in froms, "self-exemption: *-template.md skipped")
        check(not any("adr-writer" in f for f in froms), "self-exemption: *-writer.md skipped")


def test_migrate_exempt_root():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "knowledge_hub/GOVERNANCE.md", "# Spindleloom Governance\n")
        _w(root / "prd.md", "# PRD\n")
        check(scaffold.migrate(root).get("exempt") is True,
              "migrate refuses (exempt) when the root is itself a distribution")


def test_migrate_dest_collision():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "a/RTM.md", "# RTM a\n")
        _w(root / "b/RTM.md", "# RTM b\n")     # both -> docs/RTM.md
        plan = scaffold.migrate(root)
        check(bool(plan["dest_collisions"]), "dest-collision: two RTMs -> one docs/RTM.md flagged")
        check(plan["moved_count"] == 0, "dest-collision: colliding sources are not moved")
        res = scaffold.migrate(root, apply=True, force=True)
        check("error" in res and not res.get("applied"), "dest-collision: apply is refused")


def test_migrate_refuses_on_existing_dest():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "docs/RTM.md", "# RTM v2 (canonical, already here)\n")     # the existing canonical dest
        _w(root / "legacy/RTM.md", "# RTM v1 (legacy, loose)\n")             # a 2nd RTM -> docs/RTM.md
        _w(root / "prd.md", "# PRD\n")                                       # a clean move alongside
        plan = scaffold.migrate(root)
        check("docs/RTM.md" in {e["to"] for e in plan["dest_exists"]},
              "dest-exists: a legacy RTM onto an existing docs/RTM.md is flagged")
        check(all(m["to"] != "docs/RTM.md" for m in plan["moves"]),
              "dest-exists: the clobbering move is dropped from the plan")
        res = scaffold.migrate(root, apply=True, force=True)
        check("error" in res and not res.get("applied"), "dest-exists: apply is refused")
        check((root / "docs/RTM.md").read_text(encoding="utf-8").startswith("# RTM v2"),
              "dest-exists: the canonical docs/RTM.md is left untouched")


def test_migrate_routes_sprint_plan():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "docs/specs/orion/sprint-01-plan.md", "# Sprint 1 plan\n")   # in the wrong (living) plane
        m = {e["from"]: e["to"] for e in scaffold.migrate(root)["moves"]}
        check(m.get("docs/specs/orion/sprint-01-plan.md") == "docs/sprints/sprint-01-plan.md",
              "sprint-plan relocated out of specs/ into the cyclic sprints/ plane (§4)")


def test_migrate_routes_recon():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "notes/solution-recon.md", "# Recon (loose)\n")                   # loose -> specs/<feature>
        _w(root / "docs/specs/orion/recon.md", "# Recon (already in a feature)\n")  # already home -> leave
        plan = scaffold.migrate(root)
        m = {e["from"]: e["to"] for e in plan["moves"]}
        check(m.get("notes/solution-recon.md") == "docs/specs/feature-1/solution-recon.md",
              "recon: a loose solution-recon is routed into specs/<feature>/")
        leaves = {lv["path"]: lv["kind"] for lv in plan["leave_in_place"]}
        check(leaves.get("docs/specs/orion/recon.md") == "recon",
              "recon: a recon already under specs/ is classified and left in place")


def test_range_shorthand_lint():
    """A3: `<ID>..<N>` range shorthand is flagged (machine-broken orphan); atomic IDs are not.
    Real asserts (not check()) so this genuinely gates under pytest."""
    import validate_reqs
    tmp = Path(tempfile.mkdtemp(prefix="range_"))
    d = tmp / "docs"
    _w(d / "RTM.md", "# RTM\n| Req-ID | Downstream |\n|---|---|\n| FRD-REM-001 | PBI-REM-001..006 |\n")
    hits = validate_reqs.range_shorthand_lint(d)
    assert any("PBI-REM-001..006" in h for h in hits), hits
    assert any("orphans" in h for h in hits), hits
    _w(d / "RTM.md", "# RTM\n| Req-ID | Downstream |\n|---|---|\n| FRD-REM-001 | PBI-REM-001 |\n")
    assert validate_reqs.range_shorthand_lint(d) == [], "atomic IDs must not be flagged"
    print("  PASS  A3 range-shorthand lint flags ranges, ignores atomic IDs")


def test_backlog_completeness_lint():
    """B2: a PBI referenced only in deps / an estimation row (no AC-bearing backlog row) is a
    phantom and is flagged; a PBI defined by an acceptance-criteria row is not."""
    import validate_reqs
    tmp = Path(tempfile.mkdtemp(prefix="phantom_"))
    d = tmp / "docs"
    _w(d / "08-backlog.md",
       "# Backlog\n| Rank | PBI | Story | AC | Deps |\n|---|---|---|---|---|\n"
       "| 1 | PBI-QUE-001 | approve | Given a request, When I approve, Then it is audited | PBI-PLAT-004 |\n")
    _w(d / "09-estimation.md",
       "# Estimation\n| PBI | Notes | Pts |\n|---|---|---|\n| PBI-PLAT-004 | enabler audit store | 5 |\n")
    hits = validate_reqs.backlog_completeness_lint(d)
    assert any("PBI-PLAT-004" in h for h in hits), hits      # dep-only + estimate row -> phantom
    assert not any("PBI-QUE-001" in h for h in hits), hits   # AC-bearing subject row -> defined
    print("  PASS  B2 backlog-completeness flags phantom PBI, ignores AC-defined PBI")


def test_range_shorthand_ellipsis():
    """B5: ellipsis range forms (PBI-X-001…006 and ...006) are flagged too, not just ASCII '..'."""
    import validate_reqs
    d = Path(tempfile.mkdtemp(prefix="ellip_")) / "docs"
    _w(d / "frd.md", "# FRD\n| id | dn |\n|---|---|\n| FRD-A-001 | PBI-PLAT-001…006 |\n")
    assert validate_reqs.range_shorthand_lint(d), "ellipsis range must be flagged"
    _w(d / "frd.md", "# FRD\n| id | dn |\n|---|---|\n| FRD-A-001 | PBI-PLAT-001...006 |\n")
    assert validate_reqs.range_shorthand_lint(d), "'...' range must be flagged"
    print("  PASS  B5 ellipsis / '...' range shorthand flagged")


def test_quality_ok_marker_gates_compound_shall():
    """B4: a compound-shall requirement is flagged unless it carries a machine-checkable
    `quality-ok: <ID>` sign-off marker — free-text justification no longer suppresses it."""
    import validate_reqs
    d = Path(tempfile.mkdtemp(prefix="qok_")) / "docs"
    _w(d / "frd.md", "# FRD\nFRD-B-001 The system shall log the attempt and notify the admin.\n")
    assert any("FRD-B-001" in f and "shall" in f for f in validate_reqs.quality_lint(d)), "unmarked compound-shall must flag"
    _w(d / "frd.md", "# FRD\nFRD-B-001 The system shall log the attempt and notify the admin.\n"
                     "<!-- quality-ok: FRD-B-001 one subject, two audiences -->\n")
    assert not any("FRD-B-001" in f for f in validate_reqs.quality_lint(d)), "quality-ok marker must suppress"
    print("  PASS  B4 quality-ok marker gates compound-shall")


def test_nested_rtm_scope_excluded_from_parent():
    """A subdir owning its own RTM.md is an independent traceability scope — its files must
    not pollute the parent's coverage (the run3/run4-under-medremind-fleet-eval case that
    otherwise flags every sub-run PBI as an orphan against the parent RTM)."""
    import rtm_core
    tmp = Path(tempfile.mkdtemp(prefix="scope_"))
    _w(tmp / "RTM.md", "# RTM\n| FRD-A-001 |\n")
    _w(tmp / "frd.md", "# FRD\nFRD-A-001 the system shall x.\n")
    _w(tmp / "run3" / "RTM.md", "# RTM\n| PBI-B-001 |\n")
    _w(tmp / "run3" / "08-backlog.md",
       "# Backlog\n| PBI | AC |\n|---|---|\n| PBI-B-001 | Given x When y Then z |\n")
    names = {p.name for p in rtm_core.markdown_files(tmp)}
    assert "frd.md" in names, names                 # parent scope kept
    assert "08-backlog.md" not in names, names       # nested self-scoped run excluded
    names_nested = {p.name for p in rtm_core.markdown_files(tmp / "run3")}
    assert "08-backlog.md" in names_nested, names_nested  # validates standalone
    print("  PASS  nested-RTM subdir is its own scope (excluded from parent)")


def main():
    for t in (test_nested_rtm_scope_excluded_from_parent,
              test_scaffold_default, test_scaffold_config_override, test_collisions,
              test_conformance_clean, test_migrate, test_migrate_refuses_on_collision,
              test_migrate_self_exemption, test_migrate_exempt_root, test_migrate_dest_collision,
              test_migrate_refuses_on_existing_dest, test_migrate_routes_sprint_plan,
              test_migrate_routes_recon, test_range_shorthand_lint, test_backlog_completeness_lint,
              test_range_shorthand_ellipsis, test_quality_ok_marker_gates_compound_shall):
        print(f"# {t.__name__}")
        t()
    print()
    if _fails:
        print(f"FAILED - {len(_fails)} check(s).")
        return 1
    print("OK - all Standard-tooling checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
