---
name: defect-triage
description: Turn a noisy bug queue into an ordered, owned, deduplicated one — severity vs priority as independent axes, duplicate detection, cluster analysis, fix-now/defer economics, and routing to the right owner. Use when triaging incoming bugs, grooming a defect backlog, or when "everything is P1". Consumed by bug-triager; feeds debugger (fix-now), backlog-manager (defer-as-PBI), and the escaped-defect register.
---

# Defect triage — order the queue, don't just sort it

## Severity and priority are different questions

- **Severity** = technical impact, set from the report's evidence: S1 data-loss/crash/security ·
  S2 major function broken, no workaround · S3 broken with workaround · S4 cosmetic.
- **Priority** = business urgency, set with the PM: P1 fix now → P4 someday.
- They cross: a cosmetic typo on the pricing page is S4/P1; a rare crash in an admin tool
  can be S1/P3. Conflating them is how triage misfires — set both, independently.

## The triage pass (per bug, ~2 minutes)

1. **Reproducible?** No repro steps → back to reporter with what's missing; an
   irreproducible bug is noise until it isn't.
2. **Duplicate?** Search by symptom AND by suspected area — duplicates cluster under
   different words. Link, don't close-silently; the dup count is signal (frequency = priority fuel).
3. **Severity** from evidence; **priority** with the business.
4. **Route by nature**: fix-now → `debugger` with the repro; defer → typed Bug PBI via
   `backlog-manager` (it enters the ordered backlog, not a shadow queue); not-a-bug →
   requirement gap, flag the frd/srs-writer.
5. **Escape check**: anything S1/S2 found in QA/prod gets an escaped-defect register row —
   which gate should have caught it?

## Cluster analysis (the grooming pass)

Weekly, look across the queue, not at items: duplicates by area = a hot spot (route the
*cluster* to tech-debt or a retro topic, not five separate fixes); duplicates by reporter
persona = a UX gap; rising S3 trickle in one component = rot announcing itself.

## Fix-now vs defer economics

Fix now when: user-facing S1/S2, regression of something that worked, cheap-while-hot
(< the cost of re-context later), or it blocks other work. Defer when it's stable, worked
around, and priced into the backlog honestly — a deferred bug with no PBI is a hidden liability.

## Anti-patterns

| Smell | Fix |
|---|---|
| "Everything is P1" | priority is relative; force-rank the top 5 with the PM |
| Severity negotiated by who shouts | severity comes from evidence, priority from business |
| Duplicates closed as noise | linked dups measure frequency — that's data |
| Deferred bugs living in a side list | defer = typed PBI in the one backlog |
