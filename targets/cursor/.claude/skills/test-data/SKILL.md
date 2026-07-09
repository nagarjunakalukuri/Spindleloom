---
name: test-data
description: Design and manage test data — deterministic fixtures and factories, boundary-correct shapes, PII-safe synthetic data, and seeding that keeps suites fast and repeatable. Use when writing or reviewing tests that need data, when fixtures drift from real contracts, or when tests share mutable state. Consumed by test-author and test-automation-engineer; pairs with test-design (which cases) — this is the data those cases run on.
---

# Test data — deterministic, boundary-correct, PII-safe

Bad test data fails suites in three ways: nondeterminism (time/randomness/shared state),
shape drift (fixtures modeling a contract the code no longer has), and leakage (real PII
copied into fixtures). The method:

## Fixtures and factories

- **Factory over snapshot.** A factory (`make_order(status="paid", **overrides)`) builds a
  valid object with sensible defaults and lets each test override only what it asserts on —
  the test reads as its own documentation. Snapshots of real payloads rot silently.
- **Consumed-shape parity.** A fixture models the boundary it's injected at: read the real
  consumer (post-transform, post-camelize) and mirror the exact field names it reads. A
  self-consistent fixture with the wrong contract yields green tests and broken production.
- **One authoritative fixture per contract**, reused via the factory's overrides — ten
  hand-rolled variants of the same payload is ten places to miss a schema change.

## Determinism

- **Freeze the clock, seed the randomness.** Inject time (`now()` as a parameter/fixture)
  and seed every RNG; a test that depends on wall-clock or ordering is flaky by design.
- **Isolate state per test**: fresh DB transaction/rollback, per-test temp dirs, no shared
  mutable module state. Suites must pass shuffled.
- **Scratch stores over mocks for integration seams**: an in-memory/ephemeral DB catches
  what a bare mock hides (constraints, types, transactions).

## PII safety

- **Never copy production records into fixtures** — synthesize. Names/emails/ids come from
  generators, not exports; anonymized-but-realistic beats real-but-redacted.
- Fixture files live under version control and code review like any contract; a real
  customer email in a fixture is a data-handling incident, not a shortcut.

## Seeding at scale

- Seed scripts are **idempotent** (safe to re-run) and **layered**: minimal core set for
  unit/integration; a richer scenario set for e2e/UAT, each scenario named for what it
  proves ("expired-card checkout", not "test data 7").
- The seeded state is part of the test's Arrange step — document it in the test plan so
  QA and automation run against the same world.

## Anti-patterns

| Smell | Fix |
|---|---|
| `sleep()` or wall-clock in a test | inject and freeze time |
| Fixture edited to make a failing test pass | fix the contract question first — which side drifted? |
| Prod data dump as seed | synthetic factory data, PII-free |
| Tests pass in order, fail shuffled | shared state — isolate per test |
