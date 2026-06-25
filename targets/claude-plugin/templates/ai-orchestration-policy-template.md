# AI Orchestration Policy — <Team / Project>

| Field | Value |
|---|---|
| Owner | <architect / leads> |
| Last updated | <date> |

## Delegation policy

| Work | Default |
|---|---|
| Boilerplate, scaffolding, formatting | AI, auto-checks |
| Unit tests for a clear spec | AI, human reviews |
| Well-scoped feature w/ acceptance criteria | AI drafts, human reviews |
| Refactor under green tests | AI, human reviews |
| Architecture / design decisions | Human (AI advises) → ADR |
| Security, auth, payments, PII | Human-led, senior + architect review |
| Data migrations / irreversible ops | Human-led, extra gate |

## Human-in-the-loop by risk

| Risk / path | Autonomy | Required reviewers |
|---|---|---|
| docs, formatting | auto-merge on green | — |
| app logic | AI drafts | 1 peer |
| security / data / payments | human-led | senior + architect |
| protected paths (<list>) | AI may not auto-modify | — |

## Guardrails & evals

- Every AI change links a PBI/spec (traceability)
- Required: tests pass, coverage ≥ target, security scan clean (ci-cd-pipeline)
- AI-output review checklist (extends code-reviewer): traces to spec? meaningful tests? no unrequested scope? no insecure shortcut?
- Context conventions: agents pointed at <CLAUDE.md / AGENTS.md>, FRD acceptance criteria, coding-standards

## Accountability

The human approver owns merged AI output. No auto-merge to protected paths.
