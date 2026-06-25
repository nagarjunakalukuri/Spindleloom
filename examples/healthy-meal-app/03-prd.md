# PRD: FreshDesk

| Field | Value |
|---|---|
| Participants | PM, eng lead, designer, QA |
| Status | In development |
| Target release | v1.0 |
| Last updated | 2026-06-11 |

> Worked example — overview depth. Produced by `prd-writer`. Builds on `02-brd.md`.

## Problem statement
Professionals abandon healthy eating because finding a suitable meal takes too long. We need ordering a nutrition-appropriate meal to take seconds, not minutes.

## Team goals and business objectives
Drive the BRD's retention and order-frequency goals by making the healthy choice the fastest choice.

## Success metrics
- **Primary:** ≥ 3 orders/active user/week within 30 days of launch.
- **Secondary:** ≥ 40% M2 retention.
- **Guardrail:** meal-list load time increases no more than 200 ms vs. baseline.

## Assumptions
Users will set dietary preferences if onboarding is one screen; logistics partner exposes live driver location.

## User personas
Busy professional (speed-first) and fitness-focused user (macro-first).

## User stories (MoSCoW)
| # | Story | Priority | Acceptance criteria |
|---|---|---|---|
| 1 | As a user, I filter meals by dietary preference so I only see meals I can eat | Must | Given a set preference, when I open the menu, then only matching meals show |
| 2 | As a user, I order and pay so I receive a meal | Must | Given a cart, when I pay, then I get an order confirmation + ETA |
| 3 | As a user, I track my delivery live so I know when it arrives | Must | Given an active order, when I open it, then I see live driver location + ETA |
| 4 | As a user, I save favorites & reorder in one tap so I save time | Should | Given a past order, when I tap reorder, then the cart is prefilled |

## User flow
Onboard (set prefs) → browse filtered menu → cart → pay → track → (later) reorder favorite. Error states: payment failure, no drivers available, item out of stock.

## User interaction and design
Mobile-first; one-screen onboarding; live map for tracking. (Wireframes linked in design tool.)

## Decisions log
| Date | Decision | Reasoning | Trade-off |
|---|---|---|---|
| 2026-06-11 | Favorites is "Should", not "Must" for v1 | Core loop is filter→order→track; favorites can fast-follow | Slightly less stickiness at launch |

## What we're not doing
Loyalty points, subscriptions, overseas delivery (Won't-Have, v1).
