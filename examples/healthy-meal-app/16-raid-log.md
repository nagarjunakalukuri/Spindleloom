# RAID Log — FreshDesk

| Field | Value |
|---|---|
| Owner | PM |
| Status | Living |
| Last updated | 2026-06-25 |

> Worked example — produced by `raid-log`. One owner + next action per item; Decisions link to ADRs. Overview depth.

## Risks
| ID | Risk | Prob × Impact | Owner | Mitigation / next action |
|---|---|---|---|---|
| R1 | Payment-provider latency breaches the order-confirm target (SR-FUNC-004) | M × H | Lead | Timeout + retry + idempotency; load test added to DoD (retro A2) |

## Assumptions
| ID | Assumption | Owner | Validate by |
|---|---|---|---|
| A1 | Nightly menu refresh keeps stock fresh enough for checkout (SR-FUNC-002) | PM | Confirm with ops before Sprint 2 |

## Issues
| ID | Issue | Owner | Next action |
|---|---|---|---|
| I1 | FRD-FILT-002 multi-filter behavior underspecified — caused `PBI-FILT-002` slip | BA | Tighten AC (retro A1) before re-pull |

## Decisions
| ID | Decision | Where |
|---|---|---|
| D1 | Event-driven delivery tracking (vs polling) | ADR-0001 (`08-adr-0001-event-driven-tracking.md`) |
