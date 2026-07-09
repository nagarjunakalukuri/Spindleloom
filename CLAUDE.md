# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Spindleloom is **not an application** — it's a fleet of **52 role-specialist AI agents** (plus ~50 templates, 28 skills, 23 slash commands, self-validating Python hooks, and a traceability MCP server) that carry a product across the full SDLC (market → spec → design → build → test → ship → operate) as one traceable chain. The "code" here is mostly **Markdown-as-contract** (`agents/*.md`, `templates/*.md`, `skills/*/SKILL.md`, `commands/*.md`) plus **stdlib-only Python** in `hooks/` that validates and generates from it.

The product ships to end users as **harness-native bundles** under `targets/` — the same source is generated into Claude Code / Cursor / Copilot / Windsurf / AGENTS.md formats by `hooks/build_harness_artifacts.py`. `targets/` is **generated — never edit it by hand.**

## Core mental model

Every agent carries a machine-readable **contract block** in its frontmatter: `phase`, `inputs`, `outputs`, `upstream`, `downstream`, `skills`, `claude_code`, `rtm_column`. This contract is the single source of truth. Two kinds of derived artifacts are generated *from* it, then a validator checks they stay consistent:

- **Generators** (`build_agent_index.py`, `build_handoffs.py`, `build_help.py`, `build_harness_artifacts.py`) derive `agents/INDEX.md`, the per-agent Handoff blockquote, `agents/HELP.md`, and `targets/`.
- **`validate_graph.py`** runs 12 checks — chiefly **contract-graph symmetry** (every agent you list in `downstream` must list you in their `upstream`, and vice versa), no dangling refs, no missing skills, INDEX freshness, `claude_code:` mapping integrity, and harness-data sync.

The consequence: after **any** agent/skill/command change, you must re-run the generators and the validator, or CI (and pre-commit) will fail. This is the most common way to break the build.

## Commands you will use most

Hooks are stdlib-only Python — no install needed for the core loop. On Windows use `py -3`; on macOS/Linux use `python3`. The one command to remember is the front door:

```bash
py -3 hooks/sloom.py check      # auto-detects repo type and runs the right battery
```

In *this* repo (the toolkit), `sloom check` runs the fleet battery: graph symmetry + handoff freshness + bundle drift. In an *adopter's* repo it runs the spec battery (reqs + RTM + registry + gates). `sloom reqs|rtm|gates|pack|registry|context|run|approve|scaffold|backlog|graph|targets|index` forward to the underlying tools. The `run`/`approve`/`context` trio drives the multi-user concurrency + phase-acceptance layer: `sloom run` is the distributed-run ledger (status/advance), `sloom approve` writes a phase-boundary acceptance token, and `sloom context` imports/exports handoff context across a pull.

The full fleet-integrity loop after editing an agent/skill/command:

```bash
py -3 hooks/build_agent_index.py         # refresh agents/INDEX.md
py -3 hooks/build_handoffs.py            # refresh each agent's Handoff blockquote
py -3 hooks/build_help.py                # refresh agents/HELP.md
py -3 hooks/build_harness_artifacts.py   # regenerate targets/ bundles
py -3 hooks/validate_graph.py            # 12 integrity checks (must exit 0)
```

Drift checks (what CI enforces — exit 1 = stale, regenerate):

```bash
py -3 hooks/build_harness_artifacts.py --check   # targets/ not stale vs source
py -3 hooks/build_handoffs.py --check            # handoff lines not stale
py -3 hooks/validate_targets.py                  # per-harness format conformance
```

### Tests

```bash
py -3 -m pytest hooks/ -q                              # all hook unit tests
py -3 -m pytest hooks/test_validate_graph.py -q        # one test file
py -3 -m pytest hooks/test_sloom.py -q -k check         # a single test by name
```

**`pytest` is required to run the real suite** — install it (`py -3 -m pip install pytest`, or `uv sync --group dev`). The tests are pytest-style bare `def test_*` functions with plain asserts. `py -3 -m unittest discover -s hooks` is **not** an equivalent fallback: it only collects the handful of `unittest.TestCase`-based tests (~13 of ~73) and reports `OK` while silently skipping the rest — so a regression can pass it. Don't trust a green from `unittest discover`.

`pytest` and the MCP SDK are dev-only deps. With `uv`: `uv run python -m pytest hooks/ -q` (the `dev` group installs `mcp[cli]` automatically). Shell hooks are linted with `shellcheck --severity=warning hooks/*.sh`.

### MCP server

```bash
uv run python hooks/test_mcp_server.py    # exercise the server offline
uv run mcp dev hooks/mcp_server.py        # run it interactively
```

`mcp_server.py` (FastMCP) is the **only** component with a required dependency (`mcp[cli]`; `chromadb` optional, behind `SPINDLELOOM_SEMANTIC=1`). It reads `$SPINDLELOOM_SPEC_ROOT`; write tools are gated behind `SPINDLELOOM_WRITABLE=1`. Everything else — `rtm_core`, validators, generators — stays stdlib-only on purpose so any team can run them with zero install.

## Repo layout

| Path | What lives here |
|---|---|
| `agents/` | 52 agent definitions — one `.md` each; frontmatter is the contract. `INDEX.md`/`HELP.md` are **generated**. |
| `skills/` | 28 methodology skills — one `<name>/SKILL.md` each; armed to agents via their `skills:` array |
| `templates/` | ~50 blank document templates (agents fill these into adopter repos) |
| `commands/` | 23 slash commands (`/run`, `/spec-new`, `/plan-next`, `/build-verify`, …) wired via each agent's `claude_code:` block |
| `hooks/` | stdlib-only Python: validators, generators, the MCP server, tracker adapters; `*.sh` are SSRF-safe URL-cache hooks; `test_*.py` are their unit tests |
| `targets/` | **Generated** harness bundles (claude-plugin, claude-code, cursor, copilot, windsurf, agents-md) — do not hand-edit |
| `project_guides/` | The authoritative conventions (see below) |
| `examples/` | Full end-to-end runs — `healthy-meal-app` (polished exemplar) and `medremind-fleet-eval` (honest behavioral E2E) |
| `.claude-plugin/` | This repo's own plugin `marketplace.json` |

## Where the conventions live (read before editing the relevant surface)

- **`project_guides/AGENT-AUTHORING.md`** — the contract-block schema and prompting conventions. **Read this before creating or editing any agent.**
- **`project_guides/STANDARD.md`** — the authoritative, versioned layout standard for adopter repos (the `docs/` + `.spindleloom/` tree, profiles, cadence planes, ID immutability). `INFORMATION-ARCHITECTURE.md` is its detailed reference.
- **`project_guides/BEST-PRACTICES.md`** — the funnel, feedback loops, team-size tiers, the requirement-quality standard (ISO/IEC/IEEE 29148 + INCOSE, the "system shall" rule), and the Req-ID traceability backbone.
- **`project_guides/HARNESS-MATRIX.md`** — the 7-surface × 4-tool matrix that `build_harness_artifacts.py` targets. Consult when changing what generates into `targets/`.
- **`hooks/HOOKS.md`** — reference for every hook, including how to wire them as Claude Code hooks or CI gates.

## Adding or editing an agent (the workflow that keeps the graph valid)

1. Copy an existing agent's structure. Fill the full frontmatter contract block per `AGENT-AUTHORING.md`.
2. **Add reciprocal edges**: every agent in your `downstream` must list you in their `upstream`, and vice versa. `validate_graph.py` catches asymmetry — fix it before committing.
3. Re-run the generators + validator (the loop above).
4. Update the fleet count in `README.md`.

Adding a skill: create `skills/<kebab-name>/SKILL.md`, arm it to ≥1 agent's `skills:` array, run `validate_graph.py` (it checks every declared skill resolves to a file), bump the count in `README.md`.

Before proposing a *new* agent/skill/template, grep for near-duplicates first (`grep -ri "your-topic" agents/ skills/ -l`; check `agents/INDEX.md`) — the review bar is "don't create overlap." See `CONTRIBUTING.md`.

## CI / pre-commit gates (must be green to merge)

Pre-commit (`.pre-commit-config.yaml`) and GitHub Actions (`.github/workflows/test-plugin-install.yml`) both enforce: `validate_graph.py`, INDEX freshness, harness bundle non-staleness (`--check`), `validate_targets.py`, `validate_reqs.py` on changed spec folders, `shellcheck` on `hooks/*.sh`, and the full `pytest` hook suite. `spindleloom-refresh.yml` is a self-healing weekly job that opens a PR if derived artifacts have drifted.

## Conventions

- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`), one concern each.
- **Branches**: from `main`, named `feature/<slug>` or `fix/<slug>`.
- Keep new hooks **stdlib-only**; isolate any required dependency the way `mcp_server.py` does.
- Shell hooks must mirror the `validate_url()` SSRF guard from `sdd-cache-pre.sh` and use `--max-redirs 0` on any `curl`.
