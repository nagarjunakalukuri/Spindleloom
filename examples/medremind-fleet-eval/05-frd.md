# FRD: MedRemind — Refill Reminder & Approval Module

| Field | Value |
|---|---|
| Author | frd-writer (PM/BA hat) |
| Status | Draft |
| Related PRD stories | PRD-REM-001/002, PRD-REF-001, PRD-QUE-001/002, PRD-SUB-001/002, PRD-CTRL-001/002/003, PRD-PHI-001 (`04-prd.md`); URS `03-urs.md` |
| Last updated | 2026-07-09 |

## Overview
Exact behavior for the five MedRemind flows: reminder scheduling, one-tap refill request, pharmacist approve/reject, generic substitution, and the controlled-substance + audit gates. PRD-REM-003 (snooze, Could/slice-3) is deliberately not decomposed here. Agile note: this team runs 2-week sprints in Azure DevOps — the backlog-manager should embed these rows as ticket acceptance criteria; this doc stays the compliance-grade source for the CTRL/PHI/AUD flows only.

## Actors & preconditions
- **Patient** — has app account; consent per channel captured (ASSUMPTION-5, unratified); acts on personal phone.
- **Pharmacist** — licensed; signed in to the portal with a store affiliation (queue scope per ASSUMPTION-7).
- **System (scheduler)** — has prescription due dates and schedule classification (ASSUMPTION-6: data reliable; unknown fails closed per ASSUMPTION-9).

## Functional requirements
Request states: `Pending → Awaiting-patient (substitution) → Pending → Approved | Rejected`; controlled refills add a `Verification-required` gate before `Approved` becomes dispensable.

| ID | Requirement ("the system shall …") | Acceptance criteria (Given/When/Then) | Source |
|---|---|---|---|
| FRD-REM-001 | The system shall schedule one reminder per due, non-controlled prescription of a consent-holding patient, firing at 09:00 store-local time on the due date (ASSUMPTION-14). | Given a non-controlled prescription whose due date is D and a consented patient, when the scheduler runs, then exactly one reminder is queued for D 09:00 store-local. | PRD-REM-001; URS-REM-001/002 |
| FRD-REM-002 | The system shall deliver a scheduled reminder by push notification when the patient's push channel is enabled. | Given a queued reminder and push enabled, when it fires, then a push with minimized content (ASSUMPTION-10) is sent via Firebase. | PRD-REM-001; URS-REM-001 |
| FRD-REM-003 | The system shall deliver a scheduled reminder by SMS containing no drug name when the patient's SMS channel is enabled. | Given a queued reminder and SMS enabled, when it fires, then an SMS is sent via Twilio whose body contains no drug name, diagnosis, or prescriber. | PRD-REM-001; URS-REM-002, URS-PHI-001 |
| FRD-REM-004 | The system shall suppress reminders on any channel the patient has opted out of, leaving other channels unaffected. | Given SMS opted out, when a reminder fires, then no SMS is sent and push (if enabled) is still sent. | PRD-REM-002; URS-REM-003 |
| FRD-REM-005 | The system shall send the reminder on each remaining enabled channel when delivery on one channel fails. | Given push delivery fails, when the failure is reported, then the SMS send still executes (and vice versa); both failures are logged. | PRD-REM-001 (flow: error states) |
| FRD-REF-001 | The system shall create one refill request in state `Pending` — capturing prescription, patient, fulfilling store, and request timestamp — when the patient taps "Request refill" on a reminder. | Given a received reminder for a due non-controlled prescription, when the patient taps once, then a `Pending` request appears in the fulfilling store's queue. | PRD-REF-001; URS-REF-001 |
| FRD-REF-002 | The system shall show the patient an in-app confirmation naming the fulfilling store immediately after request creation, on a single screen. | Given a successful tap, when the request is created, then confirmation with store name renders without further navigation. | PRD-REF-001 |
| FRD-REF-003 | The system shall reject creation of a second open request for the same prescription, instead showing the existing request's status. | Given an open (`Pending`/`Awaiting-patient`) request, when the patient taps again, then no new request is created and the existing status is shown. | PRD-REF-001 (flow: duplicate tap) |
| FRD-REF-004 | The system shall present a retry option, without silently discarding the tap, when request submission fails in transit. | Given a network drop mid-submission, when the app cannot confirm creation, then the patient sees a retry prompt and retrying creates at most one request. | PRD-REF-001 (flow: error states) |
| FRD-QUE-001 | The system shall present a pharmacist a queue of their store's open requests — patient, medication, request time, state — ordered oldest-first. | Given open requests for store S, when a store-S pharmacist opens the queue, then all `Pending` and `Awaiting-patient` requests appear oldest-first with those fields. | PRD-QUE-001; URS-QUE-001 |
| FRD-QUE-002 | The system shall set a `Pending` request to `Approved`, remove it from the pending view, and notify the patient (minimized content) when a pharmacist approves it. | Given a `Pending` request, when the pharmacist taps Approve, then state = `Approved`, it leaves pending, and the patient is notified with no drug name in SMS. | PRD-QUE-002; URS-QUE-002 |
| FRD-QUE-003 | The system shall set a `Pending` request to `Rejected`, remove it from the pending view, and notify the patient with a "contact your pharmacy" next step (ASSUMPTION-13) when a pharmacist rejects it. | Given a `Pending` request, when the pharmacist taps Reject, then state = `Rejected` and the patient receives the next-step notification. | PRD-QUE-002; URS-QUE-003 |
| FRD-QUE-004 | The system shall record only the first decision on a request and return an "already decided" error to any later conflicting decision attempt. | Given two pharmacists act on the same request, when the second decision arrives after the first commits, then it is refused and the queue view refreshes. | PRD-QUE-002 (flow: concurrency) |
| FRD-SUB-001 | The system shall set a `Pending` request to `Awaiting-patient` and send the patient an in-app accept/decline prompt when a pharmacist proposes a generic substitution. | Given a `Pending` request with a generic available, when the pharmacist proposes it, then state = `Awaiting-patient` and the in-app prompt (in-app only, per PRD decision log) is delivered. | PRD-SUB-001; URS-SUB-001 |
| FRD-SUB-002 | The system shall return an `Awaiting-patient` request to `Pending` with the substitute medication and a recorded acceptance when the patient accepts. | Given a proposed substitution, when the patient taps Accept, then acceptance is recorded and the request is decidable with the substitute. | PRD-SUB-002; URS-SUB-002 |
| FRD-SUB-003 | The system shall return an `Awaiting-patient` request to `Pending` with the original medication when the patient declines the substitution. | Given a proposed substitution, when the patient taps Decline, then the request reverts to `Pending` showing the original medication to the pharmacist. | PRD-SUB-002 |
| FRD-SUB-004 | The system shall block a request that carries an unaccepted substitution from being set to `Approved`. | Given state `Awaiting-patient`, when a pharmacist attempts Approve, then the action is refused with reason "awaiting patient response". | PRD-SUB-002; URS-SUB-002 |
| FRD-SUB-005 | The system shall keep an unanswered substitution in `Awaiting-patient`, visibly flagged in the queue, and shall let the proposing store's pharmacist withdraw it, reverting the request to `Pending` with the original medication (ASSUMPTION-15). | Given no patient response, when the pharmacist views the queue, then the request shows "awaiting patient"; when withdrawn, then state = `Pending`, original medication. | PRD-SUB-001 (flow: unanswered) |
| FRD-CTRL-001 | The system shall schedule no reminder for a prescription classified Schedule II–V. | Given a Schedule II–V prescription reaching its due date, when the scheduler runs, then no reminder is queued on any channel. | PRD-CTRL-001; URS-CTRL-001 |
| FRD-CTRL-002 | The system shall offer no one-tap refill control for a Schedule II–V prescription in any patient-facing view. | Given a controlled prescription, when the patient views it in-app, then no "Request refill" control is rendered. | PRD-CTRL-001; URS-CTRL-002 |
| FRD-CTRL-003 | The system shall treat a prescription with missing or unknown schedule classification as controlled (ASSUMPTION-9, fail-closed). | Given classification is null/unrecognized, when any reminder or one-tap path evaluates it, then the controlled-substance rules (FRD-CTRL-001/002/004/005) apply. | PRD-CTRL-001; URS-CTRL-005 |
| FRD-CTRL-004 | The system shall block a controlled-substance refill from becoming dispensable until a successful identity verification is recorded for it. Verification *method* is an open question (compliance/architect) — not defined here. | Given a controlled refill without a recorded successful verification, when dispensing is attempted, then it is refused with reason "verification required". | PRD-CTRL-002; URS-CTRL-003 |
| FRD-CTRL-005 | The system shall generate no patient-facing prompt for a due controlled prescription, exposing contact options only in the pharmacist portal. | Given a controlled prescription due, when processing completes, then the patient receives nothing and the portal shows pharmacist-initiated contact options. | PRD-CTRL-003; URS-CTRL-004 |
| FRD-PHI-001 | The system shall compose every outbound notification from the minimized template only: generic refill/status prompt + pharmacy name + app link (ASSUMPTION-10). | Given any notification event, when content is composed, then it contains no drug name, diagnosis, prescriber, or medication detail on any channel's preview surface. | PRD-PHI-001; URS-PHI-001/002 |
| FRD-AUD-001 | The system shall write an audit record — acting pharmacist identity, action, request ID, timestamp — for every queue decision (approve, reject, substitution proposal, withdrawal). | Given any queue decision commits, when the transaction completes, then exactly one immutable audit record with those fields exists. | URS-AUD-001 (⚠ no PRD story — see Traceability) |
| FRD-AUD-002 | The system shall write an audit record — outcome and timestamp — for every controlled-substance identity-verification attempt, successful or failed. | Given a verification attempt concludes, when its result is known, then an audit record with outcome + timestamp exists. | URS-AUD-002 (⚠ no PRD story); PRD-CTRL-002 (nearest) |
| FRD-AUD-003 | The system shall record the patient's substitution response (accept or decline) with a timestamp. | Given the patient answers a substitution prompt, when the response commits, then the response and its timestamp are retrievable for audit. | URS-SUB-002, URS-AUD-001; PRD-SUB-002 |

## Business rules
- One open request per prescription at a time (FRD-REF-003); requests are store-scoped (ASSUMPTION-7).
- Fail-closed: unknown schedule ⇒ controlled (ASSUMPTION-9); unverified controlled refill ⇒ not dispensable; unaccepted substitution ⇒ not approvable.
- Notification content rule (FRD-PHI-001) applies to reminders **and** outcome notifications — SMS is an untrusted channel.
- Delivery-timing (5-min window), queue load (<2s @500), availability (99.9%): SRS territory, not restated here.

## Edge cases & error handling
| Scenario | Expected system response |
|---|---|
| One channel fails / patient opted out of one channel | Other enabled channel still fires (FRD-REM-004/005) |
| Duplicate tap or retry after network drop | At most one open request; existing status shown (FRD-REF-003/004) |
| Two pharmacists decide the same request | First commit wins; second gets "already decided" (FRD-QUE-004) |
| Substitution prompt never answered | Request held `Awaiting-patient`, flagged; pharmacist may withdraw (FRD-SUB-005) |
| Schedule classification missing | Treated as controlled; no automation (FRD-CTRL-003) |
| Opted-out patient's refill due | No reminder; prescription still visible in-app (FRD-REM-004; PRD flow) |

## Assumptions (practice 8 — tagged, owned, unratified until signed off)
- Carried: ASSUMPTION-2, -5, -6 (BRD); -7, -8, -9, -10 (URS); -13 (PRD). New here: **ASSUMPTION-14** (reminder fires 09:00 store-local on due date — owner: PM); **ASSUMPTION-15** (pharmacist may withdraw an unanswered substitution proposal — owner: PM). None may enter a sprint-committed AC before ratification.

## Traceability
FRD rows appended to [`RTM.md`](RTM.md) "Functional (FRD/PBI)" column in this pass. **PRD↔URS seam (flag upstream to prd-writer, per feedback loop):** URS-AUD-001/002 have no PRD story — the audit path is real (BR-QUE-002/BR-CTRL-002, portal audit expectation), so FRD-AUD-001/002/003 trace directly to URS/BR IDs and the PRD should add a compliance-officer auditability story rather than this FRD papering over the gap. Also carried open: Schedule II–V verification method (blocks FRD-CTRL-004 test detail); ASSUMPTION-2/5 ratification.
