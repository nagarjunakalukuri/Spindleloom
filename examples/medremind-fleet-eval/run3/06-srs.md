# SRS: MedRemind — Prescription Refill Reminder & Approval Module

*Author: `srs-writer` (architect / tech lead) · phase: requirements · 2026-07-09 · run3*
*Upstream: `frd-writer` (`05-frd.md`), `urs-writer` (`03-urs.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Source of truth for scope: `brief.md`.*
*Downstream: `sdd-writer`/`tsd-writer`, `test-plan-writer`, `backlog-manager`, `data-modeler`, `security-reviewer`, `sre`, `performance-engineer`. RTM: `examples/medremind-fleet-eval/run3/RTM.md`.*

| Field | Value |
|---|---|
| Author | `srs-writer` (architect / tech lead) |
| Status | Draft |
| Related FRD / URS | `05-frd.md`, `03-urs.md` |
| Regulatory basis | HIPAA (PHI minimization) + DEA Schedule II–V handling. **FDA 21 CFR Part 11 / GxP NOT APPLICABLE** per ASSUMPTION-3. |
| Last updated | 2026-07-09 |

## Purpose & scope

This SRS states the **constraints and measurable targets** the MedRemind software must meet — performance, scalability, availability, security, privacy/compliance, safety-critical read behavior, data integrity/audit, and observability — for the refill loop **remind → one-tap request → pharmacist triage/decision** plus the controlled-substance exclusion and generic-substitution flows. It is the *target*, not the design: it says what the software must achieve, not how. The *how* (Twilio/Firebase pipeline topology, the concrete classification-source field, cipher/key-management, scheduler design) is owned by `sdd-writer`/`tsd-writer`/`architect`. Per `doc-strategy` DS-05 this is a **lean SRS**: it owns CON-4's quantified NFRs (which `urs-writer` deliberately deferred here) and the audit-traceable HIPAA / Schedule II–V constraint rules.

**In scope:** NFR budgets (CON-4), PHI-minimization constraints, Schedule II–V fail-closed read rules, security/authz posture, attributable-record constraints, observability targets for verifying the SLOs.
**Out of scope:** functional acceptance criteria (owned by `05-frd.md`); design/architecture (owned by SDD/TSD); payment, courier logistics, e-prescribing, non-US jurisdictions (ASSUMPTION-1), Part 11/GxP validation (ASSUMPTION-3).

## Functional constraints (software-level rules)

These are software-level *rules* (limits/guards), distinct from the functional acceptance criteria in `05-frd.md`. They constrain how the functional behavior must be realized.

| ID | Requirement ("the system shall …") | Source | Verification |
|---|---|---|---|
| SR-SAF-001 | The system shall treat a prescription's DEA-schedule classification as readable **only** when it obtains a recognized, non-null Schedule value from the authoritative classification source within a bounded read timeout; a timeout, null, unrecognized enum, or read error shall be treated as "unreadable" and the prescription excluded from all automation (fail closed). | FRD-CTL-003, URS-SAF-001, ASSUMPTION-9 | AT, INSP |
| SR-SAF-002 | The system shall reach the "automation-eligible" state only via a positively-read non-controlled classification, never as a default or fallback. | FRD-CTL-001, FRD-CTL-003, URS-SAF-001 | AT, INSP |
| SR-DAT-001 | The system shall guarantee at-most-once effect per prescription per refill-due cycle for reminder dispatch and refill-request creation, preserved across retries, redelivery, and failover (idempotency key = prescription + refill-due cycle). | FRD-RMD-006, FRD-RFL-002, FRD-RMD-007 | AT |
| SR-DAT-002 | The system shall record exactly one pharmacist decision per refill request under concurrent action, rejecting or ignoring later concurrent writes atomically. | FRD-QUE-006 | AT |

## Non-functional requirements

### Performance (SR-PERF)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-PERF-001 | The system shall dispatch a due reminder to the delivery provider within 5 minutes of its scheduled evaluation time. | ≤5 min, p99 (measured to provider hand-off — ASSUMPTION-18) | CON-4, URS-USE-001/-002, FRD-RMD-001 | load test, SLO metric |
| SR-PERF-002 | The system shall serve the pharmacist queue page within 2 seconds under 500 concurrent pharmacist sessions. | <2 s, p95 @ 500 concurrent (ASSUMPTION-19) | CON-4, URS-USE-004, FRD-QUE-001 | load test |
| SR-PERF-003 | The system shall acknowledge a one-tap refill request ("request received" state) within 2 seconds. | <2 s, p95 (ASSUMPTION-19) | FRD-RFL-004, URS-USE-003 | load test |

### Scalability (SR-SCAL)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-SCAL-001 | The system shall support the RxKart patient base and evaluate all due prescriptions across it within the SR-PERF-001 budget. | 250k MAU | brief, CON-4 | load test |
| SR-SCAL-002 | The system shall sustain concurrent pharmacist sessions chain-wide (40 stores) without breaching SR-PERF-002. | 500 concurrent | CON-4, URS §3 | load test |
| SR-SCAL-003 | The system shall complete each reminder-batch evaluation cycle within its scheduling window so no due prescription is carried past SR-PERF-001. | full daily due volume / cycle | CON-4, FRD-RMD-002 | load test |

### Reliability & availability (SR-AVL)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-AVL-001 | The system shall keep the patient refill-request and pharmacist queue functions available during defined store hours. | 99.9% (store-hours window — ASSUMPTION-16) | CON-4 | SLO metric, INSP |
| SR-AVL-002 | The system shall treat push and SMS as redundant channels so that a single-channel provider failure does not drop the reminder. | no reminder lost on single-channel failure | FRD-RMD-007, CON-1 | AT (fault injection) |
| SR-AVL-003 | The system shall recover from a component failure within the module RTO/RPO without violating the SR-DAT-001 at-most-once guarantee. | RTO ≤1 h / RPO ≤5 min (ASSUMPTION-19) | CON-4, FRD-RMD-006 | DR test |

### Security & identity (SR-SEC)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-SEC-001 | The system shall authenticate patients and pharmacists exclusively through the existing IdP, introducing no new authentication platform. | existing IdP only | ASSUMPTION-4, URS-SEC-001 | SEC, INSP |
| SR-SEC-002 | The system shall enforce role-scoped authorization: a patient may access only their own prescriptions and requests; a pharmacist may act only within their authorized store queue scope. | role/scope enforced server-side | URS-USE-004, FRD-QUE-001 | SEC, AT |
| SR-SEC-003 | The system shall require a successful identity-verification step before any Schedule II–V refill proceeds, with no automated path offered. | mandatory before proceed | URS-SEC-001, FRD-CTL-004, CON-3 | SEC, AT |
| SR-SEC-004 | The system shall encrypt PHI in transit and at rest using industry-standard mechanisms. | TLS 1.2+ in transit; AES-256 (or equiv.) at rest (ASSUMPTION-20) | CON-2, URS §6 | SEC |

### Privacy & compliance (SR-PRIV)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-PRIV-001 | The system shall exclude any drug name from every push notification field, including title, body, and lock-screen preview. | zero drug names in push | FRD-RMD-003, URS-DAT-001, CON-2 | AT, INSP, SEC |
| SR-PRIV-002 | The system shall exclude any drug name from every SMS body and every outbound patient notification (reminder, rejection, approval/ready confirmation). | zero drug names in any patient notification | FRD-RMD-004, FRD-QUE-005, FRD-CFN-001, URS-DAT-001, CON-2 | AT, INSP, SEC |
| SR-PRIV-003 | The system shall operate under HIPAA and store PHI within US data residency. | HIPAA; US residency (ASSUMPTION-1) | CON-2, URS §7 | INSP |
| SR-PRIV-004 | The system shall meet verification depth of acceptance/system test + inspection + security review, not IQ/OQ/PQ, while Part 11/GxP remains out of scope. | AT+INSP+SEC (ASSUMPTION-3, ASSUMPTION-8) | ASSUMPTION-3 | INSP |

### Data integrity & audit (SR-AUD)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-AUD-001 | The system shall persist each pharmacist decision as an attributable, timestamped, append-only audit entry identifying the acting pharmacist. | attributable + UTC-timestamped + append-only | URS-DAT-002, FRD-QUE-004/-005 | AT, INSP |
| SR-AUD-002 | The system shall persist each patient substitution acceptance as an attributable, timestamped, append-only consent record that is the dispensing precondition. | attributable + timestamped + append-only | URS-DAT-003, FRD-SUB-002 | AT, INSP |
| SR-AUD-003 | The system shall retain audit and consent records for the compliance-mandated retention period. | ≥6 years (assumed — ASSUMPTION-17) | URS §6 | INSP |

### Observability & operability (SR-OBS)

| ID | Requirement (measurable) | Target | Source | Verification |
|---|---|---|---|---|
| SR-OBS-001 | The system shall emit per-channel metrics for reminder dispatch and delivery outcome, and a delivery-latency metric sufficient to verify SR-PERF-001. | metric coverage for the SLO | CON-4, FRD-RMD-005 | INSP |
| SR-OBS-002 | The system shall alert on breach of the delivery-latency, queue-latency, and availability SLOs. | alert on SLO breach | CON-4 | INSP |
| SR-OBS-003 | The system shall provide a rollback path and runbooks for the notification pipeline. | rollback + runbook exist | doc-strategy DS-06/DS-10 | INSP |

## Interfaces & environment

- **Delivery providers:** SMS via **Twilio**; push via existing **Firebase** (CON-1). The ≤5-min budget (SR-PERF-001) is measured to provider hand-off; carrier/Firebase last-mile delivery is outside the system boundary (ASSUMPTION-18).
- **Identity:** existing IdP (SR-SEC-001, ASSUMPTION-4).
- **Authoritative DEA-schedule classification source:** the existing dispensing system's prescription record (ASSUMPTION-9). Concrete source-of-truth field and read mechanism are SDD/architect-owned — see FLAG.
- **Client surfaces:** existing RxKart mobile app (250k MAU) and existing pharmacist web portal; MedRemind adds no new platform.

## Constraints & assumptions

**Constraints (ratified — carried):** CON-1 (Twilio/Firebase), CON-2 (HIPAA, no drug names in SMS), CON-3 (Schedule II–V exclusion + identity verification), CON-4 (≤5-min delivery, <2s queue @ 500 concurrent, 99.9% store-hours availability — **owned here**), CON-5 (team of 7, 2-wk sprints, Azure DevOps, first slice in 3 sprints).

**Assumptions carried from upstream (do not re-invent; not decided):** ASSUMPTION-1 (US-only jurisdiction — `spec-steward`), ASSUMPTION-3 (HIPAA+DEA not Part 11/GxP — architect), ASSUMPTION-4 (existing IdP — PM), ASSUMPTION-8 (verification depth AT+INSP — QA lead), ASSUMPTION-9 (authoritative DEA-schedule classification source + verification mechanism — architect / compliance officer), ASSUMPTION-10/-15 (batching — PM), ASSUMPTION-11 (opt-out granularity — PM), ASSUMPTION-12 (post-approval confirmation — PM), ASSUMPTION-13 (queue order — PM/`ux-ui-designer`), ASSUMPTION-14 (substitution window — PM/`ux-ui-designer`). ASSUMPTION-2/-5/-6/-7 carried for chain integrity.

**Assumptions introduced by `srs-writer` (unratified):**
- **ASSUMPTION-16** *(owner: SRE / PM)* — The "store hours" window that SR-AVL-001's 99.9% is measured against is not yet a ratified calendar (per-store local hours vs. a single chain-wide window). The 99.9% target is fixed; the window definition is pending.
- **ASSUMPTION-17** *(owner: compliance officer)* — The retention period for attributable audit/consent records (SR-AUD-003) is not yet set; assumed ≥6 years per common HIPAA practice, pending compliance ratification.
- **ASSUMPTION-18** *(owner: SRE / architect)* — The ≤5-min reminder budget (SR-PERF-001) is measured from scheduled evaluation to successful hand-off to the provider (Twilio/Firebase). Downstream carrier/Firebase delivery latency is outside the MedRemind system boundary.
- **ASSUMPTION-19** *(owner: architect / SRE)* — The "<2s at 500 concurrent" and derived latency targets are interpreted at **p95**, and the module RTO/RPO (SR-AVL-003) is assumed RTO ≤1 h / RPO ≤5 min, pending SRE ratification.
- **ASSUMPTION-20** *(owner: security-reviewer / architect)* — Encryption specifics for SR-SEC-004 (TLS 1.2+ in transit, AES-256 at rest) are stated as HIPAA-aligned targets; the exact cipher suite and key-management are security-review/SDD-owned. (External standard not re-verified under eval isolation — WebSearch not run; tagged for security review.)

## Traceability

Rows appended to `RTM.md` *Constraint (SRS)* column this pass — atomic IDs only.

| SR ID | Traces to (FRD / URS / CON) |
|---|---|
| SR-SAF-001 | FRD-CTL-003, URS-SAF-001, ASSUMPTION-9 |
| SR-SAF-002 | FRD-CTL-001/-003, URS-SAF-001 |
| SR-DAT-001 | FRD-RMD-006, FRD-RFL-002, FRD-RMD-007 |
| SR-DAT-002 | FRD-QUE-006 |
| SR-PERF-001 | CON-4, URS-USE-001/-002, FRD-RMD-001 |
| SR-PERF-002 | CON-4, URS-USE-004, FRD-QUE-001 |
| SR-PERF-003 | FRD-RFL-004, URS-USE-003 |
| SR-SCAL-001 | brief (250k MAU), CON-4 |
| SR-SCAL-002 | CON-4, URS §3 |
| SR-SCAL-003 | CON-4, FRD-RMD-002 |
| SR-AVL-001 | CON-4 |
| SR-AVL-002 | FRD-RMD-007, CON-1 |
| SR-AVL-003 | CON-4, FRD-RMD-006 |
| SR-SEC-001 | ASSUMPTION-4, URS-SEC-001 |
| SR-SEC-002 | URS-USE-004, FRD-QUE-001 |
| SR-SEC-003 | URS-SEC-001, FRD-CTL-004, CON-3 |
| SR-SEC-004 | CON-2, URS §6 |
| SR-PRIV-001 | FRD-RMD-003, URS-DAT-001, CON-2 |
| SR-PRIV-002 | FRD-RMD-004, FRD-QUE-005, FRD-CFN-001, URS-DAT-001, CON-2 |
| SR-PRIV-003 | CON-2, URS §7, ASSUMPTION-1 |
| SR-PRIV-004 | ASSUMPTION-3, ASSUMPTION-8 |
| SR-AUD-001 | URS-DAT-002, FRD-QUE-004/-005 |
| SR-AUD-002 | URS-DAT-003, FRD-SUB-002 |
| SR-AUD-003 | URS §6, ASSUMPTION-17 |
| SR-OBS-001 | CON-4, FRD-RMD-005 |
| SR-OBS-002 | CON-4 |
| SR-OBS-003 | doc-strategy DS-06/DS-10 |

## Requirement-quality note (29148/INCOSE lint justification)

`validate_reqs.py` may flag `shall … and/or …` on SRS IDs where the conjunction is **within a single obligation**, not two bundled ones — deliberate, kept for clarity:

- **SR-SAF-001** — the `timeout, null, unrecognized, or error` clause enumerates the *failure modes of one behavior* (the fail-closed read), not multiple obligations; splitting would fragment the single "readable-only-when" rule.
- **SR-PRIV-002, SR-AUD-001/-002** — the conjunctions enumerate the *fields/attributes of one constraint* (which notifications carry no drug name; the attributes of one record), one obligation each.
- **SR-SEC-004, SR-AVL-002/-003, SR-OBS-*** — `in transit and at rest`, `push and SMS`, `RTO/RPO`, latency/queue/availability lists each scope one target; not separable obligations.
- **Incidental-conjunction class (SR-SEC-001/-002, SR-SCAL-001, SR-PRIV-001/-003, SR-DAT-001/-002, SR-AVL-001, SR-AUD-003, SR-OBS-001/-002)** — the flagged `and`/`or` is a *compound subject or scope* inside one obligation ("patients and pharmacists", "audit and consent records", "in transit and at rest", "HIPAA and US residency", "reminder dispatch and delivery outcome"), not two obligations. The heuristic matches any `and`/`or` on the line; each of these is singular and verifiable as written.

The remaining findings on `06-srs.md` are upstream **FRD-*/URS-*/PRD-*** IDs *cited* here in the source/trace columns — owned by `frd-writer`/`urs-writer`/`prd-writer`, not authored in this SRS.

## Flags

```
FLAG(architect): SR-SAF-001 fixes the *constraint-level* detectable signal for FRD-CTL-003's
"missing or unreadable" classification — readable only on a recognized, non-null DEA-schedule
value obtained within a bounded read timeout; anything else fails closed. This answers the read
boundary the FRD/URS/PRD architect FLAG deferred to the SRS/SDD (ASSUMPTION-9). Still yours to
define in the SDD: the concrete source-of-truth field on the dispensing-system prescription
record, the read mechanism, and the specific timeout value. No new dependency — the intent is
fixed here; the mechanism is design-owned.
```

```
FLAG(sre): SR-AVL-001 (99.9% store-hours) needs a ratified "store hours" window (ASSUMPTION-16),
SR-AVL-003 needs RTO/RPO ratification (ASSUMPTION-19), and SR-PERF-001's measurement point
(provider hand-off, ASSUMPTION-18) needs SRE confirmation before these SLOs are testable.
```
