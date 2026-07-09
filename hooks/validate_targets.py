#!/usr/bin/env python3
"""validate_targets.py — per-harness conformance for the generated bundles.

`build_harness_artifacts --check` proves the bundles match the generator's own output;
this validates the output against each TOOL's format rules — the class of defect the
drift gate cannot see (a rule over Windsurf's truncation cap, a plugin hook whose local
import isn't bundled, a chatmode without the frontmatter Copilot requires).

Checks per bundle (targets/):
  windsurf       every rule ≤ 12,000 chars (the documented truncation cap — hard fail);
                 rules carry `trigger:` frontmatter; workflows + .claude/skills present
  cursor         native agents (≥40, name+description frontmatter); commands ≥20;
                 always-on conventions rule; .cursor/mcp.json parses with the sloom server
  copilot        chatmodes ≥40 with description frontmatter; prompts ≥20;
                 .vscode/mcp.json parses (servers.sloom)
  claude-plugin  manifests parse; agents ≥40 / commands ≥20 / skills ≥20; hooks.json
                 parses; every bundled hook's LOCAL imports resolve inside the bundle
                 (the check that would have caught the shipped-broken rtm_core hook)
  claude-code    agents ≥40, commands ≥20, skills ≥20, hook set complete, .mcp.json parses
  agents-md      ≥40 agent rows in the router
Advisory: HARNESS-MATRIX's "verified" date older than ~90 days.

Usage:  python hooks/validate_targets.py [<targets-dir>]     (default: targets/)
Exit 0 = conformant, 1 = violations. Stdlib-only, read-only.
"""
import json
import re
import sys
from datetime import date

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

WINDSURF_CAP = 12_000


def _fm(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def _json_ok(p, key=None):
    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except (ValueError, OSError):
        return None
    if key:
        for k in key.split("."):
            data = data.get(k, {}) if isinstance(data, dict) else {}
    return data


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else Path("targets")
    if not root.is_dir():
        print(f"validate_targets: no bundles at {root} — run build_harness_artifacts first")
        return 1
    errors, advisories = [], []

    # ---- windsurf: the truncation cap is a hard wall ----
    ws = root / "windsurf" / ".windsurf"
    for p in sorted((ws / "rules").glob("*.md")) if (ws / "rules").is_dir() else []:
        size = p.stat().st_size
        if size > WINDSURF_CAP:
            errors.append(f"windsurf: rule {p.name} is {size:,} chars — over the {WINDSURF_CAP:,} "
                          f"truncation cap; the generator must condense it")
        if "trigger:" not in _fm(p.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"windsurf: rule {p.name} lacks `trigger:` frontmatter")
    for sub, floor in (("rules", 40), ("workflows", 20)):
        n = len(list((ws / sub).glob("*.md"))) if (ws / sub).is_dir() else 0
        if n < floor:
            errors.append(f"windsurf: only {n} files in .windsurf/{sub} (expected ≥{floor})")

    # ---- cursor ----
    cu = root / "cursor"
    ags = sorted((cu / ".cursor" / "agents").glob("*.md")) if (cu / ".cursor" / "agents").is_dir() else []
    if len(ags) < 40:
        errors.append(f"cursor: only {len(ags)} native agents in .cursor/agents (expected ≥40)")
    for p in ags[:5] + ags[-5:]:
        fm = _fm(p.read_text(encoding="utf-8", errors="ignore"))
        if "name:" not in fm or "description:" not in fm:
            errors.append(f"cursor: agent {p.name} missing name/description frontmatter")
    if len(list((cu / ".cursor" / "commands").glob("*.md")) if (cu / ".cursor" / "commands").is_dir() else []) < 20:
        errors.append("cursor: .cursor/commands has <20 commands")
    conv = cu / ".cursor" / "rules" / "000-spindleloom-conventions.mdc"
    if not conv.is_file() or "alwaysApply: true" not in conv.read_text(encoding="utf-8", errors="ignore"):
        errors.append("cursor: always-on conventions rule missing or not alwaysApply:true")
    if not _json_ok(cu / ".cursor" / "mcp.json", "mcpServers.sloom"):
        errors.append("cursor: .cursor/mcp.json missing/unparseable or lacks the sloom server")

    # ---- copilot ----
    co = root / "copilot"
    cms = sorted((co / ".github" / "chatmodes").glob("*.chatmode.md")) if (co / ".github" / "chatmodes").is_dir() else []
    if len(cms) < 40:
        errors.append(f"copilot: only {len(cms)} chatmodes (expected ≥40)")
    for p in cms[:5]:
        if "description:" not in _fm(p.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"copilot: chatmode {p.name} missing description frontmatter")
    if len(list((co / ".github" / "prompts").glob("*.prompt.md")) if (co / ".github" / "prompts").is_dir() else []) < 20:
        errors.append("copilot: .github/prompts has <20 prompt files")
    if not _json_ok(co / ".vscode" / "mcp.json", "servers.sloom"):
        errors.append("copilot: .vscode/mcp.json missing/unparseable or lacks the sloom server")

    # ---- claude-plugin: manifests + counts + hook import resolution ----
    pl = root / "claude-plugin"
    for mf in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json", ".mcp.json"):
        if _json_ok(pl / mf) is None:
            errors.append(f"claude-plugin: {mf} missing or unparseable")
    for sub, pat, floor in (("agents", "*.md", 40), ("commands", "*.md", 20), ("skills", "*/SKILL.md", 20)):
        n = len(list((pl / sub).glob(pat))) if (pl / sub).is_dir() else 0
        if n < floor:
            errors.append(f"claude-plugin: only {n} in {sub}/ (expected ≥{floor})")
    hooks_dir = pl / "hooks"
    bundled = {p.stem for p in hooks_dir.glob("*.py")} if hooks_dir.is_dir() else set()
    for p in sorted(hooks_dir.glob("*.py")) if hooks_dir.is_dir() else []:
        for m in re.finditer(r"(?m)^(?:import|from)\s+(\w+)", p.read_text(encoding="utf-8", errors="ignore")):
            mod = m.group(1)
            # a local module = one that exists in the SOURCE hooks dir; it must ship too
            if (Path(__file__).resolve().parent / f"{mod}.py").is_file() and mod not in bundled:
                errors.append(f"claude-plugin: hooks/{p.name} imports local module '{mod}' "
                              f"which is NOT bundled — the hook will crash at runtime")

    # ---- claude-code loose target ----
    cc = root / "claude-code"
    for sub, pat, floor in (("agents", "*.md", 40), ("commands", "*.md", 20),
                            ("skills", "*/SKILL.md", 20), ("hooks", "*.py", 4)):
        n = len(list((cc / sub).glob(pat))) if (cc / sub).is_dir() else 0
        if n < floor:
            errors.append(f"claude-code: only {n} in {sub}/ (expected ≥{floor})")
    if _json_ok(cc / ".mcp.json", "mcpServers.sloom") in (None, {}):
        errors.append("claude-code: .mcp.json missing/unparseable or lacks the sloom server")

    # ---- agents-md router ----
    am = root / "agents-md" / "AGENTS.md"
    rows = len(re.findall(r"(?m)^\| `", am.read_text(encoding="utf-8", errors="ignore"))) if am.is_file() else 0
    if rows < 40:
        errors.append(f"agents-md: only {rows} agent rows in AGENTS.md (expected ≥40)")

    # ---- advisory: matrix freshness ----
    matrix = Path(__file__).resolve().parent.parent / "project_guides" / "HARNESS-MATRIX.md"
    if matrix.is_file():
        m = re.search(r"\((\d{4})-(\d{2})\)", matrix.read_text(encoding="utf-8", errors="ignore")[:600])
        if m:
            age = (date.today() - date(int(m.group(1)), int(m.group(2)), 1)).days
            if age > 90:
                advisories.append(f"HARNESS-MATRIX verified {m.group(0)} — {age} days ago; several cells "
                                  f"are Preview-status, re-verify against current tool docs")

    if errors:
        print(f"validate_targets: FAIL — {len(errors)} conformance violation(s):")
        for e in errors:
            print("  -", e)
        for a in advisories:
            print("  ·", a)
        return 1
    print("validate_targets: OK — all six bundles conform to their harness format rules.")
    for a in advisories:
        print("  ·", a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
