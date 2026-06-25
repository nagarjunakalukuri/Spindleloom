# CI/CD Pipeline — <Project>

| Field | Value |
|---|---|
| Platform | <GitHub Actions / Azure Pipelines / GitLab CI> |
| Owner | <devops / lead> |
| Deploy targets | <staging, prod> |

## Required-to-merge checks (branch protection)

- [ ] format + lint + type-check
- [ ] unit + integration tests pass
- [ ] security scan (no high/critical)
- [ ] ≥ <N> review approval(s)

## Stages

| # | Stage | Commands / tools | Gate |
|---|---|---|---|
| 1 | Lint / format / type | <…> | block merge |
| 2 | Test | <unit, integration> | block merge |
| 3 | Build + scan | <build, SAST, deps> | block |
| 4 | Deploy staging | <…> + smoke / e2e | block promotion |
| 5 | Deploy prod | canary / blue-green + health | auto-rollback |

## Rollback

<how rollback triggers and runs; who's paged>

## Metrics (DORA)

<deploy frequency, lead time for changes, change-fail rate, MTTR — targets>
