# PRD: MedRemind — RxKart Prescription Refill Reminder & Approval Module

*Author: `prd-writer` (senior product manager) · phase: requirements · 2026-07-10 · run4*
*Upstream: `brd-writer` (`02-brd.md`), `urs-writer` (`03-urs.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Scope source of truth: `brief.md`.*
*Downstream: `frd-writer`, `backlog-manager`, `solution-recon`, `ux-ui-designer`, `ai-eval`, `product-analytics`. RTM: `examples/medremind-fleet-eval/run4/RTM.md`.*
*Register id: **DOC-001** — this is the **PRD (product) section** of the merged 1-pager PRD (BRD business-goal + metrics section lives in `02-brd.md`; per doc-strategy §5 the two merge into one PM-owned doc). Kept proportionally lean.*

| Field | Value |
|---|---|
| Participants | RxKart PM (acting PO, owner), architect, 4 developers, QA (validation), Compliance/regulatory (approver). No dedicated UX designer or security engineer named (doc-strategy §10 FLAG). |
| Status | Draft |
| Target release | First shippable slice within 3 two-week sprints (~6 weeks) of build start (CON-5; ASSUMPTION-2). |
| Last updated | 2026-07-10 |

---

## FLAG & assumptions (read first)

- **FLAG(PM / acting PO):** reminder **cadence and no-response behaviour** are undefined in `brief.md` and in no upstream doc routed to me — how many times a due prescription is re-reminded, over what interval, and when reminding stops (refill requested, expired, opted out). Complete acceptance criteria for PRD-RMD-001 / PRD-RMD-002 depend on this. Logged as OQ-4; proceeding on ASSUMPTION-10. Not invented as fact.
- **FLAG(security-reviewer / compliance):** patient **consent to receive SMS and the opt-out path** (TCPA + notification-preference handling) is addressed nowhere upstream — the BRD/URS cover HIPAA PHI-minimization of *content* but not consent-to-contact. A refill-reminder SMS programme to 250k patients has a TCPA exposure independent of HIPAA. Logged as OQ-5; proceeding on ASSUMPTION-11. Owned by DOC-004 (threat model) / compliance, not by this PRD.
- **ASSUMPTION-10** *(owner: PM / acting PO)* — pending OQ-4, a due non-controlled prescription is reminded at most twice (initial + one re-reminder ~48h later); reminding stops on the first of: refill requested, prescription expired, or patient opt-out. Exact cadence is `frd-writer`'s to finalise as PBIs.
- **ASSUMPTION-11** *(owner: compliance / security-reviewer)* — pending OQ-5, patients are assumed already consented to transactional SMS under existing RxKart app terms, and an SMS opt-out (e.g. STOP keyword) is honoured. If consent is not covered by existing terms, an explicit opt-in becomes a launch-gating P0 and this PRD expands.
- **ASSUMPTION-12** *(owner: ux-ui-designer / architect)* — the patient's substitution acceptance (URS-SAF-003 / URS-DAT-003) is captured in-app as an explicit confirmation action, not by SMS reply; the exact interaction is design-downstream (`ux-ui-designer`).
- Carried unratified upstream: **ASSUMPTION-1..ASSUMPTION-9** (see `02-brd.md`, `03-urs.md`) — sponsor identity, 2-quarter window, on-time-refill definition, store-hours window, fixed Twilio/Firebase channels, non-GAMP/Part-11 scope, verification depth, DEA-schedule classification source, uniform state-board handling. Do not treat as decided.

---

## Problem statement

RxKart's 250k monthly-active patients get **no proactive prompt** when a prescription becomes due for refill — refills depend on the patient remembering, phoning, or walking in. On-time refill sits at **41%** (baseline definition unverified — OQ-2, owned by `product-analytics`). Two user pains drive that number:

1. **Patients** miss refills because nothing reaches them at the moment a refill is due, and even a motivated patient must navigate an unstructured phone/counter/voicemail path to act.
2. **Pharmacists** (40 stores) receive refill requests through fragmented channels with **no shared queue and no audit trail**, so triage is ad-hoc and controlled-substance safeguards rest on manual vigilance alone.

The fix is a proactive, one-tap, auditable refill funnel — with controlled substances deliberately kept *out* of automation and PHI kept *out* of SMS.

## Team goals and business objectives

Translated from the BRD (BR-OUTCOME-001), not copied: convert missed refills into on-time refills by closing the gap between "prescription is due" and "patient acts," while routing every patient-initiated refill into a single auditable pharmacist queue — and doing both without adding one unit of DEA/state-board or HIPAA compliance exposure. Regulatory standing is a hard launch gate, not a goal to trade against.

## Success metrics (three layers)

- **Primary:** on-time refill rate **41% → 60% within 2 quarters** of first-slice launch (BR-OUTCOME-001; ASSUMPTION-2, ASSUMPTION-3). *Measurable only once `product-analytics` resolves the baseline definition — OQ-2.*
- **Secondary:** refill-funnel conversion — reminder delivered → one-tap request submitted → pharmacist decision recorded — trending up; and a measurable drop in ad-hoc phone/counter refill intake (the queue absorbing that volume).
- **Guardrail (must NOT regress):** **zero** DEA/state-board controlled-substance violations (BR-CTRL-004) and **zero** HIPAA PHI-minimization violations in notifications (BR-PHI-002); reminder delivery ≤5 min of schedule (BR-NFR-001) and pharmacist-queue load <2 s at 500 concurrent pharmacists (BR-NFR-002) do not degrade. *NFR realization is `srs-writer`'s (CON-4); this PRD consumes them as guardrails, it does not re-author the numbers.*

## User personas

| Persona | Who they are | What they need from MedRemind |
|---|---|---|
| **Patient** (end user, 250k MAU) | Untrained consumer on the existing RxKart app; possibly low health-literacy; may read an SMS on a shared/insecure device (URS §3). | A timely, privacy-minimized nudge when a refill is due, and a way to act on it in one confirmation — without exposing what drug it is. |
| **Pharmacist** (primary operator, 40 stores) | Licensed, DEA/state-board-trained; interleaves the queue with counter/walk-in work; up to 500 concurrent chain-wide. | One place to see and decide every pending refill request, with an audit trail, and a safe lane that keeps controlled substances out of self-service. |
| **Compliance/regulatory officer** (approver) | HIPAA + DEA/state-board authority. | Confidence that no drug name leaves in an SMS and no controlled substance enters automation — evidenced, not asserted. |

## User stories (MoSCoW)

Priorities: **Must** = P0 in the first slice; **Should** = P1; **Could** = P2. Acceptance criteria are Given/When/Then. Error/empty/edge states are documented in *User flow* below and referenced per story. Every controlled-substance and PHI story is DoR-gated: it may not enter a sprint without a DOC-003 (URS) + DOC-004 (threat-model) reference (doc-strategy §8).

| # | ID | Story | Priority | Acceptance criteria (Given/When/Then) | Traces to |
|---|---|---|---|---|---|
| 1 | PRD-RMD-001 | As a patient, I want a push notification when a refillable prescription is due, so that I act without having to remember. | Must | Given an active, non-controlled prescription that reaches its refill-due date, When the scheduler runs, Then a push notification is delivered to the patient's authenticated device; the notification body carries no drug name (see PRD-PHI-001); if push delivery fails, SMS (PRD-RMD-002) is the fallback channel. | BR-REFILL-001, URS-USE-001, CON-1 |
| 2 | PRD-RMD-002 | As a patient, I want an SMS reminder when a refillable prescription is due, so that I am reached even with push disabled. | Must | Given an active, non-controlled prescription that reaches its refill-due date, When the scheduler runs, Then an SMS is sent via Twilio whose body contains no drug name or other PHI (PRD-PHI-001); a patient who has opted out (ASSUMPTION-11) is not sent SMS. | BR-REFILL-001, URS-USE-002, CON-1, CON-2 |
| 3 | PRD-RFL-001 | As a patient, I want to request a refill in one confirmation from the reminder, so that acting is effortless. | Must | Given a delivered reminder for an eligible non-controlled prescription, When the patient confirms the refill in a single action, Then a refill request is created and enters the pharmacist queue; a duplicate confirmation on an already-requested prescription creates no second request. | BR-REFILL-002, URS-USE-003 |
| 4 | PRD-QUE-001 | As a pharmacist, I want one queue of all pending refill requests, so that I triage from a single place instead of fragmented channels. | Must | Given pending refill requests across the store, When the pharmacist opens the queue, Then all pending requests are listed with the data needed to decide; an empty queue shows an explicit empty state, not an error. | BR-QUEUE-001, URS-USE-004 |
| 5 | PRD-QUE-002 | As a pharmacist, I want to approve a queued request, so that the refill proceeds to dispensing. | Must | Given a queued non-controlled request, When the pharmacist records an approve decision, Then the request leaves the pending queue and an attributable, timestamped audit entry identifying the acting pharmacist is written. | BR-QUEUE-002, URS-USE-005, URS-DAT-002 |
| 6 | PRD-QUE-003 | As a pharmacist, I want to reject a queued request with a reason, so that the patient and the audit trail know why. | Must | Given a queued request, When the pharmacist records a reject decision, Then a reject reason is required before the rejection is accepted, and an attributable, timestamped audit entry is written. | BR-QUEUE-002, URS-USE-006, URS-DAT-002 |
| 7 | PRD-SUB-001 | As a pharmacist, I want to suggest a generic substitution on a request, so that the patient can choose a lower-cost equivalent. | Should | Given a queued request, When the pharmacist attaches a suggested generic substitution, Then the suggestion is recorded against the request and surfaced to the patient for a decision (see PRD-SUB-002). | BR-SUB-001, URS-USE-007 |
| 8 | PRD-SUB-002 | As a patient, I want to accept or decline a suggested generic before it is dispensed, so that nothing is substituted without my consent. | Must | Given a pharmacist-suggested substitution, When the patient records acceptance in-app (ASSUMPTION-12), Then dispensing of the substituted item is unblocked and the acceptance is stored with a timestamp as the consent record; Given no recorded acceptance, Then the substituted item is not dispensed. | BR-SUB-002, URS-SAF-003, URS-DAT-003 |
| 9 | PRD-CTRL-001 | As a compliance officer, I want Schedule II–V prescriptions excluded from automated reminders, so that no controlled substance is ever auto-prompted. | Must | Given a prescription classified DEA Schedule II–V (per the authoritative classification source, ASSUMPTION-8), When the scheduler evaluates due prescriptions, Then no reminder is generated for it. DoR: URS + threat-model reference required. | BR-CTRL-001, URS-SAF-001 |
| 10 | PRD-CTRL-002 | As a compliance officer, I want Schedule II–V prescriptions excluded from one-tap self-service refill, so that controlled substances cannot be self-requested. | Must | Given a Schedule II–V prescription, When a patient attempts a self-service refill, Then the one-tap path is not available for it and no self-service request is created. DoR: URS + threat-model reference required. | BR-CTRL-001, URS-SAF-002 |
| 11 | PRD-CTRL-003 | As a pharmacist, I want controlled-substance refill needs routed to pharmacist-initiated contact, so that they leave automation entirely. | Must | Given a controlled-substance refill need, When it is detected, Then it is routed to a pharmacist-initiated-contact path rather than any automated fulfilment. DoR: URS + threat-model reference required. | BR-CTRL-003, URS-SAF-004 |
| 12 | PRD-CTRL-004 | As a compliance officer, I want an identity-verification step before any controlled-substance refill proceeds, so that identity is confirmed on the manual path. | Must | Given a controlled-substance refill on the pharmacist-initiated path, When it is about to proceed, Then it proceeds only after a successful identity-verification step (mechanism owned by DOC-004, ASSUMPTION-8). DoR: URS + threat-model + security review required. | BR-CTRL-002, URS-SEC-001 |
| 13 | PRD-PHI-001 | As a compliance officer, I want no drug name or PHI in any SMS body, so that a reminder read on a shared device leaks nothing. | Must | Given any outbound SMS reminder, When it is composed, Then its body contains no drug name and no other PHI; the patient learns *which* prescription only inside the authenticated app. DoR: URS + threat-model reference required. | BR-PHI-001, BR-PHI-002, URS-DAT-001, CON-2 |

*NFRs (reminder ≤5 min, queue <2 s @ 500 concurrent, 99.9% store-hours availability — BR-NFR-001, BR-NFR-002, BR-NFR-003 / CON-4) are consumed as guardrail metrics above and realized by `srs-writer`; this PRD does not re-mint them as product IDs.*

## User flow

**Happy path.** Prescription reaches its refill-due date → scheduler sends push (PRD-RMD-001) and/or SMS (PRD-RMD-002), content PHI-minimized → patient opens the app, sees which prescription is due, confirms refill in one action (PRD-RFL-001) → request lands in the pharmacist queue (PRD-QUE-001) → pharmacist approves (PRD-QUE-002) → refill proceeds to the existing dispensing workflow. Optional branch: pharmacist suggests a generic (PRD-SUB-001) → patient accepts in-app (PRD-SUB-002) → substituted item unblocked for dispensing.

**Controlled-substance path (never automated).** A due Schedule II–V prescription is excluded from reminders (PRD-CTRL-001) and from one-tap (PRD-CTRL-002); the need is routed to pharmacist-initiated contact (PRD-CTRL-003) and proceeds only after identity verification (PRD-CTRL-004).

**Error / edge / empty states (the unhappy path — where products break):**
- **Push delivery fails** → SMS is the fallback (PRD-RMD-001). Both fail → the reminder is retried within the ≤5-min SLA window (BR-NFR-001, realized by `srs-writer`); repeated failure surfaces to ops (SRE, per doc-strategy §8).
- **SMS opt-out / no consent** → no SMS is sent (ASSUMPTION-11, OQ-5); push and in-app remain.
- **Duplicate one-tap confirmation** → idempotent; no second queue request (PRD-RFL-001).
- **Empty queue** → explicit empty state, not an error (PRD-QUE-001).
- **Reject without reason** → blocked; reason is mandatory (PRD-QUE-003).
- **Substitution never accepted / declined** → substituted item is not dispensed; the original prescription remains the dispensing basis (PRD-SUB-002).
- **Prescription expires or is cancelled mid-flow** → no reminder is sent and any pending request is voided (feeds ASSUMPTION-10 cadence rules).
- **Misclassified schedule** → the exclusion is only as trustworthy as the DEA-schedule source (ASSUMPTION-8, URS §10 FLAG); a classification gap is a safety-critical defect, not a UX nit.

## User interaction and design

No wireframes exist yet — `ux-ui-designer` (downstream) owns the reminder surface, the one-tap confirmation, the queue layout, and the in-app substitution-acceptance interaction (ASSUMPTION-12). Design constraints this PRD hands down: the SMS surface must never reveal the drug (PRD-PHI-001); the one-tap action must be a single deliberate confirmation, not an accidental tap (PRD-RFL-001); the queue must remain usable while a pharmacist interleaves counter work. This section stays intentionally open for design judgement.

## Decisions log

| Date | Decision | Reasoning | Trade-off accepted |
|---|---|---|---|
| 2026-07-10 | This PRD mints only product stories (PRD-*); NFRs stay `srs-writer`'s (CON-4). | Single source of truth per doc-strategy — avoids two owners for one number. | PRD readers must follow the RTM to the RFC for the NFR targets. |
| 2026-07-10 | Generic substitution (PRD-SUB-001) is **Should**, not Must, for the first slice. | The 41%→60% outcome is driven by the reminder→one-tap→approve funnel; substitution is value-add, not the lever. Substitution *safety* (PRD-SUB-002) stays **Must** wherever substitution ships. | First slice may ship approve/reject without pharmacist-suggested substitution if the 6-week clock demands it. |
| 2026-07-10 | Reminder cadence deferred to `frd-writer` under ASSUMPTION-10 rather than fixed here. | Cadence is functional detail (PBI altitude), not product intent; over-specifying it would box in engineering. | Acceptance criteria for PRD-RMD-001/002 remain provisional until OQ-4 closes. |

## Open questions

| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| OQ-4: What is the reminder cadence and stop condition (re-reminder count, interval, when reminding ends)? | PM / acting PO (feeds `frd-writer`) | Pending — on ASSUMPTION-10 | — |
| OQ-5: Is patient consent to transactional SMS covered by existing terms, and what is the opt-out mechanism (TCPA)? | Compliance / `security-reviewer` | Pending — on ASSUMPTION-11; could become a launch-gating opt-in P0 | — |
| OQ-6: In-app substitution-acceptance interaction — confirmation model and channel? | `ux-ui-designer` / architect | Pending — on ASSUMPTION-12 | — |
| OQ-2 (carried): baseline definition for the 41% on-time-refill metric. | `product-analytics` / PM | Pending — blocks Primary-metric evidence | — |

## What we're not doing (MoSCoW Won't-Have, this release)

- **Payment / copay collection** — refill payment rides existing pharmacy adjudication (BRD scope).
- **Delivery / courier logistics** — dispensing and pickup stay in the existing store workflow.
- **Net-new app or portal** — MedRemind is a brownfield module on existing surfaces (doc-strategy §1).
- **Channel choice** — Twilio (SMS) + Firebase (push) are fixed (ASSUMPTION-5).
- **Clinical decision support / drug-interaction checking** — beyond a refill reminder; deferred.
- **Controlled-substance automation of any kind** — a permanent Won't, not a deferral (BR-CTRL-*).
- **Full FDA 21 CFR Part 11 / GAMP validation** — out of scope (ASSUMPTION-6); revisit only if that ruling flips (URS §10 FLAG).

## Handoff

- `frd-writer` — turn the hard flows (controlled-substance gating PRD-CTRL-001..PRD-CTRL-004 as atomic stories, substitution-acceptance PRD-SUB-002, reminder cadence per ASSUMPTION-10/OQ-4) into exact behaviour before they become PBIs.
- `backlog-manager` — break these product stories into ranked, AC-bearing PBIs on Azure Boards (DOC-007); every controlled-substance/PHI PBI is DoR-gated on a URS + threat-model reference.
- `solution-recon` / `ux-ui-designer` — feasibility on existing surfaces; design the reminder, one-tap, queue, and substitution-acceptance interactions.
- `product-analytics` — instrument the funnel and resolve the 41% baseline (OQ-2) so the Primary metric is measurable.
- `ai-eval` — n/a for this release (no model surface); noted for completeness.
