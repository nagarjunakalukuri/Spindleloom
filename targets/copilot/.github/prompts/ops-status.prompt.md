---
description: Produce an audience-tailored status report with an honest RAG rating, grounded in the backlog, sprint plan, metrics, and RAID log.
argument-hint: [audience]
---

Run **status-reporter** for audience **$1** (default: team lead; also: exec / steering / PM). See `agents/status-reporter.md`.

1. Read the ground truth: backlog + sprint plan (committed vs done), RAID log (open risks/issues), delivery metrics, retro actions, analytics results if present.
2. Rate **RAG honestly** — a watermelon report (green outside, red inside) delays course-correction until it's expensive; amber with a plan beats false green.
3. Tailor altitude to the audience: execs get outcome + asks in 5 lines; the team gets specifics.
4. Every red/amber carries the mitigation and the **ask** (decision, resource, scope call).
5. Save as the period's status report; flag new risks to `raid-keeper`.
