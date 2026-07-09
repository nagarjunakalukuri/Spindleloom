#!/usr/bin/env python3
"""test_sync_context_log.py — the cross-machine context flow must actually work.
Machine A saves (log line written) → machine B (fresh clone: log present, no DB)
imports → the entry is queryable. Import is idempotent; export backfills a pre-log DB;
a merge-mangled line is skipped, not fatal. Stdlib-only; pytest-compatible."""
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

ENTRY = {"agent_id": "backend-developer", "task_id": "user-auth",
         "facts": "• Decision: JWT RS256 — SRS-SEC-002", "tags": "auth,jwt",
         "saved_at": "2026-07-09T10:00:00+00:00", "source": "specs/auth/frd.md"}


def _run(root, *flags):
    return subprocess.run([sys.executable, str(HERE / "sync_context_log.py"), str(root), *flags],
                          capture_output=True, text=True)


def _rows(root):
    db = Path(root) / ".spindleloom" / "context.db"
    if not db.is_file():
        return []
    con = sqlite3.connect(db)
    rows = con.execute("SELECT agent_id, task_id, facts FROM agent_context").fetchall()
    con.close()
    return rows


def _clone_with_log(*entries):
    """A fresh 'machine B': the committed log exists, no local DB yet."""
    tmp = Path(tempfile.mkdtemp(prefix="ctxlog_"))
    d = tmp / ".spindleloom"
    d.mkdir()
    (d / "context-log.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries), encoding="utf-8")
    return tmp


def test_import_recovers_teammate_entry():
    tmp = _clone_with_log(ENTRY)
    try:
        r = _run(tmp)
        assert r.returncode == 0 and "imported 1 new entry" in r.stdout, r.stdout
        rows = _rows(tmp)
        assert rows == [("backend-developer", "user-auth", ENTRY["facts"])], rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_import_is_idempotent():
    tmp = _clone_with_log(ENTRY)
    try:
        _run(tmp)
        r = _run(tmp)
        assert "imported 0 new" in r.stdout and len(_rows(tmp)) == 1, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_mangled_merge_line_skipped_not_fatal():
    tmp = _clone_with_log(ENTRY)
    try:
        log = tmp / ".spindleloom" / "context-log.jsonl"
        log.write_text(log.read_text(encoding="utf-8") + "<<<<<<< HEAD garbage\n", encoding="utf-8")
        r = _run(tmp)
        assert r.returncode == 0 and "1 unparseable line(s) skipped" in r.stdout, r.stdout
        assert len(_rows(tmp)) == 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_export_backfills_pre_log_db():
    tmp = Path(tempfile.mkdtemp(prefix="ctxlog_"))
    try:
        d = tmp / ".spindleloom"
        d.mkdir()
        con = sqlite3.connect(d / "context.db")
        con.execute("CREATE TABLE agent_context (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "agent_id TEXT NOT NULL, task_id TEXT NOT NULL DEFAULT '', facts TEXT NOT NULL, "
                    "tags TEXT NOT NULL DEFAULT '', saved_at TEXT NOT NULL, "
                    "chroma_synced INTEGER NOT NULL DEFAULT 1, source TEXT NOT NULL DEFAULT '')")
        con.execute("INSERT INTO agent_context (agent_id, task_id, facts, tags, saved_at) "
                    "VALUES ('architect', 'payments', '• Decision: outbox pattern', 'kafka', '2026-07-01T00:00:00')")
        con.commit(); con.close()
        r = _run(tmp, "--export")
        assert "exported 1 DB row(s)" in r.stdout, r.stdout
        lines = (d / "context-log.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1 and json.loads(lines[0])["agent_id"] == "architect"
        r2 = _run(tmp, "--export")  # idempotent
        assert "exported 0 DB row(s)" in r2.stdout, r2.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    failures = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        try:
            fn()
            print(f"  ok  {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {name}: {str(e)[:200]}")
    print(f"{'FAIL' if failures else 'OK'} — sync_context_log tests: {len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
