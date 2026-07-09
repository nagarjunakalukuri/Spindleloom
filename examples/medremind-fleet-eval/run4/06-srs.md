# SRS: MedRemind — Software Constraints & NFRs (DOC-002 §Constraints & NFRs)

*Author: `srs-writer` (tech lead / architect hat) · phase: requirements · 2026-07-10 · run4*
*Upstream: `frd-writer` (`05-frd.md`), `urs-writer` (`03-urs.md`), `prd-writer` (`04-prd.md`), `doc-strategy-advisor` (`01-doc-strategy.md`). Scope source of truth: `brief.md`.*
*Downstream: `sdd-writer`/`tsd-writer` (design must satisfy these), `test-plan-writer` (QA derives scripts from the Verification column), `security-reviewer` (DOC-004), `sre`, `performance-engineer`, `backlog-manager`. RTM: `examples/medremind-fleet-eval/run4/RTM.md`.*
*Register id: this is the **Constraints & NFRs section of DOC-002** (the Lean RFC that merges SRS + SDD + TSD — doc-strategy §3/§4). It is the SR-constraint layer only; the reminder-scheduler, queue API, integration, and data-model design that satisfy these targets are the `sdd-writer`/`tsd-writer` sections of the same RFC. Kept proportionally lean per CON-5 (6-week / 3-sprint clock).*

| Field | Value |
|---|---|
| Author | `srs-writer` |
| Status | Draft |
| Related PRD/FRD/URS | `04-prd.md`, `05-frd.md`, `03-urs.md` |
| Last updated | 2026-07-10 |

## Purpose & scope

Measurable, verifiable **technical constraints** — the targets the MedRemind software must hit, not the architecture that hits them — for notification delivery, queue performance, availability/recovery, PHI security, provider integration, audit durability, data integrity, and observability. This section owns **CON-4** (the three quantified NFRs the brief stated and the URS deferred to `srs-writer`: BR-NFR-001 ≤5-min reminder delivery, BR-NFR-002 <2 s queue at 500 concurrent pharmacists, BR-NFR-003 99.9% availability during store hours) plus the **retry-count and SLA arithmetic the FRD explicitly handed back to `srs-writer`** (`05-frd.md` note under §1: "Retry counts and the ≤5-min SLA arithmetic are NFR realisation — owned by `srs-writer` (CON-4)"). Functional behaviour (FRD/PBIs) and the design/data-model (SDD/TSD sections of DOC-002) are **out of scope here**. Every SR ID below is appended to `RTM.md` in this pass.

## FLAG & assumptions (read first)

- **FLAG(prd-writer / PM):** the **measurement boundary** of BR-NFR-001 ("reminder delivered within 5 minutes of scheduled time") is undefined upstream. "Delivered" is a business-metric definition owned by the BRD/PRD, and SMS/push delivery *confirmation* is asynchronous and outside our control (the carrier / device decides when a message lands). I bind the ≤5-min SLA to **provider-accepted handoff** (the point Twilio/Firebase accept the send), at **≥99% of reminders per calendar month** — the percentile is also my addition; the brief states no percentile, so a single late send would otherwise fail a literal 100% reading. Proceeding on **ASSUMPTION-15**; needs PM/architect ratification. This materially changes what QA tests and what SRE alerts on.
- **Send-window dependency (not mine to own):** SR-PERF-001 measures the ≤5-min SLA from *eligible fire time*, which for an out-of-window due moment is the next send-window open (08:00–20:00 patient-local), per **ASSUMPTION-13 / OQ-7**. That window is owned by `ux-ui-designer` + compliance (FRD FLAG), not by this SRS. I consume it; I do not ratify it. If the window changes, SR-PERF-001's clock-start changes, the ID does not.
- **Store-hours dependency:** SR-AVL-001's availability window is "store hours" per **ASSUMPTION-4** (union of all 40 stores' posted hours, pending OQ-1) — owned by PM/architect. Consumed, not re-authored.
- **Identity-verification mechanism (not mine):** SR-SEC-006 constrains only the *record* ("a successful identity verification is recorded before the refill proceeds"); the *mechanism* is owned by the threat model (DOC-004, ASSUMPTION-8, `security-reviewer`).

New assumptions introduced by `srs-writer` (unratified — do not treat as decided):
- **ASSUMPTION-15** *(owner: PM / architect)* — BR-NFR-001 "delivered ≤5 min" is measured to **provider-accepted handoff**, at **≥99% per calendar month**, with the clock starting at eligible fire time (ASSUMPTION-13). Governs SR-PERF-001, SR-CAP-001, SR-REL-001.
- **ASSUMPTION-16** *(owner: architect)* — peak reminder volume is **≤50,000 sends/day** (rough envelope from 250k MAU and typical refill cadence). Governs SR-CAP-001. `performance-engineer` to confirm against real refill-due distribution.
- **ASSUMPTION-17** *(owner: PM)* — reminders missed during a service outage are delivered **within 30 min of service restoration** (the ≤5-min SLA is suspended for the outage window). Governs SR-REL-002; interacts with BR-NFR-001 — PM to confirm the carve-out.
- **ASSUMPTION-18** *(owner: compliance officer)* — pharmacist-portal idle-session timeout is **15 min** (shared-workstation environment, URS §3). Governs SR-SEC-005.
- **ASSUMPTION-19** *(owner: compliance officer)* — audit records are retained **≥6 years** (HIPAA §164.316(b)(2) baseline; state-board rules may extend, ASSUMPTION-9). Governs SR-AUD-003.

Carried unratified upstream: **ASSUMPTION-1..ASSUMPTION-14** (see `02-brd.md`, `03-urs.md`, `05-frd.md`) — including the Twilio/Firebase channel fix (ASSUMPTION-5), the DEA-classification source and identity-verification mechanism (ASSUMPTION-8), the fail-closed default (ASSUMPTION-14), and the send window (ASSUMPTION-13). Do not treat as decided.

## Constraints (ratified, carried)

- **CON-1** — SMS via Twilio; push via existing Firebase (ASSUMPTION-5). Governs SR-INT-001, SR-INT-002.
- **CON-2** — HIPAA applies; no drug names in SMS content. Governs SR-PHI-001.
- **CON-3** — Schedule II–V: no auto-reminder, no one-tap; identity verification + pharmacist-initiated contact. Behavioural gate is the FRD's; SR-SEC-006 constrains the verification record.
- **CON-4** — reminder ≤5 min; queue <2 s at 500 concurrent pharmacists; 99.9% availability during store hours. **Owned here** as SR-PERF-001/002 and SR-AVL-001.
- **CON-5** — fixed team of 7; two-week sprints; Azure DevOps; first shippable slice in 3 sprints. Bounds SRS scope depth (lean).

## Non-functional / constraint requirements

Each row states **one** obligation; conditions in parentheses scope it — they are not additional obligations. "Verification" is what `test-plan-writer` turns into a test protocol.

### Performance & capacity
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-PERF-001 | The system shall hand each fired reminder to its channel provider within 5 minutes of the reminder's eligible fire time, for at least 99% of reminders per calendar month (eligible fire time = the scheduled due moment; when that moment falls outside the 08:00–20:00 send window it is the next window open, per ASSUMPTION-13; measurement to provider-accepted handoff, per ASSUMPTION-15). | ≤300 s, ≥99%/month | BR-NFR-001, CON-4, FRD-RMD-001, FRD-RMD-008 | Load test + production latency SLI |
| SR-PERF-002 | The system shall render the pharmacist queue page within 2 seconds at the 95th percentile under 500 concurrent pharmacist sessions. | p95 <2 s @500 concurrent | BR-NFR-002, CON-4, FRD-QUE-001, URS-USE-004 | Load test |
| SR-CAP-001 | The system shall sustain the peak daily reminder volume (ASSUMPTION-16: ≤50,000 sends/day) without breaching SR-PERF-001. | ≤50k sends/day | brief (250k MAU), CON-4, FRD-RMD-001 | Load test |

### Availability & recovery
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-AVL-001 | The system shall maintain at least 99.9% monthly availability of its user-facing surfaces (patient refill-request path, pharmacist queue) during store hours (store hours per ASSUMPTION-4). | ≥99.9%/month, store hours | BR-NFR-003, CON-4 | Uptime monitoring report |
| SR-REL-001 | The system shall retry a failed reminder send on the same channel up to 3 times within the 5-minute SLA window before that channel is declared failed for the send. | ≤3 in-window retries | FRD-RMD-007, FRD-RMD-008, BR-NFR-001 | Fault-injection test |
| SR-REL-002 | The system shall deliver every reminder missed during a service outage within 30 minutes of service restoration (ASSUMPTION-17). | ≤30 min post-restore | FRD-RMD-001, BR-NFR-001 | Fault-injection test |

### Security & identity
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-SEC-001 | The system shall encrypt all PHI in transit using TLS 1.2 as the minimum version on every external interface (app, portal, Twilio, Firebase). | TLS ≥1.2, 100% interfaces | URS-DAT-001, brief (HIPAA) | Config inspection + scan |
| SR-SEC-002 | The system shall encrypt all PHI at rest using AES-256 as the minimum-strength algorithm. | AES-256, 100% PHI stores | brief (HIPAA) | Config inspection |
| SR-SEC-003 | The system shall return pharmacist-queue data only for requests belonging to the authenticated pharmacist's affiliated store. | 0 cross-store rows | FRD-QUE-001, URS-USE-004 | Authorization test |
| SR-SEC-004 | The system shall attribute every recorded queue decision to an individually authenticated pharmacist account (shared/service accounts not accepted for decision actions). | 100% decisions attributed | FRD-QUE-004, FRD-QUE-006, URS-DAT-002 | Test |
| SR-SEC-005 | The system shall terminate an idle pharmacist-portal session after 15 minutes of inactivity (ASSUMPTION-18; shared-workstation environment, URS §3). | ≤15 min idle | URS §3, brief (HIPAA) | Test |
| SR-SEC-006 | The system shall record a successful identity verification against a controlled-substance refill before that refill proceeds on the manual path (verification mechanism owned by DOC-004, ASSUMPTION-8). | 100% controlled refills gated | FRD-CTRL-004, URS-SEC-001, CON-3 | Test + security review (SEC) |

### PHI minimisation in notification content
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-PHI-001 | The system shall compose every outbound SMS body from the PHI-minimised template, carrying zero PHI terms in the body (no drug name, no prescriber, no diagnosis). | 0 PHI terms/SMS | FRD-PHI-001, FRD-PHI-002, URS-DAT-001, CON-2 | Automated content check per release + send-log sampling |
| SR-PHI-002 | The system shall compose every outbound push-notification body without any PHI, including its lock-screen preview. | 0 PHI/push | FRD-PHI-004, PRD-PHI-001 | Automated payload check |
| SR-PHI-003 | The system shall send production SMS only under an executed Twilio Business Associate Agreement. | BAA executed before go-live | brief (HIPAA/Twilio), URS-DAT-001 | Contract inspection |

### Integration constraints (Twilio / Firebase)
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-INT-001 | The system shall pace outbound SMS to stay within the Twilio account's configured messages-per-second cap, queueing excess sends rather than dropping them. | 0 sends dropped at cap | brief (Twilio), CON-1, FRD-RMD-007 | Load test |
| SR-INT-002 | The system shall keep every Firebase Cloud Messaging push payload free of any PHI field, because FCM is not covered by a HIPAA BAA. | 0 PHI fields in FCM | brief (Firebase/HIPAA), CON-1, FRD-PHI-004 | Automated payload check |
| SR-INT-003 | The system shall record the provider delivery status (accepted / failed) for every send attempt on any channel, keyed to that attempt. | 100% sends statused | FRD-RMD-008 | Test |

### Data integrity & concurrency
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-DAT-001 | The system shall enforce at most one open refill request per prescription at the data layer. | 1 open request/Rx | FRD-RFL-002 | Concurrency test |
| SR-DAT-002 | The system shall commit at most one decision per refill request, rejecting a second concurrent decision atomically. | 1 decision/request | FRD-QUE-007, URS-DAT-002 | Concurrency test |

### Auditability
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-AUD-001 | The system shall store every audit record append-only, exposing no mutation path through any surface (application, API). | 0 mutation paths | URS-DAT-002, URS-DAT-003, FRD-QUE-004 | Test + code inspection |
| SR-AUD-002 | The system shall commit each audit record in the same transaction as the event it records. | 0 events unrecorded | FRD-QUE-004, FRD-QUE-006, FRD-SUB-004 | Fault-injection test |
| SR-AUD-003 | The system shall retain every audit record for at least 6 years from its creation (ASSUMPTION-19). | ≥6 years | brief (HIPAA/DEA), URS-DAT-002 | Retention-policy inspection |
| SR-AUD-004 | The system shall return the audit records matching any supported query key (request ID, pharmacist ID, date range). | 100% recall on corpus | URS-DAT-002, FRD-QUE-004 | Test |

### Observability
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-OBS-001 | The system shall emit a service-level indicator for each of reminder-delivery latency, queue-page latency, availability, sufficient to evaluate SR-PERF-001, SR-PERF-002, SR-AVL-001 monthly. | 3 SLIs live at go-live | derived from SR-PERF-001/002, SR-AVL-001 | Dashboard inspection |
| SR-OBS-002 | The system shall raise an operational alert to on-call SRE when a reminder records a delivery-failure event across all enabled channels. | alert on all-channel failure | FRD-RMD-008 | Fault-injection test |

## Interfaces & environment

- **Twilio Programmable Messaging (SMS)** — HIPAA handling requires an executed BAA (SR-PHI-003). The BAA may require a paid Twilio edition; flagged to PM as a possible cost/scope item against the BRD budget assumption (feedback loop). *(Live Twilio-HIPAA confirmation was not performed in this offline eval; SR-PHI-003 is stated from the HIPAA obligation, not a live vendor check — architect to verify current Twilio HIPAA eligibility before go-live.)*
- **Firebase Cloud Messaging (push, existing setup)** — not covered by a HIPAA BAA; hence the PHI-free payload constraint SR-INT-002.
- **User surfaces** — existing patient app (iOS/Android) and existing pharmacist web portal on shared store workstations. No new hardware (brownfield module, doc-strategy §1).

## Constraints & assumptions (tagged, unratified until signed off)

- New (owned by `srs-writer`): ASSUMPTION-15 (5-min measured to provider-accepted handoff, ≥99%/month — PM/architect), ASSUMPTION-16 (peak ≤50k sends/day — architect), ASSUMPTION-17 (30-min post-outage catch-up — PM), ASSUMPTION-18 (15-min portal idle timeout — compliance), ASSUMPTION-19 (≥6-year audit retention — compliance).
- Consumed, not owned: ASSUMPTION-13 (send window — `ux-ui-designer`/compliance), ASSUMPTION-4 (store hours — PM/architect), ASSUMPTION-8 (DEA-classification source + verification mechanism — architect/compliance), ASSUMPTION-14 (fail-closed default — `security-reviewer`).

## Feedback loop (flagged back upstream)

- To **`prd-writer` / PM** — ratify the BR-NFR-001 measurement boundary + percentile (ASSUMPTION-15) and the post-outage carve-out (ASSUMPTION-17); both change what QA verifies and what SRE alerts on.
- To **`sdd-writer` / architect** — SR-REL-001 (≤3 in-window retries) and SR-INT-001 (Twilio pacing) together bound the reminder-scheduler design inside the 5-min budget; the Twilio BAA edition is a possible cost item.
- To **`security-reviewer` (DOC-004)** — SR-SEC-006 constrains the identity-verification *record*; confirm the acceptable *mechanism* (ASSUMPTION-8) before PBI-CTRL-003 clears DoR.

## Traceability

SR rows are appended to `RTM.md` — the *Constraint (SRS)* column (per-business-goal) plus a per-ID *SRS constraint decomposition* section. Upstream sources are in each row's Source column (brief NFRs, CON-*, BR-NFR-*, FRD-*, URS-*). Downstream: `sdd-writer`/`tsd-writer` (design must satisfy these), `test-plan-writer` (test protocols derive from the Verification column).
