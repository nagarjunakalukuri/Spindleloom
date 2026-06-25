# SRS: FreshDesk

| Field | Value |
|---|---|
| Author | Tech lead |
| Status | Approved |
| Related PRD/FRD | 03-prd.md / 04-frd.md |
| Last updated | 2026-06-11 |

> Worked example — overview depth. Produced by `srs-writer`. The *target* the design must hit.

## Purpose & scope
Technical constraints for the FreshDesk mobile app + backend. Excludes the logistics partner's internal systems.

## Functional requirements (software-level)
| ID | Requirement | Source | Verification |
|---|---|---|---|
| SR-FUNC-001 | The system shall persist user dietary preferences across sessions and devices | FRD-FILT-001 | integration test |
| SR-FUNC-002 | The system shall reflect stock changes in the menu within 5 s | FRD-ORD-002 | integration test |
| SR-FUNC-003 | The system shall update displayed driver location and ETA within 5 s of a new logistics event | FRD-TRK-001 | integration test |
| SR-FUNC-004 | The system shall create an order and return its ID and ETA only after the payment provider authorizes payment | FRD-ORD-001 | integration test |

## Non-functional requirements
| Category | Requirement | Target | Verification |
|---|---|---|---|
| Performance | menu p95 load | < 1.0 s; filter re-render < 200 ms | load test |
| Scalability | concurrent users at launch | 20,000 | load test |
| Reliability | uptime | 99.9% | monitoring |
| Security | auth + payment data | OAuth2 + MFA; PCI-DSS scope isolated | pentest |
| Accessibility | conformance | WCAG 2.1 AA | audit |
| Compliance | personal data | GDPR | review |
| Observability | tracing/metrics/logs | all order flows traced | review |
| Operability | alerting + rollback | one-click rollback; SLO alerts | drill |

## Interfaces & environment
Payments provider API; logistics partner location API (live driver feed); iOS + Android clients.

## Constraints & assumptions
Logistics partner provides ≤ 5 s location updates; payment provider handles PCI scope.

## Traceability
See `RTM.md`.
