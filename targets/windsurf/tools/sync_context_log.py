#!/usr/bin/env python3
"""sync_context_log.py — reconcile the git-committed context log with the local DB.

The context store has two halves with different jobs:
  .spindleloom/context-log.jsonl   COMMITTED — append-only, git-mergeable; the
                                   cross-machine source of truth for saved handoff context
  .spindleloom/context.db          LOCAL — SQLite index recall_context queries; binary,
                                   never committed (gitignored by scaffold)

`save_context` writes both. This tool covers the two flows saves can't:

    python hooks/sync_context_log.py <root>              # --import (default): replay any
                                                         # log lines missing from the local
                                                         # DB — run after `git pull`
    python hooks/sync_context_log.py <root> --export     # backfill: append any DB rows
                                                         # missing from the log (migrates a
                                                         # repo whose saves predate the log)

Dedup key is (agent_id, task_id, facts) — the same key `save_context` uses — so replaying
is idempotent and a teammate's identical re-save never duplicates. Exit 0 always unless the
log is unreadable. Stdlib-only.
"""
import json
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

FIELDS = ("agent_id", "task_id", "facts", "tags", "saved_at", "source")


def _con(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=5000")  # wait out a concurrent writer, don't fail
    # Same schema save_context creates — import must work on a fresh clone with no DB yet.
    con.execute("""
        CREATE TABLE IF NOT EXISTS agent_context (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id      TEXT    NOT NULL,
            task_id       TEXT    NOT NULL DEFAULT '',
            facts         TEXT    NOT NULL,
            tags          TEXT    NOT NULL DEFAULT '',
            saved_at      TEXT    NOT NULL,
            chroma_synced INTEGER NOT NULL DEFAULT 1,
            source        TEXT    NOT NULL DEFAULT ''
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_ctx_task ON agent_context(task_id)")
    try:
        con.execute("ALTER TABLE agent_context ADD COLUMN source TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    con.commit()
    return con


def _read_log(log):
    entries, bad = [], 0
    if not log.is_file():
        return entries, bad
    for line in log.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            entries.append({k: str(e.get(k, "")) for k in FIELDS})
        except ValueError:
            bad += 1  # a mangled merge line — report, don't crash
    return entries, bad


def do_import(con, log):
    entries, bad = _read_log(log)
    added = 0
    semantic = __import__("os").environ.get("SPINDLELOOM_SEMANTIC", "").strip() in ("1", "true", "yes")
    for e in entries:
        # One atomic INSERT-if-absent per row: SQLite serializes the write, so two
        # concurrent imports (post-pull hook + a manual run) can't both miss-then-insert
        # the same row. No UNIQUE index — the table is shared with save_context, which
        # would then raise on its plain INSERTs.
        cur = con.execute(
            "INSERT INTO agent_context (agent_id, task_id, facts, tags, saved_at, chroma_synced, source)"
            " SELECT ?,?,?,?,?,?,? WHERE NOT EXISTS ("
            "   SELECT 1 FROM agent_context WHERE agent_id=? AND task_id=? AND facts=?)",
            (e["agent_id"], e["task_id"], e["facts"], e["tags"], e["saved_at"],
             0 if semantic else 1, e["source"],
             e["agent_id"], e["task_id"], e["facts"]))
        added += cur.rowcount
    con.commit()
    note = f"; {bad} unparseable line(s) skipped — inspect the log for merge damage" if bad else ""
    print(f"sync_context_log: imported {added} new entr{'y' if added == 1 else 'ies'} "
          f"from {len(entries)} log line(s){note}")
    if added and semantic:
        print("  · semantic mode on — run the sync_contexts MCP tool to index the new rows")
    return 0


def do_export(con, log):
    seen = {(e["agent_id"], e["task_id"], e["facts"]) for e in _read_log(log)[0]}
    rows = con.execute(
        "SELECT agent_id, task_id, facts, tags, saved_at, source FROM agent_context ORDER BY id"
    ).fetchall()
    added = 0
    with open(log, "a", encoding="utf-8") as f:
        for r in rows:
            if (r["agent_id"], r["task_id"], r["facts"]) in seen:
                continue
            f.write(json.dumps({k: r[k] for k in FIELDS}, ensure_ascii=False) + "\n")
            added += 1
    print(f"sync_context_log: exported {added} DB row(s) missing from the log "
          f"({len(rows)} total rows) — commit {log.name} to share them")
    return 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if "--help" in flags or "-h" in argv[1:]:
        print(__doc__)
        return 0
    root = Path(args[0]) if args else Path(".")
    tool = root / ".spindleloom"
    if not tool.is_dir() and (root / ".shipwright").is_dir():
        tool = root / ".shipwright"  # pre-0.3 tool dir
    tool.mkdir(exist_ok=True)
    log = tool / "context-log.jsonl"
    con = _con(str(tool / "context.db"))
    try:
        return do_export(con, log) if "--export" in flags else do_import(con, log)
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
