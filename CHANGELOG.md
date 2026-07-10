# Changelog

All notable changes to Spindleloom. Format follows [Keep a Changelog](https://keepachangelog.com/); versions follow SemVer (pre-1.0: minor bumps may break).

## [Unreleased]

## [0.5.0] - 2026-07-11

Documentation consolidation, a role-based field handbook, the Woven Loop brand, a browsable website, and five new anti-drift gates - layered on 0.4.0's platform. The fleet's contract graph is unchanged; the platform grows `sloom signoff` and a 9-gate `sloom check` battery.

### Added

- **Persona Field Handbook** (`spindleloom_website/personas/`): a single-file hub plus 15 standalone role pages (builder side + business side), each with the agents that role drives, copy-ready prompts, its I/O contract, the gates it owns, KPIs, hand-offs, troubleshooting and a glossary. The hub is a five-tab front door for all of `project_guides` — Start here, Personas, Phases (a 10-phase rail with gate owners), Prompt library (54 filterable prompts + the invoke primer), and a Guides directory.
- **Woven Loop identity** (`spindleloom_website/brand/`): the lemniscate SDLC mark, a run-ledger-driven live widget, and an animated loop hero on every persona/guide page (theme-aware canvas, `prefers-reduced-motion` respected). The mark is inlined in the fleet map and personas hub.
- **`knowledge_hub/GOVERNANCE.md`** — the merged governance standard: **STANDARD.md + STORY-CRAFT.md + TEAM-ROLES-AND-AZURE-DEVOPS.md + INFORMATION-ARCHITECTURE.md** consolidated into one file (Part I the layout standard, Part II story craft, Part III team + Azure DevOps), with the IA detail folded into Part I §§12-15. Old `STANDARD.md §N` maps 1:1 to `Part I §N`. A generated reading view ships as `governance-handbook.html`.
- **`knowledge_hub/claude-prompt-library.md`** (moved from repo root) — the generic Claude power-prompts, each mapped to the fleet specialist that does it better, plus the official prompt library and model-specific tips.
- **The website proper** (`spindleloom_website/`): a generated end-to-end homepage (`index.html` - woven-loop hero, six-stage journey, four machinery pillars, harness-target cards, full page map, live fleet counts), a single install-to-first-run **`get-started.html`** walkthrough, and generated **reading twins** for every knowledge_hub doc plus the root docs (README/INSTALL/CHANGELOG/CONTRIBUTING/ONBOARDING).
- **Five new anti-drift gates**, all `--check`-able and wired into `sloom check` (now 9 gates), pre-commit, and CI: `build_governance_handbook.py` (handbook view vs GOVERNANCE.md), `build_guides_site.py` (twins + homepage vs sources), `build_fleet_page.py` (**the fleet map's nodes/edges/descriptions/skills are now generated from the agent contracts** - closes IMP-141), `validate_counts.py` (no stale fleet numbers anywhere in the docs or site), `validate_personas.py` (the persona hub's agent/command refs resolve against the contracts). Plus `validate_graph` check 12b: the fleet page's skills map and lane phases are cross-checked against the contracts.
- **`sloom signoff <gate>`** - the release sign-off writer the approve/verify loop was missing: an evidence-required GO token (`--by` and `--evidence` mandatory for GO; `--release-id` namespacing) written to `.spindleloom/signoffs/`, round-tripping with `validate_gates --release`. Ships with `templates/signoff-token-template.md`.

### Changed

- **Repo restructure: `project_guides/` split into `knowledge_hub/` (the Markdown sources of truth) and `spindleloom_website/` (the browsable site: all HTML pages, personas, brand studies, and the generated reading twins).** Every citation, generator, validator, gate pattern and shipped-bundle path rewired; legacy `project_guides/*` markers kept in `scaffold.py` for pre-rename distributions.

- **`knowledge_hub/` segregated to one owner per fact** with a front-door `README.md` (Understand / Operate / Govern). The role-by-role surface is now the persona handbook; the fleet map gained a skills band, corrected index-edge counts, and a11y fixes.
- Fleet-map, overview, and guide pages carry the animated loop; guide pages link out rather than restating detail.
- **Fleet map UX**: site navigation, `/` search with #hash deep links, per-agent contract links, and a noscript fallback on `spindleloom-agent-fleet.html`.

### Fixed (six-perspective audit remediation)

- **Windows install actually works as documented**: INSTALL.md's POSIX-only steps replaced with `py -3` equivalents (`New-Item` over `touch`, `py -3 hooks/install.py`, pytest install), plus the missing scaffold step and corrected artifact counts.
- **Eval claims made honest**: FLEET-EVAL and the medremind example README now scope the B+ -> A progression to the 10-agent market-to-plan spine with an AI-judge qualifier, instead of implying a full-fleet evaluation.
- **Doc counts were drifting** (stale "50 templates", "52 commands" class of errors) - now impossible to merge, enforced by `validate_counts`.
- **Accessibility**: AA-contrast ink tokens on both themes, keyboard-operable loop hero (`role=button`), `prefers-reduced-motion` respected across all animated pages.
- Persona-hub prompt tags pointed at a nonexistent `developer` agent (now `backend-developer`); conceptual tags no longer masquerade as slash commands.

### Removed / archived

- `STANDARD.md`, `STORY-CRAFT.md`, `TEAM-ROLES-AND-AZURE-DEVOPS.md`, `INFORMATION-ARCHITECTURE.md` — merged into `GOVERNANCE.md`.
- `AI-2026-TRENDS-AND-COVERAGE.md` and the pre-personas `how-to-use.html` moved to `knowledge_hub/archive/`; `role-playbooks.html` removed after its unique content (artifact chain, prompt-ingredient model, MCP scenarios) was folded into the overview and the handbook.

## [0.4.0] — 2026-07-10

Platform hardening and context-engineering fidelity on top of the multi-user concurrency layer. Validated end-to-end: the MedRemind fleet-eval moved **B+ → A** across two behavioral runs (RUN 3 = A−, RUN 4 = A), every fix below confirmed by an independent judge rather than asserted.

### Added — multi-user concurrency + the phase-acceptance layer

- **Phase-boundary acceptance, mechanized** (the centerpiece): the four upstream phases (discovery, requirements, design, planning) had no gate but prose — now the accountable role records acceptance via **`sloom approve <phase> --feature <slug> --role <role> --by "<name>"`** → `.spindleloom/approvals/<feature>/<phase>.md`, enforced identically by `validate_gates --accepted <phase>`, `sloom run advance` (refuses to cross an unaccepted boundary), and run-orchestrator's runnable computation. Default phase→approver matrix overridable via config `"approvals"`; `--notify-tracker` mirrors the acceptance as a **comment** on the mapped Azure/Jira items (`add_comment()` in both adapters — comment-only; item state stays the tracker's). "Can I start?" becomes a file check, not a meeting — and because gates are files, an autonomous loop and a human teammate hit the same gates.
- **DUP-REQID collision gate**: two teammates on two branches independently minting the same Req-ID merged clean and silently collided — `audit()` now flags a same-kind double-mint (`rtm_core._DEFINING_KIND`); downstream citations (SDD citing an FRD id) are never false positives.
- **Shared context that actually crosses machines**: every `save_context` also appends to the committed, git-mergeable **`.spindleloom/context-log.jsonl`** (the cross-machine source of truth); `context.db` + `chroma/` become local rebuildable indexes (gitignored by scaffold). New **`sloom context <root> --import`** (`hooks/sync_context_log.py`) replays teammates' entries after a pull; `--export` backfills a pre-log DB; merge-mangled lines are skipped, not fatal.
- **Per-run + per-release namespacing**: run-state moves to **`.spindleloom/runs/<run-id>.json`** (one file pair per run — concurrent runs never clobber); release sign-offs gain **`--release-id`** (`signoffs/<release-id>/<gate>.md`) so two release trains never overwrite each other's tokens.
- **`sloom run status|advance <run-id>`** — a teammate checks/advances a distributed run without an LLM; `advance` refuses when a required upstream isn't done or a crossed phase boundary lacks acceptance (the graph is the gate, hand-editing can't skip it).
- **Idempotent tracker push + drift check**: both adapters now consult the RTM's committed mapping before creating (`skip PBI-X → #1234`; `--force-repush` overrides) — re-running `--apply` or a second teammate pushing no longer duplicates work items. New **`emit_backlog.py check`** reports NEW (unpushed) / GONE (orphaned) drift; wired into `sloom check`. Role rule: backlog-manager is the sole pusher, from merged `main` only.
- **The adopter CI gate** (`templates/ci/sloom-gate.yml`, written by scaffold/migrate to `.github/workflows/`): merging to `main` now *proves* the spec battery ran — incl. DUP-REQID and the per-PBI verification requirement when the branch names one. Previously no adopter repo got any gate workflow; "merged = gates passed" was a convention.
- **STANDARD.md §9 "Concurrency & ownership"** (now `GOVERNANCE.md` Part I §9): the resource-ownership table (owner role, namespace key, merge strategy, enforcing gate per shared resource), the 10-phase acceptance graph + approver matrix, and the branch=local / main=global / PR-merge=promotion model; §3's tree now annotates every `.spindleloom/` path committed-vs-local.

### Added — context engineering & fleet integrity

- **Transitive upstream routing** in `build_context_pack.py`: each agent's pack now includes its *phase-bounded transitive ancestor chain* (digest-first, deduped), so an agent sees the whole spec funnel above it — SDD sees the FRD, estimation sees the FRD/SRS — without adding N² contract edges. Fixed the run-2/3 class where a downstream agent silently drifted from an unrouted ancestor.
- **`sloom flags`** — an open-flags re-work register: a writer that hits a gap it can't fix leaves `FLAG(<owner-agent>): <what>`; `sloom flags` surfaces them grouped by owner (`--strict` gates), and `sloom run status` re-surfaces a flag whose owner is an already-`done` step as re-dispatchable re-work.
- **Backlog-completeness / phantom-PBI check** (`validate_reqs`): flags `PBI-UNDEFINED` for a PBI referenced (deps/RTM/sprint) but never *defined* by an acceptance-criteria-bearing backlog row — a class no ID/RTM check previously caught.
- **Machine-checkable quality gate**: a deliberate compound-shall must now carry a `<!-- quality-ok: <Req-ID> <reason> -->` marker to pass `--strict`; free-text justification no longer suppresses the lint. Range-shorthand lint extended to `…`/`...` ellipsis forms.
- **`code-minimalism` skill** (28th skill): the reuse→stdlib→native→one-line ladder + a `delete/stdlib/native/yagni/shrink` over-engineering review taxonomy, armed to code-reviewer and both developers.
- **`examples/medremind-fleet-eval/run3` + `run4`** — two more worked end-to-end runs (isolated 10-agent pipeline + independent judge verdict each), recording the B+ → A− → A progression and the fixes that drove it.

### Fixed

- **CI ran ~13 of 73 tests silently**: `pytest` was never installed in CI, so it fell through (`2>/dev/null ||`) to `unittest discover`, which collects only `TestCase`-based tests — a broken test passed green. CI now installs pytest and runs the full suite with no fallback; a dedicated MCP-server smoke-test job; HELP + handoff freshness gates; a full checkout for spec-traceability. Pre-commit mirrors the same gates.
- **Cross-platform UTF-8 mojibake**: printing hooks that lacked the `stdout.reconfigure(utf-8)` block rendered em-dashes as `?` on Windows (visible in the `sloom check` front door); added everywhere and repaired doubled-CR line endings.
- **Req-ID grammar unified**: `build_rtm` and `validate_reqs` shared `rtm_core.REQ_ID`, so they can no longer disagree about what counts as an ID.
- **Tracker push duplicated work items on retry / silent handoff drops**: partial-safe writeback (`try/finally` + atomic `os.replace`), tracker-agnostic mapping column, and stem-aware input resolution (`estimates` → `estimation.md`) that closes the last silent context-pack edge drop.
- **`PBI-ORPHAN` / `NO-RTM` false positives on commentary**: `rtm_core.markdown_files` excludes `verdict.md` / `README.md`, so a judge verdict quoting a prior run's id is never mistaken for a spec artifact.
- **`.shipwright` legacy-dir filter** restored in `validate_gates`; **stale counts** (skills/commands/templates) corrected across README/CONTRIBUTING/CLAUDE/PROJECT-OVERVIEW.

### Changed

- Scrubbed private pilot-log and internal package references out of shipped agents and `solution-recon` examples (they surfaced in generated user-facing prompts).
- Hoisted the duplicated Python-interpreter-detection block out of `change-verifier`/`test-author` into the `verification-run-and-observe` skill, generalized to "resolve the toolchain first"; armed `defect-triage` on `qa-tester` + `incident-responder`.

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
