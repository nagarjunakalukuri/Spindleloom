---
name: threat-modeling-stride
description: Threat-model a feature or flow with STRIDE — identify assets and trust boundaries, walk Spoofing / Tampering / Repudiation / Information-disclosure / Denial-of-service / Elevation-of-privilege per component, and turn each credible threat into a testable SEC- requirement plus a control. Use at the SDD/design stage and when reviewing a risky flow (auth, payments, PII). Consumed by security-reviewer, architect, sdd-writer, api-designer, and data-modeler.
---

# STRIDE threat modeling — design security in, cheaply

Security is a design property, cheapest to build in early. A scanner catches known-bad patterns; this catches *design* weaknesses a scanner can't see.

## 1. Frame the system
- **Assets** — what's worth attacking (credentials, PII, money, tokens, the audit trail).
- **Trust boundaries** — where data crosses a privilege change: client→server, service→service, app→DB, tenant→tenant. Threats live on the boundaries.
- Sketch the data flow for the feature; mark every boundary crossing.

## 2. Walk STRIDE per element
For each component/flow that crosses a boundary, ask each:

| Threat | Question | Typical control |
|---|---|---|
| **S**poofing | Can someone impersonate a user/service? | strong authn, mTLS, signed tokens |
| **T**ampering | Can data be modified in transit/at rest? | integrity checks, authz on writes, parameterized queries |
| **R**epudiation | Can an actor deny doing it? | audit logs, signed actions |
| **I**nfo disclosure | Can data leak? | encryption, least-privilege, no PII in logs/errors |
| **D**enial of service | Can it be exhausted? | rate limits, quotas, timeouts, pagination |
| **E**levation | Can someone gain rights they shouldn't? | **server-side** authz on every path, deny-by-default |

## 3. Turn each credible threat into a requirement
- Write a **testable `SEC-` requirement** + the control ("SEC-ORD-003: the order endpoint shall enforce server-side authorization; a non-owner receives 403"). Trace it in the RTM.
- A guard described with **no negative test is unverified** — the 401/403/409/422 cases matter as much as the 200 (pairs with `test-design`).

## 4. Prioritize
Rank by **likelihood × impact**; fix the high cells now, log the rest as risks (`raid-log`) — don't pretend you closed everything.

## Smells
- Threats listed with no control or no testable requirement → a wish-list, not a model.
- Authz checked client-side only → the classic elevation hole.
- "We'll add security later" → later = never; the cheapest point is the design.
