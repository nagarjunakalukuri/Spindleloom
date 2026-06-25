# TSD: FreshDesk

| Field | Value |
|---|---|
| Author | Senior engineer |
| Status | Approved |
| Related SDD | 06-sdd.md |
| Last updated | 2026-06-11 |

> Worked example — overview depth. Produced by `tsd-writer`. The build playbook.

## Scope
Implementation spec for Menu, Order, and Tracking services + clients. (Versions illustrative.)

## Final tech stack
| Layer | Choice | Version | Notes |
|---|---|---|---|
| Backend | Node.js + NestJS | 20 LTS / 10 | per-service |
| Datastore | PostgreSQL | 16 | catalog + orders |
| Events | Kafka | 3.7 | tracking stream |
| Clients | React Native | 0.74 | iOS + Android |
| Infra | Kubernetes on AWS | — | HPA for scale |

## API specification (samples)
All error responses use the constitution's shape (`00-constitution.md` P2): `{ code, message }` with `code` from the shared registry, carried by the HTTP status below.

### `POST /api/v1/orders`
- **Auth:** JWT bearer, scope `orders:write`
- **Idempotency:** required `Idempotency-Key` header (per `00-constitution.md` P5); a repeated key returns the original `201` result and never re-charges — backs the FRD payment-retry path safely
- **Request:** `{ items:[{mealId, qty}], paymentToken }`
- **Response 201:** `{ orderId, status, etaMinutes }`
- **Errors:** `401 {code:"unauthorized"}` · `402 {code:"payment_declined"}` · `409 {code:"out_of_stock", message, alternatives:[{mealId, name}]}` (alternatives satisfy FRD-ORD-002)

### `GET /api/v1/orders/{id}/tracking`
- **Response 200:** `{ driverLat, driverLng, etaMinutes, updatedAt }`

## Data models
| Entity | Field | Type | Constraints |
|---|---|---|---|
| Order | id | uuid | pk |
| Order | status | enum | placed/preparing/enroute/delivered |
| Favorite | userId, orderId | uuid | unique(userId, orderId) |

## Testing strategy
| Level | Scope | Target |
|---|---|---|
| Unit | services | ≥ 80% |
| Integration | payment + tracking flows; gateway OAuth2/MFA auth | key paths |
| E2E | order→track happy + payment-decline; OOS+alternatives; FRD edge cases (no drivers, driver-location lost, empty-filter state) | per release |

## Performance & security standards
Filter endpoint < 200 ms p95; OAuth2 + MFA; payment via provider SDK (no card data stored).

## Deployment plan
CI/CD via pipeline; blue-green deploy; one-click rollback; SLO alerts on order error-rate and tracking lag.
