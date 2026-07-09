# URS: MedRemind — Prescription Refill Reminder & Approval Module

*Author: `urs-writer` (QA / validation lead) · phase: requirements · 2026-07-09 · run3*
*Upstream: `brd-writer` (`02-brd.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Source of truth for scope: `brief.md`.*
*Downstream: `srs-writer`, `frd-writer`, `prd-writer`. RTM: `examples/medremind-fleet-eval/run3/RTM.md`.*

| Field | Value |
|---|---|
| Author | `urs-writer` (QA / validation lead) |
| Status | Draft |
| Version | v0.1 (pre-baseline) |
| Regulatory basis | HIPAA (PHI minimization) + DEA controlled-substance handling (Schedule II–V). **FDA 21 CFR Part 11 / GxP treated as NOT APPLICABLE** per ASSUMPTION-3 — see §7 and the FLAG in §10. |
| Last updated | 2026-07-09 |

## 1. Purpose & scope

This URS states, in user-and-environment terms, what the MedRemind module must let RxKart's
patients and pharmacists do, under what conditions, and to what safety, privacy, and
data-integrity standard. It is the design input that `srs-writer` (system/NFR), `prd-writer`
(product), and `frd-writer` (functional) refine, and that `test-plan-writer` later verifies.

**In scope (user requirements):** proactive refill reminders (push + SMS); the patient's
refill-request task; the pharmacist triage/approve/reject task; pharmacist-suggested generic
substitution with mandatory patient acceptance; controlled-substance (Schedule II–V) exclusion
from automation with an identity-verification and pharmacist-initiated-contact path; HIPAA
PHI-minimization in notifications; and the attributable audit records those tasks require.

**Out of scope (inherited from BRD §Scope, restated so this URS is self-contained):** payment /
copay collection; delivery / courier logistics; any new authentication platform (builds on the
existing IdP, ASSUMPTION-4); new prescription creation / e-prescribing; market discovery (MRD
dropped by doc-strategy); FDA 21 CFR Part 11 / GxP computerized-system validation
(ASSUMPTION-3); and non-US jurisdictions (ASSUMPTION-1). Quantified NFRs (≤5-min reminder
delivery, <2s queue load at 500 concurrent, 99.9% store-hours availability — CON-4) are the
`srs-writer`'s to own; this URS states only the user-facing operating condition and traces to
CON-4 rather than restating the numeric targets.

## 2. Intended use

MedRemind is intended to be used by **RxKart patients** (US, on the existing 250k-MAU mobile
app) to receive a timely, privacy-minimized reminder that a refillable prescription is due and
to request its refill; and by **RxKart pharmacists** (across 40 stores, in the existing
back-office portal) to triage those requests, decide approve/reject, and optionally offer a
generic substitution. The module is intended **only** for *existing, active* prescriptions; it
does not originate prescriptions and is **not** intended to remind, auto-refill, or one-tap
process any controlled substance (Schedule II–V). Controlled-substance refill intent is
intentionally routed out of automation to a verified, pharmacist-initiated manual path.

## 3. Users & environment

| User role | Competency / training | Environment & conditions |
|---|---|---|
| Patient (end user / beneficiary) | Untrained general consumer; owns a smartphone with the RxKart app installed and authenticated via the existing IdP. May have low health literacy; may act on a shared/insecure device. | Uncontrolled personal environment (home, transit). SMS may be seen by others → PHI-minimization is a user-environment requirement, not just a data rule. |
| Pharmacist (primary operator) | Licensed pharmacist trained on RxKart dispensing procedures and DEA controlled-substance handling; trained on the new queue as part of rollout (RxKart store operations). | Retail pharmacy counter during store hours; interleaves the queue with walk-in/counter work; up to 500 concurrent pharmacists chain-wide (operating condition; quantified in SRS via CON-4). |
| Pharmacy operations / store manager | Trained on RxKart workflow. | Absorbs the counter-workflow change; owns pharmacist training for rollout. |
| Compliance / HIPAA officer (approver) | Regulatory competency. | Reviews and signs off the PHI-minimization mechanism and controlled-substance handling (ASSUMPTION-6). |

## 4. Definitions

- **Intended use** — the specific purpose stated in §2; use outside it (e.g. controlled-substance automation) is prohibited by this URS.
- **Patient / user** — an RxKart account holder authenticated via the existing IdP (ASSUMPTION-4) who receives reminders and requests refills.
- **Operator** — a licensed RxKart pharmacist acting on the portal refill queue.
- **Refillable prescription** — an existing, active, non-controlled prescription with refills remaining, at or past its refill-due date.
- **Controlled substance** — a prescription classified DEA Schedule II–V; excluded from all automation by this URS.
- **PHI (protected health information)** — patient-identifying health data under HIPAA; in this URS the governing case is the *drug name*, which shall not appear in an SMS body.
- **Refill-due date** — the scheduled date, derived from the prescription record, at which a refill reminder becomes eligible to send.
- **Substitution acceptance** — the patient's explicit, recorded consent to a pharmacist-suggested generic before dispensing proceeds.
- **Identity verification** — the additional confirmation-of-identity step required before any controlled-substance refill proceeds (mechanism owned downstream; see ASSUMPTION-9).

## 5. User requirements

Every requirement is user- or environment-centric, singular, and verifiable. Verification key:
**AT** = acceptance/system test (equivalent of OQ in this non-GxP context, ASSUMPTION-8);
**INSP** = documented inspection / review; **SEC** = security review. Source column cites the
BRD requirement/constraint and any governing assumption.

### 5.1 Intended use & operator tasks

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-USE-001 | The system shall send a push notification to the patient when one of that patient's refillable, non-controlled prescriptions reaches its refill-due date. | Functional | AT | BR-001, CON-1 |
| URS-USE-002 | The system shall send an SMS notification to the patient when one of that patient's refillable, non-controlled prescriptions reaches its refill-due date. | Functional | AT | BR-001, CON-1 |
| URS-USE-003 | The system shall let the patient submit a refill request for an eligible non-controlled prescription in a single confirmation action. | Functional | AT | BR-001, BR-002 |
| URS-USE-004 | The system shall present to the pharmacist a single prioritized queue of pending refill requests. | Functional | AT | BR-003 |
| URS-USE-005 | The system shall let the pharmacist record an approve decision on a queued refill request. | Functional | AT | BR-003 |
| URS-USE-006 | The system shall let the pharmacist record a reject decision, with a reject reason, on a queued refill request. | Functional | AT | BR-003 |
| URS-USE-007 | The system shall let the pharmacist attach a suggested generic substitution to a refill request. | Functional | AT | BR-004 |

### 5.2 Safety-critical requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-SAF-001 | The system shall exclude any prescription classified DEA Schedule II–V from automated refill reminders. | Safety | AT, INSP | BR-005, CON-3 |
| URS-SAF-002 | The system shall exclude any prescription classified DEA Schedule II–V from the one-tap / self-service refill-request path. | Safety | AT, INSP | BR-005, CON-3 |
| URS-SAF-003 | The system shall block dispensing of a substituted prescription until the patient has recorded explicit acceptance of the substitution. | Safety | AT | BR-004 |
| URS-SAF-004 | The system shall route a controlled-substance (Schedule II–V) refill need to a pharmacist-initiated-contact path rather than any automated fulfilment. | Safety | AT, INSP | BR-005, CON-3 |

### 5.3 Security & identity requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-SEC-001 | The system shall require a successful identity-verification step before a controlled-substance (Schedule II–V) refill proceeds. | Security | AT, SEC | BR-005, CON-3, ASSUMPTION-4, ASSUMPTION-9 |

### 5.4 Data-integrity & privacy requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-DAT-001 | The system shall omit any drug name from the body of an SMS notification. | Data integrity | AT, INSP, SEC | BR-006, CON-2 |
| URS-DAT-002 | The system shall record each pharmacist decision on a refill request as an attributable, timestamped audit entry identifying the acting pharmacist. | Data integrity | AT, INSP | BR-003, ASSUMPTION-8 |
| URS-DAT-003 | The system shall record the patient's substitution acceptance with a timestamp as the consent record of dispensing. | Data integrity | AT, INSP | BR-004 |

## 6. Safety & quality attributes

- **Controlled-substance hard exclusion (safety-critical).** Schedule II–V handling
  (URS-SAF-001, -002, -004, URS-SEC-001) is the highest-risk area: a single leak of a
  controlled substance into the automated path is a DEA violation (BRD risk, KPI-5 guardrail).
  These requirements are verified by both functional test **and** inspection, and are within
  the mandatory security-review gate (ASSUMPTION-2).
- **PHI minimization (data-integrity / privacy).** URS-DAT-001 governs the SMS body because
  the patient environment is uncontrolled (§3). This is the governing HIPAA case; broader PHI
  handling is refined in SRS/SDD (BR-006 routing).
- **Attributable, timestamped records (ALCOA+ flavor).** URS-DAT-002/-003 give every
  clinical decision and consent an attributable, time-stamped record. Full ALCOA+ / Part 11
  audit-trail rigor is **not** claimed because Part 11 is out of scope (ASSUMPTION-3); if that
  flips, these requirements expand to full audit-trail + e-signature controls (see FLAG §10).
- **Patient consent to substitution (safety).** URS-SAF-003 preserves patient consent as a
  dispensing precondition.

## 7. Constraints & assumptions

**Constraints (ratified — carried from BRD):**
- **CON-1** — SMS via Twilio; push via existing Firebase.
- **CON-2** — HIPAA applies; no drug names in SMS (governs URS-DAT-001).
- **CON-3** — Schedule II–V: no auto-reminder / no one-tap refill; identity verification +
  pharmacist-initiated contact (governs URS-SAF-001/-002/-004, URS-SEC-001).
- **CON-4** — Reminder ≤5 min of scheduled time; queue <2s at 500 concurrent; 99.9%
  store-hours availability. **Owned by `srs-writer`**; stated here only as the operating
  condition users work within (§3), not re-authored as URS requirements.
- **CON-5** — Fixed team of 7; two-week sprints; Azure DevOps; first slice in 3 sprints.

**Assumptions (unratified — carried from BRD, do not treat as decided):**
- **ASSUMPTION-1** *(owner: `spec-steward`)* — US-only jurisdiction / DEA scope inferred from `brief.md`; living-spec not routed. **Gates this URS** (§10 FLAG).
- **ASSUMPTION-2** *(owner: PM)* — Security review (and a11y) craft is borrowed/contracted; the URS-SAF/-SEC/-DAT gates depend on it.
- **ASSUMPTION-3** *(owner: architect)* — "Regulated" = HIPAA + DEA, **not** FDA 21 CFR Part 11 / GxP. **Determines this URS's verification depth** (AT+INSP, not IQ/OQ/PQ). **Gates this URS** (§10 FLAG).
- **ASSUMPTION-4** *(owner: PM)* — Patient/pharmacist authentication is the existing IdP; URS-SEC-001 builds on it.
- **ASSUMPTION-5** *(owner: PM / `product-analytics`)* — Numeric KPI-2/3/4 targets set at GA. (Not a URS driver; carried for chain integrity.)
- **ASSUMPTION-6** *(owner: PM)* — A named HIPAA/compliance sign-off authority exists to approve PHI-minimization (§3 approver role).
- **ASSUMPTION-7** *(owner: PM / `product-analytics`)* — "On-time refill rate" denominator undefined. (Business-metric assumption; carried.)

**Assumptions (new — introduced by `urs-writer`):**
- **ASSUMPTION-8** *(owner: QA lead / `urs-writer`)* — Because Part 11/GxP is out of scope (ASSUMPTION-3), verification is by acceptance/system test + inspection + security review, **not** formal IQ/OQ/PQ, and audit records are attributable-and-timestamped rather than full Part 11 audit trails. If ASSUMPTION-3 flips, this URS becomes a validated deliverable and this row is void.
- **ASSUMPTION-9** *(owner: architect / compliance officer)* — The prescription record carries an authoritative DEA-schedule classification (from the existing dispensing system) that MedRemind reads to enforce URS-SAF-001/-002/-004; and the acceptable *mechanism* of controlled-substance identity verification (URS-SEC-001) is defined downstream by the architect/compliance officer, not by this URS. The exclusion is only as trustworthy as that classification source. *(see §10 FLAG)*

## 8. Traceability

Full BR↔URS mapping is written into the shared `RTM.md` (this pass fills the *User req (URS)*
column). Design-spec and validation-protocol columns are filled downstream by `srs-writer` /
`sdd-writer` / `test-plan-writer`.

| URS ID | Traces to (BRD) | Design spec | Validation / test protocol |
|---|---|---|---|
| URS-USE-001 | BR-001 | (srs/sdd) | (test-plan) |
| URS-USE-002 | BR-001 | (srs/sdd) | (test-plan) |
| URS-USE-003 | BR-001, BR-002 | (prd/srs) | (test-plan) |
| URS-USE-004 | BR-003 | (srs/sdd) | (test-plan) |
| URS-USE-005 | BR-003 | (srs/sdd) | (test-plan) |
| URS-USE-006 | BR-003 | (srs/sdd) | (test-plan) |
| URS-USE-007 | BR-004 | (srs/sdd) | (test-plan) |
| URS-SAF-001 | BR-005, CON-3 | (srs/sdd) | (test-plan) |
| URS-SAF-002 | BR-005, CON-3 | (srs/sdd) | (test-plan) |
| URS-SAF-003 | BR-004 | (srs/sdd) | (test-plan) |
| URS-SAF-004 | BR-005, CON-3 | (srs/sdd) | (test-plan) |
| URS-SEC-001 | BR-005, CON-3 | (srs/sdd) | (test-plan) |
| URS-DAT-001 | BR-006, CON-2 | (srs/sdd) | (test-plan) |
| URS-DAT-002 | BR-003 | (srs/sdd) | (test-plan) |
| URS-DAT-003 | BR-004 | (srs/sdd) | (test-plan) |

## 9. Change control

| Version | Change | Reason | Approved by | Date |
|---|---|---|---|---|
| v0.1 | Initial URS drafted from `02-brd.md`. | Establish user requirements as design input. | (pending — QA lead) | 2026-07-09 |

## 10. Open items & flags

```
FLAG(spec-steward): ASSUMPTION-1 (US-only / DEA jurisdiction) and ASSUMPTION-3 (Part 11/GxP
not applicable) directly gate this URS. If Part 11/GxP is later ruled applicable, this URS
must be re-baselined as a validated deliverable (IQ/OQ/PQ, full audit trail + e-signatures),
voiding ASSUMPTION-8 and expanding URS-SAF/-SEC/-DAT. Please route the living-spec to ratify
ASSUMPTION-1/-3 before the URS is baselined. (Escalation echoes brd-writer's spec-steward FLAG.)
```

```
FLAG(architect): The controlled-substance exclusion (URS-SAF-001/-002/-004) and identity
verification (URS-SEC-001) depend on an authoritative DEA-schedule classification on the
prescription record and on a defined verification mechanism — captured as ASSUMPTION-9 (owner:
architect / compliance officer). The exclusion is only as reliable as that classification
source. Please confirm the source-of-truth field and the acceptable verification mechanism in
the SRS/SDD, and feed any correction back under change control.
```
