#!/usr/bin/env python3
"""test_validate_targets.py — the harness-conformance gate must hold AND trip.
Positive: real bundles pass. Negative: an oversize Windsurf rule and a plugin hook
with an unbundled local import each fail. Stdlib-only; pytest-compatible."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGETS = HERE.parent / "targets"


def _run(path):
    return subprocess.run([sys.executable, str(HERE / "validate_targets.py"), str(path)],
                          capture_output=True, text=True)


def _copy():
    tmp = Path(tempfile.mkdtemp(prefix="vt_")) / "targets"
    shutil.copytree(TARGETS, tmp, ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def test_real_bundles_conform():
    r = _run(TARGETS)
    assert r.returncode == 0, r.stdout


def test_oversize_windsurf_rule_trips():
    tmp = _copy()
    try:
        p = next((tmp / "windsurf" / ".windsurf" / "rules").glob("a*.md"))
        p.write_text(p.read_text(encoding="utf-8") + "x" * 13000, encoding="utf-8")
        r = _run(tmp)
        assert r.returncode == 1 and "truncation cap" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)


def test_unbundled_hook_import_trips():
    """The exact class of the shipped-broken hook: a bundled hook importing a local
    module that didn't ship."""
    tmp = _copy()
    try:
        (tmp / "claude-plugin" / "hooks" / "rtm_core.py").unlink()
        r = _run(tmp)
        assert r.returncode == 1 and "NOT bundled" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)


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
    print(f"{'FAIL' if failures else 'OK'} — validate_targets tests: {3 - failures}/3 passed")
    sys.exit(1 if failures else 0)
