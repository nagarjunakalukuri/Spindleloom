#!/usr/bin/env python3
"""validate_graph.py — integrity checks for the agent fleet (CI-friendly).

The toolkit preaches docs-as-code + CI gates; this makes it eat its own dog food.
Run it after adding/editing/removing an agent (and in CI) so the fleet can't
silently rot. Dependency-free (Python 3 stdlib only); read-only.

Checks (exit 1 if any fail):
  1. Contract-graph symmetry — every `downstream` edge is reciprocated in the
     target's `upstream`, and every `upstream` edge in the source's `downstream`.
  2. Dangling agent refs — an upstream/downstream name with no matching agent file.
  3. Skills declared but missing — a `skills:` entry with no skills/<name>/SKILL.md.
  4. INDEX freshness — agents/INDEX.md has one row per agent (run
     build_agent_index.py if stale).
  5. Handoff line — each agent body carries its `> **Handoff**` line.
  6. Example prompts — each agent declares an `examples:` block.
  7. Claude Code mapping integrity — each agent's `claude_code:` block names a
     `subagent_type` that resolves to an agent, and any `command:` it references
     exists in commands/<name>.md. This is the layer that makes the fleet work
     inside Claude Code, so it can't be allowed to dangle.
  8. Command well-formedness — each commands/<name>.md declares a `description`
     (Claude Code surfaces it in the slash-command picker).
  9. Skill auto-fire — any skill armed by an agent's `skills:` list is
     model-invoked (no `disable-model-invocation: true`), so it can actually fire.
 10. Orphans — an agent in no other agent's `downstream` (nothing hands off to
     it), excluding the foundational entry agents (invoked directly).
Also prints the live agent/template/skill/command counts (advisory — update README
and project-overview.html / how-to-use.html to match; section sub-counts are not checked).

Usage:
    python hooks/validate_graph.py        # from the project_managment_agents root
Exit 0 = clean, 1 = issues found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
TEMPLATES = ROOT / "templates"
SKILLS = ROOT / "skills"
COMMANDS = ROOT / "commands"


def frontmatter(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def inline_list(block, key):
    m = re.search(rf"(?m)^{key}:\s*\[(.*?)\]\s*$", block)
    if not m:
        return []
    return [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]


def block_items(block, key):
    """Items of a YAML block list (key:\\n  - ...)."""
    items, collecting = [], False
    for ln in block.split("\n"):
        if collecting:
            if re.match(r"\s+-\s+\S", ln):
                items.append(ln.strip())
                continue
            if ln.strip() and not ln[:1].isspace():
                break
        if re.match(rf"^{key}:\s*$", ln):
            collecting = True
    return items


def claude_code_map(block):
    """Parse the inline `claude_code: { command: /x, subagent_type: y }` flow mapping."""
    m = re.search(r"(?m)^claude_code:\s*\{(.*)\}\s*$", block)
    if not m:
        return {}
    inner, out = m.group(1), {}
    cm = re.search(r"command:\s*([^,}\s]+)", inner)
    if cm:
        out["command"] = cm.group(1).strip().lstrip("/")
    sm = re.search(r"subagent_type:\s*([^,}\s]+)", inner)
    if sm:
        out["subagent_type"] = sm.group(1).strip()
    return out


def main():
    files = sorted(p for p in AGENTS.glob("*.md") if p.name not in ("INDEX.md", "HELP.md"))
    names = {p.stem for p in files}
    up, down, skills, examples, cc = {}, {}, {}, {}, {}
    for p in files:
        b = frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        up[p.stem] = inline_list(b, "upstream")
        down[p.stem] = inline_list(b, "downstream")
        skills[p.stem] = inline_list(b, "skills")
        examples[p.stem] = block_items(b, "examples")
        cc[p.stem] = claude_code_map(b)

    errors = []

    # 1 + 2: symmetry and dangling agent references
    for a in sorted(names):
        for b in down[a]:
            if b not in names:
                errors.append(f"dangling: {a}.downstream -> {b} (no such agent)")
            elif a not in up.get(b, []):
                errors.append(f"asymmetric: {a}.downstream has {b}, but {b}.upstream is missing {a}")
        for b in up[a]:
            if b not in names:
                errors.append(f"dangling: {a}.upstream <- {b} (no such agent)")
            elif a not in down.get(b, []):
                errors.append(f"asymmetric: {a}.upstream has {b}, but {b}.downstream is missing {a}")

    # 3: skills declared but missing on disk
    have_skills = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}
    for a in sorted(names):
        for s in skills[a]:
            if s not in have_skills:
                errors.append(f"missing skill: {a} declares skills:[{s}] but skills/{s}/SKILL.md not found")

    # 4: INDEX freshness (one row per agent)
    idx = AGENTS / "INDEX.md"
    if not idx.exists():
        errors.append("INDEX.md missing — run hooks/build_agent_index.py")
    else:
        idx_text = idx.read_text(encoding="utf-8", errors="ignore")
        rows = len(re.findall(r"(?m)^\| `", idx_text))
        for a in sorted(names):
            if f"| `{a}` |" not in idx_text:
                errors.append(f"INDEX.md missing row for `{a}` — run hooks/build_agent_index.py")
        if rows != len(names):
            errors.append(f"INDEX.md has {rows} agent rows vs {len(names)} agents — run hooks/build_agent_index.py")

    # 5: handoff line present in each agent body (run build_handoffs.py --check for exact sync)
    for p in files:
        if "> **Handoff**" not in p.read_text(encoding="utf-8", errors="ignore"):
            errors.append(f"{p.stem}: missing handoff line — run hooks/build_handoffs.py")

    # 6: example prompts present (source for /help-role + AGENTS.md — keeps the fleet self-documenting)
    for a in sorted(names):
        if not examples[a]:
            errors.append(f"{a}: no example prompts — add an examples: block (see project_guides/AGENT-AUTHORING.md)")

    # 7: claude_code mapping integrity — subagent resolves, referenced command exists
    have_commands = {p.stem for p in COMMANDS.glob("*.md")} if COMMANDS.exists() else set()
    for a in sorted(names):
        m = cc[a]
        st = m.get("subagent_type")
        if not st:
            errors.append(f"{a}: claude_code block missing a subagent_type (see project_guides/AGENT-AUTHORING.md)")
        elif st not in names:
            errors.append(f"claude_code: {a} maps subagent_type:{st} but no agents/{st}.md exists")
        cmd = m.get("command")
        if cmd and cmd not in have_commands:
            errors.append(f"claude_code: {a} maps command:/{cmd} but commands/{cmd}.md not found")

    # 8: command files are well-formed Claude Code commands (description for the / picker)
    for cmd_file in sorted(COMMANDS.glob("*.md")):
        cb = frontmatter(cmd_file.read_text(encoding="utf-8", errors="ignore"))
        if not re.search(r"(?m)^description:\s*\S", cb):
            errors.append(f"command {cmd_file.name}: no description in frontmatter (shown in Claude Code's / picker)")

    # 9: skills armed by an agent must be model-invoked, or they can't auto-fire
    armed = {s for a in names for s in skills[a]}
    for s in sorted(armed):
        sf = SKILLS / s / "SKILL.md"
        if not sf.exists():
            continue  # already reported by check 3
        sb = frontmatter(sf.read_text(encoding="utf-8", errors="ignore"))
        if re.search(r"(?m)^disable-model-invocation:\s*true\b", sb):
            errors.append(f"skill {s}: disable-model-invocation:true but it's armed by an agent's skills: list — it can't auto-fire")

    # 10: orphans — an agent no other agent hands off to (absent from every
    # downstream), excluding the foundational/always-on entry agents (invoked
    # directly). Catches the wiki-curator class: an agent silently left with no
    # inbound edge. Update ENTRY_POINTS when adding a legitimate always-on agent.
    ENTRY_POINTS = {"ai-orchestration", "coding-standards", "dev-onboarding", "spec-driven-dev", "run-orchestrator"}
    inbound = {b for a in names for b in down[a]}
    for a in sorted(names):
        if a not in inbound and a not in ENTRY_POINTS:
            errors.append(f"orphan: {a} is in no agent's downstream and not a known entry point — nothing hands off to it")

    # advisory counts
    n_templates = len(list(TEMPLATES.glob("*.md")))
    print(f"agents: {len(names)} | templates: {n_templates} | skills: {len(have_skills)} | commands: {len(have_commands)}")

    if errors:
        print(f"\nFAIL — {len(errors)} integrity issue(s):")
        for e in sorted(set(errors)):
            print("  -", e)
        return 1
    print("OK — graph symmetric, no dangling refs, declared skills present, INDEX current, claude_code mappings resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
