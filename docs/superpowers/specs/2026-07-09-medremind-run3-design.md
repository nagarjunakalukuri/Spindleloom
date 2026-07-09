# MedRemind Fleet-Eval — RUN 3 Design

**Date:** 2026-07-09 · **Status:** approved-for-planning · **Baseline:** RUN 2 verdict (B+), RUN 1 (C+)
**Location under test:** `examples/medremind-fleet-eval/` (run2 artifacts `01`–`10`, `RTM.md`, `verdict.md`)

## 1. Goal

Close the open gaps RUN 2's verdict documented — at the **fleet level** (root-cause, not eval-local) — then re-drive the MedRemind market→plan chain under isolation as RUN 3, judge it against a target of **grade A**, and produce a deep gap analysis + the next-level plan.

RUN 2 landed at B+ with four handoffs still DEGRADED. Its §4 "new findings" and §5 name the remaining debt this run targets:

- **G1 — missing transitive upstream visibility.** `build_context_pack` routes only each agent's *declared* `inputs:`; it never walks the `upstream` graph. So `sdd-writer` never sees the FRD (state-machine drift), `prd-writer` never sees the URS (auditability story dropped; patched by a handoff-log side channel), `estimation-facilitator` never sees FRD/SRS (low-confidence estimates). The verdict's warning — *"each repaired edge promotes the next absent one"* — rules out piecemeal edges.
- **G2 — RTM shape is an unspecified contract.** Agents build a BR-keyed matrix; `build_rtm --check` expects one ID per first column → **131 false "missing"**.
- **G3 — range-shorthand orphans.** `PBI-REM-001..006` is human-fine, machine-broken: `validate_reqs` orphaned REM-004/005/006.
- **G4 — quality-lint runs post-hoc only.** 37 compound-shall advisories in FRD/SRS; no gate in the writer loop.
- **G5 — flags accumulate, nothing loops back.** The missing URS→PRD auditability story is flagged in 4 artifacts across 2 runs, fixed in 0 — no re-dispatch mechanism exists.

## 2. Non-goals

- No full auto-re-dispatch orchestration engine (G5 gets a *minimal* register now; the re-dispatch feature is deferred to the next-level plan).
- No new agent contract edges (the general-routing fix in G1 is explicitly the alternative to adding edges).
- Build→ship→operate phases stay out of scope — RUN 3 mirrors RUN 1/2's market→plan chain (doc-strategy → sprint-planner) so verdicts are comparable.
- `run2/` artifacts are preserved; RUN 3 writes to a new `run3/` dir.

## 3. Part A — Fleet fixes (the product changes under test)

Each fix lands in the real fleet **before** the run, since the run is the test of whether it worked. Each is stdlib-only and must leave the existing suite green (`sloom check`, `pytest hooks/`).

| # | Fix | Where | Acceptance |
|---|---|---|---|
| A1 | **Transitive upstream routing** — resolve each agent's `upstream` graph recursively; add a "§1b · Upstream chain (digest-first)" section to the pack listing ancestor artifacts (digest shown, full-read on budget), distinct from declared inputs. | `hooks/build_context_pack.py` (+ read `upstream` from contracts, reuse `rtm_core`) | `build_context_pack.py <root> sdd-writer` lists the FRD as an ancestor; `prd-writer` lists the URS; `estimation-facilitator` lists FRD+SRS. New unit test. |
| A2 | **RTM-shape acceptance** — count a Req-ID as present wherever it appears in RTM.md (matrix or first-column), not only in column 1. | `hooks/build_rtm.py` (`--check`) and/or `hooks/rtm_core.py` | The run2 BR-keyed matrix yields 0 false-missing (was 131). Regression test with a matrix-shaped RTM. |
| A3 | **Range-shorthand lint** — flag `<ID>..<ID>` shorthand in RTM/backlog as a machine-broken advisory (RANGE-SHORTHAND). | `hooks/validate_reqs.py` (quality lint) | `PBI-REM-001..006` raises the advisory naming the orphaned atomic IDs. Test. |
| A4 | **Quality-lint as a writer gate** — make the compound-shall / vague-term lint runnable as a gate a writer invokes before handoff (documented in the writer agents' bodies + a `sloom reqs --lint` path or `on_md_edit` wiring). | `hooks/validate_reqs.py`, relevant writer agent bodies | The lint is invocable per-writer and documented in ≥1 writer contract; existing post-hoc behavior unchanged. |
| A5 | **Open-flags register (minimal)** — a convention + a `sloom flags <root>` command that greps artifacts for unresolved upstream flags (e.g. "flagged … no loop-back") and lists them as re-work items with the target agent. | `hooks/sloom.py` (new `flags` subcommand) + a short note in `STANDARD.md` | `sloom flags` on run2 surfaces the URS→PRD auditability flag naming `prd-writer` as the owner. Test. |

**Fleet-integrity obligation:** after A1–A5, re-run the generator loop + `validate_graph` + `pytest hooks/` and regenerate `targets/`. All gates green before the run.

## 4. Part B — The re-run (RUN 3), under isolation

- **Mechanism:** a `Workflow` script drives the pipeline (explicit multi-agent orchestration, user-approved).
- **Isolation is the eval:** each agent runs as its own subagent, handed **only** its routed context pack (now transitive) + the shared RTM — never the whole folder. This is what surfaces real handoff behavior instead of my authoring.
- **Pipeline (sequential — each consumes prior outputs + RTM):** doc-strategy-advisor → brd-writer → urs-writer → prd-writer → frd-writer → srs-writer → sdd-writer → backlog-manager → estimation-facilitator → sprint-planner.
- **Inputs:** the same `brief.md` RUN 1/2 used (identical stimulus → comparable verdict).
- **Outputs:** `examples/medremind-fleet-eval/run3/01`–`10`, a run3 `RTM.md`, `handoff-log.md`.
- Each stage emits structured output (the artifact + a self-declared "what I received vs needed" note) so the judge has evidence.

## 5. Part C — Judge → analyze → plan

- **Judge:** an independent subagent (not one of the 10) produces `run3/verdict.md` in the RUN 2 format: per-handoff CLEAN/DEGRADED/BROKEN table (vs run2), cross-artifact contradiction hunt, fix verdicts for A1–A5, and an overall grade measured against A.
- **Deep gap analysis:** what remains after RUN 3 — which of G1–G5 closed, which new binding constraint the fixes exposed (the verdict's "promotes the next absent edge" pattern).
- **Next-level plan:** the RUN 4 fix set + methodology to reach A (incl. the deferred auto-re-dispatch feature), written as its own short spec.

## 6. Success criteria

- A1–A5 land; `sloom check` + `pytest hooks/` green; `targets/` regenerated.
- RUN 3 verdict shows the four RUN 2 DEGRADED handoffs improved (target: FRD→SDD drift gone, URS→PRD story present without the side channel, estimation confidence up), and 0 BROKEN.
- Grade ≥ B+ with a documented, evidence-backed path to A. (An honest B+/A- with real fixes beats a performative A.)
- The judge is adversarial and independent; a regression (grade down, new BROKEN link) is reported plainly, not hidden.

## 7. Risks & mitigations

- **Token cost** (10 isolated agents + judge). Mitigation: digest-first routing keeps packs small; the pipeline is bounded to 10 + 1.
- **A1 over-routing** (ancestor chain balloons the pack). Mitigation: digest-first, full-read only on budget; §5 budget/demotion already exists.
- **Judge leniency / author-judge coupling.** Mitigation: judge is a distinct subagent given only the artifacts + brief, prompted to refute and to compare against run2 evidence.
- **Fleet fixes destabilize the suite.** Mitigation: each fix ships with a test; full green gate before the run.
