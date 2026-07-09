#!/usr/bin/env python3
"""test_validate_gates.py — the execution-quality gate must hold AND trip.

Covers: PASS artifact with green matrix passes; PASS-with-red-AC fails (the
contradiction case); missing verification under --require fails; release AND
fails on a missing/unevidenced token and passes when all tokens are GO+evidence.
Stdlib-only; pytest-compatible and runnable directly.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

GOOD_VER = """# Verification — PBI-X-001
| Field | Value |
|---|---|
| Verdict | PASS |

## AC coverage matrix
| Criterion | Result |
|---|---|
| AC-1 login succeeds | PASS |
| AC-2 error shown on bad password | covered |
"""

BAD_VER = GOOD_VER.replace("| AC-2 error shown on bad password | covered |",
                           "| AC-2 error shown on bad password | not run |")

GO_TOKEN = """# Sign-off — {gate}
Verdict: GO
Evidence: suite 108/108 green @ abc1234
"""


def _run(root, *args):
    return subprocess.run([sys.executable, str(HERE / "validate_gates.py"), str(root), *args],
                          capture_output=True, text=True)


def _project(ver_text=None, gates=()):
    tmp = Path(tempfile.mkdtemp(prefix="gates_"))
    (tmp / ".spindleloom" / "verifications").mkdir(parents=True)
    (tmp / ".spindleloom" / "signoffs").mkdir(parents=True)
    if ver_text is not None:
        (tmp / ".spindleloom" / "verifications" / "PBI-X-001.md").write_text(ver_text, encoding="utf-8")
    for g in gates:
        (tmp / ".spindleloom" / "signoffs" / f"{g}.md").write_text(GO_TOKEN.format(gate=g), encoding="utf-8")
    return tmp


def test_pass_artifact_clean():
    tmp = _project(GOOD_VER)
    try:
        r = _run(tmp, "--require", "PBI-X-001")
        assert r.returncode == 0, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_pass_with_red_ac_trips():
    tmp = _project(BAD_VER)
    try:
        r = _run(tmp)
        assert r.returncode == 1 and "contradicts its own matrix" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_verification_trips():
    tmp = _project(None)
    try:
        r = _run(tmp, "--require", "PBI-X-001")
        assert r.returncode == 1 and "gate was skipped" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_release_missing_token_trips():
    tmp = _project(GOOD_VER, gates=("qa", "security"))
    try:
        r = _run(tmp, "--release", "--gates", "qa,security,raid")
        assert r.returncode == 1 and "release gate 'raid'" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_release_all_go_passes():
    tmp = _project(GOOD_VER, gates=("qa", "security", "raid"))
    try:
        r = _run(tmp, "--release", "--gates", "qa,security,raid")
        assert r.returncode == 0 and "all 3 release gates evidenced GO" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _ctx_db(tmp, task_id=None):
    import sqlite3
    db = tmp / ".spindleloom" / "context.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE agent_context (id INTEGER PRIMARY KEY, agent_id TEXT, "
                "task_id TEXT, facts TEXT, tags TEXT, saved_at TEXT, chroma_synced INTEGER, source TEXT)")
    if task_id:
        con.execute("INSERT INTO agent_context (agent_id, task_id, facts, tags, saved_at, chroma_synced, source)"
                    " VALUES ('brd-writer', ?, '- decided X', '', '2026-07-09T00:00:00', 1, '')", (task_id,))
    con.commit(); con.close()


def test_context_gate_passes_with_entries():
    tmp = _project(GOOD_VER)
    try:
        _ctx_db(tmp, "demo-feature")
        r = _run(tmp, "--context", "demo-feature")
        assert r.returncode == 0 and "handoff-context entr" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_context_gate_trips_when_empty():
    tmp = _project(GOOD_VER)
    try:
        _ctx_db(tmp, None)  # db exists, zero entries for the task
        r = _run(tmp, "--context", "demo-feature")
        assert r.returncode == 1 and "zero saved entries" in r.stdout, r.stdout
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
    print(f"{'FAIL' if failures else 'OK'} — validate_gates tests: {7 - failures}/7 passed")
    sys.exit(1 if failures else 0)
