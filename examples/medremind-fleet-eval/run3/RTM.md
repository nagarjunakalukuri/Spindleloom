# RTM — MedRemind (living traceability matrix)

Scaffold seeded by `doc-strategy-advisor` (2026-07-09) so downstream writers inherit the
schema without re-deciding it. `doc-strategy-advisor` authors no requirements (rtm_column `—`)
and adds no rows. **`brd-writer` fills the first requirement rows** from the BRD; then
`urs-writer`, `prd-writer`, `frd-writer`/`backlog-manager`, `srs-writer`,
`sdd-writer`/`tsd-writer`, and `test-plan-writer` append their columns. IDs are atomic and
never change once assigned (no range shorthand).

| Business goal (BRD) | Business requirement (BRD) | User req (URS) | Product requirement (PRD) | Functional (FRD/PBI) | Constraint (SRS) | Design (SDD/TSD) | Test case |
|---|---|---|---|---|---|---|---|
| BG-001 | BR-001 | URS-USE-001, URS-USE-002, URS-USE-003 | PRD-RMD-001, PRD-RMD-002, PRD-RFL-001, PRD-PRF-001 | FRD-RMD-001, FRD-RMD-002, FRD-RMD-003, FRD-RMD-005, FRD-RMD-006, FRD-RMD-007, FRD-RFL-004, FRD-PRF-001 | SR-PERF-001, SR-SCAL-001, SR-SCAL-003, SR-AVL-001, SR-AVL-002, SR-AVL-003, SR-SEC-001, SR-DAT-001, SR-OBS-001, SR-OBS-002, SR-OBS-003 | SDD-ARC-001, SDD-ARC-003, SDD-CMP-001, SDD-CMP-003, SDD-CMP-004, SDD-CMP-008, SDD-DAT-004, SDD-DAT-005, SDD-NFR-001, SDD-NFR-002, SDD-NFR-003 | |
| BG-002 | BR-002 | URS-USE-003 | PRD-RFL-001 | FRD-RFL-001, FRD-RFL-002, FRD-RFL-003 | SR-PERF-003, SR-SEC-002 | SDD-CMP-005, SDD-CMP-011, SDD-DAT-001, SDD-SEC-001, SDD-NFR-001 | |
| BG-003 | BR-003 | URS-USE-004, URS-USE-005, URS-USE-006, URS-DAT-002 | PRD-QUE-001, PRD-QUE-002, PRD-QUE-003 | FRD-QUE-001, FRD-QUE-003, FRD-QUE-004, FRD-QUE-005, FRD-QUE-006, FRD-CFN-001 | SR-PERF-002, SR-SCAL-002, SR-SEC-002, SR-AUD-001, SR-AUD-003, SR-DAT-002 | SDD-CMP-006, SDD-CMP-009, SDD-CMP-010, SDD-DAT-002, SDD-ARC-004, SDD-SEC-001, SDD-NFR-001 | |
| BG-005 | BR-004 | URS-USE-007, URS-SAF-003, URS-DAT-003 | PRD-SUB-001 | FRD-SUB-001, FRD-SUB-002, FRD-SUB-003 | SR-AUD-002 | SDD-CMP-007, SDD-CMP-010, SDD-DAT-003, SDD-ARC-004 | |
| BG-005 | BR-005 | URS-SAF-001, URS-SAF-002, URS-SAF-004, URS-SEC-001 | PRD-CTL-001 | FRD-CTL-001, FRD-CTL-002, FRD-CTL-003, FRD-CTL-004, FRD-QUE-002 | SR-SAF-001, SR-SAF-002, SR-SEC-003 | SDD-ARC-002, SDD-CMP-002, SDD-CMP-012, SDD-DAT-000, SDD-SEC-001 | |
| BG-005 | BR-006 | URS-DAT-001 | PRD-RMD-002 | FRD-RMD-004 | SR-PRIV-001, SR-PRIV-002, SR-PRIV-003, SR-PRIV-004, SR-SEC-004 | SDD-SEC-002, SDD-SEC-003, SDD-CMP-003 | |
| BG-004 | BR-007 | | | | | SDD-ARC-001 | |

## Backlog trace (PBI → FRD/PRD) — appended by `backlog-manager` (2026-07-09, run3)

The matrix above traces requirements down to the *Functional (FRD)* column. This table extends
that chain to the executable **backlog items (PBI)** — atomic IDs only, one row per PBI (no range
shorthand). Each PBI is the tracker-bound unit `test-author` writes cases against; the *Test case*
column is seeded by `test-plan-writer` / `test-author` downstream.

| PBI ID | Type | FRD (functional) | PRD story | BR / BG | SRS / SDD | Test case |
|---|---|---|---|---|---|---|
| PBI-PLAT-007 | Spike | FRD-CTL-003 | PRD-CTL-001 | BR-005 / BG-005 | SR-SAF-001, ASSUMPTION-9, ASSUMPTION-21 | |
| PBI-PLAT-001 | Story | FRD-CTL-003 | PRD-CTL-001 | BR-005 / BG-005 | SR-SAF-001, SR-SAF-002 / SDD-CMP-002 | |
| PBI-PLAT-002 | Story | FRD-RMD-006, FRD-RFL-002, FRD-RMD-007 | PRD-RMD-001, PRD-RFL-001 | BR-001, BR-002 / BG-001, BG-002 | SR-DAT-001 / SDD-CMP-001, SDD-DAT-005 | |
| PBI-PLAT-003 | Story | FRD-RMD-003, FRD-RMD-004 | PRD-RMD-001, PRD-RMD-002 | BR-006 / BG-005 | SR-PRIV-001, SR-PRIV-002 / SDD-CMP-003, SDD-SEC-002 | |
| PBI-PLAT-004 | Story | FRD-QUE-004, FRD-SUB-002 | PRD-QUE-002, PRD-SUB-001 | BR-003, BR-004 / BG-003, BG-005 | SR-AUD-001, SR-AUD-002 / SDD-CMP-010, SDD-ARC-004 | |
| PBI-PLAT-005 | Story | FRD-QUE-001, FRD-RFL-001 | PRD-QUE-001, PRD-RFL-001 | BR-002, BR-003 / BG-002, BG-003 | SR-SEC-001, SR-SEC-002 / SDD-CMP-011, SDD-SEC-001 | |
| PBI-PLAT-006 | Story | FRD-RMD-005 | PRD-RMD-001 | BR-001 / BG-001 | SR-OBS-001, SR-OBS-002, SR-OBS-003 / SDD-NFR-003 | |
| PBI-CTL-001 | Story | FRD-CTL-001 | PRD-CTL-001 | BR-005 / BG-005 | URS-SAF-001, CON-3 / SDD-CMP-002 | |
| PBI-CTL-002 | Story | FRD-CTL-002 | PRD-CTL-001 | BR-005 / BG-005 | URS-SAF-002, CON-3 / SDD-CMP-002, SDD-CMP-005 | |
| PBI-CTL-004 | Story | FRD-CTL-004 | PRD-CTL-001 | BR-005 / BG-005 | SR-SEC-003 / SDD-CMP-012 | |
| PBI-RMD-001 | Story | FRD-RMD-001 | PRD-RMD-001 | BR-001 / BG-001 | URS-USE-001 / SDD-CMP-001 | |
| PBI-RMD-002 | Story | FRD-RMD-002 | PRD-RMD-001 | BR-001 / BG-001 | ASSUMPTION-10, ASSUMPTION-15 / SDD-CMP-001 | |
| PBI-RMD-003 | Story | FRD-RMD-003 | PRD-RMD-001 | BR-006 / BG-005 | URS-DAT-001 / SDD-SEC-002 | |
| PBI-RMD-004 | Story | FRD-RMD-004 | PRD-RMD-002 | BR-006 / BG-005 | URS-DAT-001, CON-2 / SDD-SEC-002 | |
| PBI-RMD-005 | Story | FRD-RMD-005 | PRD-RMD-001, PRD-RMD-002 | BR-001 / BG-001 | — / SDD-CMP-004, SDD-CMP-008 | |
| PBI-RMD-006 | Story | FRD-RMD-006 | PRD-RMD-001 | BR-001 / BG-001 | SR-DAT-001 / SDD-DAT-005 | |
| PBI-RMD-007 | Story | FRD-RMD-007 | PRD-RMD-002 | BR-001 / BG-001 | SR-AVL-002 / SDD-ARC-003, SDD-CMP-004 | |
| PBI-RFL-001 | Story | FRD-RFL-001 | PRD-RFL-001 | BR-002 / BG-002 | URS-USE-003 / SDD-CMP-005 | |
| PBI-RFL-002 | Story | FRD-RFL-002 | PRD-RFL-001 | BR-002 / BG-002 | SR-DAT-001 / SDD-DAT-005 | |
| PBI-RFL-003 | Story | FRD-RFL-003 | PRD-RFL-001, PRD-CTL-001 | BR-002, BR-005 / BG-002, BG-005 | — / SDD-CMP-005 | |
| PBI-RFL-004 | Story | FRD-RFL-004 | PRD-RFL-001 | BR-002 / BG-002 | SR-PERF-003 / SDD-CMP-005 | |
| PBI-QUE-001 | Story | FRD-QUE-001 | PRD-QUE-001 | BR-003 / BG-003 | SR-PERF-002, URS-USE-004, ASSUMPTION-13 / SDD-CMP-006 | |
| PBI-QUE-002 | Story | FRD-QUE-002 | PRD-QUE-001, PRD-CTL-001 | BR-003, BR-005 / BG-003, BG-005 | URS-SAF-002 / SDD-CMP-002 | |
| PBI-QUE-003 | Story | FRD-QUE-003 | PRD-QUE-001 | BR-003 / BG-003 | — / SDD-CMP-006 | |
| PBI-QUE-004 | Story | FRD-QUE-004 | PRD-QUE-002 | BR-003 / BG-003 | SR-AUD-001, URS-USE-005, URS-DAT-002 / SDD-CMP-006, SDD-CMP-010 | |
| PBI-QUE-005 | Story | FRD-QUE-005 | PRD-QUE-003 | BR-003 / BG-003 | SR-AUD-001, URS-USE-006, URS-DAT-002 / SDD-CMP-006 | |
| PBI-QUE-006 | Story | FRD-QUE-006 | PRD-QUE-002 | BR-003 / BG-003 | SR-DAT-002 / SDD-CMP-006, SDD-DAT-002 | |
| PBI-CFN-001 | Story | FRD-CFN-001 | PRD-QUE-002 | BR-003 / BG-003 | URS-DAT-001, ASSUMPTION-12 / SDD-CMP-009 | |
| PBI-SUB-001 | Story | FRD-SUB-001 | PRD-SUB-001 | BR-004 / BG-005 | URS-USE-007 / SDD-CMP-007 | |
| PBI-SUB-002 | Story | FRD-SUB-002 | PRD-SUB-001 | BR-004 / BG-005 | SR-AUD-002, URS-SAF-003, URS-DAT-003 / SDD-CMP-007, SDD-CMP-010 | |
| PBI-SUB-003 | Story | FRD-SUB-003 | PRD-SUB-001 | BR-004 / BG-005 | URS-SAF-003, ASSUMPTION-14 / SDD-CMP-007 | |
| PBI-PREF-001 | Story | FRD-PRF-001 | PRD-PRF-001 | BR-001 / BG-001 | ASSUMPTION-11 / SDD-CMP-008, SDD-DAT-004 | |

## Sprint assignment (ratified) — appended by `sprint-planner` (2026-07-09, run3)

`sprint-planner` authors no requirements (rtm_column `—`) and adds no new IDs. This table maps the
existing atomic PBI IDs to a ratified sprint of the 3-sprint slice (see `10-sprint1-plan.md`). It
supersedes the `backlog-manager` sprint *proposal* per ASSUMPTION-24 (PBI-CTL-001/-002 moved to
Sprint 2 to ship each guard with the surface it protects). Provisional points per ASSUMPTION-25
(estimates handoff undelivered).

| PBI ID | Sprint | Ready state at planning | Prov. pts | Note |
|---|---|---|---|---|
| PBI-PLAT-007 | 1 | Ready (timeboxed spike) | 3 | Day 1–3, architect-led; exit answers ASSUMPTION-9/-21 |
| PBI-PLAT-001 | 1 | Conditionally Ready (gated on PBI-PLAT-007) | 8 | Fail-closed classification gate; inspection + security review |
| PBI-PLAT-002 | 1 | Ready | 5 | Idempotency ledger; no deps |
| PBI-PLAT-003 | 1 | Ready | 5 | PHI-minimization composer; no deps |
| PBI-PLAT-005 | 1 | Ready | 5 | Delegated authN/authZ; no deps |
| PBI-CTL-001 | 2 | Not Ready in S1 (blocked on gate) | 2 | Guards reminder job (PBI-RMD-001) — ships with surface |
| PBI-CTL-002 | 2 | Not Ready in S1 (blocked on gate) | 2 | Guards patient refill surface (PBI-RFL-001) — ships with surface |
| PBI-PLAT-004 | 3 | Blocked — no ranked backlog row (FLAG raised) | — | Audit/consent store; must gain an AC-bearing row before S3 |
