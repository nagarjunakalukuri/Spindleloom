---
name: test-design
description: Derive a small, high-coverage set of test cases from a requirement using proven techniques — equivalence partitioning, boundary-value analysis, decision tables, state transitions, and the negative/authorization paths. Use when writing or reviewing test cases, or when a suite is all happy-path. Pairs with the test-plan-writer agent.
---

# Test design — getting maximum coverage from minimum cases

The goal is not "more tests" — it's the *fewest* cases that would catch the most defects, each traced to a requirement. Use these techniques to choose them.

## Pick the level first (test pyramid)
Prove it at the **lowest sufficient level**: unit (logic, mocked deps) → integration (real dependency) → contract/API (one endpoint over HTTP) → e2e (a user journey). Don't write an E2E for what a unit proves — it's slower, flakier, costlier.

## Techniques to choose inputs

- **Equivalence partitioning** — group inputs that should behave the same; test one representative per class, not all values. (valid / too-low / too-high / wrong-type → 4 cases, not 400.)
- **Boundary-value analysis** — defects cluster at edges. Test min, min−1, max, max+1, and zero/empty. (A "limit 1–200" param → test 0, 1, 200, 201.)
- **Decision table** — for combinations of conditions (role × state × flag), enumerate the meaningful combinations and the expected outcome; collapse impossible ones.
- **State transition** — for stateful flows (draft→review→approved), test each legal transition and the *illegal* ones (approve an already-published item).
- **Error guessing** — null, empty string, huge input, duplicate submit, concurrent edit, timeout.

## Always include the unhappy path
For every requirement ask:
- Invalid / missing / malformed input?
- Unauthorized actor (wrong role) and unauthenticated (no token)?
- Concurrency: two writers, stale version → conflict?
- Resource missing (404), duplicate (idempotency), invariant violated (422)?
- Dependency failure: timeout, 5xx from a downstream service?

## API status-code matrix (contract tests)
For each endpoint, write one case per distinct outcome — not just 200:

| Outcome | When |
|---|---|
| 200 / 201 | valid request, authorized |
| 400 / 422 | malformed body / violated invariant |
| 401 | no / invalid token |
| 403 | authenticated but wrong role |
| 404 | resource / partition not found |
| 409 | version / concurrency conflict |

A guard described in the spec with no negative test is **unverified** — the 403 and 422 cases are as important as the 200.

## What makes a case good
- **Executable:** Given/When/Then or Arrange/Act/Assert with concrete inputs and a checkable expected result.
- **Independent:** doesn't depend on another test's side effects.
- **Traced:** names the FRD/SRS/PBI id it verifies (`TEST-<AREA>-<NUM>`).
- **Deterministic:** no reliance on time/order/network unless that's the thing under test (then control it).

## Review smell tests
- All cases are happy-path → missing negative/authz/boundary.
- Every test is E2E → pyramid inverted; push logic down to unit.
- A test asserts an adjective ("fast", "correct") → not verifiable; get a measurable target from the SRS.
- A requirement has zero tests → coverage gap; a test has no requirement → over-testing or a missing requirement.
- An integration test **mocks the very component it names** (the engine/router/graph it should exercise) → it proves nothing about wiring; every integration seam needs at least one test that wires the real components together (real registration / compile / dispatch), not a mock of the subject under test. *(A latent "unknown node" bug hid for months behind an ingest test that mocked the workflow engine it was meant to run.)*
