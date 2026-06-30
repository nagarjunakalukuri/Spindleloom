# Harness convergence matrix — 7 surfaces × 4 tools

Where each AI-coding harness exposes each customization surface, and which Spindleloom source maps onto it. This is what **Shipwright** (`hooks/build_harness_artifacts.py`) targets — one source, native artifacts per tool.

> Verified against official docs (2026-06). Several cells are **Preview** and may shift — re-verify before relying on a Preview format. `yes` = first-class native · `partial` = supported but Preview / lossy / different model · `no` = no native concept.

## Support matrix

| Surface | Claude Code | Cursor | GitHub Copilot (VS Code) | Windsurf |
|---|---|---|---|---|
| **Agents** | **yes** — `.claude/agents/*.md`, rich frontmatter (tools, model, hooks…) | **yes** — `.cursor/agents/*.md`; also reads `.claude/agents/`; no `tools`/`color` | **yes** — `.github/agents/*.agent.md` (reads `.claude/agents/`); legacy `.chatmode.md` being renamed | **no** — Cascade is one agent; **fallback: emit as Skills/rules** |
| **Skills** | **yes** — `skills/<name>/SKILL.md` (agentskills.io) | **yes** — `.cursor/skills/`; also reads `.claude/skills/` | **yes** — `.github/skills/`; reads `.claude/skills/` | **yes** — `.windsurf/skills/`; **also auto-reads `.claude/skills/`** |
| **Instructions** | **yes** — `CLAUDE.md` + `.claude/rules/*.md` (`paths:`) | **yes** — `.cursor/rules/*.mdc` + `AGENTS.md` | **yes** — `.github/copilot-instructions.md` + `*.instructions.md` (`applyTo`) + `AGENTS.md` | **yes** — `.windsurf/rules/*.md` (`trigger:`) + `AGENTS.md`; 12k-char cap |
| **Hooks** | **yes** — `settings.json` `hooks{}` / plugin `hooks/hooks.json`; ~40 events | **yes** — `.cursor/hooks.json` (`version:1`); 18+ events | **partial** — `.github/hooks/*.json` (**Preview**); 8 events; matchers ignored | **partial** — `.windsurf/hooks.json`; 12 events |
| **MCP Servers** | **yes** — `.mcp.json` / `~/.claude.json` / plugin root | **yes** — `.cursor/mcp.json` | **yes** — `.vscode/mcp.json` (`servers`/`inputs`) | **yes** — `~/.codeium/windsurf/mcp_config.json` (**user-global**, not repo) |
| **Plugins** | **yes** — `.claude-plugin/plugin.json` + `marketplace.json` | **yes** — `.cursor-plugin/plugin.json` (**has** `commands` key); v2.5+ | **partial** — Agent Plugins `plugin.json` (**Preview**; **no** `commands` key) | **no** — no multi-surface bundle format |
| **Slash Commands** | **yes** — merged into Skills; legacy `.claude/commands/*.md` | **yes** — `.cursor/commands/*.md` | **yes** — `.github/prompts/*.prompt.md` | **yes** — `.windsurf/workflows/*.md` (manual-only) |

## Spindleloom source → surface (what Shipwright emits)

| Source | Claude Code | Cursor | Copilot | Windsurf |
|---|---|---|---|---|
| `agents/*.md` | `.claude/agents/` (in the plugin) | `.cursor/rules/*.mdc` | `.github/chatmodes/*.chatmode.md` | `.windsurf/rules/*.md` (no subagents → rules) |
| `skills/` | bundled in plugin | reuse `.claude/skills/` | reuse `.claude/skills/` | reuse `.claude/skills/` |
| convention docs | `CLAUDE.md` / conventions skill | always-on `.mdc` rule | `copilot-instructions.md` | always-on `.windsurf` rule |
| `hooks/` | plugin `hooks/hooks.json` | `.cursor/hooks.json` | (Preview) | (Preview) |
| MCP server | `.mcp.json` (plugin root) | `.cursor/mcp.json` | `.vscode/mcp.json` | user-global `mcp_config.json` (snippet in bundle README) |
| — | `AGENTS.md` is the lowest-common-denominator instruction target that **all four read** |

## Two single-output shortcuts

- **`.claude/skills/`** is auto-read by Claude Code, Cursor, Copilot, *and* Windsurf — one emit covers Skills everywhere.
- **`AGENTS.md`** is read by Cursor, Copilot, and Windsurf (and is harmless for Claude Code) — the broadest single instruction surface.

## Honest caveats

- **Copilot Plugins have no `commands` manifest key** (commands ride as bundled prompt/skill files); **Cursor Plugins do**.
- **Copilot & Windsurf hooks are Preview / use a different model** — don't depend on matcher semantics.
- **Windsurf MCP config is user-global** (`~/.codeium/windsurf/mcp_config.json`), not repo-relative — Shipwright ships the server + a config snippet, not a committed repo file.
- **Copilot now reads Claude-format files** (`.claude/agents`, `.claude/skills`, `CLAUDE.md`) — a future simplification is consuming the `claude-plugin` bundle directly.
