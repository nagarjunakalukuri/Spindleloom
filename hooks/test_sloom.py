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


def test_flags_register_groups_by_owner_and_gates():
    """A5: `sloom flags` surfaces FLAG(<agent>): markers grouped by owner; --strict gates."""
    tmp = Path(tempfile.mkdtemp(prefix="sloomflags_"))
    try:
        (tmp / "docs").mkdir()
        (tmp / "docs" / "frd.md").write_text(
            "# FRD\nFRD-AUD-001 audit.\nFLAG(prd-writer): URS-AUD-001/002 have no PRD story\n",
            encoding="utf-8")
        r = _run("flags", str(tmp))
        assert r.returncode == 0 and "-> prd-writer" in r.stdout, r.stdout
        assert "no PRD story" in r.stdout, r.stdout
        assert _run("flags", str(tmp), "--strict").returncode == 1  # open flags -> gate fails
        (tmp / "docs" / "frd.md").write_text("# FRD\nFRD-AUD-001 audit.\n", encoding="utf-8")
        r2 = _run("flags", str(tmp))
        assert r2.returncode == 0 and "nothing queued" in r2.stdout, r2.stdout
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
    print(f"{'FAIL' if failures else 'OK'} — sloom tests: {len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
