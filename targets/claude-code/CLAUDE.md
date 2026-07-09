# Spindleloom — project conventions (AI-read-first)

This project uses the **Spindleloom** fleet of 52 role-specialist SDLC agents (market → spec → design → build → test → ship → operate), one traceable chain. When a task matches a role, adopt that agent. Run only the subset your team needs — start with `doc-strategy-advisor`.

## The funnel

```
MRD → BRD → PRD → FRD → SRS → SDD → TSD
```
`urs-writer` runs in parallel for regulated systems; `adr-writer` runs continuously.

## Conventions every agent follows

- **Requirement quality:** "the system shall …", one obligation per statement (ISO/IEC/IEEE 29148 + INCOSE). No vague/compound requirements.
- **Req-ID convention:** `<DOC>-<AREA>-<NUM>` (e.g. `PRD-AUTH-001`). Every requirement carries an ID and is traced in the RTM.
- **Traceability:** one RTM per initiative, kept living — business goal → story → requirement → design → test/PBI. Nothing dropped, blast radius visible.
- **Context first:** `recall_context(task_id=...)` before reading; prefer `search_specs`/`trace_requirement` and context packs (`hooks/build_context_pack.py`) over folder-wide reads; save ≤5 bullets before handing off.
- **Layout standard:** the canonical `docs/` + `.spindleloom/` tree, the profiles, and the four cadence planes (durable/living/cyclic/snapshot) are fixed by `project_guides/STANDARD.md`; existing repos convert via `scaffold.py migrate`, never by hand.
- **Right-sized output:** the leanest doc that does the job for the team's tier; fight documentation fatigue.
- **Ground, don't fabricate:** read the upstream doc(s) first; flag assumed values.

The full standard (feedback loops, change control, team-size tiers, frameworks) is in `project_guides/BEST-PRACTICES.md` (bundled). Navigate the fleet by phase in `AGENTS.md` / `agents/INDEX.md`.
