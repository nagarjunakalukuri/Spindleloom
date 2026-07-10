#!/usr/bin/env python3
"""test_new_gates.py -- the anti-drift gates added from the six-perspective audit.

Covers build_governance_handbook (reading view in sync with GOVERNANCE.md),
validate_counts (no stale fleet numbers in the docs), validate_personas (the persona
hub's agent/command references resolve), and the sloom signoff writer. Stdlib-only,
pytest-style bare asserts."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import build_governance_handbook as gh   # noqa: E402
import validate_counts as vc             # noqa: E402
import validate_personas as vp           # noqa: E402
import sloom                             # noqa: E402
import build_guides_site as gs          # noqa: E402
import build_fleet_page as fp           # noqa: E402


# ---- build_governance_handbook ----

def test_handbook_splits_three_parts():
    parts = gh.split_parts()
    assert [p[0] for p in parts] == ["I", "II", "III"]
    assert all(body.strip() for _, _, body in parts)


def test_handbook_render_deterministic_and_covers_parts():
    a, b = gh.render(), gh.render()
    assert a == b                       # pure function of the source
    assert "part-i" in a and "part-ii" in a and "part-iii" in a


def test_handbook_on_disk_in_sync():
    # the committed HTML must equal a fresh render (the --check contract)
    current = gh.OUT.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert current.strip() == gh.render().strip(), "governance-handbook.html stale -- run build_governance_handbook.py"


# ---- validate_counts ----

def test_counts_match_the_folders():
    c = vc.real_counts()
    agents = [p for p in (ROOT / "agents").glob("*.md") if p.name not in ("INDEX.md", "HELP.md")]
    assert c["agents"] == len(agents)
    assert c["commands"] == len(list((ROOT / "commands").glob("*.md")))
    assert c["templates"] == len(list((ROOT / "templates").glob("*.md")))


def test_counts_no_stale_doc_numbers():
    _, problems = vc.scan()
    assert problems == [], "stale counts: " + "; ".join("%s:%d %s" % (r, n, f) for r, n, f, *_ in problems)


def test_counts_flags_a_planted_mismatch():
    # a headline enumeration with a wrong number must be caught
    real = vc.real_counts()
    line = "the fleet: %d agents, 999 templates, %d skills" % (real["agents"], real["skills"])
    hits = [(int(m.group(1)), vc._key(m.group(2))) for m in vc.PAT.finditer(line)]
    kinds = {k for _, k in hits}
    assert "agents" in kinds and len(kinds) >= 2           # recognized as an enumeration
    assert any(n == 999 and k == "templates" for n, k in hits)


# ---- validate_personas ----

def test_personas_all_refs_resolve():
    agent_refs, cmd_refs, bad_agents, bad_cmds = vp.scan()
    assert not bad_agents, "dangling agent refs: %s" % bad_agents
    assert not bad_cmds, "dangling command refs: %s" % bad_cmds
    assert len(agent_refs) >= 15 and len(cmd_refs) >= 10


# ---- sloom signoff ----

def test_signoff_writes_evidenced_token(tmp_path):
    rc = sloom.signoff_cmd(["qa", "--verdict", "GO", "--by", "QA Lead",
                            "--evidence", "docs/reports/qa.md", str(tmp_path)])
    assert rc == 0
    tok = tmp_path / ".spindleloom" / "signoffs" / "qa.md"
    body = tok.read_text(encoding="utf-8")
    assert "Verdict: GO" in body and "Evidence:" in body and "By: QA Lead" in body


def test_signoff_go_requires_evidence(tmp_path):
    rc = sloom.signoff_cmd(["qa", "--verdict", "GO", "--by", "X", str(tmp_path)])
    assert rc == 2                                          # unevidenced GO is refused
    assert not (tmp_path / ".spindleloom" / "signoffs" / "qa.md").exists()


def test_signoff_release_id_namespaces(tmp_path):
    sloom.signoff_cmd(["security", "--by", "Sec", "--evidence", "scan.txt",
                       "--release-id", "v1.2", str(tmp_path)])
    assert (tmp_path / ".spindleloom" / "signoffs" / "v1.2" / "security.md").is_file()


# ---- build_guides_site ----

def test_site_twin_names_and_link_map():
    assert gs.twin_name("BEST-PRACTICES.md") == "best-practices.html"
    assert gs.LINK_MAP["GOVERNANCE.md"] == "governance-handbook.html"   # one reading view per doc


def test_site_outputs_deterministic_and_on_disk_in_sync():
    a, b = gs.outputs(), gs.outputs()
    assert a == b
    for name, page in a.items():
        disk = (gs.SITE / name).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        assert disk.strip() == page.strip(), name + " stale -- run build_guides_site.py"


def test_site_index_is_the_homepage():
    page = gs.outputs()["index.html"]
    assert "One loop, six stages" in page                      # the journey
    assert page.count('class="gcard"') >= 14                   # the full page manifest
    counts = gs.vc.real_counts()
    assert "<b>%d</b><span>agents</span>" % counts["agents"] in page   # live numbers
    assert "personas/index.html#/start" in page                # the Start-here CTA
    assert page.count('class="mcard"') == 4                    # machinery pillars
    assert page.count('class="hcard"') == 5                    # harness targets
    assert "harness-matrix.html" in page                       # matrix deep-link


def test_site_rewrites_intra_folder_md_links():
    out = gs.rewrite_links('<a href="BEST-PRACTICES.md#x">y</a> <a href="../README.md">root</a>')
    assert 'href="best-practices.html#x"' in out          # intra-folder -> twin
    assert 'href="../README.md"' in out                   # out-of-folder untouched


# ---- build_fleet_page ----

def test_fleet_data_deterministic_and_on_disk_in_sync():
    a, b = fp.render_data(), fp.render_data()
    assert a == b
    current = fp.PAGE.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    assert fp.splice(current, a).strip() == current.strip(), "fleet page data stale -- run build_fleet_page.py"


def test_fleet_edge_counts_match_contracts():
    agents = fp.read_contracts()
    contract_edges = sum(len(m["downstream"]) for m in agents.values())
    data = fp.render_data()
    import re
    typed = re.findall(r"t:'([psf])'", data)
    assert len(typed) == contract_edges          # every contract edge, exactly once
    assert data.count("t:'i'}") == len(set(fp.INDEX_SOURCES))


def test_fleet_stale_override_fails():
    fp.EDGE_TYPE_OVERRIDES[("ghost-agent", "nobody")] = "s"
    try:
        import pytest
        with pytest.raises(SystemExit):
            fp.render_data()
    finally:
        del fp.EDGE_TYPE_OVERRIDES[("ghost-agent", "nobody")]
