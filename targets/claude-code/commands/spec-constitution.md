---
description: Create or update the project constitution — the durable, AI-read-first principles and guardrails.
argument-hint: [create|review|update]
---

Manage the project **constitution** (`templates/constitution-template.md`) — the standing source of project law that every contributor, human or AI, reads first. Mode: **$1** (default: `create` if none exists, else `review`).

## create
1. Scaffold from `templates/constitution-template.md`.
2. Consolidate guardrails that already exist — read any `CLAUDE.md`/`AGENTS.md`, `coding-standards`, and `ai-orchestration-policy` and pull *principles* up into the constitution. **Link** to those docs for detail; do not copy their content.
3. Write each principle as a testable rule (apply the `requirement-quality` standard — no vague adjectives). Set Version v1.0, Status Active, today's date, and an owner (eng lead/architect).

## review
- Check each principle is testable and singular.
- Run the `cross-artifact-analysis` skill to confirm no principle is contradicted by the current SDD/TSD or an accepted ADR.
- Report violations and the fix; read-only.

## update
- Append the change and bump the version. If a **principle** changed (not a typo), prompt to record an ADR (`adr-writer`) and supersede rather than silently rewrite — per the change-control model in `project_guides/BEST-PRACTICES.md`.

Output the path written (or, for review, the findings table). The constitution is the rung-2 anchor in the `spec-steward` maturity ladder.
