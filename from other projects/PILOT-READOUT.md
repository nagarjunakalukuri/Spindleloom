# Pilot Readout — PM-Agents Toolkit on the live IDP project (INTERIM / proxy signal)

| Field | Value |
|---|---|
| Companion | [`PILOT-PLAN.md`](PILOT-PLAN.md) (the gate this report answers) |
| Pilot vehicle | The **IDP-Accelerator** repo — AEP decouple work (`../aep_decouple/`) |
| Period | 2026-06-15 → 2026-06-16 |
| Status | **Interim readout — proxy signal, not the full pilot** |

> **Read this caveat first.** `PILOT-PLAN.md` specifies a 4–6 week run by a *human team* with a Wk-0 baseline and an Architect scoring outputs. **This was not that.** It was **4 backlog items driven by an AI agent in a single session**, against an already-written spec set (`aep_decouple/`). So the human-team metrics (cycle-time %, DevEx pulse) are **not measurable here** and are reported as *N/A — needs the real run*. What this run *can* honestly show is whether the framework's **gates and discipline catch real problems** on live code. They did. Treat this as evidence to justify the real pilot, not a substitute for it.

## 1. What was run (4 items, mixed types)

| # | Backlog item | Type | Outcome |
|---|---|---|---|
| 1 | TEST-RULES-010..017 | tests vs existing code | 8 route tests, green; spec → tests near-mechanical |
| 2 | TEST-RULES-020..022 | tests vs existing code | 3 FE tests, green; **surfaced an unconfigured Vitest harness** |
| 3 | **PBI-RAG-BE-001** | **build from scratch** | service + 3 routes + 11 tests; planner→build→security-review→fix |
| 4 | PBI-RAG-FE-001 | verify (already built) | 3 FE tests green; **found spec/code drift — nearly rebuilt existing code** |

Item mix is the main threat to validity: **3 of 4 were test-authoring/verify; only 1 was a true build.** The framework's value showed up almost entirely on that one build item.

## 2. Measurements vs `PILOT-PLAN.md` targets

| Metric | Target | This run | Substantiated? |
|---|---|---|---|
| **Artifact quality** | rubric ≥ 4/5 | Spec set is validator-green, RTM-complete, template-conformant (independent conformance audit: high). | **Partial** — strong on *objective* dimensions; no independent Architect rubric score (the plan's ½-day step) was done. |
| **Cycle time** | ↓ 15–25% | — | **No** — no Wk-0 baseline; AI-driven, single session. Cannot claim. |
| **Defect-escape rate** | ↓ | The **gates caught real defects pre-merge**: security review caught an injection-shaped bug (RAG-BE `document_ref`→Search key); the PBI-orphan check found 3 untraced PBIs; the test migration proved 3 failures pre-existing (no false blame). | **Direction only** — gates demonstrably catch defects; *rate* needs a prod-comparison baseline. |
| **Spec→dev clarity / DevEx** | positive | Spec rows (acceptance criteria + status-code matrix) translated to tests with near-zero ambiguity on item #1. | **Anecdotal** — no human DevEx pulse. |
| **Doc overhead (guardrail)** | ≤ ~10% | A few RTM/backlog/test-plan rows per item + an auto-validator; spec set pre-existed. | **Yes** — comfortably under in this run. |

## 3. Findings

**Worked (carry forward):**
- **Plan-first earns its keep on build-from-scratch.** On RAG-BE, the planner step caught that `aep_search_index_manager` already existed (prevented a rebuild) and surfaced the audit-container / provisioning / embedding-cost decisions *before* coding.
- **The security gate caught a real bug** the build missed (`document_ref` unsanitized into an Azure Search doc-key). Defense-in-depth working as designed.
- **Enforced traceability is the framework's rare, real asset.** The RTM + `validate_reqs.py` stayed green per item; the new PBI-orphan/ADR checks found 3 genuine RTM gaps the moment they were added.
- **Low doc overhead** — the discipline did not bloat the work.

**Friction / gaps (the framework does NOT model these):**
- **Environment-readiness is unmodeled and bit us twice** — the idp-api unit suite didn't collect (stale `app.*` imports) and the Vitest harness was installed-but-unconfigured. The spec funnel assumes a working build/test environment; neither was checked.
- **Spec↔code drift** — RAG-FE was shipped in a prior session with **no backlog/test-plan/RTM update**, so the spec said "deferred" while the code was done; this run nearly **rebuilt an existing feature**. The validator traces *spec→PBI*, not *PBI→does-the-code-exist*, so it can't catch this.
- **Test-authoring is low-value overhead for the framework** — items #1/#2 would have been fast with or without the ceremony.

## 4. Decision-gate recommendation → **ADJUST**

Per the `PILOT-PLAN.md` gate (Scale / Adjust / Stop):

- **Not Scale** — the signal is real but thin (1 true build, AI-driven, no human baseline). Scaling on this would be overclaiming.
- **Not Stop** — there *was* a clear, repeatable win (plan-first + security gate on build work; enforced traceability), so shelving would discard something valuable.
- **ADJUST — run the real pilot, with three changes baked in:**
  1. **Add a Wk-0 "environment-readiness" baseline check** (build + test suites collect & pass; lint runs) — the recurring failure mode, currently invisible to the funnel.
  2. **Add a "pre-pickup existence check"** to `pbi-next`/`backlog-manager` (does the artifact already exist?) — closes the spec↔code drift that nearly caused a duplicate build.
  3. **Apply the lean-10**, and reserve the full ceremony (plan-first, security gate) for **build-from-scratch** items — skip it for pure test-authoring, where it's overhead.
- **At the real Scale step**, add the missing engineering-craft actors the gate names: **designer, DevOps/SRE, security** first, then (as the project warrants) privacy/compliance, accessibility, and product-analytics. Add only those a given project needs — see `doc-strategy-advisor` tiers.

## 5. Threats to validity (be honest about these)
- AI-driven in one session, **not** a human team over weeks.
- **No Wk-0 baseline** → speed/defect-*rate* deltas are unmeasurable.
- **Item mix skewed to tests** (3/4) → under-samples the build work where the framework matters most.
- Spec set was **pre-authored**, so the upstream funnel (MRD→SDD) wasn't itself exercised in this run — only backlog→build→test→trace.

## 6. Bottom line
The framework's **enforced traceability and its quality gates demonstrably caught real defects and prevented rework** on live IDP code — the clearest evidence yet *for* it, and it appeared on the one build-from-scratch item. But this proxy run is too thin and too AI-driven to graduate it to "Scale." **Recommendation: run the real team pilot per `PILOT-PLAN.md`, with the three adjustments above** — most importantly the Wk-0 environment-readiness baseline, the gap that bit this run twice.

---

## Addendum — Run 2 (2026-06-20): PM-agents + Boards + IA migration

A second proxy run exercised the **delivery chain** (`backlog-manager` → `sprint-planner`) on a real AEP-first re-prioritization, pushed the v2 backlog **end-to-end to Azure Boards** (4 epics / 8 features / 45 stories + a closed `[v1]` history epic), and migrated the artifacts to the **canonical information architecture** (`docs/specs/`, `docs/adr/`, `docs/RTM.md`, `.shipwright/` catalog + baseline). It confirmed the delivery chain + `solution-recon` work well on brownfield, and surfaced a fresh batch of tooling/IA gaps — most notably **no backlog→Boards automation**, **no brownfield-migration path**, and a **catalog that doesn't flag duplicate IDs** (it caught an `ADR-0004/0005` collision but only by inspection).

→ All Run-1 + Run-2 improvement candidates are consolidated in **[`IMPROVEMENTS.md`](IMPROVEMENTS.md)** (prioritized).

---

## Addendum — Run 3 (2026-06-20): Information Architecture on a brownfield repo → **ADJUST**

**Tested:** organizing the v2 SDLC artifacts (specs, ADRs, RTM, backlog, sprint plans) with the toolkit's IA on a repo that already has a mature `docs/01–18` taxonomy + a `12-decisions` ADR log.

**What happened — the finding is the oscillation.** We reversed the same files three times: (1) migrate to toolkit-canonical `docs/adr`+`docs/specs`; (2) the catalog caught an **ADR-ID collision** (`docs/adr/adr-0004/0005` vs existing `12-decisions/ADR-004/005`); (3) adapt → ADRs into `12-decisions` (ADR-015/016); (4) tidy → `docs/19-v2-program` to match the numbered taxonomy; (5) realize the goal is **standard-setting**, reversing 3/4. The thrash *is* the result: **the toolkit has no explicit stance (impose-a-standard vs adapt-to-project) and no brownfield migrator**, so a real repo bounces between layouts.

**Verdict — ADJUST.** The toolkit must (a) declare **one** stance — a project-agnostic **STANDARD** — and (b) ship a **converter** so brownfield repos convert deterministically. Without (b), every adoption repeats this.

**Worked:** the **catalog/registry is layout-agnostic** (scanned `docs_root`, detected kinds by filename token across both ADR dirs, caught the collision on first run); the **3-plane model** (durable docs / living tracker / baseline snapshots) answers "global vs sprint docs"; metadata headers + per-sprint baseline gave the catalog teeth.

**Improvements:** IMP-001 (migrator) → now #1, proven; IMP-003 (numeric-only ADR id can't namespace → one global sequence, migrator-enforced); **NEW** IMP-018 `STANDARD.md` (the IA reads as a *default* not a *standard* — the reason we waffled), IMP-019 config-driven layout knobs (default = standard), IMP-020 document the 3-plane + lean `sprints/` + baseline-per-sprint. See `IMPROVEMENTS.md`.

**Recommendation:** lock *standard + converter*; write `STANDARD.md`; build the migrator; convert this repo as the reference. **Stop hand-moving files until the converter exists** — that hand-moving caused the churn.

---

## Addendum — Run 4 (2026-06-21): Board grooming → the docs↔tracker sync gap → **ADJUST**

**Tested:** a full grooming pass on the live v2 Azure Board — repairing acceptance criteria into the native **Acceptance Criteria field** (was crammed in Description), re-tagging Sprint-1/2 to the AEP-first plan, polishing epics to the epic-template, and decomposing the ready Sprint-1/2 stories into **Tasks** (29 created). Plus the backlog-manager refinements already cited inline (split-on-blocker on CLOSE-004; PBI-type routing after a Decision PBI was mislabeled "lean code fix").

**Headline finding — the gap is one-directional drift.** Every grooming write went **board-first**, and *nothing flowed back to the docs*. The board ended up **ahead of the source**: richer AC (Gherkin/checklist) lived only on the work items, the 29 Tasks existed nowhere in the docs, and **not one board ID was recorded in the RTM** (the Azure column was entirely `—`). Worse, `backlog.md` still advertised itself as "the acceptance-criteria reference" — a role that had silently migrated to the board. Per the toolkit's own golden rule (*one system of record per kind*), board-first is *correct* — but the toolkit **declared a system of record without defining the direction, the field map, or an ID write-back**, so the two drifted with nothing to catch it.

**Root cause — same as the original defect.** The "AC-crammed-in-Description" problem (IMP-007) and this drift have one root: the docs→board flow was never a **codified field map** (which doc field → which work-item field) with a write-back step. Done by hand each time → wrong the first time, untraceable the second.

**Verdict — ADJUST (gap real; fix shipped in-toolkit this run).**
- `backlog-manager` → new **Tracker sync contract**: direction (seed once → board is SoR → board-first after), the doc→work-item **field map** (AC → its own field, never Description), **write-back** (IDs → RTM Azure column), Tasks-are-tracker-only, drift rule (tracker wins).
- `INFORMATION-ARCHITECTURE.md` → new **Directionality & drift** subsection (empty Azure column = a drift gap, not a finished load).
- **RTM write-back applied**: Azure column filled for all 25 requirement rows + the 29 Tasks recorded (`docs/RTM.md`).
- `backlog.md` reconciliation note: board is authoritative for AC; this file is the requirement-trace/generation source, not the live AC copy.

**Worked:** the grooming itself held to `STORY-CRAFT.md` (native AC field, Gherkin vs rule-checklist chosen per story, vertical tasks); the RTM already *had* an Azure column waiting for write-back — the structure was right, only the loop was open; the DoR "ready" filter correctly **held CLOSE-001/003** (runtime/release-blocked) out of task decomposition rather than faking readiness.

**Improvements / recommendation:** the sync contract is the durable fix — but it's still a *contract a human applies by hand*. The standing **Run-2 gap (no backlog→Boards automation)** is now the natural next step: a `backlog.md` → Boards **emitter** that applies the field map and writes IDs back to the RTM automatically, closing the seam permanently. Unchanged hard limit: **iteration paths need a project admin** (MCP auth lacks the classification-node permission) — sprint mapping stays on `sprint-N` tags until then.

---

## Addendum — Run 5 (2026-06-21): First build under "toolkit drives, OrionIDP executes" → **ADJUST**

**Tested:** the first real **build-from-scratch** under the operating model the user set this session — *the toolkit drives the SDLC process; OrionIDP's domain agents execute the code*. Built AEP Class 210 (CEMS) end-to-end: toolkit `dev-onboarding` **readiness gate** → OrionIDP `orion-extractor` implements (9 new files, 16 modified) → `security-reviewer` + `code-reviewer`. Result: **built + green** — 79 new unit tests, plus 244 AEP-skills + 34 orchestrator-AEP regression, **no regressions**; security **APPROVED**.

**The pilot signal — trust the running suite over static claims.** Two false alarms, one root cause:
1. The readiness gate first reported **76 collection errors** — an artifact of a *single multi-package `pytest` call* (cross-package basename/`conftest` collisions). Per-package collection was clean. The gate was right; my *use* of it was wrong.
2. The `code-reviewer` agent returned a confident **"Critical: ImportError"** — refuted by the green suite (the import resolves; Python imports any module-level name, not just `__all__`). A blocking finding the tests disprove is a false positive.

**Worked (carry forward):**
- **The "four-whitelist gotcha", enumerated in the plan, got wired correctly** — all four sites (ingest whitelist, `applicable_classes`, manifest registry, handler registry) + the four per-class state-key lists. Naming the known multi-site failure mode *in the plan* prevented it. -> toolkit lesson: plans should enumerate multi-site wiring gotchas explicitly.
- **`security-reviewer` caught the real posture** (210 logs no emissions values — stricter than 209; deterministic path = zero LLM/injection surface).
- **The model held end-to-end** on a real build: the domain executor carried the 15-class/AEP knowledge the generic doers lack while the toolkit framed the gates.

**Real findings vs false alarms:** code-review flagged two *genuine* lint items (`Optional[X]` -> `X | None` UP007; an E303 blank-run) the **green suite did not catch** — *tests passing != lint clean*. It also surfaced a **pre-existing 209 architectural gap** (the assertion node reads `extraction_result[...]` while the engine forwards the filing list top-level → the assertion *summary* is empty when rules are seeded; the handler `force_hitl` is the real T1 teeth, so HITL routing stays correct). Pre-existing OrionIDP tech-debt, **not** a toolkit gap.

**Verdict — ADJUST (model validated; two refinements applied to `dev-onboarding`):**
1. Readiness gate -> **collect per-package in a monorepo/workspace**, not one combined call.
2. VERIFY -> **"trust the running suite over static claims"** — verify any blocking finding (human or agent) against the actual run; a green suite != lint-clean (run the linter too).

The "toolkit drives, OrionIDP executes" reconciliation is **confirmed workable for build-from-scratch** — the clearest build-side evidence yet. *AEP-210 follow-ups (OrionIDP, not toolkit): the two lint items + the 209/210 assertion-summary nesting gap → a lint pass + a small PBI; the build is functionally green + security-approved meanwhile.*

### Run 5 (cont.) — latency root-cause + the warm-context handoff fix

The user then flagged **high latency across the run** and asked for a complete analysis. Two adversarially-verified workflows followed (a 13-agent latency analysis; a 5-agent context-pack design) — each one killing plausible-but-wrong fixes before they shipped:

- **Latency root cause = the monolithic, author-from-scratch executor build** — ~20 min / 102 serial tool round-trips ≈ **68% of the critical path**, and it is **round-trip-bound, not token-bound** (43k tokens — the *lowest* of the fleet). The Wheelwright toolkit was **exonerated** (inert markdown + stdlib, on no execution path). Parallelism is **mostly maxed** (the cheap branches already ran parallel; the build chain is intrinsically serial — a fan-out was modeled and **refuted**). The real lever is **orchestration: edit-from-template + warm context handoff**, not more parallelism. Five plausible-but-wrong fixes were adversarially killed (parallel sub-builds · blame-the-toolkit · de-Opus sweeps · MCP-payload-bloat · ruff-in-reviewer).

- **Root cause #3 (cold re-exploration) fixed project-agnostically.** The "context pack" is **not a new artifact — it is `solution-recon`'s `recon.md` promoted to a required executor input.** Wired across 4 agents (recon/architect → backend/frontend-developer), **zero new files**: executors now read recon FIRST (seam · real contract · sibling-to-mirror · touchpoints) instead of cold-re-greping what recon already found. Granularity: **one recon per feature/epic (group pack) + per-task delta on the tracker**. Greenfield (degrade to SDD/TSD) and recon-vs-code staleness (re-verify-the-seam) gaps closed. DoR: a brownfield PBI is Ready only if its recon section exists — **rides the existing backend-readiness gate, no new gate.**

**Toolkit verdict — IMPROVE (shipped this run):** `dev-onboarding` (per-package collect + "trust the running suite over static claims") **+** the `solution-recon` → executor **warm-context handoff** (recon as the build context pack). **Resolved (standalone design):** the scaffold-pass / logic-pass executor split — verdict **REJECT the agent**; the build is round-trip-bound *and* serial, so a split attacks only a single-digit-% slice (~6–12 mechanical touchpoints of ~102) while the 68% reasoning chain is untouchable. Folded into the executors' `edit-from-template` bullet (scaffold-before-logic + prefer a repo generator if one exists) + a `solution-recon` clause (name the generator). No new agent / skill / toolkit codemod — a scaffolder agent was the highest-surface, lowest-payoff option on the table. **Meta-honesty:** diagnosing multi-agent latency *with* multi-agent workflows is ironic, but the adversarial passes earned it — they refuted both a false "Critical" review finding and five false fixes. Non-negotiable prerequisite before trusting any latency %: **instrument per-agent + per-tool timing into `cost-log`** (the dates are still "TBD").

---

## Addendum — Run 6 (2026-06-21): First delivery under the full warm-context flow (AEP-208 GIA) → **VALIDATED (with a measurement lesson)**

**Ran:** the first real class build under the *complete* shipped flow — toolkit `solution-recon` (family warm context) → `orion-extractor` edit-from-template → verify → security + code review — for **AEP-208 (GIA)**, a contract/legal class.

**Warm-context earned its keep — it prevented an architectural wrong turn.** The brief (and my build prompt) assumed 208 was a *pure-GPT* class needing a new extractor + prompt. The recon, reading the code, **corrected that**: there is **no pure-GPT AEP class** — every one ships a deterministic synthetic-JSON path + an *additive* real-PDF path through a **shared** `PdfExtractionService` + **shared** `aep-pdf-extract@1.0.0` prompt; the right sibling is **207 (PUC Rate Case), not 210**. So the build **cloned 207 and added no new architecture or prompt** — exactly the cold re-exploration + rework the warm handoff exists to kill. Strongest evidence yet for recon-as-context-pack. Edit-from-template also worked on a **non-deterministic (GPT-PDF) sibling**, not just the 209/210 deterministic case.

**Outcome:** 208 shipped + green (17/17 domain · 272/272 skills · 14/14 workflow-reg); security **APPROVED**; the deferred **210 lint cleanup** folded in. Two *real* 208 issues caught + fixed: code-review's **F401** (`field_validator` unused — genuine this time, **verified** against the code) + a dead duplicate preclassifier pattern + a stale `# type: ignore`. **3 RED** were **verified pre-existing** (git: the failing files aren't in this session's changeset; a stale `_FakeCosmos` `parameters`→`params` double) → a separate tiny fix, not 208's.

**The verify discipline held in both directions** — code-review's Critical was *real* this time (verified true), and the 3 RED were *false-on-208* (verified pre-existing via git). "Trust the running suite over static claims" separated real from false in both cases.

**Measurement lesson (the honest gap):** wrapping the build in a *workflow* obscured the metric — only the aggregate (5 agents · 251 round-trips) is returned, so the clean **208-vs-210's-102** round-trip comparison isn't available, and the ~6.4 h `duration` is wall-clock-including-idle, not compute. **Lesson:** measure a *single agent's* round-trips with a **direct `Agent` call**, not a workflow. (Recorded in `.claude/sessions/agent-timing.md`; the next build — 212/213 — runs as a direct call to capture the quantitative delta.)

**Verdict — VALIDATED.** The warm-context + edit-from-template flow delivered a real, non-trivial class *correctly* and **prevented a wrong-architecture rework** — the qualitative win is decisive. The quantitative latency proof is deferred to the next direct-call build.

**→ Measured (Run-6 close — 212/213 direct build):** the family build ran as a single direct `Agent` call → **115 tool round-trips to build TWO classes (212 PPA + 213 Vegetation)** vs the **210 cold build's 102 for ONE** — **~57/class, ~44% under the cold baseline**, *even including* the agent debugging two self-introduced clone bugs (a PPA `aep_only` mis-filter + garbled test byte-literals) to green. The warm-context + edit-from-template levers are now validated **quantitatively**, not just qualitatively (caveat: part of the per-class drop is family-batching, part is warm-context — both are shipped levers, not separable here). Both 212/213 reviews **APPROVED** — **no F401 this time (the 208 lesson held)**; one non-blocking `ruff format` reflow (`vegetation_mgmt_parser.py`) deferred to the lint pass. **AEP Phase 1.5 (208/210/212/213) complete; 214/215/216 + the Phase-C OPS-000 enabler remain.**

---

## Addendum — Run 7 (2026-06-21): Toolkit-gap audit + the verify gate catching a build over-claim → two discipline wins

Two findings, both the same principle this pilot keeps proving: **trust the running code/tests over a confident report.**

**1. The toolkit-gap audit — 3 of 4 "open gaps" were already implemented.** Asked to fix four "still-open" toolkit gaps, a read of the hook code *before building* showed three were already shipped:
- **Brownfield migrator** → `scaffold.py migrate()` (dry-run/apply, ADR + dest-collision guards, link-rewrite, self-exemption) — the IMP-001 "#1 missing piece" was built since Run 3.
- **Duplicate-ID detection** → `rtm_core.audit()` (`DUP-ADR`/`MULTI-ADR-DIR`) + `conformance()` (`DUP-ARTIFACT-ID`) — the Run-2 gap, fixed since.
- **Agents-as-subagents** → `build_harness_artifacts.py` emits a Claude plugin + loose `.claude/agents/` + cursor/copilot/windsurf/agents-md — invocable agents already exist; only the *install* hadn't been run.

The gap-list (recalled from memory) was **stale**; reading the code caught it and **prevented rebuilding three existing features** — exactly the Run-1 "don't build what exists / spec↔code drift" failure mode, this time avoided *on the toolkit itself*. Only **one** gap was real: no backlog→tracker emitter. Closed with `hooks/emit_backlog.py` (parse → field-mapped work-item plan → ID write-back; **5/5 tests**, dry-ran on the real 45-PBI backlog; the auth-gated tracker push is a documented pluggable adapter). Wired into `backlog-manager` + the IA tools table.

**2. The verify gate caught a build's over-claim.** The AEP 214/215/216 build reported "clean run, all 15 wiring touchpoints." Verify found it had **never run `test_aep_regulatory_workflow_registration.py`** — production's `applicable_classes` included 214/215/216 but the test's hardcoded expectation didn't, so it was RED. Verify found + fixed it (16→19 tests). The build's self-report was wrong; the independent run was right. (Same run: a security-review "pre-existing PII logging" flag was checked → **false alarm** — the `facility_name` string is the HITL alert *message*, a public plant name, not a log line.)

**Verdict — no toolkit change needed (already mature); process win recorded.** The structural toolkit is more complete than the running gap-list claimed — keep the gap-list honest by *reading the code*, not memory. The discipline holds across all 7 runs: **a confident claim — a gap, a "clean build," a "Critical" — is a hypothesis until the code/tests confirm it.** The one genuine add (`emit_backlog.py`) closes the recurring backlog→Boards automation gap at every offline-testable layer. AEP Phase 1.5 (201–216) is complete; AEP-OPS-000 (Phase-C enabler) is the next AEP item.

---

## Addendum — Run 8 (2026-06-21): Agent-graph orchestration repair → a codified validator beats ad-hoc verify → **ADJUST (toolkit add)**

Triggered by a "does the fleet have orchestration gaps?" audit on the toolkit's own agents.

**1. Real orphan / half-wired edges existed in the agent graph.** The fleet's handoff graph (auto-generated `INDEX.md` from each agent's `upstream`/`downstream` frontmatter) had genuine gaps: `wiki-curator` was orphaned (its prose said "hand off to it", the frontmatter didn't), reject/rework loops weren't encoded, `raid-log` had no inbound trigger, and two one-sided edges (`rfc`←`architect`, `estimation-facilitator`←`solution-recon`). Fixed all reciprocally; enhanced `build_agent_index.py` to emit an "Entry points (no inbound)" section that documents the 4 intentional foundational agents and auto-surfaces future orphans.

**2. The headline: a codified validator caught what an adversarial agent missed.** Last turn's fix was checked by an ad-hoc Workflow verify stage that reported `reciprocity_ok=true`. This run I built `hooks/validate_agent_graph.py` (the agent-graph analog of `validate_reqs.py`: dangling-ref + forward-reciprocity + orphan checks; the dual-loop "invoked-from" asymmetry is INFO-only by design). On its first run against the *"already-fixed"* graph it **exited 1** — finding **2 half-wired edges** (`dev-onboarding`→`backend-developer`/`frontend-developer`) the adversarial verify had **missed**. Fixed; validator now exits 0; 6 unit tests green. **Lesson:** an adversarial *agent* is a hypothesis-checker; a deterministic *hook* is a guarantee — when an invariant matters, codify it into a CI gate instead of re-running a one-off reviewer. This is the first run since Run 4 to produce a genuine toolkit tool (contrast Run 7's "already mature, no change").

**3. The recurring docs↔tracker drift is now a permission wall.** AEP Phase 1.5 (208–216) is built + green, but its Boards work items (67893–67899 + 24 child tasks) are still `New`, and the A-work (sec-MEDIUM PDF-dispatch coverage) has no tracked item. Reconciling the board — the exact sync the toolkit exists to enforce — was **blocked by the harness permission classifier** as an external publish not covered by the in-session prompt. So the sync contract and `emit_backlog.py` are real, but **headless/agent execution cannot practice the tracker write-back without an explicit write-approval path**. This is an environment-readiness gap (IMP-015 family) at the tracker boundary, not a toolkit-logic gap.

**4. Env-readiness recurred, with a workaround.** `uv run ruff` still trips os-error-6 in the main loop; `.venv/Scripts/ruff.exe` works directly, and **subagents can run `uv run pytest`/`ruff`** even when the main-loop shell can't — so delegate test/lint verification to a subagent (recorded to memory).

**Verdict — ADJUST: one genuine toolkit add (`validate_agent_graph.py` + tests, wired into the IA tools table) and one unresolved process gap (tracker write-back needs an approval path for headless runs).** AEP Phase 1.5 (201–216) remains complete; AEP-OPS-000 is the next AEP item.

---

## Addendum — Run 9 (2026-06-22): AEP-OPS-000 delivered via the full toolkit loop → recon caught a latent PRODUCTION bug → **VALIDATED (strongest signal yet)**

OPS-000 (the Phase-C enabler) run end-to-end under "toolkit drives, OrionIDP executes": `solution-recon` → `architect` → ADR-018 → build → security + code review → fix pass.

**1. The headline: warm-context recon caught a latent PRODUCTION bug CI had missed for months.** `solution-recon` (which *ran* the code, not just read it) found the AEP ingest route's `engine.run()` resolves builtins via a legacy dict lacking the AEP nodes — so `aep_regulatory` (the shipped Phase-A path, 201–216) was registered + routable but **not executable**: `engine.run()` raised `Unknown builtin node 'validate_aep'`, *swallowed* by the route's broad `except` into a `202/success=false`. CI never caught it because the one ingest integration test **mocks `engine.run`**, so the real graph was never compiled; the 385 green AEP unit tests cover parsers/handlers, not route→engine execution. The `architect` independently verified it against the code. **This is the pilot's strongest evidence to date** — the recon-first + adversarial-review flow caught a *class of defect that unit tests and mocked integration tests structurally cannot*: a real shipped production gap, not a process nicety.

**2. The review gate enforced the ADR's own DoD.** The build deferred the unmocked-engine route test ("if feasible"); `code-reviewer` flagged it as must-address because **ADR-018 itself lists it as a required consequence** — the exact blind spot that hid the bug. The fix pass added it (`test_aep_ingest_real_engine.py`). Security review independently confirmed the Class-223 force-HITL control is deterministic + non-bypassable (the override survives `enrich_aep` → `route`), and verified all 9 orchestrator-suite failures were pre-existing & unrelated.

**3. Decision discipline held.** FD-1 (which builtin-resolution path) was resolved by `architect` with a trade-off table → **ADR-018** (option b: fix in the legacy dict, minimal blast radius on the live path), with the bigger `WorkflowExecutor` migration deferred to a tracked **ADR-019** rather than smuggled into an enabler. ADR-017's now-superseded assumption got an append-only cross-reference, not an edit.

**4. The tracker-write permission wall (Run-8's gap) recurred.** Board reconciliation (OPS-000 → Resolved + 3 follow-on stories #67985/#67986/#67987) was again denied by the harness classifier until the user explicitly approved — and even then denied some calls inconsistently (1 of 3 identical creates; a child-task close), requiring retries. The IMP-015 "headless tracker write-back needs an explicit approval path" gap stands unchanged.

**Verdict — VALIDATED.** OPS-000 is the clearest demonstration of the pilot's thesis: recon-first + independent architect + adversarial review catches defects the existing test discipline cannot. One real production bug found + fixed + regression-tested; one new ADR; Phase C unblocked. **Net toolkit change: none needed** — the flow worked as designed; the only standing gap is the tracker-write approval path (process/harness, not toolkit logic).

**Run-9 gap-analysis correction (post-hoc).** A verify-pass over the toolkit (5 parallel checkers, each defaulting to "already-covered") found that **Run-8's `validate_agent_graph.py` was a DUPLICATE** of the pre-existing, more-comprehensive **`hooks/validate_graph.py`** — I'd read `build_agent_index.py` but never `HOOKS.md`, so I rebuilt a validator that already existed (the Run-7 "read before you build" lesson, repeated on myself). **Removed** `validate_agent_graph.py` + its test; **ported its one unique check** (orphan / no-inbound with an entry-point allowlist) into `validate_graph.py` as check #10. The analysis also surfaced: (a) **`validate_graph.py` is RED on 7 pre-existing asymmetries** (debugger/flaky dual-loop + architect←frd/sdd "invoked-from" edges) — a standing inconsistency between the canonical full-symmetry validator and the fleet's intentional invoked-from edges (resolve by conforming the fleet *or* relaxing the validator — a design call, surfaced to the owner); (b) two genuine doc gaps, now fixed — the "don't mock the component under test / require an unmocked-wiring test per seam" rule (→ `skills/test-design`), and the headless tracker-write approval caveat + the missing `emit_backlog.py` row (→ `HOOKS.md`). **Meta-lesson reinforced: a gap analysis must read the canonical index (`HOOKS.md`) first — a "new tool" is a duplicate until you've checked what already exists.**

---

## Addendum — Run 10 (2026-06-22): End-to-end grooming of an under-specified phase (AEP Phase C 217–225) → **VALIDATED**

First **end-to-end backlog-grooming** run under the toolkit: discovery/recon → `backlog-manager` + `estimation-facilitator` (per-class fan-out) → board. Took AEP Phase C — nine *under-specified* operational classes — from "no schemas/manifests/mapping" to **9 Ready, estimated, board-resident PBIs**.

**1. Recon PINNED the mapping — no grooming guesswork.** The recon agent read `AEP_DOMAIN_UNDERSTANDING.md §5.2` + `AEP_HANDOVER.md §7.2` and found the class↔number mapping **authoritatively listed** (217 OEM Manual … 225 Spare Parts), so it did *not* fall back to "assign in listed order." Tiers: 223=T1 (always-HITL) and 219=data-quality are doc-pinned; it flagged the other 7 T2/T3 assignments as an **inference to confirm with architect/PO** rather than asserting them. Warm-context recon again de-risked the work and was honest about what was inferred vs sourced.

**2. The flow produced consistent output from a shared template.** Nine parallel author agents each emitted one PBI (title, description, AC-in-its-own-field per the field-map, MoSCoW, 5-pt estimate) from a single shared build-template + dependency context — uniform structure, per-class specifics (223 force-HITL, 220 mandatory isolation/PPE fields, 219 handwritten −0.10 penalty, 225 LastTimeBuy-always-HITL). 45 pts total. All 9 written to Boards under F2 (#67868), gated behind OPS-000 + eval-control #67985; OPS-000 task #67945 closed.

**3. The board-write permission wall sharpened (Runs 8–10).** With explicit approval the **CREATEs all went through** (9 PBIs), but **DESTRUCTIVE writes were denied**: removing the 3 superseded coarse stubs was allowed for 1 of 3 (#67903) and **denied for #67901/#67902** — the classifier (correctly) distinguishing "create/update what you made" (approved) from "remove a pre-existing item" (needs its own explicit grant). The IMP-015 headless-write gap now has a clear contour: **destructive tracker writes need per-item authorization even within an approved grooming run.**

**4. Under-spec items flagged, not hidden.** The grooming surfaced (and recorded on the PBIs, not buried) the real refinement risks: the operational rule model is undefined (zero-rule no-op start, gated behind #67985), the 223 curation-UX is richer than the standard review node (possible split), the 219 −0.10 penalty may be uncalibrated, and RAG-index provisioning per class is unresolved. A groom that says "here's what's still unknown" beats one that fakes completeness.

**Verdict — VALIDATED.** The toolkit's discovery→backlog→estimation flow took an under-specified phase to Ready end-to-end, with inferences and unknowns honestly flagged. **Net toolkit change: none** — the flow worked as designed. The one standing operational gap is unchanged and now sharper: headless tracker writes (especially *destructive* ones) need an explicit approval path. Phase C is now Ready to build, one gated per-class PBI at a time.

---

## Addendum — Run 11 (2026-06-22): Building the whole AEP Phase C tier (9 classes) → pattern-setter + batched fan-out + adversarial gate → **VALIDATED**

Executed the Run-10 backlog: built **all 9 Phase-C classes (217–225)** end-to-end on the OPS-000 `aep_operational` workflow. Sequence: **218 pattern-setter** (proved `aep_operational` actually executes for a real class — the OPS-000 R1 concern — and locked the clone template) → **sequential batches** (217/219/220, 221/222/224, 225/223) to avoid shared-file collisions → **adversarial final gate** (independent full-suite re-run + manifest-wiring check + parallel security + code review) → **remediation**. End state: **972 tests green, security PASS, new files ruff-clean.**

**1. Verify-don't-trust recurred and paid off — twice.** (a) The build agents' summaries repeatedly **under-listed files** (a "build 3 classes" run listed only its test files); a filesystem glob confirmed the schema/parser/handler/wiring all existed — the work was real, the *report* was lossy. (b) The gate's **authoritative dir-wide ruff run** surfaced "58 findings," but attribution proved **100% pre-existing Phase-1.5 debt — zero in the new files**, and the scary **S105 "hardcoded password" was a false positive** (`"CONDITIONAL_PASS"`, a commissioning enum). Lesson: a green per-file build claim and a red dir-wide gate are *both* true — always attribute findings to new-vs-existing before acting.

**2. The gate caught real new-code defects a green suite passed over.** 972 tests were green *with* a SCADA data-quality bug (no-dot tags mis-classified as `unknown_namespace` instead of `invalid_format`), an **audit-traceability gap** (manifest docstring listing 3 of 9 PBIs), and **tracker IDs leaking into a runtime routing-override `reason`** (would land in Cosmos audit). Tests don't assert taxonomy-correctness or audit-cleanliness; the review did. All fixed.

**3. Pattern-setter + sequential batches is the right shape for a multi-class tier.** Proving one class end-to-end before replicating ×8 de-risked the OPS-000 enabler once (not nine times); sequential batches kept the shared `manifest.py`/`preclassifier.py`/`__init__` wiring conflict-free (parallel fan-out would have corrupted them).

**Verdict — VALIDATED.** recon → groom → build(pattern-setter + batches) → adversarial-gate → remediate delivered an entire operational tier (9 classes) with real defects caught by review that the suite passed over. **Net toolkit change: none.** Standing gaps unchanged: headless *destructive* tracker writes need an approval path; the pre-existing Phase-1.5 ruff debt (57 findings) is a separate cleanup the gate usefully surfaced.

---

## Addendum — Run 12 (2026-06-22): Gap-resolution sprint off the pilot-verdict list → **VALIDATED (one small toolkit add)**

Worked the pilot-verdict gap backlog to ground: **#4** (9 `params`/`parameters` orchestrator tests), **#67985** (eval-control), **Gap-3** (agent-pipeline routing tests), the **Phase C board reconcile** (9 PBIs → Resolved, 3 stubs Removed), and a **hygiene pass** (AEP-dir ruff 57→0; W-3 logging-kwarg sweep across 7 nodes). All green/verified; uncommitted per the pilot's skip-commits stance.

**1. The mandatory security gate caught a CRITICAL the green suite + build self-reports missed — the strongest evidence yet for the non-negotiable `security-reviewer`.** #67985 built TDD-first (276 green) and the build's own self-check reported clean — but the build had relaxed the eval allow-list (to pass shipped seeds) in a way that reopened a `str.format` sandbox escape: `"{0.__init__.__globals__[__builtins__]}".format(field)` walks the format mini-language to module globals → **secret exfiltration**, invisible to the AST dunder check (the dunder lives inside a constant string). `security-reviewer` caught it; remediation closed it with triple defense-in-depth (positive method allow-list + no-method-on-literal + dunder-string tripwire); re-review PASS. Tests are necessary, not sufficient — the security gate is what made this safe.

**2. "Verify-don't-trust" kept paying, repeatedly.** Build summaries under-listed files (caught by `glob` on disk); ruff's F401 auto-fix nearly deleted a live re-export (caught by the import break); a dir-wide ruff gate reported "58 findings" that were **100% pre-existing** (new files clean); the "9 failures" / Gap-3 reds / S105 were each **stash/baseline-verified pre-existing** before being attributed. Separating *introduced* from *pre-existing* was the recurring discipline of the whole run.

**3. One small toolkit add (the only net change).** That attribution discipline was strong in `debugger` ("bisect / localize to the change that introduced it") and `dev-onboarding` ("trust the running suite over static claims"), but **`code-reviewer` only said "read the diff"** — it didn't name the case where a gate runs wider than the diff and surfaces pre-existing debt. Added **core principle #6 — "Attribute findings to the diff, not the gate's blast radius"** to `agents/code-reviewer.md` (stash/baseline-verify a red is from the change; flag pre-existing debt separately rather than blocking the PR).

**Verdict — VALIDATED; net toolkit change ≈ one line.** The fleet caught real defects (a security CRITICAL, dead-code, audit gaps) the suites passed over; the only content gap was the `code-reviewer` attribution nuance, now closed. The standing operational gap is unchanged: **IMP-015** (headless tracker-write approval) — every board write this run again needed a fresh human approval; the fix is a permission-allowlist settings entry (drafted), which is the user's to apply.
