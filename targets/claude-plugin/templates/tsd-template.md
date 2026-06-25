# TSD: <System / Project Name>

| Field | Value |
|---|---|
| Author | <engineer> |
| Status | Draft |
| Related SDD | <link> |
| Last updated | <date> |

## Scope

<What this spec covers; what it doesn't.>

## Final tech stack

| Layer | Choice | Version | Notes |
|---|---|---|---|
| Language | | | |
| Framework | | | |
| Datastore | | | |
| Cache | | | |
| Infra / deploy | | | |

## API specification

### `POST /api/v1/<resource>`

- **Auth:** <e.g. JWT bearer; required scopes>
- **Request:** `{ field: type, ... }`
- **Response 200:** `{ field: type, ... }`
- **Errors:** 400 / 401 / 409 / 500 — when and what body

## Data models

| Entity | Field | Type | Constraints | Index |
|---|---|---|---|---|
| | | | | |

<Relationships / ERD as needed.>

## Sequence / interaction details

<Critical flows at the implementation level; diagrams where useful.>

## Testing strategy

| Level | Scope | Tooling | Target |
|---|---|---|---|
| Unit | | | <coverage %> |
| Integration | | | |
| E2E | | | |

## Performance and security standards

<Latency/throughput budgets, load expectations; authn/authz, input validation, secrets, data-at-rest/in-transit, dependency scanning.>

## Deployment plan

<Environments, CI/CD pipeline, migration steps, feature flags, rollback procedure, monitoring/alerting.>

## Open questions

| Question | Owner | Decision | Date |
|---|---|---|---|
| | | | |
