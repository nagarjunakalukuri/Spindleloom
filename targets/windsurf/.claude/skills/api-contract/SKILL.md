---
name: api-contract
description: Treat the API contract (OpenAPI) as a first-class, reviewed artifact — design it before/with the code, keep it the source of truth for request/response shapes and error codes, and derive both docs and contract tests from it. Use when designing or reviewing an API surface, documenting endpoints, or generating API tests.
---

# API contract — the spec between caller and service

The API contract is the agreement: paths, methods, auth, request/response schemas, and the full set of status codes. It belongs in the TSD's API section, but treat the machine-readable contract (OpenAPI/JSON Schema) as the source of truth — docs, client types, and contract tests all derive from it.

## Contract-first vs. code-first
- **Contract-first:** author the OpenAPI spec, review it, then implement against it. Best when multiple teams/clients depend on the API or it's externally exposed.
- **Code-first (generated):** annotate the code (e.g. FastAPI) and generate OpenAPI from it. Fine for internal APIs — but the generated spec is still the reviewed artifact; check it in the PR.
Either way: **the spec is reviewed, versioned, and the contract tests run against it.**

## What a complete endpoint contract states
For every endpoint:
- **Method + path** and a one-line purpose.
- **Auth**: required role(s) / scopes. (Who gets 401 vs 403.)
- **Request**: path/query params (with constraints), body schema.
- **Responses**: the success shape AND every error — the full status-code matrix (`test-design`) — each with its meaning and envelope.
- **Invariants the contract promises**: idempotency, optimistic-concurrency (version/etag → 409), immutability (some state can't change → 422), pagination contract.
- **Example**: a runnable request → response.

## Versioning & change control
- Version the API (`/v1`). Additive changes (new optional field, new endpoint) are backward-compatible; removing/renaming a field or tightening a type is **breaking** → new version or a deprecation cycle.
- A breaking contract change is a decision worth an ADR.

## Derive, don't duplicate
- **Docs:** the API reference (feature-docs-writer) is generated/derived from the contract — never hand-copy status codes that will drift.
- **Tests:** the contract test suite (test-plan-writer, contract/API level) asserts the spec — one case per documented response, including every error.
- **Client types:** generate from the schema where possible.

## Review checklist
- Does every endpoint document its auth and its **full** error set (not just 200)?
- Are the promised invariants (idempotency, 409 on stale version, 422 on violated rule) in the spec AND covered by a contract test?
- Is the change additive (safe) or breaking (needs a version/ADR)?
- Do the docs and tests derive from this contract, or are values hand-copied (drift risk)?

## Tie-in
Pairs with `test-design` (the status-code matrix) and `feature-docs-writer` (the reference quadrant). The contract is the shared source all three read from.
