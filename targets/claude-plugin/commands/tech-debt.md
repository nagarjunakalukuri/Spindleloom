---
description: Maintain the technical-debt register — owned, quantified debt items negotiable with the PM and promotable to the backlog.
argument-hint: [add|review|groom]
---

Manage the **technical-debt register** (`templates/tech-debt-register-template.md`). Mode: **$1** (default: `review`). See `agents/tech-debt-register.md`.

## add
Capture a new item: description, **location** (service/file), **type** (design/code/test/infra/doc), **impact** (cost now), **interest** (quantified worsening rate — e.g. "+20 ms/release"), **effort** (S/M/L), source (postmortem/retro/review), owner. Assign the next `DEBT-NNN` and set a decision (pay now / schedule / accept / monitor).

## review
Read the register and report: items missing an owner or decision, items with vague (non-quantified) interest, and anything past threshold that should be promoted to the backlog. Read-only.

## groom
Re-score interest (has it worsened?), retire fixed items, then produce the **PM-negotiation view** — items sorted by impact × interest vs effort with a recommended decision. Group by owning team/service for the cross-team roll-up. Promote "pay now/schedule" items to the backlog via `backlog-manager`, keeping the `DEBT-NNN` ↔ PBI link.

Remember: every item needs an **owner and a decision**; **accepting** debt is valid; promote decided items to the backlog rather than shadow-tracking the work.
