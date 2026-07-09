#!/usr/bin/env python3
"""test_sloom.py — the front door must route, batteries must detect repo type.
Stdlib-only; pytest-compatible and runnable directly."""
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _run(*args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / "sloom.py"), *args],
                          capture_output=True, text=True, cwd=cwd)


def test_help_and_unknown():
    assert _run("help").returncode == 0
    r = _run("bogus")
    assert r.returncode == 2 and "unknown command" in r.stdout


def test_toolkit_battery_detected():
    r = _run("check", cwd=str(HERE.parent))
    assert "toolkit repo detected" in r.stdout, r.stdout


def test_adopter_battery_on_clean_project():
    tmp = Path(tempfile.mkdtemp(prefix="sloomchk_"))
    try:
        (tmp / "docs").mkdir()
        (tmp / "docs" / "frd.md").write_text(
            "# FRD\n| ID | Req |\n|---|---|\n| FRD-A-001 | The system shall save |\n", encoding="utf-8")
        (tmp / "docs" / "RTM.md").write_text("# RTM\n| ID |\n|---|\n| FRD-A-001 |\n", encoding="utf-8")
        r = _run("check", str(tmp))
        assert r.returncode == 0 and "adopter repo" in r.stdout and "gates green" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_passthrough_forwards_args():
    r = _run("reqs", str(HERE.parent / "examples" / "healthy-meal-app"))
    assert r.returncode == 0 and "traceability intact" in r.stdout, r.stdout


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
    print(f"{'FAIL' if failures else 'OK'} — sloom tests: {4 - failures}/4 passed")
    sys.exit(1 if failures else 0)
