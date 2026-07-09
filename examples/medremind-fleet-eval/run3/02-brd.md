# BRD: MedRemind — Prescription Refill Reminder & Approval Module

*Author: `brd-writer` · phase: requirements · 2026-07-09 · run3*
*Upstream: `doc-strategy-advisor` (`01-doc-strategy.md`). Source of truth for scope: `brief.md`.*
*MRD intentionally dropped by doc-strategy (DS decision, `01-doc-strategy.md` §2 DROP) — business context is captured here. See §Open questions FLAG.*

| Field | Value |
|---|---|
| Sponsor | RxKart leadership (retail pharmacy operations) |
| Author | `brd-writer` (business analyst) |
| Status | Draft |
| Last updated | 2026-07-09 |

## Executive summary

RxKart, a 40-store pharmacy chain with an existing 250k-MAU patient mobile app and a
pharmacist back-office portal, is losing revenue and harming adherence because only 41% of
refillable prescriptions are refilled on time. MedRemind adds a refill-reminder and
pharmacist-approval module: patients are reminded (push + SMS) when a prescription is due and
can request a refill in one tap; pharmacists triage requests in a portal queue, approve or
reject, and may offer a generic substitution the patient must accept before dispensing.
Controlled substances (Schedule II–V) are excluded from automation and routed through
identity verification and pharmacist-initiated contact. The business goal is to raise the
on-time refill rate from 41% to 60% within two quarters, without incurring a HIPAA or
controlled-substance compliance breach.

## Background and problem statement

RxKart already owns the patient relationship (250k monthly active patients) and the dispensing
workflow, but refills depend on the patient remembering to act. Today 59% of refillable
prescriptions are not refilled on time, which costs RxKart recurring dispensing revenue and
undermines medication adherence (a patient-safety and reputational concern). There is no
proactive reminder, no self-service refill request, and no structured pharmacist queue —
refill intent arrives ad hoc by phone or walk-in, so pharmacists cannot triage it efficiently.
The business needs to convert existing app reach into a repeatable, compliant refill loop.

## Business goals and objectives

Goals are stated as measurable business outcomes; see §Success metrics for baselines/targets.

- **BG-001** — Raise the on-time prescription refill rate from a 41% baseline to a 60% target
  within two quarters of general availability.
- **BG-002** — Convert reminded refill intent into completed refills through a one-tap request
  path, measured as an increase in patient-initiated refill requests per active patient.
- **BG-003** — Give pharmacists a triage queue that lets them clear refill requests within the
  store-hours service window without adding manual phone handling load.
- **BG-004** — Ship a first demonstrable slice within three two-week sprints (vertical:
  reminder → one-tap refill → pharmacist queue) to satisfy leadership's time-to-value pressure.
- **BG-005** — Operate the module with zero HIPAA PHI-exposure incidents and zero
  controlled-substance auto-refill policy violations across the first two quarters.

## Success metrics / KPIs

- **KPI-1 (primary)** — On-time refill rate: baseline **41%**, target **60%**, measured 2
  quarters post-GA. (Traces to BG-001.)
- **KPI-2** — Patient-initiated refill requests per active patient per month: baseline
  **0** (feature does not exist today), target set at GA by product-analytics
  (ASSUMPTION-5). (Traces to BG-002.)
- **KPI-3** — Reminder-to-refill conversion rate (refills completed within 7 days of a
  reminder ÷ reminders sent), target set at GA (ASSUMPTION-5). (Traces to BG-002.)
- **KPI-4** — Pharmacist queue clearance: median time from refill request to
  approve/reject decision within store hours; target set with the QA/ops owner
  (ASSUMPTION-5). (Traces to BG-003.)
- **KPI-5 (compliance guardrail)** — Number of HIPAA PHI-exposure incidents and number of
  Schedule II–V auto-reminder/one-tap-refill policy violations: target **0**. (Traces to
  BG-005.)
- **KPI-6 (delivery)** — First shippable slice demonstrated by end of sprint 3. (Traces to
  BG-004.)

## Scope

**In scope:**
- Refill reminders to patients via push (existing Firebase) and SMS (Twilio) when a
  prescription is due.
- One-tap refill request from the patient app for eligible (non-controlled) prescriptions.
- Pharmacist refill-request queue in the existing portal with approve/reject decisions.
- Pharmacist-suggested generic substitution with mandatory patient acceptance before dispensing.
- Controlled-substance (Schedule II–V) exclusion from automation, with an identity-verification
  step and pharmacist-initiated contact path.
- HIPAA PHI minimization in notifications (no drug names in SMS).

**Out of scope (and why):**
- **Payment / copay collection** — dispensing billing is handled by existing pharmacy systems;
  not part of the reminder/approval loop.
- **Delivery / courier logistics** — MedRemind covers refill request→approval, not fulfilment
  transport.
- **New patient or pharmacist authentication system** — builds on the existing IdP
  (ASSUMPTION-4); no new identity platform.
- **New prescription creation / e-prescribing** — the module reminds and refills *existing*
  prescriptions; it does not originate them.
- **Market discovery / MRD** — RxKart has an established 250k-MAU product and known market;
  doc-strategy dropped the MRD (`01-doc-strategy.md` §2).
- **FDA 21 CFR Part 11 / GxP computerized-system validation** — treated as not applicable
  (ASSUMPTION-3); this is a pharmacy service, not a medical device. If Part 11 applies, scope
  and the URS must be re-opened.
- **Non-US jurisdictions** — assumed US-only pending living-spec ratification (ASSUMPTION-1).

## Stakeholders

| Name / role | Role | Interest / responsibility |
|---|---|---|
| RxKart leadership | Sponsor | Funds the module; owns the 41%→60% business target and time-to-value pressure. |
| PM (acting PO) | Product owner | Prioritizes backlog; owns BRD/PRD; single throat-to-choke for scope. |
| Pharmacists (40 stores) | Primary operators | Triage the refill queue, approve/reject, suggest substitutions; workflow must not add load. |
| Patients (250k MAU) | End users / beneficiaries | Receive reminders, request refills; adherence and privacy at stake. |
| Architect | Technical authority | Owns SRS/SDD/RTM custody; ensures NFRs and integrations are met. |
| QA lead (validation) | Quality / compliance | Owns URS and test plan; ensures controlled-substance and HIPAA rules are verified. |
| Borrowed security engineer | Compliance gate | Mandatory threat model + security review (PHI + controlled substances). ASSUMPTION-2. |
| Compliance / HIPAA officer | Regulatory approver | Signs off PHI-minimization approach and controlled-substance handling. ASSUMPTION-6. |
| RxKart store operations | Affected org | Absorbs any change to pharmacist counter workflow. |

## Assumptions and constraints

**Constraints (ratified from brief.md):**
- **CON-1** — SMS is delivered through Twilio; push through the existing Firebase setup.
- **CON-2** — HIPAA applies; PHI in notifications must be minimized — **no drug names in SMS**.
- **CON-3** — Controlled substances (Schedule II–V) must not be auto-reminded or one-tap
  refilled; they require an extra identity-verification step and pharmacist-initiated contact.
- **CON-4** — Reminder must be delivered within 5 minutes of its scheduled time;
  queue page must load in under 2s at 500 concurrent pharmacists; 99.9% availability during
  store hours. (These are NFRs owned downstream by `srs-writer`; carried here as business
  constraints for traceability.)
- **CON-5** — Team is fixed at 7 (1 PM/PO, 1 architect, 4 devs, 1 QA); two-week sprints;
  Azure DevOps; first shippable slice expected in 3 sprints.

**Assumptions (unratified — carry, do not treat as decided):**
- **ASSUMPTION-1** *(owner: `spec-steward`)* — Living-spec was not routed; regulatory
  jurisdiction and US-only scope are inferred from `brief.md`. Carried from
  `01-doc-strategy.md`.
- **ASSUMPTION-2** *(owner: PM)* — No designer / security / SRE / BA headcount; mandatory
  security review and a11y gates assume these are borrowed or contracted. Carried from
  `01-doc-strategy.md`.
- **ASSUMPTION-3** *(owner: architect)* — "Regulated" = HIPAA + DEA controlled-substance
  handling, **not** FDA 21 CFR Part 11 / GxP. Carried from `01-doc-strategy.md`.
- **ASSUMPTION-4** *(owner: PM)* — Patient/pharmacist authentication is provided by the
  existing IdP; the Schedule II–V identity-verification step builds on it. Carried from
  `01-doc-strategy.md`.
- **ASSUMPTION-5** *(owner: PM / `product-analytics`)* — Numeric targets for KPI-2, KPI-3,
  KPI-4 are set at GA once baselines are instrumented; only KPI-1 (41%→60%) is ratified by
  the brief today. *(new — brd-writer)*
- **ASSUMPTION-6** *(owner: PM)* — A HIPAA/compliance approver exists to sign off the
  PHI-minimization mechanism; the brief names none explicitly. *(new — brd-writer)*
- **ASSUMPTION-7** *(owner: PM)* — "On-time refill rate" is measured against the
  prescription's due date across RxKart's refillable (non-controlled) prescription base; the
  brief does not define the denominator. `product-analytics` must ratify the definition
  before it becomes the acceptance metric for BG-001. *(new — brd-writer)*

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| PHI leaked in an SMS (e.g., drug name in message body) | Medium | Critical (HIPAA breach) | PHI-minimization rule (CON-2) enforced in notification design; security review gate; ADR on SMS content. |
| Controlled substance auto-reminded or one-tap refilled | Low | Critical (DEA violation) | Hard exclusion rule (CON-3); Definition of Ready requires a compliance note for any Schedule II–V-touching item. |
| Twilio SMS deliverability shortfall breaks the ≤5-min SLO | Medium | High (misses BG-001) | Delivery SLO owned by SRE; push+SMS dual-channel; monitor delivery latency. |
| Missing craft headcount (security, design, SRE) blocks mandatory gates | High | High (schedule slip) | Borrow/contract per ASSUMPTION-2; tracked as a RAID risk by `raid-keeper`. |
| Patients ignore reminders → conversion below target | Medium | High (misses 60% goal) | Channel A/B testing (product-analytics, post-launch); reminder timing tuning. |
| 3-sprint pressure forces cutting a compliance gate | Medium | Critical | Vertical slicing keeps each sprint shippable without dropping gates; gates are non-negotiable per doc-strategy. |
| Jurisdiction/Part 11 assumption wrong → URS re-scope mid-build | Low | High (rework) | Resolve ASSUMPTION-1/-3 via living-spec before SRS/URS finalize (see FLAG). |

## Current business process (as-is)

Refills are patient-initiated with no prompt: a patient must remember a prescription is due,
then phone the store or walk in. Pharmacists field these requests ad hoc alongside counter
work, with no queue or prioritization. Controlled substances follow existing manual
counter/DEA procedures. Result: 41% on-time refill rate, uneven pharmacist load, and lost
recurring dispensing revenue. Pain points: no proactive prompt, no self-service, no triage,
no visibility into pending refill demand.

## Proposed business process (to-be)

When a prescription is due, the patient receives a reminder (push + SMS, PHI-minimized). For
eligible prescriptions the patient requests a refill in one tap; the request enters the
pharmacist portal queue. The pharmacist reviews the queue, approves or rejects, and may
suggest a generic substitution that the patient must accept before dispensing proceeds.
Controlled substances (Schedule II–V) are never auto-reminded or one-tap refilled — they are
routed to identity verification and pharmacist-initiated contact. Benefits over as-is:
proactive demand capture, self-service reducing phone load, a triaged queue, and an auditable
compliant path for controlled substances.

## High-level requirements

Business-language statements (the *why/what*, not product screens or architecture):

- **BR-001** — The business requires that patients be proactively reminded when a refillable
  prescription is due, through push and SMS channels, so that refill intent is captured before
  the patient lapses. *(traces BG-001, BG-002; CON-1)*
- **BR-002** — The business requires that a patient be able to request a refill of an eligible
  prescription in a single action, so that reminded intent converts to a completed refill.
  *(traces BG-002)*
- **BR-003** — The business requires that pharmacists triage incoming refill requests from a
  single prioritized work queue and record an approve or reject decision for each, so that
  demand is cleared within store hours without added phone handling. *(traces BG-003)*
- **BR-004** — The business requires that when a pharmacist suggests a generic substitution,
  dispensing does not proceed until the patient has explicitly accepted the substitution, so
  that patient consent is preserved. *(traces BG-005)*
- **BR-005** — The business requires that controlled substances (Schedule II–V) be excluded
  from automated reminders and one-tap refill, and instead be routed through an
  identity-verification step and pharmacist-initiated contact, so that RxKart stays compliant
  with controlled-substance regulations. *(traces BG-005; CON-3)*
- **BR-006** — The business requires that protected health information in notifications be
  minimized such that no drug name appears in an SMS, so that RxKart avoids a HIPAA breach.
  *(traces BG-005; CON-2)*
- **BR-007** — The business requires that the module be delivered as an incremental,
  demonstrable slice within three two-week sprints, so that leadership realizes value on the
  stated timeline. *(traces BG-004; CON-5)*

## Impact analysis

- **Existing patient mobile app (250k MAU):** gains reminder + one-tap refill surfaces;
  frontend + notification integration (Firebase push).
- **Existing pharmacist portal:** gains a refill-request queue and decision workflow; must meet
  the <2s @ 500-concurrent NFR (CON-4).
- **Notification pipeline:** new Twilio (SMS) + Firebase (push) integration with PHI
  minimization; owned in SDD/TSD.
- **Identity / IdP:** extended for Schedule II–V identity verification (ASSUMPTION-4).
- **Pharmacist store workflow (40 stores):** counter process changes to consume the queue;
  operations must be trained.
- **Compliance:** HIPAA PHI-minimization and DEA controlled-substance handling are mandatory
  gates (security review + URS), not optional.
- **Team / staffing:** material gap — no dedicated designer, security, SRE, or BA; mandatory
  gates depend on borrowed/contracted craft (ASSUMPTION-2), a live schedule risk.

## Requirements traceability matrix (RTM)

Rows for these BR/BG IDs are seeded in the shared `RTM.md`; downstream writers append their
columns. See `examples/medremind-fleet-eval/run3/RTM.md`.

| Business goal | Business requirement | Maps to (next: PRD/URS) |
|---|---|---|
| BG-001 | BR-001 | prd-writer / urs-writer |
| BG-002 | BR-002 | prd-writer |
| BG-003 | BR-003 | prd-writer / urs-writer |
| BG-005 | BR-004 | prd-writer / urs-writer |
| BG-005 | BR-005 | urs-writer / srs-writer |
| BG-005 | BR-006 | srs-writer / sdd-writer |
| BG-004 | BR-007 | backlog-manager / sprint-planner |

## Open questions

| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| Exact regulatory jurisdiction (US states / DEA scope); is the module US-only? | `spec-steward` | Open — ASSUMPTION-1 | — |
| Does FDA 21 CFR Part 11 / GxP apply? (changes URS to a validated deliverable) | architect | Open — ASSUMPTION-3 | — |
| Numeric targets for KPI-2/3/4 (conversion, requests/patient, queue clearance) | PM / product-analytics | Open — ASSUMPTION-5 | — |
| Precise definition of the "on-time refill rate" denominator | PM / product-analytics | Open — ASSUMPTION-7 | — |
| Named HIPAA/compliance sign-off authority | PM | Open — ASSUMPTION-6 | — |

```
FLAG(mrd-writer): MRD is my declared contract input but is absent on disk. This is
EXPECTED, not a defect — doc-strategy (01-doc-strategy.md §2 DROP) deliberately dropped the
MRD because RxKart has an existing 250k-MAU product and known market, and routed business
context into this BRD. No action needed unless a market-discovery gap later emerges; flagged
only to make the intentional skip auditable in the chain.
```

```
FLAG(spec-steward): living-spec was not routed to the fleet (confirmed in 01-doc-strategy.md
§8). Jurisdiction, US-only scope, and Part 11/GxP applicability (ASSUMPTION-1, -3) remain
unratified and gate the URS/SRS. Please produce/route the living-spec before those documents
finalize.
```
