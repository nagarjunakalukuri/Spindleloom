# BRD: FreshDesk

| Field | Value |
|---|---|
| Sponsor | VP Product |
| Author | Business Analyst |
| Status | Approved |
| Last updated | 2026-06-11 |

> Worked example — overview depth. Produced by `brd-writer`. Builds on `01-mrd.md`.

## Executive summary
FreshDesk is a nutrition-first meal delivery app for working professionals. It removes the planning burden by letting users filter meals by dietary preference, order instantly, track delivery live, and reorder favorites. Goal: capture the underserved healthy-convenience segment.

## Background and problem statement
Professionals default to unhealthy takeout because healthy options require planning. No major delivery app is built nutrition-first (see MRD).

## Business goals and objectives
- Reach 50,000 active subscribers in 3 cities within 12 months.
- Achieve 40% month-2 retention.
- Average 3+ orders per active user per week.

## Success metrics / KPIs
- Subscribers (baseline 0 → target 50k Y1).
- M2 retention ≥ 40%.
- Orders/active user/week ≥ 3.

## Scope
**In scope:** meal browsing with dietary filters, ordering & payment, real-time tracking, favorites & reorder.
**Out of scope:** overseas delivery, in-house catering, loyalty points (deferred to Y2).

## Stakeholders
| Name | Role | Interest |
|---|---|---|
| VP Product | Sponsor | Business outcomes |
| BA | Author | Requirement clarity |
| Eng lead | Consumer | Feasibility |

## Current business process (as-is)
None — greenfield. Today users manually browse generic apps and filter by hand.

## Proposed business process (to-be)
User sets dietary preferences once → app surfaces matching meals → one-tap order → live tracking → reorder favorites. Benefit: seconds, not minutes, to a healthy meal.

## High-level requirements
Users can filter meals by dietary preference, order and pay, track delivery in real time, and save/reorder favorite meals.

## Impact analysis
New build; depends on a payments provider and a delivery/logistics integration. Risk: delivery SLAs in launch cities — mitigate with a vetted logistics partner.

## Requirements traceability matrix (RTM)
See `RTM.md` (shared across all docs).

## Open questions
| Question | Owner | Decision | Date |
|---|---|---|---|
| Which payment provider? | Eng lead | Deferred to TSD | — |
