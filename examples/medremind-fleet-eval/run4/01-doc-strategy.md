# Doc Strategy — MedRemind (RxKart refill reminder & approval module)

**Author:** doc-strategy-advisor · **Date:** 2026-07-10 · **Phase:** discovery
**Input actually available:** `brief.md` only (see FLAG + ASSUMPTION-1 below)

> **Handoff** · *Before:* read living-spec (from `spec-steward`). *After:* produce doc-strategy → hand to `brd-writer`, `prd-writer`, `urs-writer`, `solution-recon`, `wiki-curator`. *(Flag discoveries back upstream — see `project_guides/BEST-PRACTICES.md`.)*

---

## FLAG & assumptions (read first)

- **FLAG(spec-steward):** my sole contract input `living-spec` was not found on disk (`build_context_pack` §1 confirmed "not found on disk"; no context store yet). I did not invent its content. I proceeded from `brief.md`, which the run provides as the raw discovery input.
- **ASSUMPTION-1** *(owner: spec-steward)* — In the absence of a ratified living-spec, `brief.md` is treated as the authoritative discovery input for this strategy. If a living-spec later lands, re-check the tier call and the regulated overlays against it.
- **ASSUMPTION-2** *(owner: PM / acting PO)* — RxKart's tooling is Azure DevOps for both work items (Azure Boards) and the wiki (Azure DevOps Wiki); the repo is the docs-as-code home. Stated team is 7 (1 PM, 1 architect, 4 devs, 1 QA); no dedicated security engineer, no dedicated UX designer, no SRE named. If any of these roles exist, reassign the owners in the matrix below.

---

## 1 · Team & context read

- **Size / shape:** 7 people, **single squad** — 1 PM (acting PO), 1 architect, 4 developers, 1 QA. Two-week sprints, Azure DevOps.
- **Product shape:** **brownfield** — an existing patient mobile app (250k MAU) + an existing pharmacist back-office web portal. The feature is a *module bolted onto* both, not a greenfield app. Integration surface (Twilio SMS, Firebase push) is fixed by the brief.
- **Delivery pressure:** first shippable slice in **3 sprints** (~6 weeks). This is the single biggest constraint on the doc budget: every document must earn its keep against a 6-week clock.
- **Regulated exposure (drives the overlays):**
  - **HIPAA** — PHI must be minimized in notifications (no drug names in SMS). This is a *content-of-notification* rule that every reminder/queue story inherits.
  - **DEA / state-board controlled-substance rules** — Schedule II–V drugs cannot be auto-reminded or one-tap refilled; they require identity verification + pharmacist-initiated contact. This is *safety-critical, auditable behavior*.
- **Biggest documentation risk here** is not "too little" — it is **drift under time pressure**: a 7-person team writing a full MRD→TSD stack in 6 weeks will let it go stale by sprint 2 and auditors will find gaps. The strategy therefore optimizes for the *smallest auditable set*.

## 2 · Tier recommendation: **Tier 1 (Lean, 1–15 people) + regulated overlays**

A 7-person single squad cannot sustain the full MRD→BRD→PRD→FRD→SRS→SDD→TSD stack and ship in 3 sprints. Collapse to **two living core documents**, then add *only* the compliance/quality artifacts the regulated context makes non-negotiable. Skip everything a single squad doesn't need (tech radar, constitution, RFC process, standalone MRD/FRD/SRS/TSD).

**Why not Tier 0 (AI-native pod):** the brief describes a conventional human team (named PM/architect/devs/QA), not an AI-orchestrated pod. Do not impose the `ai-orchestrator` guardrail stack. *(If RxKart later runs AI coding agents as first-pass executors, revisit — the guardrail artifacts, RTM, and DoR/DoD grow in importance.)*

## 3 · Recommended document set (the Document Register)

Each row is assigned a stable **DOC-* register id** so the wiki, the RTM, and downstream agents can reference "which document" unambiguously. These are *document identifiers*, not requirement Req-IDs — doc-strategy-advisor owns no RTM requirement column (`rtm_column: "—"`); requirement IDs are minted downstream by `brd/prd/urs/srs/sdd` writers.

| Reg id | Document | Covers | Owner (single) | Primary consumers | Runs which agent | Keep / merge / drop |
|---|---|---|---|---|---|---|
| DOC-001 | **1-pager PRD** (BRD + PRD merged) | Business goal (on-time refill 41%→60% in 2 quarters), personas (patient, pharmacist), feature list, success metrics, explicit scope / out-of-scope | PM (acting PO) | Architect, devs, QA, RxKart stakeholders | `brd-writer` + `prd-writer`, kept to one page | **Merge** BRD into PRD |
| DOC-002 | **Lean RFC / Tech Design Doc** (SRS + SDD + TSD merged) | Reminder scheduler, refill-request/approval queue API, Twilio + Firebase integration, data model, and the "Constraints & NFRs" section (5-min delivery, queue < 2s @ 500 concurrent pharmacists, 99.9% availability during store hours) | Architect | Devs, QA, DevOps | `srs-writer` + `sdd-writer` + `tsd-writer`, merged & lean, linked to DOC-001 | **Merge** three layers into one RFC |
| DOC-003 | **URS** (lean, regulated overlay) | Intended use, operator tasks (pharmacist approve / reject / suggest-substitution), safety-critical flows (controlled-substance gating, substitution-acceptance-before-dispensing), PHI-handling & audit expectations | QA lead (validation hat) | PM, architect, auditors | `urs-writer` | **Keep** (regulated) |
| DOC-004 | **Threat model + security requirements** — a *section of DOC-002*, not standalone | STRIDE over PHI flows, SMS/push content minimization, the identity-verification step for controlled substances, authz on the pharmacist queue | Architect *(no dedicated security engineer — FLAG below)* | Devs, code review, CI | `security-reviewer` | **Merge** into RFC as a section |
| DOC-005 | **Test plan + RTM** | Verification traced to PRD / URS / security requirements — the **compliance evidence chain** auditors will ask for | QA | Devs, PM, auditors | `test-plan-writer` (RTM lives at `RTM.md`, seeded here) | **Keep** (regulated + quality backbone) |
| DOC-006 | **ADR log** (append-only, one file per decision) | Scheduler design, Twilio/SMS failure & retry handling, controlled-substance gating flow, substitution-acceptance model | Architect | Whole team | `adr-writer` | **Keep** (lightweight, pays off at any size) |
| DOC-007 | **Functional behavior → Azure Boards PBIs** (not a standalone FRD) | Exact flows, edge cases, acceptance criteria — authored as Azure Boards work items | PM writes, QA reviews AC | Devs, QA | `frd-writer` for the *hard* cases only; `backlog-manager` to structure the board | **Drop** standalone FRD; embed in tracker |
| DOC-008 | **Project wiki (home/index)** | Navigation + links to each system of record above; DoR/DoD; the "where things live" map | Architect or PM (whoever owns Azure DevOps Wiki) | Whole team + stakeholders | `wiki-curator` | **Keep** (thin index, not a content store) |

## 4 · URS verdict: **Yes — warranted, but lean**

This is **not** a GAMP-validated manufacturing/LIMS system, so a full ISPE-style URS would be over-engineering for a 7-person team. **But** the module *gates controlled-substance refills* and *generic substitution before dispensing* — patient-safety-adjacent, auditable behavior under DEA / state-board and HIPAA scrutiny. A short URS (intended use, operator tasks, safety attributes, PHI-handling rules) gives auditors and the test plan a **stable design input** that PBIs alone can't provide (PBIs churn; a URS is a fixed reference for validation). **Keep it to 2–3 pages.** Route to `urs-writer`.

## 5 · Explicitly dropped or merged (with reasons)

- **MRD — drop.** Client-commissioned feature with a stated business target; the market case is already made. No `mrd-writer` run needed.
- **Standalone BRD — merge** into DOC-001 (its business-goal + success-metric section). One doc, one owner (PM).
- **Standalone FRD — drop as a document**; functional logic lives in Azure Boards PBIs with acceptance criteria (DOC-007). A static FRD drifts from the tracker within a sprint. Use `frd-writer` only to work through the *hard* flows (controlled-substance gating, substitution acceptance) before they become PBIs.
- **Standalone SRS — merge** into DOC-002 as its "Constraints & NFRs" section; the brief's NFRs are few and concrete (three numbers).
- **Standalone TSD — merge** into DOC-002; one squad does not need SDD and TSD as separate layers.
- **Tech radar / constitution / formal RFC process — skip.** Single squad, one architect; technical direction fits in the ADR log (DOC-006). *(Revisit at Tier 2 if RxKart adds a second squad making overlapping tech choices.)*
- **Dedicated security document / UX design system / SRE runbook set — do not spin up as standalone docs now.** Fold security into DOC-004; there is no named designer and the UI extends existing surfaces; SLO/alerting notes are a thin addition (see §8).

## 6 · Harness note (experimental control)

This fleet-eval **runs the full funnel chain (MRD→BRD→PRD→FRD→SRS→SDD→TSD) regardless of this recommendation**, as an experimental control. A **binding** application of this strategy would instead:

- **Not run** `mrd-writer` at all.
- **Merge** `brd-writer` + `prd-writer` output into a single 1-pager PRD (DOC-001).
- **Emit** `frd-writer` content directly as Azure Boards PBIs (DOC-007), not a document.
- **Merge** `srs-writer` + `sdd-writer` + `tsd-writer` output into one lean RFC (DOC-002).
- **Keep** `urs-writer` (DOC-003), the threat-model section (DOC-004), the test plan + RTM (DOC-005), and the ADR log (DOC-006) as-is.

Downstream agents in this run should therefore treat their standalone documents as **sections of the merged targets above** and keep them proportionally short.

## 7 · Storage model (one system of record per kind of thing)

- **Specs, RFC, URS, ADRs, RTM → the git repo** (docs-as-code), linked from the Azure DevOps Wiki home (`wiki-curator`, DOC-008).
- **PBIs / backlog → Azure Boards only** — never duplicated as per-PBI markdown files (they drift from the board within a sprint).
- **No PDFs.** Every document is living, searchable, and linked from the wiki index.

## 8 · Process rules & delivery chain

- **Definition of Ready (DoR):** no PBI enters a sprint until the DOC-002 (RFC) section it depends on is peer-reviewed; **controlled-substance and PHI stories additionally require a DOC-003 (URS) and DOC-004 (threat-model) reference.**
- **Definition of Done (DoD):** each shipped story is traced in the RTM (DOC-005) to at least one product requirement and one test case — the auditable evidence chain.
- **Delivery chain after specs:** `backlog-manager` → `estimation-facilitator` → `sprint-planner` → build → `retrospective-facilitator`, repeating each sprint.
- **Given production + a 99.9% store-hours SLO:** add **lightweight SLO / alerting notes via `sre`** before launch (not a full runbook set), and **`product-analytics`** to instrument the 41%→60% on-time-refill success metric so the business target is measurable.

## 9 · Ownership summary

- **PM (acting PO)** owns everything business-altitude — DOC-001 (1-pager PRD) and DOC-007 (PBIs).
- **Architect** owns everything technical — DOC-002 (RFC), DOC-004 (threat-model section), DOC-006 (ADR log), and (by ASSUMPTION-2) DOC-008 (wiki).
- **QA (validation hat)** owns verification & validation — DOC-003 (URS) and DOC-005 (test plan + RTM).
- **One owner per document — no shared ownership.**

## 10 · Gaps flagged upstream / to the team

- **FLAG(spec-steward):** no living-spec on disk — this strategy rests on `brief.md` (ASSUMPTION-1).
- **FLAG(security-reviewer / staffing):** no dedicated **security engineer** on a HIPAA + controlled-substance module. The architect owns DOC-004 by default, but recommend a `security-reviewer` pass on PHI flows and the identity-verification step before launch — this is human judgement above CI scanners.
- **FLAG(staffing):** no dedicated **SRE** for a 99.9% SLO and no **UX designer** for patient-facing notification flows. Both are absorbed as light additions here; if the slice grows, staff them.
