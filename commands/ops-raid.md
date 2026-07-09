---
description: Maintain the RAID log — Risks, Assumptions, Issues, Decisions — each with one owner and a next action; decisions link to ADRs.
argument-hint: [add|review]
---

Manage the **RAID log** (`templates/raid-log-template.md`). Mode: **$1** (default: `review`). See `agents/raid-keeper.md`.

## add
Capture the item with its category (Risk = might happen · Assumption = believed true, unverified · Issue = happening now · Decision = chosen path), an **owner**, impact/likelihood for risks, and the next action. Decisions get one line + a link to the ADR (`/spec-adr`) — never duplicate the ADR's content.

## review
Walk the register: items with no owner or stale next actions, risks whose mitigation has no owning work item (flag to `sprint-planner`), assumptions that are now testable (verify or promote to issue), and unratified `ASSUMPTION-n` tags cited by sprint-committed items. Report what changed since last review.
