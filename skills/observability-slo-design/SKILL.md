---
name: observability-slo-design
description: Design how a service is observed and what "healthy" means — SLIs / SLOs and an error budget, the four golden signals (latency, traffic, errors, saturation), instrumentation at the boundaries (structured logs, metrics, traces, correlation IDs), and alerts that are actionable, not noisy. Use when building a service, setting reliability targets, or wiring alerting. Consumed by sre, backend-developer, performance-engineer, incident-responder, and pipeline-engineer.
---

# Observability & SLO design — you can't operate what you can't see

Decide what "working" means *as a number*, then instrument so you can prove it.

## SLIs, SLOs, error budgets
- **SLI** — a measured indicator of health from the user's view (request success rate, p95 latency, freshness). Measure what users feel, not internal vanity metrics.
- **SLO** — the target for an SLI over a window ("99.9% of reads < 300 ms over 28 days"). Set it from the SRS, not from a wish.
- **Error budget** — `100% − SLO`. It's permission to ship: budget left → ship features; budget burned → stop and harden. Makes the reliability-vs-velocity trade-off explicit instead of political.

## The four golden signals (instrument all four)
**Latency** (split success vs error latency) · **Traffic** (demand) · **Errors** (rate + classes) · **Saturation** (how full the constrained resource is). Most service problems show up in one of these first.

## Instrument at the boundaries
Structured logs (no PII), metrics, and traces on every meaningful path; **correlation IDs** propagated across services so one request is followable end-to-end. Emit the data a future debugger/postmortem will need *before* the incident, not after.

## Alert on symptoms, not causes
- Alert on **SLO burn rate** and user-facing symptoms, not on every CPU blip. Cause-based alerts are noisy and miss novel failures.
- Every alert is **actionable** and links a **runbook** (`sre`); if there's nothing to do, it's a dashboard, not a page.
- Tune for signal: an alert that fires and gets ignored trains the team to ignore alerts.

## Smells
- "It's observable" with no SLI/SLO defined → unmeasurable goal.
- Logs but no traces → can't follow a request across services.
- Alerts on causes (high CPU) instead of symptoms (error budget burning) → noise + blind spots.
- PII or secrets in logs → an information-disclosure incident waiting to happen.
