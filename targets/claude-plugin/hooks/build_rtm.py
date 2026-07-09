#!/usr/bin/env python3
"""build_rtm.py — deterministically seed/refresh docs/RTM.md from the IDs on disk.

The RTM convention says the BRD seeds the matrix and every writer appends its rows —
but that relies on agent discipline, and a run that mints IDs without materializing
RTM.md fails `validate_reqs` (NO-RTM). This tool closes the gap mechanically:

  - scans the docs root (via rtm_core) for every `<DOC>-<AREA>-<NUM>` Req-ID,
  - creates RTM.md if absent (header + one row per ID: id, kind, defining file,
    empty Downstream / Test / Status cells for humans/agents to fill),
  - on an existing RTM.md, appends rows ONLY for IDs not already present —
    existing rows are never modified or reordered (append-only, idempotent).

Usage:
    python hooks/build_rtm.py <project-root>          # seed/refresh
    python hooks/build_rtm.py <project-root> --check  # exit 1 if IDs are missing from RTM.md
Stdlib-only; writes only <docs_root>/RTM.md.
"""
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402

HEADER = """# RTM — Requirements Traceability Matrix

| Field | Value |
|---|---|
| Owner | <PM / BA> |
| Status | Living |
| Last updated | <YYYY-MM-DD> |

> Seeded by `hooks/build_rtm.py` from the Req-IDs on disk; agents and humans fill the
> Downstream / Test / Status columns. Re-run the tool after adding documents — it
> appends missing IDs and never touches existing rows. Both RTM shapes are sanctioned:
> row-per-ID (this seed) or a matrix keyed on the top altitude with per-doc columns —
> an ID counts as present wherever it appears. Write IDs out in full: range shorthand
> (`PBI-X-004..006`) is invisible to every validator.

| Req-ID | Kind | Defined in | Downstream | Test | Status |
|---|---|---|---|---|---|
"""

# Presence = the ID appears ANYWHERE in RTM.md (matrix-shaped RTMs put IDs in any
# column, not just the first) — same semantics as rtm_core's coverage grep.
ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,7}-[A-Z0-9]{2,12}-\d{1,4})\b")


def collect_ids(root):
    """Every Req-ID and the file that defines it, from the docs root."""
    docs_root = rtm_core.resolve_docs_root(root)
    found = {}
    for p in sorted(docs_root.rglob("*.md")):
        if any(seg.startswith(".") for seg in p.parts):
            continue
        if p.name == "RTM.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,7}-[A-Z0-9]{2,12}-\d{1,4})\b", text):
            found.setdefault(m.group(1), p.relative_to(docs_root))
    return docs_root, found


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    check = "--check" in argv
    docs_root, ids = collect_ids(root)
    rtm = docs_root / "RTM.md"

    existing = set()
    if rtm.exists():
        existing = set(ID_RE.findall(rtm.read_text(encoding="utf-8", errors="ignore")))
    missing = sorted(i for i in ids if i not in existing)

    if check:
        if missing:
            print(f"build_rtm --check: {len(missing)} Req-ID(s) not in {rtm}:")
            for i in missing[:20]:
                print(f"  - {i} (defined in {ids[i]})")
            return 1
        print(f"build_rtm --check: OK — all {len(ids)} Req-IDs present in {rtm}")
        return 0

    rows = "".join(
        f"| `{i}` | {i.split('-')[0]} | `{ids[i]}` |  |  |  |\n" for i in missing
    )
    if not rtm.exists():
        rtm.write_text(HEADER + rows, encoding="utf-8")
        print(f"build_rtm: created {rtm} with {len(missing)} seeded row(s)")
    elif missing:
        with rtm.open("a", encoding="utf-8") as f:
            f.write(rows)
        print(f"build_rtm: appended {len(missing)} missing row(s) to {rtm}")
    else:
        print(f"build_rtm: {rtm} already covers all {len(ids)} Req-IDs — nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
