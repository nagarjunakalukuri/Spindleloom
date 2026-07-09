# BRD: MedRemind — RxKart Prescription Refill Reminder & Approval Module

| Field | Value |
|---|---|
| Sponsor | RxKart leadership (ASSUMPTION-1: exact sponsor unnamed in brief — owner: PM to confirm) |
| Author | brd-writer (business analyst) |
| Status | Draft |
| Last updated | 2026-07-09 |

> **Upstream gap:** my contract expects an MRD; `01-doc-strategy.md` sanctioned dropping it (client-commissioned feature — market case already made). Market context below comes from the client brief only. Per the doc strategy, this BRD is kept 1-pager-lean for merging into the PRD.

## Executive summary
RxKart, a 40-store pharmacy chain with 250k monthly active app patients, loses revenue and patient adherence because only 41% of refills happen on time. MedRemind adds refill reminders and one-tap refill requests to the existing patient app, and an approval queue to the existing pharmacist portal, targeting a 60% on-time refill rate within two quarters — while staying compliant with HIPAA and controlled-substance rules.

## Background and problem statement
Today patients must remember refill dates themselves and phone or visit a store; pharmacists handle refill requests ad hoc with no unified queue. The result: 59% of refills are late or missed, hurting patient health outcomes, prescription revenue, and pharmacist efficiency. RxKart already owns the two channels (patient app, pharmacist portal) needed to fix this.

## Business goals and objectives
- Raise the on-time refill rate from 41% to 60% within 2 quarters of launch.
- Deliver a first shippable slice within 3 sprints (~6 weeks), per leadership timeline.
- Remain fully compliant with HIPAA and DEA/state-board controlled-substance rules — zero reportable violations attributable to this module.

## Success metrics / KPIs
- On-time refill rate: baseline 41% → target 60% (within 2 quarters of launch).
- Reportable HIPAA/controlled-substance violations caused by the module: target 0.
- ASSUMPTION-2: "on-time refill" = refill dispensed on or before the prescription due date — owner: PM/RxKart to ratify the exact definition and measurement window.

## Scope
**In scope:**
- Refill reminders to patients (push and SMS) when a prescription is due.
- One-tap refill request from the reminder.
- Pharmacist refill-request queue with approve/reject decisions.
- Pharmacist-suggested generic substitution, requiring patient acceptance before dispensing.
- Compliant handling of controlled substances (Schedule II–V) and PHI minimization in notifications.

**Out of scope:**
- New patient acquisition or app-store marketing — this module serves existing app patients.
- Prescription e-prescribing, transfers, or new-prescription intake — refills of existing prescriptions only.
- Payments, insurance adjudication, and delivery/shipping — unchanged existing processes.
- Replacing the existing patient app or pharmacist portal — MedRemind extends both.

## Stakeholders
| Name | Role | Interest / responsibility |
|---|---|---|
| RxKart leadership | Sponsor / approver | Funds the work; owns the 41%→60% target and 3-sprint slice deadline |
| Patients (250k MAU) | End users | Timely reminders; effortless refills; privacy of their health data |
| Pharmacists (40 stores) | End users / operators | Manageable queue; safe dispensing; substitution and controlled-substance compliance |
| RxKart compliance officer | Approver (ASSUMPTION-3: role exists — owner: PM to confirm) | HIPAA and DEA/state-board adherence |
| PM (acting PO) | Business owner of this document | Scope, priorities, downstream PRD |

## Assumptions and constraints
- Constraint: HIPAA applies — PHI in notifications must be minimized; no drug names in SMS.
- Constraint: Schedule II–V prescriptions may not be auto-reminded or one-tap refilled.
- Constraint: reuse existing, already-contracted SMS and push notification channels (vendor specifics belong to the technical design, not this document).
- Constraint: client-stated service levels (reminder timeliness, queue responsiveness, availability) are handed to the SRS/RFC unchanged — not restated here as business requirements.
- ASSUMPTION-4: budget is the existing team's capacity (1 PM, 1 architect, 4 devs, 1 QA); no additional budget line stated — owner: sponsor.
- ASSUMPTION-5: patients have already consented (or will consent in-app) to receive SMS/push health reminders — owner: compliance officer.

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| PHI leaks into a notification (HIPAA breach) | Medium | High | PHI-minimization rule (BR-PHI-001); threat model; QA gate on notification content |
| Controlled-substance flow violates DEA/state-board rules | Medium | High | Explicit gating requirements (BR-CTRL-001..003); URS + compliance review before launch |
| Reminder fatigue — patients disable notifications | Medium | Medium | Frequency/relevance rules to be defined in PRD; monitor opt-out rate |
| 3-sprint slice pressure squeezes compliance work | High | High | Slice scope chosen so compliance-critical flows are never shipped partially |
| Pharmacist queue adds workload instead of saving it | Low | Medium | Pharmacist input on queue design; measure time-per-request post-launch |

## Current business process (as-is)
Patient remembers (or forgets) the refill date → phones or visits a store → pharmacist checks the prescription manually and dispenses. No proactive outreach, no shared queue, no structured substitution step. Pain: 59% of refills late/missed; pharmacist time lost to ad-hoc handling.

## Proposed business process (to-be)
System detects a refill coming due → patient gets a compliant reminder → patient requests the refill in one tap → request lands in the pharmacist queue → pharmacist approves, rejects, or proposes a generic substitution → patient accepts any substitution → pharmacy dispenses on time. Controlled substances follow a separate, pharmacist-initiated, identity-verified path.

## High-level requirements
| ID | Business requirement |
|---|---|
| BR-REM-001 | Patients receive a refill reminder (push and SMS) when a prescription is due. |
| BR-REF-001 | Patients can request a refill of a due prescription in one tap. |
| BR-QUE-001 | Pharmacists see all pending refill requests in a single portal queue. |
| BR-QUE-002 | Pharmacists can approve or reject each refill request. |
| BR-SUB-001 | Pharmacists can suggest a generic substitution on a refill request. |
| BR-SUB-002 | A substituted medication is dispensed only after the patient accepts the substitution. |
| BR-CTRL-001 | Controlled substances (Schedule II–V) are excluded from automated reminders and one-tap refills. |
| BR-CTRL-002 | Controlled-substance refills require an extra identity verification step. |
| BR-CTRL-003 | Controlled-substance refill contact is initiated by the pharmacist, not the system or patient. |
| BR-PHI-001 | Notifications minimize PHI; SMS messages never contain drug names. |

## Impact analysis
Affected: existing patient mobile app (new reminder/refill/substitution-acceptance flows), existing pharmacist portal (new queue), pharmacy dispensing workflow in all 40 stores (new approval step), compliance function (new notification and controlled-substance surface). Dependencies: existing notification channels; prescription data with due dates and controlled-substance schedule classification (ASSUMPTION-6: this data exists and is reliable in current systems — owner: architect to verify in recon). Risks and mitigations: see Risks table.

## Requirements traceability matrix (RTM)
Seeded as a standalone living file — see [`RTM.md`](RTM.md) (docs root); downstream writers append their columns/rows there. One row per BR-* above; PRD mappings pending `prd-writer`.

## Open questions
| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| Who is the named business sponsor? (ASSUMPTION-1) | PM | Open | 2026-07-09 |
| Exact definition + measurement of "on-time refill"? (ASSUMPTION-2) | PM / RxKart | Open | 2026-07-09 |
| Is SMS/push consent already captured for all 250k patients? (ASSUMPTION-5) | Compliance | Open | 2026-07-09 |
| What identity-verification method satisfies state boards for Schedule II–V? | Compliance / architect | Open — business rule needed before PRD locks the flow | 2026-07-09 |
