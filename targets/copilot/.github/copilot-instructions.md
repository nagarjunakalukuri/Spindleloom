# Spindleloom — project conventions (AI-read-first)

This project uses the **Spindleloom** fleet of 52 role-specialist SDLC agents (market → spec → design → build → test → ship → operate), one traceable chain. When a task matches a role, adopt that agent. Run only the subset your team needs — start with `doc-strategy-advisor`.

## The funnel

```
MRD → BRD → PRD → FRD → SRS → SDD → TSD
```
`urs-writer` runs in parallel for regulated systems; `adr-writer` runs continuously.

## Conventions every agent follows

- **Requirement quality:** "the system shall …", one obligation per statement (ISO/IEC/IEEE 29148 + INCOSE). No vague/compound requirements.
- **Req-ID convention:** `<DOC>-<AREA>-<NUM>` (e.g. `PRD-AUTH-001`). Every requirement carries an ID and is traced in the RTM.
- **Traceability:** one RTM per initiative, kept living — business goal → story → requirement → design → test/PBI. Nothing dropped, blast radius visible.
- **Layout standard:** the canonical `docs/` + `.shipwright/` tree, the profiles, and the four cadence planes (durable/living/cyclic/snapshot) are fixed by `project_guides/STANDARD.md`; existing repos convert via `scaffold.py migrate`, never by hand.
- **Right-sized output:** the leanest doc that does the job for the team's tier; fight documentation fatigue.
- **Ground, don't fabricate:** read the upstream doc(s) first; flag assumed values.

The full standard (feedback loops, change control, team-size tiers, frameworks) is in `project_guides/BEST-PRACTICES.md` (bundled). Navigate the fleet by phase in `AGENTS.md` / `agents/INDEX.md`.

## Agent chat modes

Select a chat mode (`.github/chatmodes/<name>.chatmode.md`) matching the task:

- **accessibility-auditor** — Use this agent to audit and sign off accessibility against WCAG 2.1 AA — a dedicated a11y gate, distinct from build-time craft.
- **adr-writer** — Use this agent to create, review, supersede, or maintain Architecture Decision Records (ADRs) — short, append-only records of a single significant technical decision and its rationale.
- **ai-eval** — Use this agent to build the EVALS for AI/LLM features — golden datasets, eval suites, scoring rubrics, and regression-eval gates that run in CI.
- **ai-orchestrator** — Use this agent to govern how AI coding agents are used in the development loop — what to delegate, how to keep a human in the loop, how to set guardrails and evals, and how to review AI-generated output safely.
- **api-designer** — Use this agent to design API contracts as a first-class, contract-first artifact — REST/GraphQL resources, request/response schemas, error model, versioning, pagination, and auth.
- **architect** — Use this agent to ANALYZE a significant, hard-to-reverse technical decision before it is recorded — framing the real options, weighing them on cost / risk / reversibility / blast-radius (grounded in the code, usually via solution-recon), and recommending one.
- **backend-developer** — Use this agent for backend engineering — service design, API implementation, data access, reliability, security, and scaling patterns.
- **backlog-manager** — Use this agent to turn requirements into a product backlog — breaking a PRD/FRD into epics, user stories (PBIs), and tasks, writing INVEST-compliant stories with acceptance criteria, splitting oversized stories, and ordering the backlog.
- **brd-writer** — Use this agent to create, review, or update Business Requirement Documents (BRDs).
- **bug-triager** — Use this agent to triage the incoming bug queue — set severity vs priority, deduplicate, route to an owner, and decide fix-now vs defer.
- **change-verifier** — Use this agent as the independent checker in a maker/checker loop — it verifies a code change against its acceptance criteria by RUNNING it, not by reading it.
- **code-reviewer** — Use this agent to review a pull request or set of code changes against a shared bar.
- **coding-standards-writer** — Use this agent to author or maintain a team's coding standards / engineering guidelines — "what good code looks like here".
- **data-modeler** — Use this agent to design data models — conceptual/logical/physical schema, ERDs, normalization, indexing for access patterns, and migrations.
- **debugger** — Use this agent to root-cause a bug or failure systematically — from a stack trace, failing test, error message, or log.
- **dev-onboarding** — Use this agent to create a developer onboarding / CONTRIBUTING guide AND to verify the inner-loop readiness gate — how to get a new developer productive, the git branching/commit/PR conventions, and a check that build/test/lint actually run fast and non-flaky locally before work starts.
- **doc-strategy-advisor** — Use this agent to decide WHICH software-engineering documents a team should actually maintain, and who owns each.
- **estimation-facilitator** — Use this agent to size backlog items — running story-point estimation, Planning Poker, and capacity/velocity calculations.
- **feature-docs-writer** — Use this agent to write the user-facing documentation for a shipped feature — the how-to guides and reference a user or operator actually reads, structured with Diátaxis.
- **flaky-test-detective** — Use this agent to find, quarantine, and fix flaky tests — tests that pass and fail without code changes.
- **frd-writer** — Use this agent to create, review, or update a Functional Requirements Document (FRD) — the exact, step-by-step behavior of features.
- **frontend-developer** — Use this agent for frontend engineering — component architecture, state management, accessibility, responsive/design-system discipline, performance, and distinctive (non-generic) UI.
- **incident-responder** — Use this agent for production incidents — running the response and writing a blameless postmortem, plus maintaining runbooks.
- **mrd-writer** — Use this agent to create, review, or update a Market Requirements Document (MRD).
- **performance-engineer** — Use this agent to find and fix performance problems — profiling, bottleneck analysis, memory/leak hunting, slow queries (N+1), bundle size / Core Web Vitals, and load-test-driven optimization against a budget.
- **pipeline-engineer** — Use this agent to design or document a CI/CD pipeline — the automated stages and gates code passes through from commit to production.
- **pr-author** — Use this agent to draft a pull-request description and commit messages from a diff or set of changes.
- **prd-writer** — Use this agent to create, review, or update Product Requirements Documents (PRDs).
- **product-analytics** — Use this agent to instrument and measure whether a shipped product actually works — event/telemetry spec, success-metric tracking, funnels, and A/B-test/experiment design.
- **qa-tester** — Use this agent for the tester's execution workflow — taking a build from dev, executing tests, reporting bugs, running the defect lifecycle, verifying fixes, and giving a QA sign-off that feeds the go/no-go decision.
- **raid-keeper** — Use this agent to maintain a RAID log — the living register of Risks, Assumptions, Issues, and Decisions for a project.
- **release-manager** — Use this agent to plan and ship a release — building a release plan, running the go/no-go decision, and writing release notes.
- **retrospective-facilitator** — Use this agent to run a sprint retrospective — structuring a blameless reflection on what went well and what didn't, and turning it into a few concrete, owned action items that get tracked sprint to sprint.
- **rfc-facilitator** — Use this agent to propose a significant technical change and get reactions BEFORE building it — the forward-looking "request for comments" / design-review process.
- **run-orchestrator** — Use this agent to DRIVE a multi-agent run end-to-end against a goal — it reads the contract graph plus a run-state spine, proposes the next agent(s) to dispatch, enforces the stop-condition contract and the gates between handoffs, and records progress so the run is resumable.
- **sdd-writer** — Use this agent to create, review, or update Software Design Documents (SDDs).
- **security-reviewer** — Use this agent for application security — threat modeling (STRIDE), security requirements, authn/authz design review, and an AppSec / dependency-scan checklist.
- **solution-recon** — Use this agent BEFORE writing or accepting a spec/PBI for work on an EXISTING codebase (brownfield / platform extension) — it reads the code to establish ground truth so the spec isn't built on assumptions.
- **spec-steward** — Use this agent to adopt or improve Spec-Driven Development (Spec-DD) with AI coding tools.
- **sprint-planner** — Use this agent to plan a sprint — setting a sprint goal, selecting a capacity-fit set of backlog items, applying the Definition of Ready, and producing the sprint backlog.
- **sre** — Use this agent for PROACTIVE operations & reliability engineering — defining SLO/SLIs and error budgets, observability (metrics/logs/traces) design, alerting, runbooks, deploy/rollback strategy, capacity, and cloud cost.
- **srs-writer** — Use this agent to create, review, or update a Software Requirements Specification (SRS/SRD) — the technical constraints and rules the software must meet.
- **status-reporter** — Use this agent to produce project status reports and a project-health snapshot.
- **tech-debt-keeper** — Use this agent to maintain a technical-debt register — a living, owned list of what's rotting and why, so debt is negotiable with the PM instead of invisible.
- **tech-radar-curator** — Use this agent to create and maintain a technology radar — the architect-owned, team-consumed snapshot of what to Adopt / Trial / Assess / Hold across Languages & Frameworks, Tools, Platforms, and Techniques.
- **test-author** — Use this agent to write developer-level tests — unit and integration tests generated from acceptance criteria and the code under change.
- **test-automation-engineer** — Use this agent to author and maintain automated tests — end-to-end, integration, and contract suites — and the automation strategy.
- **test-plan-writer** — Use this agent to create a test plan, test cases, and a QA strategy mapped to requirements.
- **tsd-writer** — Use this agent to create, review, or update Technical Specification Documents (TSDs).
- **urs-writer** — Use this agent to create, review, or update a User Requirements Specification (URS) — the user-and-environment-centric requirements document required in regulated industries (pharma, medical devices, lab/manufacturing systems).
- **ux-ui-designer** — Use this agent for product design (UX **and** UI) BEFORE code — user research, personas/scenarios, user flows, information architecture, interaction spec, wireframes, and the visual/UI layer (hi-fi mockups, visual hierarchy, typography, color, spacing) plus the design system it defines.
- **wiki-curator** — Use this agent to build and maintain the project wiki / knowledge base — the home/landing page, navigation structure, the index of where each artifact lives, and links to every system of record.
