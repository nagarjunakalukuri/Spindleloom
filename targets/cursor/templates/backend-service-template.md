# Backend Service — <name / feature>

| Field | Value |
|---|---|
| Author | <backend dev> |
| Related | <FRD / SRS / SDD / TSD links> |

## Responsibility & boundary

<what it owns; what it does NOT; its data store>

## Endpoints (contract → api-designer)

<list; link the OpenAPI contract>

## Data access (→ data-modeler)

<entities touched; transactions; indexes for the real access patterns>

## Reliability

- Idempotency: <keys / approach>
- Timeouts / retries / backoff · circuit breakers
- Failure modes & responses

## Security

- AuthN / AuthZ · input validation · secrets · encryption (in transit & at rest)

## Observability

- Logs / metrics / traces · correlation IDs · alerts (ties to SRS targets)

## Scale

- Caching, async / queues, partitioning — justified against SRS NFRs
