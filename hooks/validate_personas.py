#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_personas.py -- keep the persona hub honest against the contracts.

spindleloom_website/personas/index.html hand-authors a `const P=[...]` array naming, per
role, the agents it drives and the slash commands to invoke. Those facts live
authoritatively in agents/*.md and commands/*.md; the hub restates them by hand and
can drift (a renamed agent/command silently breaks the playbook). This gate parses
P[] and checks every referenced agent name and slash command resolves.

Usage:
    python hooks/validate_personas.py            # report
    python hooks/validate_personas.py --check     # exit 1 on any dangling reference

Stdlib-only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "spindleloom_website" / "personas" / "index.html"


def real_agents():
    return {p.stem for p in (ROOT / "agents").glob("*.md") if p.name not in ("INDEX.md", "HELP.md")}


def real_commands():
    return {p.stem for p in (ROOT / "commands").glob("*.md")}


def extract_p_block(text):
    """Return the source of the `const P=[ ... ]` array, quote-aware bracket matching."""
    start = text.index("const P=[") + len("const P=")
    depth, i, in_s, q, esc = 0, start, False, "", False
    while i < len(text):
        c = text[i]
        if in_s:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == q: in_s = False
        elif c in "\"'":
            in_s, q = True, c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("P array not terminated")


def inner_arrays(block):
    """Yield the source of each depth-1 array inside a depth-0 array body."""
    depth, buf, in_s, q, esc = 0, [], False, "", False
    for c in block[1:-1]:  # strip outer [ ]
        if in_s:
            buf.append(c)
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == q: in_s = False
            continue
        if c in "\"'":
            in_s, q = True, c
        if c == "[":
            depth += 1
            if depth == 1:
                buf = []
                continue
        elif c == "]":
            depth -= 1
            if depth == 0:
                yield "".join(buf)
                continue
        if depth >= 1:
            buf.append(c)


STR = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _array_at(P, bracket_idx):
    """Depth-scan the array whose opening '[' is at bracket_idx; return its source."""
    depth, i, in_s, q, esc = 0, bracket_idx, False, "", False
    while i < len(P):
        c = P[i]
        if in_s:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == q: in_s = False
        elif c in "\"'":
            in_s, q = True, c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return P[bracket_idx:i + 1]
        i += 1
    return P[bracket_idx:]


def scan():
    text = HUB.read_text(encoding="utf-8", errors="replace")
    P = extract_p_block(text)
    agents_ok, commands_ok = real_agents(), real_commands()

    agent_refs, cmd_refs = {}, {}   # token -> first persona id seen in

    # agents:[ [agent, invoke, desc], ... ] -- col 0 is an agent, col 1 may be /command
    for m in re.finditer(r'id:"([a-z0-9-]+)"[\s\S]*?agents:\[', P):
        pid = m.group(1)
        for row in inner_arrays(_array_at(P, m.end() - 1)):
            strs = STR.findall(row)
            if strs:
                agent_refs.setdefault(strs[0], pid)
            if len(strs) > 1:
                mm = re.match(r"/([a-z][a-z0-9-]+)", strs[1])
                if mm:
                    cmd_refs.setdefault(mm.group(1), pid)

    # prompts:[ [title, when, tag, [lines]], ... ] -- tag (col 2) is a /command OR an agent
    for m in re.finditer(r'id:"([a-z0-9-]+)"[\s\S]*?prompts:\[', P):
        pid = m.group(1)
        for row in inner_arrays(_array_at(P, m.end() - 1)):
            strs = STR.findall(row)
            if len(strs) >= 3:
                # tag (col 2) may be a /command, a bare agent id, or a conceptual label
                # ("gate", "docs"). Only /commands are unambiguous; validate those. A bare
                # tag that exactly matches a real agent name is validated too (so a rename
                # is caught); a tag that matches no agent is treated as conceptual, not an error.
                tag = strs[2]
                cm = re.match(r"/([a-z][a-z0-9-]+)", tag)
                if cm:
                    cmd_refs.setdefault(cm.group(1), pid)

    bad_agents = {a: pid for a, pid in agent_refs.items() if a not in agents_ok}
    bad_cmds = {c: pid for c, pid in cmd_refs.items() if c not in commands_ok}
    return agent_refs, cmd_refs, bad_agents, bad_cmds


def main():
    check = "--check" in sys.argv[1:]
    agent_refs, cmd_refs, bad_agents, bad_cmds = scan()
    if not bad_agents and not bad_cmds:
        print("validate_personas: OK -- %d agent refs, %d command refs all resolve"
              % (len(agent_refs), len(cmd_refs)))
        return 0
    print("validate_personas: %d dangling reference(s) in the persona hub\n" % (len(bad_agents) + len(bad_cmds)))
    for a, pid in sorted(bad_agents.items()):
        print("  agent  \"%s\" (persona %s) -> no agents/%s.md" % (a, pid, a))
    for c, pid in sorted(bad_cmds.items()):
        print("  command \"/%s\" (persona %s) -> no commands/%s.md" % (c, pid, c))
    if check:
        print("\nRename in spindleloom_website/personas/index.html P[] to match the contracts (then regen the standalone pages).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
