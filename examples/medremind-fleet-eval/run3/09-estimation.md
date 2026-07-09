# Estimation — MedRemind: Prescription Refill Reminder & Approval Module

*Author: `estimation-facilitator` · phase: planning · loop: planning · 2026-07-09 · run3*
*Upstream: `backlog-manager` (`08-backlog.md`, contract input) · brief (`brief.md`, scope source of truth). SDD/FRD/SRS ancestors read digest-first for sizing context.*
*Downstream: `sprint-planner` (consumes these points + the velocity/capacity forecast to ratify the sprint plan and the 3-sprint slice — ASSUMPTION-24).*

| Field | Value |
|---|---|
| Facilitator | `estimation-facilitator` (solo relative estimate — ASSUMPTION-25) |
| Estimators of record | The 4-developer team, by Planning Poker consensus — **not yet run** (eval constraint, ASSUMPTION-25) |
| Reference story | **PBI-QUE-003 = 2** (explicit empty-state on the pharmacist queue: one screen, one load-state branch, no new backend — well-understood, small, testable) |
| Scale | Modified Fibonacci `1, 2, 3, 5, 8, 13, 20, 40, 100`; `?` = needs a spike |
| Units | Relative effort + complexity + risk/uncertainty. **Not hours.** |
| Date | 2026-07-09 |

## How to read these estimates

- **Points are relative to PBI-QUE-003 = 2.** A 5 is "a few times the empty-state story"; an 8 is a large, multi-branch or safety-critical slice at the upper edge of a single sprint item. Nothing was forced onto a number — see *Outliers & splits*.
- **These are the facilitator's provisional solo estimates (ASSUMPTION-25).** In a real session the 4 developers vote by Planning Poker and the consensus value replaces mine. I surfaced the reasoning (Notes column) so the team can converge or challenge, not so a single number stands unquestioned.
- **Confidence** reflects unknowns, not effort: `High` = scope + read-path clear; `Medium` = normal implementation risk; `Low` = gated on an open ASSUMPTION or a spike, so the number is *stale-until-resolved* and will be re-pointed.
- **The spike (PBI-PLAT-007) is not a story point commitment** — it is timeboxed. I give it a nominal 3 (≈2 dev-days of capacity) purely so `sprint-planner` can reserve room; it is not "3 points of value delivered."
- Estimates attach to the existing PBIs. `estimation-facilitator` owns no RTM column (`rtm_column: —`) and authored no requirements, so **no RTM rows are added or changed** — every PBI here already traces in `RTM.md`.

## Estimates

| PBI ID | Story (short) | Priority | Points | Confidence | Notes / action |
|---|---|---|---|---|---|
| PBI-PLAT-007 | Spike: authoritative DEA-schedule classification field, read mechanism, timeout | Must | 3 *(spike, timebox ≈2d)* | n/a | Not a value estimate — reserve capacity. Closing it un-gates PLAT-001 (ASSUMPTION-9/-21). |
| PBI-PLAT-001 | Fail-closed Classification Gate | Must | **8** | **Low** | **Stale-until-spike.** Safety-critical, fail-closed on every error path, plus inspection+security review (SR-PRIV-004). **Re-point after PBI-PLAT-007** — if the read seam is a cache/read-model (ASSUMPTION-21), this can grow ≥13 → split. |
| PBI-PLAT-002 | At-most-once idempotency ledger (prescription+cycle) | Must | 5 | Medium | Cross-cutting correctness (retry/redelivery/failover); keying is the real work, not volume. |
| PBI-PLAT-003 | PHI-minimization composer boundary | Must | 5 | Medium | Enforce "no drug name in any field" incl. push title/body/lock-screen + SMS; test surface is broad. |
| PBI-PLAT-004 | Attributable audit + consent store (enabler) | Must | 5 | Low | **Estimated off the RTM/Notes trace only — no backlog row exists (see FLAG).** Append-only, attributable, timestamped; underpins QUE-004/-005/-006 + SUB-002. Provisional (ASSUMPTION-27). |
| PBI-PLAT-005 | IdP-delegated authN + server-side role/scope authZ | Must | 5 | Medium | Reuses existing IdP (ASSUMPTION-4) — integration + scope enforcement, not a new auth platform. |
| PBI-PLAT-006 | Per-channel metrics, SLO alerts, rollback/runbook | Should | 5 | Medium | Instrumentation + alerting + runbook; trails RMD-005 to verify the ≤5-min SLO (SR-OBS). |
| PBI-CTL-001 | Controlled Rx never entered into reminder job | Must | 2 | Medium | Thin consumer once the gate lands; via PLAT-001. |
| PBI-CTL-002 | No one-tap affordance on patient surface for controlled Rx | Must | 2 | Medium | UI guard consuming the gate; via PLAT-001. |
| PBI-CTL-004 | Manual path: id-verify → pharmacist-initiated contact | Must | **8** | **Low** | **Split candidate.** Bundles two distinct capabilities (identity-verification step + pharmacist-contact routing) on a new surface. Recommend `backlog-manager` split into `PBI-CTL-004a` (id-verify) + `PBI-CTL-004b` (contact routing); would drop each to ~5. |
| PBI-RMD-001 | Eligibility predicate (active ∧ non-controlled ∧ refills≥1 ∧ due) | Must | 5 | Medium | Core selection logic; several predicates + exclusion-on-fail; via PLAT-001. |
| PBI-RMD-003 | No drug name in push (incl. lock-screen) | Must | 2 | High | Consumes composer (PLAT-003); mostly assertion + wiring. |
| PBI-RMD-004 | Neutral SMS + deep link, names no drug | Must | 2 | High | Consumes composer; Twilio body + deep link. |
| PBI-RMD-005 | Dispatch on enabled channels (push+SMS) | Must | 3 | Medium | Two-provider dispatch (Firebase + Twilio); channel-skip depends on PREF-001. |
| PBI-RMD-006 | At most one reminder per cycle | Must | 2 | Medium | Thin consumer of the ledger (PLAT-002). |
| PBI-RMD-007 | Push/SMS treated as redundant (no double reminder/request) | Must | 5 | Low | Cross-channel dedup + late/failed-delivery reconciliation; real concurrency reasoning. |
| PBI-RFL-001 | One-tap refill request from reminder | Must | 5 | Medium | Happy-path create with tap-time re-check; no second-screen form; via PLAT-005. |
| PBI-RFL-002 | Duplicate tap is harmless | Must | 2 | Medium | Consumer of ledger (PLAT-002) + RFL-001. |
| PBI-RFL-003 | Ineligible tap refused with reason + correct routing | Must | 5 | Medium | Multi-branch (expired / out-of-refills / reclassified→manual path); via PLAT-001 + CTL-004. |
| PBI-RFL-004 | "Request received" acknowledgement <2s p95 | Must | 2 | High | Distinct state + perf assertion; via RFL-001. |
| PBI-QUE-001 | Prioritized, store-scoped pending queue, <2s @500 concurrent | Must | **8** | **Low** | Perf target (SR-PERF-002) + prioritization key unresolved (ASSUMPTION-13). Watch: if the 500-concurrent SLO needs a read-model, may split (query vs. render). |
| PBI-QUE-002 | Controlled Rx never a one-tap request in queue | Must | 2 | Medium | Queue-surface guard; via PLAT-001 + QUE-001. |
| PBI-QUE-003 | Explicit empty state | Must | **2** *(anchor)* | High | **Reference story.** |
| PBI-QUE-004 | Approve → attributable audit + dequeue + patient confirmation | Must | 5 | Medium | Write audit (PLAT-004) + state transition + trigger CFN; via PLAT-004 + QUE-001. |
| PBI-QUE-006 | Concurrency: exactly one decision on same request | Must | 5 | Low | Safety-critical concurrency guard; requires inspection (per DoD); via PLAT-004 + QUE-004. |
| PBI-CFN-001 | Approval/ready confirmation, no drug name | Must | 3 | Medium | Channel/copy open (ASSUMPTION-12); consumes composer + QUE-004. |
| PBI-RMD-002 | Batch several due Rx into one reminder | Should | 5 | Low | Batching rule + window unresolved (ASSUMPTION-10/-15) — stale-until-ratified. |
| PBI-QUE-005 | Reject with required reason + audit + notify | Should | 3 | Medium | Reason-required validation + audit write; via PLAT-004 + PLAT-003 + QUE-001. |
| PBI-SUB-001 | Attach suggested generic substitution | Should | 3 | Medium | Associate substitution with a request; via QUE-001. |
| PBI-SUB-002 | Dispensing blocked until explicit patient consent | Should | 5 | Medium | Consent record (append-only) + dispensing gate; via PLAT-004 + SUB-001. |
| PBI-SUB-003 | Decline/no-response → pharmacist fallback | Should | 5 | Low | Response-window logic unresolved (ASSUMPTION-14); timer + fallback routing. |
| PBI-PREF-001 | Turn reminders off / choose channel, persists | Could | 3 | Low | Granularity + SMS-compliance open (ASSUMPTION-11); persistence across cycles. |

**Totals** — Must (in slice): **106** pts · Should: **21** pts · Could: **3** pts · **Grand total: 130 pts** (incl. the 3-pt spike reservation).

## Outliers & splits

- **No item is ≥13**, so nothing is force-fit or immediately un-plannable. The three **8s** sit at the upper edge of a single sprint item and each carries a watch:
  - **PBI-PLAT-001** — *stale-until-spike.* Re-point after PBI-PLAT-007; if the classification read turns out to need a cache/read-model seam (ASSUMPTION-21), it likely crosses 13 and must go back to `backlog-manager` to split (read mechanism vs. fail-closed decision logic).
  - **PBI-CTL-004** — **recommend splitting now.** It bundles an identity-verification step and pharmacist-contact routing; splitting into two ~5s de-risks the sprint and gives each surface its own testable guard.
  - **PBI-QUE-001** — watch the 500-concurrent SLO; may split into query/read-model vs. render if perf work dominates.
- **PBI-PLAT-007** stays a spike (timeboxed), not a numbered story — correct handling of a `?`-class unknown.

## Velocity & capacity forecast

- **No velocity history** — this is a brand-new team on this module, so I forecast conservatively rather than assert a number (ASSUMPTION-26). For a **4-developer** team on two-week sprints, a defensible starting band is **~20–26 pts/sprint**, ramping as the team gels; treat the low end as the planning number until 1–2 sprints of *measured* velocity replace it.
- **Do not read these points as a schedule.** Velocity forecasts; it does not grade, and points are not hours.

**Load vs. the `backlog-manager` proposed 3-sprint slice (ASSUMPTION-24):**

| Sprint (proposed) | Items | Points | vs. ~20–26 capacity |
|---|---|---|---|
| Sprint 1 (spine) | PLAT-007, PLAT-001, PLAT-002, PLAT-003, PLAT-005, CTL-001, CTL-002 | **30** | **Over** |
| Sprint 2 (remind + one-tap) | RMD-001/-003/-004/-005/-006/-007, RFL-001/-002/-003/-004, CTL-004 | **41** | **Well over** |
| Sprint 3 (queue + approve) | PLAT-004, QUE-001/-002/-003/-004/-006, CFN-001, PLAT-006 | **35** | **Over** |
| **Slice total** | | **106** | **~4–5 sprints at this velocity, not 3** |

**Finding:** the Must-have slice (106 pts) needs roughly **4–5 sprints** at a conservative 20–26 pts/sprint, not the 3 leadership expects. Every proposed sprint is over a first-team's plausible capacity, Sprint 2 heavily so. This is the quantified backing for `backlog-manager`'s `FLAG(sprint-planner)`. Options for `sprint-planner` to weigh with the PM: (a) accept a 4–5 sprint slice; (b) thin Sprint 2 (defer RMD-007 redundancy and/or CTL-004 to a later sprint — but CTL-004 is a Must safety path, so prefer deferring RMD-007); (c) add capacity. **The enablers and the controlled-substance guards cannot be dropped to fit** (KPI-5 guardrail).

## Assumptions

Carried (do **not** re-invent — from `08-backlog.md`):
- **ASSUMPTION-23** (owner PM / `estimation-facilitator`) — *partially resolved here:* the S/M/L column was an ordering hint only; **authoritative story points are set above.** The S/M/L hints were used as a sanity cross-check, not as the estimate.
- **ASSUMPTION-24** (owner PM / `sprint-planner`) — the 3-sprint mapping is a proposal; these points feed its ratification (see load table).
- **ASSUMPTION-9 / -21** — DEA-classification source + read-seam; gate PBI-PLAT-007 → PBI-PLAT-001. Until closed, PLAT-001 (and its `Low`-confidence dependents) are stale-until-spike.
- **ASSUMPTION-10/-15, -11, -12, -13, -14** — open scope on RMD-002, PREF-001/RMD-005, CFN-001, QUE-001, SUB-003 respectively; each drives the `Low`/`Medium` confidence on its PBI.

New in this artifact (unratified):
- **ASSUMPTION-25** (owner PM / team / `estimation-facilitator`) — these are the **facilitator's solo relative estimates**; no live Planning Poker with the 4-developer doing-team was run (eval constraint). They are provisional until the team ratifies by consensus; the consensus value replaces the facilitator's where they differ.
- **ASSUMPTION-26** (owner PM / `sprint-planner`) — the **~20–26 pts/sprint velocity band is a conservative placeholder** for a team with no history; replace it with measured velocity after Sprint 1–2 and re-forecast the slice length.
- **ASSUMPTION-27** (owner `backlog-manager` / `estimation-facilitator`) — **PBI-PLAT-004 was estimated (5) from its RTM row + backlog Notes description only** (append-only attributable audit/consent store, SR-AUD-001/-002, SDD-CMP-010), because it has no backlog-table row (see FLAG). Re-point once a proper PBI with AC exists.

## Flags

```
FLAG(backlog-manager): PBI-PLAT-004 (audit/consent store enabler) is referenced as a dependency
by PBI-QUE-004, PBI-QUE-005, PBI-QUE-006 and PBI-SUB-002, is listed in the Sprint-3 mapping, and
has an RTM row (RTM.md backlog-trace) — but there is NO row for it in the 08-backlog.md backlog
table (ranks 1–31 jump PLAT-003 → PLAT-005). I estimated it provisionally at 5 (ASSUMPTION-27)
from the RTM/Notes trace so the Sprint-3 load is not understated, but it needs a real PBI row
(story + acceptance criteria + priority + deps) before it is Ready. Please add it.
```

```
FLAG(sprint-planner): The Must-have slice totals 106 points. At a conservative first-team velocity
of ~20–26 pts/sprint for 4 developers, that is ~4–5 sprints, not the 3 leadership expects; every
proposed sprint is over capacity and Sprint 2 (41 pts) is well over. This quantifies the
backlog-manager's enabler-heavy warning. Re-negotiate slice length or scope with the PM — the
enablers (PLAT-*) and the controlled-substance guards (CTL-*, QUE-002) cannot be deferred to fit
without dropping the KPI-5 safety guardrails. Recommend splitting PBI-CTL-004 (8) and re-pointing
PBI-PLAT-001 after the spike before you commit Sprint 1.
```
