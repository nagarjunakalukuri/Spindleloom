# FRD: FreshDesk

| Field | Value |
|---|---|
| Author | BA |
| Status | Approved |
| Related PRD | 03-prd.md |
| Last updated | 2026-06-11 |

> Worked example — overview depth. Produced by `frd-writer`. Specifies behavior for the PRD's must/should stories.

## Overview
Functional behavior for dietary filtering, ordering/payment, live tracking, and favorites/reorder.

## Functional requirements
| ID | Requirement ("the system shall …") | Acceptance criteria | PRD story |
|---|---|---|---|
| FRD-FILT-001 | The system shall show only meals matching the user's active dietary preferences | Given pref=vegan, when menu loads, then no non-vegan meals appear | 1 |
| FRD-FILT-002 | The system shall let the user change preferences at any time and re-filter immediately | Given menu open, when pref changes, then list updates without reload | 1 |
| FRD-ORD-001 | The system shall create an order and return a confirmation with ETA on successful payment | Given valid payment, when submitted, then order id + ETA returned | 2 |
| FRD-ORD-002 | The system shall block ordering an out-of-stock item and offer alternatives | Given item OOS, when added, then user is warned + shown alternatives | 2 |
| FRD-TRK-001 | The system shall display live driver location and ETA for an active order | Given active order, when opened, then map shows driver + ETA | 3 |
| FRD-FAV-001 | The system shall let a user mark a past order as favorite and reorder it in one tap | Given a favorite, when tapped, then cart is prefilled with same items | 4 |

## Edge cases & error handling
| Scenario | Expected response |
|---|---|
| Payment declined | Show error, preserve cart, offer retry/another method |
| No drivers available | Hold order, notify user, auto-assign when available |
| Driver location lost | Show last-known + "updating…", fall back to ETA only |
| Empty menu after filter | Show "no meals match — adjust preferences" empty state |

## Traceability
See `RTM.md`.
