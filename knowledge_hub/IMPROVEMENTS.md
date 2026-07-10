# Improvement Register — from the 2026-07-09 phase-by-phase audit

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Living |
| Source | Four-lens per-phase audit (Discovery→Process), synthesized 2026-07-09 |

> The audit's Tier-1 mechanization and quick contract fixes were **built** (see CHANGELOG
> 0.3.0: `validate_gates.py`, requirement-quality lint, altitude coverage, bypass-edge
> prune, escaped-defect register, `/ops-metrics` maker, analytics→backlog edge). This
> register holds what was deliberately **deferred** — each item is cut-ready. Successor to
> the archived pilot-era register (`archive/IMPROVEMENTS.md`).

## Tier 2 — self-measurement (remaining)

| ID | Item | Phase | Effort | Notes |
|---|---|---|---|---|
| IMP-101 | `/plan-calibrate` — Actual column in the estimation template, estimate-error trend, reference-story re-anchoring | Planning | M | Estimation is the last open loop: velocity is tracked, per-item accuracy never is |
| IMP-102 | Cross-sprint action-item ledger — retro + postmortem + debt actions in one tracker with a completion rate | Process | M | Extends run-orchestrator's state pattern; turns "did retros change behavior?" into a number |
| IMP-106 | Tool-run telemetry — every hook appends `{tool, ts, rc}` to `.spindleloom/telemetry.jsonl`; `/ops-metrics` and a staleness check read it | Cross-phase | S | tools/skills audit N5; path renamed — `.spindleloom/runs/` is now the v0.4.0 run-ledger namespace |
| IMP-107 | Board→RTM status pull — reverse tracker sync (the missing half of emit_backlog) so `/ops-status` reads real board state | Planning/Review | M | tools/skills audit N6 |
| IMP-108 | Skill-level evals — golden-transcript eval per skill (does requirement-quality measurably improve output?) mirroring FLEET-EVAL at skill granularity | Process | L | tools/skills audit N7 |
| IMP-105 | MCP parity for the new CLIs — `get_context_pack`, `check_gates`, `seed_rtm` as `sloom` tools so in-session agents need no Bash hop | Cross-phase | S/M | expanded per tools/skills audit N4 |
| IMP-104 | Pipeline re-entrancy — the chain is single-pass: an upstream fix landed after downstream docs exist needs a second orchestration pass that re-opens the affected downstream steps, and security-reviewer belongs in-chain at SDD time. Residual from the original flag item: within-run closure (a flag raised twice against the same doc becomes a blocking, RAID-tracked open question). The surfacing half shipped in v0.4.0 (`sloom flags` + the run-ledger re-work loop; run-4 verdict grades flag loop-back PARTIAL) | Cross-phase | M | E2E run-4 headline finding (supersedes the run-2 wording) |
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

- Real human-team pilot per `archive/PILOT-PLAN.md` (verdict ADJUST — still the biggest validation gap).
- Drift gates or generation for the remaining hand-authored HTML guides — only the fleet page is gated; `for-everyone.html` is hand-authored and ungated, and `governance-handbook.html` is generated from `GOVERNANCE.md` but its generator is not yet a hook with a `--check` gate.

## Six-perspective gap audit (2026-07-10)

Six parallel subagents traced one stakeholder journey each (reader · installer · operator · contributor · maintainer · skeptic) through the live repo, running the real gates. Structural spine verified sound (6 gates green, ~30 GOVERNANCE citations resolve). The gaps below cluster in two layers: the hand-authored HTML/doc surface (already drifting from source), and behavioral/freshness claims that outrun evidence. IMP-140+ track the items not fixed in the same session.

### The root cause — facts hand-restated with no generation link (highest leverage)

- **IMP-140** | Count-consistency gate — a stdlib `--check` that computes real fleet counts (agents/templates/skills/commands) and fails on any stale count string in README / PROJECT-OVERVIEW.md / project-overview.html / for-everyone.html / CLAUDE.md. Counts had already drifted (PROJECT-OVERVIEW §1 "28" vs §6 "27"; project-overview.html hero 28/23 vs body 22/13). | Cross-phase | S | **fixed strings this session; gate is the durable fix**
- **IMP-141** | Fleet-page generator — `spindleloom-agent-fleet.html` is hand-authored but hard-enforced by `validate_graph` checks 12/13; there is no generator, so following the add-agent docs produces a hard validator failure with no documented fix. Emit its node/edge dataset from the contract graph (derive like INDEX.md) + `--check`. | Contributor | M | **fixed: `hooks/build_fleet_page.py` derives nodes/edges/descs/skills from the contracts (p/s/f taxonomy + wiki overlay + labels stay as completeness-checked curated maps in the hook); `--check` wired into battery/pre-commit/CI; checks 12/12b/13 verify independently** |
- **IMP-142** | Persona-data drift guard — the hub's `const P[]` and the 15 standalone pages hand-restate each persona's agents/commands/gates with no tie to `agents/*.md` frontmatter; a command rename breaks all three copies silently ("11 personas" comment already drifted vs 15). Validate `P[]` agent/command tokens against the contracts. | Reader/Skeptic | M | **partially fixed this session (validator added)**
- **IMP-143** | Resolve the 15 orphaned standalone persona pages — zero inbound links repo-wide; duplicate `P[]`. | Reader | S | **fixed: now linked from the hub `<noscript>` (doubles as the JS-off fallback); already generated from `P[]` by the standalone-page generator, so not a drift source**

### Behavioral-eval honesty (claims vs evidence)

- **IMP-144** | Eval scope honesty — the "market→operate, one traceable chain, graded A behavioral E2E of the fleet" framing covers only the **10-agent spec+plan spine**; build→test→ship→operate (30+ agents) is structural-only. State the scope plainly in FLEET-EVAL.md + medremind README; ideally extend the eval one build→verify→review→release→operate pass. | Process | M | **scope caveat landed this session; eval extension STILL-OPEN**
- **IMP-145** | Commit `handoff-log.md` for runs 3 and 4 (the protocol's mandatory "judge's instrument," absent from exactly the two top-graded runs) or re-grade with it; preserve/annotate run 1. | Process | S | STILL-OPEN
- **IMP-146** | Volume-normalized eval metric (contradictions per 100 Req-IDs) so a CLEAN sweep on ~47% less output (run 4: 56 pts vs run 3: 106) isn't rewarded as pure capability gain. | Process | S | STILL-OPEN

### Journey friction (fixed or tracked)

- **IMP-147** | `sloom signoff <gate>` command + `signoff-token-template.md` — the six release gates `validate_gates` reads have no writer; the QA→Release go/no-go can't be produced from the docs. | Test/Release | S | **fixed this session**
- **IMP-148** | A worked example past Planning — one real PBI with `runs/`, `approvals/`, a verification report, `signoffs/`, and a `sloom flags` round-trip; half the lifecycle + the whole concurrency layer have no copyable reference. | Cross-phase | M | STILL-OPEN
- **IMP-149** | `sloom run advance` enforces the row's DoD/verification gate, not just upstream+acceptance; generate the run-ledger skeleton from the contract graph so `upstream`/`requires_acceptance` can't drift. | Cross-phase | M | STILL-OPEN
- **IMP-150** | a11y on the reading surfaces — the clickable Woven Loop is mouse-only + `role="img"` (WCAG 2.1.1); `--ink-dim` fails AA contrast (~2.9:1 light); no `<noscript>` fallback on the JS-driven hub/fleet-map. | Harness | S | **fixed this session**
- **IMP-151** | Local==CI — `validate_targets.py` (+ MCP smoke) run only in CI though CLAUDE.md claims parity; add `validate_targets` to pre-commit. | Contributor | S | **fixed this session**

Superseded/absorbed: IMP-113 (command holes) is broadened by the operator audit — Review phase + `sre` + API/data/UX design have no slash command at all; keep tracking under IMP-113.
