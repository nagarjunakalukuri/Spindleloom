# Test Plan — <Project / Feature>

| Field | Value |
|---|---|
| Author | <QA / lead> |
| Related | <FRD / SRS / URS / TSD links> |
| Status | Draft |
| Last updated | <date> |

## Test strategy

- **Levels in scope:** unit / integration / e2e / UAT (+ perf, security, accessibility)
- **Environments:** <dev / stage / prod-like>
- **Entry criteria:** <code merged, build green, env ready>
- **Exit criteria:** <all P0/P1 cases pass, no open critical defects, coverage ≥ target>
- **Tooling:** <frameworks, Azure Test Plans, etc.>

## Test cases

| Case ID | Requirement | Type | Level | Preconditions | Steps | Test data | Expected result |
|---|---|---|---|---|---|---|---|
| TC-001 | FRD-<AREA>-001 | Functional | Integration | | | | |

## Coverage / traceability

| Requirement | Covered by | Gap? |
|---|---|---|
| FRD-<AREA>-001 | TC-001 | — |
| FRD-<AREA>-00X | — | ⚠️ no test |

## (Regulated only) Validation protocols

| Protocol | URS item | Scope |
|---|---|---|
| IQ | URS-USE-001 | install/config verified |
| OQ | URS-USE-001 | operates to spec across ranges |
| PQ | URS-USE-002 | performs in real use/environment |

## Defect handling

<Severity scale, where bugs are logged (e.g. Azure Boards Bug work item), retest/closure flow.>
