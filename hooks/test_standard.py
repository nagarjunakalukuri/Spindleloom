#!/usr/bin/env python3
"""
test_standard.py — stdlib-only tests for the Wheelwright Standard tooling: config-driven
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
        cfg = (root / ".shipwright/config.json").read_text(encoding="utf-8")
        check('"standard_version"' in cfg and '"profile"' in cfg,
              "scaffold writes standard_version + profile to config")


def test_scaffold_config_override():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / ".shipwright/config.json",
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
        a = rtm_core.audit(rtm_core.resolve_docs_root(root))
        codes = {p["code"] for p in a["problems"]}
        check("DUP-ADR" in codes, "audit flags DUP-ADR")
        check("MULTI-ADR-DIR" in codes, "audit flags MULTI-ADR-DIR")
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
        _w(root / "vendor_toolkit/project_guides/STANDARD.md", "# The Wheelwright Standard\n")      # copied-in distribution
        _w(root / "vendor_toolkit/agents/adr-writer.md", "---\nname: adr-writer\n---\nbody\n")
        _w(root / "vendor_toolkit/examples/x/01-mrd.md", "# MRD\n")
        _w(root / "templates/prd-template.md", "# PRD template\n")                   # toolkit-shaped file
        froms = {m["from"] for m in scaffold.migrate(root)["moves"]}
        check("prd.md" in froms, "self-exemption: a real project doc is still planned")
        check(not any(f.startswith("vendor_toolkit/") for f in froms),
              "self-exemption: a nested distribution subtree (project_guides/STANDARD.md) is excluded wholesale")
        check("templates/prd-template.md" not in froms, "self-exemption: *-template.md skipped")
        check(not any("adr-writer" in f for f in froms), "self-exemption: *-writer.md skipped")


def test_migrate_exempt_root():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _w(root / "project_guides/STANDARD.md", "# The Wheelwright Standard\n")
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


def main():
    for t in (test_scaffold_default, test_scaffold_config_override, test_collisions,
              test_conformance_clean, test_migrate, test_migrate_refuses_on_collision,
              test_migrate_self_exemption, test_migrate_exempt_root, test_migrate_dest_collision,
              test_migrate_refuses_on_existing_dest, test_migrate_routes_sprint_plan,
              test_migrate_routes_recon):
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
