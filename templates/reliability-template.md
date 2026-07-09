# Reliability Plan — <Service / System>

| Field | Value |
|---|---|
| Owner | <SRE / DevOps> |
| Related | <SRS NFRs / SDD> |
| Status | Draft / Active |
| Last updated | <date> |

> Proactive operability: SLOs, observability, alerts, runbooks, and rollback — defined *before* incidents. Turns the SRS reliability NFRs into measured targets. Use `OPS-<AREA>-<NUM>` IDs.

## SLIs & SLOs
| Service / journey | SLI (what we measure) | SLO (target) | Window | Source SRS NFR |
|---|---|---|---|---|
| <svc> | e.g. P95 latency | < 200 ms | 28-day | SR-PERF-… |
| <svc> | availability | 99.9% | 28-day | SR-… |

**Error budget policy:** <e.g. budget = 0.1%/28d; when burned, freeze feature work and spend on reliability.>

## Observability
| Signal | What/where | Used for which SLI |
|---|---|---|
| Metrics | <…> | <SLI> |
| Logs (structured) | <…> | <…> |
| Traces | <…> | <…> |
Dashboards: <links/owners>

## Alerts (symptom-based, each → runbook)
| Alert | Condition (symptom) | Severity / page? | Runbook |
|---|---|---|---|
| <name> | SLO burn / error-budget alert | page / ticket | <link> |

## Runbooks (critical paths)
For each: **detect → diagnose → mitigate → roll back → escalate.** One runbook per
recurring failure mode, at `docs/runbooks/<service>/<symptom>.md`, shaped as:

```markdown
# Runbook — <Service>: <Symptom>
**Alert:** <alert name/condition> · **SEV default:** <1/2/3> · **Last updated:** <date>

## Symptoms            <observable signals>
## Quick checks        <command or URL to verify, numbered>
## Mitigation steps    <exact commands/actions, numbered>
## If mitigation fails <escalate to whom; manual fallback>
## Root-cause clues    <log pattern / metric that distinguishes known causes>
## Prevention          <post-incident action items / ADR links>
```

- <path>: <runbook link>

## Deploy & rollback
- Strategy: <canary / blue-green / feature flags> · rollback tested? <y/n> · trigger: <SLO breach>

## Capacity & cost
- Headroom for SRS scale target <N>; scaling approach <…>; cost guardrail <…>.
