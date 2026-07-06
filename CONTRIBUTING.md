# Contributing to Spindleloom

Spindleloom is a fleet of 52 AI agents for the full SDLC.  Changes here affect every team that installs it — so the bar is: add value, don't break symmetry, don't create hidden dependencies.

---

## Get set up (≈ 5 minutes)

**Prerequisites:** Python 3.10+, Git, bash/zsh (for shell hooks), shellcheck (optional, for local lint).

```bash
git clone <repo-url>
cd spindleloom

# Verify the fleet is healthy — should print "OK" with counts:
py -3 hooks/validate_graph.py

# Build harness bundles (targets/ directory):
py -3 hooks/build_harness_artifacts.py
```

No `pip install` required for the core hooks (stdlib-only). The MCP server needs:
```bash
pip install "mcp[cli]"
```

---

## Codebase map

| Path | What lives here |
|---|---|
| `agents/` | 52 agent definitions (one `.md` per agent; frontmatter is the contract) |
| `skills/` | 19+ reusable methodology skills (one `<name>/SKILL.md` each) |
| `templates/` | 50 document templates (filled by agents, checked into project repos) |
| `commands/` | 13 slash commands wired into Claude Code |
| `hooks/` | Python automation (validators, generators, MCP server, Azure adapter) |
| `hooks/*.sh` | Shell hooks (SSRF-safe URL caching for remote spec fetches) |
| `targets/` | Generated harness bundles — **do not edit by hand** |
| `examples/` | End-to-end project artifacts (healthy-meal-app reference) |
| `docs/` | Spindleloom-level docs (per-agent config, onboarding, etc.) |
| `.github/workflows/` | CI (fleet integrity, harness bundles, shellcheck, plugin install) |

Key single-source files: `project_guides/STANDARD.md` (information-architecture contract), `project_guides/BEST-PRACTICES.md` (fleet conventions), `project_guides/HARNESS-MATRIX.md` (per-tool feature surface), `hooks/HOOKS.md` (hook reference).

---

## How change flows

- **Branch:** from `main`; name `feature/<slug>` or `fix/<slug>` (no PBI ref required for doc-only changes; include one for agent/skill changes that map to a roadmap item)
- **Commit:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`); small and logical; one concern per commit
- **PR:** use `templates/pr-template.md`; keep it reviewable; CI must be green
- **Ready / Done:** see `templates/definition-of-ready-done-template.md`
- **Review bar:** see `project_guides/AGENT-AUTHORING.md` for agent quality bar; `project_guides/BEST-PRACTICES.md` for general conventions

---

## Catch overlaps before you open a PR

Run these commands before submitting to avoid "this already exists" in review:

```bash
# Does an agent with a similar purpose already exist?
grep -ri "your-topic" agents/ --include="*.md" -l

# Does a skill covering this methodology already exist?
grep -ri "your-topic" skills/ --include="*.md" -l

# Does a template for this document type already exist?
ls templates/ | grep -i "your-topic"

# Check the agent index for coverage gaps or near-duplicates:
grep -i "your-topic" agents/INDEX.md

# Full-text search across all agent descriptions:
grep -ri "triggers on requests like" agents/ | grep -i "your-topic"
```

If you find a near-duplicate, consider whether your change belongs as:
1. An addition to the existing agent's workflow section, or
2. A new skill armed to the existing agent, or
3. A genuinely distinct new agent (justify in the PR why it can't extend the existing one)

---

## Adding an agent

1. Copy the structure from any existing agent as a starting point.
2. Fill in the full frontmatter contract block (`name`, `description`, `tools`, `model`, `examples`, `phase`, `inputs`, `outputs`, `upstream`, `downstream`, `skills`, `claude_code`).
3. Add reciprocal edges: every agent you list in `downstream` must list you in their `upstream`, and vice versa. The validator will catch this, but fix it before committing.
4. Run the generators and validator:
   ```bash
   py -3 hooks/build_agent_index.py    # refreshes agents/INDEX.md
   py -3 hooks/build_handoffs.py       # injects/refreshes the Handoff blockquote
   py -3 hooks/validate_graph.py       # symmetry + dangling refs + skills + INDEX
   py -3 hooks/build_harness_artifacts.py   # rebuild bundles
   ```
5. Add the new agent to the fleet count table in `README.md`.
6. See `project_guides/AGENT-AUTHORING.md` for the full quality bar (examples block, handoff line, style rules).

---

## Adding a skill

1. Create `skills/<kebab-name>/SKILL.md` — follow the pattern of an existing skill (frontmatter: `name`, `description`; body: principle, workflow, anti-patterns, style rules).
2. Arm it to at least one agent: add the skill slug to that agent's `skills:` array.
3. Run `py -3 hooks/validate_graph.py` — it checks that every declared skill has a corresponding `SKILL.md`.
4. Update `README.md` skill count.

---

## Adding a shell hook

1. Write it to `hooks/<name>.sh` — use `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Mirror the `validate_url()` SSRF guard from `hooks/sdd-cache-pre.sh` for any hook that accepts or constructs URLs.
3. Use `--max-redirs 0` for all `curl` calls — no redirect-following.
4. Run `shellcheck --severity=warning hooks/<name>.sh` locally before committing.
5. Add a row to `hooks/HOOKS.md`.

---

## CI gates (must be green before merge)

| Job | What it checks |
|---|---|
| `validate-fleet` | Graph symmetry, INDEX freshness, harness bundles not stale |
| `validate-traceability` | RTM coverage on changed spec folders |
| `lint-hooks` | `shellcheck --severity=warning` on all `hooks/*.sh` |
| `test-hooks` | All `hooks/test_*.py` unit tests |
| `plugin-install` | Builds `targets/` and checks `claude-plugin` manifest structure |

---

## Getting help

- Read `project_guides/BEST-PRACTICES.md` and `project_guides/AGENT-AUTHORING.md` before authoring new agents.
- Run `py -3 hooks/validate_graph.py` — it tells you exactly what's wrong.
- Stuck? Open a discussion issue with the `question` label.
