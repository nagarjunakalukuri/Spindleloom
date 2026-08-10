# Coding Standards — <Team / Project>

| Field | Value |
|---|---|
| Owner | <architect / leads> |
| Stack | <languages / frameworks> |
| Last updated | <date> |

## Baseline

We follow <PEP 8 / Google style / Effective Go / …> plus the formatter & linter below; only deviations and team rules are listed here.

## Tooling (authoritative — enforced in CI)

| Concern | Tool | Rule |
|---|---|---|
| Format | <prettier / black / gofmt> | CI fails on diff |
| Lint | <eslint / ruff / golangci-lint> | no errors |
| Types | <tsc / mypy> | strict |

## Team rules (review-enforced)

| # | Rule | Why | Good / bad |
|---|---|---|---|
| 1 | Validate input only at system boundaries | trust internal code | |
| 2 | Name booleans as predicates (isReady) | readability | |

## Error handling

<how errors are raised, wrapped, logged; no silent catches>

## Testing expectations

<what must be tested; what a "meaningful test" is; ties to DoD>

## Anti-patterns (don't do)

- <specific thing we've decided against, + why>
