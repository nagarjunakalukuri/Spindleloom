---
description: Generate or review a test plan + traceable test cases for a feature, from its SRS/FRD/PBIs.
argument-hint: [path-to-spec-folder-or-feature]
---

Produce a test plan for **$1** (default: the spec folder / feature in context) using the `test-plan-writer` agent and the `test-design` skill.

1. Read the upstream SRS (measurable targets — the oracle), FRD (behaviors + edge cases), the backlog PBIs (acceptance criteria), and any API spec / OpenAPI. Also read the project's own testing rules (coverage target, naming, mocking) and conform to them.
2. For each requirement, derive the minimum high-coverage set of cases at the **lowest sufficient level** (unit → integration → contract/API → e2e), using equivalence partitioning, boundary values, and decision tables. Always include the **unhappy path** — invalid input, unauthorized/unauthenticated actor, conflict, missing resource, violated invariant.
3. For any endpoints, build the **API status-code matrix** (200 + 401/403/404/409/422), one case per distinct outcome — not just the 200.
4. Give each case a `TEST-<AREA>-<NUM>` aligned to the FRD AREA codes, with Given/When/Then, the upstream `Traces` IDs, and a Status (already-written → point at the test file; or to-write).
5. Emit a **coverage table** (requirement → test cases) and flag any FRD/SRS ID with no test as a gap (route upstream if the requirement is untestable). Save as `NN-test-plan.md` and extend the RTM's test column.
6. If asked to REVIEW instead: report coverage gaps, orphan tests, happy-path-only endpoints, wrong-level tests, and whether the coverage target is met.

Run `hooks/validate_reqs.py` afterward — with a test plan present it reports the requirement→test coverage.
