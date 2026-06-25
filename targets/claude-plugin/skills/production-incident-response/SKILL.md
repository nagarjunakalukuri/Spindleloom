---
name: production-incident-response
description: Full production incident lifecycle — declare/triage, mitigate, resolve, blameless postmortem, action items. SEV-1–4 matrix, 5-Whys root-cause method, runbook template, and hardening patterns by contributing factor. The shared method for sre, release-manager, and performance-engineer so every incident is handled consistently.
---

> Auto-fires when an agent is responding to a production failure, outage, degradation, or on-call alert.

Production incidents are time-boxed crises. The goal is: **fast mitigation first, root cause second, hardening third.** Skipping any step wastes the incident.

## Severity matrix

| SEV | Definition | Response target | Examples |
|---|---|---|---|
| **SEV-1** | Full outage or data loss — all users affected, revenue/safety impact | Wake the on-call now; response in ≤15 min | Payment service down, DB corruption, security breach |
| **SEV-2** | Major degradation — significant user population affected, workaround exists | Response in ≤30 min | Checkout errors for 20% of users, login 10× slow |
| **SEV-3** | Partial impact — small set of users, internal tool, or non-critical path | Response in ≤4 h (business hours) | Admin panel broken, report email delayed |
| **SEV-4** | Cosmetic or minor — one user, rare edge case, no operational impact | Best-effort, same sprint | Wrong timestamp in footer, rare 404 on old URL |

Declare SEV immediately; you can downgrade later. Failing to declare = slower response.

## Lifecycle

### 1 — Declare and triage (first 5 minutes)
- Page the incident commander (IC) and open the incident channel.
- Post the initial impact statement: *"[SEV-X] <service> is <symptom> affecting <scope> since <time>."*
- Assign roles: **IC** (coordinates, owns comms), **Tech Lead** (diagnoses), **Comms** (stakeholder updates).
- Set a 15-minute checkpoint for SEV-1/2: if not mitigated, escalate.

### 2 — Mitigate (stop the bleeding first)
**Mitigation ≠ fix.** Restore service as fast as possible — rollback, failover, feature-flag off, rate-limit, shed load. Do not wait for root cause.

Mitigation checklist:
- [ ] Can we roll back the last deploy? (fastest)
- [ ] Can we disable the affected feature flag?
- [ ] Can we shed/redirect traffic (route to a backup region, CDN serve stale)?
- [ ] Can we scale up / restart the service to buy time?

Once mitigated: post the all-clear with the mitigation taken. Update SEV if impact changed.

### 3 — Investigate (after mitigation)
Follow `systematic-debugging` for the diagnosis pass:
1. Read the actual error (logs, traces, metrics) — don't guess.
2. Identify the change or load event that coincided with the start of the incident.
3. Narrow to the smallest failing unit.
4. Confirm the fix on a staging environment before applying to production.

Preserve evidence **before** cleaning up: screenshots, log exports, profiling dumps, timeline of changes. The postmortem needs them.

### 4 — Resolve
- Apply the verified fix to production.
- Confirm via metrics/monitors that the service is back at normal SLOs.
- Post the resolution message: *"[RESOLVED] <service> is healthy. Impact duration: <X> min. Fix: <one-liner>."*
- Close the incident channel; hand off to the postmortem owner.

### 5 — Blameless postmortem (within 48 h for SEV-1/2)

> The goal is learning, not blame. Systems fail; focus on the conditions that made failure possible.

**Postmortem structure** (use `templates/postmortem-template.md`):

| Section | What to write |
|---|---|
| **Timeline** | Minute-by-minute from first signal to resolution, sourced from logs — not from memory |
| **Impact** | Duration, user/revenue/SLO impact, customer-visible vs internal |
| **Root cause** | Single sentence: the specific technical condition that made this happen |
| **5-Whys** | Chain: Why did X happen? → Because Y. Why Y? → Because Z. Repeat 4–5× to reach the systemic cause |
| **Contributing factors** | What made it *worse* or *harder to recover*: missing alerts, slow deploys, manual steps |
| **What went well** | Honestly — fast detection, clean rollback, good comms |
| **Action items** | Concrete, owned, time-boxed hardening items (see below) |

**5-Whys example:**
```
Incident: DB query timeout causing 500s on checkout.
Why 1: Query plan changed unexpectedly.  Why? → Stats stale after big data load.
Why 2: Stats not auto-updated after bulk insert.  Why? → autovacuum turned off on that table.
Why 3: autovacuum was disabled in a "performance test" config months ago.  Why? → No config review gate after performance tests.
Root cause: no gate requiring post-test config restoration; stale stats led to a bad plan under load.
```

### 6 — Action items

Each contributing factor maps to a hardening pattern:

| Contributing factor | Hardening pattern |
|---|---|
| No alert on the symptom | Add an SLO burn-rate alert on the affected SLI |
| Alert fired but was noisy / ignored | Tune the alert; fix the underlying flap |
| Root cause was in a blind spot | Add a metric/trace to instrument that path |
| Manual step in the recovery | Automate it (runbook → script → deploy pipeline) |
| Config drift caused by a test | Add a config-restore gate in the test workflow |
| Slow deploy blocked fast rollback | Optimize deploy pipeline for rollback speed |
| Missing runbook | Write one now; link from alert |
| Over-provisioned trust / blast radius | Scope the permissions; add circuit-breaker |

Action item format: `[ ] <what> — owner: @<name>, due: <date>, SEV blocked until done`

---

## Runbook template

> One runbook per recurring failure mode. Store in `docs/runbooks/<service>/<symptom>.md`.

```markdown
# Runbook — <Service>: <Symptom>

**Alert:** <alert name or condition>
**SEV default:** <1/2/3>
**Last updated:** <date>

## Symptoms
- <observable signals>

## Quick checks
1. <command or URL to verify>
2. <…>

## Mitigation steps
1. <exact command or action>
2. <…>

## If mitigation doesn't work
- Escalate to: <person/team>
- Fallback: <manual workaround>

## Root-cause clues
- <log pattern or metric that distinguishes known causes>

## Prevention (post-incident)
- <link to action items / ADR>
```

---

## Style rules
- Mitigate first, root-cause second. Never delay mitigation to understand the cause.
- Declare SEV early; downgrade after, never upgrade after silence.
- Timeline from logs, not memory. Memory of a crisis is unreliable.
- 5-Whys stops when you reach a *systemic* condition (policy, tooling, process) — not "human error."
- Every postmortem ends with an owned, time-boxed action item per contributing factor.
- Blameless: name systems and conditions, not people.
