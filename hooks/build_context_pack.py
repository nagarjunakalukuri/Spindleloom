#!/usr/bin/env python3
"""build_context_pack.py — assemble the minimal context manifest for one agent + task.

Context engineering, mechanized: instead of "read the docs folder", a dispatcher (the
run-orchestrator or a human) hands an agent a PACK — exactly what its contract routes to
it, sliced to the feature at hand:

  1. the agent's contract `inputs:` resolved to real artifact paths (registry-stamped
     with Status / Last-updated, and each doc's `## Digest` when present),
  2. the feature's RTM slice (only rows citing the feature's IDs),
  3. saved handoff-context entries for the task_id (stale-flagged via the registry),
  4. open ASSUMPTION-n tags in the scoped docs (unratified facts the agent must not
     treat as decided),
  5. a size estimate vs the budget, with demotion advice when over.

Usage:
    python hooks/build_context_pack.py <project-root> <agent> [--feature <slug>]
        [--task-id <slug>] [--budget <chars>] [--write]
`--write` also saves the manifest to <tool-dir>/context-packs/<agent>[-<slug>].md.
Stdlib-only; read-only except under the tool dir with --write.
"""
import json
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402

DEFAULT_BUDGET = 60_000  # chars of full-read material (~15k tokens) before demotion advice
ASSUMPTION = re.compile(r"\bASSUMPTION-[A-Z0-9-]*\d+\b")
DIGEST = re.compile(r"(?ms)^## Digest\s*\n(.*?)(?=^## |\Z)")


def agent_contract(agent):
    """The agent's declared inputs, from its definition (toolkit or bundled copy)."""
    for base in (Path(__file__).resolve().parent.parent / "agents",
                 Path("agents"), Path(".claude") / "agents"):
        p = base / f"{agent}.md"
        if p.is_file():
            fm = p.read_text(encoding="utf-8", errors="ignore")
            fm = fm[3:fm.find("\n---", 3)]
            m = re.search(r"(?m)^inputs: \[(.*)\]$", fm)
            return [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []
    return None


def registry(root):
    reg = Path(rtm_core.tool_dir(root)) / "artifacts.json"
    if not reg.exists():
        return []
    try:
        data = json.loads(reg.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, list) else data.get("artifacts", [])
    except ValueError:
        return []


def match_inputs(inputs, arts, docs_root, feature):
    """Resolve declared input names to on-disk artifacts (registry first, then scan)."""
    hits = []
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
    known = {a["path"]: a for a in arts}
    files = rtm_core.markdown_files(docs_root)
    for inp in inputs:
        toks = set(norm(inp))
        found = None
        for f in files:
            rel = f.relative_to(docs_root).as_posix()
            if feature and f"/{feature}/" not in f"/{rel}" and feature not in rel:
                pass  # non-feature files still eligible (durable docs)
            stem_toks = set(norm(Path(rel).stem))
            if toks & stem_toks or any(t in Path(rel).stem.lower() for t in toks if len(t) > 2):
                # prefer the feature-scoped match when both exist
                if found is None or (feature and feature in rel):
                    found = rel
        meta = known.get(found, {})
        hits.append({"input": inp, "path": found,
                     "status": meta.get("status", "—"), "updated": meta.get("updated", "—")})
    return hits


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    root = Path(argv[1])
    agent = argv[2]
    feature = argv[argv.index("--feature") + 1] if "--feature" in argv else ""
    task_id = argv[argv.index("--task-id") + 1] if "--task-id" in argv else (feature or "")
    budget = int(argv[argv.index("--budget") + 1]) if "--budget" in argv else DEFAULT_BUDGET
    write = "--write" in argv

    inputs = agent_contract(agent)
    if inputs is None:
        print(f"build_context_pack: no agent definition found for '{agent}'")
        return 2
    docs_root = rtm_core.resolve_docs_root(root)
    arts = registry(root)

    out = [f"# Context pack — {agent}" + (f" · {feature}" if feature else ""),
           "", f"> Assembled by `build_context_pack.py`. Read in this order; "
           f"demote to digest/query anything the budget note flags.", ""]

    # 1. contract inputs -> artifacts (+ digests)
    out.append("## 1 · Contract inputs (your full-read set)")
    total = 0
    resolved = match_inputs(inputs, arts, docs_root, feature)
    for h in resolved:
        if h["path"]:
            p = docs_root / h["path"]
            size = p.stat().st_size if p.exists() else 0
            total += size
            out.append(f"- **{h['input']}** → `{h['path']}` (status {h['status']}, "
                       f"updated {h['updated']}, {size:,} chars)")
            dg = DIGEST.search(p.read_text(encoding="utf-8", errors="ignore")) if p.exists() else None
            if dg:
                for ln in dg.group(1).strip().splitlines()[:5]:
                    out.append(f"    {ln.strip()}")
        else:
            out.append(f"- **{h['input']}** → *not found on disk* — flag the missing handoff "
                       f"before inventing its content")
    out.append("")

    # 2. RTM slice
    rtm = docs_root / rtm_core.RTM_NAME
    out.append("## 2 · RTM slice" + (f" (rows citing '{feature}')" if feature else " (skip full RTM; trace only your IDs)"))
    if rtm.exists() and feature:
        rows = [ln for ln in rtm.read_text(encoding="utf-8", errors="ignore").splitlines()
                if ln.startswith("|") and feature.upper().replace("-", "") in re.sub(r"[^A-Z0-9]", "", ln.upper())]
        for ln in rows[:20]:
            out.append(ln)
        if not rows:
            out.append(f"- no RTM rows mention '{feature}' yet — your IDs will seed them")
    elif not rtm.exists():
        out.append("- RTM.md missing — run hooks/build_rtm.py (traceability is unprovable without it)")
    out.append("")

    # 3. saved handoff context (stale-flagged)
    out.append(f"## 3 · Saved handoff context (task_id: {task_id or '—'})")
    db = Path(rtm_core.tool_dir(root)) / "context.db"
    if db.is_file() and task_id:
        try:
            con = sqlite3.connect(db)
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT agent_id, facts, saved_at, "
                               "COALESCE(source,'') AS source FROM agent_context "
                               "WHERE task_id=? ORDER BY saved_at DESC LIMIT 8", (task_id,)).fetchall()
            con.close()
            for r in rows:
                upd = None
                for a in arts:
                    if a.get("path") == r["source"]:
                        upd = a.get("updated")
                stale = " ⚠ STALE — source changed since save" if (upd and upd > r["saved_at"][:10]) else ""
                out.append(f"- [{r['agent_id']} @ {r['saved_at'][:10]}]{stale}")
                for ln in r["facts"].strip().splitlines()[:5]:
                    out.append(f"    {ln.strip()}")
            if not rows:
                out.append("- none — you are first; save yours before handing off")
        except sqlite3.Error as e:
            out.append(f"- context.db unreadable: {e}")
    else:
        out.append("- no context store yet — recall skipped; save yours before handing off")
    out.append("")

    # 4. open assumptions in the scoped docs
    tags = set()
    for h in resolved:
        if h["path"]:
            tags |= set(ASSUMPTION.findall((docs_root / h["path"]).read_text(encoding="utf-8", errors="ignore")))
    out.append("## 4 · Open assumptions in scope (unratified — do not treat as decided)")
    out.append("- " + ", ".join(sorted(tags)) if tags else "- none found in your inputs")
    out.append("")

    # 5. budget verdict
    out.append("## 5 · Budget")
    if total > budget:
        biggest = max((h for h in resolved if h["path"]),
                      key=lambda h: (docs_root / h["path"]).stat().st_size, default=None)
        out.append(f"- full-read set is {total:,} chars vs budget {budget:,} — OVER. "
                   f"Demote `{biggest['path'] if biggest else '?'}` to digest + traced-sections; "
                   f"query the rest via search_specs/trace_requirement.")
    else:
        out.append(f"- full-read set {total:,} chars, within budget {budget:,}.")

    manifest = "\n".join(out) + "\n"
    print(manifest)
    if write:
        dest = Path(rtm_core.tool_dir(root)) / "context-packs"
        dest.mkdir(parents=True, exist_ok=True)
        name = f"{agent}{('-' + feature) if feature else ''}.md"
        (dest / name).write_text(manifest, encoding="utf-8")
        print(f"build_context_pack: wrote {dest / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
