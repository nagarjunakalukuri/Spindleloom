#!/usr/bin/env python3
"""
emit_backlog.py — Wheelwright: backlog.md -> work-tracker work items (the sync contract, run).

Closes the recurring "no backlog->Boards automation" gap. The `backlog-manager` **Tracker
sync contract** (which doc field maps to which work-item field) is encoded here as runnable
code, so a team stops hand-creating work items and hand-copying IDs back into the RTM.

Three pure, tracker-AGNOSTIC steps + one pluggable push:
  1. parse_backlog(md)  -> the ordered PBIs from the canonical "Backlog (ordered)" table.
  2. plan(md)           -> field-mapped work-item payloads. The sync contract, as code:
                           Story -> Description; **Acceptance criteria -> its OWN field
                           (NEVER folded into Description)**; Type -> Work Item Type;
                           MoSCoW -> Priority; Est -> Story Points; epic -> Parent;
                           Source -> a trace ref; Ready? -> a flag. Dry-run JSON you can
                           preview before anything hits the tracker.
  3. push (YOUR adapter): a callable plan -> {pbi_id: work_item_id}. The live Azure Boards /
                           Jira call lives in YOUR adapter (needs a host/PAT; varies by
                           tracker) — deliberately NOT bundled. Contract documented below.
  4. writeback(md, id_map) -> fill (or append) the **Azure** column of any markdown table
                           (the RTM or the backlog) keyed by PBI ID, recording the
                           source->tracker link the sync contract requires.

Dependency-free (Python 3 stdlib only). Steps 1/2/4 are fully testable offline; only the
adapter touches the network. See `backlog-manager` "Tracker sync contract" and
`project_guides/INFORMATION-ARCHITECTURE.md` "Directionality & drift".

Usage:
    python hooks/emit_backlog.py <backlog.md>                       # dry-run: work-item plan (JSON)
    python hooks/emit_backlog.py <backlog.md> --table               # readable plan table
    python hooks/emit_backlog.py writeback <table.md> <idmap.json>  # fill the Azure column (stdout)
    python hooks/emit_backlog.py writeback <table.md> <idmap.json> --apply   # ...write in place

Adapter contract (write ~20 lines against your tracker's REST/SDK):
    def push(plan, dry_run=True) -> dict[str, str]:
        # create/update one work item per plan["work_items"], returning {pbi_id: work_item_id}.
        # field map -> Azure Boards example:
        #   title               -> System.Title
        #   description         -> System.Description           (markdown)
        #   acceptance_criteria -> Microsoft.VSTS.Common.AcceptanceCriteria   (its OWN field!)
        #   work_item_type      -> System.WorkItemType
        #   priority            -> Microsoft.VSTS.Common.Priority
        #   story_points        -> Microsoft.VSTS.Scheduling.StoryPoints
        #   parent_epic         -> System.Parent (resolve the epic's id first)
        #   tags                -> System.Tags
        # then: writeback(rtm_md, push(plan))  to record the ids.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402  (reuse the stdlib markdown-table parser)

# MoSCoW -> tracker numeric priority (1 = highest). Tracker-configurable; this is the default.
_MOSCOW = {"must": 1, "should": 2, "could": 3, "won't": 4, "wont": 4, "would": 4}
# PBI Type -> canonical work-item type. Tracker-configurable.
_TYPE = {"story": "User Story", "code": "User Story", "bug": "Bug",
         "spike": "Task", "decision": "Task", "docs": "Task", "task": "Task"}

_PBI_FULL = re.compile(r"PBI-[A-Z0-9]+-\d+", re.IGNORECASE)
_READY = {"✅", "yes", "y", "true", "ready", "done"}


def _col_index(header):
    """Map the backlog table's header cells to canonical keys (case/spacing tolerant)."""
    idx = {}
    for i, h in enumerate(header):
        k = h.strip().lower()
        if "pbi" in k or k == "id":
            idx["id"] = i
        elif k.startswith("type"):
            idx["type"] = i
        elif "acceptance" in k:
            idx["ac"] = i
        elif k.startswith(("story", "item")):
            idx.setdefault("story", i)
        elif "priorit" in k:
            idx["priority"] = i
        elif k.startswith("est") or k in ("pts", "points") or k.startswith("point"):
            idx["est"] = i
        elif k.startswith("dep"):
            idx["deps"] = i
        elif k.startswith("source"):
            idx["source"] = i
        elif "ready" in k:
            idx["ready"] = i
    return idx


def parse_backlog(md):
    """Extract the ordered PBIs from the canonical "Backlog (ordered)" table. Tolerant of
    column order; needs at least a PBI-ID column and a Story/item column. Returns raw cell
    values per PBI (mapping to work items is `to_work_item`)."""
    pbis = []
    for t in rtm_core.parse_tables(md):
        idx = _col_index(t["header"])
        if "id" not in idx or "story" not in idx:
            continue
        for row in t["rows"]:
            def cell(key):
                i = idx.get(key)
                return row[i].strip() if (i is not None and i < len(row)) else ""
            m = _PBI_FULL.search(cell("id"))
            if not m:
                continue
            pid = m.group(0).upper()
            pbis.append({
                "id": pid,
                "epic": pid.split("-")[1],
                "type": cell("type") or "Story",
                "story": cell("story"),
                "acceptance_criteria": cell("ac"),
                "priority": cell("priority"),
                "est": cell("est"),
                "deps": cell("deps"),
                "source": cell("source"),
                "ready": cell("ready"),
            })
    return pbis


def _title(pbi):
    s = " ".join(pbi["story"].split())
    if len(s) > 80:
        s = s[:77].rstrip() + "…"
    return f"{pbi['id']} — {s}" if s else pbi["id"]


def to_work_item(pbi):
    """Map one parsed PBI to a tracker-agnostic work-item payload per the Tracker sync
    contract. AC lands in its OWN field; it is NEVER concatenated into the description."""
    moscow = re.sub(r"[^a-z']", "", (pbi["priority"] or "").lower())
    est = re.search(r"\d+(?:\.\d+)?", pbi["est"] or "")
    return {
        "pbi_id": pbi["id"],
        "work_item_type": _TYPE.get((pbi["type"] or "").strip().lower(), "User Story"),
        "title": _title(pbi),
        "description": pbi["story"],
        "acceptance_criteria": pbi["acceptance_criteria"],  # OWN field — never in description
        "priority": _MOSCOW.get(moscow),
        "story_points": float(est.group(0)) if est else None,
        "parent_epic": pbi["epic"],
        "source_ref": pbi["source"],
        "ready": (pbi["ready"] or "").strip().lower() in _READY or (pbi["ready"] or "").strip() in _READY,
        "tags": [pbi["epic"].lower()] if pbi["epic"] else [],
    }


def plan(md):
    """Field-mapped work-item payloads for a backlog markdown — the dry-run preview of what
    `push` would create. Emits warnings for DoR misses (no AC, unmapped priority)."""
    items = [to_work_item(p) for p in parse_backlog(md)]
    warnings = []
    for it in items:
        if not it["acceptance_criteria"]:
            warnings.append(f"{it['pbi_id']}: no acceptance criteria (DoR: not Ready)")
        if it["priority"] is None and it["work_item_type"] != "Task":
            warnings.append(f"{it['pbi_id']}: priority not mapped from MoSCoW")
    return {"count": len(items), "work_items": items, "warnings": warnings}


# ---------------------------------------------------------------- write-back (ids -> RTM/backlog)

def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_sep(line):
    body = line.replace("|", "").replace(":", "").strip()
    return bool(body) and set(body) <= {"-", " "}


def _writeback_block(block, id_map):
    """Fill/append the 'Azure' column of one pipe-table block. Rows whose PBI ID(s) are in
    id_map get the work-item id(s); others are untouched. Returns rewritten lines."""
    if len(block) < 2 or not _is_sep(block[1]):
        return block
    header = _cells(block[0])
    az = next((i for i, h in enumerate(header) if "azure" in h.strip().lower()), None)
    appended = az is None
    if appended:
        az = len(header)
        header.append("Azure (work-item id)")
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for line in block[2:]:
        cells = _cells(line)
        ids = [id_map[i] for i in {m.group(0).upper() for m in _PBI_FULL.finditer(line)} if i in id_map]
        while len(cells) <= az:
            cells.append("")
        if ids:
            cells[az] = ", ".join(sorted(ids))
        out.append("| " + " | ".join(cells) + " |")
    return out


def writeback(md, id_map):
    """Fill (or append) an 'Azure' column in every markdown pipe-table in `md`, keyed by PBI
    ID. `id_map`: {PBI-ID: work-item-id}. Idempotent; only sets cells for ids in the map.
    Returns the updated markdown — the source->tracker link the sync contract requires."""
    id_map = {k.upper(): v for k, v in id_map.items()}
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and _is_sep(lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            out.extend(_writeback_block(lines[i:j], id_map))
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


# ---------------------------------------------------------------- CLI

def _print_table(p):
    print(f"{'PBI':22} {'TYPE':11} {'PRI':3} {'PTS':4} {'AC':3} PARENT")
    for it in p["work_items"]:
        print(f"{it['pbi_id']:22} {it['work_item_type']:11} "
              f"{str(it['priority'] or '-'):3} {str(it['story_points'] or '-'):4} "
              f"{'Y' if it['acceptance_criteria'] else '·':3} {it['parent_epic']}")
    for w in p["warnings"]:
        print("  warn:", w)
    print(f"  {p['count']} work item(s); {len(p['warnings'])} warning(s). Dry-run — wire an adapter to push.")


def main(argv):
    if len(argv) >= 2 and argv[1] == "writeback":
        if len(argv) < 4:
            print("usage: emit_backlog.py writeback <table.md> <idmap.json> [--apply]")
            return 2
        table_p, idmap_p = Path(argv[2]), Path(argv[3])
        id_map = json.loads(idmap_p.read_text(encoding="utf-8"))
        updated = writeback(table_p.read_text(encoding="utf-8"), id_map)
        if "--apply" in argv:
            table_p.write_text(updated, encoding="utf-8")
            print(f"writeback: filled Azure column for {len(id_map)} id(s) in {table_p}")
        else:
            sys.stdout.write(updated)
        return 0

    if len(argv) < 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\nusage: emit_backlog.py <backlog.md> [--table] | writeback <table.md> <idmap.json> [--apply]")
        return 2
    md = Path(argv[1]).read_text(encoding="utf-8")
    p = plan(md)
    if "--table" in argv:
        _print_table(p)
    else:
        print(json.dumps(p, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
