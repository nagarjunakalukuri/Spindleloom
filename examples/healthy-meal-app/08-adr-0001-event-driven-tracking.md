# ADR-0001: Event-driven delivery tracking

- **Status:** Accepted
- **Date:** 2026-06-11
- **Deciders:** Architect, eng lead
- **Related:** 06-sdd.md §4, FRD-TRK-001, SR-FUNC-003; proposed in RFC-0001 (09-rfc-0001-event-driven-tracking.md)

> Worked example — produced by `adr-writer` (Nygard format).

## Context
Live tracking (FRD-TRK-001) depends on a third-party logistics feed whose latency we don't control. The order flow must stay fast and reliable (99.9% uptime) even if the location feed is slow or briefly down.

## Decision
We will consume the logistics location feed asynchronously via Kafka events in a separate Tracking Service, rather than calling the partner synchronously inside the order/request path.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Synchronous calls to partner on each tracking request | Simplest | Couples our latency/uptime to the partner's | Violates the 99.9% / fast-path constraint |
| Poll partner on a timer | Easy to reason about | Wasteful, laggy updates | Worse UX, still coupled |
| Event-driven (chosen) | Isolates partner latency, scales | More infra (Kafka) | Accepted — worth it |

## Consequences
Tracking failures no longer affect ordering. We take on Kafka operational complexity, and tracking reads become eventually-consistent (acceptable: we show "updating…" with last-known location, per FRD edge cases).
