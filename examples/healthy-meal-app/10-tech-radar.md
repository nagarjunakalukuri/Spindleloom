# Technology Radar — FreshDesk — 2026-Q2

- **Owner:** Architect
- **Published:** 2026-06-11

> Worked example — produced by `tech-radar-curator`. Architect-owned snapshot aligning the frontend, backend, and systems teams. Rings show current state; the *why* lives in the cited ADR/RFC. **Hold = no new usage.** Seeded from the TSD stack and ADR-0001/RFC-0001.

## Rings
- **Adopt** — proven; default for new work. · **Trial** — low-risk project + fallback. · **Assess** — spike only. · **Hold** — no new work with this.

## Blips
| Blip | Quadrant | Ring | New/Moved | Rationale | Driving ADR/RFC |
|---|---|---|---|---|---|
| Node.js / NestJS | Languages & Frameworks | Adopt | new | Standard backend stack per TSD; strong typing across services | — (TSD) |
| React Native | Languages & Frameworks | Adopt | new | One codebase for iOS + Android, per PRD mobile-first | — (TSD) |
| PostgreSQL | Platforms | Adopt | new | Relational fit for catalog + orders; ACID for payments | — (TSD) |
| Kafka | Platforms | Adopt | new | Backbone for event-driven tracking | ADR-0001 / RFC-0001 |
| Kubernetes on AWS | Platforms | Adopt | new | HPA for the 20k-concurrent scale target (SRS) | — (TSD) |
| Event-driven integration | Techniques | Adopt | new | Isolates third-party latency from the core path | ADR-0001 |
| Synchronous third-party calls on request path | Techniques | Hold | new | Couples our uptime to partners; violates 99.9% target | ADR-0001 (rejected option) |
| Feature-flag service | Tools | Trial | new | Wanted for progressive rollout; pilot on one service first | — (no RFC yet) |
| Polling for live data | Techniques | Hold | new | Wasteful + laggy vs events | RFC-0001 (rejected option) |

## Quadrants
Languages & Frameworks · Tools · Platforms · Techniques.

## Changes since last radar
First published radar (Q2). Event-driven tracking moved straight to **Adopt** off the back of RFC-0001 → ADR-0001; its two rejected alternatives (sync calls, polling) are recorded as **Hold** so no team re-proposes them.
