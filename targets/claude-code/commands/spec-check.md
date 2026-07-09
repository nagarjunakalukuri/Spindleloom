---
description: Verify traceability — every requirement traces both ways; report coverage gaps and orphans.
argument-hint: [path-to-spec-folder]
---

Run a traceability audit on the spec set at **$1** (default: spec folder in context). This proves nothing was dropped and shows blast radius, per `project_guides/BEST-PRACTICES.md`.

1. Collect every Req-ID across the docs (BRD/PRD/FRD/SRS) using the `<DOC>-<AREA>-<NUM>` pattern, plus every PBI ID and ADR ID.
2. Read `RTM.md`. For each requirement, confirm it appears in the matrix with **both** an upstream source and a downstream artifact (design and/or PBI/test).
3. Report three lists:
   - **Uncovered** — FRD/SRS IDs with no downstream PBI/test (unbuilt scope).
   - **Orphans** — PBIs/design with no upstream requirement (scope creep, or a missing requirement to add upstream).
   - **Broken refs** — IDs referenced that don't exist, or duplicate IDs.
4. If a `hooks/validate_reqs.py` validator exists, run it and fold in its findings.
5. Output a coverage summary (e.g. "FRD: 8/8 covered, SRS: 11/12 — SR-PERF-002 has no PBI") and the exact fixes. Read-only.
