# Changelog

All notable changes to Spindleloom. Format follows [Keep a Changelog](https://keepachangelog.com/); versions follow SemVer (pre-1.0: minor bumps may break).

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
