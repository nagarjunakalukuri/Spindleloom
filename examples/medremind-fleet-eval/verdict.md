# JUDGE VERDICT — e2e-medremind RUN 2 (post-contract-fix)
Judge: independent · Date: 2026-07-09 · Basis: brief.md, 01–10, RTM.md, handoff-log.md, validate_reqs/build_rtm tooling pass · Baseline: run 1 verdict (C+)

## 1. Per-handoff verdict table (run 2 vs run 1)
| # | Agent | Received vs needed | Verdict | Run 1 | Evidence |
|---|---|---|---|---|---|
| 1 | doc-strategy-advisor | brief only; intake unaskable — same as run 1 | CLEAN | CLEAN | Output complete; NEW: "harness note" declares full funnel an experimental control and instructs downstream to stay lean — run 1's silent tier-divergence is now sanctioned, and docs visibly complied (BRD: "kept 1-pager-lean") |
| 2 | brd-writer | brief + strategy; MRD drop sanctioned | CLEAN | CLEAN | 10 BR- IDs, 6 tagged/owned ASSUMPTIONs; **seeded RTM.md** with BR rows (E1 duty discharged) |
| 3 | urs-writer | brief + strategy + **BRD + RTM** — contract fully met | **CLEAN** | **BROKEN** | Source column cites BR- IDs on all 18 URS rows; all 10 BRs covered; BRD assumptions carried, not re-invented (A2 edge delivered) |
| 4 | prd-writer | brief + BRD + RTM + handoff-log; **URS still not edge-routed** | DEGRADED | DEGRADED | PRD §Assumptions: "ASSUMPTION-7/8/9/10 per handoff log; the URS itself was not routed" — mitigated by RTM/log, but audit stories (URS-AUD-*) still invisible → PRD auditability story missing again |
| 5 | frd-writer | brief + PRD + URS full text + RTM — over-satisfied | CLEAN | CLEAN | Re-healed the PRD↔URS audit seam: FRD-AUD-001..003 trace to URS/BR directly, gap flagged upstream instead of papered over |
| 6 | srs-writer | brief + FRD + URS + RTM; PRD text unrouted (body wants it) | DEGRADED (minor) | DEGRADED | Same gap class as run 1 but severity collapsed: all 6 invented numerics now ASSUMPTION-16..21 with owners; Twilio/FCM BAA facts WebSearch-verified, not memory |
| 7 | sdd-writer | brief + PRD + **SRS** + RTM (A1 edge delivered); **FRD not routed** | DEGRADED | **BROKEN** | All 17 SR-* mapped to real design (see §2); NEW seam: SDD-SUB-001 state machine "re-derived from the PRD, not checked against FRD's" (self-flagged) — and it drifted (§2) |
| 8 | backlog-manager | PRD+FRD+SRS+SDD+RTM = declared contract edges; URS via RTM/FRD Source | **CLEAN** | DEGRADED | Run 1's "compliance chain unaudited" closed: PBI→FRD→URS→BR now verifiable in RTM.md; caveat: "PBI-REM-001..006" range shorthand machine-orphans REM-004/005/006 (validate_reqs PBI-ORPHAN) |
| 9 | estimation-facilitator | backlog + brief only; body says read FRD/SRS — **unchanged gap** | DEGRADED | DEGRADED | 09 Notes: "my body says to read FRD/SRS... contract routes only the backlog" — drove Low confidence on QUE-001/REM-001/REM-006. The one audited seam not touched by the fixes |
| 10 | sprint-planner | backlog + estimates — contract fully satisfied | CLEAN | CLEAN | 13-pt commit vs 15 capacity; bounced ⛔A-n items on DoR; demoted CTRL-001 to stretch on mid-sprint-dependency grounds (stricter than estimator) |

**Tally: 6 CLEAN / 4 DEGRADED / 0 BROKEN (run 1: 4 / 4 / 2).**

## 2. Cross-artifact contradiction hunt
### 07-sdd vs 06-srs — is the SR-coverage table real? (7 spot-checks)
- SR-AVL-002 (outage catch-up) → SDD-REM-002 Catch-up Replayer, persisted watermark — a named component, absent in run 1. REAL.
- SR-INT-001 (Twilio pacing) → SDD-NOT-001 token-bucket at account MPS cap, queue-not-drop — run 1 had none of it. REAL.
- SR-AUD-002 (same-transaction audit) → SDD-AUD-001 + trade-off table *rejects* a separate log store explicitly because "SR-AUD-002 atomicity is trivial in one DB" — the constraint drove a decision. REAL.
- SR-SEC-005 (15-min idle) → SDD-SEC-001 server-side timeout + ASSUMPTION-22 + spike PBI-PLAT-002 to verify IdP capability. REAL.
- SR-OBS-001 (3 SLIs) → SDD-OBS-001 component + PBI-PLAT-004; run 1 SDD had zero observability. REAL.
- SR-PERF-002 (p95<2s@500) → SDD-QUE-001 read-model projection; trade-off row rejects joined queries for this exact target. REAL.
- SR-PHI-002 (Twilio BAA) → adapter + go-live gate; run 1's contradiction (SDD re-opened a question the SRS had answered) is gone. REAL.
Verdict: **coverage table is engineering, not decoration** — constraints appear in components, trade-offs, and backlog items, not just the table.

### The drift that DID occur — FRD↔SDD (the unrouted edge)
FRD state machine: `Pending → Awaiting-patient → Pending → Approved|Rejected`, with pharmacist withdrawal (FRD-SUB-005). SDD-SUB-001: `Pending → Awaiting-patient → Approved/Rejected` — omits the return-to-Pending transition and the withdrawal path. Exactly where the missing edge predicted, self-flagged by sdd-writer for spec-analyze. Mild, caught, but real.

### FRD↔URS↔PRD
- Run 1's Could→Must silent escalation: not reproduced — rejection next-step is ASSUMPTION-13, tagged, and PBI-QUE-003 is DoR-blocked on it.
- Run 1's convergent-invention (fail-safe rule invented twice): not reproduced — single origin ASSUMPTION-9 (URS), carried by tag through PRD→FRD→SRS→SDD→backlog.
- Persisting: URS-AUD-001/002 still have no PRD story — flagged in RTM header, FRD, backlog, handoff log (4 flags, 0 fixes; no loop-back to prd-writer exists).
- FRD-QUE-002 AC spans two PBIs after the backlog's decision/notification split (QUE-002 Ready, QUE-003 ⛔A-10/13) — documented, but done-ness of one FRD row now depends on a blocked sibling.

### Backlog trace spot-check (6 IDs)
PBI-AUD-001→FRD-AUD-001+SR-AUD-001/002 ✓; PBI-CTRL-004→FRD-CTRL-004+FRD-AUD-002 ✓; PBI-QUE-002→FRD-QUE-002/003/004+SR-SEC-004 ✓; PBI-REM-003→FRD-REM-003+SR-INT-001+SR-PHI-002 ✓; PBI-REM-006→SR-AVL-002 ✓ (SR-only, FRD deliberately deferred timing); PBI-SUB-002→FRD-SUB-002/003+FRD-AUD-003 ✓. All cited IDs exist. Sound.

## 3. Fix verdicts
| Fix | Verdict | Strongest evidence |
|---|---|---|
| A1 SRS→SDD | **FIXED** | Run 1: 14 SR-* unaddressed, 2 flags never arrived. Run 2: 17/17 SR mapped, 7/7 spot-checks show constraints driving components and trade-offs (Catch-up Replayer, token-bucket, same-transaction ledger) |
| A2 BRD→URS | **FIXED** | Run 1: zero BR- IDs in URS. Run 2: every URS row Source-cites a BR-, all 10 BRs covered, BRD assumptions carried by tag |
| E1 RTM materialization | **FIXED** (with tooling caveats) | RTM.md seeded by brd-writer, appended by 5 downstream writers in-pass; traceability grep covers all BR/URS/PRD/FRD/SR layers. Caveats: ".." range shorthand orphaned 3 PBIs to the validator; Test-case column empty (test-plan-writer still not in funnel); build_rtm --check "131 missing" is a matrix-vs-first-column convention clash, not agent failure |
| E3 Assumption ledger + DoR gate | **FIXED** | Continuous A-1..22 + ASSUMPTION-EST-1, every one tagged/owned/carried-not-reinvented. The gate has teeth: 10 of 26 PBIs marked not-Ready on ⛔A-n; sprint-planner committed only unblocked items — run 1's exact failure (its audit PBI shipping an unratified ≤5s AC in Sprint 1) cannot recur: the invented numeric (A-21) sits in PBI-AUD-002, which is blocked |

## 4. NEW findings this run revealed
1. **The FRD→SDD seam.** Fixing SRS→SDD exposed the next missing edge: FRD is not a contract input to sdd-writer, and the SDD-SUB-001 state machine measurably drifted from FRD's (missing return-to-Pending + withdrawal). Each repaired edge promotes the next absent one to the binding constraint.
2. **RTM shape is an unspecified contract.** Agents built a BR-keyed matrix (one row per BR, comma-lists per column); build_rtm --check expects one ID per first column → 131 false "missing". The E1 fix said *materialize* the RTM but never said *in what machine-readable shape* — the tool and the fleet hold different conventions.
3. **Range-shorthand orphans.** "PBI-REM-001..006" in the RTM is human-fine, machine-broken: validate_reqs orphaned PBI-REM-004/005/006 because they never appear as atomic IDs. A living RTM must be written for parsers, not readers.
4. **Quality-lint density.** 37 compound-shall advisories concentrated in FRD/SRS ("set state, remove from view, and notify") — no requirement-quality gate is wired into the writer loop; the lint exists but runs only post-hoc.
5. **Flags accumulate, nothing loops back.** The missing PRD auditability story is flagged in 4 artifacts across both runs and fixed in none — the fleet has feedback *annotations* but no re-dispatch mechanism to send prd-writer back to work.
6. **handoff-log.md became a sanctioned side channel.** prd-writer consumed ASSUMPTION-7..10 from the log instead of the unrouted URS — effective, but lossy by design ("via this log, not the URS"), and it quietly compensates for the one edge (URS→PRD) still missing from the graph.

## 5. Overall grade: **B+** (run 1: C+; delta: +2 steps)
All four fixes under test landed and are verifiably real, not performative: both BROKEN links are CLEAN/healed, the SDD's SR-coverage survives adversarial spot-checking, the RTM is a living cross-document artifact, and the assumption/DoR gate demonstrably stopped unratified facts from entering Sprint 1 — the precise failure mode of run 1. What remains is second-order: one measured drift (FRD→SDD state machine), one unchanged contract gap (estimation inputs), a flag-without-loopback culture, and machine-readability hygiene (range shorthand, RTM shape, compound shalls). Not an A because 4 handoffs still run degraded, the URS→PRD edge is still absent (patched by a side channel), and no fix loop exists for upstream flags — the graph is now sound, but its repair and hygiene loops are not yet closed.
