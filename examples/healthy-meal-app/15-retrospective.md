# Sprint 1 Retrospective — FreshDesk

| Field | Value |
|---|---|
| Owner | Lead (facilitator) |
| Status | Closed |
| Last updated | 2026-06-25 |

> Worked example — produced by `retrospective-facilitator`, grounded in Sprint 1 data (`14-sprint-plan.md`). Blameless; Start / Stop / Continue → owned action items. Overview depth.

## Sprint 1 outcome
Committed 24 pts; completed 21 (`PBI-FILT-002` slipped — multi-filter AC churned mid-sprint). Tracking enabler (`PBI-TRK-BE-001`) shipped, unblocking Sprint 2.

## Start / Stop / Continue
- **Start:** load-testing the payment path in the same sprint we build it (latency surprised us late).
- **Stop:** pulling stories whose AC isn't settled — `PBI-FILT-002` churned because FRD-FILT-002 was thin.
- **Continue:** backend-first enabler PBIs — scheduling `PBI-TRK-BE-001` first kept the tracking UI unblocked.

## Action items (owned, tracked into Sprint 2)
| ID | Action | Owner | Trace |
|---|---|---|---|
| A1 | Tighten FRD-FILT-002 multi-filter behavior before re-pulling `PBI-FILT-002` | BA | RAID I1 |
| A2 | Add a payment-latency load test to the Definition of Done | Lead | RAID R1 |
