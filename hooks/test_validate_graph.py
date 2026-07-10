#!/usr/bin/env python3
"""test_validate_graph.py — regression tests for the fleet validator.

Positive: the repo itself passes all 13 checks. Negative: each recently-added
check (11 loop fields, 12 fleet-page sync, 13 artifact chain) must TRIP when its
invariant is broken in a temp copy — a gate that can't fail is dead config.
Stdlib-only; pytest-compatible (test_* functions) and runnable directly.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _run(root):
    return subprocess.run(
        [sys.executable, str(HERE / "validate_graph.py")],
        capture_output=True, text=True, cwd=str(root),
    )


def _tmp_repo():
    """Copy the pieces validate_graph reads into a temp root."""
    tmp = Path(tempfile.mkdtemp(prefix="vgtest_"))
    for d in ("agents", "skills", "commands", "templates"):
        shutil.copytree(ROOT / d, tmp / d)
    (tmp / "spindleloom_website").mkdir()
    shutil.copy(ROOT / "spindleloom_website" / "spindleloom-agent-fleet.html",
                tmp / "spindleloom_website" / "spindleloom-agent-fleet.html")
    # the validator resolves ROOT from its own location — copy it (and nothing else
    # from hooks/) so it runs against the temp tree
    (tmp / "hooks").mkdir()
    shutil.copy(HERE / "validate_graph.py", tmp / "hooks" / "validate_graph.py")
    return tmp


def _run_tmp(tmp):
    return subprocess.run(
        [sys.executable, str(tmp / "hooks" / "validate_graph.py")],
        capture_output=True, text=True, cwd=str(tmp),
    )


def test_repo_passes():
    r = _run(ROOT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_tmp_copy_passes():
    tmp = _tmp_repo()
    try:
        r = _run_tmp(tmp)
        assert r.returncode == 0, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_check11_loop_fields_trip():
    tmp = _tmp_repo()
    try:
        p = tmp / "agents" / "debugger.md"
        p.write_text(re.sub(r"(?m)^loop: .*\n", "", p.read_text(encoding="utf-8"), count=1),
                     encoding="utf-8")
        r = _run_tmp(tmp)
        assert r.returncode == 1 and "missing loop:" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_check12_fleet_page_trips():
    tmp = _tmp_repo()
    try:
        p = tmp / "spindleloom_website" / "spindleloom-agent-fleet.html"
        t = p.read_text(encoding="utf-8")
        line = next(l for l in t.splitlines() if "from:'brd-writer', to:'urs-writer'" in l)
        p.write_text(t.replace(line + "\n", "", 1), encoding="utf-8")
        r = _run_tmp(tmp)
        assert r.returncode == 1 and "fleet-page: contract edge brd-writer -> urs-writer" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_check13_artifact_chain_trips():
    """Reintroduce the original A1 bug (sdd-writer inputs: [PRD]) — must fail."""
    tmp = _tmp_repo()
    try:
        p = tmp / "agents" / "sdd-writer.md"
        p.write_text(re.sub(r"(?m)^inputs: \[.*\]$", "inputs: [PRD]",
                            p.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        r = _run_tmp(tmp)
        assert r.returncode == 1 and "artifact-chain:" in r.stdout, r.stdout
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
    print(f"{'FAIL' if failures else 'OK'} — validate_graph tests: "
          f"{5 - failures}/5 passed")
    sys.exit(1 if failures else 0)
