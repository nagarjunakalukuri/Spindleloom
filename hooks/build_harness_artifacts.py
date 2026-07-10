#!/usr/bin/env python3
"""
build_harness_artifacts.py — the harness generator: one source -> harness-native artifacts.

The fleet is authored once (agents/*.md + skills/ + commands/ + hooks/ + the
convention docs). The generator reads that single source and emits it in the native
shape and location of each target harness — across every customization *surface*
the harness exposes (Agents, Skills, Instructions, Hooks, Commands, Plugin), not
just agents. So a team adopts the fleet in their tool of choice without the manual
copy-table in INSTALL.md.

Targets:
  claude-plugin  one installable Claude Code PLUGIN bundling agents + commands +
                 skills + hooks + templates + instructions (the headline: `/plugin
                 install` replaces the whole copy-table).
  claude-code    loose Claude Code subagents (.claude/agents/) for hand-wiring.
  cursor         native subagents (.cursor/agents/) + commands + an always-on
                 conventions rule + .cursor/mcp.json.
  copilot        custom chat modes (.github/chatmodes/) + prompts + copilot-instructions.md.
  windsurf       rules (.windsurf/rules/, trigger frontmatter, 12k cap) + workflows.
  agents-md      the cross-tool AGENTS.md router (one file, any tool reads it).

Convergence: source of truth = agents/*.md + sibling folders. Targets are derived,
never hand-edited (same contract as build_agent_index.py). Re-run on source change;
run with --check in CI as a drift gate.

Dependency-free (Python 3 stdlib only). Read-only except for writing under the
output root (default: targets/).

Usage:
    python hooks/build_harness_artifacts.py
    python hooks/build_harness_artifacts.py --only claude-plugin,cursor
    python hooks/build_harness_artifacts.py --out yard
    python hooks/build_harness_artifacts.py --check

Add a harness in one place: write an emit_* function and register it in HARNESSES.
"""
import json
import re
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

PHASE_ORDER = [
    "discovery", "requirements", "design", "planning",
    "build", "test", "review", "release", "operate", "process",
]
PLUGIN_NAME = "sloom"          # short plugin id -> command prefix /sloom:<cmd>
MARKETPLACE_NAME = "spindleloom"  # the brand stays on the marketplace

# ---------------------------------------------------------------- source parsing

def split_doc(text):
    """Return (frontmatter_lines, body_str). Frontmatter is the first --- ... --- block."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return [], text
    return m.group(1).splitlines(), m.group(2)


def scalar(lines, key):
    for ln in lines:
        m = re.match(rf"\s*{re.escape(key)}\s*:\s*(.+?)\s*$", ln)
        if m:
            v = m.group(1).strip()
            if len(v) >= 2 and v[0] == v[-1] == "'":      # single-quoted YAML
                return v[1:-1].replace("''", "'")
            if len(v) >= 2 and v[0] == v[-1] == '"':      # double-quoted YAML
                return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            return v
    return ""


def inline_list(lines, key):
    raw = scalar(lines, key)
    if not raw or raw in ("[]", "—"):
        return []
    return [x.strip().strip('"') for x in raw.strip("[]").split(",") if x.strip()]


def block_list(lines, key):
    """Items of a YAML block list (key:\\n  - "v")."""
    out, collecting = [], False
    for ln in lines:
        if collecting:
            s = ln.strip()
            if ln[:1] in (" ", "\t") and s.startswith("- "):
                v = s[2:].strip()
                if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                    v = v[1:-1]
                out.append(v.replace('\\"', '"').replace("\\\\", "\\"))
                continue
            break
        if ln.lstrip().startswith(key + ":"):
            collecting = True
    return out


def yaml_sq(s):
    """Single-quote a scalar for YAML — safe for descriptions with : , " inside."""
    return "'" + s.replace("'", "''") + "'"


def first_sentence(s):
    s = s.strip()
    m = re.search(r"\.\s", s)
    return (s[: m.start() + 1] if m else s).strip()


def load_agents(agents_dir):
    out = []
    for f in sorted(agents_dir.glob("*.md")):
        if f.name in ("INDEX.md", "HELP.md"):
            continue
        fm, body = split_doc(f.read_text(encoding="utf-8", errors="ignore"))
        if not fm:
            continue
        out.append({
            "name": f.stem,
            "fm": fm,
            "body": body.rstrip() + "\n",
            "description": scalar(fm, "description"),
            "tools": scalar(fm, "tools"),
            "model": scalar(fm, "model") or "inherit",
            "phase": scalar(fm, "phase") or "process",
            "outputs": scalar(fm, "outputs") or "—",
            "downstream": inline_list(fm, "downstream"),
            "examples": block_list(fm, "examples"),
        })
    return out


def read_tree(base, prefix, patterns=("*",), recurse=True):
    """Return {f'{prefix}/{relpath}': content} for files under base. Skips if base missing."""
    out = {}
    if not base.is_dir():
        return out
    files = []
    for pat in patterns:
        files += (base.rglob(pat) if recurse else base.glob(pat))
    for f in sorted(set(files)):
        if not f.is_file():
            continue
        rel = f.relative_to(base).as_posix()
        out[f"{prefix}/{rel}"] = f.read_text(encoding="utf-8", errors="ignore")
    return out


# ---- MCP surface (the traceability server: rtm_core + mcp_server, + per-harness config) ----

def mcp_server_files(src):
    """The bundled MCP server: stdlib core + FastMCP wrapper + artifact-registry
    generator, under mcp/."""
    out = {}
    for nm in ("rtm_core.py", "mcp_server.py", "build_artifact_registry.py", "scaffold.py"):
        p = src / "hooks" / nm
        if p.is_file():
            out[f"mcp/{nm}"] = p.read_text(encoding="utf-8", errors="ignore")
    return out


def mcp_config(style, server_arg, spec_root):
    """A harness-native MCP config pointing at the bundled `sloom` server (short for Spindleloom).
    style 'vscode' uses the `servers` key + explicit stdio type; others use `mcpServers`.

    Launches via `uv run --with "mcp[cli]"`: uv provisions the one dependency in a
    cached ephemeral env on first run (no global `pip install` step) and resolves an
    interpreter itself — sidestepping the `python` vs `py` launcher problem that bites
    bare `"command": "python"` on machines where `python` is a stub/missing. The one
    prerequisite becomes `uv` (https://docs.astral.sh/uv/), which also bootstraps Python."""
    entry = {
        "command": "uv",
        "args": ["run", "--with", "mcp[cli]", "python", server_arg],
        "env": {"SPINDLELOOM_SPEC_ROOT": spec_root},
    }
    if style == "vscode":
        entry = {"type": "stdio", **entry}
        cfg = {"servers": {"sloom": entry}}
    else:
        cfg = {"mcpServers": {"sloom": entry}}
    return json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------- shared content

def agent_md(a):
    """A Claude-Code-native agent file (CC-recognized frontmatter only)."""
    fm = [f"name: {a['name']}", f"description: {yaml_sq(a['description'])}"]
    if a["tools"]:
        fm.append(f"tools: {a['tools']}")
    fm.append(f"model: {a['model']}")
    return "---\n" + "\n".join(fm) + "\n---\n\n" + a["body"]


WINDSURF_RULE_CAP = 12_000  # chars — Windsurf silently truncates rules beyond this


def condense_body(a, limit):
    """A deterministic short form of an agent body for size-capped surfaces:
    role paragraph(s) + Core principles + Style rules + a pointer to the full text.
    Used when the rendered rule would exceed the harness cap — never truncate silently."""
    import re as _re
    body = a["body"]
    head = body.split('\n## ', 1)[0].rstrip()

    def section(name):
        m = _re.search(r"(?ms)^## " + name + r"\s*?$(.*?)(?=^## |\Z)", body)
        return ("## " + name + m.group(1).rstrip()) if m else ""

    parts = [head, section("Core principles"), section("Style rules"),
             "> Condensed to fit this harness's rule-size cap — the full definition "
             "(workflow, templates, pitfalls) is `agents/" + a["name"] + ".md` in the "
             "Spindleloom source / plugin."]
    out = '\n\n'.join(p for p in parts if p) + '\n'
    return out if len(out) <= limit else out[: limit - 80].rsplit('\n', 1)[0] + '\n> (condensed)\n'


def load_commands(src):
    """[(name, file_content)] for every source command — shipped to each tool's
    native slash-command surface (Cursor commands / Copilot prompts / Windsurf workflows)."""
    out = []
    cdir = src / "commands"
    if cdir.is_dir():
        for p in sorted(cdir.glob("*.md")):
            out.append((p.stem, p.read_text(encoding="utf-8", errors="ignore")))
    return out


def instructions_md(agents, src):
    """The Instructions surface: project-wide conventions distilled from the convention docs.

    Kept concise and AI-read-first; points to the bundled knowledge_hub/BEST-PRACTICES.md for the
    full standard rather than duplicating 13KB."""
    n = len(agents)
    out = [
        "# Spindleloom — project conventions (AI-read-first)",
        "",
        f"This project uses the **Spindleloom** fleet of {n} role-specialist SDLC agents "
        "(market → spec → design → build → test → ship → operate), one traceable chain. "
        "When a task matches a role, adopt that agent. Run only the subset your team needs — "
        "start with `doc-strategy-advisor`.",
        "",
        "## The funnel",
        "",
        "```",
        "MRD → BRD → PRD → FRD → SRS → SDD → TSD",
        "```",
        "`urs-writer` runs in parallel for regulated systems; `adr-writer` runs continuously.",
        "",
        "## Conventions every agent follows",
        "",
        "- **Requirement quality:** \"the system shall …\", one obligation per statement "
        "(ISO/IEC/IEEE 29148 + INCOSE). No vague/compound requirements.",
        "- **Req-ID convention:** `<DOC>-<AREA>-<NUM>` (e.g. `PRD-AUTH-001`). Every "
        "requirement carries an ID and is traced in the RTM.",
        "- **Traceability:** one RTM per initiative, kept living — business goal → story → "
        "requirement → design → test/PBI. Nothing dropped, blast radius visible.",
        "- **Context first:** `recall_context(task_id=...)` before reading; prefer `search_specs`/`trace_requirement` and context packs (`hooks/build_context_pack.py`) over folder-wide reads; save ≤5 bullets before handing off.",
        "- **Layout standard:** the canonical `docs/` + `.spindleloom/` tree, the profiles, and the "
        "four cadence planes (durable/living/cyclic/snapshot) are fixed by `knowledge_hub/GOVERNANCE.md` Part I; existing "
        "repos convert via `scaffold.py migrate`, never by hand.",
        "- **Right-sized output:** the leanest doc that does the job for the team's tier; "
        "fight documentation fatigue.",
        "- **Ground, don't fabricate:** read the upstream doc(s) first; flag assumed values.",
        "",
        "The full standard (feedback loops, change control, team-size tiers, frameworks) is in "
        "`knowledge_hub/BEST-PRACTICES.md` (bundled). Navigate the fleet by phase in `AGENTS.md` / `agents/INDEX.md`.",
        "",
    ]
    return "\n".join(out)


# ---------------------------------------------------------------- harness emitters
# Each returns {relative_path: content}. Pure (no disk writes) so --check can diff.

def emit_claude_plugin(agents, src):
    """P0 — one installable Claude Code plugin bundling every surface.

    Self-contained: manifest + marketplace + agents + commands + skills + hooks +
    templates + instructions. `/plugin install` replaces the entire copy-table."""
    files = {}

    # --- manifest (auto-discovery handles agents/ commands/ skills/ hooks/hooks.json) ---
    # version omitted on purpose: for an actively-developed fleet the commit SHA drives
    # updates; a pinned version in plugin.json silently overrides the marketplace entry
    # and must be hand-bumped every release.
    files[".claude-plugin/plugin.json"] = json.dumps({
        "name": PLUGIN_NAME,
        "description": "Spindleloom — an AI agent fleet for the entire SDLC "
                       "(market → spec → design → build → test → ship → operate), one traceable chain.",
        "author": {"name": "Spindleloom"},
        "keywords": ["sdlc", "requirements", "specs", "traceability", "backlog", "agents", "project-management"],
    }, indent=2, ensure_ascii=False) + "\n"

    # --- marketplace so users can `/plugin marketplace add <repo>` then install ---
    # source: "." = marketplace root (targets/claude-plugin/), where agents/ commands/
    # skills/ hooks/ etc. live. Claude Code resolves source paths relative to the
    # marketplace root, not relative to this marketplace.json file — so "." is correct.
    files[".claude-plugin/marketplace.json"] = json.dumps({
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Spindleloom"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": ".",
            "description": "The full Spindleloom SDLC agent fleet (agents, skills, commands, hooks, templates).",
        }],
    }, indent=2, ensure_ascii=False) + "\n"

    # --- Agents (generated, clean CC frontmatter) + the generated role-help index ---
    for a in agents:
        files[f"agents/{a['name']}.md"] = agent_md(a)
    help_md = src / "agents" / "HELP.md"
    if help_md.is_file():
        files["agents/HELP.md"] = help_md.read_text(encoding="utf-8", errors="ignore")

    # --- Skills + Commands + Templates (verbatim from source) ---
    files.update(read_tree(src / "skills", "skills"))
    files.update(read_tree(src / "commands", "commands", patterns=("*.md",), recurse=False))
    files.update(read_tree(src / "templates", "templates", patterns=("*.md",), recurse=False))

    # --- Hooks: the consumer-facing spec gate + its wiring. on_md_edit.py filters to
    # spec .md edits, runs validate_reqs (traceability + quality lint) and
    # build_rtm --check, and surfaces failures on stderr (exit 2 -> fed to the model).
    # Ships every module the gate imports; the pre-0.3 wiring silently swallowed a
    # missing-rtm_core crash behind `2>/dev/null || true` -- never again. ---
    hook_files = ("on_md_edit.py", "validate_reqs.py", "build_rtm.py", "rtm_core.py")
    if all((src / "hooks" / n).is_file() for n in hook_files):
        for n in hook_files:
            files[f"hooks/{n}"] = (src / "hooks" / n).read_text(encoding="utf-8", errors="ignore")
        files["hooks/hooks.json"] = json.dumps({
            "hooks": {
                "PostToolUse": [{
                    "matcher": "Write|Edit",
                    "hooks": [{
                        "type": "command",
                        "command": 'python "${CLAUDE_PLUGIN_ROOT}/hooks/on_md_edit.py"',
                    }],
                }],
            }
        }, indent=2) + "\n"

    # --- Instructions surface: shipped as a SKILL, not plugin-root CLAUDE.md.
    # A plugin-root CLAUDE.md is NOT auto-loaded by Claude Code (verified), so the
    # conventions ride as a relevance-loaded skill; the full standard stays at root,
    # referenced by both the agents and this skill. ---
    conv_desc = ("Spindleloom SDLC conventions — the funnel (MRD→…→TSD), the Req-ID convention, "
                 "the living RTM, and the requirement-quality standard. Use when writing, reviewing, "
                 "or decomposing any spec, requirement, backlog, or design artifact in this project.")
    files["skills/spindleloom-conventions/SKILL.md"] = (
        "---\nname: spindleloom-conventions\ndescription: " + yaml_sq(conv_desc) + "\n---\n\n"
        + instructions_md(agents, src)
    )
    bp = src / "knowledge_hub" / "BEST-PRACTICES.md"
    if bp.is_file():
        files["knowledge_hub/BEST-PRACTICES.md"] = bp.read_text(encoding="utf-8", errors="ignore")
    sd = src / "knowledge_hub" / "GOVERNANCE.md"
    if sd.is_file():
        files["knowledge_hub/GOVERNANCE.md"] = sd.read_text(encoding="utf-8", errors="ignore")

    # --- MCP surface: the live traceability server, auto-discovered at plugin root ---
    files.update(mcp_server_files(src))
    files[".mcp.json"] = mcp_config("claude", "${CLAUDE_PLUGIN_ROOT}/mcp/mcp_server.py", "${CLAUDE_PROJECT_DIR}")

    files["README.md"] = (
        "# Spindleloom — Claude Code plugin\n\n"
        "Generated by `hooks/build_harness_artifacts.py` from the single source. "
        "Do not edit — re-run the generator.\n\n"
        "## Install\n\n"
        "```\n"
        "# from a repo/marketplace that contains this bundle\n"
        f"/plugin marketplace add <owner/repo-or-path>\n"
        f"/plugin install {PLUGIN_NAME}@{PLUGIN_NAME}\n"
        "```\n\n"
        "Then the agents trigger by description (or `/agents`), the slash commands "
        "(`/spec-new`, `/pbi-next`, `/rtm-check`, …) are available, skills load on relevance, "
        "and the spec-traceability hook runs on edits. One install — the whole fleet.\n\n"
        "## Live traceability (MCP, optional)\n\n"
        "The bundled `sloom` MCP server (short for Spindleloom) exposes **19 tools** in two groups. "
        "**RTM / catalog / conformance (12):** trace/coverage (`trace_requirement`, `rtm_coverage`, `funnel_status`), "
        "catalog (`list_requirements`, `list_artifacts`, `find_artifact`, `find_decision`, `search_specs`), "
        "conformance (`check_conformance`), and authoring (`next_req_id`, `stale_artifacts`, `scaffold_project`). "
        "**Agent context memory (6):** `save_context` / `recall_context` / `list_contexts` / `get_context` / "
        "`delete_context` / `sync_contexts` — token-efficient handoff layer so agents retrieve prior decisions "
        "in one call instead of re-reading upstream docs. Enable semantic search with "
        "`\"SPINDLELOOM_SEMANTIC\":\"1\"` (local ONNX embeddings, no API calls). "
        "`.mcp.json` launches it via `uv run --with \"mcp[cli]\"`, so the only prerequisite is "
        "[uv](https://docs.astral.sh/uv/) — uv provisions the MCP SDK (and a Python interpreter) "
        "on first run, no manual `pip install`.\n\n"
        "`.mcp.json` is auto-discovered; it points the server at your project root. `scaffold_project` "
        "writes and is disabled unless you add `\"SPINDLELOOM_WRITABLE\": \"1\"` to the server's `env`.\n"
    )
    return files


def emit_claude_code(agents, src):
    """Loose Claude Code subagents for teams that hand-wire `.claude/` (no plugin)."""
    files = {f"agents/{a['name']}.md": agent_md(a) for a in agents}
    for name, content in load_commands(src):
        files[f"commands/{name}.md"] = content
    files.update(read_tree(src / "skills", "skills"))
    for n in ("on_md_edit.py", "validate_reqs.py", "build_rtm.py", "rtm_core.py"):
        p = src / "hooks" / n
        if p.is_file():
            files[f"hooks/{n}"] = p.read_text(encoding="utf-8", errors="ignore")
    files["CLAUDE.md"] = instructions_md(agents, src)
    files.update(mcp_server_files(src))
    files[".mcp.json"] = mcp_config("claude", "${CLAUDE_PROJECT_DIR}/mcp/mcp_server.py", "${CLAUDE_PROJECT_DIR}")
    files["README.md"] = (
        "# Claude Code bundle (loose files)\n\n"
        "Generated by `build_harness_artifacts.py` from the single source. Prefer the `claude-plugin` target "
        "(one `/plugin install`); use this only to hand-wire `.claude/`.\n\n"
        "Copy `agents/` → `.claude/agents/`, `commands/` → `.claude/commands/`, `skills/` → `.claude/skills/`, "
        "`CLAUDE.md` → repo root, and `mcp/` + `.mcp.json` → repo root (MCP launches via `uv run` — install "
        "[uv](https://docs.astral.sh/uv/)). Wire `hooks/on_md_edit.py` as a PostToolUse Write|Edit hook in "
        "`.claude/settings.json` for the live spec gate.\n"
    )
    return files


def emit_cursor(agents, src):
    """Cursor project rules: .cursor/rules/<name>.mdc + an always-on conventions rule."""
    files = {}
    # Agents ride Cursor's native subagent surface (.cursor/agents/, first-class per
    # HARNESS-MATRIX) instead of 52 pseudo-agent rules — rules carry only the always-on
    # conventions. Commands and skills use their documented native locations.
    for a in agents:
        files[f".cursor/agents/{a['name']}.md"] = agent_md(a)
    for name, content in load_commands(src):
        files[f".cursor/commands/{name}.md"] = content
    files.update(read_tree(src / "skills", ".claude/skills"))
    # Instructions surface as an always-on rule (Cursor has no separate "instructions" slot)
    conv = ["---", "description: Spindleloom project conventions (SDLC funnel, Req-ID, RTM).",
            "globs:", "alwaysApply: true", "---", ""]
    files[".cursor/rules/000-spindleloom-conventions.mdc"] = "\n".join(conv) + instructions_md(agents, src)
    files.update(mcp_server_files(src))
    # Cursor resolves ${workspaceFolder} (the dir containing .cursor/mcp.json) — portable, no abs path.
    files[".cursor/mcp.json"] = mcp_config("cursor", "${workspaceFolder}/mcp/mcp_server.py", "${workspaceFolder}")
    files["README.md"] = (
        "# Cursor bundle\n\n"
        "Generated by `build_harness_artifacts.py`. Copy `.cursor/`, `.claude/`, and `mcp/` into your repo root. "
        "Each role is a native Cursor agent (`.cursor/agents/`); slash commands live in `.cursor/commands/`; "
        "skills in `.claude/skills/` (Cursor auto-reads them); `000-spindleloom-conventions.mdc` is the always-on rule. "
        "`.cursor/mcp.json` registers the live traceability server, launched via `uv run` "
        "(install [uv](https://docs.astral.sh/uv/); it provisions the MCP SDK on first run); "
        "it uses `${workspaceFolder}`, so it's portable across machines.\n"
    )
    return files


def emit_copilot(agents, src):
    """GitHub Copilot custom chat modes + the instructions surface."""
    files = {}
    for a in agents:
        fm = ["---", f"description: {yaml_sq(a['description'])}", "---", ""]
        files[f".github/chatmodes/{a['name']}.chatmode.md"] = "\n".join(fm) + a["body"]
    for name, content in load_commands(src):
        files[f".github/prompts/{name}.prompt.md"] = content
    files.update(read_tree(src / "skills", ".claude/skills"))
    lines = [instructions_md(agents, src).rstrip(), "", "## Agent chat modes", "",
             "Select a chat mode (`.github/chatmodes/<name>.chatmode.md`) matching the task:", ""]
    for a in sorted(agents, key=lambda x: x["name"]):
        lines.append(f"- **{a['name']}** — {first_sentence(a['description'])}")
    files[".github/copilot-instructions.md"] = "\n".join(lines) + "\n"
    files.update(mcp_server_files(src))
    files[".vscode/mcp.json"] = mcp_config("vscode", "${workspaceFolder}/mcp/mcp_server.py", "${workspaceFolder}")
    files["README.md"] = (
        "# GitHub Copilot bundle\n\n"
        "Generated by `build_harness_artifacts.py`. Copy `.github/`, `.vscode/`, and `mcp/` into your repo root. "
        "Chat modes + `copilot-instructions.md` carry the fleet; `.github/prompts/` carries the slash "
        "commands; `.claude/skills/` is auto-read by Copilot; `.vscode/mcp.json` registers the "
        "live traceability server, launched via `uv run` (install "
        "[uv](https://docs.astral.sh/uv/); it provisions the MCP SDK on first run).\n"
    )
    return files


def emit_agents_md(agents, src):
    """The cross-tool open standard: a single root AGENTS.md (router/index by phase)."""
    out = ["# AGENTS.md", "",
           "> Generated by `hooks/build_harness_artifacts.py` from `agents/*.md` — "
           "the single source. Any AGENTS.md-aware tool reads this. Do not edit by hand.", "",
           "This project carries a fleet of role-specialist AI agents spanning the SDLC "
           "(market → spec → design → build → test → ship → operate). When a task matches a "
           "role below, **adopt that agent's instructions** — full text in `agents/<name>.md`. "
           "Run only the subset your team needs (start with `doc-strategy-advisor`). "
           "Conventions: Req-ID `<DOC>-<AREA>-<NUM>`, one living RTM, \"the system shall …\" "
           "(ISO/IEC/IEEE 29148); see `knowledge_hub/BEST-PRACTICES.md`.", ""]
    by_phase = {}
    for a in agents:
        by_phase.setdefault(a["phase"], []).append(a)
    for phase in PHASE_ORDER + sorted(set(by_phase) - set(PHASE_ORDER)):
        group = by_phase.get(phase)
        if not group:
            continue
        out += [f"## {phase.capitalize()}", "",
                "| Agent | Produces | Hands off to | Role | Example prompt |",
                "|---|---|---|---|---|"]
        for a in sorted(group, key=lambda x: x["name"]):
            ds = ", ".join(a["downstream"]) or "—"
            ex = (a["examples"][0].replace("|", "\\|") if a["examples"] else "—")
            out.append(f"| `{a['name']}` | {a['outputs']} | {ds} | {first_sentence(a['description'])} | {ex} |")
        out.append("")
    return {"AGENTS.md": "\n".join(out)}


def emit_windsurf(agents, src):
    """Windsurf has no subagents, so each role becomes a `model_decision` rule and the
    conventions an always-on rule. MCP is user-global, so we ship the server + a snippet."""
    files = {}
    for a in agents:
        fm = ["---", "trigger: model_decision", f"description: {yaml_sq(a['description'])}", "---", ""]
        rule = "\n".join(fm) + a["body"]
        if len(rule) > WINDSURF_RULE_CAP:  # never let Windsurf truncate silently
            rule = "\n".join(fm) + condense_body(a, WINDSURF_RULE_CAP - len("\n".join(fm)))
        files[f".windsurf/rules/{a['name']}.md"] = rule
    for name, content in load_commands(src):
        files[f".windsurf/workflows/{name}.md"] = content
    files.update(read_tree(src / "skills", ".claude/skills"))
    conv = ["---", "trigger: always_on",
            "description: Spindleloom project conventions (SDLC funnel, Req-ID, RTM).", "---", ""]
    files[".windsurf/rules/000-spindleloom-conventions.md"] = "\n".join(conv) + instructions_md(agents, src)
    files.update(mcp_server_files(src))
    snippet = mcp_config("claude", "/abs/path/to/your/repo/mcp/mcp_server.py", "/abs/path/to/your/repo")
    files["README.md"] = (
        "# Windsurf bundle\n\n"
        "Generated by `build_harness_artifacts.py`. Copy `.windsurf/` and `mcp/` into your repo root. Windsurf has no "
        "subagents, so each role is a `model_decision` rule (activates when relevant); "
        "`000-spindleloom-conventions.md` is always-on. Oversize roles are auto-condensed to Windsurf's ~12k rule cap "
        "(full text stays in the source/plugin). `.windsurf/workflows/` carries the slash commands; "
        "`.claude/skills/` is auto-read by Windsurf.\n\n"
        "## Live traceability (MCP)\n\n"
        "Windsurf's MCP config is **user-global**, so add this to `~/.codeium/windsurf/mcp_config.json` "
        "(install [uv](https://docs.astral.sh/uv/) — it provisions the MCP SDK on first run), with "
        "absolute paths to where you copied `mcp/`:\n\n"
        "```json\n" + snippet + "```\n"
    )
    return files


HARNESSES = {
    "claude-plugin": emit_claude_plugin,
    "claude-code": emit_claude_code,
    "cursor": emit_cursor,
    "copilot": emit_copilot,
    "windsurf": emit_windsurf,
    "agents-md": emit_agents_md,
}


# ---------------------------------------------------------------- driver

def build(agents, src, only):
    return {h: HARNESSES[h](agents, src) for h in (only or HARNESSES)}


def main(argv):
    only, out_dir, check = None, "targets", False
    i = 1
    while i < len(argv):
        if argv[i] == "--only" and i + 1 < len(argv):
            only = [x.strip() for x in argv[i + 1].split(",") if x.strip()]; i += 2
        elif argv[i] == "--out" and i + 1 < len(argv):
            out_dir = argv[i + 1]; i += 2
        elif argv[i] == "--check":
            check = True; i += 1
        else:
            print(f"build_harness_artifacts: ignoring unknown arg {argv[i]!r}"); i += 1

    if only:
        bad = [h for h in only if h not in HARNESSES]
        if bad:
            print(f"build_harness_artifacts: unknown harness(es) {bad}; known: {list(HARNESSES)}")
            return 2

    agents_dir = Path("agents")
    if not agents_dir.is_dir():
        agents_dir = Path("spindleloom/agents")
    src = agents_dir.parent
    agents = load_agents(agents_dir)
    if not agents:
        print(f"build_harness_artifacts: no agents found under {agents_dir}")
        return 2

    out_root = Path(out_dir)
    built = build(agents, src, only)

    def orphans(harness, files):
        """Files on disk under the harness root that the generator did not emit.
        The harness dirs are fully generated, so anything extra is a stale leftover
        (e.g. a renamed agent's old file) that would still load in installs."""
        root = out_root / harness
        if not root.is_dir():
            return []
        expected = {(root / rel).resolve() for rel in files}
        return sorted(p for p in root.rglob("*")
                      if p.is_file() and p.resolve() not in expected
                      and "__pycache__" not in p.parts and p.suffix != ".pyc")

    if check:
        drift, stale = [], []
        for harness, files in built.items():
            for rel, content in files.items():
                p = out_root / harness / rel
                if not p.exists() or p.read_text(encoding="utf-8", errors="ignore") != content:
                    drift.append(str(p))
            stale.extend(str(p) for p in orphans(harness, files))
        if drift or stale:
            if drift:
                print(f"build_harness_artifacts: DRIFT — {len(drift)} artifact(s) stale vs source. "
                      f"Re-run the generator. First few:\n  " + "\n  ".join(drift[:8]))
            if stale:
                print(f"build_harness_artifacts: ORPHANS — {len(stale)} file(s) in targets the "
                      f"generator no longer emits (renamed/removed source?). Re-run the generator "
                      f"to sweep them. First few:\n  " + "\n  ".join(stale[:8]))
            return 1
        print(f"build_harness_artifacts: in sync — {sum(len(f) for f in built.values())} artifacts "
              f"across {len(built)} harness(es).")
        return 0

    total, swept = 0, 0
    for harness, files in built.items():
        for rel, content in files.items():
            p = out_root / harness / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            total += 1
        for p in orphans(harness, files):
            p.unlink()
            swept += 1
        # prune directories emptied by the sweep
        for d in sorted((x for x in (out_root / harness).rglob("*") if x.is_dir()), reverse=True):
            if not any(d.iterdir()):
                d.rmdir()
    print(f"build_harness_artifacts: wrote {total} artifacts for {len(agents)} agents -> "
          f"{out_root}/ ({', '.join(built)})"
          + (f"; swept {swept} orphan(s)" if swept else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
