# Team Roles & Azure DevOps Fit

*How a real team runs this toolkit: who drives which agents, and how the artifacts map onto Azure DevOps as the system of record. (Salvaged from the original project review; the one-time verification audit and 5-project stress test that accompanied it have been retired as spent.)*

---

## 1. Team of 9 — who runs what

Team: **1 Principal Director, 1 Project Manager, 1 Architect, 2 Leads, 5 Software Developers.**

One important note up front: there is **no dedicated Product Owner / Product Manager** in this team. Someone must own the PRD, backlog priority, and acceptance — by default the **Project Manager wears the PO hat**, with the **Principal Director** setting business priorities. Flag this as the single biggest role gap to resolve before kickoff.

| Person | Primary agents they drive | Ceremonies / responsibilities |
|---|---|---|
| **Principal Director** (sponsor/exec) | mrd-writer, brd-writer (approves) | Sets business goals & funding; approves BRD/charter; consumes status reports; go/no-go at releases. Accountable, not hands-on. |
| **Project Manager** (+ acting PO) | doc-strategy-advisor (start here), prd-writer, backlog-manager, sprint-planner, retrospective-facilitator, raid-keeper, status-reporter | Owns the doc strategy, backlog priority & PRD; runs Sprint Planning, facilitates the retro and daily standup; tracks risks and reports status; manages the Azure board. |
| **Architect** | sdd-writer (arc42/C4, HLD), adr-writer, srs-writer (NFRs), spec-steward; the technical-direction layer (rfc-facilitator, tech-radar-curator, tech-debt-keeper, /spec-constitution) | Owns architecture & significant decisions (ADRs); sets technical constraints & sanctioned tech; reviews leads' designs; guards the Definition of Done's technical bar. |
| **Lead 1 & Lead 2** | frd-writer, tsd-writer (LLD/API contracts), estimation-facilitator, backlog-manager (refinement), code-reviewer | Translate PRD→functional specs; write the build spec with the architect; facilitate Planning Poker; run backlog refinement with the team; review developers' code; mentor. Split by feature area (one lead per 2–3 devs). |
| **5 Developers** | Consume frd/tsd; contribute to estimation (Planning Poker), ADRs, and backlog refinement; pr-author, test-author, debugger | Implement stories/tasks; estimate as the team that does the work; raise ADRs for local decisions; keep the board updated; participate in standup/review/retro. |

### How the 9 complete a project end-to-end
1. **Inception** — Principal Director + PM run `mrd-writer`/`brd-writer`; PM runs `doc-strategy-advisor` to pick the doc set for a 9-person (Mid-tier) team: **PRD + FRD-in-tickets + SDD**, with TSD for the build.
2. **Definition** — PM (PO hat) writes the PRD; Architect + Leads produce SRS/SDD; Architect logs ADRs and sets the constitution/tech-radar.
3. **Breakdown** — PM/Leads run `backlog-manager` (PRD/FRD → epics → PBIs); whole team runs `estimation-facilitator` (Planning Poker).
4. **Delivery loop** — `sprint-planner` each sprint (goal + capacity-fit backlog); devs build; daily standup; Architect/Leads review (`code-reviewer`); `retrospective-facilitator` at sprint end; repeat.
5. **Governance/Release** — PM runs `raid-keeper` + `status-reporter`; Leads run `test-plan-writer`/`qa-tester`; `release-manager` handles go/no-go with the Director.

This maps to a clean **RACI**: Director = Accountable (business), PM = Responsible (delivery/process), Architect = Accountable (technical), Leads = Responsible (specs/quality), Devs = Responsible (implementation). The `doc-strategy-advisor` ownership matrix already seeds this.

---

## 2. Epic decomposition sequence (architect's path from epic to PBIs)

One epic, from "it's a PRD feature" to "build-ready, traceable tickets." No single agent does the whole thing — it's a chain with the architect signing off at defined gates. The RTM thread (`PRD → FRD → SRS → SDD → PBI → task → test`) is what makes it a *sequence*, not a pile; `/spec-check` proves nothing was dropped.

| # | Step | Owner · agent | Architect's responsibility |
|---|---|---|---|
| 1 | Epic exists as a PRD feature | PM · `prd-writer` | Sanity-check feasibility early; flag if it's an architecture-significant epic |
| 2 | Feature behaviour + edge cases | Lead/BA · `frd-writer` | — |
| 3 | Constraints / NFRs the epic must meet | **Architect · `srs-writer`** | **Own** — performance, scale, security, accessibility, interfaces |
| 4 | Architecture for the epic (HLD→LLD, components, interfaces) | **Architect · `sdd-writer`** | **Own** — the blueprint stories build against (arc42/C4) |
| 5 | Significant decisions | **Architect · `rfc-facilitator` → `adr-writer`** | **Own** — propose before building, record the why |
| 5b | *(brownfield only)* ground the epic in real code | dev · `solution-recon` | Confirm the design matches what exists; catch spec↔code drift |
| 6 | Epic → stories (PBIs) → tasks; INVEST, SPIDR splits | `backlog-manager` | **Sign off** the breakdown — the DoR technical gate (no story enters a sprint until its blueprint is peer-reviewed) |
| 7 | Sized + scheduled | `estimation-facilitator` → `sprint-planner` | Advise on risk and build order (which PBI unblocks which) |
| 8 | Built; reviewed for architecture fit | devs → `code-reviewer` (+ `security-reviewer`, `performance-engineer`, `accessibility-auditor` as the epic warrants) | Guard the DoD technical bar; review architecturally significant changes |

**It's a feedback-looped funnel, not rigid waterfall.** You don't fully spec every epic before any code — you spec *this* epic, decompose it, build, and let discoveries flow back up (an SRS target the design can't meet → revise the SRS; a missing endpoint found in recon → a backend-enabler PBI scheduled first). See the feedback loops in `BEST-PRACTICES.md`.

**The architect's two non-negotiable gates:** (4–5) the blueprint + decisions exist *before* decomposition, and (6) the architect signs off the PBI breakdown's technical feasibility before it enters a sprint. Everything else they advise on; these two they own.

> **Systems engineering note:** this covers *software* systems engineering (architecture, interfaces, NFRs, V&V via `test-plan-writer`'s IQ/OQ/PQ). True multidisciplinary SE — ICDs, hardware↔software co-design, system-of-systems integration, the full V-model — is **not** a dedicated role here; add a specialist only if you build beyond software.

## 3. Azure DevOps Boards fit check

The project's artifacts map cleanly onto Azure DevOps. Recommended setup: **Azure Boards (Agile or Scrum process) + Repos + Wiki + Test Plans + Pipelines.**

### Work-item hierarchy mapping
| Our artifact | Azure Boards work item (Agile process) | Notes |
|---|---|---|
| Epic (backlog-manager) | **Epic** | One per major feature area |
| — (optional grouping) | **Feature** | Use if epics are large; group PBIs under Features |
| User story / PBI (backlog-manager) | **User Story** (Agile) / **Product Backlog Item** (Scrum) | Story text → Description; acceptance criteria → the **Acceptance Criteria** field |
| Task under a story | **Task** | The "first task / note" from the sprint plan |
| Bug | **Bug** | PBI type "Bug" maps directly |
| Spike | **Issue** or a Task tagged `spike` | For estimation "?" items |

### Field & feature mapping
- **Story points** (estimation-facilitator) → the **Story Points** (or Effort) field. Velocity, burndown, and CFD are then **built-in Azure Analytics charts** — this directly covers the DORA/flow-metrics need (see also `engineering-metrics-template`).
- **Sprint plan** (sprint-planner) → an Azure **Iteration**; the sprint goal goes in the iteration description; **Capacity** planning is a native Boards feature.
- **Definition of Ready / Done** → Board column policies / a shared Wiki page; gate columns enforce DoR.
- **Priority / MoSCoW** → backlog **order** (stack rank) + the Priority field or a `MoSCoW` tag.
- **RTM / traceability** → Azure **work-item links**: parent-child (Epic→Story→Task) plus **"Tested By"** links to **Test Plans** test cases, and links from commits/PRs (Repos) to work items. This realizes the RTM natively.
- **Retro action items** (retrospective-facilitator) → work items tagged `retro-action`, assigned and tracked in the next iteration.
- **RAID / risk** (raid-keeper) → a custom **Risk/Issue** work-item type or a Wiki RAID page; Decisions → link to ADRs in Repos.

### Where the documents live
- **BRD/PRD/FRD/SRS/SDD/TSD/URS** → Azure **Wiki** pages (or Repos as Markdown via Docs-as-Code), each **linked from the Epic/Feature** it governs. Keep the doc as the source of truth; link work items to it.
- **ADRs / RFCs** → `docs/adr/NNNN-*.md` and `docs/rfc/NNNN-*.md` in **Repos**, reviewed in PRs (matches the docs-as-code stance).
- **Backlog** → lives natively in Boards (don't duplicate the markdown backlog once imported); use `backlog-manager` to generate the initial import, then maintain in Azure.

### Recommended flow on Azure
1. Generate docs with the agents → store in Wiki/Repos.
2. `backlog-manager` output → create Epics/Features/Stories in Boards (or bulk-import via CSV).
3. `estimation-facilitator` → fill Story Points; `sprint-planner` → assign to an Iteration with capacity.
4. Devs work the board; link commits/PRs to stories; Test Plans hold test cases (`test-plan-writer` feeds these).
5. Analytics dashboards give velocity/burndown/CFD/DORA — covering most of the metrics/reporting need natively.

### Fit verdict
**Strong fit.** Azure Boards natively absorbs the backlog, estimation, sprint, metrics, and traceability concepts — and its built-in analytics covers much of the metrics/reporting need. The agents become the **authoring/standardization layer** (generate well-formed docs, INVEST stories, sprint goals, retro structure) that feeds Azure, while Azure is the **system of record** for execution. The one thing Azure won't do for you is *write good content* — which is exactly what these agents are for.
