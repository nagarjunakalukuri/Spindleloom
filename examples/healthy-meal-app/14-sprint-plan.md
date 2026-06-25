# Sprint 1 Plan — FreshDesk

| Field | Value |
|---|---|
| Owner | PM (acting PO) |
| Status | Active |
| Last updated | 2026-06-11 |

> Worked example — produced by `sprint-planner` from `12-backlog.md` + `13-estimation.md`. 2-week sprint, ~24-pt capacity. Overview depth.

## Sprint goal
**A diner can filter the menu by diet and place a paid order; the event-driven tracking backend is ready so live ETA can ship next sprint.**

## Sprint backlog (24 / 24 pts)
| Order | PBI | Pts | Why this sprint |
|---|---|---|---|
| 1 | `PBI-TRK-BE-001` | 8 | enabler — unblocks `PBI-TRK-001` next sprint; architecture-significant, do early |
| 2 | `PBI-ORD-001` | 8 | core revenue path |
| 3 | `PBI-FILT-001` | 5 | core product value |
| 4 | `PBI-FILT-002` | 3 | completes the filtering story |

## Deferred to Sprint 2
`PBI-ORD-002` (5), `PBI-TRK-001` (5, now unblocked), `PBI-FAV-001` (3) — 13 pts, fits next capacity.

## Risks flagged at planning
- Payment-provider latency could breach the order-confirm target (SR-FUNC-004) → see `16-raid-log.md` R1; load-test in this sprint.
- `PBI-FILT-002` multi-filter behavior is thinly specified (FRD-FILT-002) → RAID I1; confirm AC before pulling.
