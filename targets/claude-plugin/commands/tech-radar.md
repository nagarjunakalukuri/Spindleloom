---
description: Create or maintain the technology radar — the architect-owned Adopt/Trial/Assess/Hold snapshot that aligns tech choices across teams.
argument-hint: [create|update|review]
---

Manage the **technology radar** (`templates/tech-radar-template.md`) — the cross-team snapshot of sanctioned tech choices. Mode: **$1** (default: `create` if none exists, else `review`). See `agents/tech-radar.md`.

## create
1. Seed from existing decisions: scan `docs/adr/`, `coding-standards`, and the TSD for chosen tech; place each as a blip in its quadrant (Languages & Frameworks / Tools / Platforms / Techniques) and ring (Adopt / Trial / Assess / Hold) with a one-line rationale.
2. Add **Hold** entries for deliberately rejected options, citing the rejecting ADR/RFC.
3. Date it, set the architect owner, save as `docs/tech-radar/YYYY-QN.md`.

## update
Move a blip one ring (or add one), citing the ADR/RFC that drove the move and noting the previous ring. If a significant move has no ADR, prompt to record one (`/adr-new`) first — the radar reflects decisions, it doesn't make them.

## review
Check every blip has a ring + rationale; flag blips with no driving ADR, tech in the TSD/code that isn't on the radar (ungoverned), and a stale snapshot date. Read-only.

Remember: **Hold means no new usage, not removal.** The radar is how a decision by one team becomes visible to frontend/backend/systems alike.
