---
name: cross-artifact-analysis
description: Detect contradictions, coverage gaps, and drift ACROSS spec artifacts (requirement↔design↔tasks↔tests↔ADR), beyond ID-level traceability. Use before implementation, in a spec review, or when one document seems to disagree with another. Returns severity-grouped findings with the exact doc to fix.
---

# Cross-artifact analysis

Traceability (`traceability-rtm`) proves every ID links both ways. Requirement quality (`requirement-quality`) proves each requirement is well-formed. **Neither catches a requirement that contradicts the architecture, or a designed component nobody built.** That semantic, between-documents layer is what this skill covers — the cheapest place to catch "translation loss" is before code is written.

## The six pairwise checks

For each, read both artifacts and look for the failure mode named.

1. **Requirement ↔ Design.** Every FRD/SRS requirement has an SDD/TSD element that can *satisfy* it — not just trace to it. Flag any requirement whose constraint the chosen design cannot meet.
2. **Design ↔ Tasks.** Every SDD/TSD component appears in the backlog/PBIs. Flag *designed-but-unbuilt* (no PBI) and *built-but-undesigned* (PBI with no design basis = scope creep).
3. **Requirement ↔ Requirement.** Two requirements that cannot both hold (contradiction), or the same intent under two IDs (duplication).
4. **Acceptance criteria ↔ Test plan.** Every PBI acceptance criterion maps to a test case. Flag untested criteria.
5. **ADR ↔ current design.** SDD/TSD choices that contradict an *accepted* ADR, or significant decisions made with no ADR recorded.
6. **Terminology drift.** One concept named differently across docs (e.g. "user" / "member" / "account") — a latent ambiguity that becomes a real bug. Prevent it proactively with `ubiquitous-language`; this check is the after-the-fact backstop.

## Severity

- **Blocker** — a contradiction that will cause rework if implemented as-is.
- **Gap** — missing coverage (unbuilt, untested, undesigned).
- **Drift** — stale or divergent between documents.
- **Nit** — terminology only.

## How to apply

1. Load the artifact set (funnel docs + RTM + ADRs + backlog + test plan).
2. Run the six checks. For each finding, name the **two artifacts involved** and the **single doc to fix** (per "update upstream before downstream" in `knowledge_hub/BEST-PRACTICES.md`).
3. Never assume the code is correct — the spec is the reference.

## Output format

```
BLOCKER  Requirement ↔ Design: SR-PERF-002 requires P95 < 200 ms, but SDD §4 chooses
         synchronous fan-out to 5 services — that path cannot meet the budget.
         Fix: SDD (introduce async/cache) or renegotiate SR-PERF-002 upstream in SRS.
GAP      Design ↔ Tasks: SDD component "notification service" has no PBI. Fix: backlog.
GAP      AC ↔ Tests: PBI-ORD-004 AC "stock reflects within 5 s" has no test case. Fix: test plan.
DRIFT    ADR ↔ Design: TSD picks REST, but ADR-0001 accepted event-driven. Fix: TSD or supersede ADR-0001.
NIT      Terminology: PRD says "member", FRD/SRS say "user". Fix: pick one in PRD, flow down.
```
End with a one-line verdict per check (pass / N findings).
