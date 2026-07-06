# RFC-0001: Event-driven delivery tracking

- **Status:** Accepted
- **Author:** Architect
- **Deciders:** Architect, eng lead
- **Comments by:** 2026-06-10
- **Related:** 06-sdd.md §4, FRD-TRK-001, SR-FUNC-003

> Worked example — produced by `rfc-facilitator`. The *proposal and debate* that preceded the decision; the outcome was recorded as ADR-0001 (`08-adr-0001-event-driven-tracking.md`). RFCs and ADRs run continuously, outside the linear MRD→TSD funnel.

## Summary
I propose we consume the logistics partner's location feed asynchronously via events, in a dedicated Tracking Service, rather than calling the partner synchronously on the order/request path. This isolates a third-party latency we don't control from our core flow.

## Problem & context
Live tracking (FRD-TRK-001) depends on a third-party feed whose latency and uptime we can't control, yet SR-FUNC-003 requires location/ETA updates within 5 s and the order flow must hold 99.9% uptime (SRS). A slow or down partner must not degrade ordering.

## Proposal
Run a separate **Tracking Service** that subscribes to logistics location events (Kafka) and streams driver position/ETA to the app. The order path emits `OrderPlaced`; tracking reads are served from the Tracking Service's own state, never by a synchronous partner call.

## Alternatives considered
| Option | Pros | Cons | Why not (yet) |
|---|---|---|---|
| Do nothing (no live tracking v1) | No new infra | Fails FRD-TRK-001, a Must story | Rejected — core PRD value |
| Synchronous calls to partner per request | Simplest | Couples our latency/uptime to the partner's | Violates 99.9% / fast-path constraint |
| Poll partner on a timer | Easy to reason about | Wasteful, laggy updates | Worse UX, still coupled |
| Event-driven (proposed) | Isolates partner latency, scales | More infra (Kafka), eventual consistency | **Recommended** |

## Impact
Adds Kafka to the stack and operational complexity (the TSD picks Kafka 3.7). Tracking reads become eventually-consistent — acceptable, handled by the FRD edge case ("show last-known + updating…"). No change to the order/payment path. Blast radius: Tracking Service only.

## Open questions
- Is the added Kafka operational cost justified for v1, or defer live tracking to v1.1?
- Is eventual consistency acceptable to product for the tracking view? (Resolved: yes, with the "updating…" fallback.)

## Decision
**Accepted** — event-driven tracking. Kafka cost judged worth the isolation; eventual consistency accepted with the last-known-location fallback. Recorded immutably as **ADR-0001**; design updated in SDD §4.
