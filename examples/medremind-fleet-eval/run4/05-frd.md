# FRD: MedRemind — Functional Behaviour of the Hard Flows (→ Azure Boards PBIs)

*Author: `frd-writer` (business analyst / functional spec) · phase: requirements · 2026-07-10 · run4*
*Upstream: `prd-writer` (`04-prd.md`), `urs-writer` (`03-urs.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Scope source of truth: `brief.md`.*
*Downstream: `backlog-manager` (DOC-007 PBIs), `srs-writer`, `test-plan-writer`, `ux-ui-designer`, `solution-recon`, `product-analytics`, `architect`, `sdd-writer`. RTM: `examples/medremind-fleet-eval/run4/RTM.md`.*
*Register id: **DOC-007** — per doc-strategy §5 the standalone FRD is **dropped as a document**; functional behaviour lives as Azure Boards PBIs. This file is the `frd-writer` pass over the **hard flows only** (controlled-substance gating, substitution-acceptance-before-dispensing, reminder cadence, PHI minimisation) that must be pinned to deterministic behaviour before `backlog-manager` structures the board. Kept proportionally lean per the 6-week clock (CON-5).*

| Field | Value |
|---|---|
| Author | `frd-writer` |
| Status | Draft |
| Related PRD | `04-prd.md` (PRD-RMD-001..PRD-PHI-001 — see per-requirement Source column) |
| Related URS | `03-urs.md` (safety / privacy overlay, DOC-003) |
| Last updated | 2026-07-10 |

---

## FLAG & assumptions (read first)

- **FLAG(ux-ui-designer / compliance):** the **time-of-day send window** for reminders is undefined in `brief.md`, the PRD, and the URS. Cadence *count/interval* was handed to me (ASSUMPTION-10, OQ-4), but *when in the day* a reminder may fire is a separate obligation — an SMS at 03:00 is a patient-experience and TCPA-adjacent problem independent of the ≤5-min SLA. No upstream doc owns it. Logged as **OQ-7**; proceeding on **ASSUMPTION-13**. Not invented as ratified fact; owned by `ux-ui-designer` (interaction) with compliance sign-off.
- **FLAG(security-reviewer / compliance):** FRD-CTRL-005 introduces a **fail-closed** default — a prescription whose DEA-schedule classification is *absent/unresolved* is gated **as if controlled**. This is a safety decision, not a functional detail, and it hardens the ASSUMPTION-8 dependency (the exclusion is only as trustworthy as the classification source — URS §10 FLAG). It needs explicit compliance ratification. Logged as **ASSUMPTION-14**; owned by `security-reviewer` / compliance, realised against the DOC-004 classification field. Do not treat as decided.
- **FLAG(security-reviewer):** the **identity-verification mechanism** behind FRD-CTRL-004 is owned by the threat model (DOC-004, ASSUMPTION-8), not by this FRD. I specify only the *behavioural gate* ("proceeds only after a successful verification is recorded"); the mechanism must be confirmed in DOC-004 before PBI-CTRL-003 clears DoR.
- **ASSUMPTION-10** *(owner: PM / acting PO; carried from PRD, pending OQ-4)* — a due non-controlled prescription is reminded at most twice (initial + one re-reminder). I operationalise this in FRD-RMD-001..FRD-RMD-006. If OQ-4 closes with a different cadence, those rows and PBI-RMD-001 change; the IDs do not.
- **ASSUMPTION-13** *(owner: `ux-ui-designer` / compliance; new, pending OQ-7)* — reminders (push + SMS) are dispatched only within a patient-local daytime window **08:00–20:00**; a reminder whose due moment falls outside the window is held to the next window open, with the ≤5-min delivery SLA (BR-NFR-001, `srs-writer`) measured from window open rather than from the raw due moment.
- **ASSUMPTION-14** *(owner: `security-reviewer` / compliance; new)* — a prescription with an absent/unresolved DEA-schedule classification is treated as controlled (fail-closed) for all gating (FRD-CTRL-005). See FLAG above.
- Carried unratified upstream: **ASSUMPTION-1..ASSUMPTION-12** (see `02-brd.md`, `03-urs.md`, `04-prd.md`) — including SMS consent/opt-out (ASSUMPTION-11) and in-app substitution acceptance (ASSUMPTION-12), on which FRD-RMD-006 and FRD-SUB-002..FRD-SUB-004 respectively depend. Do not treat as decided.

---

## Overview

Deterministic behaviour for the four flows the PRD/doc-strategy singled out as *hard*: (1) reminder scheduling and cadence, (2) the one-tap refill request and its idempotency, (3) the pharmacist queue with approve/reject/substitution and its audit + consent gates, and (4) the two hard-launch guardrails — controlled-substance exclusion and SMS/push PHI minimisation. Each functional requirement is written as a singular "the system shall …", carries Given/When/Then acceptance criteria QA can turn into a test case, and traces to a PRD story and (where regulated) a URS requirement. Architecture, APIs, and data model are **out of scope here** — they belong to the RFC (DOC-002, `srs-writer`/`sdd-writer`).

## Actors & preconditions

- **Patient** — RxKart account holder authenticated via the existing app login (URS §3). Precondition for any reminder: an existing, active, **non-controlled** prescription at or past its refill-due date.
- **Pharmacist** — licensed operator on the existing back-office portal; acts on the store's refill-request queue.
- **Scheduler** — the system actor that evaluates due prescriptions and dispatches reminders (behaviour only; realisation owned by the RFC).
- **Compliance officer** — approver of the PHI-minimisation and controlled-substance behaviour; does not operate the runtime flow.

---

## Functional requirements

### 1 · Reminder scheduling & cadence (PRD-RMD-001, PRD-RMD-002; ASSUMPTION-10, ASSUMPTION-13)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-RMD-001 | The system shall send one initial refill reminder when a refillable non-controlled prescription reaches its refill-due date. | Given an active non-controlled prescription at its refill-due date, When the scheduler runs inside the send window (ASSUMPTION-13), Then exactly one initial reminder is dispatched on the patient's enabled channels. | PRD-RMD-001, PRD-RMD-002, URS-USE-001, URS-USE-002 |
| FRD-RMD-002 | The system shall send exactly one re-reminder 48 hours after the initial reminder when no refill request exists for that prescription. | Given an initial reminder sent 48h ago with no refill request created since, When the scheduler next runs inside the send window, Then exactly one re-reminder is dispatched. | PRD-RMD-001, ASSUMPTION-10 |
| FRD-RMD-003 | The system shall send no more than two reminders per refill-due cycle for a prescription. | Given an initial reminder plus one re-reminder already dispatched, When the scheduler runs again for the same due cycle, Then no further reminder is dispatched. | ASSUMPTION-10 |
| FRD-RMD-004 | The system shall stop further reminders for a prescription once a refill request exists for it. | Given a prescription with an open refill request, When the scheduler evaluates it, Then no reminder (initial or re-reminder) is dispatched. | PRD-RFL-001, ASSUMPTION-10 |
| FRD-RMD-005 | The system shall stop reminders for a prescription that is no longer active. | Given a prescription that has expired or been cancelled, When the scheduler evaluates it, Then no reminder is dispatched and any un-dispatched re-reminder is cancelled. | PRD-RMD-001 (edge), ASSUMPTION-10 |
| FRD-RMD-006 | The system shall suppress SMS reminders to a patient who has recorded an SMS opt-out. | Given a patient with a recorded SMS opt-out (ASSUMPTION-11), When a reminder is dispatched, Then no SMS is sent to that patient; push (if enabled) is unaffected. | PRD-RMD-002, ASSUMPTION-11 |
| FRD-RMD-007 | The system shall attempt an SMS reminder when push delivery of that reminder reports failure. | Given a reminder whose push delivery reports failure, When the failure is observed, Then an SMS reminder is attempted as fallback (subject to FRD-RMD-006). | PRD-RMD-001 |
| FRD-RMD-008 | The system shall record a delivery-failure event for operations when a reminder cannot be delivered on any channel. | Given a reminder for which every enabled channel reports failure, When retries within the SLA window are exhausted, Then a delivery-failure event is recorded for ops (SRE). | PRD-RMD-001 (edge), BR-NFR-001 |

*Retry counts and the ≤5-min SLA arithmetic are NFR realisation — owned by `srs-writer` (CON-4); FRD-RMD-008 states only the observable end-of-window behaviour.*

### 2 · One-tap refill request (PRD-RFL-001)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-RFL-001 | The system shall create a refill request when the patient confirms a refill in a single in-app action. | Given a delivered reminder for an eligible non-controlled prescription, When the patient completes the single confirmation action, Then one refill request is created and enters the pharmacist queue. | PRD-RFL-001, URS-USE-003 |
| FRD-RFL-002 | The system shall reject a repeat confirmation on a prescription that already has an open refill request. | Given a prescription with an open refill request, When the patient confirms a refill again, Then no second request is created and the existing request's status is shown. | PRD-RFL-001 |
| FRD-RFL-003 | The system shall withhold the one-tap refill action for a prescription that is no longer active. | Given a prescription that has expired or been cancelled, When the patient views it, Then the one-tap refill action is not offered. | PRD-RFL-001 (edge) |

### 3 · Pharmacist queue, decisions & audit (PRD-QUE-001, PRD-QUE-002, PRD-QUE-003)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-QUE-001 | The system shall list every pending refill request for the pharmacist's store in one queue. | Given pending requests across the store, When the pharmacist opens the queue, Then all pending requests are listed with the data needed to decide. | PRD-QUE-001, URS-USE-004 |
| FRD-QUE-002 | The system shall present an explicit empty state when the store's pending queue contains no requests. | Given no pending requests, When the pharmacist opens the queue, Then an explicit empty state is shown, not an error. | PRD-QUE-001 (edge), URS-USE-004 |
| FRD-QUE-003 | The system shall remove a request from the pending queue when a pharmacist records an approve decision on it. | Given a queued non-controlled request, When the pharmacist records an approve decision, Then the request leaves the pending queue. | PRD-QUE-002, URS-USE-005 |
| FRD-QUE-004 | The system shall write an attributable, timestamped audit entry identifying the acting pharmacist on each approve decision. | Given an approve decision is recorded, When it is committed, Then an audit entry naming the acting pharmacist with a timestamp is written. | PRD-QUE-002, URS-USE-005, URS-DAT-002 |
| FRD-QUE-005 | The system shall require a non-empty reject reason before it accepts a reject decision. | Given a reject decision with no reason entered, When the pharmacist submits it, Then the rejection is blocked until a reason is supplied. | PRD-QUE-003, URS-USE-006 |
| FRD-QUE-006 | The system shall write an attributable, timestamped audit entry identifying the acting pharmacist on each reject decision. | Given a reject decision (with reason) is recorded, When it is committed, Then an audit entry naming the acting pharmacist with a timestamp is written. | PRD-QUE-003, URS-USE-006, URS-DAT-002 |
| FRD-QUE-007 | The system shall accept only the first decision recorded against a given refill request. | Given two pharmacists open the same request, When both submit a decision, Then the first committed decision stands, the second is rejected as already-decided, and no duplicate audit entry is written. | PRD-QUE-002 (concurrency edge), URS-DAT-002 |

### 4 · Generic substitution & consent gate (PRD-SUB-001, PRD-SUB-002)

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-SUB-001 | The system shall let a pharmacist attach one suggested generic substitution to a queued request. | Given a queued request, When the pharmacist attaches a suggested generic, Then the suggestion is recorded against that request. | PRD-SUB-001, URS-USE-007 |
| FRD-SUB-002 | The system shall surface a pharmacist-suggested substitution to the patient for an explicit decision. | Given a recorded substitution suggestion, When the patient opens the request in-app (ASSUMPTION-12), Then the suggestion is presented with accept / decline actions. | PRD-SUB-002, URS-SAF-003 |
| FRD-SUB-003 | The system shall block dispensing of a substituted item until the patient records explicit acceptance. | Given a suggested substitution with no recorded patient acceptance, When dispensing is attempted for the substituted item, Then dispensing is blocked. | PRD-SUB-002, URS-SAF-003 |
| FRD-SUB-004 | The system shall record a patient's substitution acceptance with a timestamp as the consent record. | Given the patient accepts the substitution in-app, When acceptance is committed, Then it is stored with a timestamp as the dispensing consent record. | PRD-SUB-002, URS-DAT-003 |
| FRD-SUB-005 | The system shall keep the originally prescribed item as the dispensing basis when no substitution acceptance is recorded. | Given a patient who declines or does not respond to a suggested substitution, When dispensing proceeds, Then the original prescribed item remains the basis and the substituted item stays blocked. | PRD-SUB-002 (edge), URS-SAF-003 |

### 5 · Controlled-substance gating (PRD-CTRL-001, PRD-CTRL-002, PRD-CTRL-003, PRD-CTRL-004) — safety-critical

*DoR: every requirement in this block requires a URS + threat-model (DOC-004) reference before its PBI enters a sprint (doc-strategy §8).*

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-CTRL-001 | The system shall exclude a prescription classified DEA Schedule II–V from automated reminder generation. | Given a prescription classified Schedule II–V (ASSUMPTION-8), When the scheduler evaluates due prescriptions, Then no reminder is generated for it. | PRD-CTRL-001, URS-SAF-001 |
| FRD-CTRL-002 | The system shall withhold the one-tap self-service refill action for a prescription classified DEA Schedule II–V. | Given a Schedule II–V prescription, When the patient views it, Then the one-tap refill action is not available and no self-service request can be created. | PRD-CTRL-002, URS-SAF-002 |
| FRD-CTRL-003 | The system shall route a detected controlled-substance refill need to the pharmacist-initiated-contact path. | Given a controlled-substance refill need is detected, When it is triaged, Then it is placed on the pharmacist-initiated-contact path, not any automated fulfilment path. | PRD-CTRL-003, URS-SAF-004 |
| FRD-CTRL-004 | The system shall block a controlled-substance refill on the manual path until a successful identity-verification step is recorded. | Given a controlled-substance refill on the pharmacist-initiated path, When it is about to proceed, Then it proceeds only after a successful identity verification is recorded (mechanism per DOC-004, ASSUMPTION-8). | PRD-CTRL-004, URS-SEC-001 |
| FRD-CTRL-005 | The system shall treat a prescription whose DEA-schedule classification is absent as controlled for all gating purposes. | Given a prescription with a missing/unresolved schedule classification, When the scheduler or one-tap path evaluates it, Then it is gated as if Schedule II–V (no reminder, no one-tap) until the classification resolves. | PRD-CTRL-001 (fail-safe), URS-SAF-001, ASSUMPTION-14 |

### 6 · PHI minimisation in notifications (PRD-PHI-001) — hard guardrail

*DoR: URS + threat-model reference required (doc-strategy §8).*

| ID | Requirement ("the system shall …") | Acceptance criteria (Given / When / Then) | Source |
|---|---|---|---|
| FRD-PHI-001 | The system shall compose every outbound SMS body without any drug name. | Given any outbound SMS reminder, When it is composed, Then its body contains no drug name. | PRD-PHI-001, URS-DAT-001 |
| FRD-PHI-002 | The system shall compose every outbound SMS body without other protected health information. | Given any outbound SMS reminder, When it is composed, Then its body contains no PHI beyond the fact that a generic refill is due. | PRD-PHI-001, URS-DAT-001 |
| FRD-PHI-003 | The system shall reveal which prescription is due only inside the authenticated app. | Given a due prescription, When the patient wants to know which one, Then that detail is shown only after in-app authentication, never in the SMS. | PRD-PHI-001, URS-DAT-001 |
| FRD-PHI-004 | The system shall compose every push notification body without any drug name. | Given any outbound push reminder, When it is composed, Then its body (including any lock-screen preview) contains no drug name. | PRD-RMD-001, PRD-PHI-001 |

---

## Seeded PBIs (DOC-007 — for `backlog-manager` to rank on Azure Boards)

Ranked, INVEST-checked, acceptance-criteria-bearing decomposition of the hard flows. `backlog-manager` owns the full board (including the non-hard reminder/queue plumbing) and final ranking/estimates; these are the seed for the flows `frd-writer` was asked to pin. **No phantom PBIs** — every PBI referenced in this file or the RTM has its defining row here. Points are rough seeds (`backlog-manager` re-estimates with `estimation-facilitator`).

| PBI | Story | Acceptance criteria (Given / When / Then) | Traces (FRD) | Rank | Pts | DoR gate |
|---|---|---|---|---|---|---|
| `PBI-CTRL-001` | As a compliance officer, I want Schedule II–V prescriptions excluded from automated reminders so no controlled substance is auto-prompted. | Given a Schedule II–V prescription, When the scheduler runs, Then no reminder is generated. | FRD-CTRL-001 · FRD-CTRL-005 · URS-SAF-001 | 1 | 5 | URS + threat-model (DOC-004) |
| `PBI-CTRL-002` | As a compliance officer, I want Schedule II–V prescriptions excluded from one-tap self-service so they cannot be self-requested. | Given a Schedule II–V prescription, When the patient views it, Then the one-tap action is unavailable and no self-service request is created. | FRD-CTRL-002 · FRD-CTRL-005 · URS-SAF-002 | 2 | 3 | URS + threat-model (DOC-004) |
| `PBI-CTRL-003` | As a compliance officer, I want controlled-substance refills routed to a verified pharmacist-initiated path so identity is confirmed off automation. | Given a controlled-substance refill need, When detected, Then it is routed to pharmacist-initiated contact; When it is about to proceed, Then a successful identity verification is required first. | FRD-CTRL-003 · FRD-CTRL-004 · URS-SAF-004 · URS-SEC-001 | 3 | 8 | URS + threat-model + security review (DOC-004) |
| `PBI-PHI-001` | As a compliance officer, I want no drug name or PHI in any SMS/push body so a reminder on a shared device leaks nothing. | Given any outbound SMS or push reminder, When composed, Then the body carries no drug name and no other PHI; Then the drug is revealed only in the authenticated app. | FRD-PHI-001 · FRD-PHI-002 · FRD-PHI-003 · FRD-PHI-004 · URS-DAT-001 | 4 | 5 | URS + threat-model (DOC-004) |
| `PBI-RMD-001` | As a patient, I want a timely refill reminder with a sane cadence so I act without being spammed. | Given a due non-controlled prescription, When the scheduler runs in the send window, Then one initial reminder fires; When 48h pass with no request, Then one re-reminder fires; When a request exists or the Rx is inactive, Then reminders stop. | FRD-RMD-001 · FRD-RMD-002 · FRD-RMD-003 · FRD-RMD-004 · FRD-RMD-005 · FRD-RMD-006 | 5 | 8 | RFC (DOC-002) reminder-scheduler section |
| `PBI-RMD-002` | As a patient, I want the reminder to reach me even if push fails so I am not missed. | Given a reminder whose push delivery fails, When the failure is observed, Then an SMS fallback is attempted; When every channel fails, Then a delivery-failure event is recorded for ops. | FRD-RMD-007 · FRD-RMD-008 | 8 | 3 | RFC (DOC-002) |
| `PBI-RFL-001` | As a patient, I want to request a refill in one confirmation so acting is effortless, without creating duplicates. | Given a delivered reminder for an eligible Rx, When I confirm once, Then one request enters the queue; When I confirm again, Then no second request is created. | FRD-RFL-001 · FRD-RFL-002 · FRD-RFL-003 · URS-USE-003 | 6 | 5 | RFC (DOC-002) |
| `PBI-QUE-001` | As a pharmacist, I want one queue of pending requests so I triage from one place, with a clear empty state. | Given pending requests, When I open the queue, Then all are listed; Given none, When I open it, Then an explicit empty state shows, not an error. | FRD-QUE-001 · FRD-QUE-002 · URS-USE-004 | 7 | 5 | RFC (DOC-002) |
| `PBI-QUE-002` | As a pharmacist, I want to approve or reject a request with an audited, reasoned decision so the trail is complete. | Given a queued request, When I approve, Then it leaves the queue with an attributable timestamped audit entry; When I reject, Then a reason is required before an equally-audited rejection is accepted. | FRD-QUE-003 · FRD-QUE-004 · FRD-QUE-005 · FRD-QUE-006 · URS-USE-005 · URS-USE-006 · URS-DAT-002 | 9 | 8 | RFC (DOC-002) + URS |
| `PBI-QUE-003` | As a pharmacist, I want concurrent decisions on one request handled safely so two of us cannot double-decide. | Given two pharmacists on the same request, When both submit, Then only the first committed decision stands and no duplicate audit entry is written. | FRD-QUE-007 · URS-DAT-002 | 11 | 3 | RFC (DOC-002) |
| `PBI-SUB-001` | As a pharmacist, I want to suggest a generic on a request so the patient can choose a lower-cost equivalent. | Given a queued request, When I attach a suggested generic, Then it is recorded and surfaced to the patient for a decision. | FRD-SUB-001 · FRD-SUB-002 · URS-USE-007 | 12 | 3 | RFC (DOC-002) |
| `PBI-SUB-002` | As a patient, I want to accept or decline a suggested generic before it is dispensed so nothing is substituted without consent. | Given a suggested substitution, When I accept in-app, Then a timestamped consent record unblocks dispensing; Given no acceptance, Then the substituted item stays blocked and the original remains the basis. | FRD-SUB-003 · FRD-SUB-004 · FRD-SUB-005 · URS-SAF-003 · URS-DAT-003 | 10 | 5 | RFC (DOC-002) + URS |

**Pull order (value / risk / dependency).** The three controlled-substance guardrails (`PBI-CTRL-001`, `PBI-CTRL-002`, `PBI-CTRL-003`) and PHI minimisation (`PBI-PHI-001`) rank first — they are hard launch gates; a leak is a DEA/HIPAA violation, not a missed feature. The funnel core follows: `PBI-RMD-001` → `PBI-RFL-001` → `PBI-QUE-001` → `PBI-RMD-002`. Substitution safety (`PBI-SUB-002`) outranks the substitution feature (`PBI-SUB-001`) — the consent gate must exist wherever substitution ships (PRD Decisions log). `PBI-QUE-002`/`PBI-QUE-003` complete the audited decision path. `backlog-manager` finalises ranking against sprint capacity (CON-5: 3 sprints).

---

## Business rules

- **Cadence.** At most two reminders per refill-due cycle: initial, then one re-reminder at +48h if no request exists (FRD-RMD-001..FRD-RMD-003; ASSUMPTION-10). Reminding stops on the first of: refill requested (FRD-RMD-004), prescription inactive (FRD-RMD-005), or SMS opt-out for the SMS channel only (FRD-RMD-006).
- **Send window.** Reminders dispatch only 08:00–20:00 patient-local; out-of-window due events are held to next window open (ASSUMPTION-13; OQ-7 — needs ux-ui/compliance ratification).
- **Idempotency.** One open refill request per prescription; repeat confirmation is a no-op (FRD-RFL-002).
- **Reject reason mandatory.** No rejection is accepted without a non-empty reason (FRD-QUE-005).
- **Consent-before-dispensing.** A substituted item is never dispensed without a recorded patient acceptance; the original prescription is the fallback basis (FRD-SUB-003..FRD-SUB-005).
- **Controlled-substance hard exclusion, fail-closed.** Schedule II–V is excluded from all automation; an unclassified prescription is treated as controlled until classified (FRD-CTRL-001..FRD-CTRL-005; ASSUMPTION-8, ASSUMPTION-14).
- **PHI floor.** No drug name / PHI in any SMS or push body; the drug is revealed only in-app (FRD-PHI-001..FRD-PHI-004).

## Edge cases & error handling

| Scenario | Expected system response | Requirement |
|---|---|---|
| Push delivery fails | Attempt SMS fallback (subject to opt-out) | FRD-RMD-007 |
| All channels fail | Record delivery-failure event for ops after SLA-window retries | FRD-RMD-008 |
| SMS opt-out / no consent | Suppress SMS; push + in-app unaffected | FRD-RMD-006 |
| Duplicate one-tap confirmation | Idempotent — no second request | FRD-RFL-002 |
| Prescription expires / cancelled mid-flow | Stop reminders, cancel un-dispatched re-reminder, withhold one-tap | FRD-RMD-005, FRD-RFL-003 |
| Empty pharmacist queue | Explicit empty state, not an error | FRD-QUE-002 |
| Reject without reason | Blocked until a reason is supplied | FRD-QUE-005 |
| Two pharmacists decide the same request | First committed decision wins; second rejected as already-decided | FRD-QUE-007 |
| Substitution never accepted / declined | Substituted item stays blocked; original is the dispensing basis | FRD-SUB-005 |
| Missing / unresolved DEA-schedule classification | Treated as controlled (fail-closed) until resolved | FRD-CTRL-005 |
| Reminder due outside send window | Held to next window open | ASSUMPTION-13 (OQ-7) |

## Feedback loop (flagged back upstream)

- To **`prd-writer`** — cadence (ASSUMPTION-10/OQ-4) is now operationalised as FRD-RMD-001..FRD-RMD-006; the **send-window** gap (OQ-7) is genuinely un-owned upstream and needs a home (proposed: `ux-ui-designer` + compliance).
- To **`security-reviewer` / compliance** — ratify the fail-closed default (ASSUMPTION-14) and confirm the DOC-004 identity-verification mechanism (ASSUMPTION-8) before PBI-CTRL-001/002/003 clear DoR.

## Traceability

Full FRD ↔ PRD/URS ↔ PBI mapping is appended to `RTM.md` (the *Functional (FRD/PBI)* column). Design-spec and test-case columns are filled downstream by `srs-writer`/`sdd-writer` and `test-plan-writer`.
