# Worked Example: FreshDesk (Healthy Meal Delivery App)

A full run of the documentation chain for one app, at **overview depth**, to show how the agents interlock. Each document was produced by its specialist agent and hands off to the next; one shared RTM ties them together.

Read them in order:

0. `00-constitution.md` — Project Constitution (`/spec-constitution`) — *the standing guardrails every feature inherits*
1. `01-mrd.md` — Market Requirements (`mrd-writer`) — *is there a market?*
2. `02-brd.md` — Business Requirements (`brd-writer`) — *why build it?*
3. `03-prd.md` — Product Requirements (`prd-writer`) — *what, for the user?*
4. `04-frd.md` — Functional Requirements (`frd-writer`) — *how does it behave?*
5. `05-srs.md` — Software Requirements Spec (`srs-writer`) — *what constraints?*
6. `06-sdd.md` — Software Design (`sdd-writer`) — *how is it architected?*
7. `07-tsd.md` — Technical Spec (`tsd-writer`) — *how is it built?*
8. `08-adr-0001-event-driven-tracking.md` — a decision record (`adr-writer`)
9. `09-rfc-0001-event-driven-tracking.md` — the proposal & debate that *preceded* ADR-0001 (`rfc-facilitator`)
10. `10-tech-radar.md` — the sanctioned tech choices aligning the teams (`tech-radar-curator`)
11. `11-tech-debt-register.md` — owned, quantified debt (some traced from the `/spec-analyze` run) (`tech-debt-keeper`)

**Delivery & governance loop** (the specs become running agile work):
12. `12-backlog.md` — epics → INVEST PBIs, traced to FRD/SRS (`backlog-manager`)
13. `13-estimation.md` — story points + velocity/capacity (`estimation-facilitator`)
14. `14-sprint-plan.md` — Sprint 1 goal + capacity-fit backlog (`sprint-planner`)
15. `15-retrospective.md` — blameless retro → owned action items (`retrospective-facilitator`)
16. `16-raid-log.md` — Risks/Assumptions/Issues/Decisions register (`raid-keeper`)
17. `17-status-report.md` — RAG status grounded in metrics + RAID (`status-reporter`)

- `RTM.md` — the traceability matrix tying business goals → stories → requirements → design → tests, now extended with a **backlog trace** (PBI → FRD/SRS) into the delivery layer.

## What this demonstrates
- **Altitude discipline:** the BRD names no tools; the TSD pins versions and endpoints.
- **Clean handoffs:** each doc references the one above (e.g. FRD acceptance criteria map to PRD stories).
- **Shared IDs:** `FRD-TRK-001`, `SR-FUNC-002`, `ADR-0001` thread through the RTM end-to-end.
- **Feedback in action:** ADR-0001 records an architecture decision that shapes how FRD-TRK-001 is met.

> Figures (market size, SLAs, versions) are illustrative for the example. A real run would cite sources and confirm current tool versions.
