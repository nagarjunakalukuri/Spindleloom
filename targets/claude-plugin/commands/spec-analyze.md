---
description: Cross-artifact consistency analysis — find contradictions, coverage gaps, and drift across the spec set before implementation.
argument-hint: [path-to-spec-folder]
---

Run a cross-artifact consistency analysis on the spec set at **$1** (default: the spec folder in context). This is the pre-implementation gate that catches *translation loss between documents* — contradictions and gaps that ID-level traceability misses. Read-only — propose, don't edit.

This command owns the **semantic cross-pair** layer. It does **not** re-do the work of:
- `rtm-check` / `traceability-rtm` skill — ID-level coverage (orphans, uncovered, broken refs). Delegate that; don't reprint its lists.
- `requirement-quality` skill — per-requirement well-formedness. Delegate that.

## What to do

1. Load the artifacts: MRD→TSD funnel docs, `RTM.md`, ADRs, and the backlog/PBIs + test plan if present.
2. Run the `cross-artifact-analysis` skill's six pairwise checks:
   - **Requirement ↔ Design** — each FRD/SRS requirement has an SDD/TSD element that *can satisfy it*; flag requirements whose constraints the chosen architecture cannot meet.
   - **Design ↔ Tasks** — each SDD/TSD component appears in the backlog; flag designed-but-unbuilt and built-but-undesigned.
   - **Requirement ↔ Requirement** — contradictions (two requirements that can't both hold) and duplicate intent under different IDs.
   - **Acceptance criteria ↔ Test plan** — each PBI acceptance criterion has a test case; flag untested criteria.
   - **ADR ↔ current design** — SDD/TSD choices that contradict an *accepted* ADR, or significant decisions with no ADR.
   - **Terminology drift** — one concept named differently across docs.
3. Severity-group every finding: **Blocker** (contradiction that will cause rework) · **Gap** (missing coverage) · **Drift** (stale/divergent) · **Nit** (terminology). Never assume code is correct — the spec is the reference (per `knowledge_hub/BEST-PRACTICES.md`).

## Output

A table: *finding · artifacts involved · severity · which doc to fix*. Then the top 3 blockers with the exact upstream fix (per "update upstream before downstream"). If clean, say so and cite the checks that passed.
