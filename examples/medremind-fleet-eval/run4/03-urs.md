# URS: MedRemind — RxKart Prescription Refill Reminder & Approval Module

*Author: `urs-writer` (QA / validation lead) · phase: requirements · 2026-07-10 · run4*
*Upstream: `brd-writer` (`02-brd.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Scope source of truth: `brief.md`.*
*Downstream: `srs-writer`, `frd-writer`, `prd-writer`. RTM: `examples/medremind-fleet-eval/run4/RTM.md`.*
*Register id: **DOC-003** (Keep — regulated overlay; kept to ~2–3 pages per doc-strategy §4).*

| Field | Value |
|---|---|
| Author | `urs-writer` (QA / validation lead) |
| Status | Draft |
| Version | v0.1 (pre-baseline) |
| Regulatory basis | HIPAA (PHI minimization in notifications) + DEA / state-board controlled-substance handling (Schedule II–V). **FDA 21 CFR Part 11 / GAMP computerized-system validation treated as NOT APPLICABLE** per ASSUMPTION-6 — see §7 and the FLAG in §10. |
| Last updated | 2026-07-10 |

## 1. Purpose & scope

This URS states, in user-and-environment terms, what the MedRemind module must let RxKart's
patients and pharmacists do, under what conditions, and to what safety, privacy, and
data-integrity standard. It is the design input that `srs-writer` (system/NFR), `prd-writer`
(product), and `frd-writer` (functional behaviour → PBIs) refine, and that `test-plan-writer`
later verifies as the auditable evidence chain (doc-strategy §8 DoD). It is intentionally lean:
doc-strategy §4 rules this a HIPAA + DEA overlay, **not** a GAMP-validated system, so the URS
gives auditors and the test plan a stable design input that churning PBIs cannot.

**In scope (user requirements):** proactive refill reminders (push + SMS); the patient's
one-tap refill-request task; the pharmacist triage / approve / reject task; pharmacist-suggested
generic substitution with mandatory patient acceptance before dispensing; controlled-substance
(Schedule II–V) exclusion from automation with an identity-verification and
pharmacist-initiated-contact path; HIPAA PHI-minimization in notification content; and the
attributable, timestamped records those tasks require.

**Out of scope (inherited from BRD §Scope, restated so this URS is self-contained):** payment /
copay collection; delivery / courier logistics; net-new mobile-app or portal builds (brownfield
module bolted onto existing surfaces, doc-strategy §1); channel selection (Twilio SMS + Firebase
push are fixed, ASSUMPTION-5); clinical decision support / drug-interaction checking; and
FDA 21 CFR Part 11 / GAMP validation (ASSUMPTION-6). The three quantified NFRs — ≤5-min reminder
delivery, <2 s queue load at 500 concurrent pharmacists, 99.9% store-hours availability
(CON-4) — are the `srs-writer`'s to own; this URS states only the user-facing operating
condition (§3) and traces to CON-4, rather than re-authoring the numeric targets as URS
requirements.

## 2. Intended use

MedRemind is intended to be used by **RxKart patients** (on the existing 250k-MAU mobile app) to
receive a timely, privacy-minimized reminder that a refillable prescription is due and to
request its refill; and by **RxKart pharmacists** (across 40 stores, in the existing back-office
portal) to triage those requests, decide approve / reject, and optionally offer a generic
substitution. The module is intended **only** for *existing, active, non-controlled*
prescriptions; it does not originate prescriptions, and it is **not** intended to remind,
auto-refill, or one-tap process any controlled substance (Schedule II–V). Controlled-substance
refill intent is deliberately routed out of automation to a verified, pharmacist-initiated
manual path (§5.2–5.3).

## 3. Users & environment

| User role | Competency / training | Environment & conditions |
|---|---|---|
| Patient (end user / beneficiary) | Untrained general consumer; owns a smartphone with the RxKart app installed and authenticated via the existing app login. May have low health literacy; may act on a shared or insecure device. | Uncontrolled personal environment (home, transit). An SMS may be visible to others → PHI-minimization is a *user-environment* requirement, not merely a data rule (§5.4). |
| Pharmacist (primary operator) | Licensed pharmacist trained on RxKart dispensing procedures and DEA / state-board controlled-substance handling; trained on the new refill queue as part of rollout. | Retail pharmacy counter during store hours; interleaves the queue with walk-in / counter work; up to 500 concurrent pharmacists chain-wide (operating condition; quantified by `srs-writer` via CON-4). |
| Pharmacy operations / store manager | Trained on RxKart workflow. | Absorbs the counter-workflow change; owns pharmacist training for rollout. |
| Compliance / regulatory officer (approver) | DEA / state-board + HIPAA regulatory competency. | Reviews and signs off the PHI-minimization mechanism and the controlled-substance handling path before baseline (ASSUMPTION-9). |

## 4. Definitions

- **Intended use** — the specific purpose stated in §2; use outside it (e.g. controlled-substance automation) is prohibited by this URS.
- **Patient / user** — an RxKart account holder authenticated via the existing app login who receives reminders and requests refills.
- **Operator** — a licensed RxKart pharmacist acting on the portal refill-request queue.
- **Refillable prescription** — an existing, active, non-controlled prescription with refills remaining, at or past its refill-due date.
- **Controlled substance** — a prescription classified DEA Schedule II–V; excluded from all automation by this URS.
- **PHI (protected health information)** — patient-identifying health data under HIPAA; in this URS the governing case is the *drug name*, which shall not appear in an SMS body (URS-DAT-001).
- **Refill-due date** — the scheduled date, derived from the prescription record, at which a refill reminder becomes eligible to send.
- **Substitution acceptance** — the patient's explicit, recorded consent to a pharmacist-suggested generic before dispensing proceeds.
- **Identity verification** — the additional confirmation-of-identity step required before any controlled-substance refill proceeds (mechanism owned downstream; see ASSUMPTION-8).

## 5. User requirements

Every requirement is user- or environment-centric, singular, and verifiable. Verification key:
**AT** = acceptance / system test (the OQ-equivalent in this non-GAMP context, ASSUMPTION-7);
**INSP** = documented inspection / review; **SEC** = security review (doc-strategy DOC-004,
owned by architect / `security-reviewer`). The Source column cites the governing BRD
requirement / constraint and any governing assumption.

### 5.1 Intended use & operator tasks

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-USE-001 | The system shall send a push notification to the patient when one of that patient's refillable, non-controlled prescriptions reaches its refill-due date. | Functional | AT | BR-REFILL-001, CON-1 |
| URS-USE-002 | The system shall send an SMS notification to the patient when one of that patient's refillable, non-controlled prescriptions reaches its refill-due date. | Functional | AT | BR-REFILL-001, CON-1 |
| URS-USE-003 | The system shall let the patient submit a refill request for an eligible non-controlled prescription in a single confirmation action. | Functional | AT | BR-REFILL-002 |
| URS-USE-004 | The system shall present to the pharmacist a single queue of all pending refill requests. | Functional | AT | BR-QUEUE-001 |
| URS-USE-005 | The system shall let the pharmacist record an approve decision on a queued refill request. | Functional | AT | BR-QUEUE-002 |
| URS-USE-006 | The system shall let the pharmacist record a reject decision, with a reject reason, on a queued refill request. | Functional | AT | BR-QUEUE-002 |
| URS-USE-007 | The system shall let the pharmacist attach a suggested generic substitution to a refill request. | Functional | AT | BR-SUB-001 |

### 5.2 Safety-critical requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-SAF-001 | The system shall exclude any prescription classified DEA Schedule II–V from automated refill reminders. | Safety | AT, INSP | BR-CTRL-001, BR-CTRL-004 |
| URS-SAF-002 | The system shall exclude any prescription classified DEA Schedule II–V from the self-service one-tap refill-request path. | Safety | AT, INSP | BR-CTRL-001, BR-CTRL-004 |
| URS-SAF-003 | The system shall block dispensing of a substituted prescription until the patient has recorded explicit acceptance of the substitution. | Safety | AT | BR-SUB-002 |
| URS-SAF-004 | The system shall route a controlled-substance (Schedule II–V) refill need to a pharmacist-initiated-contact path rather than any automated fulfilment. | Safety | AT, INSP | BR-CTRL-003, BR-CTRL-004 |

### 5.3 Security & identity requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-SEC-001 | The system shall require a successful identity-verification step before a controlled-substance (Schedule II–V) refill proceeds. | Security | AT, SEC | BR-CTRL-002, BR-CTRL-004, ASSUMPTION-8 |

### 5.4 Data-integrity & privacy requirements

| ID | Requirement ("the system shall …") | Category | Verification | Source |
|---|---|---|---|---|
| URS-DAT-001 | The system shall omit any drug name from the body of an SMS notification. | Data integrity | AT, INSP, SEC | BR-PHI-001, BR-PHI-002, CON-2 |
| URS-DAT-002 | The system shall record each pharmacist decision on a refill request as an attributable, timestamped audit entry identifying the acting pharmacist. | Data integrity | AT, INSP | BR-QUEUE-002, ASSUMPTION-7 |
| URS-DAT-003 | The system shall record the patient's acceptance of a suggested generic substitution with a timestamp as the consent record for dispensing. | Data integrity | AT, INSP | BR-SUB-002 |

## 6. Safety & quality attributes

- **Controlled-substance hard exclusion (safety-critical).** Schedule II–V handling
  (URS-SAF-001, URS-SAF-002, URS-SAF-004, URS-SEC-001) is the highest-risk area: a single leak
  of a controlled substance into the automated path is a DEA / state-board violation (BRD risk;
  BR-CTRL-004 zero-violation guardrail). These requirements are verified by both functional test
  **and** documented inspection, and fall inside the mandatory security-review gate
  (DOC-004; doc-strategy §8 DoR: controlled-substance stories additionally require a URS +
  threat-model reference before entering a sprint).
- **PHI minimization (data-integrity / privacy).** URS-DAT-001 governs the SMS body because the
  patient environment is uncontrolled (§3). This is the governing HIPAA case (BR-PHI-001 /
  BR-PHI-002 zero-violation guardrail); broader PHI handling in push/in-app surfaces is refined
  downstream in the RFC (DOC-002).
- **Attributable, timestamped records (ALCOA+ flavour).** URS-DAT-002 and URS-DAT-003 give every
  pharmacist decision and every patient consent an attributable, time-stamped record. Full
  ALCOA+ / Part 11 audit-trail and e-signature rigour is **not** claimed because Part 11 is out
  of scope (ASSUMPTION-6, ASSUMPTION-7); if that ruling flips, these requirements expand to full
  audit-trail + e-signature controls (see FLAG §10).
- **Patient consent to substitution (safety).** URS-SAF-003 preserves patient consent as a
  hard dispensing precondition, and URS-DAT-003 is its record.

## 7. Constraints & assumptions

**Constraints (ratified — carried from BRD / doc-strategy):**
- **CON-1** — SMS via Twilio; push via the existing Firebase setup (ASSUMPTION-5).
- **CON-2** — HIPAA applies; no drug names in SMS content (governs URS-DAT-001).
- **CON-3** — Schedule II–V: no auto-reminder, no one-tap refill; identity verification +
  pharmacist-initiated contact (governs URS-SAF-001, URS-SAF-002, URS-SAF-004, URS-SEC-001).
- **CON-4** — Reminder ≤5 min of scheduled time; queue <2 s at 500 concurrent pharmacists; 99.9%
  availability during store hours. **Owned by `srs-writer`** (BR-NFR-001, BR-NFR-002,
  BR-NFR-003); stated here only as the operating condition users work within (§3), not
  re-authored as URS requirements.
- **CON-5** — Fixed team of 7; two-week sprints; Azure DevOps; first shippable slice in 3 sprints.

**Assumptions (unratified — carried from BRD, do not treat as decided):**
- **ASSUMPTION-1** *(owner: PM / acting PO)* — RxKart's PM acts as sponsor / PO. (Not a URS driver; carried for chain integrity.)
- **ASSUMPTION-2** *(owner: PM / acting PO)* — "within 2 quarters" measured from first-slice launch. (Business-metric assumption; carried.)
- **ASSUMPTION-3** *(owner: PM / acting PO)* — "on-time refill" = dispensed on or before due date. (Business-metric assumption; carried.)
- **ASSUMPTION-4** *(owner: PM / architect)* — "store hours" = union of all 40 stores' posted hours (pending OQ-1). Bounds the CON-4 availability window; not a URS requirement.
- **ASSUMPTION-5** *(owner: architect)* — Twilio (SMS) + Firebase (push) fixed; governs CON-1.

**Assumptions (new — introduced by `urs-writer`):**
- **ASSUMPTION-6** *(owner: architect / compliance officer)* — "Regulated" scope = HIPAA + DEA / state-board, **not** FDA 21 CFR Part 11 / GAMP computerized-system validation. **Determines this URS's verification depth** (AT + INSP + SEC, not IQ/OQ/PQ). **Gates this URS** (§10 FLAG).
- **ASSUMPTION-7** *(owner: QA lead / `urs-writer`)* — Because Part 11 / GAMP is out of scope (ASSUMPTION-6), verification is by acceptance/system test + inspection + security review, and audit records (URS-DAT-002, URS-DAT-003) are attributable-and-timestamped rather than full Part 11 audit trails with e-signatures. If ASSUMPTION-6 flips, this URS becomes a validated deliverable and this row is void.
- **ASSUMPTION-8** *(owner: architect / compliance officer)* — The prescription record carries an authoritative DEA-schedule classification (from the existing dispensing system) that MedRemind reads to enforce URS-SAF-001, URS-SAF-002, URS-SAF-004; and the acceptable *mechanism* of controlled-substance identity verification (URS-SEC-001) is defined downstream in the RFC / threat model (DOC-002 / DOC-004), not by this URS. The exclusion is only as trustworthy as that classification source. *(see §10 FLAG)*
- **ASSUMPTION-9** *(owner: compliance officer)* — Pending OQ-3, controlled-substance exclusion and identity-verification rules are taken to apply uniformly as DEA Schedule II–V across all 40 stores' states; per-state state-board variation is resolved and a named regulatory sign-off authority confirmed before this URS is baselined. *(see §10 FLAG)*

## 8. Traceability

Full BR↔URS mapping is written into the shared `RTM.md` (this pass fills the *User req (URS)*
column). Design-spec and validation-protocol columns are filled downstream by `srs-writer` /
`sdd-writer` / `test-plan-writer`.

| URS ID | Traces to (BRD / constraint) | Design spec | Validation / test protocol |
|---|---|---|---|
| URS-USE-001 | BR-REFILL-001, CON-1 | (srs/sdd) | (test-plan) |
| URS-USE-002 | BR-REFILL-001, CON-1 | (srs/sdd) | (test-plan) |
| URS-USE-003 | BR-REFILL-002 | (prd/srs) | (test-plan) |
| URS-USE-004 | BR-QUEUE-001 | (srs/sdd) | (test-plan) |
| URS-USE-005 | BR-QUEUE-002 | (srs/sdd) | (test-plan) |
| URS-USE-006 | BR-QUEUE-002 | (srs/sdd) | (test-plan) |
| URS-USE-007 | BR-SUB-001 | (srs/sdd) | (test-plan) |
| URS-SAF-001 | BR-CTRL-001, BR-CTRL-004 | (srs/sdd) | (test-plan) |
| URS-SAF-002 | BR-CTRL-001, BR-CTRL-004 | (srs/sdd) | (test-plan) |
| URS-SAF-003 | BR-SUB-002 | (srs/sdd) | (test-plan) |
| URS-SAF-004 | BR-CTRL-003, BR-CTRL-004 | (srs/sdd) | (test-plan) |
| URS-SEC-001 | BR-CTRL-002, BR-CTRL-004 | (srs/sdd) | (test-plan) |
| URS-DAT-001 | BR-PHI-001, BR-PHI-002, CON-2 | (srs/sdd) | (test-plan) |
| URS-DAT-002 | BR-QUEUE-002 | (srs/sdd) | (test-plan) |
| URS-DAT-003 | BR-SUB-002 | (srs/sdd) | (test-plan) |

## 9. Change control

| Version | Change | Reason | Approved by | Date |
|---|---|---|---|---|
| v0.1 | Initial URS drafted from `02-brd.md` + `01-doc-strategy.md`. | Establish user requirements as the regulated design input (DOC-003). | (pending — QA / validation lead) | 2026-07-10 |

## 10. Open items & flags

```
FLAG(security-reviewer / architect): The controlled-substance exclusion (URS-SAF-001,
URS-SAF-002, URS-SAF-004) and identity verification (URS-SEC-001) depend on TWO inputs not
routed to this agent and not on disk: (a) an authoritative DEA-schedule classification field on
the prescription record, and (b) the acceptable identity-verification MECHANISM. Both are owned
by the RFC / threat-model (DOC-002 / DOC-004), not the URS. Captured as ASSUMPTION-8. The
exclusion is only as reliable as that classification source. Please confirm the source-of-truth
field and the acceptable verification mechanism in the RFC, and feed any correction back under
change control (doc-strategy §8 requires a URS + threat-model reference before these stories
enter a sprint).
```

```
FLAG(spec-steward / compliance): Two rulings gate baselining this URS. (1) ASSUMPTION-6 —
"regulated" = HIPAA + DEA/state-board, NOT FDA 21 CFR Part 11/GAMP; this sets the verification
depth (AT+INSP+SEC, not IQ/OQ/PQ) and the audit-record rigour (ASSUMPTION-7). If Part 11 is
later ruled applicable, this URS must be re-baselined as a validated deliverable (IQ/OQ/PQ, full
audit trail + e-signatures), voiding ASSUMPTION-7 and expanding URS-SAF/-SEC/-DAT. (2) OQ-3
(open in BRD §Open questions) — which state board governs per store is unresolved; ASSUMPTION-9
assumes uniform Schedule II–V handling until it is. Please route ratification of both before the
URS is baselined.
```
