---
name: traceability-rtm
description: Build or audit a Requirements Traceability Matrix (RTM) — the chain from business goal → story → requirement → design → test/PBI. Use when creating an RTM, checking coverage, or assessing the blast radius of a change. Returns coverage gaps, orphans, and broken references.
---

# Traceability & the RTM

The RTM is the one artifact that proves nothing was dropped and shows the blast radius of any change (`project_guides/BEST-PRACTICES.md`). One RTM per project/initiative, kept living.

## The chain
```
MRD (market goal) → BRD (scope) → PRD (story) → FRD (behavior)
  → SRS (constraint) → SDD (design) → PBI / test case → defect
```

## Req-ID convention
The shared `<DOC>-<AREA>-<NUM>` convention — canonical definition, prefixes, and examples in `project_guides/BEST-PRACTICES.md`. IDs never change once assigned. RTM-specific: align PBI AREA codes to the FRD AREA codes they trace to, so a row reads cleanly.

## RTM table shape
| Business goal (BRD) | Product story (PRD) | Functional req (FRD) | Software req (SRS) | Design (SDD) | Build/test (PBI) |
|---|---|---|---|---|---|
One business goal per row, traced across every altitude to the item that delivers and the test that verifies it.

## To BUILD an RTM
1. List BRD goals (one per row).
2. For each, attach the PRD story, then the FRD behavior IDs, then the SRS constraint IDs, then the SDD section, then the PBI/test.
3. An empty downstream cell = a gap (unbuilt scope). A populated downstream cell with no upstream = an orphan (scope creep).
4. Add a Decisions index mapping ADR IDs to their files.

## To AUDIT coverage
1. Collect all Req-IDs from BRD/PRD/FRD/SRS + all PBI/ADR IDs.
2. For each requirement, confirm it appears in the RTM with both an upstream source and a downstream artifact.
3. Output three lists:
   - **Uncovered:** FRD/SRS IDs with no PBI/test.
   - **Orphans:** PBIs/design with no upstream requirement.
   - **Broken/duplicate:** referenced IDs that don't exist, or reused IDs.
4. Report a coverage ratio per doc (e.g. "FRD 8/8, SRS 11/12").

## To assess CHANGE blast radius
Follow the row of the thing changing — it names every downstream artifact (story, FRD, SRS, design, PBI/test) that the change touches. That row *is* the impact analysis.

## Tie-in
A `hooks/validate_reqs.py`-style check can automate the audit on every doc edit (see `hooks/HOOKS.md`). The `/spec-check` command runs this on demand.
