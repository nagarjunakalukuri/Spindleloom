# Estimation & Capacity — FreshDesk

| Field | Value |
|---|---|
| Owner | Lead (facilitator) |
| Status | Living |
| Last updated | 2026-06-11 |

> Worked example — produced by `estimation-facilitator` via Planning Poker (modified Fibonacci) over `12-backlog.md`. Anchor story: `PBI-FILT-001` = 5. Overview depth.

## Story points (consensus)
| PBI | Points | Note |
|---|---|---|
| `PBI-FILT-001` | 5 | anchor |
| `PBI-FILT-002` | 3 | small variation on FILT-001 |
| `PBI-ORD-001` | 8 | payment integration + idempotency (SR-FUNC-004) |
| `PBI-ORD-002` | 5 | stock check at checkout |
| `PBI-TRK-BE-001` | 8 | event pipeline; architecture-significant (ADR-0001) |
| `PBI-TRK-001` | 5 | UI on top of the BE enabler |
| `PBI-FAV-001` | 3 | CRUD + reorder |

No story ≥ 13 (none needs splitting). **Backlog total: 37 pts.**

## Velocity & capacity
- **Velocity assumption:** ~24 pts/sprint (no history yet → start conservative; recalibrate after Sprint 1).
- **Sprint 1 capacity:** 5 devs × 8 working days (one dev out 2 days) ≈ 24 pts.
- **Forecast:** the 37-pt backlog spans ~2 sprints; tracking UI (`PBI-TRK-001`) lands Sprint 2 once its enabler ships in Sprint 1.
