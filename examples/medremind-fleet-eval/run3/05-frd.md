# FRD: MedRemind — Prescription Refill Reminder & Approval Module

*Author: `frd-writer` (business analyst / PM) · phase: requirements · 2026-07-09 · run3*
*Upstream: `prd-writer` (`04-prd.md`), `urs-writer` (`03-urs.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Source of truth for scope: `brief.md`.*
*Downstream: `srs-writer`, `backlog-manager`, `test-plan-writer`, `api-designer`, `ux-ui-designer`, `product-analytics`, `architect`, `sdd-writer`. RTM: `examples/medremind-fleet-eval/run3/RTM.md`.*

| Field | Value |
|---|---|
| Author | `frd-writer` (BA / PM) |
| Status | Draft |
| Related PRD | `04-prd.md` (PRD-RMD/-RFL/-QUE/-SUB/-CTL/-PRF stories) |
| Last updated | 2026-07-09 |

## Overview

MedRemind specifies the exact, deterministic behavior of the refill loop **remind → one-tap request → pharmacist triage/decision**, plus the two high-risk flows `doc-strategy` (DS-04) kept as explicit FRD sections — the **controlled-substance exclusion** and **generic-substitution acceptance**. This FRD defines every trigger, precondition, rule, state transition, and unhappy-path outcome so developers and QA have no ambiguity. It states behavior only; the *how* (Twilio/Firebase pipeline, classification-source read mechanism, NFR budgets) is owned by `srs-writer` / `sdd-writer` / `tsd-writer` and by the architect.

## Documentation mode (why a standalone FRD, not only tickets)

Per this agent's Agile guidance, routine functional logic would normally live in Azure Boards PBIs (the team's system of record, `doc-strategy` DS-04). Two things are kept as explicit, auditor-readable FRD sections because they are **regulated and safety-critical** — a single defect is a HIPAA or DEA violation (KPI-5 guardrail): the **controlled-substance exclusion** (§FRD-CTL) and **generic-substitution acceptance** (§FRD-SUB). All requirements below are written as ticket-ready acceptance criteria so `backlog-manager` can lift them into Boards without re-authoring.

## Actors & preconditions

- **Patient (Priya)** — authenticated via the existing IdP (ASSUMPTION-4), on the 250k-MAU app, in an *uncontrolled* environment (`03-urs.md` §3): no notification content may reveal a drug name.
- **Pharmacist (Sam)** — licensed, DEA-trained, acting in the existing portal queue during store hours.
- **Reminder job** — the scheduled process that evaluates due prescriptions (behavioral trigger; scheduling mechanism owned by `srs-writer`/architect).
- **Preconditions:** an existing, active prescription record carrying an authoritative DEA-schedule classification (ASSUMPTION-9). MedRemind never originates prescriptions.

## Functional requirements

### FRD-RMD — Reminder eligibility & delivery (traces PRD-RMD-001, PRD-RMD-002)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-RMD-001 | The system shall treat a prescription as reminder-eligible only when it is active, non-controlled, has at least one refill remaining, with its refill-due date reached. | Given a prescription failing any one of {active, non-controlled, refills-remaining, due}, When the reminder job evaluates it, Then it is not selected for a reminder. | PRD-RMD-001, URS-USE-001 |
| FRD-RMD-002 | The system shall combine all of a patient's prescriptions that become eligible within one reminder window into a single reminder notification. | Given two eligible prescriptions for the same patient in the same window (ASSUMPTION-15), When the job runs, Then exactly one push and one SMS are produced for that patient. | PRD-RMD-001, ASSUMPTION-10, ASSUMPTION-15 |
| FRD-RMD-003 | The system shall exclude any drug name from all push notification content, including its title, body, lock-screen preview. | Given a reminder push, When it renders on the device (including lock screen), Then no drug name appears in any visible field. | PRD-RMD-001, URS-DAT-001 |
| FRD-RMD-004 | The system shall compose the SMS body as neutral copy plus a deep link, containing no drug name. | Given a reminder SMS, When its body is inspected, Then it states a prescription is ready to refill with a deep link and names no drug. | PRD-RMD-002, URS-DAT-001, CON-2 |
| FRD-RMD-005 | The system shall dispatch the reminder over each channel that the patient has not disabled. | Given a patient with push and SMS both enabled, When a reminder fires, Then it is dispatched on both; Given a channel disabled (FRD-PRF-001), Then that channel is skipped. | PRD-RMD-001, PRD-RMD-002 |
| FRD-RMD-006 | The system shall send at most one reminder per prescription per refill-due cycle. | Given a prescription already reminded this cycle, When the job re-runs, Then no additional reminder is produced for it. | PRD-RMD-001 |
| FRD-RMD-007 | The system shall treat push and SMS as redundant channels such that a delayed or failed SMS produces no duplicate reminder and no duplicate refill request. | Given the SMS provider reports failure or late delivery, When the patient acts on the push instead, Then exactly one reminder event and at most one request exist. | PRD-RMD-002 |

### FRD-RFL — One-tap refill request (traces PRD-RFL-001)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-RFL-001 | The system shall create a refill request from a single confirmation action, requiring no second-screen form on the happy path. | Given a delivered reminder for an eligible non-controlled prescription, When the patient taps "Request refill" and confirms once, Then a request is created without any further form. | PRD-RFL-001, URS-USE-003 |
| FRD-RFL-002 | The system shall make refill-request creation idempotent per prescription per due cycle. | Given a request already created for the prescription this cycle, When the patient taps "Request refill" again, Then no second queue item is created and the existing state is shown. | PRD-RFL-001 |
| FRD-RFL-003 | The system shall refuse a refill request at tap time, with a stated reason, when the prescription is no longer eligible. | Given a prescription now expired, out of refills, or reclassified controlled, When the patient taps to request, Then no request is created, a reason is shown, and the patient is routed to the correct path (controlled → FRD-CTL-004). | PRD-RFL-001, PRD-CTL-001 |
| FRD-RFL-004 | The system shall display a "request received" state to the patient once a request is created. | Given a successful request, When creation completes, Then the patient sees a distinct "request received" acknowledgement state. | PRD-RFL-001 |

### FRD-QUE — Pharmacist queue & decisions (traces PRD-QUE-001, PRD-QUE-002, PRD-QUE-003)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-QUE-001 | The system shall present pending refill requests in one prioritized queue showing per item the patient, prescription reference, request time. | Given one or more pending requests, When the pharmacist opens the queue, Then all pending items appear in one prioritized view (order per ASSUMPTION-13) with those decision fields. | PRD-QUE-001, URS-USE-004 |
| FRD-QUE-002 | The system shall never list a controlled-substance (Schedule II–V) item as a one-tap refill request in the queue. | Given a Schedule II–V prescription, When the queue renders, Then no self-service one-tap request for it is present. | PRD-QUE-001, PRD-CTL-001, URS-SAF-002 |
| FRD-QUE-003 | The system shall show an explicit empty state when no requests are pending. | Given zero pending requests, When the pharmacist opens the queue, Then an explicit empty state is shown, not a spinner or error. | PRD-QUE-001 |
| FRD-QUE-004 | The system shall record an approve decision as an attributable, timestamped audit entry identifying the acting pharmacist, and remove the item from the pending queue. | Given a pending request, When the pharmacist approves it, Then an audit entry with pharmacist identity and timestamp is written and the item leaves the pending queue. | PRD-QUE-002, URS-USE-005, URS-DAT-002 |
| FRD-QUE-005 | The system shall block a reject decision until a reject reason is supplied, then record it as an attributable, timestamped audit entry and notify the patient with no drug name in any SMS. | Given a pending request, When the pharmacist rejects without a reason, Then the rejection is blocked; When a reason is supplied, Then the audit entry is written and the patient is notified. | PRD-QUE-003, URS-USE-006, URS-DAT-002, URS-DAT-001 |
| FRD-QUE-006 | The system shall record exactly one decision per request under concurrent pharmacist action. | Given two pharmacists opening the same pending request, When both submit a decision, Then only the first is recorded and the second sees an already-decided state. | PRD-QUE-002 |

### FRD-SUB — Generic-substitution acceptance (high-risk section; traces PRD-SUB-001)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-SUB-001 | The system shall let a pharmacist attach a suggested generic substitution to a refill request. | Given a request under review, When the pharmacist attaches a generic substitution, Then the substitution is associated with that request. | PRD-SUB-001, URS-USE-007 |
| FRD-SUB-002 | The system shall block dispensing of a substituted prescription until the patient's explicit acceptance is recorded with a timestamp as the consent record. | Given an attached substitution, When the patient records acceptance, Then a timestamped consent record is stored and dispensing may proceed; absent acceptance, dispensing stays blocked. | PRD-SUB-001, URS-SAF-003, URS-DAT-003 |
| FRD-SUB-003 | The system shall halt the substituted dispensing when the patient declines or does not respond within the substitution response window, routing to pharmacist follow-up. | Given a decline or no response within the window (ASSUMPTION-14), When the window closes, Then dispensing does not proceed on the substitution and the item routes to pharmacist follow-up. | PRD-SUB-001, URS-SAF-003 |

### FRD-CTL — Controlled-substance exclusion (highest-risk section; traces PRD-CTL-001)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-CTL-001 | The system shall never enter a prescription classified DEA Schedule II–V into the reminder job. | Given a Schedule II–V prescription reaching its due date, When the reminder job runs, Then no reminder is produced for it. | PRD-CTL-001, URS-SAF-001, CON-3 |
| FRD-CTL-002 | The system shall never present a one-tap / self-service refill option for a prescription classified DEA Schedule II–V. | Given a Schedule II–V prescription, When any patient surface renders, Then no one-tap refill affordance is shown. | PRD-CTL-001, URS-SAF-002, CON-3 |
| FRD-CTL-003 | The system shall fail closed by treating a prescription as excluded from automation when its authoritative DEA-schedule classification is missing or unreadable. | Given the classification source is absent or unreadable (ASSUMPTION-9), When eligibility is evaluated, Then the prescription is excluded from reminders and one-tap refill (never fail-open into automation). | PRD-CTL-001, URS-SAF-001, ASSUMPTION-9 |
| FRD-CTL-004 | The system shall route a controlled-substance refill need to the identity-verification and pharmacist-initiated-contact path instead of any automated fulfilment. | Given a patient with a Schedule II–V refill need, When they seek a refill, Then they are routed to identity verification then pharmacist-initiated contact, with no automated path offered. | PRD-CTL-001, URS-SAF-004, URS-SEC-001, CON-3 |

### FRD-PRF / FRD-CFN — Preferences & closing-the-loop confirmation

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-PRF-001 | The system shall stop sending reminders on a channel once the patient disables that channel, and shall persist the preference across cycles. | Given the patient disables a reminder channel, When later reminders fire, Then none are sent on the disabled channel and the setting persists (granularity per ASSUMPTION-11). | PRD-PRF-001, ASSUMPTION-11 |
| FRD-CFN-001 | The system shall notify the patient that a refill is approved/ready after a pharmacist approves it, with no drug name in any SMS confirmation. | Given an approved request (FRD-QUE-004), When approval completes, Then the patient receives an approval/ready confirmation naming no drug (channel/copy per ASSUMPTION-12). | PRD-QUE-002, ASSUMPTION-12, URS-DAT-001 |

## User flow

**Patient happy path:** prescription hits refill-due date → FRD-RMD-001 eligibility (non-controlled per FRD-CTL-001/-003) → FRD-RMD-002 batched, FRD-RMD-003/-004 PHI-minimized reminder over enabled channels (FRD-RMD-005) → patient taps deep link → FRD-RFL-003 tap-time re-check → FRD-RFL-001 one-tap + single confirm → FRD-RFL-004 "request received" → request enters queue → pharmacist approves (FRD-QUE-004) → FRD-CFN-001 approval/ready confirmation.

**Pharmacist happy path:** open portal → FRD-QUE-001 prioritized queue (FRD-QUE-003 empty state if none) → select request → approve (FRD-QUE-004) **or** reject-with-reason (FRD-QUE-005) **or** attach substitution (FRD-SUB-001).

**Substitution path:** pharmacist suggests generic (FRD-SUB-001) → patient accepts → consent stored, dispensing proceeds (FRD-SUB-002); patient declines / times out → dispensing halts on the substitution, routes to pharmacist follow-up (FRD-SUB-003).

**Controlled-substance path:** Schedule II–V is never reminded or one-tapped (FRD-CTL-001/-002); on missing/unreadable classification the system fails closed (FRD-CTL-003); the patient is routed to identity verification + pharmacist-initiated contact (FRD-CTL-004).

## Business rules

- **Eligibility predicate (FRD-RMD-001):** active AND non-controlled AND refills-remaining AND due. All four required; failing any one excludes the prescription.
- **Fail-closed default (FRD-CTL-003):** the automation-eligible state is only reached on a positively-read non-controlled classification. Absence of a positive signal = excluded.
- **Idempotency key (FRD-RFL-002, FRD-RMD-006):** one reminder and at most one request per prescription per refill-due cycle.
- **Reject reason mandatory (FRD-QUE-005):** rejection is not accepted without a non-empty reason.
- **Consent-before-dispense (FRD-SUB-002):** recorded patient acceptance is a hard precondition to dispensing a substitution.
- **PHI minimization is channel-wide (FRD-RMD-003/-004, FRD-QUE-005, FRD-CFN-001):** no drug name in any push preview, SMS body, or outbound patient notification — the guardrail is the uncontrolled environment, not the transport.

## Edge cases & error handling

| Scenario | Expected system response | Req |
|---|---|---|
| SMS delivery fails or is delayed | Push is redundant; no duplicate reminder or request is created | FRD-RMD-007 |
| Duplicate / double tap on "Request refill" | Idempotent — no second queue item; existing state shown | FRD-RFL-002 |
| Prescription ineligible at tap time (expired / no refills / now controlled) | Request refused with a stated reason; none created; routed to correct path | FRD-RFL-003 |
| DEA classification missing or unreadable | Fail closed — excluded from reminders and one-tap refill | FRD-CTL-003 |
| Patient on a shared / lock-screen-visible device | No drug name in any push preview or SMS body | FRD-RMD-003, FRD-RMD-004 |
| Pharmacist rejects with no reason | Blocked until a reason is supplied | FRD-QUE-005 |
| Two pharmacists decide the same request | Exactly one decision recorded; second sees already-decided | FRD-QUE-006 |
| Substitution declined or no response in window | Dispensing halts on the substitution; pharmacist follow-up | FRD-SUB-003 |
| No pending requests | Explicit empty state, not a spinner or error | FRD-QUE-003 |
| Multiple prescriptions due same window | Batched into one push and one SMS per patient | FRD-RMD-002 |

## Assumptions

Carried from upstream (do not re-invent; not decided): **ASSUMPTION-9** (owner architect / compliance officer — authoritative DEA-schedule classification source; FRD-CTL-003 depends on it), **ASSUMPTION-10** (owner PM / product-analytics — batching), **ASSUMPTION-11** (owner PM — opt-out granularity), **ASSUMPTION-12** (owner PM — post-approval confirmation channel/copy), **ASSUMPTION-4** (owner PM — existing IdP).

New in this FRD:

- **ASSUMPTION-13** *(owner: PM / `ux-ui-designer`)* — The queue prioritization order (e.g., oldest-request-first vs. nearest-lapse-first) is not yet ratified; FRD-QUE-001 states that a single prioritized order exists, not which key. `ux-ui-designer` / PM to fix the ordering key.
- **ASSUMPTION-14** *(owner: PM / `ux-ui-designer`)* — The substitution response window duration before FRD-SUB-003 fallback is not yet set. The behavior (halt-on-no-response) is defined; the duration is a PM/design decision.
- **ASSUMPTION-15** *(owner: PM / `product-analytics`)* — The reminder batching window (FRD-RMD-002) is taken as the same calendar day in the patient's local timezone. This concretizes ASSUMPTION-10's batching; the exact window granularity needs PM ratification.

## Traceability

Rows appended to `examples/medremind-fleet-eval/run3/RTM.md` (the *Functional (FRD/PBI)* column) in this pass — atomic IDs only.

| FRD ID | PRD story | URS |
|---|---|---|
| FRD-RMD-001 | PRD-RMD-001 | URS-USE-001 |
| FRD-RMD-002 | PRD-RMD-001 | — (ASSUMPTION-10/-15) |
| FRD-RMD-003 | PRD-RMD-001 | URS-DAT-001 |
| FRD-RMD-004 | PRD-RMD-002 | URS-DAT-001 |
| FRD-RMD-005 | PRD-RMD-001, PRD-RMD-002 | URS-USE-001, URS-USE-002 |
| FRD-RMD-006 | PRD-RMD-001 | — |
| FRD-RMD-007 | PRD-RMD-002 | — |
| FRD-RFL-001 | PRD-RFL-001 | URS-USE-003 |
| FRD-RFL-002 | PRD-RFL-001 | — |
| FRD-RFL-003 | PRD-RFL-001, PRD-CTL-001 | URS-USE-003 |
| FRD-RFL-004 | PRD-RFL-001 | — |
| FRD-QUE-001 | PRD-QUE-001 | URS-USE-004 |
| FRD-QUE-002 | PRD-QUE-001, PRD-CTL-001 | URS-SAF-002 |
| FRD-QUE-003 | PRD-QUE-001 | — |
| FRD-QUE-004 | PRD-QUE-002 | URS-USE-005, URS-DAT-002 |
| FRD-QUE-005 | PRD-QUE-003 | URS-USE-006, URS-DAT-002, URS-DAT-001 |
| FRD-QUE-006 | PRD-QUE-002 | — |
| FRD-SUB-001 | PRD-SUB-001 | URS-USE-007 |
| FRD-SUB-002 | PRD-SUB-001 | URS-SAF-003, URS-DAT-003 |
| FRD-SUB-003 | PRD-SUB-001 | URS-SAF-003 |
| FRD-CTL-001 | PRD-CTL-001 | URS-SAF-001 |
| FRD-CTL-002 | PRD-CTL-001 | URS-SAF-002 |
| FRD-CTL-003 | PRD-CTL-001 | URS-SAF-001 (ASSUMPTION-9) |
| FRD-CTL-004 | PRD-CTL-001 | URS-SAF-004, URS-SEC-001 |
| FRD-PRF-001 | PRD-PRF-001 | — (ASSUMPTION-11) |
| FRD-CFN-001 | PRD-QUE-002 | URS-DAT-001 (ASSUMPTION-12) |

## Requirement-quality note (29148/INCOSE lint justification)

`validate_reqs.py` flags a residual set of `shall … and/or …` findings on FRD IDs where the conjunction is **within a single obligation**, not two bundled ones — deliberate, kept for clarity:

- **FRD-RMD-007, FRD-CTL-003, FRD-CTL-004, FRD-SUB-003** — the `and`/`or` joins two *triggers or failure modes of one behavior* (redundant channels; missing-or-unreadable classification; the single "identity-verification + pharmacist-contact" path; decline-or-no-response), not two obligations.
- **FRD-QUE-004, FRD-QUE-005** — the conjunction joins the *effects of one atomic decision action* (approve = record audit entry + dequeue; reject = require reason → record → notify). Splitting would fragment one state transition and lose the ordering guarantee. If Boards granularity is preferred, `backlog-manager` may split these into sub-tasks; the FRD obligation stays one transition.

The lint also attributes PRD-* / URS-* compound findings to this file because those IDs are *cited* here (source/trace columns); they are owned upstream by `prd-writer` / `urs-writer`, not authored here.

## Flags

```
FLAG(architect): FRD-CTL-003 (fail closed on missing/unreadable classification) is only testable
once the read boundary defines what "missing or unreadable" looks like at the authoritative
DEA-schedule source (ASSUMPTION-9, owner architect / compliance officer). The functional intent
is fixed here — never fail-open into automation — but the detectable signal for "unreadable" and
the source-of-truth field are yours to define in the SRS/SDD. Echoes the architect FLAG in
04-prd.md and 03-urs.md §10; no new dependency, restated at the functional read boundary.
```
