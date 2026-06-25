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
