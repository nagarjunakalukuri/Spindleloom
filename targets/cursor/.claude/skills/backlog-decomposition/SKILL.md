---
name: backlog-decomposition
description: Turn approved specs (PRD/FRD/SRS) into a sequenced, pick-up-able backlog of PBIs with testable acceptance criteria, dependencies, and a Definition of Done. Use when a spec is ready to build and the team needs sprint-ready tickets, or to check that a backlog is well-formed. Pairs with the backlog-manager agent.
---

# Backlog decomposition (spec → pick-up-able PBIs)

The bridge from the spec funnel to the sprint board. The output is what engineers pull from, one item at a time.

## What a good PBI is
- **One pick-up-able unit** — independently shippable and demonstrable. "And" in the title → split.
- **Traceable** — carries the upstream FRD/SRS/PRD IDs it satisfies. No trace = scope creep (cut) or missing requirement (flag upstream, don't invent it in the ticket).
- **Testable** — acceptance criteria written Given/When/Then or as a checklist QA can run unaided.
- **Sequenced** — the top of the backlog is always pull-able now; dependencies are explicit.

## Procedure
1. Read PRD stories + FRD behaviors + SRS constraints + any RTM. Start from requirement IDs, not a blank page.
2. Group into **epics** (a screen, flow, or capability), ordered by phase/dependency.
3. For each requirement, write a PBI with: `PBI-<AREA>-<NUM>` (AREA aligned to the FRD), story, acceptance criteria, **Traces** (upstream IDs), **Depends on**, estimate (S/M/L).
4. Separate **verify-existing** work from **build-new** work — they carry very different risk and estimate. (A screen that already exists needs an "un-hide + verify against live API" PBI, not a "build" PBI.)
5. State a shared **Definition of Ready** and **Definition of Done** once.
6. Produce a **suggested pull order** where every step is unblocked when reached.
7. List assumptions and any FRD/SRS ID with no PBI (coverage gap → flag upstream).

## Definition of Ready / Definition of Done
These are one living team artifact — `templates/definition-of-ready-done-template.md` (per `project_guides/BEST-PRACTICES.md`), referenced not redefined. Decompose to PBIs that *can* meet that DoR (upstream IDs exist, acceptance criteria testable, dependencies done or flagged, interface/endpoint confirmed reachable) and that the DoD can later gate; don't restate the gate criteria here.

## Estimation
Relative only (S/M/L or points), never invented hours. Mark spikes and decision-gated items explicitly ("build OR defer — decision required").

## Anti-patterns to catch on review
- A spec marked "done" with no pull-able units.
- PBIs with untestable acceptance criteria ("works correctly").
- A backlog ordered by wish — the top item is blocked.
- FRD/SRS requirements that never become a PBI (silent under-delivery).
