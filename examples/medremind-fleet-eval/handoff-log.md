# Handoff log — MedRemind E2E run 2

## 1. doc-strategy-advisor
- Inputs received: brief.md only (client brief: feature scope, team size/roles, NFRs, HIPAA/controlled-substance constraints, tooling, timeline).
- Inputs my definition expects: living-spec from `spec-steward` (upstream), plus answers to my intake batch (team size, squads, industry, tools, biggest pain).
- Missing at my handoff: living-spec (no spec-steward ran); no user to interview, so intake questions unasked; current doc landscape/pain unknown.
- Facts I assumed/invented: (1) single squad, no separate FE/BE teams; (2) no dedicated security engineer — assigned threat model to architect; (3) not a GAMP-validated system, so lean URS suffices; (4) docs-as-code in git + Azure DevOps Wiki acceptable to the client; (5) QA lead can wear the validation hat for the URS.
- Quality impact: brief was rich enough for a confident tier pick; main risk is the URS depth call and ownership assignments resting on assumed org details.

## 2. brd-writer
- Inputs received: brief.md (client brief), 01-doc-strategy.md (tier pick, merge/drop decisions).
- Inputs my definition expects: MRD (from mrd-writer / doc-strategy-advisor) plus a stakeholder interview (max 4-5 questions).
- Missing at my handoff: MRD — dropped per strategy (sanctioned gap; market case = brief only); no human to interview, so gaps became tagged assumptions instead of answers.
- Facts I assumed/invented: ASSUMPTION-1 sponsor = "RxKart leadership" (owner: PM); ASSUMPTION-2 definition of "on-time refill" (owner: PM/RxKart); ASSUMPTION-3 a compliance-officer role exists (owner: PM); ASSUMPTION-4 budget = existing 7-person team capacity (owner: sponsor); ASSUMPTION-5 SMS/push consent already/obtainable (owner: compliance); ASSUMPTION-6 due-date + schedule-classification data exists and is reliable (owner: architect). All tagged in 02-brd.md; "zero violations" KPI framing is mine, derived from stated HIPAA/DEA constraints.
- Quality impact: goals, scope, and 10 BR-* requirements are solid and brief-grounded; sponsor/consent/data-reliability assumptions are the fragile edges — PRD should not commit flows until ASSUMPTION-2/5/6 are ratified.

## 3. urs-writer
- Inputs received: brief.md, 01-doc-strategy.md, 02-brd.md, RTM.md (docs root, seeded with BR- rows).
- Inputs my definition expects: BRD (from doc-strategy-advisor, brd-writer) — fully satisfied; regulatory regime derivable from brief + BRD.
- Missing at my handoff: identity-verification method for Schedule II–V (BRD open question, unresolved); exact "on-time refill"/due-date definition (BRD ASSUMPTION-2); queue scoping (store vs chain) unstated anywhere upstream.
- Facts I assumed/invented: ASSUMPTION-7 (queue scoped per store, owner PM); ASSUMPTION-8 (per-channel reminder opt-out, owner compliance); ASSUMPTION-9 (unknown schedule classification fails closed as controlled, owner compliance+architect); ASSUMPTION-10 (minimized reminder content = generic prompt + pharmacy name + app link, owner compliance). URS-CTRL-003 kept method-agnostic rather than inventing a verification mechanism.
- Quality impact: URS is complete and fully BR-traced (all 10 BR- IDs covered, RTM column appended), but four tagged assumptions and the open verification method must be ratified before controlled-substance/PHI PBIs are sprint-committed.

## 4. prd-writer
- Inputs received: brief.md, 02-brd.md, RTM.md (seeded, URS column present), handoff-log.md.
- Inputs my definition expects: BRD (from brd-writer / doc-strategy-advisor) — satisfied; plus a user interview (no human available, gaps became tagged assumptions).
- Missing at my handoff: 03-urs.md exists in the run dir but no graph edge routes it to me — I could see URS IDs in the RTM and ASSUMPTION-7..10 summaries in this log, but not the URS text; risk of PRD↔URS drift (e.g. audit-trail URS-AUD-* items have no PRD story). Also still open: Schedule II–V identity-verification method; ASSUMPTION-2/5 unratified.
- Facts I assumed/invented: carried forward ASSUMPTION-2/3/5/6 (BRD) and ASSUMPTION-7/8/9/10 (via this log, not the URS) rather than re-inventing; new ASSUMPTION-11 (secondary-metric target ≥50% one-tap uptake, owner PM), ASSUMPTION-12 (opt-out guardrail <5%, owner PM), ASSUMPTION-13 (rejection notifies patient with next step, owner PM). All tagged in 04-prd.md.
- Quality impact: all 10 BR- IDs covered by 13 PRD stories with Given/When/Then AC and RTM column filled; the URS routing gap means frd-writer must reconcile PRD stories against URS-AUD-*/URS text before decomposing.

## 5. frd-writer
- Inputs received: brief.md, 04-prd.md, 03-urs.md (full text — routing gap from step 4 closed), RTM.md, handoff-log.md.
- Inputs my definition expects: PRD + URS (from prd-writer, urs-writer, solution-recon) — PRD/URS satisfied; no solution-recon ran (greenfield-ish module, sanctioned skip, but ASSUMPTION-6 data reliability stays unverified).
- Missing at my handoff: Schedule II–V identity-verification *method* (still open — FRD-CTRL-004 gates on "recorded verification" without defining it); ASSUMPTION-2/5 unratified; no PRD story for the audit path.
- Facts I assumed/invented: carried ASSUMPTION-2/5/6/7/8/9/10/13 tagged; new ASSUMPTION-14 (reminder fires 09:00 store-local on due date — owner PM) and ASSUMPTION-15 (pharmacist may withdraw an unanswered substitution proposal — owner PM). Request state machine (Pending/Awaiting-patient/Approved/Rejected + verification gate) is my derivation from PRD flows, not upstream fact.
- Quality impact: 27 deterministic FRD-* requirements with G/W/T, all PRD/URS-traced and RTM column filled; PRD↔URS audit seam reconciled by tracing FRD-AUD-001/002/003 to URS-AUD-*/BR- directly and flagging the missing PRD auditability story back to prd-writer (per feedback loop) rather than papering over it.

## 6. srs-writer
- Inputs received: brief.md, 05-frd.md, 03-urs.md (full text), RTM.md, handoff-log.md — exactly my contract edges.
- Inputs my definition expects: FRD + URS (from frd-writer, solution-recon, urs-writer) — satisfied; workflow also says "read the PRD first", and 04-prd.md was not routed to me (FRD's Source column gave PRD IDs but not story text). No solution-recon ran, so ASSUMPTION-6 (data reliability) stays code-unverified.
- Missing at my handoff: PRD text (minor — FRD is decomposition-complete); Schedule II–V verification method (still open; SR-AUD-002/004 written method-agnostic); ASSUMPTION-2/5 unratified; no stated peak load, store-hours definition, outage-recovery, retention, or session-timeout numbers anywhere upstream.
- Facts I assumed/invented: ASSUMPTION-16 (5-min window = to provider handoff, ≥99%/month), -17 (peak 40k reminders/day), -18 (store hours 08:00–21:00 local), -19 (30-min post-outage catch-up), -20 (15-min portal idle timeout), -21 (6-yr audit retention) — all tagged with owners in 06-srs.md. Twilio BAA eligibility and FCM non-eligibility verified by WebSearch, not memory.
- Quality impact: 17 measurable SR-* constraints, one obligation each, all traced and RTM column filled; fragile edges are the six invented numbers — none may enter a sprint-committed AC before ratification, and the Twilio Security/Enterprise-edition cost flag needs a PM decision.

## 7. sdd-writer
- Inputs received: brief.md, 04-prd.md, 06-srs.md, RTM.md, handoff-log.md.
- Inputs my definition expects: PRD, SRS, solution-recon-findings, RFC (from srs-writer, rfc-facilitator, solution-recon) — PRD/SRS satisfied; no solution-recon ran (greenfield exercise, sanctioned skip) and no RFC exists.
- Missing at my handoff: solution-recon findings — ASSUMPTION-6 (Rx due-date/classification data) and gateway/IdP capability remain code-unverified; 05-frd.md exists in the run dir but was not routed to me (FRD-* behavior seen only via SRS Source column and RTM — the SDD-SUB-001 state machine is re-derived from the PRD, not checked against FRD's); Schedule II–V verification method still open (SDD-CTRL-002 kept pluggable); ASSUMPTION-2/5 unratified.
- Facts I assumed/invented: carried ASSUMPTION-6/7/9/10/14/16–21 tagged; new ASSUMPTION-22 (existing gateway/IdP supports individual pharmacist accounts + configurable 15-min idle timeout — owner: architect). Modular-monolith shape, durable-queue pipeline, dedupe key, and read-model projection are my design derivations, justified in the trade-offs table.
- Quality impact: all 17 SR-* constraints explicitly mapped to design decisions and all 10 RTM rows now carry SDD IDs; residual risk is FRD↔SDD drift on the request state machine (frd-writer or spec-analyze should reconcile) and the two unverified infrastructure assumptions.

## 8. backlog-manager
- Inputs received: brief.md, 04-prd.md, 05-frd.md, 06-srs.md, 07-sdd.md, RTM.md, handoff-log.md — my contract edges as routed.
- Inputs my definition expects: PRD/FRD/SRS/SDD (satisfied), TSD (not yet written — acceptable, PBIs stay at "what" altitude), solution-recon findings (absent — ASSUMPTION-6/-22 unverified, so cut as Sprint-1 spikes PBI-PLAT-001/002), bug/retro/debt/analytics feeds (N/A, greenfield run).
- Missing at my handoff: URS not edge-routed — the FRD Source column + RTM URS column carry the URS IDs, which suffices for the PBI→FRD→URS→BR compliance chain, but I could not re-verify URS wording against my AC; Schedule II–V verification method (cut as Decision PBI-PLAT-003 → ADR); story-point estimates (routed to estimation-facilitator — no ✅ item is fully DoR-complete until pointed); no PRD auditability story (PBI-AUD-001/002 trace to FRD/URS-AUD directly, gap stays flagged to prd-writer).
- Facts I assumed/invented: none — all assumption dependencies carried as tagged ⛔A-n blocks; the QUE decision-vs-notification split, sprint-slice mapping, and S/M/L size hints are planning derivations from PRD/FRD, not new facts.
- Quality impact: 26 PBIs across 8 epics, every one FRD/SR-traced and written back to the RTM; DoR applied honestly — 10 items marked not-Ready, blocked on the A-5/7/8/9/10/13/14/15/19/21 ratification batch + the PLAT-003 decision, which is the single action gating Sprint-2 commitment.

## 9. estimation-facilitator
- Inputs received: brief.md, 08-backlog.md — exactly my contract edges (`inputs: [backlog]` + brief).
- Inputs my definition expects: backlog (from backlog-manager / solution-recon) — satisfied; my workflow body also says "read the relevant FRD/SRS for context", but 05-frd.md / 06-srs.md are not contract-routed, so NFR context (SR-PERF-002 @500 concurrent, SR-INT-001 pacing, SR-AVL-002 catch-up) reached me only via AC text and Source columns.
- Missing at my handoff: FRD/SRS full text (routing gap above — drove Low confidence on PBI-QUE-001/REM-001/REM-006); velocity history (none exists — new team); Schedule II–V verification method (PBI-CTRL-004 left "?", correctly gated on PLAT-003); the A-n ratification batch (10 items' points provisional until scope confirmed).
- Facts I assumed/invented: ASSUMPTION-EST-1 — conservative starting velocity ≈ 20 pts/sprint (≤15 in Sprint 1 net of spike timeboxes), owner PM+team, replace with measured velocity after Sprint 1 (tagged in 09-estimation.md). Solo-mode estimates themselves are one estimator's judgment, flagged for Planning Poker confirmation.
- Quality impact: all 23 sizeable items pointed (86 pts total; no ≥13 — decomposition held), CTRL-004 honestly left "?"; headline finding for sprint-planner: the 3-sprint slice does NOT fit conservatively (~76–79 pts vs ~55) — Sprint 2 (33 pts) is the breaking point.

## 10. sprint-planner
- Inputs received: brief.md, 08-backlog.md, 09-estimation.md — exactly my contract edges (`inputs: [backlog, estimates]` + brief).
- Inputs my definition expects: backlog + estimates (from backlog-manager, estimation-facilitator) — fully satisfied; my gate template (`definition-of-ready-done-template.md`) not in the run dir, so DoR applied from the backlog's own legend + my role's five DoR elements.
- Missing at my handoff: team capacity is ASSUMPTION-EST-1 (no velocity history) not a measured number; sprint start date unstated anywhere upstream; the A-n ratification batch and PLAT-003 ADR still open (by design — Sprint 1 exists to close them); estimates are solo-mode, unconfirmed by the team.
- Facts I assumed/invented: sprint dates 2026-07-13–07-24 (tagged "assumed — confirm at planning"); the CTRL-001-as-stretch demotion (its spike dep resolves mid-sprint, so committing it would breach DoR "no blocking dependency") is my planning judgment, stricter than the estimator's 16-pt recommendation. No new product facts.
- Quality impact: capacity-honest 13-pt commitment (vs the 19-pt backlog mapping) with the ratification batch named as the sprint's critical unblocking action and the 76–79-vs-55 slice math put to leadership as an explicit (a)/(b)/(c) choice — main fragility is that all points and capacity rest on one solo estimator + ASSUMPTION-EST-1 until Planning Poker at the planning session.
