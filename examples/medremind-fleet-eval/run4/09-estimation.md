# Estimation — MedRemind (story points + capacity forecast · run4)

*Author: `estimation-facilitator` · phase: planning · loop: planning · 2026-07-10 · run4*
*Upstream: `backlog-manager` (`08-backlog.md`, 13 ranked PBIs + seed points). `solution-recon`: **not run / not on disk** — see FLAG.*
*Downstream: `sprint-planner` (final sprint selection), `status-reporter`.*
*Scope source of truth: `brief.md`. RTM: `examples/medremind-fleet-eval/run4/RTM.md` (§Estimation decomposition appended).*

I own no RTM requirement column (`rtm_column: "—"`). I set **relative story points** (effort + complexity + risk) on the `backlog-manager`'s PBIs, replacing `frd-writer`'s rough seeds (ASSUMPTION-22), and forecast how many sprints the backlog spans. Points are **relative, never hours**. I invent **no new PBI**; every id below has its defining AC-bearing row in `08-backlog.md`.

| Field | Value |
|---|---|
| Facilitator | Scrum Master (acting) |
| Estimators | 4 developers + 1 architect (the people doing the work); PM/PO clarifies scope |
| Reference story | **PBI-SUB-001 = 3** — "pharmacist attaches a suggested generic to a queued request, it is recorded and surfaced" — small, well-understood, self-contained |
| Scale | Modified Fibonacci: 1, 2, 3, 5, 8, 13, 20, 40, 100; `0` trivial; `?` too unknown to point (needs a spike) |
| Date | 2026-07-10 |

---

## FLAG & assumptions (read first)

- **FLAG(solution-recon):** no `solution-recon` feasibility pass was routed to me and none is on disk (carried forward from `08-backlog.md`). The point loads on the funnel PBIs assume the existing patient app, pharmacist portal, and the dispensing-system prescription/DEA-classification read expose the surfaces these stories consume (ASSUMPTION-23). **Unconfirmed brownfield surfaces are the dominant uncertainty in every estimate below** and are why I hold velocity to the conservative end of the band. If recon disproves a surface, the affected PBI is re-scoped and **re-estimated** (I do not churn stable estimates otherwise — contract §RE-ESTIMATE).
- **FLAG(backlog-manager):** **PBI-CTRL-003** (controlled-substance manual path + identity verification) is **`?` — too unknown to point.** The identity-verification *mechanism* is unratified (ASSUMPTION-8) and its threat model (DOC-004) is absent, so its scope is not knowable; forcing a number would be false precision. Per contract §"split or spike the outliers" it needs a **spike to resolve the identity-verification mechanism before it can be pointed.** I do not mint the spike PBI myself (that would be a phantom PBI I cannot define with AC) — routing to `backlog-manager` to split a spike out of PBI-CTRL-003, after which I re-estimate the remaining story. This is a **Must** and a non-deferrable launch gate, so its un-estimability is the single largest schedule risk on the board.
- **ASSUMPTION-24** *(owner: `estimation-facilitator` / PM; new)* — with **no velocity history** (brand-new team on a brownfield module), I forecast a conservative provisional velocity of **18–22 delivered points per sprint** (4 developers, 2-week sprint), midpoint **~20**. This tightens `backlog-manager`'s provisional 20–24 (ASSUMPTION-22) downward because of the unconfirmed surfaces (ASSUMPTION-23) and first-time-on-codebase drag. Replace with **measured** velocity after sprint 1; do not treat 18–22 as a target or a commitment.
- Carried unratified upstream (do not treat as decided): **ASSUMPTION-1, ASSUMPTION-8, ASSUMPTION-11, ASSUMPTION-13, ASSUMPTION-14, ASSUMPTION-20, ASSUMPTION-21, ASSUMPTION-23** — notably DEA-classification source + identity mechanism (ASSUMPTION-8), fail-closed default (ASSUMPTION-14), SMS consent/TCPA (ASSUMPTION-11), send window (ASSUMPTION-13). Each inflates the confidence caveat on the PBI it touches.

---

## Estimates (Planning Poker, re-anchored on PBI-SUB-001 = 3)

Points are the team's consensus size relative to the reference. "Δ seed" shows my re-estimate vs `frd-writer`'s seed; where it moved, the rationale is in Notes.

| Rank | PBI ID | Story (short) | Points | Δ seed | Confidence | Notes / action |
|---|---|---|---|---|---|---|
| 1 | PBI-ENABLE-001 | Twilio HIPAA BAA (procure + execute) | **Spike** | (2→spike) | — | Timeboxed procurement/compliance work, **not developer effort — excluded from dev velocity**. Long lead time: start sprint 1 day 1. Blocks production SMS in PBI-RMD-001 / PBI-RMD-002 / PBI-PHI-001. |
| 2 | PBI-PHI-001 | No drug name / PHI in any SMS or push body | **5** | = 5 | Medium | Notification-composer PHI boundary incl. lock-screen preview; app-only drug detail. Uncertainty from DOC-004 (threat model) absent. |
| 3 | PBI-CTRL-001 | Schedule II–V excluded from automated reminders (fail-closed) | **8** | ▲ 5→8 | Low | Raised: the fail-closed gate depends on a DEA-schedule classification read whose **source is unconfirmed** (ASSUMPTION-8 / ASSUMPTION-20 / ASSUMPTION-23) and whose fail-closed default is unratified (ASSUMPTION-14). Recommend a thin **classification-read spike** alongside; if the read cannot serve the gate, split a backend enabler and re-estimate. |
| 4 | PBI-CTRL-002 | Schedule II–V excluded from one-tap self-service | **3** | = 3 | Medium | Rides the PBI-CTRL-001 classification gate (its dep); UI suppression + guard once the gate exists. |
| 5 | PBI-RMD-001 | Timely reminder, capped cadence, re-reminder, opt-out suppression | **8** | = 8 | Low | Largest single funnel story: scheduler + send-window + cadence cap + 48h re-reminder + SMS opt-out, 4 AC branches. Send window (ASSUMPTION-13) and consent-to-contact (ASSUMPTION-11) unresolved. **Split candidate** if scope grows past 8 — route to `backlog-manager`. |
| 6 | PBI-RFL-001 | One-tap refill request, idempotent | **5** | = 5 | Medium | Single-confirmation create + duplicate-suppression (idempotency) + inactive-prescription guard. |
| 7 | PBI-QUE-001 | Pharmacist queue of pending requests + empty state | **5** | = 5 | Medium | Read-optimised projection; must hold the <2s / 500-concurrent NFR (SR-PERF-002) — perf work carries the load. |
| 8 | PBI-QUE-002 | Approve / reject with reasoned, same-transaction audit | **8** | = 8 | Medium | Reason-required reject + attributable, timestamped, same-txn audit entry (audit obligation SR-AUD-001/002 rides here, not a separate PBI). |
| 9 | PBI-RMD-002 | Push-fail → SMS fallback + delivery-failure event | **3** | = 3 | Medium | Fallback path + delivery ledger; SMS production gated by PBI-ENABLE-001. |
| 10 | PBI-CTRL-003 | Controlled-substance manual path + identity verification | **?** | (8→?) | — | **Too unknown to point** — identity-verification mechanism unratified (ASSUMPTION-8), DOC-004 absent. **Spike first** (FLAG to `backlog-manager`), then re-estimate. Top schedule risk. |
| 11 | PBI-QUE-003 | Concurrent decisions on one request handled safely | **3** | = 3 | Medium | Optimistic-concurrency guard: first commit wins, second rejected as already-decided, no duplicate audit. |
| 12 | PBI-SUB-002 | Patient consent gate before a substitute is dispensed | **5** | = 5 | Medium | Consent record + dispensing block; the gate PBI-SUB-001 is release-gated behind. |
| 13 | PBI-SUB-001 | Pharmacist suggests a generic on a request | **3** | = 3 | High | **Reference story (= 3).** Straightforward record + surface against the existing queue. |

**Totals:** pointed developer work = **56 points** across 11 PBIs. Un-pointed: **PBI-CTRL-003** (`?`, spike-gated) and **PBI-ENABLE-001** (spike, non-dev). Net change from the 63-point seed total: seed counted ENABLE (2) and CTRL-003 (8) as dev points and CTRL-001 at 5; my pass moves ENABLE and CTRL-003 out of the dev count and raises CTRL-001 to 8 → 56 dev points + one spike-gated unknown.

---

## Velocity & capacity forecast

- **Velocity:** no history → provisional band **18–22 pts/sprint**, midpoint **~20** (ASSUMPTION-24). Forecast only; re-baseline on measured sprint-1 throughput.
- **Backlog span (pointed work only):** 56 ÷ 20 ≈ **2.8 → ~3 sprints** at midpoint velocity. CON-5's "first shippable slice in 3 sprints" is **achievable for the pointed funnel but at risk**, because two Must items sit outside the 56-point count: PBI-ENABLE-001 (external lead time) and **PBI-CTRL-003 (`?`)**, a non-deferrable launch gate that cannot be scheduled until its spike resolves — realistically pushing it toward a **sprint 3–4** landing.
- **Re-estimate cascade (surface to `sprint-planner` / `backlog-manager`):** raising PBI-CTRL-001 from 5→8 removes the headroom `backlog-manager`'s seed relied on to fit all of PBI-RMD-001 into sprint 1. At a conservative cap (~20) the reminder→one-tap→queue→decision funnel (the 41%→60% lever) does not fully close until **sprint 3** in my forecast, one sprint later than the seed plan. Two levers close the gap: (a) commit to the top of the band (22–24, a stretch for a new team), or (b) `backlog-manager` re-ranks. **Resolution is `sprint-planner`'s call, not mine.**

### Provisional sprint forecast (illustrative — `sprint-planner` owns final selection)

Assumes the sprint-1 prerequisite from `08-backlog.md` holds: architect / `security-reviewer` produce **DOC-004** and ratify ASSUMPTION-8 / ASSUMPTION-14, or the four DoR-blocked CTRL/PHI stories cannot start.

| Sprint | PBIs (points) | Firm dev pts | Rationale |
|---|---|---|---|
| **Sprint 1** | PBI-ENABLE-001 (spike, start) · PBI-PHI-001 (5) · PBI-CTRL-001 (8) · PBI-CTRL-002 (3) + begin PBI-RMD-001 | ~16 firm | Land the two hard gates (PHI + controlled auto-exclusion) and kick the BAA; only ~4 pts headroom under a 20 cap, so PBI-RMD-001 largely spills to sprint 2 (this is the CTRL-001 5→8 cascade). Run the PBI-CTRL-003 identity-verification spike here. |
| **Sprint 2** | PBI-RMD-001 finish (8) · PBI-RFL-001 (5) · PBI-QUE-001 (5) · PBI-RMD-002 (3) | 21 | Complete the reminder + one-tap + queue read + SMS fallback; SMS production gated on the sprint-1 BAA. |
| **Sprint 3** | PBI-QUE-002 (8) · PBI-QUE-003 (3) · PBI-SUB-002 (5) · PBI-SUB-001 (3) | 19 | Close the funnel with the audited decision + concurrency guard; substitution behind its consent gate (PBI-SUB-001 release-gated by PBI-SUB-002). |
| **At risk / un-slotted** | **PBI-CTRL-003 (`?`)** | — | Point-and-schedule only after its spike resolves; likely sprint 3–4. Non-deferrable launch gate ⇒ tracked as the top schedule risk. |

**Cut-line (unchanged from `08-backlog.md`):** the SUB epic (PBI-SUB-001 + PBI-SUB-002) is the cleanest deferral if the clock slips. **Never** deferrable: PBI-PHI-001, PBI-CTRL-001, PBI-CTRL-002, PBI-CTRL-003 (regulatory gates).

---

## Handoff to `sprint-planner`

- Take the **56 pointed dev points**, the **18–22 provisional velocity** (ASSUMPTION-24), and the reference anchor (PBI-SUB-001 = 3) as inputs; the sprint table above is a forecast, not a commitment.
- **Do not schedule PBI-CTRL-003** until its identity-verification spike (FLAG to `backlog-manager`) resolves and I re-estimate it.
- Decide the CTRL-001 cascade: accept a stretch sprint 1 (~24) or re-rank to keep the funnel on the 3-sprint CON-5 target.
- Re-baseline velocity on measured sprint-1 throughput before finalising sprints 2–3.
