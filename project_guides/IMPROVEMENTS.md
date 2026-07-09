# Improvement Register — from the 2026-07-09 phase-by-phase audit

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Living |
| Source | Four-lens per-phase audit (Discovery→Process), synthesized 2026-07-09 |

> The audit's Tier-1 mechanization and quick contract fixes were **built** (see CHANGELOG
> Unreleased: `validate_gates.py`, requirement-quality lint, altitude coverage, bypass-edge
> prune, escaped-defect register, `/ops-metrics` maker, analytics→backlog edge). This
> register holds what was deliberately **deferred** — each item is cut-ready. Successor to
> the archived pilot-era register (`archive/IMPROVEMENTS.md`).

## Tier 2 — self-measurement (remaining)

| ID | Item | Phase | Effort | Notes |
|---|---|---|---|---|
| IMP-101 | `/plan-calibrate` — Actual column in the estimation template, estimate-error trend, reference-story re-anchoring | Planning | M | Estimation is the last open loop: velocity is tracked, per-item accuracy never is |
| IMP-102 | Cross-sprint action-item ledger — retro + postmortem + debt actions in one tracker with a completion rate | Process | M | Extends run-orchestrator's state pattern; turns "did retros change behavior?" into a number |
| IMP-106 | Tool-run telemetry — every hook appends `{tool, ts, rc}` to `.spindleloom/runs.jsonl`; `/ops-metrics` and a staleness check read it | Cross-phase | S | tools/skills audit N5 |
| IMP-107 | Board→RTM status pull — reverse tracker sync (the missing half of emit_backlog) so `/ops-status` reads real board state | Planning/Review | M | tools/skills audit N6 |
| IMP-108 | Skill-level evals — golden-transcript eval per skill (does requirement-quality measurably improve output?) mirroring FLEET-EVAL at skill granularity | Process | L | tools/skills audit N7 |
| IMP-105 | MCP parity for the new CLIs — `get_context_pack`, `check_gates`, `seed_rtm` as `sloom` tools so in-session agents need no Bash hop | Cross-phase | S/M | expanded per tools/skills audit N4 |
| IMP-104 | Flag loop-back forcing function — an upstream flag raised twice against the same doc becomes a blocking open-question (RAID-tracked) in that doc's next revision; today flags accumulate with no consequence (PRD audit story: 4 flags, 0 fixes across 2 eval runs) | Cross-phase | M | E2E run-2 judge finding |
| IMP-103 | Postmortem-action completion rate as a reliability SLI | Operate | S | Folds into IMP-102's ledger |

## Tier 3 — ownership orphans & parity gaps

| ID | Item | Phase | Effort | Notes |
|---|---|---|---|---|
| IMP-111 | Design-verifier — maker≠checker parity for design: runs the SDD/TSD REVIEW rubrics as a gate, emits a PRD-req→component coverage matrix | Design | M | Build got change-verifier; design self-reviews. The E2E run's SDD gaps would have been caught here |
| IMP-112 | Async/event-contract ownership — extend api-designer (or new agent) to message/event schemas | Design | M | The SDD's own worked example uses a broker; contract-first stops at REST/GraphQL |
| IMP-113 | Commands for the command-less specialists: `/plan-groom`, `/plan-replan`, `/slo`, `/runbook` (proactive) | Planning/Operate | S | The agent modes exist; they're just not exposed |
| IMP-114 | UAT coordination fold-in (qa-tester or test-plan-writer): entry/exit + sign-off loop | Test | S | UAT is listed as a level with no coordinator |
| IMP-115 | Architecture-review-board edge — label-triggered `architect` review for arch-significant PRs | Review | S | Today a prose convention in code-reviewer/security-reviewer |
| IMP-116 | Migration-coordination owner — data-modeler gains a release-phase edge + rehearsed-migration evidence artifact (feeds a `migration` sign-off token) | Release | S | "Migration rehearsed" is a checkbox nobody owns |

## Harness lane (from the 2026-07-10 harnessing audit)

| ID | Item | Phase | Effort | Notes |
|---|---|---|---|---|
| IMP-131 | Cursor `hooks.json` emission — port `on_md_edit` once Cursor's hook schema is verified against current docs | Harness | S | native support documented; schema unverified |
| IMP-132 | Copilot consumes the `claude-plugin` bundle directly (it now reads `.claude/*` natively) — retire the chatmode emission | Harness | M | the matrix's own simplification caveat |
| IMP-133 | Per-tool release smoke checklist — 10-min manual: install, list agents, fire one command, one MCP call, per harness | Harness | S | automatable only when the tools are |

## Tier 4 — new capability lanes (adopt per product scope)

| ID | Item | Phase | Effort | Notes |
|---|---|---|---|---|
| IMP-120 | `discovery-researcher` agent — customer interviews, JTBD, survey synthesis, problem-validation experiments | Discovery | M | The biggest role hole: mrd-writer does desk research only |
| IMP-121 | Discovery exit gate + MRD evidence/citation lint | Discovery | S/M | Mirror of the requirements-quality mechanization |
| IMP-122 | NFR completeness: i18n/l10n, data-retention, consent/DPIA rows in the SRS template + an nfr-elicitation skill; STRIDE pulled up to SRS time | Requirements | M | Security requirements currently elicited a phase late |
| IMP-123 | Infra/cloud-architect agent — topology, IaC, design-time cost/capacity estimate | Design | M | The deployment plane is named by SDD/TSD, owned by nobody |
| IMP-124 | Economic prioritization (RICE/WSJF) option in backlog-manager; quarter/roadmap planner bridging MRD→sprints | Planning | M | MoSCoW-only today; planning is sprint-local |
| IMP-125 | Perf/pentest execution lane — nightly stage running the SR-PERF/pentest cases test-plan-writer authors | Test | M | Cases are authored with no executor |
| IMP-126 | License-compliance gate consuming the SBOM pipeline-engineer already emits | Review | M | SBOM generated, never license-gated |
| IMP-127 | Feature-flag/experiment rollout owner — flag lifecycle ↔ release plan ↔ product-analytics cohorts | Release | L | Flags exist only as a rollback mention |
| IMP-128 | FinOps/cost-watch operate agent (cloud + LLM spend vs budget); on-call rotation + capacity/DR-drill ownership | Operate | M | Operate's biggest holes |
| IMP-129 | OKR/goal-tracking agent closing BRD outcomes → product metrics → backlog | Process | M | Nothing tracks goal attainment over time |
| IMP-130 | Pricing/monetization coverage (agent or MRD template section) | Discovery | M | Business-model gap feeding BRD ROI |

## Explicitly out of scope

- **Mobile development agent — N/A by decision (2026-07-09).** The fleet targets web/app + backend; frontend-developer stays web-scoped. Revisit only if a mobile product enters scope.
- Store/marketplace publishing (IMP-class, only if a client ships to app stores).

## Standing items carried from earlier sessions

- Real human-team pilot per `PILOT-PLAN.md` (verdict ADJUST — still the biggest validation gap).
- Drift gates or generation for the remaining hand-authored HTML guides (only the fleet page is gated).
- Consolidate `.spindleloom/` + `.spindleloom/` into one tool-state dir.
