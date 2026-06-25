# Epic — <capability name>

> For work too large for one sprint. An epic is a **placeholder, progressively decomposed** as it nears the top of the backlog (see `project_guides/STORY-CRAFT.md` §6). The system of record is the work tracker; this file is the staging/source artifact synced to it.

| Field | Value |
|---|---|
| Epic ID | <EPIC> |
| Owner | <name> |
| Status | Proposed / Active / Done |
| Last updated | <YYYY-MM-DD> |

## Problem / context
<The forces in play — what's broken or missing today, and why it matters now. Neutral, no solution yet.>

## Goal (measurable)
<The business outcome, ideally a metric: "reduce X by Y%", "onboard a client with no code", "cut Z to N". If you can't make it measurable, say how you'll know it's done.>

## Type
- [ ] **Compound** — multiple shorter stories; split by CRUD verb or data boundary
- [ ] **Complex / uncertain** — timebox a spike first, then write the real stories

## Scope
- **In:** <what this epic covers>
- **Out:** <explicit exclusions — prevents scope creep>

## Child stories (vertical slices)
1. <slice — delivers standalone, user-visible value>
2. <...>

> Compound → split by CRUD/data. Complex → story 1 = timeboxed spike; story 2 = the real feature. Each child must be an INVEST-valid, vertically-sliced story (see `project_guides/STORY-CRAFT.md` §4).

## Success criteria / Done when
<Epic-level success measure or metric — the condition under which the epic is complete. Distinct from any single story's acceptance criteria.>

## Refs
<Source brief / PRD / FRD / ADR / RTM ids.>
