# Product Backlog — FreshDesk

| Field | Value |
|---|---|
| Owner | PM (acting PO) |
| Status | Living |
| Last updated | 2026-06-11 |

> Worked example — produced by `backlog-manager` from the PRD (`03-prd.md`) and FRD (`04-frd.md`), INVEST-checked and traced to FRD/SRS IDs in `RTM.md`. Overview depth.

## Epics → stories (PBIs)

### Epic A — Diet filtering (PRD #1)
| PBI | Story | Acceptance (G/W/T abbrev.) | Traces | Pts |
|---|---|---|---|---|
| `PBI-FILT-001` | As a diner, I filter the menu by a diet tag so I see only meals I can eat | Given vegan selected, when I open the menu, then only vegan meals show | FRD-FILT-001 · SR-FUNC-001 | 5 |
| `PBI-FILT-002` | As a diner, I combine multiple diet filters so results match all of them | Given vegan + nut-free, then results satisfy both | FRD-FILT-002 | 3 |

### Epic B — Order & pay (PRD #2)
| PBI | Story | Acceptance | Traces | Pts |
|---|---|---|---|---|
| `PBI-ORD-001` | As a diner, I place and pay for an order so my meal is scheduled | Given a valid cart, when I pay, then an order is confirmed within the target | FRD-ORD-001 · SR-FUNC-004 | 8 |
| `PBI-ORD-002` | As a diner, I'm blocked from ordering out-of-stock meals so I'm not disappointed | Given a sold-out meal, then checkout rejects it with a clear message | FRD-ORD-002 · SR-FUNC-002 | 5 |

### Epic C — Live tracking (PRD #3)
| PBI | Story | Acceptance | Traces | Pts |
|---|---|---|---|---|
| `PBI-TRK-BE-001` | *(enabler)* Event-driven tracking backend so the UI can show live ETA | Given a courier location event, then the order's ETA updates within 5s | SR-FUNC-003 · ADR-0001 | 8 |
| `PBI-TRK-001` | As a diner, I see a live ETA on the order screen so I know when food arrives | Given an active order, then ETA refreshes live | FRD-TRK-001 | 5 |

> **Backend-first split** (BEST-PRACTICES platform-extension exception): `PBI-TRK-BE-001` blocks `PBI-TRK-001` and is scheduled first — a UI against a non-existent endpoint isn't Ready.

### Epic D — Favorites (PRD #4)
| PBI | Story | Acceptance | Traces | Pts |
|---|---|---|---|---|
| `PBI-FAV-001` | As a returning diner, I save and reorder favorites so reordering is one tap | Given a saved favorite, then reorder pre-fills the cart | FRD-FAV-001 | 3 |

## Pull order (value / risk / dependency)
1. `PBI-TRK-BE-001` (unblocks tracking) → 2. `PBI-ORD-001` (core revenue) → 3. `PBI-FILT-001` (core value) → 4. `PBI-FILT-002` → 5. `PBI-ORD-002` → 6. `PBI-TRK-001` (after BE) → 7. `PBI-FAV-001`.

**Definition of Ready** met for items 1–5 (clear story, AC, estimate, no blocking dep). `PBI-TRK-001` is **blocked** by `PBI-TRK-BE-001`. Total: **37 pts** across 7 stories.
