# Wheelwright

*An AI agent fleet for the entire software development lifecycle — market → spec → design → build → test → ship → operate, one traceable chain.*

A *wheelwright* builds the wheel that keeps turning — and the SDLC is exactly that wheel (build → ship → operate → learn → repeat). The project comes in three `-wright`s: **Wheelwright** is the fleet that builds the wheel, **Shipwright** ships it to every harness (`hooks/build_harness_artifacts.py` → `targets/`), and **Loopwright** runs it inside the delivery feedback loop (`project_guides/LOOPWRIGHT.md`). Wheelwright is a tool-agnostic fleet of **52 role-specialist AI agents** (plus 50 templates, commands, and self-validating hooks) that carry a product from the market problem at 30,000 feet down to build-ready, shipped, monitored code. Each agent owns one role, reads the artifact above it, and **hands off to the next** along a single traceable chain — and pushes discoveries back upstream. Run only the subset your team needs (`doc-strategy-advisor`).

## The funnel

```
MRD (market)  → BRD (business) → PRD (product) → FRD (behavior)
  → SRS (constraints) → SDD (architecture) → TSD (build)
```

Two agents sit outside this linear flow: **urs-writer** runs in parallel for regulated/validated systems (a user-requirements alternative entry point), and **adr-writer** runs continuously, logging significant decisions as they're made.

You rarely need all of these. Run **doc-strategy-advisor** to pick the right set for your team size, then **spec-driven-dev** to keep whatever you keep from drifting.

## Document agents

| Agent | File | Answers | Purpose |
|---|---|---|---|
| mrd-writer | `agents/mrd-writer.md` | **What market problem** | Market need, personas, competitive landscape — justifies the business case. Run first. |
| brd-writer | `agents/brd-writer.md` | **Why** | Business goals, scope, stakeholders, risks — non-technical. |
| prd-writer | `agents/prd-writer.md` | **What** | Product behavior — user stories, requirements, acceptance criteria (Atlassian style). |
| frd-writer | `agents/frd-writer.md` | **How it behaves** | Exact feature logic, flows, and edge cases (often embedded in tickets). |
| srs-writer | `agents/srs-writer.md` | **What constraints** | Measurable technical rules/targets — scale, performance, security, accessibility, compliance (the target). |
| urs-writer | `agents/urs-writer.md` | **What the user needs (regulated)** | User Requirements Spec for validated/regulated systems (ISPE/GAMP, FDA 21 CFR 820.30) — intended use, operator tasks, safety. Use in regulated contexts. |
| sdd-writer | `agents/sdd-writer.md` | **How (design)** | Architectural blueprint — arc42 structure, C4 diagrams, HLD→LLD (the plan to hit the target). |
| tsd-writer | `agents/tsd-writer.md` | **How (build)** | Developer playbook — final stack, API specs, schemas, testing, deployment. |

## Delivery agents

Bridge the specs into running agile work.

| Agent | File | Purpose |
|---|---|---|
| backlog-manager | `agents/backlog-manager.md` | Turns the PRD/FRD/SRS into a product backlog — epics → user stories (PBIs) → tasks, INVEST-checked, with acceptance criteria, ordering, Definition of Ready, and the next pull-able item (`/pbi-next`). The single canonical backlog agent. |
| estimation-facilitator | `agents/estimation-facilitator.md` | Sizes backlog items via story points / Planning Poker (modified Fibonacci); computes velocity & capacity. |
| sprint-planner | `agents/sprint-planner.md` | Sets a sprint goal, selects a capacity-fit sprint backlog from Ready items, flags deferrals and risks. |
| retrospective-facilitator | `agents/retrospective-facilitator.md` | Runs a blameless retro grounded in sprint data; produces 1–3 owned, tracked action items. |

The delivery loop: **backlog-manager** → **estimation-facilitator** → **sprint-planner** → build → **retrospective-facilitator** → (refine backlog, repeat).

## Governance & quality agents

Run continuously alongside delivery.

| Agent | File | Purpose |
|---|---|---|
| raid-log | `agents/raid-log.md` | Living register of Risks, Assumptions, Issues, Decisions; one owner + action per item; decisions link to ADRs. |
| status-reporter | `agents/status-reporter.md` | Audience-tailored status reports with a RAG health rating, grounded in metrics and the RAID log. |
| product-analytics | `agents/product-analytics.md` | Instruments the PRD's success metrics: event/telemetry spec, funnels, A/B-test design. Closes the build→learn loop (product metrics, vs status-reporter's delivery metrics). |
| test-plan-writer | `agents/test-plan-writer.md` | Test plan, test cases, and QA strategy traced to FRD/SRS/PBI requirements; IQ/OQ/PQ for regulated systems. |

## Engineering (inner-loop) agents

The developer's daily cycle — write, review, ship, operate.

| Agent | File | Purpose |
|---|---|---|
| dev-onboarding | `agents/dev-onboarding.md` | CONTRIBUTING / onboarding guide + git branching, commit, and PR conventions. Day-one productivity for new devs. |
| coding-standards | `agents/coding-standards.md` | "What good code looks like here" — enforceable engineering guidelines; automate what tools can. |
| code-reviewer | `agents/code-reviewer.md` | Reviews PRs against the standard & DoD; severity-grouped, kind, actionable feedback + PR template. |
| security-reviewer | `agents/security-reviewer.md` | Threat modeling (STRIDE), security requirements, authz-design review, AppSec checklist. The human-judgement security owner above CI's scanners. |
| qa-tester | `agents/qa-tester.md` | Tester actor: dev→QA handoff, test execution, bug reporting, defect lifecycle, QA sign-off → go/no-go. |
| accessibility-auditor | `agents/accessibility-auditor.md` | Independent WCAG 2.1 AA audit + sign-off gate (keyboard/screen-reader/contrast). Verifies what ux-ui-designer intends and frontend-developer builds. |
| performance-engineer | `agents/performance-engineer.md` | Profiles and optimizes against a budget — bottlenecks, memory, slow queries (N+1), bundle/Core Web Vitals; behavior-preserving, verified under load. |
| ci-cd-pipeline | `agents/ci-cd-pipeline.md` | Automated build→deploy stages and gates; makes DoD/coding-standards enforced, not aspirational. |
| sre | `agents/sre.md` | **Proactive** reliability: SLO/SLIs + error budgets, observability design, alerting, runbooks, deploy/rollback strategy, capacity & cost. The run-and-operate owner. |
| incident-postmortem | `agents/incident-postmortem.md` | Production incident response + blameless postmortem + runbooks (reactive — improves the SRE runbooks after a failure). |
| release-manager | `agents/release-manager.md` | Release plan, evidence-based go/no-go gate, and release notes. |
| pr-author | `agents/pr-author.md` | Drafts PR descriptions & Conventional-Commit messages from a diff. |
| test-author | `agents/test-author.md` | Unit/integration tests from acceptance criteria + code (the dev's own tests). |
| change-verifier | `agents/change-verifier.md` | **Independent checker (maker/checker).** Verifies a change against its acceptance criteria by *running* it — build, changed tests, lint, smoke the path — and returns a PASS/FAIL verdict with an AC coverage matrix. Has no Write/Edit (verifies, never patches); red goes to `debugger`. The in-loop execution gate between the builder and the PR. |
| debugger | `agents/debugger.md` | Systematic root-cause from a stack trace / failing test / log → fix + regression test. |
| test-automation-engineer | `agents/test-automation-engineer.md` | Authors & maintains e2e/integration automation; balances the pyramid. |
| bug-triager | `agents/bug-triager.md` | Triages the bug queue: severity vs priority, dedupe, route, fix-now/defer. |
| flaky-test-detective | `agents/flaky-test-detective.md` | Finds, quarantines & fixes flaky tests; tracks flake rate so red means broken. |

## Stack-depth & AI-native agents

Frontend/backend craft and the 2026 agentic-SDLC layer.

| Agent | File | Purpose |
|---|---|---|
| ux-ui-designer | `agents/ux-ui-designer.md` | Pre-code product design (UX **+ UI**): research, flows, wireframes, IA, interaction spec, hi-fi visuals (hierarchy/type/color/spacing) and the design system. Produces the "design" `frontend-developer` implements. |
| frontend-developer | `agents/frontend-developer.md` | Component architecture, state, accessibility (WCAG), design system, performance, anti-"AI-slop" UI. |
| backend-developer | `agents/backend-developer.md` | Service design, reliability (idempotency/failure handling), security, observability, scaling. |
| api-designer | `agents/api-designer.md` | Contract-first API design (OpenAPI/GraphQL): resources, error model, versioning, pagination, auth. |
| data-modeler | `agents/data-modeler.md` | Conceptual→logical→physical data model, ERD, indexing for access patterns, reversible migrations. |
| ai-orchestration | `agents/ai-orchestration.md` | Governs AI coding agents: what to delegate, human-in-the-loop by risk, guardrails/evals, reviewing AI output. |
| ai-eval | `agents/ai-eval.md` | Builds the eval harness for shipped AI/LLM features: golden datasets, scorers (incl. LLM-as-judge), and regression-eval CI gates. The execution counterpart to ai-orchestration's policy. |

Inner loop: **dev-onboarding/coding-standards** (set the bar) → build → **code-reviewer** + **security-reviewer** → **ci-cd-pipeline** → **qa-tester** → **release-manager** (go/no-go) → operate (**sre** SLOs/runbooks) → **incident-postmortem** → (feeds backlog/retro). **ux-ui-designer** feeds the build from the design phase.

## Practice agents

| Agent | File | Purpose |
|---|---|---|
| doc-strategy-advisor | `agents/doc-strategy-advisor.md` | Recommends which documents a team should maintain by size (Lean/Mid/Enterprise) and assigns owners. Start here. |
| solution-recon | `agents/solution-recon.md` | **Brownfield ground-truth.** Reads the codebase before a spec/PBI is written or accepted — confirms what exists, extracts the real contract/data shapes/status values, names the pattern to mirror, enumerates real scenarios, classifies FE-only vs backend-first, and produces a codebase-grounded PBI→task breakdown. Feeds frd/pbi/sdd-writer *verified facts* and flags spec↔code mismatches upstream. The missing code-grounded layer (greenfield doesn't need it). |
| wiki-curator | `agents/wiki-curator.md` | Builds & maintains the project wiki — home/index, navigation, links to each system of record, discoverability. (advisor decides *which* docs; this *builds* the wiki). |
| feature-docs-writer | `agents/feature-docs-writer.md` | Writes end-user / feature documentation in the Diátaxis model (tutorial · how-to · reference · explanation) from shipped features. |
| architect | `agents/architect.md` | **Decision analysis.** Takes a single architecturally-significant, hard-to-reverse choice and turns it into an evidence-grounded recommendation — frames the real options, weighs them on cost/risk/reversibility/blast-radius (grounded in the code via `solution-recon`), and recommends one. Sits between design/recon and the ADR: it produces the decision *analysis*; `adr-writer` *records* it. Distinct from `rfc` (socialize for comment) and `sdd-writer` (describe the chosen design). |
| adr-writer | `agents/adr-writer.md` | Records Architecture Decision Records — one immutable, append-only file per significant decision, capturing the *why*. Complements the SDD/TSD. |
| rfc | `agents/rfc.md` | Runs the **RFC / design-review** process — the forward-looking proposal opened for comment *before* building. An accepted RFC produces an ADR. The home for the "RFC" the funnel references. |
| tech-radar | `agents/tech-radar.md` | Architect-owned **technology radar** (Adopt/Trial/Assess/Hold) aligning tech choices across frontend/backend/systems teams. Ring moves are driven by ADRs. |
| tech-debt-register | `agents/tech-debt-register.md` | Living, owned **tech-debt register** — impact × interest vs effort, negotiable with the PM, promotable to the backlog. Fed by postmortems, retros, and reviews. |
| spec-driven-dev | `agents/spec-driven-dev.md` | Assesses Spec Driven Development maturity and keeps a living spec so AI tools don't drift from intent. |
| run-orchestrator | `agents/run-orchestrator.md` | **The conductor.** Drives a multi-agent run end-to-end against a goal — reads the contract graph + a run-state spine, proposes the next runnable agent (required upstreams done + gate passed), enforces the stop contract, and dispatches with confirmation (`/run`). Makes the implicit funnel an explicit, resumable run; pairs with `change-verifier` (its build-phase gate) and `ai-orchestration` (its policy). |

Each document agent can **create**, **review**, or **update** its document, reads the upstream doc(s) before drafting, and flags discoveries back upstream (see feedback loops in `project_guides/BEST-PRACTICES.md`).

> Navigate the full fleet by lifecycle phase in [`agents/INDEX.md`](agents/INDEX.md) — auto-generated from each agent's machine-readable contract block (`phase:` / `inputs` / `outputs` / `rtm_column` / `upstream` / `downstream`) by `hooks/build_agent_index.py`. See `project_guides/AGENT-AUTHORING.md` for the contract schema.

## Usage

**Claude Code:** copy the agent file(s) into your repo's `.claude/agents/` (or `~/.claude/agents/` for global use). Then ask, e.g. "write a BRD for a healthy-meal delivery app" — the subagent triggers automatically, or invoke with `/agents`.

**Cowork / Claude.ai:** paste the agent's body (below the frontmatter) as project instructions, or just ask Claude to follow `agents/<agent>.md`.

## Templates

Blank, fill-in-the-blank versions of each document:

- `templates/mrd-template.md`
- `templates/brd-template.md`
- `templates/prd-template.md`
- `templates/frd-template.md`
- `templates/srs-template.md`
- `templates/urs-template.md`
- `templates/sdd-template.md`
- `templates/tsd-template.md`
- `templates/adr-template.md`
- `templates/rfc-template.md` — forward-looking design proposal opened for comment
- `templates/tech-radar-template.md` — Adopt/Trial/Assess/Hold technology radar (cross-team alignment)
- `templates/tech-debt-register-template.md` — owned, quantified technical-debt register
- `templates/backlog-template.md`
- `templates/epic-template.md` — epic definition (top of the work-item hierarchy)
- `templates/task-template.md` — task under a user story
- `templates/estimation-template.md`
- `templates/sprint-plan-template.md`
- `templates/retrospective-template.md`
- `templates/raid-log-template.md`
- `templates/status-report-template.md`
- `templates/engineering-metrics-template.md` — DORA four keys + cycle-time breakdown (delivery-loop health)
- `templates/test-plan-template.md`
- `templates/definition-of-ready-done-template.md` — the DoR/DoD gate criteria
- `templates/run-state-template.md` — the run-orchestrator's spine (stop contract · agent ledger · decision log)
- `templates/pr-template.md` — PR description + review checklist
- `templates/coding-standards-template.md`
- `templates/contributing-template.md` — onboarding + git conventions
- `templates/bug-report-template.md`
- `templates/ci-cd-pipeline-template.md`
- `templates/postmortem-template.md`
- `templates/release-template.md`
- `templates/root-cause-template.md`
- `templates/test-automation-plan-template.md`
- `templates/bug-triage-template.md`
- `templates/flaky-test-register-template.md`
- `templates/frontend-design-template.md`
- `templates/ux-ui-design-template.md` — pre-code UX: flows, wireframes, states, interaction spec
- `templates/reliability-template.md` — SLO/SLIs, observability, alerts, runbooks, rollback (SRE)
- `templates/threat-model-template.md` — STRIDE threat model + security requirements + AppSec checklist
- `templates/accessibility-audit-template.md` — WCAG 2.1 AA audit (POUR) + conformance sign-off
- `templates/performance-audit-template.md` — budgets, ranked bottlenecks, optimizations, load-test + Core Web Vitals
- `templates/analytics-spec-template.md` — event/telemetry tracking plan, metric definitions, A/B design
- `templates/ai-eval-plan-template.md` — golden dataset, scorers, thresholds, regression-eval CI gate
- `templates/backend-service-template.md`
- `templates/api-contract-template.md`
- `templates/data-model-template.md`
- `templates/ai-orchestration-policy-template.md`
- `templates/wiki-home-template.md` — project wiki home / IA-map page
- `templates/spec-driven-maturity-assessment.md` — Spec-Driven Development maturity scorecard
- `templates/constitution-template.md` — the durable, AI-read-first project guardrails (principles, boundaries, non-goals)

## Worked example

`examples/healthy-meal-app/` — a full run of the chain (MRD → TSD + an ADR) for one app, tied together by a shared RTM. Use it as a reference for how the documents interlock, and as the canonical exemplar when authoring or testing agents.

## Shared conventions

`project_guides/STANDARD.md` — **the authoritative, versioned layout standard**: the one project-agnostic `docs/` + `.shipwright/` tree, the profiles (lean/mid/enterprise), the four cadence planes (durable/living/cyclic/snapshot), naming + ID immutability, backlog system-of-record, and the sanctioned-exception config. Greenfield scaffolds it; existing repos **convert** via `scaffold.py migrate` (never by hand).

`project_guides/INFORMATION-ARCHITECTURE.md` — the **detailed reference** under `project_guides/STANDARD.md`: where artifacts live and how they're organized, found, and versioned — the canonical tree, the profiles, the metadata convention, baselines, and the four retrieval paths (RTM · catalog · MCP · wiki).

`project_guides/HARNESS-MATRIX.md` — the 7-surface × 4-tool convergence matrix (Claude Code · Cursor · Copilot · Windsurf): which customization surface each tool exposes and which Wheelwright source maps onto it. What `hooks/build_harness_artifacts.py` (Shipwright) targets.

`project_guides/BEST-PRACTICES.md` — the funnel, feedback loops, team-size doc tiers, ownership matrix, the requirement quality standard (ISO/IEC/IEEE 29148 + INCOSE checklist and the "system shall" rule), the traceability backbone with Req-ID convention, change control & baselines, and frameworks (arc42, C4, Diátaxis, Docs-as-Code) that all agents follow.

`project_guides/AGENT-AUTHORING.md` — the prompting conventions every agent follows (role, context, calm instructions, grounding, right-sized output) and a checklist for adding a new agent. Read this before creating or editing an agent.

`SPEC-KIT-CROSSWALK.md` — how this toolkit maps to [GitHub Spec Kit](https://github.com/github/spec-kit): a command-by-command crosswalk, the per-feature vs per-document structural choice, and three adoption paths (Spec Kit container + this toolkit's depth).

`project_guides/TEAM-ROLES-AND-AZURE-DEVOPS.md` — who drives which agents on a 9-person team (Director/PM/Architect/Leads/Devs), and how the artifacts map onto Azure DevOps Boards/Repos/Wiki/Test Plans as the system of record.

`how-to-use.html` — a standalone, role-by-role usage guide (open in a browser): for each role — Director, PM, Architect, Lead, UX/UI Designer, Developer, QA, Security, SRE, AI/Data — the agents they drive, a typical flow, and copy-paste **sample prompts**, plus an end-to-end FreshDesk walkthrough.

`for-everyone.html` — a plain-language, end-to-end overview (open in a browser or share the link): the SDLC as a turning wheel, the eight stages, how to use it by role, the slash commands, configuration with per-platform install steps, the hooks reference, where artifacts live (the four cadence planes), and the Azure DevOps mapping. The "explain it to anyone" companion to the role-by-role `how-to-use.html`.
