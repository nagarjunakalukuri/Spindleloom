# Pilot Plan — Proving the PM-Agents Toolkit (one-pager)

*Purpose: validate that the toolkit produces good outputs and measurably improves delivery, on one real project, in 4–6 weeks — before any wider rollout.*

## Objective
Move the toolkit from "excellent design" to "proven practice" by running one real project through the agent chain and measuring the impact on **speed, quality, and clarity** against a baseline.

## Scope (deliberately small)
- **One project / one team.** Pick a real, self-contained initiative of ~1–2 epics (not the most critical system, not a toy). A web/app build is ideal so the FE/BE/API/data agents are exercised.
- **Lean agent set first**, not all 31: `doc-strategy-advisor` → `prd-writer` → `backlog-manager` → `estimation-facilitator` → `sprint-planner` → `code-reviewer` + `coding-standards-writer` → `pipeline-engineer` → `qa-tester` → `release-manager` → `retrospective-facilitator`, with `raid-keeper` + `status-reporter` for governance. Add `sdd-writer`/`api-designer`/`data-modeler` if the design warrants.
- **On Azure DevOps** as the system of record (Boards, Repos, Pipelines, Wiki) — toolkit is the authoring/standardization layer.

## Team
The existing pod: Principal Director (sponsor), PM (+PO hat), Architect, 2 Leads, 5 Developers, QA. Name a **pilot owner** (the PM) accountable for running it and reporting.

## Timeline (4–6 weeks)
| Week | Focus |
|---|---|
| 0 (pre) | Capture **baseline** metrics from a comparable past project; set targets; agree the Definition of Ready/Done |
| 1 | Inception: doc-strategy pick, PRD, lean specs, backlog created in Azure Boards |
| 2 | Estimate + plan sprint 1; build starts; code-review & CI gates live |
| 3–4 | Sprint(s): build → review → CI → QA → release to staging; RAID + weekly status |
| 5 | Release (go/no-go), operate, first retro; one incident drill if feasible |
| 6 | Measure, compare to baseline, write the readout |

## Success metrics (baseline → target)
| Metric | How measured | Target vs baseline |
|---|---|---|
| **Output quality** | Architect/lead score sample artifacts (PRD, stories, PRs, tests) on a 1–5 rubric | ≥ 4/5 average; reviewers prefer vs ad-hoc |
| **Cycle time** (story start→done) | Azure Boards analytics | ↓ 15–25% |
| **Defect escape rate** (bugs found post-merge / in QA vs prod) | qa-tester + bug work items | ↓ measurable; fewer prod escapes |
| **PR review clarity/time** | time-to-first-review; rework rounds | ↓ rounds; faster reviews |
| **Requirement churn / rework** | stories reopened or re-specced | ↓ vs baseline |
| **Spec→dev clarity** | dev survey: "I knew what to build" (1–5) | ≥ 4/5 |
| **Team experience** | short DevEx/SPACE pulse (flow, cognitive load, feedback) | neutral-to-positive |

Keep DORA (deploy freq, lead time, change-fail, MTTR) from Azure analytics as context. **Guardrail:** the toolkit must not *increase* documentation overhead beyond ~10% of capacity — if it does, that's a finding.

## Roles in the pilot
PM = pilot owner & report; Architect = artifact-quality scorer; Leads = run reviews/estimation; Devs = build + give the clarity/DevEx feedback; QA = defect data; Director = sponsor + final readout audience.

## Risks & mitigations
- **Process over product** → lead with the lean set; enforce the right-sizing/Definition-of-Ready guardrail.
- **Baseline hard to get** → use a comparable recent project or the team's own estimates; note the confidence level.
- **Too small to be conclusive** → pick something real with genuine ambiguity, not a toy.
- **Hawthorne effect** (people try harder because measured) → note it; weight the artifact-quality and escape-rate metrics over raw speed.

## Decision gate (end of week 6)
- **Scale** — quality ≥ target and ≥1 of cycle-time/escape-rate improved, no overhead blowout → roll out with the tier model, add missing actors (designer, DevOps/SRE, security).
- **Adjust** — mixed results → trim to the agents that paid off, re-pilot.
- **Stop** — no quality lift and added overhead → shelve; keep only the few high-value agents.

> **Interim readout filed:** [`PILOT-READOUT-INTERIM.md`](PILOT-READOUT-INTERIM.md) — a *proxy* run (4 AEP backlog items, AI-driven, no Wk-0 baseline) against the live IDP project. Verdict **ADJUST → run the real team pilot**, with a Wk-0 environment-readiness baseline + a pre-pickup existence check added. Not a substitute for the full human-team run below.

## The ask
Approve a **4–6 week pilot** on one named project, a pilot owner (PM), and ~half a day of the Architect's time to score outputs. Cost: marginal (the team's existing capacity). Upside: a data-backed decision on whether to standardize delivery on the toolkit.
