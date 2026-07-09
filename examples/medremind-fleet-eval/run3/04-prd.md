# PRD: MedRemind — Prescription Refill Reminder & Approval Module

*Author: `prd-writer` (senior product manager) · phase: requirements · 2026-07-09 · run3*
*Upstream: `brd-writer` (`02-brd.md`), `urs-writer` (`03-urs.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Source of truth for scope: `brief.md`.*
*Downstream: `frd-writer`, `backlog-manager`, `solution-recon`, `ux-ui-designer`, `ai-eval`, `product-analytics`. RTM: `examples/medremind-fleet-eval/run3/RTM.md`.*

| Field | Value |
|---|---|
| Participants | PM (acting PO, owner) · architect · borrowed UI/UX designer (ASSUMPTION-2) · QA lead · borrowed security engineer (ASSUMPTION-2) · compliance/HIPAA officer (ASSUMPTION-6) |
| Status | Draft |
| Target release | First shippable slice by end of sprint 3 (vertical: reminder → one-tap refill → pharmacist queue); full module by end of quarter 2 (CON-5) |
| Last updated | 2026-07-09 |

## Problem statement

RxKart owns the relationship with 250k monthly-active patients and the dispensing workflow, yet **59% of refillable prescriptions are not refilled on time** (41% on-time baseline, `02-brd.md` §Background). The refill loop is entirely patient-initiated with no prompt: a patient must *remember* a prescription is due, then phone or walk into a store. Pharmacists absorb that intent ad hoc alongside counter work, with **no queue, no prioritization, and no visibility into pending refill demand**. Two user pains sit under the business number:

- **Patient pain:** there is no proactive signal that a refill is due, so intent is lost before it becomes action — and any signal must survive an *uncontrolled* environment (an SMS may be read by someone other than the patient, `03-urs.md` §3), so it must not leak what the patient takes.
- **Pharmacist pain:** refill intent arrives unstructured (phone/walk-in), so pharmacists cannot triage it within the store-hours service window without adding phone-handling load.

The fix is a compliant, repeatable loop — **remind → one-tap request → pharmacist triage/decision** — that converts existing reach into completed on-time refills without a HIPAA or controlled-substance breach.

## Team goals and business objectives

Translated (not copied) from the BRD business goals: convert RxKart's existing 250k-MAU reach into a **repeatable, compliant refill loop** that lifts the on-time refill rate toward the leadership target (BG-001), captures reminded intent through a one-tap path (BG-002), and gives pharmacists a triage queue that clears within store hours without new phone load (BG-003) — all delivered as a demonstrable vertical slice on the 3-sprint timeline (BG-004) with **zero** PHI-exposure and controlled-substance policy violations (BG-005).

## Success metrics

Three layers, translated from the BRD KPIs. Only the primary target is ratified today; supporting targets are set at GA once baselines are instrumented (**ASSUMPTION-5**, owner PM / `product-analytics`).

- **Primary** — On-time refill rate: **41% → 60%** within two quarters post-GA (KPI-1 / BG-001). Denominator definition is **not yet ratified** (**ASSUMPTION-7**, owner PM / `product-analytics`) — the metric is directional until `product-analytics` fixes it.
- **Secondary** — Reminder-to-refill conversion: refills completed within 7 days of a reminder ÷ reminders sent (KPI-3); and patient-initiated refill requests per active patient per month (KPI-2). Baselines are 0 (feature is new); targets set at GA (ASSUMPTION-5).
- **Guardrail** — **Zero** HIPAA PHI-exposure incidents and **zero** Schedule II–V auto-reminder / one-tap-refill policy violations (KPI-5 / BG-005). These must not regress under any trade-off; they are non-negotiable gates, not tunable targets.

Operational guardrails owned as NFRs by `srs-writer` (CON-4) and carried here for the flow only: reminder delivered ≤5 min of scheduled time; queue loads <2s at 500 concurrent pharmacists; 99.9% store-hours availability.

## Assumptions

Carried from upstream (do not re-invent; do not treat as decided):

- **ASSUMPTION-1** *(owner: `spec-steward`)* — US-only jurisdiction / DEA scope inferred from `brief.md`; living-spec not routed. Gates URS/SRS.
- **ASSUMPTION-2** *(owner: PM)* — Designer, security, SRE, BA craft is borrowed/contracted; the design and security-review gates in this PRD depend on it.
- **ASSUMPTION-3** *(owner: architect)* — "Regulated" = HIPAA + DEA, **not** FDA 21 CFR Part 11 / GxP.
- **ASSUMPTION-4** *(owner: PM)* — Patient/pharmacist auth is the existing IdP; the Schedule II–V identity-verification step builds on it.
- **ASSUMPTION-5** *(owner: PM / `product-analytics`)* — Numeric targets for the secondary metrics are set at GA once instrumented.
- **ASSUMPTION-6** *(owner: PM)* — A named HIPAA/compliance sign-off authority exists to approve the PHI-minimization mechanism.
- **ASSUMPTION-7** *(owner: PM / `product-analytics`)* — "On-time refill rate" denominator is undefined; `product-analytics` must ratify it before it is the acceptance metric for the primary goal.
- **ASSUMPTION-9** *(owner: architect / compliance officer)* — The prescription record carries an authoritative DEA-schedule classification that the module reads to enforce the controlled-substance exclusion; the exclusion is only as trustworthy as that source.

New in this PRD:

- **ASSUMPTION-10** *(owner: PM / product-analytics)* — When a patient has **multiple** prescriptions due in the same window, reminders are **batched into one notification** (rather than one per prescription) to avoid notification fatigue and reduce PHI surface. Batching content/UX is a design decision for `ux-ui-designer`; the batching rule itself needs PM ratification.
- **ASSUMPTION-11** *(owner: PM)* — A patient can **turn refill reminders off** (channel/opt-out preference). Whether opt-out is per-channel (push vs SMS) or all-or-nothing, and whether it is required for a compliant SMS program, is unratified — `ux-ui-designer` and the compliance officer to confirm.
- **ASSUMPTION-12** *(owner: PM)* — After a pharmacist **approves** a refill, the patient is notified that the refill is ready/approved (a closing-the-loop confirmation). The exact channel and copy are for `ux-ui-designer`; that a confirmation exists is the product decision here.

## User personas

- **Priya, the busy patient (primary end user).** Untrained general consumer on the existing RxKart app, authenticated via the IdP. May have low health literacy and may read notifications on a shared or lock-screen-visible device. Wants to not run out of a medication without having to remember or call the store. **Privacy-sensitive by environment**, not by choice — see `03-urs.md` §3.
- **Sam, the counter pharmacist (primary operator).** Licensed pharmacist trained on RxKart dispensing and DEA handling; interleaves the new queue with walk-in and counter work during store hours. Wants to clear pending refills fast and safely, and must never be nudged toward auto-processing a controlled substance.
- **Compliance/HIPAA officer (approver).** Signs off the PHI-minimization mechanism and controlled-substance handling (ASSUMPTION-6).

## User stories (MoSCoW)

Priority key: **Must** = in the 3-sprint vertical slice (BG-004); **Should** = target release, not slice-blocking; **Could** = opportunistic; **Won't** = §What we're not doing. Every story traces to a BRD requirement and (where applicable) the ratified URS user requirement, so downstream QA can verify it.

| # | ID | Story | Priority | Acceptance criteria (Given/When/Then) | Traces |
|---|---|---|---|---|---|
| 1 | PRD-RMD-001 | As a patient, I want a push reminder when a refillable prescription is due, so that I act before I lapse. | Must | Given an active, non-controlled prescription that reaches its refill-due date, when the reminder job runs, then a push notification is delivered to the patient's authenticated device within the operating window (CON-4), and it contains **no drug name**. | BR-001, URS-USE-001, CON-1 |
| 2 | PRD-RMD-002 | As a patient, I want an SMS reminder as well as push, so that I'm reminded even if push is off or unseen. | Must | Given the same due prescription, when the reminder is sent, then an SMS is delivered whose **body contains no drug name** (a neutral "a prescription is ready to refill" message with a deep link); PHI minimization is verifiable in the message body. | BR-001, URS-USE-002, URS-DAT-001, CON-1, CON-2 |
| 3 | PRD-RFL-001 | As a patient, I want to request a refill in one tap from the reminder, so that reminded intent becomes a request without friction. | Must | Given a delivered reminder for an eligible non-controlled prescription, when the patient taps "Request refill" and confirms once, then a refill request is created and the patient sees a "request received" state; **no second-screen form** is required for the happy path. | BR-002, URS-USE-003 |
| 4 | PRD-QUE-001 | As a pharmacist, I want a single prioritized queue of pending refill requests, so that I can triage demand within store hours. | Must | Given one or more pending requests, when the pharmacist opens the portal queue, then all pending requests are listed in one prioritized view with the fields needed to decide (patient, prescription, request time), loading within the CON-4 window; controlled substances never appear as one-tap requests here. | BR-003, URS-USE-004 |
| 5 | PRD-QUE-002 | As a pharmacist, I want to approve a queued request, so that the refill proceeds and the patient is informed. | Must | Given a pending request, when the pharmacist approves it, then the decision is recorded as an attributable, timestamped audit entry identifying the pharmacist, the item leaves the pending queue, and the patient receives an approval/ready confirmation (ASSUMPTION-12). | BR-003, URS-USE-005, URS-DAT-002 |
| 6 | PRD-QUE-003 | As a pharmacist, I want to reject a request with a reason, so that the patient understands the outcome and the decision is auditable. | Should | Given a pending request, when the pharmacist rejects it, then a **reject reason is required** before the rejection is accepted, the decision is recorded as an attributable timestamped audit entry, and the patient is notified of the outcome (no drug name in any SMS). | BR-003, URS-USE-006, URS-DAT-002 |
| 7 | PRD-SUB-001 | As a pharmacist, I want to offer a generic substitution the patient must accept, so that consent is preserved before dispensing. | Should | Given a request, when the pharmacist attaches a suggested generic substitution, then dispensing is **blocked until the patient records explicit acceptance**; the acceptance is stored with a timestamp as the consent record; if the patient declines or does not respond, dispensing does not proceed on the substitution. | BR-004, URS-USE-007, URS-SAF-003, URS-DAT-003 |
| 8 | PRD-CTL-001 | As a patient with a controlled-substance (Schedule II–V) refill need, I want a clear manual path, so that I'm never auto-reminded or one-tap-refilled and I know what to do instead. | Must | Given a prescription classified DEA Schedule II–V (per the authoritative classification, ASSUMPTION-9), when a refill would otherwise be due, then **no automated reminder and no one-tap refill option is ever presented**; the patient is instead routed to identity verification and a pharmacist-initiated-contact path. | BR-005, URS-SAF-001, URS-SAF-002, URS-SAF-004, URS-SEC-001, CON-3 |
| 9 | PRD-PRF-001 | As a patient, I want to control whether/how I receive refill reminders, so that I'm not spammed and my privacy preference is respected. | Could | Given the patient is in reminder settings, when they turn reminders off (or choose a channel), then no further reminders are sent on the disabled channel; the preference persists. **Opt-out granularity and compliance requirement are unratified (ASSUMPTION-11).** | BR-001 (derived), ASSUMPTION-11 |

## User flow

**Happy path (patient):** prescription reaches refill-due date → module confirms it is non-controlled (ASSUMPTION-9 classification) → batched, PHI-minimized reminder sent via push + SMS (ASSUMPTION-10) → patient taps deep link → one-tap "Request refill" + single confirm → "request received" state → request enters pharmacist queue → pharmacist approves → patient gets approval/ready confirmation (ASSUMPTION-12).

**Happy path (pharmacist):** opens portal → sees prioritized pending queue (loads <2s at 500 concurrent, CON-4) → selects a request → approves, **or** rejects with a required reason, **or** attaches a generic substitution → decision recorded as attributable timestamped audit entry.

**Substitution path:** pharmacist suggests generic → patient sees substitution → patient **accepts** (dispensing proceeds, acceptance stored as consent) **or declines / times out** (dispensing does **not** proceed on the substitution; falls back to pharmacist follow-up).

**Controlled-substance path (excluded from automation):** a Schedule II–V prescription is **never** entered into the reminder job or the one-tap path; the patient is routed to identity verification + pharmacist-initiated contact. This is the highest-risk flow (KPI-5 guardrail) and is verified by test **and** inspection upstream (URS §6).

**Error / edge states (the unhappy path — where products break):**

- **SMS deliverability fails / delayed (Twilio):** push is the redundant channel; a missed/late SMS must not double-charge intent or create duplicate requests. Delivery SLO owned by SRE/`srs-writer` (CON-4).
- **Duplicate tap / double submit:** a second tap on "Request refill" for the same due prescription is **idempotent** — it does not create a second queue item.
- **Prescription no longer eligible at tap time** (no refills remaining, expired, now flagged controlled): the request is refused with a clear reason; **no request is created** and the patient is directed to the appropriate path (e.g., controlled-substance manual path).
- **Misclassified schedule / classification source unavailable (ASSUMPTION-9):** if the authoritative DEA-schedule classification is missing or unreadable, the system **fails closed** — it does not auto-remind or offer one-tap refill (never fail-open into the automated path). *(Product intent; enforcement mechanism owned by architect/`srs-writer`.)*
- **Patient on a shared/visible device (uncontrolled environment, URS §3):** no notification (push preview or SMS body) reveals the drug name.
- **Pharmacist rejects without reason:** blocked — the reason is a required field (PRD-QUE-003).
- **Substitution not accepted:** dispensing halts on the substitution (PRD-SUB-001).
- **Empty queue:** pharmacist sees an explicit empty state, not a spinner or error.

## User interaction and design

Design is owned by the **borrowed UI/UX designer** (ASSUMPTION-2); no wireframes exist yet. Product intent for design to solve:

- **Patient surfaces** (existing 250k-MAU app + notifications): a reminder notification whose visible content is PHI-minimized (neutral copy, deep link — no drug name in push preview or SMS body), and a one-tap refill confirmation that is genuinely one tap on the happy path. Batching UX for multiple-due prescriptions (ASSUMPTION-10) and reminder settings/opt-out (ASSUMPTION-11) to be designed.
- **Pharmacist surface** (existing portal): a prioritized queue and a decision panel (approve / reject-with-reason / suggest-substitution) usable while interleaving counter work, meeting the <2s @ 500-concurrent NFR (CON-4).
- **Accessibility** is a mandatory gate for the patient app (owner: borrowed a11y craft, ASSUMPTION-2) — hand to `ux-ui-designer` / `accessibility-auditor`.

## Decisions log

| Date | Decision | Reasoning | Trade-off accepted |
|---|---|---|---|
| 2026-07-09 | The 3-sprint slice (BG-004) is the reminder → one-tap request → pharmacist **approve** vertical: PRD-RMD-001, PRD-RMD-002, PRD-RFL-001, PRD-QUE-001, PRD-QUE-002, plus the PRD-CTL-001 exclusion guard. | This is the smallest end-to-end demonstrable loop that proves the business hypothesis and keeps the controlled-substance guardrail intact. | Reject-with-reason (PRD-QUE-003), substitution (PRD-SUB-001), and opt-out (PRD-PRF-001) are **Should/Could** — deferred past the slice, not dropped. |
| 2026-07-09 | Controlled-substance handling is expressed as a **Must** product story (PRD-CTL-001) even though BR-005 routes primarily to URS/SRS. | The exclusion has a patient-facing UX (what the patient sees instead of a one-tap option); leaving it implicit risks a designer/dev inventing an unsafe path. | Duplicates traceability into URS-SAF/-SEC, accepted for safety clarity. |
| 2026-07-09 | Reminders are **PHI-minimized in both channels**, not just SMS. | The push preview is also visible on a lock screen in an uncontrolled environment (URS §3); the guardrail is the environment, not the transport. | Slightly less actionable notification copy, accepted to protect the zero-PHI guardrail. |
| 2026-07-09 | On classification failure the module **fails closed** (no automation). | A false-negative that lets a controlled substance into automation is a DEA violation (KPI-5); a false-positive merely falls back to the manual path. | A non-controlled refill may occasionally miss automation and need the manual path — acceptable vs. the compliance risk. |

## Open questions

| Question | Owner | Answer / Decision | Date |
|---|---|---|---|
| Precise "on-time refill rate" denominator (acceptance metric for BG-001) | PM / `product-analytics` | Open — ASSUMPTION-7 | — |
| GA numeric targets for conversion, requests/patient, queue clearance | PM / `product-analytics` | Open — ASSUMPTION-5 | — |
| Are multiple-due reminders batched into one notification? | PM / `ux-ui-designer` | Open — ASSUMPTION-10 | — |
| Opt-out granularity (per-channel vs all) and whether SMS opt-out is compliance-required | PM / compliance / `ux-ui-designer` | Open — ASSUMPTION-11 | — |
| Post-approval patient confirmation channel & copy | PM / `ux-ui-designer` | Open — ASSUMPTION-12 | — |
| Authoritative DEA-schedule classification field + verification mechanism | architect / compliance officer | Open — ASSUMPTION-9 (see FLAG) | — |

## What we're not doing (MoSCoW Won't-Have this release)

Inherited from `02-brd.md` §Scope and restated so this PRD is self-contained:

- **Payment / copay collection** — handled by existing pharmacy billing; not part of the reminder/approval loop.
- **Delivery / courier logistics** — module covers request → approval, not fulfilment transport.
- **New auth platform** — builds on the existing IdP (ASSUMPTION-4).
- **New prescription creation / e-prescribing** — reminds and refills *existing* prescriptions only.
- **Market discovery / MRD** — RxKart has an established product and known market (doc-strategy DROP).
- **FDA 21 CFR Part 11 / GxP validation** — treated as not applicable (ASSUMPTION-3); if it applies, PRD and URS re-open.
- **Non-US jurisdictions** — US-only pending ratification (ASSUMPTION-1).
- **Automated controlled-substance refilling of any kind** — a hard, permanent exclusion (CON-3), not a deferral.

## Flags

```
FLAG(architect): PRD-CTL-001's "fail closed on classification failure" and the controlled-substance
exclusion depend on the authoritative DEA-schedule classification and verification mechanism
captured as ASSUMPTION-9 (owner: architect / compliance officer). This PRD states the product
intent (never fail-open into automation); the enforcement mechanism and source-of-truth field
are yours to confirm in the SRS/SDD. Echoes urs-writer's architect FLAG (03-urs.md §10).
```

```
FLAG(product-analytics): The primary success metric (on-time refill rate 41%→60%) is
directional until its denominator is ratified (ASSUMPTION-7) and the secondary targets are set
(ASSUMPTION-5). Please fix these before the PRD metrics become acceptance gates for BG-001/002.
```
