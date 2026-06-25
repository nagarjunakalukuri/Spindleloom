# RTM: FreshDesk — Requirements Traceability Matrix

> Worked example. The single chain tying business intent down to tests, per `BEST-PRACTICES.md`. This is the artifact that proves nothing was dropped and shows the blast radius of any change.

| Business goal (BRD) | Product story (PRD) | Functional req (FRD) | Software req (SRS) | Design (SDD) | Build / test (TSD) |
|---|---|---|---|---|---|
| Healthy choice is fastest | #1 Filter by diet | FRD-FILT-001/002 | SR-FUNC-001, perf<200ms | Menu Service §3 | filter endpoint, unit ≥80% |
| 3+ orders/user/week | #2 Order & pay | FRD-ORD-001/002 | SR-FUNC-004 (order), SR-FUNC-002 (stock) | Order Service §3 | `POST /api/v1/orders`, E2E payment-decline |
| Know when meal arrives | #3 Live tracking | FRD-TRK-001 | SR-FUNC-003 (5s) | Tracking Service §4 + ADR-0001 | `GET /api/v1/orders/{id}/tracking`, integration |
| Retention / stickiness | #4 Favorites & reorder | FRD-FAV-001 | — | Favorites (data model) | Favorite entity, unit |

## How to read this
- **Across a row:** one business goal traced through every altitude down to the test that verifies it.
- **Coverage check:** every FRD/SRS requirement should appear here; an empty downstream cell is a gap.
- **Change impact:** to change tracking, follow the row — it touches PRD #3, FRD-TRK-001, the Tracking Service, ADR-0001, and the tracking endpoint/tests.

## Backlog trace (delivery)
Each PBI from `12-backlog.md` traced to the requirement it implements — extends the chain into the delivery layer (`backlog-manager` → `estimation-facilitator` → `sprint-planner`).

| Backlog item (PBI) | Product story | Functional req | Software req | Sprint |
|---|---|---|---|---|
| PBI-FILT-001 | #1 Filter by diet | FRD-FILT-001 | SR-FUNC-001 | 1 |
| PBI-FILT-002 | #1 Filter by diet | FRD-FILT-002 | — | 1 |
| PBI-ORD-001 | #2 Order & pay | FRD-ORD-001 | SR-FUNC-004 | 1 |
| PBI-ORD-002 | #2 Order & pay | FRD-ORD-002 | SR-FUNC-002 | 2 |
| PBI-TRK-BE-001 | #3 Live tracking | — | SR-FUNC-003 (ADR-0001) | 1 |
| PBI-TRK-001 | #3 Live tracking | FRD-TRK-001 | — | 2 |
| PBI-FAV-001 | #4 Favorites & reorder | FRD-FAV-001 | — | 2 |

## Decisions
| ID | Decision | Where |
|---|---|---|
| ADR-0001 | Event-driven tracking | 08-adr-0001-event-driven-tracking.md |
