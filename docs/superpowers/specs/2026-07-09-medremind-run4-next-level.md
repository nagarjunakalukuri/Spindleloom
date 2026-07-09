# MedRemind Fleet-Eval — Next-Level Plan (RUN 4 → grade A)

**Date:** 2026-07-09 · **Status:** proposed · **Baseline:** RUN 3 verdict **A−** (RUN 1 C+ → RUN 2 B+ → RUN 3 A−)
**Artifacts:** `examples/medremind-fleet-eval/run3/` (01–10, RTM.md, verdict.md)

## 1. What RUN 3 proved

RUN 3 tested the current fleet plus the Part-A fixes (A1 transitive routing, A3 range lint, A4 quality gate, A5 flags register). Result: **7 CLEAN / 3 DEGRADED / 0 BROKEN** (run2: 6/4/0), grade **A−**.

- **A1 (transitive upstream routing) — FIXED, the headline win.** It closed *three* run-2 DEGRADED seams: URS→PRD (the audit story is now first-class in PRD ACs, no more handoff-log side channel), FRD→SDD (state-machine drift gone), and ancestors→estimation (estimates now *cite* SDD/SRS detail: `SDD ASSUMPTION-21`, `SR-PERF-002`, `SDD-CMP-010`). SDD and estimation demonstrably *used* ancestor context, not just listed it.
- **A3 (range lint) — FIXED.** Zero range-shorthand anywhere; the run-2 `PBI-REM-001..006` orphan class cannot recur.
- **A5 (flags register) — FIXED.** Every agent emitted `FLAG(owner)` markers; `sloom flags` surfaced **21 open flags across 10 owners** as a routed re-work queue.
- **A4 (quality gate) — PARTIAL.** The gate is real (`--strict` exits 1 on 38 findings) but the fleet *routed around* it: instead of splitting compound-shalls it added "requirement-quality note" prose justifying them; density stayed flat (37→38) and the gate is opt-in.

## 2. Why it's A− and not A (the three held-open issues)

1. **The estimation→sprint edge silently failed on a filename mismatch.** The context pack keys the input `estimates` and `match_inputs` could not resolve it to the on-disk `09-estimation.md` (singular/plural stem miss: `estimates` ≠ `estimation`). So sprint-planner reported the handoff "not on disk" and re-derived points blind → a **live decision contradiction**: `09-estimation.md` says the Must-slice needs **4–5 sprints**; `10-sprint1-plan.md` reaffirms **3 sprints**. The fleet *produced* the warning and failed to *propagate* it. This is the run-2 pattern repeating — A1 connected the deep edges, promoting the last unrouted hop (a filename convention) to the binding constraint.
2. **backlog-manager shipped a phantom PBI.** `PBI-PLAT-004` (audit/consent store) is referenced 5× (epic done-when, deps of QUE-004/-005/-006 + SUB-002, sprint-3 mapping, an RTM row) but has **no ranked, AC-bearing row** in the backlog table. `validate_reqs` and `build_rtm --check` both stay green because an RTM row exists — the gap is **machine-invisible**; only the deep cross-artifact read (estimation, sprint-planner) caught it.
3. **A5 surfaces but does not close.** The flag register makes the re-work queue visible and owned, but there is no backward re-dispatch — the phantom-PBI flag and the product-analytics metric flag are each raised by ≥2 agents and fixed by none within the run.

## 3. The RUN 4 fix set (each targets one held-open issue)

| # | Fix | Where | Acceptance |
|---|---|---|---|
| **B1** | **Robust input resolution (stem/plural-aware `match_inputs`).** Normalize input names and filename stems to a shared stem (`estimate`/`estimates`/`estimation` → `estimat`) before matching; fall back to the agent's `outputs` name. Kills the silent estimation→sprint drop. | `hooks/build_context_pack.py` (`match_inputs`) | `build_context_pack <run3> sprint-planner` resolves `estimates` → `09-estimation.md`; new unit test asserts the singular/plural/‑ion family resolves. |
| **B2** | **Backlog-completeness check.** Reconcile PBIs *referenced* (RTM rows, epic/dep/sprint mentions) against PBIs *defined* (an AC-bearing backlog-table row). Flag `PBI-REFERENCED-UNDEFINED` (the phantom class). | `hooks/validate_reqs.py` or a small sibling check | On run3, flags `PBI-PLAT-004` as referenced-but-undefined; clean on a well-formed backlog. Test. |
| **B3** | **Close the flag loop (auto re-dispatch) — the deferred A5-full feature.** `sloom run` consults `sloom flags`; a `FLAG(<owner>)` whose owner is an already-`done` upstream ledger row **re-opens** that row (status → `flagged`) and surfaces it as runnable re-work, so the orchestrator sends the owner back. `sloom run advance --strict` blocks a phase while owned flags target it. | `hooks/sloom.py` (`run`/`flags` integration) + `run-orchestrator` body | A `FLAG(backlog-manager)` on a done backlog step makes `sloom run status` list backlog-manager as re-runnable; test. |
| **B4** | **Give the A4 gate teeth.** Make the requirement-quality gate reduce, not annotate: (a) wire `validate_reqs --strict` into `on_md_edit` for requirement docs (advisory→blocking on the writer's own new IDs), and (b) require any retained compound-shall to carry a machine-checkable `<!-- quality-ok: <ID> single-subject -->` marker the lint recognizes, so unjustified conjunctions still fail. | `hooks/validate_reqs.py`, `hooks/on_md_edit.py` | Compound-shall count on a fresh run drops materially, or every retained one has a `quality-ok` marker; test. |
| **B5** | **Widen A3 to ellipsis ranges.** Also flag `…`/`...` prose ranges like `PBI-PLAT-001…-006` (advisory), so range-thinking is caught even outside machine rows. | `hooks/validate_reqs.py` (`RANGE_SHORTHAND`) | The ellipsis form raises the advisory; atomic IDs still clean. Test. |

**Priority:** B1 and B2 are the two defects that cost the A (both bounded, both testable) — do first. B3 is the highest-leverage feature (closes the last systemic gap the run-N series keeps naming). B4/B5 are polish.

## 4. Success criteria for RUN 4

- B1–B2 land with tests; `sloom check` + `pytest hooks/` green; `targets/` regenerated.
- A re-run resolves estimation→sprint (no 3-vs-N contradiction), and the phantom-PBI class is machine-caught.
- Judge grade **A**, with 0 DEGRADED-from-routing and the flag loop demonstrably closing at least one re-dispatch.
- Honesty bar unchanged: a real A− that names its remaining gaps beats a performative A.

## 5. Meta-finding (worth carrying beyond MedRemind)

The run-N series keeps validating one law: **each repaired edge promotes the next absent one to the binding constraint.** RUN 1→2 fixed SRS→SDD and exposed FRD→SDD; RUN 2→3's transitive routing (A1) fixed FRD→SDD/URS→PRD and exposed the estimation→sprint *filename* hop. The frontier has moved from *missing edges* (structural) to *edge fidelity* (naming, completeness, loop-closure) — the graph is sound; its **hygiene and repair loops** are the remaining work. RUN 4's B1/B2/B3 target exactly that layer.
