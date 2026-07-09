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
                          capture_output=True, text=True)


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


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok  {name}")
            except AssertionError as e:
                failures += 1
                print(f"  FAIL {name}: {str(e)[:200]}")
    print(f"{'FAIL' if failures else 'OK'} — build_context_pack tests: {3 - failures}/3 passed")
    sys.exit(1 if failures else 0)
