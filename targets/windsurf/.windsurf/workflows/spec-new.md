---
description: Scaffold a new spec-driven document set for a feature/initiative in the canonical docs/ + .spindleloom/ layout, sized to the team.
argument-hint: <feature-name> [lean|mid|enterprise]
---

Scaffold the canonical project layout for feature **$1** (kebab-case), per `project_guides/INFORMATION-ARCHITECTURE.md`.

Steps:
1. Pick the team tier ($2 if given, else ask team size once) via `doc-strategy-advisor` logic. Lean = 1-pager PRD + RFC; Mid = PRD + FRD-in-tickets + SDD; Enterprise = BRD→PRD→SRS→SDD (+MRD if market-facing).
2. Lay down the skeleton — run `python hooks/scaffold.py . --tier <tier> --feature $1` (or, if the script isn't available, create the layout by hand): durable funnel in `docs/product/`, per-feature docs in `docs/specs/$1/`, `docs/adr/` + `docs/rfc/`, a seeded `docs/RTM.md`, and `.spindleloom/config.json`. The script is idempotent and won't overwrite existing files.
3. Fill each scaffolded stub from its `templates/<doc>-template.md` — complete the metadata header table (Owner/Status/Version/Last updated), the problem/why, and a TODO list of remaining sections. Don't fabricate requirements; mark unknowns as open questions.
4. Seed `docs/RTM.md` from the BRD/PRD, and create `docs/backlog.md` from `backlog-template.md` if the set includes FRD/SRS (or hand the backlog to the work tracker — see `project_guides/INFORMATION-ARCHITECTURE.md`).
5. Assign one owner per document (BEST-PRACTICES rule #4) — ask if unknown.

Use the `<DOC>-<AREA>-<NUM>` Req-ID convention. Report which docs you created and which agent should fill each next. Then `python hooks/build_artifact_registry.py .` to catalog them.
