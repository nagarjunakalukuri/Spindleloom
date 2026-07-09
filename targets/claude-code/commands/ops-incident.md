---
description: Run a production incident — declare/triage severity, mitigate first, then a blameless postmortem with owned action items, and runbook updates.
argument-hint: [declare|postmortem|runbook]
---

Run **incident-responder**. Mode: **$1** (default: `declare`). See `agents/incident-responder.md`.

## declare
Set severity (SEV-1–4), name the incident commander, open the timeline, and **mitigate first** — restore service before root-causing (rollback beats debugging in prod).

## postmortem
Blameless, from the timeline: impact, detection, root cause (5-Whys — systems, not people), what went well/poorly, and **owned action items** routed to the backlog (`backlog-manager`), debt register (`tech-debt-keeper`), and RAID log. Every incident should spawn at least one test or guardrail in a cheaper loop.

## runbook
Create/update the runbook for this failure class so the next on-call resolves it from the page, not from archaeology; hand to `sre` to keep with the reliability plan.
