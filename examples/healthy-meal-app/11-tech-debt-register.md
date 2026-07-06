# Technical-Debt Register — FreshDesk

- **Owner:** Architect
- **Last groomed:** 2026-06-11

> Worked example — produced by `tech-debt-keeper`. Owned, quantified debt negotiable with the PM. Two items below trace directly to the `/spec-analyze` run on this example: the idempotency gap (a fixed blocker) and the PII-in-logs residual (a deliberately accepted gap).

## Register
| ID | Description | Location | Type | Impact | Interest (worsening) | Effort | Owner | Decision | Backlog link |
|---|---|---|---|---|---|---|---|---|---|
| DEBT-001 | Early order endpoints shipped without idempotency keys before the constitution P5 rule | Order Service `POST /api/v1/orders` | design | retry path risks double-charge | high — every new write path repeats the pattern | M | Backend lead | pay now | PBI-ORD-IDEM-1 |
| DEBT-002 | Constitution P4 "no PII in logs" has no automated verification | logging/observability (cross-service) | infra | compliance exposure if PII leaks to logs | low now — rises as log volume grows | M | Systems lead | schedule | PBI-OBS-PII-1 |
| DEBT-003 | Filter re-render trending toward the 200 ms budget under load | Menu Service filter path | code | UX risk near SR perf target | medium — +20 ms/release, now ~180 ms vs 200 ms | S | Frontend lead | monitor | — |
| DEBT-004 | E2E edge-case coverage (no drivers, location lost) added late; thin assertions | Tracking Service tests | test | regressions could slip on tracking edges | low | S | QA | accept | — |

## Decision key
pay now → current backlog · schedule → future sprint · accept → live with it (recorded) · monitor → re-score next grooming.

## PM-negotiation view (sorted by impact × interest vs effort)
1. **DEBT-001** (high interest, M effort) — pay now; the pattern propagates to every new service. *Recommend this sprint.*
2. **DEBT-003** (medium, S) — cheap; fix before it crosses the budget. *Recommend next sprint.*
3. **DEBT-002** (low-but-rising, M) — schedule before launch scale-up.
4. **DEBT-004** — accept for v1.

Grouped by team: **Backend** 1 (DEBT-001), **Systems** 1 (DEBT-002), **Frontend** 1 (DEBT-003), **QA** 1 (DEBT-004) — rot is evenly spread, no single hotspot this period.

## Sources this period
DEBT-001/002 from the `/spec-analyze` cross-artifact run; DEBT-003 from a load-test observation; DEBT-004 from `code-reviewer` on the tracking PR.
