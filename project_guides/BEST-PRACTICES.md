# Documentation Best Practices

Shared conventions for every agent in this project. The goal is documentation that actually gets read and stays true — not a mountain of stale paperwork ("documentation fatigue").

## The funnel

Documents form a waterfall from 30,000 feet (business) to the trenches (code). Each refines the one above and hands off to the one below:

```
[MRD] Market problem      → mrd-writer
  ↓
[BRD] Business why / ROI    → brd-writer
  ↓
[PRD] User-facing features → prd-writer
  ↓
[FRD] Feature behavior     → frd-writer   (often merged into tickets)
  ↓
[SRS] Constraints / rules  → srs-writer
  ↓
[SDD] Architecture blueprint → sdd-writer
  ↓
[TSD] Build details        → tsd-writer
```

`doc-strategy-advisor` decides which of these a given team should actually maintain; `spec-driven-dev` keeps whichever you keep from drifting.

Above the funnel sits the **constitution** (`templates/constitution-template.md`) — the standing, AI-read-first guardrails (principles, boundaries, non-goals) that hold across all features. The funnel describes *this release*; the constitution describes *the system's durable law*. Build it once via the `/constitution` command and keep it versioned.

Alongside the funnel run the **engineering-craft lanes** the doc spine only touches generically: `ux-ui-designer` sits in the design phase doing UX **and** UI (PRD → flows/wireframes/hi-fi visuals + design system → `frontend-developer` implements them); `security-reviewer` is continuous (threat-models at the SDD, gates at review/CI); and `sre` owns proactive operate-phase reliability (SLOs/runbooks, feeding `incident-postmortem`). Four further specialists by need: `accessibility-auditor` (independent WCAG sign-off gate), `performance-engineer` (profiles and optimizes against a budget, behavior-preserving), `product-analytics` (instruments the PRD's success metrics to close the build→learn loop), and `ai-eval` (golden datasets + regression-eval gates for shipped AI features). Add each by what you're building (see `doc-strategy-advisor`).

## Feedback loops (documentation is not one-way)

The handoff flows down, but discoveries flow back up. Build these loops into how the docs are maintained:

- **Reality-check loop (SDD → PRD/SRS).** While designing, an architect may find a PRD/SRS requirement architecturally impossible or too costly (e.g. "global sync under 10ms"). Push back and force a scope update *upstream* rather than quietly missing the target.
- **Scope-adjustment loop (SRS/FRD → PRD).** Constraints uncovered during specification can change what's realistic to build this release.
- **Budget/timeline loop (any stage → BRD).** Effort or cost surprises can shift the business case itself.
- **Parallel-work loop (SRS/FRD → Dev + QA).** The moment the SRS/FRD is final, developers build from the SDD while QA writes test scripts from the SRS — same source of truth, so QA is ready the instant code lands.

Each specialist agent should, when it discovers something that invalidates an upstream document, flag it and route back to that agent rather than silently absorbing the conflict.

## Practices every agent follows

1. **Ban the PDF.** Keep docs in a searchable, editable workspace (Notion, Confluence, Git). If it isn't searchable or editable, it's dead.
2. **Definition of Ready.** A feature cannot enter a sprint until its technical blueprint (SDD/TSD/RFC) has been reviewed and signed off by at least one peer engineer.
3. **Embed logic in tickets.** Write a clean, high-level doc for context; put hyper-specific functional logic ("if user clicks X, then Y") in the Jira/Linear ticket, not a fat standalone FRD.
4. **One owner per document.** Shared ownership = no ownership.
5. **Capture the *why*, not just the *what*.** Record decisions and rejected alternatives so the next reader (human or AI) doesn't re-litigate or "fix" deliberate choices. For architecturally significant decisions, keep an append-only **ADR log** (`adr-writer`) in the repo — one immutable record per decision, superseded rather than edited. For significant changes that need debate *before* building, raise an **RFC** (`rfc`) — the forward-looking proposal opened for comment; an accepted RFC produces the ADR. RFCs live in `/docs/rfc`, ADRs in `/docs/adr`, both reviewed in PRs.
6. **Docs-as-Code where it fits.** Treat docs like code: Markdown in the repo, reviewed in the same PR as the code, deployed via CI/CD. This is the single biggest lever for keeping technical docs current.
7. **Update upstream before downstream.** When something changes, fix the source-of-truth document first, then let it flow down.

## Requirement quality standard (ISO/IEC/IEEE 29148 + INCOSE)

Every requirement any agent writes — in a BRD, PRD, FRD, SRS, or URS — should pass this checklist. It's the industry gold standard for well-formed requirements.

**Per requirement, ask:**
- **Necessary** — does it serve a stated goal/problem? If not, cut it.
- **Unambiguous** — only one reading is possible.
- **Singular** — exactly one obligation. If you wrote "and" or "or", split it into two.
- **Feasible** — achievable within constraints.
- **Verifiable** — you can prove it's met with a test or inspection.
- **Traceable** — links upstream to its source and downstream to design/tests.
- **Correct** — accurately reflects the real need.
- **Consistent** — doesn't contradict another requirement.

**Per requirement set, confirm:** completeness (no gaps), consistency (no conflicts), and feasibility (achievable as a whole).

### Writing rules
- Use **active voice with "the system shall …"** for functional/system requirements.
- **One obligation per statement.** The word "and"/"or" is a smell — split it.
- **Ban vague adjectives** ("fast", "user-friendly", "intuitive"). Replace with a measurable target: not "search should be fast" but "for `/v1/search`, P95 latency < 200 ms at <10 RPS/tenant; error rate < 0.1% over 24h".
- **Normative text is the source of truth; visuals are informative.** Diagrams, wireframes, and sequence charts aid understanding but the written requirement governs.

## Traceability backbone

A well-structured project traces in an unbroken chain, and every artifact carries a stable ID:

```
MRD (market goal) → BRD (scope) → PRD (feature) → FRD (behavior)
  → SRS (constraints) → SDD/TSD (design & build) → test cases → defects
```

- **Req-ID convention:** `<DOC>-<AREA>-<NUM>`, e.g. `FRD-AUTH-012`, `SR-PERF-004`, `URS-USE-003`, `PBI-CHECKOUT-007`. IDs never change once assigned. Doc prefixes: the SRS uses `SR`; the backlog uses `PBI` with the epic name as the `<AREA>`.
- **Link both directions:** each requirement names its upstream source and its downstream design/test artifacts (e.g. `FRD-AUTH-012` → `TEST-AUTH-045`). This lets you prove coverage and assess the blast radius of any change.
- Keep the traceability tables that each agent's template already includes in sync as the documents evolve.

**The Requirements Traceability Matrix (RTM)** is the named artifact that holds this chain: a single table mapping each business requirement → product/functional requirement → design → test case → defect. The BRD seeds it (business → PRD), and each downstream agent extends it. Maintain one RTM per project as living evidence of coverage; at audit or release time it proves nothing was dropped and shows the blast radius of any change.

## Change control & baselines

Documents are living, but changes should be deliberate, not silent:
- **Establish a baseline** at each decision point (sprint planning in Agile; a phase gate in waterfall).
- **Set a review cadence** — grooming each sprint, or formal phase-gate reviews.
- **Version explicitly** (v1.0, v1.1) and keep a change log of what changed and why.
- **Regulated contexts** (e.g. FDA 21 CFR 820.30) require a formal change board with reviews and signatures — the URS and its downstream docs fall under this.
- **Agile contexts** can baseline with a lightweight backlog-refinement vote; when a story closes, update the doc to reflect what actually shipped.

## Where artifacts live (information architecture)

> **See [`INFORMATION-ARCHITECTURE.md`](INFORMATION-ARCHITECTURE.md)** for the full, consolidated reference — the canonical `docs/` + `.shipwright/` layout, per-document vs per-feature, the metadata convention, versioning/baselines, and how to find anything. This section is the summary.

The golden rule: **one system of record per kind of thing.** Don't duplicate; link by ID (the RTM).

| Artifact kind | Lives in (system of record) | Why |
|---|---|---|
| Project-level docs (BRD, PRD, SRS, SDD, TSD, URS, RAID, status, coding-standards, CONTRIBUTING) | **Project wiki** (Azure DevOps Wiki / Confluence) **or** repo `/docs` (docs-as-code) | durable, searchable, shared; reviewed like content |
| ADRs, feature/RFC design docs, spec-driven `/specs` | **Repo** (`/docs/adr`, `/docs/specs`), reviewed in PRs | versioned with the code they govern; AI agents read them |
| **PBIs / backlog items / tasks / bugs** | **Work tracker** (Azure Boards / Jira) — the SoT | status, workflow, queries, capacity, links all live on the work item |
| Code, tests, pipelines | **Repo** | obvious |

### Project-level vs PBI-level — the rule
- **Project/feature documents** are written *once* and evolve; they belong in the **wiki/repo**. `doc-strategy-advisor` decides which to keep and where.
- **PBIs** are *work items*; their home is the **tracker**, not a markdown file. Put the story, acceptance criteria, and links **on the work item**; embed hyper-specific logic in the ticket (don't write a fat per-PBI doc).

### "Should I write a file per PBI (e.g. `pbi/PBI-123.md`)?"
Usually **no** — it duplicates the tracker and drifts (two sources of truth). Write a file only when:
1. **A complex PBI/feature needs a design doc or RFC** → `/docs/specs/<feature>.md` (or per-epic), *linked from* the work item — one doc covers many PBIs, not one-per-story.
2. **You're git-native** (e.g. issues-as-files, no separate tracker) → then the file *is* the tracker; fine, but pick one.
3. **As a generation/staging step** → `backlog-manager` emits markdown that you **import into Azure Boards**; the file is scaffolding, the tracker becomes the SoT. Never keep both as parallel truths.

Rule of thumb: **wiki/repo = durable knowledge; tracker = work items; linked by RTM IDs.** If you find yourself updating the same fact in two places, the architecture is wrong.

## Validation & quality gates

Two different questions, often confused — the toolkit handles both, but name them:

- **Verification** — "did we build it *right*?" (conforms to the spec). Mechanisms: each agent's **REVIEW mode**, **acceptance criteria**, the 29148 **"verifiable"** rule, and the **test-plan-writer** (cases traced to requirements).
- **Validation** — "did we build the *right thing*?" (meets the real need). Mechanisms: **PO/stakeholder acceptance**, **UAT**, and for regulated systems **PQ** (Performance Qualification).

### Gate at each stage
| Stage | Artifact | Verified by (right-built) | Validated by (right-thing) |
|---|---|---|---|
| Business | BRD/MRD | brd/mrd REVIEW vs rubric | Sponsor sign-off |
| Product | PRD | prd REVIEW; testable acceptance criteria | PO + stakeholder review |
| Functional | FRD | frd REVIEW; 29148 checklist | maps to a PRD story |
| Constraints | SRS/URS | measurable + verifiable; REVIEW | URS → PQ (regulated) |
| Design | SDD/ADR | reality-check loop; REVIEW | meets SRS targets |
| Build | TSD | API/schema specifics; REVIEW | — |
| Backlog item | PBI | INVEST + acceptance criteria | "so that" value link |
| Sprint work | increment | test-plan-writer cases pass | PO accepts; UAT |

### The PBI quality gates (how a story is validated end to end)
```
INVEST (well-formed)        → backlog-manager
  → acceptance criteria (testable)
  → Definition of Ready     → gate to ENTER a sprint (sprint-planner)
  → built + test cases pass  → test-plan-writer (verification)
  → Definition of Done       → gate to be ACCEPTED as complete
  → PO / UAT acceptance       → validation (value delivered)
```
A PBI that fails any gate goes back, not forward. The **RTM** proves coverage (no requirement without a test); **change control** keeps the gates honest over time.

The team's **Definition of Ready and Definition of Done** are the explicit gate criteria — keep them as one living artifact (`templates/definition-of-ready-done-template.md`) that the backlog-manager and sprint-planner reference rather than redefining per story.

## Frameworks worth adopting

| Problem | Framework |
|---|---|
| "We don't know how to structure our design notes" | **arc42** (pare to 4 core sections) + **C4 model** for diagrams |
| "Our wiki is a chaotic mess" | **Diátaxis** (Tutorials / How-to / Reference / Explanation quadrants) |
| "Developers won't update the wiki" | **Docs-as-Code** (Markdown in Git, reviewed in PRs) |

## Choosing your document set by team size

| Team | Keep | Notes |
|---|---|---|
| Lean (1–15) | 1-pager PRD (BRD+PRD) + RFC/TDD (SRS+SDD) | Two living docs, nothing more. |
| Mid (15–50) | PRD + FRD-in-tickets + SDD | Three docs; functional logic lives in Jira/Linear. |
| Enterprise (50+) | BRD → PRD → SRS → SDD (+MRD where needed) | Full stack, but automate the pipeline (BRD mandates PRD → auto Jira epics → linked SDD). |

Run `doc-strategy-advisor` to apply this to a specific team.

---

## Delivery patterns (pilot-hardened)

Patterns distilled from real SDLC funnel runs. Each addresses a recurring failure mode.

### Small-change lane (≤ ~3 well-scoped tasks)

Running the full funnel (decompose → recon → SDD → backlog split → sprint-plan) on a tiny, self-contained change is ceremony that wastes tokens and burns context. When the change is ≤ ~3 clearly-scoped tasks:

- **Collapse decompose into recon.** If `solution-recon` already enumerates an ordered task list, treat it as PBI-grade and skip the separate backlog-manager decompose call. The gate: could a developer start immediately from the recon output? If yes, proceed directly to build.
- Still run: recon → build → test-author → change-verifier → code-reviewer. The quality controls don't shrink; only the ceremony stages do.
- Right-size the funnel to the blast radius; don't right-size the quality gates.

### Project operating manual (avoid re-discovery per agent)

Key project-specific facts — Python interpreter path, test run incantation, repo root layout, per-package test commands — are re-derived by each new agent in a session if they're not persisted. This wastes tokens and causes friction (G8):

- **Use `save_agent_context` (MCP tool):** at session start, one agent resolves and saves the incantation; every subsequent agent calls `load_agent_context` first before running commands.
- **Use a project `CLAUDE.md` addendum:** add a `## Running tests` section with the literal, resolved commands for this repo (e.g., `uv run pytest oi_atlas_cache/tests/ -x`). Every agent reads CLAUDE.md at start.
- **On Windows with `uv`:** the interpreter is typically `.venv/Scripts/python.exe` and the test runner is `uv run pytest`. Write the resolved form once and reference it everywhere rather than re-probing per agent.

### Increment by blast radius

When a planned change includes both net-new/isolated work and a cutover of a hot path (shared infrastructure, heavily-imported module, live API endpoint or store), **ship them as separate increments** — not one combined change:

1. Build and verify the net-new isolated replacement independently.
2. Cut over the hot path in its own gated step with its own recon → build → test-author → change-verifier → code-reviewer cycle.

The cutover increment is the one that can break callers — it deserves its own blast-radius assessment, its own symbol-removal grep (see `backend-developer`), and its own `change-verifier` run. "Agent enthusiasm vs blast radius" is the failure mode: don't let the readiness of the isolated piece tempt a combined hot-path cutover in one pass (G11).

### Maker/checker split — mandatory, not optional

The maker/checker pattern is the pilot's **highest-ROI control** (G3/G13/G16):

- `code-reviewer` must be a **different agent from both the maker and the test-author**. The agent that wrote the bug is the worst one to spot it; the agent that wrote the tests can agree with the maker's wrong contract.
- For every cutover (hot-path migration, symbol removal, store replacement), run `code-reviewer` on the diff it did not write. This is not optional and not a ceremony — it is the control that catches Critical/Major bugs that tests and the verifier both miss.
- The maker builds → `change-verifier` executes the change → `code-reviewer` reads the diff statically. All three are distinct agents; collapsing any two collapses the separation that makes the loop work.

### Recon-before-implement — mandatory for brownfield

`solution-recon` must run before any brownfield implementation (G4/G10):

- Recon establishes ground truth: what the code actually does, not what the spec describes. In brownfield codebases, the spec routinely understates the work (broken import placeholders, "5 caches" that are really 3, shells that don't function).
- **Feed recon drift back into the ADR.** When recon finds a mismatch between the spec/ADR and the actual code (e.g., the ADR describes a 5-cache architecture but the code has 3), amend the ADR or write a superseding one — don't silently diverge (G10).
- Recon is per-family / per-epic, not per-task: one recon covers the whole feature; per-story builds cite it as warm context; per-task is a pointer, not a re-run.

### Brownfield cache / symbol-cutover playbook

The canonical template for migrating an existing brownfield store, cache, or shared symbol — proven repeatable across multiple caches in the pilot (G14/G16):

```
1. solution-recon   — establish ground truth; find broken shells, real contracts,
                      non-functional placeholders; amend the ADR if scope changed.

2. backend-developer (maker)
   a. Clone-and-re-point the nearest working sibling as a mechanical scaffold pass.
   b. Hand-edit only spec-driven logic.
   c. Symbol removal grep: grep -r "<old_symbol>" tests/ **/tests/ and fix every
      hit IN THE SAME CHANGE before handing off.
   d. Batch-verify: run the full suite (not per-file) before hand-off.

3. test-author      — write unit + integration tests; add consumed-shape parity
                      assertions for any fixture against the real consumer shape.

4. change-verifier  — impacted-test discovery first (grep all changed symbols across
                      ALL test dirs); run every hit suite; report gaps explicitly.

5. code-reviewer    — distinct agent from maker + test-author; all-call-forms grep
                      for every removed/renamed symbol; check pre-existing test suites
                      that import the changed package.

6. Repeat for each cutover unit (one increment per hot path, by blast radius).
```

Test-author discoveries (latent bugs surfaced while writing tests) route to `tech-debt-register`, not back to the maker — they are real bugs found during writing, not test failures. Apply cheap hardening (e.g., `isinstance` guards) in-loop rather than always deferring to a follow-up (G6/G9).
