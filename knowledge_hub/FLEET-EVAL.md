# Fleet E2E Evaluation — the behavioral regression test for the agent chain

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Active protocol (v1, from the 2026-07-07 MedRemind run) |
| Complements | `validate_graph.py` (structural), this = behavioral |
| Reference run | `examples/medremind-fleet-eval/` — run 4 (A); runs 2-4 carry artifacts + judge verdict |
| Scope | The 10-agent **spec+plan spine** (market->plan). Build->test->ship->operate is validated structurally (the contract graph), not yet behaviorally. |
| Judge | A fresh AI subagent, same model family — not a human or third-party judge |

The validators prove the contract graph is *well-formed*; this protocol proves the fleet
*coordinates* — that each agent, given only what the graph routes to it, produces work the
next agent can build on. Run it after any change to agent contracts, the funnel shape, or
handoff conventions. The first run (MedRemind, 2026-07-07) graded **C+** and behaviorally confirmed two funnel
breaks static analysis had only predicted; both are fixed and now guarded by validator
check 13. Subsequent runs graded **B+ (run 2) -> A- (run 3) -> A (run 4)** as coordination
fixes landed. Note run 4's own verdict: part of the CLEAN sweep rides on a leaner backlog
(56 pts vs run 3's 106), so compare grades with output volume in mind, and the chain still
ends at planning — `security-reviewer` and the build->operate half are not yet in the run.

## Protocol

1. **Scratch run dir** with the golden brief (below) as `brief.md`.
2. **Chain the agents sequentially**, one isolated subagent per step, in funnel order:
   `doc-strategy-advisor → brd-writer → urs-writer → prd-writer → frd-writer → srs-writer
   → sdd-writer → backlog-manager → estimation-facilitator → sprint-planner`.
3. **Contract-strict inputs** — the experimental control. Each subagent receives ONLY the
   files the contract graph routes to it (its upstream edges' artifacts + the brief), is told
   to follow its `agents/<name>.md` definition exactly, and must NOT read other artifacts in
   the run dir even if present. Cap each artifact (~90–120 lines) to keep the run lean.
4. **Context memory** — when the `sloom` MCP server is available, every agent calls `recall_context(task_id=<run slug>)` at start and `save_context(...)` before finishing (with `source=` citing its artifact); the tooling pass runs `validate_gates.py <run-dir> --context <run slug>`. The handoff log below is the *judge's instrument*, not the transport.
5. **Handoff report** — every agent appends to `handoff-log.md`:
   `Inputs received / Inputs my definition expects / Missing at my handoff /
   Facts I assumed-or-invented (each, specifically) / Quality impact (one line)`.
6. **Tooling pass** — run `hooks/build_rtm.py <run-dir> --check` and
   `hooks/validate_reqs.py <run-dir>` against the generated artifacts.
7. **Independent judge** — a fresh subagent reads everything and scores per the rubric.

## Judge rubric

1. **Per-handoff verdict table** — CLEAN / DEGRADED / BROKEN per agent, with one-line evidence.
   BROKEN = a declared-or-needed input never arrived and the output shows it.
2. **Cross-artifact contradiction hunt** — diff each design/constraint pair the authors never
   saw together (especially SDD↔SRS); spot-check ≥6 backlog trace IDs for existence.
3. **Invented-fact cascade** — which flagged assumptions propagated downstream and were
   treated as ratified? (Convergent invention is coincidence, not corroboration.)
4. **Tier compliance** — did the run honor doc-strategy-advisor's doc-set decision?
5. **Context fidelity** — did downstream recalls match upstream saves (nothing invented that a saved entry already answered; nothing saved that contradicts the artifact it cites)?
6. **Grade A–F** with a 3-line justification.

**Pass bar:** no BROKEN handoffs, no severed RTM links, grade ≥ B. Anything below: file the
findings as contract fixes (inputs/edges), validator checks, or convention changes — the
2026-07-07 run produced check 13, the RTM seeder, the binding-tier rule, and the
assumption-ledger convention this way.

## Golden brief (v1 — "MedRemind"; keep stable so grades compare across runs)

> RxKart is a 40-store pharmacy chain with an existing mobile app (250k monthly active
> patients) and a pharmacist back-office portal. Build a **prescription refill reminder and
> approval module**: patients get refill reminders (push + SMS via Twilio/Firebase) and
> one-tap refill requests; pharmacists approve/reject from a queue and can propose a generic
> substitution the patient must accept. **Controlled substances (Schedule II–V)**: no
> auto-reminders or one-tap refills — extra identity verification + pharmacist-initiated
> contact. **HIPAA applies** — minimize PHI in notifications (no drug names in SMS).
> Business target: on-time refill rate 41% → 60% in 2 quarters. Stated NFRs: reminder
> delivered ≤5 min of schedule; queue p95 <2 s at 500 concurrent pharmacists; 99.9%
> availability during store hours. Team: 1 PM (acting PO), 1 architect, 4 devs, 1 QA;
> two-week sprints on Azure DevOps; leadership wants a first shippable slice in 3 sprints.

The brief is deliberately "a little complex": two personas, a regulated branch (exercises
URS routing), hard NFRs (exercises SRS→SDD), a third-party integration, business rules, and
a capacity-vs-mandate conflict the planning tail must surface honestly.
