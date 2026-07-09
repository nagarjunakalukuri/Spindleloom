# Doc Strategy — MedRemind (RxKart refill reminder & approval module)

**Author:** doc-strategy-advisor · **Date:** 2026-07-09 · **Input:** brief.md only

## Team & context read
- 7 people, single squad: 1 PM (acting PO), 1 architect, 4 devs, 1 QA. Two-week sprints, Azure DevOps.
- Brownfield: existing patient mobile app + pharmacist portal. Timeline: shippable slice in 3 sprints.
- Regulated exposure: **HIPAA** (PHI minimization in notifications) and **DEA/state-board rules for Schedule II–V controlled substances** (no auto-remind, identity verification, pharmacist-initiated contact).

## Tier recommendation: **Tier 1 (Lean, 1–15 people) + regulated overlays**

A 7-person single squad cannot sustain the full MRD→TSD stack. Two living documents,
plus the compliance artifacts the regulated context makes non-negotiable.

## Recommended document set

| # | Document | Covers | Owner | Consumers | Agent |
|---|---|---|---|---|---|
| 1 | **1-pager PRD** (BRD+PRD merged) | Business goal (41%→60% on-time refills), personas (patient, pharmacist), feature list, success metrics, scope/out-of-scope | PM (acting PO) | Architect, devs, QA, RxKart stakeholders | `brd-writer`+`prd-writer` (kept short) |
| 2 | **RFC / Tech Design Doc** (SRS+SDD+TSD merged) | Reminder scheduler, refill-queue API, Twilio/Firebase integration, data model, NFRs (5-min delivery, <2s @ 500 concurrent, 99.9% store-hours), security section | Architect | Devs, QA, DevOps | `sdd-writer`+`tsd-writer` (lean, links to PRD) |
| 3 | **URS** (lean) | Intended use, operator tasks (pharmacist approve/reject/substitute), safety-critical flows (controlled-substance gating, substitution acceptance before dispensing), audit expectations | QA lead (validation hat) | PM, architect, auditors | `urs-writer` |
| 4 | **Threat model / SEC- requirements** (section of the RFC, not standalone) | STRIDE on PHI flows, notification content minimization, identity-verification step, authz on queue | Architect (no dedicated security engineer — flagged gap) | Devs, code review, CI | `security-reviewer` |
| 5 | **Test plan + RTM** | Verification traced to PRD/URS/SEC requirements — the compliance evidence chain | QA | Devs, PM, auditors | `test-plan-writer` |
| 6 | **ADR log** | One file per significant decision (scheduler design, Twilio failure handling, controlled-substance flow) | Architect | Whole team | `adr-writer` |
| 7 | **PBIs / functional behavior** | Exact flows, edge cases, acceptance criteria — **in Azure Boards work items, not a standalone FRD** | PM writes, QA reviews AC | Devs, QA | `frd-writer` for hard cases only |

## URS verdict: **Yes — warranted, but lean**
This is not a GAMP-validated manufacturing system, so a full ISPE-style URS would be
overkill. But the module gates **controlled-substance refills** and **generic substitution
before dispensing** — patient-safety-adjacent, auditable behavior under DEA/state-board and
HIPAA scrutiny. A short URS (intended use, operator tasks, safety attributes, PHI-handling
rules) gives auditors and the test plan a stable design input. Keep it to 2–3 pages.

## Explicitly dropped or merged (with reasons)
- **MRD — drop.** Client-commissioned feature; the market case is already made. No `mrd-writer` run needed.
- **Standalone BRD — merge** into the 1-pager PRD (business-goal section). One doc, one owner.
- **Standalone FRD — drop**; functional logic lives in Azure Boards PBIs with acceptance criteria. A static FRD would drift from the tracker within a sprint.
- **Standalone SRS — merge** into the RFC as its "Constraints & NFRs" section; the brief's NFRs are few and concrete.
- **Standalone TSD — merge** into the RFC; one squad doesn't need SDD and TSD as separate layers.
- **Tech radar / constitution / RFC process — skip.** Single squad, one architect; direction fits in ADRs.

## Harness note (experimental control)
This evaluation runs the **full funnel chain (MRD→BRD→PRD→FRD→SRS→SDD→TSD) regardless of
this recommendation**, as a control. A **binding** application of this strategy would:
- **Not run** `mrd-writer` at all.
- **Merge** `brd-writer` + `prd-writer` output into a single 1-pager PRD.
- **Emit** `frd-writer` content directly as Azure Boards PBIs, not a document.
- **Merge** `srs-writer` + `sdd-writer` + `tsd-writer` output into one lean RFC.
- **Keep** `urs-writer`, the threat model, the test plan + RTM, and ADRs as-is.
Downstream agents in this run should treat their standalone documents as sections of the
merged targets above, and keep them proportionally short.

## Storage model (one system of record per kind)
- Specs, RFC, URS, ADRs, RTM → **git repo** (docs-as-code), linked from the Azure DevOps Wiki home (`wiki-curator`).
- PBIs/backlog → **Azure Boards only** — never duplicated as per-PBI markdown.
- No PDFs. All documents living and linked.

## Process rules
- **Definition of Ready:** no PBI enters a sprint until the RFC section it depends on is peer-reviewed; controlled-substance and PHI stories additionally need a URS/threat-model reference.
- Delivery chain after specs: `backlog-manager` → `estimation-facilitator` → `sprint-planner` → build → `retrospective-facilitator`.
- Given production + uptime SLO (99.9%): add lightweight SLO/alerting notes via `sre` before launch; `product-analytics` to instrument the 41%→60% refill metric.

## Ownership summary
PM owns everything business-altitude (PRD, PBIs). Architect owns everything technical
(RFC, ADRs, threat model). QA owns verification and validation (URS, test plan, RTM).
One owner per document — no shared ownership.
