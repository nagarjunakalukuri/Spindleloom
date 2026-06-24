# Install — Wheelwright Agent Fleet

52 AI agents for the full SDLC (market → spec → design → build → test → ship → operate), shipped to every AI coding tool from one source.

---

## 5-minute quickstart (Claude Code)

The fastest path — no bundle step, no MCP, no gates. Just clone and use.

```bash
# 1. Prerequisites: Git + Python 3.10+
git clone <repo-url> project_managment_agents

# 2. Verify the source is healthy
py -3 project_managment_agents/hooks/validate_graph.py   # Windows
# python3 project_managment_agents/hooks/validate_graph.py  # macOS/Linux

# 3. Copy agents + skills + commands into your project's .claude/ folder
mkdir -p .claude/agents .claude/skills .claude/commands

# Windows (PowerShell)
Copy-Item project_managment_agents\agents\*   .claude\agents\
Copy-Item project_managment_agents\skills\*   .claude\skills\ -Recurse
Copy-Item project_managment_agents\commands\* .claude\commands\

# macOS / Linux
cp project_managment_agents/agents/*       .claude/agents/
cp -r project_managment_agents/skills/*    .claude/skills/
cp project_managment_agents/commands/*     .claude/commands/

# 4. Open Claude Code in your project and try it
#    /agents           → lists all 52 agents
#    /spec-new hello   → scaffolds a project
#    @prd-writer       → invoke a specific agent
```

That's it for trying it out. When you're ready to go further: Step 4 covers the plugin install (one command, everything included), Steps 6–7 add tracker integration and quality gates.

---

## Enterprise rollout checklist

For teams rolling out Wheelwright across multiple repos or to 10+ developers.

### Phase 1 — Validate and package (owner/champion, 1 day)

- [ ] Clone source, run `validate_graph.py` — confirm OK
- [ ] Run `build_harness_artifacts.py` — confirm 386 artifacts across 6 harnesses
- [ ] Run all hook tests: `py -3 -m unittest discover -s hooks -p "test_*.py"` — all pass
- [ ] Decide install method: **plugin** (recommended for Claude Code teams) or **manual copy**
- [ ] Decide tracker: Azure Boards (set `AZURE_DEVOPS_*` vars) or Jira (set `JIRA_*` vars)
- [ ] Create a shared internal fork/mirror if policies require (the source is product-agnostic)
- [ ] Set `WHEELWRIGHT_SPEC_ROOT` to your org's standard `docs/` location

### Phase 2 — Pilot repo (1–2 days)

- [ ] Install into one pilot repo (Step 4 below)
- [ ] Wire the MCP server (Step 5) — confirm `trace_requirement` and `rtm_coverage` work
- [ ] Run `/spec-new <feature>` → confirm scaffold produces the right layout
- [ ] Run one agent end-to-end: `prd-writer` → `frd-writer` → `backlog-manager`
- [ ] Wire tracker dry-run: confirm `emit_backlog.py` + adapter produces the right plan
- [ ] Wire quality gates (Step 7): Claude Code hook + CI workflow
- [ ] Run `pre-commit install` and `pre-commit run --all-files` — confirm clean
- [ ] Document any org-specific customisations (custom agents, extra skills, team conventions)

### Phase 3 — Team rollout (per repo, per developer)

- [ ] Share the plugin install command (or the internal mirror path) with each team
- [ ] Add the CI workflow (`.github/workflows/test-plugin-install.yml`) to each repo — or add the `validate_graph.py` + `build_harness_artifacts.py --check` steps to the existing CI pipeline
- [ ] Set tracker env vars in CI secrets (`AZURE_DEVOPS_PAT` / `JIRA_API_TOKEN`)
- [ ] Share `docs/per-agent-configuration.md` — per-developer hook setup and model overrides
- [ ] Run `dev-onboarding` agent on each repo to confirm the environment is ready
- [ ] Run `doc-strategy-advisor` to pick the right agent subset for each team's size and workflow

### Phase 4 — Operate

- [ ] Pin to a release tag so teams don't get breaking changes on `main`
- [ ] Wire `build_harness_artifacts.py --check` as a CI drift gate so stale bundles can't merge
- [ ] After any Wheelwright source update: re-run `build_harness_artifacts.py` and re-distribute
- [ ] Use `run-orchestrator` + `.shipwright/run-state.json` for any autonomous fleet runs
- [ ] Review `PILOT-READOUT.md` for known adjustment areas before wider rollout

### Size your adoption

| Team size | Suggested profile | Key agents to start with |
|---|---|---|
| 1–3 people | Lean | `prd-writer`, `frd-writer`, `backlog-manager`, `backend-developer`, `debugger` |
| 4–10 people | Mid | Add `srs-writer`, `sdd-writer`, `test-plan-writer`, `qa-tester`, `code-reviewer`, `sprint-planner` |
| 10+ people | Enterprise | Full funnel + `sre`, `release-manager`, `incident-postmortem`, `ai-orchestration`, `run-orchestrator` |

Run `doc-strategy-advisor` — it picks the right subset for your context.

---

## Prerequisites

| Tool | Why | Windows | macOS | Linux |
|---|---|---|---|---|
| **Git** | clone the repo | [git-scm.com](https://git-scm.com) | `brew install git` | `apt install git` |
| **Python 3.10+** | run hooks (stdlib-only, no venv needed) | `py -3 --version` | `python3 --version` | `python3 --version` |
| **uv** | MCP server only (auto-provisions SDK) | `irm https://astral.sh/uv/install.ps1 \| iex` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | same as macOS |
| **shellcheck** | lint `hooks/*.sh` in CI / pre-commit | `scoop install shellcheck` or WSL | `brew install shellcheck` | `apt install shellcheck` |
| **pre-commit** | local gate before `git commit` | `pip install pre-commit` | `brew install pre-commit` | `pip install pre-commit` |

> **Minimum to get started:** Git + Python 3.10. Everything else is optional (uv for MCP, shellcheck/pre-commit for local gates).

---

## Step 1 — Get the source

```bash
git clone <repo-url> project_managment_agents
cd project_managment_agents
```

---

## Step 2 — Verify it's healthy

```bash
# Windows
py -3 hooks/validate_graph.py

# macOS / Linux
python3 hooks/validate_graph.py
```

Expected output:
```
agents: 52 | templates: 50 | skills: 21 | commands: 13
OK — graph symmetric, no dangling refs, declared skills present, INDEX current, claude_code mappings resolve.
```

If this passes, the source is intact and ready to bundle.

---

## Step 3 — Build harness bundles (one-time, then after source changes)

Shipwright reads the single-source `agents/`, `skills/`, `commands/` and emits each tool's native bundle under `targets/`:

```bash
# Windows
py -3 hooks/build_harness_artifacts.py

# macOS / Linux
python3 hooks/build_harness_artifacts.py
```

Output: `targets/` with `claude-plugin/`, `claude-code/`, `cursor/`, `copilot/`, `windsurf/`, `agents-md/`.

---

## Step 4 — Install into your AI coding tool

### Claude Code — plugin ★ (recommended)

One command installs everything: agents + skills + commands + hooks + templates + MCP.

```
/plugin marketplace add <owner/repo-or-path>
/plugin install wheelwright@wheelwright
```

After install: agents auto-trigger by description, every `/spec-new` `/rtm-check` etc. works, and the traceability hook fires on spec edits.

**Verify:**
```
/agents          # should list 52 agents
/help-role       # shows grouped agent prompts by phase
```

---

### Claude Code — manual (loose files)

Use when you don't want the plugin install step.

```bash
# From your project repo root:
mkdir -p .claude/agents .claude/skills .claude/commands

# Windows (PowerShell)
Copy-Item project_managment_agents\targets\claude-code\agents\* .claude\agents\
Copy-Item project_managment_agents\targets\claude-code\CLAUDE.md .
Copy-Item project_managment_agents\targets\claude-code\mcp .\ -Recurse
Copy-Item project_managment_agents\targets\claude-code\.mcp.json .

# macOS / Linux
cp project_managment_agents/targets/claude-code/agents/*  .claude/agents/
cp project_managment_agents/targets/claude-code/CLAUDE.md .
cp -r project_managment_agents/targets/claude-code/mcp    .
cp project_managment_agents/targets/claude-code/.mcp.json .
```

**Global install (all repos):** copy into `~/.claude/` instead of `.claude/`:

```bash
# macOS / Linux
cp project_managment_agents/targets/claude-code/agents/* ~/.claude/agents/
cp -r project_managment_agents/targets/claude-code/skills/* ~/.claude/skills/
cp project_managment_agents/targets/claude-code/commands/* ~/.claude/commands/
```

```powershell
# Windows
Copy-Item project_managment_agents\targets\claude-code\agents\* "$env:USERPROFILE\.claude\agents\"
```

---

### Cursor

```bash
# macOS / Linux — copy into your repo root
cp -r project_managment_agents/targets/cursor/.cursor .
cp -r project_managment_agents/targets/cursor/mcp .
cp    project_managment_agents/targets/cursor/.mcp.json .
```

```powershell
# Windows
Copy-Item project_managment_agents\targets\cursor\.cursor .\ -Recurse
Copy-Item project_managment_agents\targets\cursor\mcp     .\ -Recurse
Copy-Item project_managment_agents\targets\cursor\.mcp.json .
```

Each role becomes a description-triggered `.mdc` rule. `000-wheelwright-conventions.mdc` is always-on. `.cursor/mcp.json` uses `${workspaceFolder}` so it's portable across machines.

---

### GitHub Copilot

```bash
# macOS / Linux
cp -r project_managment_agents/targets/copilot/.github  .
cp -r project_managment_agents/targets/copilot/.vscode  .
cp -r project_managment_agents/targets/copilot/mcp      .
```

```powershell
# Windows
Copy-Item project_managment_agents\targets\copilot\.github .\ -Recurse
Copy-Item project_managment_agents\targets\copilot\.vscode .\ -Recurse
Copy-Item project_managment_agents\targets\copilot\mcp     .\ -Recurse
```

Custom chat modes + `copilot-instructions.md` + `.vscode/mcp.json` for live traceability.

---

### Windsurf

```bash
# macOS / Linux
cp -r project_managment_agents/targets/windsurf/.windsurf .
cp -r project_managment_agents/targets/windsurf/mcp       .
```

```powershell
# Windows
Copy-Item project_managment_agents\targets\windsurf\.windsurf .\ -Recurse
Copy-Item project_managment_agents\targets\windsurf\mcp       .\ -Recurse
```

> **Windsurf MCP is user-global.** Copy the server entry from `targets/windsurf/README.md` into `~/.codeium/windsurf/mcp_config.json` (use absolute paths — `${workspaceFolder}` is not supported there).

---

### Any AGENTS.md tool (Gemini CLI, Codex, …)

```bash
cp project_managment_agents/targets/agents-md/AGENTS.md .
```

The cross-tool router any `AGENTS.md`-aware tool reads.

---

## Step 5 — Wire the MCP server (optional, recommended)

The MCP server gives any wired tool 12 live RTM query tools (`trace_requirement`, `rtm_coverage`, `funnel_status`, `search_specs`, `scaffold_project`, …).

**Prerequisite: uv** — provisions the MCP SDK on first run (no manual `pip install`).

```bash
# Install uv — macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

The generated `.mcp.json` auto-discovers and launches the server. Set `WHEELWRIGHT_SPEC_ROOT` to your project's `docs/` folder:

```json
// .mcp.json (already generated — just set the env var)
{
  "mcpServers": {
    "wheelwright": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "python", "mcp/mcp_server.py"],
      "env": { "WHEELWRIGHT_SPEC_ROOT": "${CLAUDE_PROJECT_DIR}/docs" }
    }
  }
}
```

**Smoke test:**
```bash
uv run python hooks/test_mcp_server.py
```

**Enable the write tool** (`scaffold_project`) — disabled by default:
```json
"env": { "WHEELWRIGHT_SPEC_ROOT": "...", "WHEELWRIGHT_WRITABLE": "1" }
```

---

## Step 6 — Wire tracker integration (optional)

### Azure Boards

```bash
# Set env vars (add to your shell profile or CI secrets)
export AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
export AZURE_DEVOPS_PROJECT=your-project
export AZURE_DEVOPS_PAT=your-pat-token      # Work Items (Read, write & manage) scope
```

```powershell
# Windows
$env:AZURE_DEVOPS_ORG_URL = "https://dev.azure.com/your-org"
$env:AZURE_DEVOPS_PROJECT = "your-project"
$env:AZURE_DEVOPS_PAT     = "your-pat-token"
```

**Dry-run (no writes):**
```bash
python3 hooks/azure_boards_adapter.py docs/backlog.md
```

**Apply (creates work items):**
```bash
python3 hooks/azure_boards_adapter.py docs/backlog.md --apply --rtm docs/RTM.md
```

---

### Jira Cloud

```bash
# Required
export JIRA_BASE_URL=https://your-org.atlassian.net
export JIRA_PROJECT_KEY=PROJ
export JIRA_USER_EMAIL=service@your-org.com
export JIRA_API_TOKEN=your-api-token          # https://id.atlassian.com/manage-profile/security/api-tokens

# Optional — Jira field IDs vary per instance; run --list-fields to discover them
export JIRA_SP_FIELD=story_points             # Story Points field id (default)
export JIRA_AC_FIELD=customfield_10040        # Acceptance Criteria field id (if you have one)
```

```powershell
# Windows
$env:JIRA_BASE_URL    = "https://your-org.atlassian.net"
$env:JIRA_PROJECT_KEY = "PROJ"
$env:JIRA_USER_EMAIL  = "service@your-org.com"
$env:JIRA_API_TOKEN   = "your-api-token"
```

**Discover your instance's field IDs:**
```bash
python3 hooks/jira_adapter.py --list-fields
```

**Dry-run:**
```bash
python3 hooks/jira_adapter.py docs/backlog.md
```

**Apply:**
```bash
python3 hooks/jira_adapter.py docs/backlog.md --apply --rtm docs/RTM.md
```

---

## Step 7 — Wire quality gates

### Option A — Claude Code hook (live feedback on every save)

Add to `.claude/settings.local.json` (personal, gitignored):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "shell": "bash",
        "command": "out=$(py \"$CLAUDE_PROJECT_DIR/hooks/validate_graph.py\" 2>&1); ec=$?; if [ $ec -ne 0 ]; then echo \"$out\" >&2; exit 2; fi",
        "timeout": 30,
        "statusMessage": "Validating fleet integrity…"
      }]
    }]
  }
}
```

> On macOS/Linux replace `py` with `python3`. Put this in `settings.local.json` (not the committed `settings.json`) because the launcher is platform-specific.

### Option B — pre-commit (local gate before every commit)

```bash
# Install pre-commit
pip install pre-commit           # or: brew install pre-commit

# Wire it — run once in the repo root
pre-commit install

# Test it runs cleanly
pre-commit run --all-files
```

The `.pre-commit-config.yaml` at the repo root runs: INDEX refresh → fleet validate → bundle drift check → shellcheck → pytest.

### Option C — CI (GitHub Actions, already wired)

`.github/workflows/test-plugin-install.yml` covers all five jobs on every push/PR:
- `validate-fleet` — graph + bundles
- `validate-traceability` — RTM on changed spec folders
- `lint-hooks` — shellcheck on `hooks/*.sh`
- `test-hooks` — all `hooks/test_*.py`
- `plugin-install` — builds bundles + checks manifest

No extra setup — commit the workflow file and CI runs automatically.

---

## Step 8 — Verify end-to-end

```bash
# 1. Fleet healthy
py -3 hooks/validate_graph.py           # → OK

# 2. Bundles current
py -3 hooks/build_harness_artifacts.py --check   # → exit 0

# 3. All tests pass
py -3 -m unittest discover -s hooks -p "test_*.py" -v

# 4. MCP server (if wired)
uv run python hooks/test_mcp_server.py  # → OK

# 5. Claude Code — inside a session
/agents          # lists 52 agents
/spec-new hello  # scaffolds a test project
```

---

## Upgrade

After pulling new source:

```bash
git pull

# Windows
py -3 hooks/build_harness_artifacts.py

# macOS / Linux
python3 hooks/build_harness_artifacts.py
```

Then re-copy the updated bundle for your tool (same Step 4 commands). The plugin install auto-updates if you run `/plugin install wheelwright@wheelwright` again.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `validate_graph.py` exits 1 | Read the error — usually a dangling ref or stale INDEX. Run `py -3 hooks/build_agent_index.py` first, then re-validate. |
| `build_harness_artifacts.py --check` exits 1 | Bundles are stale. Run without `--check` to regenerate. |
| Agent not found in Claude Code | The `claude_code.subagent_type` in the agent's frontmatter must match its `name`. The validator catches this (check 7). |
| MCP server won't start | Check `uv` is on PATH (`uv --version`). Check `WHEELWRIGHT_SPEC_ROOT` is set and points to a real directory. |
| Jira `--apply` refused | `JIRA_BASE_URL`, `JIRA_PROJECT_KEY`, `JIRA_USER_EMAIL`, `JIRA_API_TOKEN` must all be set. Run `--list-fields` to confirm connectivity. |
| Azure Boards `--apply` refused | `AZURE_DEVOPS_ORG_URL` (or `AZURE_DEVOPS_ORG`), `AZURE_DEVOPS_PROJECT`, `AZURE_DEVOPS_PAT` must all be set. PAT needs Work Items read+write scope. |
| `pre-commit run` fails on shellcheck | Install shellcheck first (`brew install shellcheck` / `apt install shellcheck`). |
| Hook not firing in Claude Code | Run `/hooks` or restart the Claude Code session — hooks are loaded at session start. |
| Skill not firing on an agent | Check the agent's `skills:` array contains the skill slug, and `skills/<slug>/SKILL.md` exists (`validate_graph.py` catches this). |

---

## Quick reference — all platform commands

| Task | Windows (`py -3`) | macOS / Linux (`python3`) |
|---|---|---|
| Validate fleet | `py -3 hooks/validate_graph.py` | `python3 hooks/validate_graph.py` |
| Rebuild INDEX | `py -3 hooks/build_agent_index.py` | `python3 hooks/build_agent_index.py` |
| Build bundles | `py -3 hooks/build_harness_artifacts.py` | `python3 hooks/build_harness_artifacts.py` |
| Check bundles | `py -3 hooks/build_harness_artifacts.py --check` | `python3 hooks/build_harness_artifacts.py --check` |
| Run all tests | `py -3 -m unittest discover -s hooks -p "test_*.py"` | `python3 -m unittest discover -s hooks -p "test_*.py"` |
| Azure dry-run | `py -3 hooks/azure_boards_adapter.py backlog.md` | `python3 hooks/azure_boards_adapter.py backlog.md` |
| Jira dry-run | `py -3 hooks/jira_adapter.py backlog.md` | `python3 hooks/jira_adapter.py backlog.md` |
| Jira list fields | `py -3 hooks/jira_adapter.py --list-fields` | `python3 hooks/jira_adapter.py --list-fields` |
| MCP smoke test | `uv run python hooks/test_mcp_server.py` | `uv run python hooks/test_mcp_server.py` |
| Scaffold project | `/spec-new <feature>` in Claude Code | same |
| Pre-commit setup | `pip install pre-commit && pre-commit install` | `brew install pre-commit && pre-commit install` |
