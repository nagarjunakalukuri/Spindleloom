#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_counts.py -- fail if any human-facing doc states a stale fleet count.

The fleet's headline numbers (agents / templates / skills / commands) live in the
folders; docs restate them in prose and drift (this gate exists because they had).
Counts are computed the same way validate_graph.py reports them, then a curated set
of doc surfaces is scanned.

A count is validated only when it is unambiguously a HEADLINE TOTAL:
  - an explicit headline phrasing ("N role-specialist agents", "N methodology skills",
    "N reusable/document templates", "N slash commands"), or
  - a bare noun on an ENUMERATION line -- one counting agents together with at least
    one other kind (the "52 agents, 51 templates, 28 skills, 23 commands" summaries).
A line mentioning a single kind is a subcount ("Discover: 7 agents") and is skipped.

Usage:
    python hooks/validate_counts.py            # report
    python hooks/validate_counts.py --check     # exit 1 on mismatch (CI/pre-commit)

Stdlib-only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def real_counts():
    agents = len([p for p in (ROOT / "agents").glob("*.md") if p.name not in ("INDEX.md", "HELP.md")])
    templates = len(list((ROOT / "templates").glob("*.md")))
    skills = len({p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")})
    commands = len(list((ROOT / "commands").glob("*.md")))
    return {"agents": agents, "templates": templates, "skills": skills, "commands": commands}


FILES = [
    "README.md", "PROJECT-OVERVIEW.md", "CLAUDE.md", "CONTRIBUTING.md", "ONBOARDING.md", "INSTALL.md",
    "knowledge_hub/README.md", "spindleloom_website/project-overview.html", "spindleloom_website/for-everyone.html",
]

NOUNS = [
    ("role-specialist ai agents", "agents"), ("role-specialist agents", "agents"),
    ("ai agents", "agents"), ("agents", "agents"),
    ("reusable templates", "templates"), ("document templates", "templates"), ("templates", "templates"),
    ("methodology skills", "skills"), ("skills", "skills"),
    ("slash commands", "commands"), ("slash-commands", "commands"), ("commands", "commands"),
]
NOUN_ALT = "|".join(re.escape(n) for n, _ in NOUNS)
PAT = re.compile(r"(\d+)[\s-]{1,3}(" + NOUN_ALT + r")\b", re.I)
HEADLINE = re.compile(r"(role-specialist agents|role-specialist ai agents|reusable templates|document templates|methodology skills|slash commands|slash-commands)", re.I)


def _key(noun):
    return next(k for n, k in NOUNS if n == noun.lower())


def scan():
    counts = real_counts()
    problems = []
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        for lineno, line in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            matches = [(int(m.group(1)), _key(m.group(2)), m.group(0).strip()) for m in PAT.finditer(line)]
            kinds = {k for _, k, _ in matches}
            enumeration = "agents" in kinds and len(kinds) >= 2
            for num, key, frag in matches:
                is_headline = enumeration or HEADLINE.search(frag)
                if is_headline and num != counts[key]:
                    problems.append((rel, lineno, frag, key, counts[key]))
    return counts, problems


def main():
    check = "--check" in sys.argv[1:]
    counts, problems = scan()
    hdr = "counts: agents %(agents)d | templates %(templates)d | skills %(skills)d | commands %(commands)d" % counts
    if not problems:
        print("validate_counts: OK -- " + hdr)
        return 0
    print("validate_counts: %d stale count(s) -- %s\n" % (len(problems), hdr))
    for rel, lineno, frag, key, expected in problems:
        print("  %s:%d  \"%s\" -> should be %d %s" % (rel, lineno, frag, expected, key))
    if check:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
