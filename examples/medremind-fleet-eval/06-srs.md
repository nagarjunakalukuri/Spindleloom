# SRS: MedRemind — Refill Reminder & Approval Module

| Field | Value |
|---|---|
| Author | srs-writer (tech lead / architect hat) |
| Status | Draft |
| Related PRD/FRD | `04-prd.md`, `05-frd.md`; URS `03-urs.md` |
| Last updated | 2026-07-09 |

## Purpose & scope
Measurable technical constraints (targets, not architecture) for the MedRemind module: notification delivery, queue performance, availability, PHI security, provider-integration limits, and audit durability. Excludes the design that satisfies them (SDD/TSD) and functional behavior (FRD). Each ID below is appended to `RTM.md` in this pass.

## Requirements
Each row states one obligation; conditions in parentheses scope it, they are not additional obligations.

### Performance & capacity
| ID | Requirement ("the system shall …") | Target | Source | Verification |
|---|---|---|---|---|
| SR-PERF-001 | The system shall hand each fired reminder to its channel provider (Twilio or Firebase) within 5 minutes of its scheduled fire time, for ≥99% of reminders per calendar month (measurement boundary + percentile: ASSUMPTION-16). | ≤300 s, ≥99%/month | brief NFR; FRD-REM-002/003 | Load test + production latency metric |
| SR-PERF-002 | The system shall render the pharmacist queue page in <2 s at the 95th percentile under 500 concurrent pharmacist sessions. | p95 <2 s @500 concurrent | brief NFR; FRD-QUE-001 | Load test |
| SR-PERF-003 | The system shall sustain the peak daily reminder batch (ASSUMPTION-17: 40,000/day) without breaching SR-PERF-001. | 40k reminders/day | brief (250k MAU); FRD-REM-001 | Load test |

### Availability & recovery
| ID | Requirement | Target | Source | Verification |
|---|---|---|---|---|
| SR-AVL-001 | The system shall achieve ≥99.9% availability of the refill-request API and pharmacist queue during store hours (ASSUMPTION-18: 08:00–21:00 store-local), measured monthly. | 99.9%/month, store hours | brief NFR; FRD-REF-001, FRD-QUE-001 | Uptime monitoring report |
| SR-AVL-002 | The system shall send every reminder missed during an outage within 30 minutes of service restoration (ASSUMPTION-19). | ≤30 min after recovery | FRD-REM-001; brief NFR (5-min window) | Fault-injection test |

### Security & PHI (HIPAA minimum-necessary, 45 CFR §164.502(b))
| ID | Requirement | Target | Source | Verification |
|---|---|---|---|---|
| SR-SEC-001 | The system shall encrypt all PHI in transit using TLS 1.2 or higher on every interface (app, portal, Twilio, Firebase). | TLS ≥1.2, 100% of interfaces | URS-PHI-001/002; brief (HIPAA) | Configuration inspection + scan |
| SR-SEC-002 | The system shall encrypt all stored PHI at rest using AES-256 or an equivalent-strength algorithm. | AES-256, 100% of PHI stores | brief (HIPAA) | Configuration inspection |
| SR-SEC-003 | The system shall return queue data only for requests belonging to the authenticated pharmacist's affiliated store. | 0 cross-store rows | FRD-QUE-001; URS-QUE-001 (ASSUMPTION-7) | Authorization test |
| SR-SEC-004 | The system shall attribute every queue decision to an individually authenticated pharmacist account, with shared or service accounts rejected for decision actions. | 100% of decisions attributed | FRD-AUD-001; URS-AUD-001 | Test |
| SR-SEC-005 | The system shall terminate an idle pharmacist portal session after 15 minutes of inactivity (ASSUMPTION-20; shared-workstation environment per URS §3). | ≤15 min idle | URS §3; brief (HIPAA) | Test |
| SR-PHI-001 | The system shall compose 100% of outbound SMS and push payloads from the minimized template (ASSUMPTION-10), with zero occurrences of drug name, diagnosis, or prescriber. | 0 PHI terms per message | FRD-PHI-001; URS-PHI-001/002 | Automated content check per release + send-log sampling |
| SR-PHI-002 | The system shall send production SMS only under an executed Twilio Business Associate Agreement (requires Twilio Security/Enterprise edition — see Interfaces). | BAA executed before go-live | brief (HIPAA, Twilio); URS-PHI-001 | Contract inspection |

### Integration constraints (Twilio / Firebase)
| ID | Requirement | Target | Source | Verification |
|---|---|---|---|---|
| SR-INT-001 | The system shall pace outbound SMS at or below the Twilio account's configured messages-per-second cap, queueing (not dropping) excess sends. | 0 sends dropped at cap | brief (Twilio); FRD-REM-003 | Load test |
| SR-INT-002 | The system shall keep every push payload PHI-free, because Firebase Cloud Messaging is not HIPAA-eligible and is outside any BAA. | 0 PHI fields in FCM payloads | brief (Firebase, HIPAA); FRD-PHI-001 | Automated payload check |
| SR-INT-003 | The system shall record the provider delivery status (accepted/failed) for every SMS and push send, keyed to the send attempt. | 100% of sends statused | FRD-REM-005 | Test |

### Auditability (controlled substances + queue decisions)
| ID | Requirement | Target | Source | Verification |
|---|---|---|---|---|
| SR-AUD-001 | The system shall store audit records append-only, exposing no update or delete operation for them in any application or API path. | 0 mutation paths | FRD-AUD-001/002; URS-AUD-001/002 | Test + code inspection |
| SR-AUD-002 | The system shall commit each audit record in the same transaction as the decision or verification event it records. | 0 events without a record | FRD-AUD-001/002/003 | Fault-injection test |
| SR-AUD-003 | The system shall retain audit records for ≥6 years from creation (ASSUMPTION-21: HIPAA §164.316(b)(2) baseline; state-board rules may extend). | ≥6 years | URS-AUD-001/002; brief (HIPAA/DEA) | Retention-policy inspection |
| SR-AUD-004 | The system shall return the audit records matching a query by request ID, pharmacist ID, or date range. | 100% recall on test corpus | URS-AUD-001/002; FRD-AUD-002 | Test |

### Observability
| ID | Requirement | Target | Source | Verification |
|---|---|---|---|---|
| SR-OBS-001 | The system shall emit metrics for reminder-delivery latency, queue-page latency, and availability, sufficient to evaluate SR-PERF-001/002 and SR-AVL-001 monthly. | 3 SLIs live at go-live | Derived from SR-PERF/AVL | Dashboard inspection |

## Interfaces & environment
- **Twilio Programmable Messaging** (SMS): HIPAA-eligible under a signed BAA on Security/Enterprise edition — verified 2026-07-09 ([Twilio HIPAA](https://www.twilio.com/en-us/hipaa), [Twilio BAA changelog](https://www.twilio.com/en-us/changelog/programmable-voice--sip--and-sms-are-now-hipaa-eligible)). Edition upgrade may carry cost — flagged to PM.
- **Firebase Cloud Messaging** (push, existing setup): not HIPAA-eligible; no BAA covers it ([Firebase HIPAA coverage](https://www.accountablehq.com/post/is-firebase-hipaa-compliant-baa-covered-services-and-how-to-use-it-safely)) — hence SR-INT-002.
- Patient app (iOS/Android, existing) and pharmacist portal (web, shared store workstations) are the only user surfaces; no new hardware.

## Constraints & assumptions (practice 8 — tagged, unratified until signed off)
- Carried: ASSUMPTION-2, -5, -6 (BRD); -7, -9, -10 (URS); -14 (FRD). Schedule II–V verification *method* still open (compliance/architect) — SR-AUD-002/004 constrain its records regardless of method.
- New: **ASSUMPTION-16** (5-min window measured to provider-accepted handoff, ≥99%/month — owner: PM + architect); **ASSUMPTION-17** (peak 40k reminders/day — owner: architect); **ASSUMPTION-18** (store hours = 08:00–21:00 store-local — owner: PM); **ASSUMPTION-19** (30-min post-outage catch-up — owner: PM); **ASSUMPTION-20** (15-min portal idle timeout — owner: compliance officer); **ASSUMPTION-21** (6-year audit retention — owner: compliance officer).
- Feedback upstream: Twilio BAA edition requirement is a possible cost/scope item for the BRD budget assumption (ASSUMPTION-4); SR-AVL-002 interacts with the 5-min NFR — PM should confirm the outage carve-out.

## Traceability
SR rows appended to [`RTM.md`](RTM.md) "Constraint (SRS)" column in this pass. Upstream: brief NFRs, FRD-*, URS-* as per Source column. Downstream: sdd-writer (design must satisfy these), test-plan-writer (QA scripts derive directly from Verification column).
