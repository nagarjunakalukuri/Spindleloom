#!/usr/bin/env python3
"""
mcp_server.py — Spindleloom traceability MCP server (FastMCP).

Exposes the live requirement/traceability graph (parsed by rtm_core) so any
MCP-aware harness — Claude Code, Cursor, Copilot/VS Code, Windsurf — can query
the RTM live instead of reading static markdown.

Requires the MCP SDK (the one opt-in dependency, isolated to this server; the
validator and rtm_core stay stdlib-only):
    pip install "mcp[cli]"

$SPINDLELOOM_SPEC_ROOT (default: current dir) is the *project root*, set in the
harness's .mcp.json; the actual docs folder is resolved from .spindleloom/config.json
(`docs_root`, default `docs/`, falling back to the project root for a flat layout).
Read-only.
"""
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402
import scaffold  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.exit('mcp_server: the MCP SDK is not installed. Run:  pip install "mcp[cli]"')

mcp = FastMCP("sloom")


def _root():
    return str(rtm_core.resolve_docs_root(os.environ.get("SPINDLELOOM_SPEC_ROOT", ".")))


def _project_root():
    """The project root the server was pointed at (SPINDLELOOM_SPEC_ROOT) — scaffolding
    targets this, not the resolved docs_root."""
    return os.environ.get("SPINDLELOOM_SPEC_ROOT", ".")


def _writable():
    """Write tools are opt-in: enabled only when SPINDLELOOM_WRITABLE is truthy."""
    return os.environ.get("SPINDLELOOM_WRITABLE", "").strip().lower() in ("1", "true", "yes", "on")


@mcp.tool()
def trace_requirement(req_id: str) -> dict:
    """Trace one Req-ID (e.g. 'FRD-TRK-001') through the RTM: where it is defined
    and the full row across every altitude (business goal -> story -> FRD -> SRS
    -> design -> build/test) — its blast radius if changed."""
    return rtm_core.trace(_root(), req_id)


@mcp.tool()
def rtm_coverage() -> dict:
    """Audit traceability for the spec folder: coverage gaps (UNCOVERED), broken
    references, PBI orphans (scope creep), ADR-reference integrity, plus counts."""
    return rtm_core.audit(_root())


@mcp.tool()
def list_requirements(doc: str = "") -> list:
    """List every Req-ID in the spec folder, optionally filtered by document type
    (e.g. doc='FRD' or 'SRS'), with the files each is defined in."""
    return rtm_core.list_requirements(_root(), doc or None)


@mcp.tool()
def find_decision(adr_id: str) -> dict:
    """Look up an architecture decision by id/number (e.g. 'ADR-0001' or '1'): its
    decisions-table row, whether a defining ADR file exists, and where it's cited."""
    return rtm_core.find_decision(_root(), adr_id)


@mcp.tool()
def list_artifacts(kind: str = "", status: str = "") -> list:
    """Catalog every project artifact (PRD, SRS, SDD, ADRs, RTM, …) with its path,
    owner, status, version, last-updated, and Req-ID count. Optionally filter by
    kind (e.g. 'adr', 'prd') or status (e.g. 'draft', 'approved')."""
    arts = rtm_core.artifacts(_root())
    if kind:
        arts = [a for a in arts if a["kind"].lower() == kind.lower()]
    if status:
        arts = [a for a in arts if (a["status"] or "").lower() == status.lower()]
    return arts


@mcp.tool()
def find_artifact(query: str) -> list:
    """Find an artifact by id ('PRD', 'ADR-0001'), kind ('adr'), or a title/path
    substring — returns where it lives plus its owner/status/version. 'How do I get X?'"""
    return rtm_core.find_artifact(_root(), query)


@mcp.tool()
def funnel_status(req_id: str = "") -> dict:
    """How far requirements propagate down the funnel (MRD→…→TSD). For each RTM row
    (or just the row(s) carrying req_id), reports which altitude columns are filled
    vs blank, the deepest altitude reached, and the first gap — 'is this fully
    specified, and where does the chain stop?'"""
    return rtm_core.funnel_status(_root(), req_id or None)


@mcp.tool()
def stale_artifacts() -> dict:
    """Change-control check: funnel docs whose last-updated date is older than an
    upstream they derive from (e.g. the PRD changed but the FRD didn't follow).
    Returns each stale doc with what it's stale against, plus any undated docs."""
    return rtm_core.stale_artifacts(_root())


@mcp.tool()
def next_req_id(doc: str, area: str) -> dict:
    """Suggest the next free Req-ID for a document + area (e.g. doc='PRD', area='AUTH'
    -> 'PRD-AUTH-004'), so a newly authored requirement doesn't collide with an
    existing one."""
    return rtm_core.next_req_id(_root(), doc, area)


@mcp.tool()
def search_specs(query: str, max_results: int = 50) -> dict:
    """Full-text search across the spec docs (case-insensitive substring): returns
    path + line number + the matching line. Find where something is discussed without
    reading whole files."""
    return rtm_core.search_specs(_root(), query, max_results)


@mcp.tool()
def check_conformance() -> dict:
    """Does this repo match the Spindleloom Standard? Returns the conformance report
    (declared profile/version vs the toolkit's, plus duplicate artifact IDs — e.g. two
    RTMs or two ADR files claiming one id) alongside the RTM/Req-ID audit (which now
    flags duplicate ADRs and multiple ADR directories). See project_guides/STANDARD.md §11."""
    return {"conformance": rtm_core.conformance(_project_root()), "audit": rtm_core.audit(_root())}


@mcp.tool()
def scaffold_project(profile: str = "mid", feature: str = "feature-1") -> dict:
    """WRITE TOOL (opt-in) — lay down the canonical Spindleloom doc layout under the
    project root: the docs/ funnel, the RTM backbone, the cyclic sprints/ home, and the
    .spindleloom/ machinery (per project_guides/STANDARD.md). profile is 'lean' | 'mid' | 'enterprise'.
    Idempotent: never overwrites an existing file. Disabled unless the server was started
    with SPINDLELOOM_WRITABLE=1."""
    if not _writable():
        return {"writable": False,
                "error": "scaffold_project is a write tool and is disabled. Restart the "
                         "server with SPINDLELOOM_WRITABLE=1 in its env to enable it."}
    try:
        created = scaffold.scaffold(_project_root(), profile=profile, feature=feature)
    except ValueError as e:
        return {"writable": True, "error": str(e)}
    return {"writable": True, "root": _project_root(), "profile": profile, "feature": feature,
            "created": created, "count": len(created)}


# --- Agent context / memory handoff ---
# Default:  SQLite keyword search (always available, zero deps, zero config)
# Optional: ChromaDB local semantic search -- enabled by setting
#           SPINDLELOOM_SEMANTIC=1 in the server env AND installing chromadb:
#               pip install chromadb   (or uv add chromadb)
#           Uses built-in ONNX all-MiniLM-L6-v2 embeddings -- zero API calls,
#           ~40 MB model cached in ~/.cache/chroma/ after first run.

def _semantic_enabled() -> bool:
    return os.environ.get("SPINDLELOOM_SEMANTIC", "").strip().lower() in ("1", "true", "yes", "on")

_chromadb = None
if _semantic_enabled():
    try:
        import chromadb as _chromadb  # type: ignore
    except ImportError:
        pass  # env flag set but package missing -- stays on SQLite

def _CHROMA() -> bool:
    return _chromadb is not None


def _artifact_updated(path_str):
    """The registry's Last-updated stamp (YYYY-MM-DD) for an artifact path, or None.
    Reads <tool-dir>/artifacts.json once per call; missing registry -> None."""
    try:
        reg = Path(rtm_core.tool_dir(_project_root())) / "artifacts.json"
        if not reg.exists():
            return None
        data = json.loads(reg.read_text(encoding="utf-8", errors="ignore"))
        for a in (data if isinstance(data, list) else data.get("artifacts", [])):
            if a.get("path") == path_str:
                return a.get("updated") or None
    except Exception:
        return None
    return None


def _stale(source, saved_at):
    """True when the cited source artifact was updated after this entry was saved."""
    if not source:
        return False
    upd = _artifact_updated(source)
    return bool(upd and saved_at and upd > saved_at[:10])


def _ctx_db_path() -> str:
    root = Path(_project_root())
    ww = root / ".spindleloom"
    ww.mkdir(exist_ok=True)
    return str(ww / "context.db")


def _ctx_log_append(agent_id, task_id, facts, tags, saved_at, source):
    """Mirror every save to the append-only, git-committed context log. The JSONL log is
    the CROSS-MACHINE source of truth (SQLite is binary — git can't merge it; this can:
    appends rarely conflict and a conflict is a trivial keep-both). Teammates rebuild
    their local DB from it via `sloom context <root> --import` after a pull."""
    line = json.dumps({"agent_id": agent_id, "task_id": task_id, "facts": facts,
                       "tags": tags, "saved_at": saved_at, "source": source},
                      ensure_ascii=False)
    log = Path(_ctx_db_path()).parent / "context-log.jsonl"
    with open(log, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _ctx_con():
    con = sqlite3.connect(_ctx_db_path())
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS agent_context (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id      TEXT    NOT NULL,
            task_id       TEXT    NOT NULL DEFAULT '',
            facts         TEXT    NOT NULL,
            tags          TEXT    NOT NULL DEFAULT '',
            saved_at      TEXT    NOT NULL,
            chroma_synced INTEGER NOT NULL DEFAULT 1
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_ctx_task  ON agent_context(task_id)")
    try:  # lazy migration: entries may cite a source artifact for freshness checks
        con.execute("ALTER TABLE agent_context ADD COLUMN source TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists
    con.execute("CREATE INDEX IF NOT EXISTS idx_ctx_agent ON agent_context(agent_id)")
    # Migrate older DBs that predate the chroma_synced column
    try:
        con.execute("ALTER TABLE agent_context ADD COLUMN chroma_synced INTEGER NOT NULL DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # column already exists
    con.commit()
    return con


def _chroma_col():
    """Return the ChromaDB collection, or None when semantic search is not enabled."""
    if not _CHROMA():
        return None
    root = Path(_project_root())
    client = _chromadb.PersistentClient(path=str(root / ".spindleloom" / "chroma"))
    return client.get_or_create_collection(
        "agent_context",
        metadata={"hnsw:space": "cosine"},  # distance in [0,2]; score = 1-dist in [-1,1]
    )


@mcp.tool()
def save_context(agent_id: str, task_id: str, facts: str, tags: str = "", source: str = "") -> dict:
    """Save compressed handoff context so downstream agents recall it without re-reading
    full documents. Keep facts to <=5 bullets: decisions + reason, outputs + path,
    blockers, inherited constraints, open questions for the next agent. task_id groups
    facts for a feature/sprint (e.g. 'user-auth', 'sprint-3'). Deduplicates: if the
    same agent_id+task_id+facts already exists, returns the existing entry unchanged.
    Optional `source` cites the artifact path these facts summarize (e.g.
    'specs/auth/frd.md'): recall then flags the entry STALE if the registry shows the
    artifact was updated after the save — stale context becomes visible, not authoritative.
    Stored in SQLite + ChromaDB when installed (local semantic search, no API calls)."""
    con = _ctx_con()
    # Deduplication: skip if identical facts already saved for this agent+task
    existing = con.execute(
        "SELECT id, saved_at FROM agent_context WHERE agent_id=? AND task_id=? AND facts=?",
        (agent_id, task_id, facts),
    ).fetchone()
    if existing:
        return {"saved": True, "duplicate": True, "agent_id": agent_id, "task_id": task_id,
                "saved_at": existing["saved_at"], "semantic": _CHROMA()}

    saved_at = datetime.now(timezone.utc).isoformat()
    chroma_synced = 0 if _CHROMA() else 1  # 0 = pending Chroma write; 1 = done / not needed
    cur = con.execute(
        "INSERT INTO agent_context (agent_id, task_id, facts, tags, saved_at, chroma_synced, source)"
        " VALUES (?,?,?,?,?,?,?)",
        (agent_id, task_id, facts, tags, saved_at, chroma_synced, source),
    )
    con.commit()
    row_id = str(cur.lastrowid)
    try:  # the committed cross-machine mirror; a log failure never blocks the save
        _ctx_log_append(agent_id, task_id, facts, tags, saved_at, source)
    except OSError:
        pass

    col = _chroma_col()
    if col is not None:
        try:
            col.add(
                ids=[row_id],
                documents=[facts],
                metadatas=[{"agent_id": agent_id, "task_id": task_id,
                            "tags": tags, "saved_at": saved_at, "source": source}],
            )
            con.execute("UPDATE agent_context SET chroma_synced=1 WHERE id=?", (int(row_id),))
            con.commit()
        except Exception:
            pass  # SQLite write succeeded; Chroma failure non-fatal -- sync_contexts() repairs

    return {"saved": True, "duplicate": False, "agent_id": agent_id, "task_id": task_id,
            "saved_at": saved_at, "semantic": _CHROMA()}


@mcp.tool()
def recall_context(query: str, task_id: str = "", limit: int = 5) -> list:
    """Retrieve saved handoff facts from previous agents. query is a natural-language
    phrase or keywords; task_id scopes to one feature/sprint. When chromadb is installed
    returns semantically similar results (cosine score included); otherwise falls back to
    SQLite keyword search. Call at the START of a task before reading upstream docs."""
    col = _chroma_col()
    if col is not None and query:
        try:
            total = col.count()
            if total > 0:
                n = min(limit, total)
                kw = {"task_id": task_id} if task_id else None
                res = col.query(query_texts=[query], n_results=n, where=kw)
                ids, docs, metas, dists = (
                    res["ids"][0], res["documents"][0],
                    res["metadatas"][0], res["distances"][0],
                )
                return [
                    {"agent_id": m["agent_id"], "task_id": m["task_id"],
                     "facts": d, "tags": m["tags"], "saved_at": m["saved_at"],
                     "source": m.get("source", ""),
                     "stale": _stale(m.get("source", ""), m["saved_at"]),
                     "score": round(1.0 - dist, 4)}
                    for d, m, dist in zip(docs, metas, dists)
                ]
        except Exception:
            pass  # fall through to SQLite

    # SQLite keyword search -- relevance-ranked (keyword hit count), recency as tiebreak
    con = _ctx_con()
    inner_where = "WHERE task_id = ?" if task_id else ""
    inner_params = [task_id] if task_id else []

    if query:
        kws = query.lower().split()
        score_expr = " + ".join(
            f"(CASE WHEN lower(facts) LIKE ? OR lower(tags) LIKE ? THEN 1 ELSE 0 END)"
            for _ in kws
        )
        score_params = [p for kw in kws for p in (f"%{kw}%", f"%{kw}%")]
        rows = con.execute(
            f"SELECT agent_id, task_id, facts, tags, saved_at, source, relevance FROM ("
            f"  SELECT *, ({score_expr}) AS relevance"
            f"  FROM agent_context {inner_where}"
            f") WHERE relevance > 0 ORDER BY relevance DESC, saved_at DESC LIMIT ?",
            score_params + inner_params + [limit],
        ).fetchall()
        n_kws = len(kws)
        return [
            {"agent_id": r["agent_id"], "task_id": r["task_id"], "facts": r["facts"],
             "tags": r["tags"], "saved_at": r["saved_at"], "source": r["source"],
             "stale": _stale(r["source"], r["saved_at"]),
             "score": round(r["relevance"] / n_kws, 4)}
            for r in rows
        ]
    else:
        rows = con.execute(
            f"SELECT agent_id, task_id, facts, tags, saved_at, source FROM agent_context "
            f"{inner_where} ORDER BY saved_at DESC LIMIT ?",
            inner_params + [limit],
        ).fetchall()
        return [dict(r) | {"stale": _stale(r["source"], r["saved_at"])} for r in rows]


@mcp.tool()
def list_contexts(task_id: str = "", agent_id: str = "") -> list:
    """List saved context snapshots, optionally filtered by task_id and/or agent_id.
    Shows agent, task, timestamp, and a 120-char preview of the facts. Use to see what
    previous agents have recorded before starting work on a task."""
    con = _ctx_con()
    where, params = [], []
    if task_id:
        where.append("task_id = ?")
        params.append(task_id)
    if agent_id:
        where.append("agent_id = ?")
        params.append(agent_id)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    rows = con.execute(
        f"SELECT id, agent_id, task_id, substr(facts,1,120) AS facts_preview, "
        f"tags, saved_at FROM agent_context {clause} ORDER BY saved_at DESC LIMIT 200",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def get_context(agent_id: str, task_id: str) -> dict:
    """Retrieve the full facts for a specific agent's most recent saved context on a task.
    Use when list_contexts shows a truncated preview and you need the complete entry.
    Returns the latest snapshot for that agent+task combination."""
    con = _ctx_con()
    row = con.execute(
        "SELECT id, agent_id, task_id, facts, tags, saved_at FROM agent_context "
        "WHERE agent_id=? AND task_id=? ORDER BY saved_at DESC LIMIT 1",
        (agent_id, task_id),
    ).fetchone()
    if row is None:
        return {"found": False, "agent_id": agent_id, "task_id": task_id}
    return {"found": True, **dict(row)}


@mcp.tool()
def delete_context(task_id: str, agent_id: str = "") -> dict:
    """Delete saved context snapshots. Requires task_id (deletes all entries for that
    task/sprint). Optionally restrict to one agent with agent_id. Use at sprint
    boundaries or when a decision is superseded. Returns count of deleted entries."""
    con = _ctx_con()
    if agent_id:
        deleted = con.execute(
            "DELETE FROM agent_context WHERE task_id=? AND agent_id=?",
            (task_id, agent_id),
        ).rowcount
    else:
        deleted = con.execute(
            "DELETE FROM agent_context WHERE task_id=?", (task_id,),
        ).rowcount
    con.commit()

    col = _chroma_col()
    if col is not None and deleted > 0:
        try:
            existing = col.get(where={"task_id": task_id})
            if existing["ids"]:
                ids_to_del = (
                    [i for i, m in zip(existing["ids"], existing["metadatas"])
                     if m.get("agent_id") == agent_id]
                    if agent_id else existing["ids"]
                )
                if ids_to_del:
                    col.delete(ids=ids_to_del)
        except Exception:
            pass  # SQLite delete succeeded; Chroma cleanup is best-effort

    return {"deleted": deleted, "task_id": task_id, "agent_id": agent_id or None}


@mcp.tool()
def delete_context_entry(entry_id: int) -> dict:
    """Delete ONE saved context entry by its id (shown by list_contexts/get_context).
    Use to surgically remove a single bad/superseded note without wiping the task's
    or agent's whole set — for bulk cleanup use delete_context instead. Removes the
    matching ChromaDB document too (best-effort; sync_contexts repairs strays)."""
    con = _ctx_con()
    row = con.execute(
        "SELECT id, agent_id, task_id FROM agent_context WHERE id=?", (entry_id,)
    ).fetchone()
    if row is None:
        return {"deleted": False, "id": entry_id, "reason": "no entry with that id"}
    con.execute("DELETE FROM agent_context WHERE id=?", (entry_id,))
    con.commit()
    col = _chroma_col()
    if col is not None:
        try:
            col.delete(ids=[str(entry_id)])
        except Exception:
            pass  # SQLite delete succeeded; Chroma cleanup is best-effort
    return {"deleted": True, "id": entry_id,
            "agent_id": row["agent_id"], "task_id": row["task_id"]}


@mcp.tool()
def sync_contexts() -> dict:
    """Re-sync SQLite rows that failed to write to ChromaDB (chroma_synced=0). Only
    relevant when SPINDLELOOM_SEMANTIC=1 is set. Call after a Chroma outage or first
    enabling semantic mode on an existing DB to replay all missed rows."""
    if not _CHROMA():
        return {"semantic": False, "message": "ChromaDB not enabled -- nothing to sync"}
    con = _ctx_con()
    rows = con.execute(
        "SELECT id, agent_id, task_id, facts, tags, saved_at FROM agent_context "
        "WHERE chroma_synced=0"
    ).fetchall()
    if not rows:
        return {"semantic": True, "synced": 0, "message": "Already in sync"}
    col = _chroma_col()
    synced, failed = 0, 0
    for row in rows:
        try:
            col.add(
                ids=[str(row["id"])],
                documents=[row["facts"]],
                metadatas=[{"agent_id": row["agent_id"], "task_id": row["task_id"],
                            "tags": row["tags"], "saved_at": row["saved_at"]}],
            )
            con.execute("UPDATE agent_context SET chroma_synced=1 WHERE id=?", (row["id"],))
            synced += 1
        except Exception:
            failed += 1
    con.commit()
    return {"semantic": True, "synced": synced, "failed": failed}


@mcp.resource("rtm://current")
def rtm_resource() -> str:
    """The current RTM as structured JSON (columns, rows, decisions table)."""
    return json.dumps(rtm_core.parse_rtm(_root()), ensure_ascii=False, indent=2)


@mcp.resource("sloom://requirements")
def requirements_resource() -> str:
    """The full requirement list as JSON (every Req-ID + where defined)."""
    return json.dumps(rtm_core.list_requirements(_root()), ensure_ascii=False, indent=2)


@mcp.resource("sloom://artifacts")
def artifacts_resource() -> str:
    """The artifact catalog as JSON (every artifact + location/owner/status/version)."""
    return json.dumps(rtm_core.artifacts(_root()), ensure_ascii=False, indent=2)


@mcp.resource("sloom://decisions")
def decisions_resource() -> str:
    """The RTM decisions table (ADR/RFC ledger) as JSON."""
    return json.dumps(rtm_core.decisions(_root()), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
