#!/usr/bin/env python3
"""test_build_context_pack.py — the pack must assemble, flag gaps, and advise on budget.
Stdlib-only; pytest-compatible and runnable directly."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _run(*args):
    return subprocess.run([sys.executable, str(HERE / "build_context_pack.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def _project():
    tmp = Path(tempfile.mkdtemp(prefix="pack_"))
    (tmp / "docs").mkdir()
    (tmp / "docs" / "prd.md").write_text(
        "# PRD\n\n| Field | Value |\n|---|---|\n| Status | Approved |\n\n"
        "| ID | Story |\n|---|---|\n| PRD-AUTH-001 | login (ASSUMPTION-3 pending) |\n\n"
        "## Digest\n- decides the login flow\n- mints PRD-AUTH-001\n", encoding="utf-8")
    (tmp / "docs" / "srs.md").write_text(
        "# SRS\n| ID | Req |\n|---|---|\n| SR-PERF-001 | The system shall respond in 200 ms |\n",
        encoding="utf-8")
    return tmp


def test_pack_assembles_with_digest_and_assumptions():
    tmp = _project()
    try:
        r = _run(str(tmp), "sdd-writer", "--task-id", "auth")
        assert r.returncode == 0, r.stdout + r.stderr
        assert "prd.md" in r.stdout and "decides the login flow" in r.stdout, r.stdout
        assert "ASSUMPTION-3" in r.stdout, r.stdout
        assert "not found on disk" in r.stdout  # recon/RFC genuinely absent -> flagged
        assert "within budget" in r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_pack_budget_demotion_advice():
    tmp = _project()
    try:
        r = _run(str(tmp), "sdd-writer", "--budget", "10")
        assert r.returncode == 0 and "OVER" in r.stdout and "Demote" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_unknown_agent_fails():
    tmp = _project()
    try:
        r = _run(str(tmp), "no-such-agent")
        assert r.returncode == 2 and "no agent definition" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_upstream_chain_routes_ancestors_not_only_direct_inputs():
    """A1: an agent sees its spec-chain ancestors (an earlier funnel phase) in section 1b,
    even when they aren't declared inputs. estimation-facilitator declares only `backlog`,
    yet must see the FRD/SRS above it. And 1b must NOT dump the whole cyclic fleet graph."""
    tmp = Path(tempfile.mkdtemp(prefix="pack_"))
    try:
        d = tmp / "docs"
        d.mkdir()
        for name, body in (
            ("frd.md", "# FRD\n| ID | Rule |\n|---|---|\n| FRD-AUTH-001 | login |\n"),
            ("srs.md", "# SRS\n| ID | Req |\n|---|---|\n| SR-PERF-001 | 200ms |\n"),
            ("backlog.md", "# Backlog\n| PBI | Story |\n|---|---|\n| PBI-AUTH-001 | login |\n"),
        ):
            (d / name).write_text(body, encoding="utf-8")
        r = _run(str(tmp), "estimation-facilitator")
        assert r.returncode == 0, r.stdout + r.stderr
        section_1b = r.stdout.split("Upstream chain")[1].split("RTM slice")[0]
        assert "frd.md" in section_1b and "srs.md" in section_1b, section_1b
        # phase-bounded + on-disk-only: no later-phase / not-yet-produced noise leaks in
        assert "not on disk" not in section_1b, section_1b
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_input_resolution_is_stem_aware():
    """B1: a declared input name resolves to its artifact across plural/-ion forms.
    sprint-planner's input `estimates` must resolve to `09-estimation.md` — the run3 silent
    estimation->sprint drop (no token matched `estimates` vs `estimation`)."""
    tmp = Path(tempfile.mkdtemp(prefix="pack_"))
    try:
        d = tmp / "docs"
        d.mkdir()
        (d / "backlog.md").write_text("# Backlog\n| PBI |\n|---|\n| PBI-A-001 |\n", encoding="utf-8")
        (d / "09-estimation.md").write_text("# Estimation\nPBI-A-001 = 3 pts\n", encoding="utf-8")
        r = _run(str(tmp), "sprint-planner")
        assert r.returncode == 0, r.stdout + r.stderr
        contract = r.stdout.split("Contract inputs")[1].split("Upstream chain")[0]
        assert "09-estimation.md" in contract, contract  # 'estimates' resolved, not "not found"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    failures = 0
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        try:
            fn()
            print(f"  ok  {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {name}: {str(e)[:200]}")
    print(f"{'FAIL' if failures else 'OK'} — build_context_pack tests: "
          f"{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
