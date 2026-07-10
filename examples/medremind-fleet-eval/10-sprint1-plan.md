# Sprint 1 Plan — MedRemind

| Field | Value |
|---|---|
| Sprint goal | **Prove the ground and lay the compliance keel:** a patient can request a refill in one tap with every action written to an append-only audit ledger, while the two recon spikes and the Schedule II–V verification decision (ADR) de-risk everything downstream — and the assumption-ratification batch lands so Sprint 2 can commit the reminder pipeline. |
| Dates | 2026-07-13 – 2026-07-24 (two-week sprint; start date assumed — confirm at planning) |
| Team capacity | ~20 pts conservative (ASSUMPTION-EST-1, no velocity history) → **≤15 pts of stories** after the 3 unsized timeboxed items (2d + 1d spikes + PLAT-003 analysis) |
| Committed | **13 pts** of stories + 3 timeboxed items (2 pts slack; +3-pt stretch, see below) |

## Committed items
| Rank | PBI ID | Story (short) | Points | Serves goal? | Ready? | First task / note |
|---|---|---|---|---|---|---|
| 1 | PBI-PLAT-001 | Spike: Rx read interface recon (ratifies A-6, informs A-9) | — (2d timebox) | ✅ | ✅ | Read Rx integration code/data; evidence memo; cut follow-up PBIs |
| 2 | PBI-PLAT-002 | Spike: gateway/IdP individual accounts + 15-min timeout (A-22) | — (1d timebox) | ✅ | ✅ | Check IdP config/docs; confirm or cut identity-workstream PBI |
| 3 | PBI-PLAT-003 | Decision: Sched II–V verification method → ADR | — (analysis) | ✅ | ✅ | Architect frames options → adr-writer; then re-point CTRL-004 |
| 4 | PBI-AUD-001 | Same-transaction append-only audit ledger | 5 | ✅ | ✅ | Ledger schema + transactional write hook; prove no update/delete path |
| 5 | PBI-REF-001 | One-tap refill request + store-named confirmation | 5 | ✅ | ✅ | API endpoint + request entity + store routing, then mobile UI |
| 6 | PBI-REF-002 | Idempotent / retry-safe request | 3 | ✅ | ✅ | Implement SDD dedupe key on REF-001's endpoint; retry tests |

**Stretch (not committed): PBI-CTRL-001** (no reminder/one-tap for controlled, 3 pts, ✅). Its Dep is spike PBI-PLAT-001 — the dependency resolves *mid-sprint*, so committing it up front would breach DoR "no blocking dependency". Pull it only if the spike lands clean by ~day 3.

**Sprint-critical parallel action (not a PBI):** PM + compliance ratify the assumption batch **A-5, A-7, A-8, A-9, A-10, A-13, A-14, A-15 and SRS A-16..A-21** before Sprint-2 planning. This single action unblocks 10 of the 26 PBIs (ranks 8, 10, 12–16, 23–26 subset); without it Sprint 2 cannot commit the reminder pipeline or the queue, and the slice slips regardless of velocity.

**Planning Poker confirmation:** all points are solo-mode estimates — re-estimate committed items with the 4 devs + QA at the Sprint-1 planning session before commitment stands (divergence > one card step ⇒ discuss).

## Deferred (top items that didn't fit or aren't Ready)
| PBI ID | Points | Why deferred |
|---|---|---|
| PBI-CTRL-001 | 3 | Stretch only — dep on PLAT-001 spike outcome resolves mid-sprint |
| PBI-CTRL-003 | 3 | Capacity (19 → ≤15); estimator's recommended move to Sprint 2 |
| PBI-CTRL-002 | 2 | ⛔A-9 unratified — fails DoR, bounced to ratification batch |
| PBI-QUE-001 / QUE-002 | 5 / 5 | QUE-001 ⛔A-7; QUE-002 Ready but dep-blocked behind it |
| PBI-PHI-001 | 5 | ⛔A-10 unratified — gates all notification content work |
| PBI-REM-001..003 | 8/3/5 | ⛔A-5/6/14 and ⛔A-10; REM-001 re-estimate after PLAT-001 spike |
| PBI-CTRL-004 | ? | ⛔D — unestimable until the PLAT-003 ADR lands (this sprint) |

## Committed vs capacity — and the leadership math
**Sprint 1:** 13 pts committed vs ~15 pts effective capacity (16 with stretch). The backlog's original Sprint-1 mapping was 19 pts — an overcommit on a no-history team; we cut CTRL-003 (per the estimator) and demoted CTRL-001 to stretch.

**The 3-sprint slice does not fit on a conservative forecast — leadership must pick now:**
- Demand ≈ **76–79 pts** (71 sized + CTRL-004 provisional 5–8) vs capacity ≈ **55 pts** (15+20+20). Sprint 2 as mapped is 33 pts vs 20 — the breaking point.
- **(a) Trim the slice:** defer SUB-001/002/003 (−10) plus PLAT-004 + QUE-003 (−6) to a Sprint-4 hardening sprint → ~60–63 pts; close only if measured velocity edges up.
- **(b) 4 sprints** for the full slice at conservative velocity — the honest schedule answer.
- **(c) Keep 3 sprints** only if measured Sprint-1 velocity ≥ ~24 pts — a bet, decided with data at Sprint-2 planning.
- **Not a lever:** CTRL ships whole inside whatever slice is chosen (PRD decision log); it cannot be descoped to fit.
- **Recommendation:** commit Sprint 1 as above, pre-negotiate option (a) with the PO now, re-forecast at Sprint-2 planning with measured velocity, and only then choose (a)/(b)/(c).

## Risks & dependencies
- **Ratification batch slips** → Sprint 2 has almost nothing Ready to pull (only CTRL-003, QUE-002-after-A-7, SUB trio). Mitigation: it is named the sprint's critical action, owner PM+compliance, due before Sprint-2 planning.
- **PLAT-001 finds an unreliable Rx interface** → split REM-001 (scheduler-core vs data-adaptation) and re-estimate; stretch CTRL-001 stays out.
- **PLAT-003 ADR slips** → CTRL-004 stays "?", threatening "CTRL ships whole" inside the slice; timebox the analysis to week 1.
- **PLAT-002 finds no individual-account support** → cut identity-workstream PBI; QUE-002 attribution AC at risk.
- **Zero velocity history** → treat Sprint-1 actuals as the first real forecast input; do not convert points to hours.
- Handoff: committed PBIs → frontend-developer / backend-developer; risks above → raid-keeper; sprint end → retrospective-facilitator.
