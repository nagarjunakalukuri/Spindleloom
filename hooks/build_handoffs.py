#!/usr/bin/env python3
"""build_handoffs.py — inject a uniform "Handoff" line into every agent body.

The contract block (frontmatter) already declares inputs/outputs/upstream/downstream,
but that's metadata the index reads — not prose the model follows. This surfaces the
same before/after handoff as a one-line blockquote at the top of each agent body, so
an agent invoked in isolation knows what to read first and where to hand off. Generated
from the contract block (single source of truth) and idempotent — re-run after any
contract change; `validate_graph.py` checks the line stays in sync.

Usage:
    python hooks/build_handoffs.py            # rewrite all agents
    python hooks/build_handoffs.py --check    # exit 1 if any agent is missing/stale (no writes)
Dependency-free (stdlib only).
"""
import re
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"
MARKER = "> **Handoff**"


def split_frontmatter(text):
    """Return (head_including_closing_---, body) or (None, None) if no frontmatter."""
    if not text.startswith("---"):
        return None, None
    end = text.find("\n---", 3)
    if end == -1:
        return None, None
    return text[: end + 4], text[end + 4:]


def scalar(block, key):
    m = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", block)
    return m.group(1).strip().strip('"') if m else ""


def inline_list(block, key):
    raw = scalar(block, key)
    if not raw or raw in ("[]", "—"):
        return []
    return [x.strip().strip('"') for x in raw.strip("[]").split(",") if x.strip()]


def code(items):
    return ", ".join(f"`{x}`" for x in items)


def handoff_line(block):
    inputs = inline_list(block, "inputs")
    outputs = scalar(block, "outputs")
    upstream = inline_list(block, "upstream")
    downstream = inline_list(block, "downstream")

    # Before
    if inputs and upstream:
        before = f"read {', '.join(inputs)} (from {code(upstream)})"
    elif inputs:
        before = f"read {', '.join(inputs)} (top of funnel — no upstream agent)"
    elif upstream:
        before = f"take the handoff from {code(upstream)}"
    else:
        before = "start from the request (top of funnel)"

    # After
    out = outputs if outputs and outputs != "—" else "your output"
    if downstream:
        after = f"produce {out} → hand to {code(downstream)}"
    else:
        after = f"produce {out} (terminal — no downstream agent)"

    return f"{MARKER} · *Before:* {before}. *After:* {after}. *(Flag discoveries back upstream — see `knowledge_hub/BEST-PRACTICES.md`.)*"


def main(argv):
    check = "--check" in argv
    files = sorted(p for p in AGENTS.glob("*.md") if p.name not in ("INDEX.md", "HELP.md"))
    stale, written = [], 0
    for p in files:
        text = p.read_text(encoding="utf-8")
        head, body = split_frontmatter(text)
        if head is None:
            stale.append(f"{p.name}: no frontmatter")
            continue
        line = handoff_line(head)
        # strip any existing handoff line (+ following blank) from the top of the body
        body_clean = re.sub(rf"(?m)^{re.escape(MARKER)}.*\n\n?", "", body).lstrip("\n")
        desired = head + "\n\n" + line + "\n\n" + body_clean
        if desired != text:
            if check:
                stale.append(p.name)
            else:
                p.write_text(desired, encoding="utf-8")
                written += 1

    if check:
        if stale:
            print(f"FAIL — {len(stale)} agent(s) missing/stale handoff line (run build_handoffs.py):")
            for s in sorted(stale):
                print("  -", s)
            return 1
        print(f"OK — all {len(files)} agents have a current handoff line.")
        return 0
    print(f"build_handoffs: updated {written}/{len(files)} agents.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
