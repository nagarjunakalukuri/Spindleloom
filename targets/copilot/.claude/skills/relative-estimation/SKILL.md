---
name: relative-estimation
description: Size work by relative effort, not invented hours — story points on a modified-Fibonacci scale, reference-class anchoring ("this is like that 5"), Planning Poker to surface disagreement, and spikes/decisions marked unsized. Derive velocity and capacity from history, not optimism. Use when estimating a backlog or running Planning Poker. Consumed by estimation-facilitator, backlog-manager, and sprint-planner.
---

# Relative estimation — compare, don't predict hours

Humans are bad at absolute time estimates and good at relative comparison. Estimate *size*, let *velocity* convert size to time.

## Story points, relatively
- Use a **modified-Fibonacci** scale (1, 2, 3, 5, 8, 13, 20, ?) — the gaps force a choice and encode growing uncertainty.
- **Anchor to a reference class:** keep 1–2 agreed reference stories ("the password-reset was a 3") and size new work *against them* — "is this bigger or smaller than the 3?" — not in hours.
- Points blend effort, complexity, and uncertainty — not just time.

## Planning Poker — disagreement is information
Everyone estimates at once (so no anchoring on the loudest voice), then reveal. A wide spread isn't noise — it means people understand the story differently. **Discuss the spread, re-estimate.** The conversation is the value; the number is the byproduct.

## Spikes, decisions, and the unknown
- Too big to estimate → **split it** (SPIDR), or
- Too unknown to estimate → a **timeboxed spike** (a research task with a deadline, not a point estimate), or a Decision PBI (→ `architecture-decision-framing`). Don't guess a number onto genuine unknowns.

## Velocity & capacity from history
- **Velocity** = points completed per sprint, averaged over the last few — measured, not chosen.
- **Capacity** = velocity adjusted for this sprint's real availability (leave, holidays, support load).
- Plan to capacity; an overcommitted sprint just moves the failure to the end.

## Smells
- Estimating in hours/days → you've left relative estimation; re-anchor to points.
- One person estimates for the team → no shared understanding, no surfaced disagreement.
- A number forced onto a true unknown → spike it instead.
- Velocity treated as a target to inflate → Goodhart's law; it's a measurement, not a goal.
