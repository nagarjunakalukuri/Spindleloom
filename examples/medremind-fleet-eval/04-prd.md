# PRD: MedRemind — Prescription Refill Reminder & Approval Module

| Field | Value |
|---|---|
| Participants | PM/acting PO (owner), architect, 4 devs, QA, compliance officer (ASSUMPTION-3) |
| Status | Draft |
| Target release | First shippable slice in 3 sprints (~6 weeks); full module within 2 quarters |
| Last updated | 2026-07-09 |

## Problem statement
59% of RxKart refills are late or missed (on-time rate 41%). Patients must remember refill dates unaided and then phone or visit a store; pharmacists field these requests ad hoc with no shared queue. Late refills hurt patient adherence and prescription revenue across 40 stores and 250k monthly app patients — on channels RxKart already owns.

## Team goals and business objectives
Move patients from "remember and phone" to "get nudged and tap once", and give pharmacists one safe place to decide requests. This serves the BRD goals: on-time refill rate 41%→60% within 2 quarters, a shippable slice in 3 sprints, and zero reportable HIPAA/controlled-substance violations from this module.

## Success metrics (traced to BRD goals)
- **Primary:** on-time refill rate 41% → 60% within 2 quarters of launch (BR goal "On-time refill 41%→60%"; measurement definition pends ASSUMPTION-2 ratification).
- **Secondary:** ≥50% of due, non-controlled refills are requested via one-tap within 30 days of reminder rollout (ASSUMPTION-11: target value invented — owner: PM).
- **Guardrail:** zero reportable HIPAA/controlled-substance violations attributable to the module (BR goal "Zero compliance violations"), and reminder opt-out rate stays below 5% of reminded patients (ASSUMPTION-12: threshold invented — owner: PM; mitigates BRD "reminder fatigue" risk).

## Assumptions
Carried forward from upstream (tags per BEST-PRACTICES practice 8; not re-invented):
- ASSUMPTION-2 (BRD): "on-time refill" = dispensed on/before due date — owner: PM/RxKart. Blocks final metric wording.
- ASSUMPTION-5 (BRD): SMS/push consent captured or obtainable in-app — owner: compliance. Blocks PRD-REM-001 sprint commitment.
- ASSUMPTION-6 (BRD): due-date and schedule-classification data exists and is reliable — owner: architect (verify in recon).
- ASSUMPTION-7/8/9/10 (per handoff log; the URS itself was not routed to this agent): queue scoped per store; per-channel opt-out; unknown schedule fails closed as controlled; minimized reminder content = generic prompt + pharmacy name + app link.
New in this PRD: ASSUMPTION-11, ASSUMPTION-12 (see Success metrics); ASSUMPTION-13: rejected/expired requests notify the patient with a next-step prompt ("contact your pharmacy") — owner: PM.

## User personas
- **Maria, 68, chronic-care patient:** five recurring prescriptions, forgets due dates, will tap a notification but won't navigate menus.
- **Dev, store pharmacist:** dispenses under time pressure; needs a queue that is faster than today's phone calls, never a compliance trap.

## User stories (MoSCoW)
| ID | Story | Priority | Acceptance criteria | Notes |
|---|---|---|---|---|
| PRD-REM-001 | As a patient, I want a push + SMS reminder when a prescription is due, so that I refill on time. | Must | Given a non-controlled prescription reaching its due date and a consented patient, when the reminder is triggered, then the patient receives push and SMS, and the SMS contains no drug name. | BR-REM-001, BR-PHI-001; content per ASSUMPTION-10 |
| PRD-REF-001 | As a patient, I want to request the refill in one tap from the reminder, so that I don't have to phone the store. | Must | Given a received reminder, when the patient taps "Request refill", then a request is created in the pharmacist queue and the patient sees confirmation with the fulfilling store. | BR-REF-001 |
| PRD-QUE-001 | As a pharmacist, I want all pending refill requests in one portal queue, so that nothing is handled ad hoc. | Must | Given pending requests for my store, when I open the queue, then I see each request with patient, medication, and request time, ordered oldest-first. | BR-QUE-001; store scope per ASSUMPTION-7 |
| PRD-QUE-002 | As a pharmacist, I want to approve or reject each request, so that dispensing stays under my control. | Must | Given a pending request, when I approve or reject it, then its status updates, it leaves the pending queue, and the patient is notified of the outcome without drug names in SMS. | BR-QUE-002, BR-PHI-001 |
| PRD-SUB-001 | As a pharmacist, I want to suggest a generic substitution on a request, so that patients get cheaper equivalents. | Should | Given a pending request with a generic available, when I propose the substitution, then the patient receives an in-app accept/decline prompt and the request is held pending their answer. | BR-SUB-001 |
| PRD-SUB-002 | As a patient, I want dispensing blocked until I accept a proposed substitution, so that I'm never given a swap I didn't agree to. | Must | Given a proposed substitution, when the patient has not accepted it, then the request cannot be marked approved-for-dispensing; when the patient declines, then the request reverts to the pharmacist with the original medication. | BR-SUB-002 |
| PRD-CTRL-001 | As a compliance officer, I want Schedule II–V prescriptions excluded from auto-reminders and one-tap refill, so that DEA/state rules are never breached by automation. | Must | Given a prescription classified Schedule II–V — or with unknown classification (fails closed, ASSUMPTION-9) — when its due date arrives, then no reminder is sent and one-tap refill is unavailable. | BR-CTRL-001 |
| PRD-CTRL-002 | As a pharmacist, I want an extra identity-verification step on controlled-substance refills, so that dispensing is defensible. | Must | Given a controlled-substance refill in progress, when verification has not been completed and recorded, then the refill cannot proceed to dispensing. | BR-CTRL-002; method is an open question — not invented here |
| PRD-CTRL-003 | As a pharmacist, I want controlled-substance contact to be initiated by me, so that the system never solicits a controlled refill. | Must | Given a controlled-substance prescription due, when the system processes it, then no patient-facing prompt is generated; contact options appear only in the pharmacist portal. | BR-CTRL-003 |
| PRD-PHI-001 | As a compliance officer, I want every notification PHI-minimized, so that a lost phone or SMS preview never exposes health data. | Must | Given any outbound notification, when its content is composed, then SMS never contains a drug name and all channels carry only the minimized content (ASSUMPTION-10). | BR-PHI-001 |
| PRD-REM-002 | As a patient, I want to opt out of reminders per channel, so that I control how I'm contacted. | Should | Given reminder settings, when the patient disables a channel, then no further reminders go to that channel and the other channel is unaffected. | BR-REM-001; per ASSUMPTION-8 |
| PRD-REM-003 | As a patient, I want to snooze a reminder to a later day, so that I'm re-prompted instead of forgetting. | Could | Given a reminder, when the patient snoozes it, then it re-fires on the chosen day through consented channels. | BR-REM-001; slice-3 candidate, not P0 |

## User flow (happy path + unhappy paths)
Refill due → system checks schedule classification (unknown ⇒ treat as controlled, stop) → consented patient gets push + SMS (minimized content) → one tap creates a request → request appears in the store queue → pharmacist approves (patient notified; dispense on time), rejects (patient notified with next step, ASSUMPTION-13), or proposes a substitution → patient accepts (proceed) or declines (back to pharmacist).
Error states: SMS or push delivery fails → the other consented channel still fires; network drop mid-tap → request not silently lost, patient sees retry; duplicate tap → one request, not two; substitution prompt unanswered → request stays held, visible to pharmacist as "awaiting patient"; opted-out patient → no reminder, prescription still visible in-app.

## User interaction and design
Extends existing patient app and pharmacist portal — match their current navigation and design language. Reminder tap-through must reach confirmation in one screen. Queue needs at-a-glance status (pending / awaiting patient / decided). Wireframes: `ux-ui-designer`, downstream.

## Decisions log
| Date | Decision | Reasoning | Trade-off accepted |
|---|---|---|---|
| 2026-07-09 | Substitution acceptance is in-app only, not SMS reply | SMS replies would carry PHI context and are unauthenticated | Patients without the app installed can't accept remotely |
| 2026-07-09 | Controlled-substance stories (PRD-CTRL-*) ship whole in one slice, never partially | BRD risk: 3-sprint pressure must not split compliance-critical flows | Slice 1 may carry less patient-visible scope |
| 2026-07-09 | Snooze (PRD-REM-003) deferred to Could | Not needed to move the primary metric; protects 3-sprint slice | Possible minor reminder-fatigue cost, watched via opt-out guardrail |

## Open questions
| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| Identity-verification method for Schedule II–V (blocks PRD-CTRL-002 acceptance detail) | Compliance / architect | Open (carried from BRD) | 2026-07-09 |
| Ratify ASSUMPTION-2 (on-time definition) and ASSUMPTION-5 (consent) before sprint commitment | PM / compliance | Open (carried from BRD) | 2026-07-09 |
| Ratify invented metric values ASSUMPTION-11/-12 and rejection next-step ASSUMPTION-13 | PM | Open | 2026-07-09 |

## What we're not doing (Won't-Have, from BRD scope)
- New-patient acquisition or marketing — module serves existing app patients only.
- E-prescribing, prescription transfers, or new-prescription intake — refills of existing prescriptions only.
- Payments, insurance adjudication, delivery/shipping — existing processes unchanged.
- Replacing the patient app or pharmacist portal — MedRemind extends both.
- Auto-approval of any refill without a pharmacist decision — every request is human-decided.
