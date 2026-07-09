# Sprint 1 Plan — MedRemind (run4)

*Author: `sprint-planner` · phase: planning · loop: planning · agentic_role: facilitator · 2026-07-10 · run4*
*Upstream: `estimation-facilitator` (`09-estimation.md`, 56 pointed dev pts + 18–22 velocity band), `backlog-manager` (`08-backlog.md`, 13 ranked PBIs + DoR state). Scope source of truth: `brief.md`.*
*Downstream: `frontend-developer`, `backend-developer` (execution), `raid-keeper` (risks), `retrospective-facilitator` (sprint end). RTM: `examples/medremind-fleet-eval/run4/RTM.md` (§Sprint 1 commitment appended).*
*Gate: `templates/definition-of-ready-done-template.md` (DoR). This agent owns no requirement column (`rtm_column: "—"`) — it mints no Req-ID/PBI; it selects from the estimated backlog and records the sprint commitment. Every PBI referenced here has its AC-bearing defining row in `08-backlog.md`.*

| Field | Value |
|---|---|
| Sprint | 1 of 3 (CON-5 first-shippable-slice window) |
| Dates | 2026-07-14 – 2026-07-25 (2-week sprint) — **ASSUMPTION-25** |
| Team | 4 developers + 1 architect + 1 QA; PM = acting PO; Scrum Master facilitates |
| Team capacity | **~20 dev pts** (provisional midpoint of the 18–22 band, ASSUMPTION-24 — no velocity history; re-baseline on measured sprint-1 throughput) |
| Committed (dev stories) | **16 pts** (PBI-PHI-001, PBI-CTRL-001, PBI-CTRL-002) |
| Reserved (spikes/discovery) | **~4 pts** architect+dev timebox (classification-read spike + identity-verification spike — to be minted by `backlog-manager`) |
| Non-dev, in-flight | PBI-ENABLE-001 (Twilio HIPAA BAA — PM/compliance; excluded from dev velocity) |

---

## Sprint goal

**Clear the two hard regulatory launch gates — no PHI in any notification body, and zero automated touch of a controlled substance — so that the reminder pipeline can be switched on safely in Sprint 2.**

This is the only coherent goal available at the top of the backlog: PBI-PHI-001, PBI-CTRL-001 and PBI-CTRL-002 are the three non-deferrable regulatory gates (`08-backlog.md` cut-line: *never deferrable*), they share the compliance-choke-point design (SDD-ARC-002, SDD-CMP-002/003), and until they close **no reminder may fire** (PBI-RMD-001 depends on PBI-PHI-001 + PBI-CTRL-001). Landing them is the prerequisite for the 41%→60% funnel, not the funnel itself.

---

## Critical-path precondition (blocks the whole sprint goal)

All three committed stories are **DoR-blocked today** on the same missing artifact: **DOC-004 (threat model + security requirements)** is not on disk, and the DoR gate (doc-strategy §8, carried in `08-backlog.md`) makes a DOC-004 reference mandatory for every PHI and controlled-substance story. PBI-CTRL-001/002 additionally need **ASSUMPTION-8** (DEA-classification source) and **ASSUMPTION-14** (fail-closed default) ratified.

**Facilitator call:** I do **not** commit DoR-blocked items as if Ready. The sprint therefore opens with a **Day-1 non-code prerequisite** owned by the architect / `security-reviewer`: author DOC-004 and ratify ASSUMPTION-8 / ASSUMPTION-14. The three gate stories are committed **conditionally** — they enter WIP the moment DOC-004 lands, forecast **by day 3** (ASSUMPTION-26). If DOC-004 is not authored by ~day 5, these stories cannot start and the sprint goal is missed; there is **no Ready dev fallback** because every other Ready story (PBI-RFL-001 → PBI-QUE-001 → PBI-QUE-002) chains its dependency back through these same blocked gates. **DOC-004 is the single highest-leverage item on the board — see FLAG.**

---

## Committed items

| Rank | PBI ID | Story (short) | Points | Serves goal? | Ready? / DoR | First task / note |
|---|---|---|---|---|---|---|
| 1 | PBI-ENABLE-001 | Twilio HIPAA BAA — procure + execute | Spike (non-dev) | ✅ (unblocks SMS) | ✅ Ready now (PM/compliance) | Start **day 1** — longest external lead time; blocks production SMS in PBI-RMD-001/002. Not counted in dev velocity. |
| 2 | PBI-PHI-001 | No drug name / PHI in any SMS or push body | 5 | ✅ | ⚠️ **Conditional** — clears when DOC-004 lands (ASSUMPTION-26); URS-DAT-001 ref present | Build Notification Composer PHI boundary (SDD-CMP-003 / SDD-SEC-002); assert no drug name in body **or lock-screen preview**; drug detail app-only behind authN. |
| 3 | PBI-CTRL-001 | Schedule II–V excluded from automated reminders (fail-closed) | 8 | ✅ | ⚠️ **Conditional** — DOC-004 + ASSUMPTION-8 + ASSUMPTION-14 | Classification Gate (SDD-CMP-002, SDD-DAT-001); **run the classification-read spike first** (see FLAG to backlog-manager) — if the DEA-schedule read cannot serve the ≤5-min cycle, split a backend enabler and re-estimate. Fail-closed on absent/unresolved classification. |
| 4 | PBI-CTRL-002 | Schedule II–V excluded from one-tap self-service | 3 | ✅ | ⚠️ **Conditional** — rides PBI-CTRL-001 gate (its dep) | UI suppression + server-side guard once the PBI-CTRL-001 gate exists; no self-service request created for Schedule II–V or unresolved classification. |

**Committed dev total: 16 pts** against ~20 capacity, leaving **~4 pts** reserved for the two discovery spikes below (architect + one dev, timeboxed). This is deliberately conservative for a first-time-on-codebase team (ASSUMPTION-24) and absorbs the PBI-CTRL-001 5→8 re-estimate cascade.

## Spikes run this sprint (discovery — to be minted as PBIs by `backlog-manager`)

These are **not yet defined PBIs** and I do not assign them PBI IDs (that would be a phantom PBI). They are surfaced as findings for `backlog-manager` to split with acceptance criteria, then `estimation-facilitator` to point:

1. **Classification-read spike** (split from PBI-CTRL-001) — confirm the dispensing-system prescription + DEA-schedule read (ASSUMPTION-20 / ASSUMPTION-23) exists and can serve the fail-closed gate within the ≤5-min reminder cycle. Outcome: either PBI-CTRL-001 proceeds as estimated, or a backend enabler is split and PBI-CTRL-001 re-scoped/re-estimated.
2. **Identity-verification-mechanism spike** (split from PBI-CTRL-003) — resolve the unratified identity mechanism (ASSUMPTION-8) so PBI-CTRL-003 can be pointed. Per `09-estimation.md`, PBI-CTRL-003 is `?` (un-pointable) and **must not be scheduled** until this spike resolves. Running it in Sprint 1 protects the CON-5 timeline for the top schedule risk on the board.

## Deferred (top backlog items that did not fit Sprint 1)

| PBI ID | Points | Why deferred |
|---|---|---|
| PBI-RMD-001 | 8 | Ready-blocked this sprint (deps PBI-PHI-001 + PBI-CTRL-001 land **in** Sprint 1, so it cannot start until they close) **and** 8 pts exceeds the ~4 pt headroom under a 20 cap. This is the PBI-CTRL-001 5→8 cascade `09-estimation.md` surfaced. Pulled to Sprint 2 (its composer/exclusion deps close here). |
| PBI-RFL-001, PBI-QUE-001, PBI-QUE-002, PBI-RMD-002 | 5+5+8+3 | Funnel body — dependency-chained behind PBI-RMD-001 / the gates; Sprint 2. |
| PBI-CTRL-003 | ? | **Un-pointable** (spike-gated, ASSUMPTION-8 / DOC-004). Not scheduled until its identity-verification spike (run this sprint) resolves and `estimation-facilitator` re-estimates. Likely Sprint 3–4. Non-deferrable launch gate ⇒ top schedule risk. |
| PBI-QUE-003, PBI-SUB-002, PBI-SUB-001 | 3+5+3 | Concurrency hardening + substitution behind consent gate; Sprint 3. |

## Cascade decision (`estimation-facilitator` handed this to me)

`09-estimation.md` asked `sprint-planner` to resolve the PBI-CTRL-001 5→8 cascade: either **(a)** commit to the top of the band (~24, a stretch for a new team) to keep PBI-RMD-001 in Sprint 1, or **(b)** re-rank / accept the slip.

**Decision: neither stretch nor re-rank — hold capacity at the conservative ~20 midpoint, protect the two hard gates as the sprint goal, and let PBI-RMD-001 spill to Sprint 2.** Rationale: ASSUMPTION-24 explicitly says the 18–22 band is a forecast, not a target, for a team with zero velocity history on an unconfirmed brownfield surface (ASSUMPTION-23); over-committing a first sprint to protect a schedule the estimate already flags as *at risk* is the exact over-commitment pitfall the DoR/capacity discipline exists to prevent. **Consequence, surfaced honestly:** the reminder→one-tap→queue→decision funnel (the 41%→60% lever) does not fully close until Sprint 3, and CON-5's "first shippable slice in 3 sprints" is **at risk**, driven by (i) the DOC-004 precondition and (ii) PBI-CTRL-003 being un-pointable. **Re-baseline velocity on measured Sprint-1 throughput before finalising Sprints 2–3** — if the team clears 16 pts comfortably plus the spikes, Sprint 2 can commit toward the top of the band.

## Risks & dependencies (hand to `raid-keeper`)

| # | Risk / dependency | Impact | Mitigation / owner |
|---|---|---|---|
| R1 | **DOC-004 not authored by ~day 3** (ASSUMPTION-26) | All 3 committed stories cannot start; sprint goal missed; no Ready dev fallback exists | Day-1 commitment for architect / `security-reviewer`; escalate at first standup if not in progress. **FLAG below.** |
| R2 | PBI-CTRL-001 DEA-classification read can't serve the fail-closed gate (ASSUMPTION-20 / ASSUMPTION-23) | PBI-CTRL-001 re-scoped, backend enabler split, PBI-CTRL-002 slips | Classification-read spike day 1–2; re-estimate on outcome (`estimation-facilitator`). |
| R3 | Twilio BAA procurement lead time (PBI-ENABLE-001) | Production SMS held → PBI-RMD-002 / SMS path in PBI-RMD-001 blocked in Sprint 2 | Start day 1; confirm HIPAA-eligible edition + cost (SR-PHI-003). PM/compliance. |
| R4 | ASSUMPTION-8 / ASSUMPTION-14 (identity mechanism, fail-closed default) never ratified | PBI-CTRL-001/002 stay DoR-blocked; PBI-CTRL-003 stays un-pointable | Ratify as part of DOC-004; identity-verification spike this sprint. |
| R5 | SMS consent-to-contact / TCPA (ASSUMPTION-11, OQ-5) and send window (ASSUMPTION-13, OQ-7) unresolved | Shapes PBI-RMD-001 AC; if OQ-5 → explicit opt-in, a new launch-gating enabler splits out | Resolve before Sprint 2 PBI-RMD-001 pull; PM/PO. |

## FLAGs raised

- **FLAG(security-reviewer / architect):** **DOC-004 (threat model + security requirements)** is absent on disk and is the DoR gate for all three Sprint-1 committed stories (PBI-PHI-001, PBI-CTRL-001, PBI-CTRL-002) — and PBI-CTRL-003 downstream. It must be authored and ASSUMPTION-8 / ASSUMPTION-14 ratified as the **Day-1 sprint prerequisite**, or the sprint goal is unachievable. This is the single highest-leverage blocker on the board. Not an artifact `sprint-planner` can author. (Carried from `08-backlog.md` / `09-estimation.md`; re-raised as a live Sprint-1 blocker.)
- **FLAG(backlog-manager):** two discovery spikes need minting as AC-bearing, ranked, pointed PBIs so they are not phantom work: (1) a **classification-read spike** split from PBI-CTRL-001, and (2) an **identity-verification-mechanism spike** split from PBI-CTRL-003 (per `09-estimation.md`'s explicit routing). I reference them descriptively only and assign no PBI ID until `backlog-manager` defines them and `estimation-facilitator` points them.

## Assumptions introduced here (unratified)

- **ASSUMPTION-25** *(owner: PM / Scrum Master)* — Sprint 1 dates 2026-07-14 – 2026-07-25. The brief gives no start date; dates are provisional until the team confirms the calendar and PTO/holiday capacity adjustments.
- **ASSUMPTION-26** *(owner: architect / `security-reviewer`)* — DOC-004 is authored and ASSUMPTION-8 / ASSUMPTION-14 ratified **by ~day 3** of Sprint 1, so the three gate stories clear DoR with enough runway to finish in-sprint. The entire committed forecast rests on this; if it slips, the sprint re-plans (scope drops to protect the goal, per replan discipline).
