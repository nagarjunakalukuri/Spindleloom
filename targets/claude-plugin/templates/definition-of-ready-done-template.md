# Definition of Ready & Definition of Done — <Team / Project>

One living team artifact. The **DoR** is the gate a backlog item must pass to *enter* a sprint; the **DoD** is the gate work must pass to be *accepted as complete*. The `backlog-manager` and `sprint-planner` reference this — don't redefine per story.

| Field | Value |
|---|---|
| Owner | <PM / team> |
| Last agreed | <date> |

## Definition of Ready (to enter a sprint)

A PBI is Ready when **all** are true:

- [ ] Written as a user story ("As a… I want… so that…") or a clearly-typed item (bug/spike/task)
- [ ] Has testable **acceptance criteria** (Gherkin *or* rule-checklist), **co-authored in a Three Amigos pass** — not written solo (`project_guides/STORY-CRAFT.md` §3)
- [ ] Meets **INVEST** (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [ ] **Right-sized** — 6–10 similar stories fit one sprint (`project_guides/STORY-CRAFT.md` §5)
- [ ] **Estimated** (story points)
- [ ] No blocking dependency (or the dependency is scheduled first)
- [ ] Traces to a source requirement (PRD/FRD ID) in the RTM
- [ ] **No unratified assumptions** — every upstream `ASSUMPTION-n` this item's AC depends on has been ratified by its owner (or the item is blocked on that decision, not Ready)
- [ ] UX / design available where needed
- [ ] **Backend/data readiness — recon-backed** — for brownfield / platform-extension work, a **`solution-recon` section exists** for the feature (seam · real contract · sibling-to-mirror · ordered touchpoints); it is both the readiness check *and* the executor's warm build context (see `solution-recon` → "Recon is the build's warm context"). For a UI/screen story, the endpoint(s) and data it consumes are confirmed to exist; if not, a blocking **backend PBI is split out and scheduled first**. Don't spec a UI against a non-existent endpoint. *(The recon doubles as the warm handoff, so this adds **no new gate** — the 5-minute recon you already run becomes the Ready signal AND the thing the builder reads first; the alternative is dead/stub UI, a mid-sprint surprise, or a builder re-exploring the code cold.)*

## Definition of Done (to be accepted as complete)

Work is Done when **all** are true:

- [ ] Code complete and merged to the main branch
- [ ] Peer-reviewed (PR approved)
- [ ] Unit + integration tests written and passing; coverage ≥ target
- [ ] **Ran green locally before review** — build, the changed tests, and the linter were executed and pass (the running suite is the source of truth, not a static read)
- [ ] Acceptance criteria verified **by execution** — the changed path was run and observed to meet each criterion, not merely covered by a test that exists (`verification-run-and-observe`)
- [ ] **Independently checked** — `change-verifier` (maker ≠ checker) returned a PASS verdict with a complete acceptance-criteria coverage matrix (no uncovered or red AC)
- [ ] **AI/LLM features:** the `ai-eval` regression suite passes (unit tests alone are insufficient for model-backed features)
- [ ] Non-functional bars met (perf/security/accessibility as applicable)
- [ ] Docs / ADRs / RTM updated
- [ ] No open critical/high defects
- [ ] Product Owner has accepted it

## Notes

<Team-specific additions: e.g. feature-flagged, deployed to staging, demoed at review. For regulated work, add validation-protocol (IQ/OQ/PQ) sign-off to the DoD.>
