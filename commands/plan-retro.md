---
description: Run a blameless sprint retrospective grounded in sprint data — what worked, what didn't, and 1–3 owned, tracked action items.
argument-hint: [sprint-number]
---

Run **retrospective-facilitator** for sprint **$1**. See `agents/retrospective-facilitator.md`.

1. Start with last retro's action items: done, helping, or stalled? Unfinished actions are the first smell.
2. Ground in data: committed vs delivered points, carry-over, defect/incident counts, gate trips, and the escaped-defect register's trend (a gate topping "should have caught it" twice running is an automatic topic) — not vibes.
3. Facilitate blamelessly (pick a format that fits the sprint's mood); systems and process, never people.
4. Converge on **1–3 action items**, each with an owner, a concrete change, and a way to tell it worked. Route them: tracker via `backlog-manager`, debt via `tech-debt-keeper`, systemic design themes to `sdd-writer`/`spec-steward`.
5. Save to `docs/sprints/<sprint>/retro.md`.
