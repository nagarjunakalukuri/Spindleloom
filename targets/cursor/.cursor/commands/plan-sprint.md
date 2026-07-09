---
description: Plan a sprint — one goal, a capacity-fit set of Ready items, verified blockers, committed-vs-capacity math, deferrals with reasons.
argument-hint: [sprint-number]
---

Run **sprint-planner** for sprint **$1**. See `agents/sprint-planner.md`. Consumes the estimated backlog (`/plan-estimate`) and capacity.

1. Propose one coherent **Sprint Goal** from the top of the backlog.
2. Select Ready items in priority order up to capacity (with slack). Definition of Ready is a hard gate: bounce unready items back to refinement.
3. "No blocking dependency" means **verified** — every blocked-by link resolves to a real, cleared item; a ghost or uncleared blocker bounces the item regardless of points.
4. Every risk mitigation the sprint depends on must map to a committed, owned work item.
5. Output: goal, committed items (points), committed-vs-capacity, deferred items with reasons, risks. Be honest when a mandate doesn't fit — show the math, don't wish it away.
