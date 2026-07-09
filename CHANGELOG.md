# Changelog

All notable changes to Spindleloom. Format follows [Keep a Changelog](https://keepachangelog.com/); versions follow SemVer (pre-1.0: minor bumps may break).

## [0.3.0] — 2026-07-09

### ⚠ Breaking

- **Tool-state dir consolidated: `.shipwright/` → `.spindleloom/`** — one home for config, catalog, baselines, verifications, sign-offs, and the context DB. Legacy `.shipwright/` trees remain readable (config resolution and the registry follow whichever exists) and `scaffold.py migrate` renames them; new scaffolds create `.spindleloom/` only.
- **The Shipwright brand is retired** — `build_harness_artifacts.py` is now referred to plainly as the harness generator; the project brands as Spindleloom (with the `sloom` short form) plus the Loopwright loop layer.
- **MCP server renamed `spindleloom` → `sloom`** (short for Spindleloom): tools are now `mcp__sloom__<tool>`, resources `sloom://…`. Re-add the server under the new key (env vars `SPINDLELOOM_*` unchanged).
- **Plugin id renamed `spindleloom` → `sloom`**: install is now `/plugin install sloom@spindleloom`; commands surface as `/sloom:<command>`. The marketplace name stays `spindleloom`.
- **Commands reorganized into a phase taxonomy** (typeahead groups by funnel phase): `rtm-check→spec-check`, `adr-new→spec-adr`, `rfc→spec-rfc`, `constitution→spec-constitution`, `pbi-next→plan-next`.

### Added

- **Harness parity + conformance**: every tool now gets every surface it supports — Cursor gains native agents (`.cursor/agents/`, replacing 52 pseudo-agent rules), commands, and skills; Copilot gains prompt files (the 23 commands) and skills; Windsurf gains workflows, skills, and **auto-condensed rules** (3 agents previously shipped over the 12k truncation cap and were silently cut off); the loose claude-code target is complete (commands/skills/hooks). New `validate_targets.py` gate enforces per-tool format rules incl. bundled-hook import resolution, wired into `sloom check` and CI.
- **`sloom` unified CLI** (`hooks/sloom.py`): one front door — `sloom check` auto-detects toolkit vs adopter repo and runs the right gate battery; all tools reachable as subcommands.
- **The shipped plugin hook actually works now**: the old wiring crashed on a missing `rtm_core` import and `2>/dev/null || true` swallowed it — the plugin has never validated anything for adopters. v2 ships `on_md_edit.py` + its dependencies, filters to spec `.md` edits, runs traceability + RTM checks, and surfaces failures to the model (exit 2) instead of hiding them.
- **Four method skills** closing the methodless-agent gap: `test-data` (closes IMP-110's dangling pointer), `ux-design-method`, `defect-triage`, `analytics-instrumentation`; the register-keeper agents arm `agent-handoff-context`. Skill hygiene: stray auto-fire lines removed; the runbook structure now has one home (`reliability-template`).
- **`delete_context_entry(entry_id)`** — surgical single-entry deletion (ids now surfaced by `list_contexts`/`get_context`); the context store's 19th tool.
- **Context engineering, mechanized**: `hooks/build_context_pack.py` assembles a per-agent/task manifest (stamped contract inputs + digests, RTM slice, stale-flagged recalls, open assumptions, budget verdict); a `context-engineering` skill encodes the budget-first reading order and the `## Digest` producer convention; run-orchestrator dispatches packs, not folders; the emitted harness instructions teach recall-first reading.
- **Context maintenance mechanized**: `save_context` entries can cite a `source` artifact and `recall_context` flags them **stale** when the registry shows the artifact changed after the save; `validate_gates --context <task_id>` fails a run that passed work between agents without persisting handoff context; the run-state ledger records each step's saved entry; a context-layer boundary rule (docs = facts, context.db = working notes, run-state = orchestration) lands in AGENT-AUTHORING and the handoff skill; dev-onboarding seeds the `project-ops` operating manual; FLEET-EVAL now exercises and judges the context layer.
- **`examples/medremind-fleet-eval/`** — the eval's run-2 artifacts saved as the second worked example: chained agent output with handoff reports, judge verdict, living matrix RTM, and the assumption ledger in action.
- **E2E eval run 2: C+ → B+** — all four coordination fixes verified behaviorally (0 BROKEN handoffs, DoR blocked 10 unratified-assumption items). Follow-ups applied from the judge's findings: `frd-writer→sdd-writer` and `urs-writer→prd-writer` edges, matrix-tolerant `build_rtm` presence semantics, a full-ID (no range shorthand) rule, and a quality-lint exit bar on the five requirement writers.
- **Execution-quality gates mechanized** (`hooks/validate_gates.py` + tests): change-verifier verdicts persist to `.spindleloom/verifications/<PBI>.md` and are machine-checked (a PASS contradicting its own AC matrix fails); release go/no-go is a **computed AND** over `.spindleloom/signoffs/*.md` tokens written by the gate owners. The builder→pr-author bypass edges are pruned — the only path to PR now runs through the checker.
- **Requirement-quality lint** in `validate_reqs.py` (advisory; `--strict` blocks): the 29148 vague-adjective ban-list and compound-shall smell, applied at requirement-defining lines. RTM coverage now enforced at **every** altitude (`COVERED_DOCS` + BR/PRD/URS).
- **Escaped-defect register** (`templates/escaped-defect-register-template.md`) — every QA/prod escape names the gate that should have caught it; wired into qa-tester, incident-responder, and the retro. The test phase becomes self-measuring.
- **Engineering-metrics gets a maker**: `/ops-metrics` (pipeline-engineer) produces the DORA/cycle-time snapshot the status-reporter consumes; new contract edges `pipeline-engineer→status-reporter` and `product-analytics→backlog-manager` (a missed PRD metric can now spawn work).
- **Phase-audit improvement register** (`project_guides/IMPROVEMENTS.md`) — Tier 2-4 deferred items, cut-ready; mobile explicitly N/A.
- **Nine new commands** closing the funnel's command gap: `/build-recon`, `/build-verify`, `/plan-estimate`, `/plan-sprint`, `/plan-retro`, `/ops-status`, `/ops-raid`, `/ops-incident`, `/ship-release` — the weekly ceremonies and inner-loop gates now have first-class entry points (23 commands total).

## [0.2.0] — 2026-07-07

### ⚠ Breaking

- **Ten agents renamed** to fit the role-suffix taxonomy (`<artifact>-<role>`). Existing installs must re-run `install.py` / re-pull the plugin; old `subagent_type` names no longer resolve.

  | Old | New |
  |---|---|
  | `rfc` | `rfc-facilitator` |
  | `ci-cd-pipeline` | `pipeline-engineer` |
  | `coding-standards` | `coding-standards-writer` |
  | `raid-log` | `raid-keeper` |
  | `tech-debt-register` | `tech-debt-keeper` |
  | `tech-radar` | `tech-radar-curator` |
  | `incident-postmortem` | `incident-responder` |
  | `ai-orchestration` | `ai-orchestrator` |
  | `spec-driven-dev` | `spec-steward` |

  Artifact, template, and command names are unchanged (`coding-standards.md`, `/tech-radar`, `docs/rfc/`, …).
- **`chromadb` moved to the optional `semantic` extra** (`pip install spindleloom[semantic]` / `SPINDLELOOM_SEMANTIC=1`); the base install is stdlib-only again.

### Added

- **Contract fields `loop:` and `agentic_role:`** on all 52 agents — which delivery loop each agent tightens (LOOPWRIGHT §6) and its maker/checker-loop role. Surfaced as a "Loop · Role" column in the generated `agents/INDEX.md`.
- **Three new validator checks** in `validate_graph.py` (now 13): (11) loop-classification fields present with valid values; (12) `spindleloom-agent-fleet.html` node/edge data in sync with the contract graph; (13) **artifact-chain** — every handoff edge must carry a declared artifact (the check that would have caught the SRS→SDD and URS funnel breaks).
- **Coordination rules from the fleet E2E evaluation**: brd-writer materializes `docs/RTM.md` and every funnel writer appends its rows; the doc-strategy tier decision is binding routing for `run-orchestrator`; invented facts carry `ASSUMPTION-n` tags and a new DoR checkbox blocks unratified assumptions from sprint-committed AC.
- Local pre-commit gains the example-traceability gate (`validate_reqs` on `examples/`); drift-gate triggers broadened to `templates/` and `project_guides/`.

### Fixed

- **Shipwright now sweeps orphaned target files.** Renaming/removing a source agent left its old generated file in every `targets/<harness>/` bundle (this release's renames stranded 51 stale files — installs would have loaded both old and new agents). The generator now deletes files it no longer emits, and `--check` fails on orphans.
- **Contract-graph funnel breaks**: `sdd-writer` now declares SRS + recon inputs; the URS regulated branch is wired at both ends (`brd-writer → urs-writer`, URS consumed by frd/srs-writer); `tsd-writer` hands off to `backend-developer`/`pipeline-engineer`; the `backlog-manager`, `adr-writer`, `rfc-facilitator`, and 14 other agents now declare the artifacts their edges actually deliver.
- SEC/UX/A11Y IDs now have RTM columns; `qa-tester`/`accessibility-auditor` declare their `gate:`; role labels corrected (`performance-engineer`, `dev-onboarding` → maker).
- Four broken skill↔agent pairings re-armed; two orphan templates re-linked from their producing agents.
- Docs drift: `HOOKS.md` now documents the real 18-tool/4-resource MCP surface and all validator checks; ONBOARDING agent count; README guide paths; dangling SPEC-KIT-CROSSWALK references removed; ~70 legacy `project_managment_agents` paths corrected; orphaned `.wheelwright/` removed.
- Agent-definition hardening from the AEP gap register (evidence-standard, gate-integrity, ghost-blocker, autospec, executed-vs-inferred rules across 8 agents + the DoR/DoD template), generalized to be project-agnostic.

### Removed

- `.wheelwright/` (pre-rename tool state; superseded by `.shipwright/` + `.spindleloom/`).
