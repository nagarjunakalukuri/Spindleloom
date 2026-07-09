# RTM — MedRemind (living traceability matrix)

**Seeded by `doc-strategy-advisor` from `brief.md` + `01-doc-strategy.md` (2026-07-10).** This agent owns no requirement column (`rtm_column: "—"`); it lays down (a) the **business-goal skeleton** (leftmost column, drawn from the brief's stated targets) and (b) the **Document Register** so downstream writers have a matrix to append into. Downstream writers append their columns/rows and never change an ID once assigned: `brd-writer` fills "Business requirement (BRD)", then `urs-writer`, `prd-writer`, `frd-writer`/`backlog-manager`, `srs-writer`, `sdd-writer`/`tsd-writer`, and `test-plan-writer` in column order. Cells shown as `—` are **pending downstream**, not "none".

## Requirements matrix

| Business goal (brief) | Business requirement (BRD) | User req (URS) | Product requirement (PRD) | Functional (FRD/PBI) | Constraint (SRS) | Design (SDD/TSD) | Test case |
|---|---|---|---|---|---|---|---|
| On-time refill 41%→60% within 2 quarters | BR-OUTCOME-001, BR-REFILL-001, BR-REFILL-002, BR-QUEUE-001, BR-QUEUE-002, BR-SUB-001, BR-SUB-002 | URS-USE-001, URS-USE-002, URS-USE-003, URS-USE-004, URS-USE-005, URS-USE-006, URS-USE-007, URS-SAF-003, URS-DAT-002, URS-DAT-003 | PRD-RMD-001, PRD-RMD-002, PRD-RFL-001, PRD-QUE-001, PRD-QUE-002, PRD-QUE-003, PRD-SUB-001, PRD-SUB-002 | PBI-RMD-001, PBI-RMD-002, PBI-RFL-001, PBI-QUE-001, PBI-QUE-002, PBI-QUE-003, PBI-SUB-001, PBI-SUB-002 (FRD ids per §Functional decomposition below) | SR-SEC-003, SR-SEC-004, SR-DAT-001, SR-DAT-002, SR-AUD-001, SR-AUD-002, SR-AUD-004, SR-INT-003 | SDD-ARC-001, SDD-ARC-003, SDD-ARC-004, SDD-CMP-001, SDD-CMP-003, SDD-CMP-004, SDD-CMP-005, SDD-CMP-006, SDD-CMP-007, SDD-CMP-008, SDD-DAT-003, SDD-DAT-004, SDD-DAT-005, SDD-DAT-006 | — |
| Reminder delivered within 5 min of scheduled time | BR-NFR-001 | — (NFR; `srs-writer` owns CON-4; URS §3 states it as operating condition only) | — | — | SR-PERF-001, SR-CAP-001, SR-REL-001, SR-REL-002, SR-INT-001, SR-OBS-002 | SDD-ARC-003, SDD-ARC-005, SDD-CMP-001, SDD-CMP-004, SDD-CMP-012, SDD-DAT-002, SDD-DAT-007, SDD-NFR-001, SDD-NFR-003, SDD-NFR-004 | — |
| Queue page loads < 2s at 500 concurrent pharmacists | BR-NFR-002 | — (NFR; `srs-writer` owns CON-4; URS §3 states it as operating condition only) | — | — | SR-PERF-002 | SDD-CMP-006, SDD-NFR-002 | — |
| 99.9% availability during store hours | BR-NFR-003 | — (NFR; `srs-writer` owns CON-4; URS §3 states it as operating condition only) | — | — | SR-AVL-001, SR-OBS-001 | SDD-NFR-003, SDD-NFR-004, SDD-CMP-012 | — |
| Zero controlled-substance compliance violations (DEA / state-board) | BR-CTRL-001, BR-CTRL-002, BR-CTRL-003, BR-CTRL-004 | URS-SAF-001, URS-SAF-002, URS-SAF-004, URS-SEC-001 | PRD-CTRL-001, PRD-CTRL-002, PRD-CTRL-003, PRD-CTRL-004 | PBI-CTRL-001, PBI-CTRL-002, PBI-CTRL-003 (FRD ids per §Functional decomposition below) | SR-SEC-006, SR-AUD-003 | SDD-ARC-002, SDD-CMP-002, SDD-CMP-009, SDD-SEC-004, SDD-DAT-001, SDD-DAT-009 | — |
| Zero HIPAA/PHI-minimization violations in notifications | BR-PHI-001, BR-PHI-002 | URS-DAT-001 | PRD-PHI-001 | PBI-PHI-001 (FRD ids per §Functional decomposition below) | SR-SEC-001, SR-SEC-002, SR-SEC-005, SR-PHI-001, SR-PHI-002, SR-PHI-003, SR-INT-002 | SDD-ARC-002, SDD-SEC-002, SDD-SEC-003, SDD-CMP-003, SDD-CMP-011 | — |

## Document Register (owned by doc-strategy-advisor)

Stable identifiers for the recommended document set (see `01-doc-strategy.md` §3). These are **document ids, not requirement Req-IDs** — they name *which document*, so the wiki and downstream agents can reference a source unambiguously.

| Reg id | Document | Owner | Runs agent(s) | Disposition |
|---|---|---|---|---|
| DOC-001 | 1-pager PRD (BRD + PRD merged) | PM (acting PO) | brd-writer + prd-writer | Merge |
| DOC-002 | Lean RFC / Tech Design (SRS + SDD + TSD merged) | Architect | srs-writer + sdd-writer + tsd-writer | Merge |
| DOC-003 | URS (lean, regulated) | QA (validation) | urs-writer | Keep |
| DOC-004 | Threat model + security requirements (section of DOC-002) | Architect | security-reviewer | Merge |
| DOC-005 | Test plan + RTM | QA | test-plan-writer | Keep |
| DOC-006 | ADR log (append-only) | Architect | adr-writer | Keep |
| DOC-007 | Functional behavior → Azure Boards PBIs | PM writes / QA reviews AC | frd-writer (hard cases) + backlog-manager | Drop standalone FRD |
| DOC-008 | Project wiki (home / index) | Architect or PM | wiki-curator | Keep |

## Functional decomposition (FRD → PBI) — appended by `frd-writer` (DOC-007, `05-frd.md`)

Each functional requirement (`05-frd.md`) traced to its PRD/URS source and the seeded PBI that carries it to Azure Boards. Atomic IDs only. PBI defining rows (ranked, AC-bearing) live in `05-frd.md` §Seeded PBIs — `backlog-manager` owns final ranking/estimates and the non-hard-flow remainder.

| Functional req (FRD) | Traces to (PRD / URS) | Seeded PBI |
|---|---|---|
| FRD-RMD-001 | PRD-RMD-001, PRD-RMD-002, URS-USE-001, URS-USE-002 | PBI-RMD-001 |
| FRD-RMD-002 | PRD-RMD-001 | PBI-RMD-001 |
| FRD-RMD-003 | PRD-RMD-001 | PBI-RMD-001 |
| FRD-RMD-004 | PRD-RFL-001 | PBI-RMD-001 |
| FRD-RMD-005 | PRD-RMD-001 | PBI-RMD-001 |
| FRD-RMD-006 | PRD-RMD-002 | PBI-RMD-001 |
| FRD-RMD-007 | PRD-RMD-001 | PBI-RMD-002 |
| FRD-RMD-008 | PRD-RMD-001, BR-NFR-001 | PBI-RMD-002 |
| FRD-RFL-001 | PRD-RFL-001, URS-USE-003 | PBI-RFL-001 |
| FRD-RFL-002 | PRD-RFL-001 | PBI-RFL-001 |
| FRD-RFL-003 | PRD-RFL-001 | PBI-RFL-001 |
| FRD-QUE-001 | PRD-QUE-001, URS-USE-004 | PBI-QUE-001 |
| FRD-QUE-002 | PRD-QUE-001, URS-USE-004 | PBI-QUE-001 |
| FRD-QUE-003 | PRD-QUE-002, URS-USE-005 | PBI-QUE-002 |
| FRD-QUE-004 | PRD-QUE-002, URS-USE-005, URS-DAT-002 | PBI-QUE-002 |
| FRD-QUE-005 | PRD-QUE-003, URS-USE-006 | PBI-QUE-002 |
| FRD-QUE-006 | PRD-QUE-003, URS-USE-006, URS-DAT-002 | PBI-QUE-002 |
| FRD-QUE-007 | PRD-QUE-002, URS-DAT-002 | PBI-QUE-003 |
| FRD-SUB-001 | PRD-SUB-001, URS-USE-007 | PBI-SUB-001 |
| FRD-SUB-002 | PRD-SUB-002, URS-SAF-003 | PBI-SUB-001 |
| FRD-SUB-003 | PRD-SUB-002, URS-SAF-003 | PBI-SUB-002 |
| FRD-SUB-004 | PRD-SUB-002, URS-DAT-003 | PBI-SUB-002 |
| FRD-SUB-005 | PRD-SUB-002, URS-SAF-003 | PBI-SUB-002 |
| FRD-CTRL-001 | PRD-CTRL-001, URS-SAF-001 | PBI-CTRL-001 |
| FRD-CTRL-002 | PRD-CTRL-002, URS-SAF-002 | PBI-CTRL-002 |
| FRD-CTRL-003 | PRD-CTRL-003, URS-SAF-004 | PBI-CTRL-003 |
| FRD-CTRL-004 | PRD-CTRL-004, URS-SEC-001 | PBI-CTRL-003 |
| FRD-CTRL-005 | PRD-CTRL-001, URS-SAF-001, ASSUMPTION-14 | PBI-CTRL-001 |
| FRD-PHI-001 | PRD-PHI-001, URS-DAT-001 | PBI-PHI-001 |
| FRD-PHI-002 | PRD-PHI-001, URS-DAT-001 | PBI-PHI-001 |
| FRD-PHI-003 | PRD-PHI-001, URS-DAT-001 | PBI-PHI-001 |
| FRD-PHI-004 | PRD-RMD-001, PRD-PHI-001 | PBI-PHI-001 |

*Note: FRD-CTRL-002 and FRD-CTRL-005 also gate the one-tap path; PBI-CTRL-002 carries FRD-CTRL-002 with FRD-CTRL-005 as its fail-closed guard (see `05-frd.md` §Seeded PBIs).*

## SRS constraint decomposition (SR → source) — appended by `srs-writer` (DOC-002 §Constraints & NFRs, `06-srs.md`)

Each software constraint (`06-srs.md`) traced to its upstream source. Atomic IDs only. Design (SDD/TSD) and test-case columns are filled downstream by `sdd-writer`/`tsd-writer` and `test-plan-writer`.

| Constraint (SRS) | Traces to (brief / CON / BR-NFR / FRD / URS) |
|---|---|
| SR-PERF-001 | BR-NFR-001, CON-4, FRD-RMD-001, FRD-RMD-008 |
| SR-PERF-002 | BR-NFR-002, CON-4, FRD-QUE-001, URS-USE-004 |
| SR-CAP-001 | BR-NFR-001, CON-4, FRD-RMD-001 |
| SR-AVL-001 | BR-NFR-003, CON-4 |
| SR-REL-001 | BR-NFR-001, FRD-RMD-007, FRD-RMD-008 |
| SR-REL-002 | BR-NFR-001, FRD-RMD-001 |
| SR-SEC-001 | URS-DAT-001, CON-2 |
| SR-SEC-002 | BR-PHI-001, CON-2 |
| SR-SEC-003 | FRD-QUE-001, URS-USE-004 |
| SR-SEC-004 | FRD-QUE-004, FRD-QUE-006, URS-DAT-002 |
| SR-SEC-005 | CON-2, URS-DAT-001 |
| SR-SEC-006 | FRD-CTRL-004, URS-SEC-001, CON-3 |
| SR-PHI-001 | FRD-PHI-001, FRD-PHI-002, URS-DAT-001, CON-2 |
| SR-PHI-002 | FRD-PHI-004, PRD-PHI-001 |
| SR-PHI-003 | BR-PHI-001, URS-DAT-001 |
| SR-INT-001 | CON-1, FRD-RMD-007 |
| SR-INT-002 | CON-1, FRD-PHI-004 |
| SR-INT-003 | FRD-RMD-008 |
| SR-DAT-001 | FRD-RFL-002 |
| SR-DAT-002 | FRD-QUE-007, URS-DAT-002 |
| SR-AUD-001 | URS-DAT-002, URS-DAT-003, FRD-QUE-004 |
| SR-AUD-002 | FRD-QUE-004, FRD-QUE-006, FRD-SUB-004 |
| SR-AUD-003 | URS-DAT-002 |
| SR-AUD-004 | URS-DAT-002, FRD-QUE-004 |
| SR-OBS-001 | SR-PERF-001, SR-PERF-002, SR-AVL-001 |
| SR-OBS-002 | FRD-RMD-008 |

## SDD design decomposition (SDD → source) — appended by `sdd-writer` (DOC-002 §Design, `07-sdd.md`)

Each design element (`07-sdd.md`) traced to the SRS/FRD/PRD requirement it satisfies. Atomic IDs only. SDD is not a requirement-defining doc — these IDs name *design structure* that satisfies the upstream requirements; the test-case column is filled downstream by `test-plan-writer`. Concrete versions/schemas/endpoints are the `tsd-writer`/`api-designer`/`data-modeler` sections of DOC-002.

| Design element (SDD) | Kind | Satisfies (SR / FRD / PRD / CON) |
|---|---|---|
| SDD-ARC-001 | Architecture decision — modular deployment shape | CON-5 |
| SDD-ARC-002 | Architecture decision — compliance choke points | SR-SEC-006, SR-PHI-001, FRD-CTRL-001, FRD-CTRL-005, FRD-PHI-001 |
| SDD-ARC-003 | Architecture decision — event-driven idempotent pipeline | SR-PERF-001, SR-CAP-001, SR-DAT-001, SR-REL-001, SR-INT-001 |
| SDD-ARC-004 | Architecture decision — append-only audit, same-txn commit | SR-AUD-001, SR-AUD-002 |
| SDD-ARC-005 | Architecture decision — durable post-outage catch-up | SR-REL-002 |
| SDD-CMP-001 | Component — Reminder Evaluation & Scheduler | FRD-RMD-001, FRD-RMD-002, FRD-RMD-004, FRD-RMD-005, SR-PERF-001, SR-CAP-001 |
| SDD-CMP-002 | Component — Classification Gate (fail-closed) | FRD-CTRL-001, FRD-CTRL-002, FRD-CTRL-005, SR-SEC-006 |
| SDD-CMP-003 | Component — Notification Composer (PHI boundary) | SR-PHI-001, SR-PHI-002, SR-INT-002, FRD-PHI-001, FRD-PHI-002, FRD-PHI-004 |
| SDD-CMP-004 | Component — Channel Dispatch (Push/SMS) | FRD-RMD-007, FRD-RMD-008, SR-REL-001, SR-INT-001, SR-INT-003, SR-OBS-002 |
| SDD-CMP-005 | Component — Refill Request Service | FRD-RFL-001, FRD-RFL-002, FRD-RFL-003, FRD-CTRL-002, SR-DAT-001 |
| SDD-CMP-006 | Component — Queue & Decision Service | FRD-QUE-001, FRD-QUE-002, FRD-QUE-003, FRD-QUE-004, FRD-QUE-005, FRD-QUE-006, FRD-QUE-007, SR-PERF-002, SR-DAT-002, SR-SEC-003, SR-SEC-004 |
| SDD-CMP-007 | Component — Substitution & Consent Service | FRD-SUB-001, FRD-SUB-002, FRD-SUB-003, FRD-SUB-004, FRD-SUB-005 |
| SDD-CMP-008 | Component — Audit / Consent Store | SR-AUD-001, SR-AUD-002, SR-AUD-003, SR-AUD-004, FRD-QUE-004, FRD-QUE-006, FRD-SUB-004 |
| SDD-CMP-009 | Component — Controlled-substance manual path | FRD-CTRL-003, FRD-CTRL-004, SR-SEC-006 |
| SDD-CMP-010 | Component — Notification Preference | FRD-RMD-006 |
| SDD-CMP-011 | Component — API / BFF layer | SR-SEC-003, SR-SEC-005, FRD-PHI-003, FRD-RFL-001 |
| SDD-CMP-012 | Component — Observability & Alerting | SR-OBS-001, SR-OBS-002 |
| SDD-DAT-001 | Data entity — Prescription reference (external, DEA read) | FRD-CTRL-001, FRD-CTRL-005, SR-SEC-006 |
| SDD-DAT-002 | Data entity — ReminderCycle / send ledger | FRD-RMD-001, FRD-RMD-002, FRD-RMD-003, FRD-RMD-005, SR-DAT-001 |
| SDD-DAT-003 | Data entity — RefillRequest | FRD-RFL-001, FRD-RFL-002, SR-DAT-001 |
| SDD-DAT-004 | Data entity — QueueDecision | FRD-QUE-004, FRD-QUE-006, FRD-QUE-007, SR-DAT-002, SR-SEC-004 |
| SDD-DAT-005 | Data entity — Substitution + ConsentRecord | FRD-SUB-003, FRD-SUB-004, FRD-SUB-005 |
| SDD-DAT-006 | Data entity — AuditEntry | SR-AUD-001, SR-AUD-002, SR-AUD-003, SR-AUD-004 |
| SDD-DAT-007 | Data entity — DeliveryAttempt | SR-INT-003, FRD-RMD-008 |
| SDD-DAT-008 | Data entity — NotificationPreference | FRD-RMD-006 |
| SDD-DAT-009 | Data entity — IdentityVerification record | SR-SEC-006, FRD-CTRL-004 |
| SDD-SEC-001 | Security design — authN/authZ/session | SR-SEC-003, SR-SEC-004, SR-SEC-005 |
| SDD-SEC-002 | Security design — PHI-minimisation boundary | SR-PHI-001, SR-PHI-002, SR-INT-002, FRD-PHI-001, FRD-PHI-002, FRD-PHI-003, FRD-PHI-004 |
| SDD-SEC-003 | Security design — encryption + Twilio BAA | SR-SEC-001, SR-SEC-002, SR-PHI-003 |
| SDD-SEC-004 | Security design — controlled-substance safety topology | SR-SEC-006, FRD-CTRL-003, FRD-CTRL-004 |
| SDD-NFR-001 | Non-functional design — dispatch pipeline budget | SR-PERF-001, SR-CAP-001 |
| SDD-NFR-002 | Non-functional design — read-optimised queue projection | SR-PERF-002 |
| SDD-NFR-003 | Non-functional design — availability + redundancy | SR-AVL-001, SR-REL-001, SR-REL-002 |
| SDD-NFR-004 | Non-functional design — observability | SR-OBS-001, SR-OBS-002 |

## Backlog decomposition (PBI → epic / rank / DoR) — appended by `backlog-manager` (DOC-007, `08-backlog.md`)

Final board ownership for the seeded PBIs plus the one enabler `backlog-manager` minted (`PBI-ENABLE-001`). Atomic IDs only. Each PBI's defining, ranked, AC-bearing row lives in `08-backlog.md` §Backlog; the FRD→PBI trace lives in §Functional decomposition above. `Ready?` encodes the doc-strategy §8 DoR gate; a `No` marks a DoR block (chiefly the absent DOC-004 threat model). Sprint is provisional (ASSUMPTION-22); `estimation-facilitator` sets points and `sprint-planner` finalises sprints.

| PBI | Epic | Rank | Priority | Traces to (FRD / SR / URS) | Ready? / DoR block | Sprint (prov.) |
|---|---|---|---|---|---|---|
| PBI-ENABLE-001 | ENABLE | 1 | Must | SR-PHI-003 | Yes — actionable (PM/compliance) | 1 |
| PBI-PHI-001 | PHI | 2 | Must | FRD-PHI-001, FRD-PHI-002, FRD-PHI-003, FRD-PHI-004, URS-DAT-001 | No — DOC-004 absent | 1 |
| PBI-CTRL-001 | CTRL | 3 | Must | FRD-CTRL-001, FRD-CTRL-005, URS-SAF-001 | No — DOC-004 + ASSUMPTION-8, ASSUMPTION-14 | 1 |
| PBI-CTRL-002 | CTRL | 4 | Must | FRD-CTRL-002, FRD-CTRL-005, URS-SAF-002 | No — DOC-004 + ASSUMPTION-8, ASSUMPTION-14 | 1 |
| PBI-RMD-001 | RMD | 5 | Must | FRD-RMD-001, FRD-RMD-002, FRD-RMD-003, FRD-RMD-004, FRD-RMD-005, FRD-RMD-006 | Yes — pending RFC peer-review | 1 |
| PBI-RFL-001 | RFL | 6 | Must | FRD-RFL-001, FRD-RFL-002, FRD-RFL-003, URS-USE-003 | Yes — pending RFC peer-review | 2 |
| PBI-QUE-001 | QUE | 7 | Must | FRD-QUE-001, FRD-QUE-002, URS-USE-004 | Yes — pending RFC peer-review | 2 |
| PBI-QUE-002 | QUE | 8 | Must | FRD-QUE-003, FRD-QUE-004, FRD-QUE-005, FRD-QUE-006, URS-USE-005, URS-USE-006, URS-DAT-002 | Yes — pending RFC peer-review | 2 |
| PBI-RMD-002 | RMD | 9 | Must | FRD-RMD-007, FRD-RMD-008 | Yes — SMS gated by PBI-ENABLE-001 | 2 |
| PBI-CTRL-003 | CTRL | 10 | Must | FRD-CTRL-003, FRD-CTRL-004, URS-SAF-004, URS-SEC-001 | No — DOC-004 + ASSUMPTION-8 + security review | 3 |
| PBI-QUE-003 | QUE | 11 | Must | FRD-QUE-007, URS-DAT-002 | Yes — pending RFC peer-review | 3 |
| PBI-SUB-002 | SUB | 12 | Must | FRD-SUB-003, FRD-SUB-004, FRD-SUB-005, URS-SAF-003, URS-DAT-003 | Yes — consent gate | 3 |
| PBI-SUB-001 | SUB | 13 | Should | FRD-SUB-001, FRD-SUB-002, URS-USE-007 | Yes — release-gated by PBI-SUB-002 | 3 |

*`PBI-ENABLE-001` (Twilio HIPAA BAA, SR-PHI-003) is `backlog-manager`'s single minted enabler — no `frd-writer` PBI carried it, yet it gates production SMS. Azure work-item IDs are written back into an Azure column on board seeding (`hooks/emit_backlog.py`); that column is pending until the board load runs.*

## Estimation decomposition (PBI → points) — appended by `estimation-facilitator` (`09-estimation.md`)

Relative story points (effort + complexity + risk) set by `estimation-facilitator`, replacing `frd-writer`'s seeds (ASSUMPTION-22). This agent owns no requirement column (`rtm_column: "—"`) and defines no new Req-ID — every PBI below has its AC-bearing defining row in `08-backlog.md`. `?` = too unknown to point (spike-gated). Reference anchor: PBI-SUB-001 = 3. Provisional velocity 18–22 pts/sprint (ASSUMPTION-24). Atomic IDs only.

| PBI | Points | Confidence | Estimation note |
|---|---|---|---|
| PBI-ENABLE-001 | Spike | — | Non-dev procurement; excluded from dev velocity |
| PBI-PHI-001 | 5 | Medium | PHI composer boundary; DOC-004 absent |
| PBI-CTRL-001 | 8 | Low | ▲ seed 5→8: unconfirmed DEA-classification read (ASSUMPTION-8, ASSUMPTION-20, ASSUMPTION-23) |
| PBI-CTRL-002 | 3 | Medium | Rides PBI-CTRL-001 gate |
| PBI-RMD-001 | 8 | Low | Largest funnel story; send-window/consent unresolved (ASSUMPTION-11, ASSUMPTION-13); split candidate |
| PBI-RFL-001 | 5 | Medium | Idempotent one-tap request |
| PBI-QUE-001 | 5 | Medium | Read-optimised queue; SR-PERF-002 load |
| PBI-QUE-002 | 8 | Medium | Reasoned same-txn audit rides here |
| PBI-RMD-002 | 3 | Medium | SMS fallback; gated by PBI-ENABLE-001 |
| PBI-CTRL-003 | ? | — | Too unknown — identity-verification mechanism (ASSUMPTION-8), DOC-004 absent → spike first (FLAG to backlog-manager) |
| PBI-QUE-003 | 3 | Medium | Optimistic-concurrency guard |
| PBI-SUB-002 | 5 | Medium | Consent gate before substitute dispensed |
| PBI-SUB-001 | 3 | High | Reference story (= 3) |

*Pointed dev total: 56 across 11 PBIs; PBI-CTRL-003 (`?`) and PBI-ENABLE-001 (spike) sit outside the dev count. Sprints provisional (ASSUMPTION-24); `sprint-planner` owns final selection.*

## Sprint 1 commitment (PBI → sprint) — appended by `sprint-planner` (`10-sprint1-plan.md`)

Final Sprint-1 selection against the Definition of Ready and ~20-pt conservative capacity (ASSUMPTION-24). This agent owns no requirement column (`rtm_column: "—"`) and mints no Req-ID/PBI — it records which existing PBIs the team commits. Atomic IDs only. `Committed?` = pulled into Sprint 1; `Conditional` = committed but DoR-blocked on DOC-004 until it lands (forecast day 3, ASSUMPTION-26). Sprint dates 2026-07-14 – 2026-07-25 (ASSUMPTION-25).

| PBI | Points | Sprint 1 disposition | DoR / gate |
|---|---|---|---|
| PBI-ENABLE-001 | Spike (non-dev) | Committed — start day 1 | Ready now (PM/compliance) |
| PBI-PHI-001 | 5 | Committed — conditional | Clears when DOC-004 lands (ASSUMPTION-26) |
| PBI-CTRL-001 | 8 | Committed — conditional | DOC-004 + ASSUMPTION-8 + ASSUMPTION-14; classification-read spike first |
| PBI-CTRL-002 | 3 | Committed — conditional | DOC-004 + ASSUMPTION-8 + ASSUMPTION-14; rides PBI-CTRL-001 gate |
| PBI-RMD-001 | 8 | Deferred → Sprint 2 | Deps land in Sprint 1; 8 pts exceeds Sprint-1 headroom (CTRL-001 5→8 cascade) |
| PBI-RFL-001 | 5 | Deferred → Sprint 2 | Dependency-chained behind PBI-CTRL-002 |
| PBI-QUE-001 | 5 | Deferred → Sprint 2 | Dependency-chained behind PBI-RFL-001 |
| PBI-QUE-002 | 8 | Deferred → Sprint 2/3 | Dependency-chained behind PBI-QUE-001 |
| PBI-RMD-002 | 3 | Deferred → Sprint 2 | SMS production gated by PBI-ENABLE-001 |
| PBI-CTRL-003 | ? | Not scheduled | Un-pointable; identity-verification spike runs Sprint 1, then re-estimate |
| PBI-QUE-003 | 3 | Deferred → Sprint 3 | Concurrency hardening on PBI-QUE-002 |
| PBI-SUB-002 | 5 | Deferred → Sprint 3 | Consent gate |
| PBI-SUB-001 | 3 | Deferred → Sprint 3 | Release-gated by PBI-SUB-002 |

*Two discovery spikes run in Sprint 1 (classification-read; identity-verification-mechanism) are **not yet PBIs** — flagged to `backlog-manager` to split with AC and to `estimation-facilitator` to point; no PBI ID assigned here to avoid a phantom PBI. DOC-004 authoring is the Day-1 non-code sprint prerequisite (FLAG to `security-reviewer`/architect).*
