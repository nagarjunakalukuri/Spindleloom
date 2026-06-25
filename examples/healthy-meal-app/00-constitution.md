# Project Constitution — FreshDesk

| Field | Value |
|---|---|
| Owner | Architect |
| Version | v1.0 |
| Status | Active |
| Last updated | 2026-06-11 |

> Worked example — overview depth. The standing guardrails every contributor (human or AI) reads before changing FreshDesk. Feature behavior lives in `03-prd.md`/`04-frd.md`; this holds only durable law.

## Purpose & intent
A mobile-first healthy-meal delivery app that gets diet-appropriate meals to users with live order tracking. The system exists to make *trustworthy* dietary filtering and *accurate* delivery ETAs — those two outcomes outrank feature breadth.

## Non-negotiable principles
1. The system shall never show a meal that violates an active dietary filter — a filtering false-positive is a safety incident, not a bug.
2. The system shall return all external API errors as `{code, message}` with codes from the shared registry.
3. The system shall keep payment-card data within the PCI-DSS-isolated scope; no card data crosses into the app backend.
4. The system shall not write PII to logs, traces, or analytics events.
5. The system shall make every order-state write idempotent (retries must not double-charge or duplicate orders).

## Architectural boundaries
Mobile clients talk only to the API gateway, never to services directly. Order tracking is event-driven (see `08-adr-0001`). The payments provider is integrated through an isolated boundary; the core backend never holds card data.

## Conventions
WCAG 2.1 AA, GDPR by default, all order flows traced. See the team `coding-standards` for language-level detail.

## AI-agent operating rules
1. Read `04-frd.md` / `05-srs.md` for the relevant area before changing code.
2. If a spec is stale or intent is unclear, update the spec first and flag it upstream — never guess on dietary-filter or payment logic.
3. Keep every change traceable to a Req-ID in `RTM.md` or a principle above.
See the `ai-orchestration-policy` for the full delegation matrix; dietary-filter and payment changes are human-review-required.

## Non-goals
- No in-app social/feed features this release.
- No support for the logistics partner's internal systems (out of scope per `05-srs.md`).

## Amendment process
Versioned and PR-reviewed. Changing a principle requires an ADR and a version bump; supersede, don't rewrite.
