# Sprint 1 Plan — MedRemind: Prescription Refill Reminder & Approval Module

*Author: `sprint-planner` (facilitator) · phase: planning · loop: planning · 2026-07-09 · run3*
*Upstream: `backlog-manager` (`08-backlog.md`), `estimation-facilitator` (`09-estimates.md` — **not delivered**, see FLAG). Source of truth for scope: `08-backlog.md` → `brief.md`.*
*Downstream: `frontend-developer`, `backend-developer`, `raid-keeper`, `retrospective-facilitator`. Gate: `templates/definition-of-ready-done-template.md`.*

| Field | Value |
|---|---|
| Sprint | 1 of the 3-sprint first-shippable slice (brief timeline pressure) |
| Sprint goal | **Stand up the fail-closed safety + delivery spine — classification gate, idempotency ledger, PHI-minimization composer, and delegated authZ — so no controlled substance can reach an automated path and no drug name can leak, making the remind→one-tap→approve slice safe to build in Sprint 2.** |
| Dates | 2026-07-13 – 2026-07-24 (two-week sprint, CON-5) — dates ASSUMPTION-27 |
| Team | 4 developers + borrowed security/SRE review (ASSUMPTION-2); 1 PM (PO), 1 architect drives the spike, 1 QA |
| Team capacity | **28 pts** planning forecast (ASSUMPTION-26 — first sprint, **no velocity history**) |
| Committed | **26 pts** (5 items + 1 spike) — thin slack by design; binding constraint is the spike→gate dependency, not raw points |
| Estimates basis | Provisional S/M/L→Fibonacci conversion (ASSUMPTION-25) — **estimation-facilitator has not delivered `09-estimates.md`**; points below are NOT ratified |

## Ratification of the proposed slice (ASSUMPTION-24 — owner of final sprint assignment)

`backlog-manager` proposed Sprint 1 = PBI-PLAT-007, PBI-PLAT-001, PBI-PLAT-002, PBI-PLAT-003, PBI-PLAT-005, **PBI-CTL-001, PBI-CTL-002** and left a `FLAG(sprint-planner)` asking whether an enabler-heavy Sprint 1 is acceptable. My ratified decision:

- **Keep** the spine + spike in Sprint 1 (PBI-PLAT-007, -001, -002, -003, -005). This is the correct sequencing — nothing controlled- or PHI-touching is buildable until the gate, composer, ledger, and authZ exist.
- **Move PBI-CTL-001 and PBI-CTL-002 to the front of Sprint 2** (they were in the backlog's Sprint 1 proposal). Rationale — this is **not** a safety regression and **not** deferring a guardrail:
  1. Both are consumption guards over surfaces that **do not exist until Sprint 2** — PBI-CTL-001 guards the *reminder job* (built Sprint 2, PBI-RMD-001) and PBI-CTL-002 guards the *patient refill surface* (Sprint 2, PBI-RFL-001). There is **no automated path to leak through in Sprint 1**, so shipping the guard *with the surface it protects* keeps the KPI-5 guardrail present the moment a reachable path first exists.
  2. Both are two dependency-hops out (spike → PBI-PLAT-001 gate → guard). Committing them to Sprint 1 would mean starting them only after both the spike **and** the 8-pt gate complete — realistically the last 2–3 days — which is exactly the overcommit-then-spill pattern the Definition of Ready exists to prevent.
  3. Per the backlog's own DoR sub-gate, PBI-CTL-001/-002 are **not Ready** at planning time (blocked on PBI-PLAT-001, itself blocked on the spike). Committing not-Ready items violates the gate.
- Net answer to the FLAG: **Yes, an enabler-only Sprint 1 is acceptable and necessary.** The headline demo (a delivered reminder) legitimately lands in Sprint 2; the 3-sprint slice still closes on the remind→request→approve vertical. Leadership should be told Sprint 1 ships *infrastructure with test evidence*, not a user-visible feature. This is confirmed to the PM, not silently re-scoped.

## Committed items

| Rank | PBI ID | Story (short) | Prov. pts | Serves goal? | Ready? | First task / note |
|---|---|---|---|---|---|---|
| 1 | PBI-PLAT-007 | Spike: authoritative DEA-schedule classification field, read mechanism, timeout | 3 (timebox) | ✅ unblocks the gate | ✅ | **Day 1–3, architect-led.** Answer ASSUMPTION-9 + ASSUMPTION-21. Exit = source field + read mechanism (direct vs read-model/cache) + timeout documented; PBI-PLAT-001 marked Ready or follow-up PBIs cut. **Hard timebox — see Risk R1.** |
| 2 | PBI-PLAT-002 | At-most-once idempotency ledger (prescription + refill-cycle key) | 5 | ✅ delivery spine | ✅ (no deps) | Day 1 start, parallel to spike. Model the ledger key; prove no-second-effect across retry/redelivery/failover. |
| 3 | PBI-PLAT-003 | PHI-minimization composer boundary (no drug name in any outbound field) | 5 | ✅ PHI spine | ✅ (no deps) | Day 1 start, parallel. Enforce at the composer seam incl. push title/body/lock-screen preview + SMS body. Borrowed security review before DoD. |
| 4 | PBI-PLAT-005 | IdP-delegated authN + server-side role/scope authZ (patient-own / pharmacist-store) | 5 | ✅ authZ spine | ✅ (no deps) | Day 1 start, parallel. No new auth platform (ASSUMPTION-4); wire existing IdP; enforce scope server-side. |
| 5 | PBI-PLAT-001 | Fail-closed Classification Gate ({non-controlled, controlled, unreadable}; fail → excluded) | 8 | ✅ **the** safety keystone | ⚠ **conditionally Ready** — becomes Ready when PBI-PLAT-007 closes (target day 3) | Starts once spike closes (~day 3). Fail-closed on timeout/null/unknown-enum/read-error → "unreadable" → excluded, never default-eligible. Requires **inspection + security review** per SR-PRIV-004 / URS §6, not test alone. |
| | | **Total committed** | **26** | | | vs 28 capacity — ~7% slack |

## Deferred (top backlog items that did NOT enter Sprint 1)

| PBI ID | Prov. pts | Why deferred |
|---|---|---|
| PBI-CTL-001 | 2 | Guards the reminder job, which is built in Sprint 2 (PBI-RMD-001). Ships with its surface → **Sprint 2 rank 1**. Not Ready in S1 (blocked on gate). |
| PBI-CTL-002 | 2 | Guards the patient refill surface, built in Sprint 2 (PBI-RFL-001). Ships with its surface → **Sprint 2 rank 2**. Not Ready in S1 (blocked on gate). |
| PBI-RMD-001…-007, PBI-RFL-001…-004, PBI-CTL-004 | — | Sprint 2 slice (reminder + one-tap). All depend on the Sprint 1 spine; not Ready until it lands. |
| PBI-QUE-*, PBI-CFN-001, PBI-PLAT-004, PBI-PLAT-006 | — | Sprint 3 slice (queue + approve + close-the-loop + observability). |
| PBI-RMD-002, PBI-QUE-005, PBI-SUB-*, PBI-PREF-001 | — | Post-slice Should/Could; several gated on open assumptions (ASSUMPTION-10/-11/-14). |

## Revised 3-sprint sequencing (ratified — supersedes the backlog proposal, ASSUMPTION-24)

- **Sprint 1 — safety + delivery spine (enablers only):** PBI-PLAT-007 (spike), PBI-PLAT-001, PBI-PLAT-002, PBI-PLAT-003, PBI-PLAT-005.
- **Sprint 2 — reminder + one-tap (guards ship with surfaces):** **PBI-CTL-001, PBI-CTL-002** (pulled forward from backlog's S1), then PBI-RMD-001, -003, -004, -005, -006, -007, PBI-RFL-001, -002, -003, -004, PBI-CTL-004.
- **Sprint 3 — queue + approve + close-the-loop:** PBI-PLAT-004 (audit/consent store — **see FLAG(backlog-manager): no ranked backlog row exists for it**), PBI-QUE-001, -002, -003, -004, -006, PBI-CFN-001, PBI-PLAT-006 (observability, trailing to verify SR-PERF-001).
- **Post-slice:** PBI-RMD-002, PBI-QUE-005, PBI-SUB-001/-002/-003, PBI-PREF-001.

## Task breakdown (the "how" — below-story tasks are tracker-only, illustrative here)

- **PBI-PLAT-007 (spike):** interview dispensing-system owner → locate DEA-schedule field → confirm read seam (direct call vs cached read-model, ASSUMPTION-21) → set bounded read timeout → write findings → cut/close follow-up PBIs.
- **PBI-PLAT-002:** define `(prescriptionId, refillCycle)` ledger key → persist-once write path → idempotent guard on dispatch + request-create → failover/redelivery test harness.
- **PBI-PLAT-003:** composer interface accepting only neutral copy + deep link → static-analysis/contract test rejecting any field carrying drug name → cover push preview + SMS body → security review.
- **PBI-PLAT-005:** IdP token validation → patient-scope filter (own records) → pharmacist-store-scope filter → server-side enforcement tests for both roles.
- **PBI-PLAT-001:** consume the spike's field/mechanism → three-valued classifier → fail-closed default path → exclusion wiring point for Sprint 2 consumers → inspection + security review.

## Risks & dependencies

- **R1 — CRITICAL (dependency compression, not capacity).** The 8-pt gate (PBI-PLAT-001), the single most safety-critical item, cannot start until the spike (PBI-PLAT-007) closes. If the spike overruns its day-3 timebox (real risk — it depends on an **external** dispensing-system owner, ASSUMPTION-9/-21), the gate compresses into too few days. **Guardrail (protect the goal, adjust scope):** if the spike is not closed by end of day 3, PBI-PLAT-001 drops to Sprint 2 and the Sprint 1 goal narrows to "ledger + composer + authZ delivered; classification source de-risked." The three independent enablers (PBI-PLAT-002/-003/-005, 15 pts) carry the sprint regardless and keep 3 devs productive from day 1. → tracked by `raid-keeper`.
- **R2 — No velocity history.** This is the team's first sprint on this module; the 28-pt capacity (ASSUMPTION-26) is a conservative forecast, not measured. Re-baseline after this sprint's actuals; `retrospective-facilitator` to capture true velocity.
- **R3 — Estimates not ratified.** All points are provisional S/M/L conversions (ASSUMPTION-25). If `estimation-facilitator`'s ratified points differ materially (esp. PBI-PLAT-001 = L), the commitment must be re-checked before it is firm. → see FLAG(estimation-facilitator).
- **R4 — External + borrowed dependencies.** Spike needs the dispensing-system owner; PBI-PLAT-003/-001 need borrowed security review; PBI-PLAT-005 assumes existing IdP capacity (ASSUMPTION-4). Confirm reviewer availability at sprint start.
- **R5 — Governance.** PBI-PLAT-001 and PBI-PLAT-003 require **inspection + security review** for DoD (SR-PRIV-004 / URS §6), not test alone — budget reviewer time inside the sprint, not after.

## Definition of Ready / Done

- **DoR:** `templates/definition-of-ready-done-template.md` (team's single living artifact). The three independent enablers (PBI-PLAT-002/-003/-005) are fully Ready. PBI-PLAT-001 is **conditionally Ready**, gated on the spike closing (day 3) — committed under the R1 guardrail. The spike (PBI-PLAT-007) is Ready as a timeboxed investigation with a defined exit.
- **DoD:** team's shared bar (coded, reviewed, tested, docs updated, merged). Safety-critical additions above (R5).

## Assumptions

Carried from upstream (do **not** re-invent; not decided): **ASSUMPTION-2** (borrowed craft — security/SRE part-time), **ASSUMPTION-4** (existing IdP underpins PBI-PLAT-005), **ASSUMPTION-9 / -21** (DEA-classification source + read seam — feed the PBI-PLAT-007 spike; still open), **ASSUMPTION-23** (S/M/L is an ordering hint, not points), **ASSUMPTION-24** (final sprint assignment is `sprint-planner`'s — **exercised here**).

New in this plan (unratified):

- **ASSUMPTION-25** *(owner: PM / `estimation-facilitator`)* — with `09-estimates.md` undelivered, provisional points are a rough S/M/L→Fibonacci conversion (S=2, M=5, L=8; spike=3 timebox) used **only** to check capacity fit. Not ratified; must be confirmed before the commitment is firm.
- **ASSUMPTION-26** *(owner: PM / `sprint-planner`)* — Sprint 1 planning capacity ≈ 28 pts. Derived conservatively (4 devs, first sprint, no velocity, borrowed specialists part-time, spike-coordination overhead). To be re-baselined from actuals at retro.
- **ASSUMPTION-27** *(owner: PM / `sprint-planner`)* — sprint dates 2026-07-13 – 2026-07-24 are indicative two-week bounds; PM to confirm against the release calendar.

## Flags

```
FLAG(estimation-facilitator): The estimates handoff (09-estimates.md) is NOT on disk — my context
pack routed 'estimates' as "not found." I proceeded on ASSUMPTION-25 (provisional S/M/L→Fibonacci)
purely to validate capacity fit. Please deliver ratified story points, especially for PBI-PLAT-001
(sized L) and the timeboxed spike PBI-PLAT-007; if they differ materially from my provisional set,
the Sprint 1 commitment (26 vs 28) must be re-checked before it is firm.
```

```
FLAG(backlog-manager): PBI-PLAT-004 (audit/consent store enabler) is referenced as a dependency by
PBI-QUE-004/-005/-006 and PBI-SUB-002, appears in the RTM backlog-trace and in your Sprint 3
proposal, but has NO ranked row in 08-backlog.md's ordered backlog table. It does not affect Sprint 1,
but it must be given a ranked, AC-bearing row before Sprint 3 planning or those queue/approve stories
are not Ready. Please add it (or tell me it was intentionally omitted).
```

```
FLAG(product-analytics): Carrying your prior flag forward — no analytics/instrumentation PBI exists.
Sprint 1 ships no user-visible surface, so no metric is measurable yet, but once the on-time-refill
denominator (ASSUMPTION-7) is ratified a measurement PBI will be needed in Sprint 2/3 to verify BG-001.
```
