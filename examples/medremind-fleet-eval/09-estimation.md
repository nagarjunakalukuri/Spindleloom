# Estimation — MedRemind, full backlog (pre-Sprint-1)

| Field | Value |
|---|---|
| Facilitator | estimation-facilitator (**solo mode** — no team session; every row carries rationale + confidence; re-run as Planning Poker with the 4 devs + QA at Sprint-1 refinement) |
| Reference story | PBI-SUB-003 = **2** (single state-guard rule, one clear G/W/T, no integration) |
| Scale | Modified Fibonacci 1, 2, 3, 5, 8, 13, 20, 40, 100 · "?" = spike needed · spikes/decisions unsized (timeboxed) |
| Date | 2026-07-09 |

## Estimates
| Rank | PBI ID | Story (short) | Points | Confidence | Rationale / action |
|---|---|---|---|---|---|
| 1 | PBI-PLAT-001 | Spike: Rx read interface recon | — (timebox 2d) | — | Spikes are unsized; buys down A-6/A-9 risk |
| 2 | PBI-PLAT-002 | Spike: gateway/IdP capability | — (timebox 1d) | — | Unsized; buys down A-22 |
| 3 | PBI-PLAT-003 | Decision: Sched II–V verification method → ADR | — (analysis) | — | Decisions unsized; gates PBI-CTRL-004's "?" |
| 4 | PBI-AUD-001 | Same-transaction append-only audit ledger | 5 | Med | New ledger + transactional wiring + immutability; ~2.5× ref |
| 5 | PBI-REF-001 | One-tap refill + confirmation | 5 | Med | API + mobile UI + store routing across two apps |
| 6 | PBI-REF-002 | Idempotent/retry-safe request | 3 | High | Dedupe key on top of REF-001; SDD already names the key |
| 7 | PBI-CTRL-001 | No reminder/one-tap for controlled | 3 | High | Filter in scheduler + hide control; clear rules |
| 8 | PBI-CTRL-002 | Unknown classification fails closed | 2 | High | Null/unrecognized branch of CTRL-001 = ref-sized |
| 9 | PBI-CTRL-003 | Pharmacist-only contact options | 3 | Med | Portal UI + patient-side suppression check |
| 10 | PBI-QUE-001 | Store-scoped oldest-first queue | 5 | Low | List itself simple; SR-PERF-002 (<2s @500 concurrent) adds read-model + perf-test effort |
| 11 | PBI-QUE-002 | Approve/reject, first-decision-wins | 5 | Med | Concurrency refusal + individual attribution |
| 12 | PBI-PHI-001 | Minimized-template composer + content-lint | 5 | Med | Composer small; release lint gate is real CI work |
| 13 | PBI-REM-001 | Schedule exactly-one reminder 09:00 store-local | 8 | Low | First scheduler infra + timezones + exactly-once; rides on PLAT-001 outcome — **re-estimate after spike** |
| 14 | PBI-REM-002 | Push via existing Firebase + status | 3 | Med | Existing FCM setup; status recording is the work |
| 15 | PBI-REM-003 | Twilio SMS, paced never-dropped, minimized | 5 | Med | Pacing queue under account cap > plain send |
| 16 | PBI-QUE-003 | Outcome notification + rejection next step | 3 | Med | Two events into existing composer/channels |
| 17 | PBI-REM-005 | Cross-channel failover | 3 | Med | Failure-report handling once both channels exist |
| 18 | PBI-CTRL-004 | Verification gate before dispensing | **?** | — | **Unestimable until PLAT-003 ADR picks the method** (⛔D); provisional 5–8 for planning only |
| 19 | PBI-SUB-001 | Propose substitution + in-app prompt | 5 | Med | New Awaiting-patient state + patient prompt UI |
| 20 | PBI-SUB-002 | Accept/decline recorded & honored | 3 | Med | Two transitions + audit hook on AUD-001 |
| 21 | PBI-SUB-003 | Block approval while awaiting patient | **2** | High | **Reference story** |
| 22 | PBI-PLAT-004 | Three SLIs live at go-live | 3 | Med | Emit + dashboard metrics already designed in SDD |
| 23 | PBI-SUB-004 | Withdraw unanswered proposal | 2 | High | One transition, mirrors SUB-003 |
| 24 | PBI-REM-004 | Per-channel opt-out | 3 | Med | Preference check in scheduler + settings UI |
| 25 | PBI-REM-006 | Post-outage catch-up ≤30 min | 5 | Low | Missed-work detection/replay; depends on A-19 |
| 26 | PBI-AUD-002 | Audit query + ≥6-yr retention | 5 | Med | Query API (100% recall) + retention policy |

## Split / spike flags
- **PBI-CTRL-004 = "?"** — do not force a number; sized only after Decision PBI-PLAT-003 lands its ADR (already ranked 3, Sprint 1). Route back to backlog-manager to update AC + size then.
- **No item ≥ 13** — backlog-manager's decomposition is sound; nothing needs splitting. PBI-REM-001 (8, Low) is the watch item: if spike PBI-PLAT-001 finds an unreliable Rx interface, split scheduler-core from data-adaptation.

## Velocity & capacity (no history — conservative)
- Team: 4 devs + 1 QA, two-week sprints, zero velocity history → forecast conservatively for sprints 1–3, then switch to measured velocity (points never converted to hours).
- **ASSUMPTION-EST-1 (owner: PM + team at Sprint-1 planning):** conservative starting forecast ≈ **20 pts/sprint**; new codebase, HIPAA review overhead, single QA.
- Sprint 1 additionally absorbs 3 unsized timeboxed items (2d + 1d spikes + the PLAT-003 analysis) → plan ≤ **15 pts** of stories in Sprint 1.
- Totals: sized backlog = **86 pts** + CTRL-004 (?) + 3 unsized items · 3-sprint slice (ranks 1–22) = **71 pts** + CTRL-004 (?).

## Does the 3-sprint shippable slice fit?
**Not on a conservative forecast — the slice as mapped is over capacity.**
- Demand ≈ 71 pts + CTRL-004 (~5–8 provisional) = **~76–79 pts** vs conservative capacity ≈ **55 pts** (15 + 20 + 20).
- Per-sprint check: Sprint 1 = 19 pts vs ~15 (slightly over, spikes eat capacity); **Sprint 2 = 33 pts vs 20 (the breaking point)**; Sprint 3 = 19 + ? vs 20 (fits only if CTRL-004 ≤ small).
- Options for PM/sprint-planner: **(a)** defer the SUB trio (SUB-001 Should + SUB-002/003, −10 pts → ~66–69, still ~20% over → also move PLAT-004 + QUE-003 to a hardening sprint); **(b)** plan 4 sprints for the slice; **(c)** keep 3 sprints only if measured Sprint-1 velocity ≥ ~24 pts. CTRL must ship whole within whatever slice is chosen (PRD decision log) — it is not a descope lever.
- Recommendation: commit Sprint 1 as mapped minus 1 story (move PBI-CTRL-003 to Sprint 2), re-forecast at Sprint-2 planning with real velocity, and pre-negotiate option (a) with the PO now.

## Notes / friction
- Solo-mode caveat: these are one estimator's numbers — confirm via Planning Poker with the people doing the work before Sprint-1 commitment; divergence > one card step ⇒ discuss, don't average.
- 10 items remain ⛔ not-Ready (A-n batch / PLAT-003); points above are provisional for them — ratification may change scope and therefore size (esp. REM-001 via A-5/6/14, REM-006 via A-19).
- Contract friction: my body says to read FRD/SRS for context, but my contract routes only the backlog (+brief). NFR context (SR-PERF-002, SR-INT-001, SR-AVL-002) reached me only through AC text and Source columns — Low-confidence marks on QUE-001/REM-001/REM-006 partly stem from that.
- Hand-off: → sprint-planner (this file + backlog); ? flag → backlog-manager after PLAT-003.
