# Spindleloom — Project Overview

> **Purpose of this file:** a complete, single-file orientation so a new session (human or agent) can be productive without reading the whole repo. It summarizes *what* Spindleloom is, *how* it's built, the *commands*, the *architecture*, and *where to go* for detail. Current version: **0.3.0** (2026-07-09). Pre-1.0 — minor bumps may break.

---

## 1. What this is (in one paragraph)

Spindleloom is **not an application** — it's a **tool-agnostic fleet of 52 role-specialist AI agents** (plus **28 skills**, **51 document templates**, **23 slash commands**, stdlib-Python **hooks**, and a **traceability MCP server**) that carry a product across the entire software development lifecycle — market → spec → design → build → test → ship → operate — as *one traceable chain*. Each agent owns one role, reads the artifact above it, hands off to the next, and pushes discoveries back upstream. Teams run only the subset they need. The whole fleet is authored once as Markdown-with-contracts and **generated into harness-native bundles** (Claude Code, Cursor, Copilot, Windsurf, AGENTS.md) under `targets/`.

**Three layers to keep straight:**
- **Spindleloom** — the agent fleet that builds the SDLC wheel (this repo's source).
- **The harness generator** (`hooks/build_harness_artifacts.py`) — ships the fleet to every AI coding tool as `targets/<harness>/` bundles.
- **Loopwright** (`project_guides/LOOPWRIGHT.md`) — the delivery-feedback-loop layer the agents run inside and tighten.

---

## 2. The funnel (the spec chain)

The document spine runs as a waterfall from 30,000 feet (business) to the trenches (code) — each doc refines the one above and hands off to the one below:

```
              ┌─────────────────────────────────────────────┐
 CONSTITUTION │  durable law: principles, boundaries,        │  (above the funnel;
 (/spec-      │  non-goals — holds across ALL features       │   built once, versioned)
  constitution)└─────────────────────────────────────────────┘
                              │  (governs every release)
                              ▼
   MRD → BRD → PRD → FRD → SRS → SDD → TSD          ← the 7-document spine
   ▲                                    │            (each ↓ hands off,
   └──────── feedback loops ────────────┘             each ▲ flows back up)
```

**The spine is bidirectional, not a pure waterfall.** Handoffs flow *down*, but discoveries flow *back up* via four named loops (BEST-PRACTICES §"Feedback loops"):
- **Reality-check** (SDD → PRD/SRS) — an architect finds a requirement impossible/too costly; force a scope change upstream rather than quietly miss it.
- **Scope-adjustment** (SRS/FRD → PRD) — constraints found during spec change what's realistic this release.
- **Budget/timeline** (any stage → BRD) — cost/effort surprises can shift the business case itself.
- **Parallel-work** (SRS/FRD → Dev + QA) — the instant SRS/FRD is final, devs build from the SDD while QA writes tests from the SRS off the same source of truth.

**Off-spine entry & decision agents:**
- **Constitution** (`templates/constitution-template.md`, `/spec-constitution`) sits *above* the funnel — the standing, AI-read-first guardrails. The funnel describes *this release*; the constitution describes *the system's durable law*.
- **URS-writer** — the *regulated/validated-systems* entry point (ISPE/GAMP, FDA 21 CFR 820.30). Entered after BRD, runs parallel to PRD, and feeds **PRD + FRD + SRS**.
- **RFC → ADR decision loop** — a significant change that needs debate *before* building is raised as an **RFC** (`rfc-facilitator`, `/spec-rfc`, opened for comment in `/docs/rfc`); an *accepted* RFC produces an **ADR** (`adr-writer`, `/spec-adr`) — one immutable, append-only record per decision in `/docs/adr` (superseded, never edited). ADR-writer runs continuously as decisions are made.

**Alongside the funnel** run the engineering-craft lanes the doc spine only touches generically — `ux-ui-designer` (design phase), `security-reviewer` (continuous), `sre` (operate) — plus `accessibility-auditor`, `performance-engineer`, `product-analytics`, and `ai-eval` by need. These are *not* in the spec spine.

You rarely need all documents. Start with **doc-strategy-advisor** to pick the right set by team size (Lean/Mid/Enterprise), then **spec-steward** keeps whatever you keep from drifting.

Everything is tied together by a **Requirement Traceability Matrix (RTM)** — `docs/RTM.md`, materialized by brd-writer and appended to by every funnel writer. Req-IDs follow `<DOC>-<AREA>-<NUM>` and are immutable.

---

## 3. The 52 agents, by lifecycle phase

Navigate by *when you run it*, not by theme. Full machine-readable index (auto-generated): [`agents/INDEX.md`](agents/INDEX.md). Per-agent "how do I use this" surface: [`agents/HELP.md`](agents/HELP.md).

| Phase | Agents |
|---|---|
| **Discovery** | doc-strategy-advisor · mrd-writer |
| **Requirements** | brd-writer · prd-writer · frd-writer · srs-writer · urs-writer |
| **Design** | sdd-writer · tsd-writer · api-designer · data-modeler · ux-ui-designer · architect · rfc-facilitator · adr-writer · solution-recon |
| **Planning** | backlog-manager · estimation-facilitator · sprint-planner |
| **Build** | frontend-developer · backend-developer · coding-standards-writer · dev-onboarding · ai-orchestrator · pr-author |
| **Test** | test-plan-writer · test-author · test-automation-engineer · change-verifier · qa-tester · debugger · bug-triager · flaky-test-detective · accessibility-auditor · ai-eval |
| **Review** | code-reviewer · security-reviewer · performance-engineer · raid-keeper · status-reporter |
| **Release** | pipeline-engineer · release-manager |
| **Operate** | sre · incident-responder |
| **Process (always-on / cross-cutting)** | spec-steward · run-orchestrator · wiki-curator · feature-docs-writer · product-analytics · retrospective-facilitator · tech-debt-keeper · tech-radar-curator |

**Key orchestration agents:**
- **run-orchestrator** (`/run`) — the conductor. Reads the contract graph + a run-state spine, proposes the next runnable agent (upstreams done + gate passed), enforces the stop contract, dispatches with confirmation. Makes the implicit funnel an explicit, resumable run.
- **change-verifier** (`/build-verify`) — the maker/checker execution gate. *Runs* a change against its acceptance criteria (build, tests, lint, smoke), returns PASS/FAIL with an AC coverage matrix. Has no Write/Edit. Red → debugger. The **only** path from builder to PR now runs through it.
- **solution-recon** (`/build-recon`) — brownfield ground-truth. Reads the codebase before a spec/PBI is accepted; feeds *verified facts* to the writers and flags spec↔code mismatches.

**Entry points (no inbound handoff — invoked directly / always-on):** ai-orchestrator, coding-standards-writer, dev-onboarding, run-orchestrator, spec-steward.

---

## 4. The core mental model (read this before editing anything)

Every agent's frontmatter carries a **machine-readable contract block**: `phase`, `inputs`, `outputs`, `upstream`, `downstream`, `skills`, `claude_code`, `rtm_column`, `loop`, `agentic_role`. **This contract is the single source of truth.** Two families of artifacts are derived *from* it, then a validator checks they stay consistent:

```
                    ┌─── build_agent_index.py ──→ agents/INDEX.md
  agent contract    ├─── build_handoffs.py    ──→ per-agent "Handoff" blockquote
  block (frontmatter)├─── build_help.py        ──→ agents/HELP.md
  = SINGLE SOURCE    └─── build_harness_artifacts.py ──→ targets/<harness>/ bundles
                                        │
                                        ▼
                     validate_graph.py — 12 checks prove the above stayed consistent
```

**`validate_graph.py`'s 12 checks** (the fleet eating its own docs-as-code): (1) contract-graph **symmetry** — every agent in your `downstream` must list you in their `upstream`, and vice versa; (2) no dangling refs; (3) no missing skills; (4) INDEX freshness; (5) handoff line present; (6) examples present; (7) `claude_code:` mapping integrity; (8) command well-formedness; (9) armed skills are model-invocable; (10) no orphan agents outside the entry-point allowlist; (11) loop/role classification valid; (12) fleet-HTML node/edge data in sync.

**The #1 way to break the build:** editing an agent without re-running the generators + validator. CI and pre-commit both gate on it.

---

## 5. Commands you will actually use

Hooks are **stdlib-only Python** — no install needed for the core loop. On **Windows use `py -3`** (bare `python`/`python3` are not on PATH here); on macOS/Linux use `python3`.

### The one command to remember — the front door
```bash
py -3 hooks/sloom.py check      # auto-detects repo type, runs the right gate battery
```
In *this* repo (the toolkit) → fleet battery: graph symmetry + handoff freshness + bundle drift.
In an *adopter* repo → spec battery: reqs + RTM + registry + gates.
Subcommands forward unchanged: `sloom reqs|rtm|gates|pack|registry|context|run|approve|scaffold|backlog|graph|targets|index`.
`run` (distributed-run ledger), `approve` (phase-acceptance token), and `context` (handoff-log import/export) drive the multi-user concurrency layer.

### After editing an agent / skill / command — the full resync loop
```bash
py -3 hooks/build_agent_index.py         # refresh agents/INDEX.md
py -3 hooks/build_handoffs.py            # refresh each agent's Handoff blockquote
py -3 hooks/build_help.py                # refresh agents/HELP.md
py -3 hooks/build_harness_artifacts.py   # regenerate targets/ bundles
py -3 hooks/validate_graph.py            # 12 integrity checks — must exit 0
```

### Drift / conformance checks (what CI enforces — exit 1 = stale)
```bash
py -3 hooks/build_harness_artifacts.py --check   # targets/ not stale vs source
py -3 hooks/build_handoffs.py --check            # handoff lines not stale
py -3 hooks/validate_targets.py                  # per-harness format conformance
```

### Tests
```bash
py -3 -m pytest hooks/ -q                          # all hook unit tests
py -3 -m pytest hooks/test_validate_graph.py -q    # one test file
py -3 -m pytest hooks/test_sloom.py -q -k check    # a single test by name
py -3 -m unittest discover -s hooks -p 'test_*.py' # fallback if pytest unavailable
```
With `uv`, the `dev` group auto-installs `mcp[cli]`: `uv run python -m pytest hooks/ -q`.

### Shell hooks
```bash
shellcheck --severity=warning hooks/*.sh
```

### MCP server
```bash
uv run python hooks/test_mcp_server.py    # exercise offline
uv run mcp dev hooks/mcp_server.py        # run interactively
```

### Adopter-repo commands (run against a *project* root, not this repo)
```bash
py -3 hooks/scaffold.py <root>            # lay down docs/ + .spindleloom/ tree (idempotent)
py -3 hooks/scaffold.py migrate <root>    # convert an existing repo / rename legacy .shipwright/
py -3 hooks/validate_reqs.py <spec-dir>   # RTM traceability + requirement-quality lint
```

---

## 6. Repository layout

| Path | What lives here |
|---|---|
| `agents/` | **52** agent definitions — one `.md` each; frontmatter is the contract. `INDEX.md` / `HELP.md` are **generated** — do not hand-edit. |
| `skills/` | **27** methodology skills — one `<name>/SKILL.md` each; armed to agents via their `skills:` array (e.g. `requirement-quality`, `traceability-rtm`, `context-engineering`, `systematic-debugging`). |
| `templates/` | **51** blank document templates agents fill into adopter repos (mrd → tsd, adr, rfc, backlog, sprint, raid, test-plan, threat-model, a11y-audit, constitution, run-state, …). |
| `commands/` | **23** slash commands wired to agents via each agent's `claude_code:` block. Phase-grouped: `spec-*`, `plan-*`, `build-*`, `ops-*`, `ship-*`, `tech-*`, `/run`, `/test-plan`, `/help-role`. |
| `hooks/` | stdlib-only Python: validators, generators, the MCP server, tracker adapters (Jira/Azure), the `sloom` CLI, scaffold. `*.sh` are SSRF-safe URL-cache hooks. `test_*.py` are unit tests. Reference: [`hooks/HOOKS.md`](hooks/HOOKS.md). |
| `targets/` | **Generated** harness bundles: `claude-plugin`, `claude-code`, `cursor`, `copilot`, `windsurf`, `agents-md`. **Never edit by hand.** |
| `project_guides/` | Authoritative conventions + human-facing HTML guides (see §8). |
| `examples/` | End-to-end runs: `healthy-meal-app` (polished exemplar) and `medremind-fleet-eval` (honest behavioral E2E, graded C+ → B+). |
| `.claude-plugin/` | This repo's own plugin `marketplace.json`. |
| `.github/workflows/` | CI (`test-plugin-install.yml`) + self-healing weekly refresh (`spindleloom-refresh.yml`). |

---

## 7. The hooks (what each does)

All stdlib-only and read-only unless noted. Full detail in [`hooks/HOOKS.md`](hooks/HOOKS.md).

| Hook | Role |
|---|---|
| `sloom.py` | **The front door** — one CLI over every tool; `sloom check` auto-detects repo type. |
| `validate_graph.py` | Fleet integrity — the 12 checks (§4). CI/pre-commit gate. |
| `validate_reqs.py` | Req-ID format, dup/orphan detection, RTM coverage, ADR-ref integrity + 29148 quality lint (`--strict` blocks). |
| `validate_gates.py` | Execution-quality gates — change-verifier PASS artifacts (`.spindleloom/verifications/`); release go/no-go = computed AND over `.spindleloom/signoffs/*.md`. |
| `validate_targets.py` | Per-harness format conformance (Windsurf 12k rule cap, frontmatter, bundled-hook import resolution). |
| `build_agent_index.py` / `build_handoffs.py` / `build_help.py` | Generators derived from the contract block. |
| `build_harness_artifacts.py` | **The harness generator** — one source → 6 tool-native bundles + per-tool `.mcp.json`. `--check` = drift gate. |
| `build_rtm.py` / `build_artifact_registry.py` / `build_context_pack.py` | RTM seeder · artifact catalog (`.spindleloom/artifacts.json` + `ARTIFACTS.md`) · per-agent/task context manifest. |
| `rtm_core.py` | Shared traceability + artifact parser (library; imported by validator, registry, MCP — one parser, no drift). |
| `scaffold.py` | Lays down / migrates the canonical adopter layout (tier-aware, idempotent). |
| `emit_backlog.py` + `jira_adapter.py` / `azure_boards_adapter.py` | backlog.md → tracker work items. **Dry-run by default; network writes only with `--apply` + creds.** |
| `mcp_server.py` | The MCP server (see §9). |
| `sdd-cache-pre.sh` / `sdd-cache-post.sh` | SSRF-safe TTL cache for remote spec-doc fetches (blocks non-http(s) + RFC-1918/loopback; `--max-redirs 0`). |
| `on_md_edit.py` | The shipped plugin's PostToolUse hook — filters to spec `.md` edits, runs traceability + RTM, surfaces failures (exit 2). |

---

## 8. Where the conventions live (read before editing that surface)

- **`project_guides/AGENT-AUTHORING.md`** — contract-block schema + prompting conventions. **Read before creating/editing any agent.**
- **`project_guides/STANDARD.md`** — the authoritative, versioned adopter layout (the `docs/` + `.spindleloom/` tree, profiles, four cadence planes, ID immutability). Greenfield scaffolds it; brownfield converts via `scaffold.py migrate`.
- **`project_guides/INFORMATION-ARCHITECTURE.md`** — the detailed reference under STANDARD (where artifacts live, the four retrieval paths: RTM · catalog · MCP · wiki).
- **`project_guides/BEST-PRACTICES.md`** — the funnel, feedback loops, team-size tiers, requirement-quality standard (ISO/IEC/IEEE 29148 + INCOSE, the "system shall" rule), traceability backbone, change control, frameworks (arc42, C4, Diátaxis).
- **`project_guides/HARNESS-MATRIX.md`** — the 7-surface × 4-tool matrix that the generator targets.
- **`project_guides/LOOPWRIGHT.md`** — the delivery-loop layer; the `loop:` contract field maps each agent to the loop it tightens.
- **`project_guides/FLEET-EVAL.md`** — the behavioral regression test (chained contract-strict E2E + independent judge).
- **`hooks/HOOKS.md`** — every hook, plus how to wire them as Claude Code hooks or CI gates.
- **Human-facing HTML** (open in a browser): `how-to-use.html` (role-by-role + sample prompts), `for-everyone.html` (plain-language overview), `spindleloom-agent-fleet.html` (the interactive graph), `role-playbooks.html`.

---

## 9. The MCP server

`hooks/mcp_server.py` (FastMCP) is the **only** component with a required dependency (`mcp[cli]`; `chromadb` optional). Everything else stays stdlib-only on purpose. Under 0.3.0 the server key is **`sloom`** (tools surface as `mcp__sloom__<tool>`, resources as `sloom://…`).

- **12 traceability/catalog/conformance tools**: `trace_requirement`, `rtm_coverage`, `list_requirements`, `find_decision`, `list_artifacts`, `find_artifact`, `funnel_status`, `stale_artifacts`, `next_req_id`, `search_specs`, `check_conformance`, `scaffold_project` (gated behind `SPINDLELOOM_WRITABLE=1`).
- **7 agent-context-memory tools**: `save_context`, `recall_context`, `list_contexts`, `get_context`, `delete_context`, `delete_context_entry`, `sync_contexts` (SQLite in `.spindleloom/context.db`; semantic search behind `SPINDLELOOM_SEMANTIC=1`).
- **4 resources**: `rtm://current`, `sloom://requirements`, `sloom://artifacts`, `sloom://decisions`.
- Reads `$SPINDLELOOM_SPEC_ROOT`. Env vars are still `SPINDLELOOM_*` (unchanged across the rename).

---

## 10. How to add things (the workflows that keep the graph valid)

**Add/edit an agent:** copy an existing agent's structure → fill the full contract block per `AGENT-AUTHORING.md` → **add reciprocal handoff edges** (downstream ↔ upstream must be symmetric) → run the §5 resync loop → update the count in `README.md`. Before proposing a *new* agent, grep for near-duplicates (`grep -ri "your-topic" agents/ -l`, check `INDEX.md`); the review bar is "don't create overlap."

**Add a skill:** create `skills/<kebab-name>/SKILL.md` → arm it to ≥1 agent's `skills:` array → `validate_graph.py` (checks every declared skill resolves) → bump count in `README.md`.

**Add a shell hook:** `#!/usr/bin/env bash` + `set -euo pipefail` → mirror the `validate_url()` SSRF guard from `sdd-cache-pre.sh` → `--max-redirs 0` on all `curl` → `shellcheck --severity=warning` → add a row to `hooks/HOOKS.md`.

---

## 11. CI / pre-commit gates (must be green to merge)

Both `.pre-commit-config.yaml` and `.github/workflows/test-plugin-install.yml` enforce:

| Gate | Checks |
|---|---|
| `validate-fleet` | `validate_graph.py`, INDEX freshness, `build_harness_artifacts.py --check`, `validate_targets.py` |
| `validate-traceability` | `validate_reqs.py` on changed spec folders (RTM.md diffs) |
| `lint-hooks` | `shellcheck --severity=warning` on `hooks/*.sh` |
| `test-hooks` | full `pytest` suite (`hooks/test_*.py`) |
| `plugin-install` | builds `targets/`, verifies the `claude-plugin` manifest + ≥40 agents in bundle |

`spindleloom-refresh.yml` is a self-healing weekly job that regenerates derived artifacts and opens a PR if anything drifted (from a manual edit, a `--no-verify` bypass, or a UI merge).

---

## 12. Conventions

- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`), one concern each.
- **Branches:** from `main`, named `feature/<slug>` or `fix/<slug>`.
- **PRs:** use `templates/pr-template.md`; keep reviewable; CI must be green.
- Keep new hooks **stdlib-only**; isolate any required dependency the way `mcp_server.py` does.
- **Tool-state dir is `.spindleloom/`** (legacy `.shipwright/` still readable; `scaffold.py migrate` renames it).

---

## 13. Fastest path to understanding

1. Read `examples/healthy-meal-app/` — a full MRD→TSD run tied by one RTM. The quickest way to see how documents interlock.
2. Skim `README.md` (fleet overview) and `project_guides/AGENT-AUTHORING.md` (how agents are written).
3. Try it live: ask Claude to "write a BRD for &lt;a feature&gt;" and watch the handoffs down the funnel; then run `py -3 hooks/validate_graph.py` to see the integrity checks.
