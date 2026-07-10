# URS: MedRemind — RxKart Refill Reminder & Approval Module (lean)

| Field | Value |
|---|---|
| Author | urs-writer (QA lead, validation hat — ownership per `01-doc-strategy.md`) |
| Status | Draft |
| Version | v0.1 |
| Regulatory basis | HIPAA Privacy Rule minimum-necessary standard (45 CFR §164.502(b)); DEA / state-board-of-pharmacy rules for Schedule II–V refills. Not a medical device — FDA 21 CFR 820.30 / GAMP validation not invoked; kept lean per `01-doc-strategy.md` URS verdict |
| Last updated | 2026-07-09 |

## 1. Purpose & scope
User-and-environment design input for MedRemind: what patients and pharmacists must be able to do, under what conditions, and to what safety/privacy standard. Traces up to `02-brd.md` (BR- IDs) and down to the test plan and RFC via `RTM.md`. Out of scope (per BRD): e-prescribing, new-prescription intake, transfers, payments, delivery, and replacing the existing app or portal.

## 2. Intended use
MedRemind is a communication-and-workflow adjunct to RxKart's existing patient app and pharmacist portal: it reminds patients when refills of existing prescriptions come due, carries one-tap refill requests into a pharmacist approval queue, and gates generic-substitution and controlled-substance flows. It does not diagnose, dose, or replace pharmacist clinical judgment — every dispensing decision remains with a licensed pharmacist. Conditions of use: patients on personal mobile devices, anywhere; pharmacists on portal workstations at the retail counter during store hours.

## 3. Users & environment
| User role | Competency / training | Environment & conditions |
|---|---|---|
| Patient (250k MAU) | Layperson; no training; has existing app account | Personal phone (push + SMS); home or on the move; frequent interruptions; SMS readable by bystanders/lock screen |
| Pharmacist (40 stores) | State-licensed pharmacist; brief portal walkthrough only | Busy retail counter; shared workstation; acts between customers, so queue actions must be fast and unambiguous |

## 4. Definitions
- **Operator** — the pharmacist acting on the refill queue; the accountable decision-maker.
- **Due prescription** — an existing prescription whose refill window has opened (exact "due"/"on-time" definition: BRD ASSUMPTION-2, open).
- **Controlled substance** — a prescription classified DEA Schedule II–V.
- **Dispensable** — a refill request that has cleared every required gate (approval; substitution acceptance; identity verification where applicable).
- **PHI** — protected health information under HIPAA.

## 5. User requirements
| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-REM-001 | The system shall notify a patient by push notification when a non-controlled prescription of theirs becomes due for refill. | Functional | Test | BR-REM-001 |
| URS-REM-002 | The system shall notify a patient by SMS when a non-controlled prescription of theirs becomes due for refill. | Functional | Test | BR-REM-001 |
| URS-REM-003 | The system shall let a patient opt out of refill reminders per channel at any time. (ASSUMPTION-8) | Functional | Test | BR-REM-001; BRD risk "reminder fatigue" |
| URS-REF-001 | The system shall let a patient submit a refill request for a due non-controlled prescription in one tap from the reminder. | Functional | Test | BR-REF-001 |
| URS-QUE-001 | The system shall present a pharmacist a single queue of all pending refill requests for their store. (ASSUMPTION-7) | Functional | Test | BR-QUE-001 |
| URS-QUE-002 | The system shall let a pharmacist approve a pending refill request. | Functional | Test | BR-QUE-002 |
| URS-QUE-003 | The system shall let a pharmacist reject a pending refill request. | Functional | Test | BR-QUE-002 |
| URS-SUB-001 | The system shall let a pharmacist propose a generic substitution on a pending refill request. | Functional | Test | BR-SUB-001 |
| URS-SUB-002 | The system shall block a substituted medication from becoming dispensable until the patient's acceptance of the substitution is recorded. | Safety | Test | BR-SUB-002 |
| URS-CTRL-001 | The system shall exclude Schedule II–V prescriptions from automated refill reminders. | Safety | Test | BR-CTRL-001 |
| URS-CTRL-002 | The system shall exclude Schedule II–V prescriptions from one-tap refill requests. | Safety | Test | BR-CTRL-001 |
| URS-CTRL-003 | The system shall require successful patient identity verification before a Schedule II–V refill request proceeds. (method open — BRD open question, compliance/architect) | Safety | Test | BR-CTRL-002 |
| URS-CTRL-004 | The system shall permit refill contact for a Schedule II–V prescription to be initiated only by a pharmacist. | Safety | Test | BR-CTRL-003 |
| URS-CTRL-005 | The system shall treat a prescription whose schedule classification is missing or unknown as controlled. (ASSUMPTION-9, fail-safe default) | Safety | Test | Derived from BR-CTRL-001 |
| URS-PHI-001 | The system shall send SMS messages that contain no drug name. | Privacy | Test + inspection | BR-PHI-001 |
| URS-PHI-002 | The system shall limit reminder content to a generic refill prompt — no diagnosis, prescriber, or medication details. (ASSUMPTION-10) | Privacy | Inspection | BR-PHI-001 |
| URS-AUD-001 | The system shall record each pharmacist queue decision (approve, reject, substitution proposal) with the acting pharmacist's identity and a timestamp. | Data integrity | Test | BR-QUE-002, BR-SUB-001; `01-doc-strategy.md` audit expectation |
| URS-AUD-002 | The system shall record the outcome of each controlled-substance identity-verification attempt with a timestamp. | Data integrity | Test | BR-CTRL-002 |

## 6. Safety & quality attributes
- **Fail-safe gating:** controlled-substance exclusions (URS-CTRL-001/002/005) must fail closed — when in doubt, no automation.
- **Substitution gate:** dispensing a substitution without recorded patient acceptance is a safety defect, not a UX bug (URS-SUB-002).
- **PHI minimization:** notification content is a QA release gate (URS-PHI-001/002); SMS is treated as an untrusted channel.
- **Attributability:** every operator decision and verification outcome is attributable, timestamped, and retained for audit (URS-AUD-001/002 — ALCOA-lean, not full ALCOA+).

## 7. Constraints & assumptions
- HIPAA applies to all notification content; DEA/state-board rules govern the Schedule II–V flow (per brief and BRD).
- Reuses existing app, portal, and contracted notification channels; service levels (5-min delivery, <2s queue, 99.9%) are SRS/RFC territory, not restated here.
- Carried forward from BRD: ASSUMPTION-2 ("on-time" definition), ASSUMPTION-5 (SMS/push consent), open identity-verification method.
- ASSUMPTION-7: the queue is scoped to the pharmacist's own store, not chain-wide — owner: PM to confirm.
- ASSUMPTION-8: per-channel reminder opt-out is required (consent hygiene; not stated in brief) — owner: compliance officer.
- ASSUMPTION-9: unknown/missing schedule classification defaults to "controlled" — owner: compliance officer + architect (ties to BRD ASSUMPTION-6 data reliability).
- ASSUMPTION-10: minimized reminder content = generic prompt + pharmacy name + app link only — owner: compliance officer.

## 8. Traceability
URS rows were appended to the living [`RTM.md`](RTM.md) ("User req (URS)" column) in the same pass that assigned these IDs. Design-spec and test-protocol mappings are filled downstream by the RFC (srs/sdd/tsd) and `test-plan-writer`.

## 9. Change control
| Version | Change | Reason | Approved by | Date |
|---|---|---|---|---|
| v0.1 | Initial draft | New module | Pending (PM + compliance officer) | 2026-07-09 |
