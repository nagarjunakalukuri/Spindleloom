#!/usr/bin/env python3
"""
add_examples.py — inject an `examples:` block into each agent's frontmatter.

Takes a JSON file of the form {"examples": [{"name": "...", "examples": ["...", "..."]}, ...]}
(the output of the author-agent-examples workflow) and writes a machine-readable
`examples:` list into each `agents/<name>.md` frontmatter, just after `model:`.

Additive and idempotent: re-running replaces any existing `examples:` block; nothing
else in the file changes. Dependency-free (stdlib only).

Usage:
    python hooks/add_examples.py <examples.json> [agents-dir]
"""
import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path


def yaml_dq(s):
    """Double-quoted YAML scalar — unambiguous for prompts containing ' or "."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_existing(fm):
    """Drop an existing `examples:` block (the key line + its indented `- ` items)."""
    out, skipping = [], False
    for ln in fm:
        if skipping:
            if ln.startswith((" ", "\t")) and ln.lstrip().startswith("-"):
                continue
            skipping = False
        if ln.strip() == "examples:" or ln.lstrip().startswith("examples:"):
            skipping = True
            continue
        out.append(ln)
    return out


def insert_after(fm, examples):
    block = ["examples:"] + [f"  - {yaml_dq(e)}" for e in examples]
    for key in ("model:", "tools:", "description:"):
        for i, ln in enumerate(fm):
            if ln.lstrip().startswith(key):
                return fm[: i + 1] + block + fm[i + 1:]
    return fm + block  # no anchor found — append to frontmatter


def main(argv):
    if len(argv) < 2:
        print("usage: add_examples.py <examples.json> [agents-dir]")
        return 2
    data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    entries = data.get("examples", data) if isinstance(data, dict) else data
    agents_dir = Path(argv[2]) if len(argv) > 2 else Path("agents")
    if not agents_dir.is_dir():
        agents_dir = Path("spindleloom/agents")

    changed, missing = 0, []
    for e in entries:
        name, examples = e["name"], e["examples"]
        f = agents_dir / f"{name}.md"
        if not f.is_file():
            missing.append(name)
            continue
        text = f.read_text(encoding="utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split("\n")
        lines = [ln.rstrip("\r") for ln in lines]
        if lines[0].strip() != "---":
            missing.append(name + " (no frontmatter)")
            continue
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            missing.append(name + " (unterminated frontmatter)")
            continue
        fm = insert_after(strip_existing(lines[1:end]), examples)
        new_lines = ["---"] + fm + ["---"] + lines[end + 1:]
        f.write_text(nl.join(new_lines), encoding="utf-8")
        changed += 1

    print(f"add_examples: injected examples into {changed} agents"
          + (f"; MISSING: {', '.join(missing)}" if missing else ""))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
