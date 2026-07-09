# BRD: MedRemind — RxKart Prescription Refill Reminder & Approval Module

| Field | Value |
|---|---|
| Sponsor | RxKart PM (acting Product Owner) — ASSUMPTION-1 |
| Author | brd-writer (business analyst) |
| Status | Draft |
| Last updated | 2026-07-10 |

> Produced by `brd-writer`. Contract input **MRD** was **not on disk** — but doc-strategy §5 explicitly **drops the MRD** ("client-commissioned feature with a stated business target; the market case is already made"). This BRD therefore builds directly on `brief.md` + `01-doc-strategy.md`. Per doc-strategy DOC-001, this BRD is destined to **merge into a 1-pager PRD** (BRD business-goal + success-metric section); it is kept proportionally lean but at real-spec traceable depth. Hands off to `prd-writer` and `urs-writer`.

---

## FLAG & assumptions (read first)

- **FLAG(mrd-writer):** my contract input `MRD` is absent from disk. This is **not** treated as a gap because `01-doc-strategy.md` §5 deliberately dropped the standalone MRD; I did not invent MRD content. I proceeded from `brief.md` (raw discovery input) and the ratified `01-doc-strategy.md`.
- **FLAG(PM / acting PO):** "store hours" — the window governing the 99.9% availability target (BR-NFR-003) — is undefined in the brief. The SLO is unverifiable until this window is stated. Logged as OQ-1; proceeding on ASSUMPTION-4.
- **FLAG(product-analytics):** the 41% on-time-refill baseline has no stated measurement definition (numerator/denominator, refill window). The success metric (BR-OUTCOME-001) cannot be evidenced without it. Logged as OQ-2.
- **ASSUMPTION-1** *(owner: PM / acting PO)* — RxKart's PM acts as sponsor/PO; there is no separate business sponsor named. Reassign if a VP-level sponsor exists.
- **ASSUMPTION-2** *(owner: PM / acting PO)* — "within 2 quarters" (brief) means two fiscal quarters measured from the launch of the first shippable slice, not from project kickoff.
- **ASSUMPTION-3** *(owner: PM / acting PO)* — "on-time refill" counts a refill dispensed on or before the prescription's due date; the reminder/refill funnel is the primary lever on this rate.
- **ASSUMPTION-4** *(owner: PM / architect)* — pending OQ-1, "store hours" is taken as the union of all 40 stores' posted operating hours in their local time zones. The 99.9% availability target applies only within that window.
- **ASSUMPTION-5** *(owner: architect)* — Twilio (SMS) and Firebase (push) are fixed integration channels per the brief; no channel choice is open at business altitude.

---

## Executive summary
RxKart, a 40-store pharmacy chain with 250k monthly-active patients, wants to raise its on-time prescription refill rate from 41% to 60% within two quarters. MedRemind adds a refill-reminder and pharmacist-approval module onto the existing patient mobile app and pharmacist back-office portal: patients are reminded when a prescription is due and can request a refill in one tap; pharmacists triage a refill-request queue and may suggest a generic substitution. Controlled substances are deliberately excluded from automation and gated behind identity verification and pharmacist-initiated contact, and notification content is minimized to satisfy HIPAA.

## Background and problem statement
Today RxKart patients have no proactive, in-app prompt when a prescription becomes due; refills depend on the patient remembering, calling, or walking in. The result is a 41% on-time refill rate — lost adherence for patients and lost dispensing revenue for the chain. The pharmacist portal has no structured intake for patient-initiated refill requests, so requests arrive through fragmented channels (phone, counter, voicemail) with no queue, no audit trail, and no controlled-substance safeguard beyond manual pharmacist vigilance.

## Business goals and objectives
- **BR-OUTCOME-001** — The business requires that MedRemind raise the on-time refill rate from a 41% baseline to a 60% target within two quarters of launch (ASSUMPTION-2, ASSUMPTION-3).
- Reduce reliance on ad-hoc phone/counter refill intake by routing patient-initiated refills into a single auditable pharmacist queue.
- Maintain full regulatory standing (DEA / state-board and HIPAA) so that automation adds zero new compliance exposure.

## Success metrics / KPIs
- On-time refill rate: baseline 41% → target 60% within 2 quarters (BR-OUTCOME-001).
- Reminder timeliness: 100% of reminders delivered within 5 minutes of scheduled time (BR-NFR-001).
- Queue responsiveness: queue page load within 2 seconds at 500 concurrent pharmacists (BR-NFR-002).
- Service availability: 99.9% during store hours (BR-NFR-003).
- Compliance: zero DEA / state-board controlled-substance violations (BR-CTRL-004); zero HIPAA PHI-minimization violations in notifications (BR-PHI-002).

## Scope
**In scope:**
- Refill reminders (push + SMS) and one-tap refill for non-controlled prescriptions.
- Pharmacist refill-request queue with approve / reject decisions.
- Pharmacist-suggested generic substitution requiring patient acceptance before dispensing.
- Controlled-substance (Schedule II–V) gating: exclusion from automation + identity verification + pharmacist-initiated contact.
- PHI minimization in all notification content.

**Out of scope (and why):**
- New payment or billing flows — refill payment/adjudication rides existing pharmacy processes; this module only requests and approves refills.
- Delivery / courier logistics — dispensing and pickup are handled by the existing store workflow.
- Net-new mobile app or portal builds — MedRemind is a module bolted onto existing surfaces (brownfield, per doc-strategy §1).
- Channel selection — Twilio (SMS) and Firebase (push) are fixed by the brief (ASSUMPTION-5).
- Clinical decision support / drug-interaction checking — beyond a business refill reminder; deferred.

## Stakeholders
| Name | Role | Interest / responsibility |
|---|---|---|
| RxKart PM (acting PO) | Sponsor / Product Owner | Business outcome (41%→60%), scope, priorities (ASSUMPTION-1) |
| Pharmacists (40 stores) | Primary operators | Refill-queue triage, substitution, controlled-substance handling |
| Patients (250k MAU) | End users | Timely reminders, one-tap refill, minimal PHI exposure |
| Architect | Technical owner | Feasibility of NFRs, integration, controlled-substance/PHI safeguards |
| QA (validation hat) | V&V owner | URS, test plan, compliance evidence chain |
| Compliance / regulatory (RxKart) | Approver | DEA / state-board and HIPAA sign-off |

## Assumptions and constraints
- Assumptions ASSUMPTION-1 … ASSUMPTION-5 above.
- **Constraint:** first shippable slice due in 3 two-week sprints (~6 weeks) — the dominant delivery constraint (doc-strategy §1).
- **Constraint:** brownfield — module must integrate with existing mobile app, pharmacist portal, Twilio, and Firebase without re-platforming.
- **Constraint:** HIPAA (PHI minimization) and DEA / state-board controlled-substance rules are non-negotiable and gate launch.

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Controlled-substance request slips through automation | Low | Severe (regulatory) | Explicit exclusion + identity verification + pharmacist-initiated contact (BR-CTRL-001, BR-CTRL-002, BR-CTRL-003, BR-CTRL-004 as atomic reqs); URS + threat-model reference required before those stories enter a sprint |
| PHI (drug name) leaks into SMS | Medium | Severe (HIPAA) | Notification content minimization (BR-PHI-001); zero-violation acceptance bar (BR-PHI-002) |
| 6-week timeline forces cutting compliance work | High | Severe | Compliance stories are DoR-gated (doc-strategy §8), not deferrable; slice scope around them |
| 41%→60% target not met within 2 quarters | Medium | High (business case) | Instrument the funnel via `product-analytics`; revisit business case if leading indicators lag (feedback loop) |
| Reminder timeliness degrades at scale | Medium | Medium | 5-minute SLA made an explicit, testable requirement (BR-NFR-001) handed to SRS/SDD |

## Current business process (as-is)
A prescription becomes due, but no proactive prompt reaches the patient. The patient may or may not remember; if they act, they phone the store, leave voicemail, or visit the counter. A pharmacist handles each request ad hoc with no shared queue and no structured audit trail. Controlled-substance requests are policed by manual pharmacist judgement only. On-time refill rate sits at 41%.

## Proposed business process (to-be)
The system detects a due non-controlled prescription and reminds the patient via push and SMS. The patient requests a refill in one tap. The request lands in a single pharmacist queue in the portal, where a pharmacist approves or rejects it and may suggest a generic substitution; a substitution dispenses only after the patient accepts. Controlled-substance prescriptions never enter this automated path — they are routed to identity verification and pharmacist-initiated contact. All notification content is stripped of drug names and other PHI. Benefit: a proactive, auditable, compliant refill funnel that lifts on-time refills toward 60%.

## High-level requirements
Business-language, non-technical. Product behavior (screens, flows, APIs) is the PRD's job.

**Refill reminders & one-tap refill**
- **BR-REFILL-001** — The business requires that patients be reminded through push notification and SMS when a non-controlled prescription becomes due for refill.
- **BR-REFILL-002** — The business requires that patients be able to request a refill of a non-controlled prescription in a single tap from the reminder.

**Pharmacist approval queue**
- **BR-QUEUE-001** — The business requires that pharmacists be able to view all pending refill requests in a single back-office queue.
- **BR-QUEUE-002** — The business requires that a pharmacist be able to record an approve-or-reject decision for each refill request. <!-- quality-ok: BR-QUEUE-002 one obligation: record a single decision whose outcome is approve or reject -->

**Generic substitution**
- **BR-SUB-001** — The business requires that a pharmacist be able to suggest a generic substitution on a refill request.
- **BR-SUB-002** — The business requires that a suggested generic substitution be dispensed only after the patient has accepted it.

**Controlled substances (Schedule II–V)**
- **BR-CTRL-001** — The business requires that Schedule II–V controlled substances be excluded from automatic reminders and from one-tap refill.
- **BR-CTRL-002** — The business requires that a controlled-substance refill complete an additional identity-verification step before it is processed.
- **BR-CTRL-003** — The business requires that a controlled-substance refill be initiated through pharmacist-initiated contact rather than patient self-service.
- **BR-CTRL-004** — The business requires that the module incur zero DEA / state-board controlled-substance compliance violations.

**PHI minimization (HIPAA)**
- **BR-PHI-001** — The business requires that refill notifications exclude protected health information, including drug names, from SMS content.
- **BR-PHI-002** — The business requires that the module incur zero HIPAA PHI-minimization violations in notification content.

**Business service levels (targets handed down to SRS/SDD for realization)**
- **BR-NFR-001** — The business requires that a refill reminder be delivered within 5 minutes of its scheduled time.
- **BR-NFR-002** — The business requires that the pharmacist queue page load within 2 seconds at 500 concurrent pharmacists.
- **BR-NFR-003** — The business requires that the module sustain 99.9% availability during store hours (ASSUMPTION-4).

## Impact analysis
- **Existing patient mobile app** — gains reminder surfacing + one-tap refill entry; depends on the Firebase push channel already in place.
- **Existing pharmacist portal** — gains a refill-request queue, decision controls, and substitution suggestion; new authenticated back-office surface.
- **Twilio (SMS)** — new outbound reminder traffic; content must be PHI-minimized (BR-PHI-001).
- **Compliance / regulatory** — controlled-substance gating (BR-CTRL-*) and PHI minimization (BR-PHI-*) are launch-gating; require URS (DOC-003) and threat-model (DOC-004) references before those stories enter a sprint (doc-strategy §8).
- **Analytics** — the 41%→60% metric must be instrumented (`product-analytics`) or BR-OUTCOME-001 is unverifiable (OQ-2).

## Requirements traceability matrix (RTM)
See `RTM.md` (shared across all docs). This BRD fills the **"Business requirement (BRD)"** column against the business-goal skeleton seeded by `doc-strategy-advisor`.

## Open questions
| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| OQ-1: What exact window is "store hours" for the 99.9% SLO (BR-NFR-003)? | PM / architect | Pending — on ASSUMPTION-4 | — |
| OQ-2: How is the 41% on-time-refill baseline measured (numerator/denominator, window)? | product-analytics / PM | Pending — blocks BR-OUTCOME-001 evidence | — |
| OQ-3: Which regulatory body's rules govern per-store (varies by state)? | Compliance | Pending — feeds BR-CTRL-004 acceptance | — |
