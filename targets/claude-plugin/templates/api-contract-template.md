# API Contract — <service> (v1)

| Field | Value |
|---|---|
| Author | <api-designer> |
| Related | <FRD / SRS / SDD> |
| Status | Draft / Approved |

## Conventions

- Base: `/api/v1` · casing: <camel / snake> · pagination: <cursor / offset> · auth: <OAuth2 + scopes>

## Error model

`{ "code": "string", "message": "string", "details": [] }` — 4xx client, 5xx server.

## Resources / operations

### `POST /api/v1/<resource>`

- **Auth:** <scheme + scope>  ·  **Idempotent:** yes/no (key: <…>)
- **Request:** `{ field: type, … }`
- **200 / 201:** `{ field: type, … }`
- **Errors:** 400 / 401 / 403 / 404 / 409 / 422 — when & body
- **Example:** <req → resp>

## Versioning & compatibility

<strategy (URI / header / media type); what's additive-safe vs breaking>
