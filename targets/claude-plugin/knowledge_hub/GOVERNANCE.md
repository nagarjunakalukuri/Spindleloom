# Spindleloom Governance

| Field | Value |
|---|---|
| Owner | Spindleloom (toolkit maintainer) |
| Status | Active |
| Standard version | 1.0 (Part I) |
| Merged | 2026-07-10 from STANDARD.md + STORY-CRAFT.md + TEAM-ROLES-AND-AZURE-DEVOPS.md |

One file, three governing standards. Cite sections as `GOVERNANCE.md Part I §N` (layout standard),
`Part II §N` (story craft), `Part III §N` (team + Azure DevOps). Section numbering inside each
part is unchanged from the source documents, so any older citation of the form `STANDARD.md §N`
maps 1:1 to `Part I §N`, `STORY-CRAFT.md §N` to `Part II §N`, and TEAM-ROLES sections to `Part III`.
The readable single-page view is [`governance-handbook.html`](governance-handbook.html) (generated
from this file -- edit here, never there).

---

# Part I — The Standard

| Field | Value |
|---|---|
| Standard version | 1.0 |
| Status | Active |
| Owner | Spindleloom (toolkit maintainer) |
| Last updated | 2026-06-20 |

> **This is the standard, not a default.** Spindleloom defines **one** project-agnostic way to lay out, name, and version SDLC artifacts. Every project that adopts Spindleloom targets this shape: greenfield projects **scaffold** it; existing projects **convert** to it (`scaffold.py migrate`). The layout is not a menu — where a project genuinely cannot use a canonical path, it declares the deviation in `.spindleloom/config.json` (the sanctioned exception, §8), never by improvising a new tree. Nothing here is specific to any product, domain, or tool.
>
> **This repository is exempt.** Spindleloom's own source repo *ships* the standard — it is the toolkit distribution, not a consuming project. The standard governs the repos that **adopt** Spindleloom.

## 1. Two layers of knowledge

Knowledge is owned by exactly one party — never both, never duplicated.

| Layer | What | Lives in | Edited by |
|---|---|---|---|
| **Toolkit knowledge** (global) | The standard, conventions, requirement-quality rules, ceremony, and the agents / skills / commands / templates themselves | The Spindleloom **bundle / plugin** (referenced, updated centrally) | The toolkit maintainer — **never** the adopting team |
| **Project knowledge** | The artifacts a team produces — product docs, specs, RTM, ADRs, backlog, sprint docs | The **adopter's repo** (`docs/` + `.spindleloom/`) + the work tracker | The adopting team |

**The rule that keeps them clean:** the toolkit ships the *how*; the project holds the *what*. Toolkit knowledge is **never copied into a project's `docs/`** — it is referenced through the installed bundle and updates centrally. A project never stores its own artifacts inside the toolkit.

## 2. Invariant vs. variable

The standard is a set of **invariant rules** plus one chosen **profile** that varies only *which documents are populated* — never the tree shape or the names.

**Invariant — every profile, always:**
- the `docs/` (visible deliverables) + `.spindleloom/` (hidden machinery) split;
- the four cadence planes (§4);
- the naming + traceability rules (§5);
- the metadata header on every durable / living document (§6);
- one RTM per initiative; one initiative per repo root.

**Variable — the profile** (declared as `profile` in config):

| Profile | Populates | For |
|---|---|---|
| `lean` (flat) | `prd.md` + `RTM.md`; funnel/specs may sit flat at the docs root | small / solo, fast-moving work |
| `mid` (default) | `prd` + per-feature `frd`, `sdd` | most teams |
| `enterprise` | full funnel `mrd brd prd` + per-feature `srs sdd` + `constitution` | larger / regulated programs |

A flat or lean layout is a **sanctioned profile**, not a violation.

The funnel (MRD→PRD) is durable and cross-feature (`docs/product/`); per-feature work stays **together** in `docs/specs/<feature>/`. Reserve kind-folders only for the append-only logs (`adr/`, `rfc/`). Don't scatter one feature across `mrd/`, `prd/`, `srs/` folders.

## 3. The canonical tree

```
repo/
├── docs/                         # VISIBLE — project deliverables (project knowledge)
│   ├── constitution.md           #   durable law (enterprise profile)
│   ├── product/                  #   DURABLE plane — the cross-feature funnel
│   │   └── mrd.md  brd.md  prd.md
│   ├── specs/<feature>/          #   LIVING plane — per-feature work
│   │   └── frd.md  srs.md  sdd.md  tsd.md  recon.md
│   ├── sprints/<sprint>/         #   CYCLIC plane — one fresh set per sprint
│   │   └── plan.md  retro.md
│   ├── adr/  rfc/                #   LIVING — append-only decision logs (one global ADR sequence)
│   └── RTM.md                    #   LIVING — the one traceability backbone (one per initiative root)
└── .spindleloom/                  # HIDDEN — tool machinery (project knowledge, generated)
    ├── config.json               #   profile, standard_version, sanctioned path deviations, approvals map
    ├── .gitignore                #   the committed-vs-local split below (written by scaffold)
    ├── artifacts.json            #   generated catalog (the registry) — COMMITTED, regenerate never hand-edit
    ├── ARTIFACTS.md              #   human-readable catalog — COMMITTED, generated
    ├── velocity.json             #   durable capacity baseline the planner reads (see §4) — COMMITTED
    ├── baselines/<tag>.json      #   SNAPSHOT plane — frozen per sprint / release — COMMITTED
    ├── verifications/<PBI>.md    #   change-verifier PASS/FAIL evidence, one per PBI — COMMITTED
    ├── signoffs/[<release-id>/]<gate>.md  # release gate tokens (qa, security, …) — COMMITTED
    ├── approvals/<feature>/<phase>.md     # phase-boundary acceptance tokens (§9) — COMMITTED
    ├── runs/<run-id>.json (+.md) #   one run-orchestrator ledger PER RUN — COMMITTED
    ├── context-log.jsonl         #   append-only handoff-context log — COMMITTED (git-mergeable)
    ├── context.db                #   LOCAL-ONLY SQLite index of the log (gitignored; rebuild:
    │                             #   `sloom context . --import`)
    └── chroma/                   #   LOCAL-ONLY semantic vectors (gitignored, optional)
```

## 4. The four cadence planes

Project knowledge is organized by how often it changes, so recurring work never pollutes durable knowledge.

| Plane | What | Cadence | Home |
|---|---|---|---|
| **Durable** | constitution, MRD, BRD, PRD, roadmap, velocity baseline | set once, rarely changes | `docs/product/` (+ `.spindleloom/velocity.json`) |
| **Living** | FRD, SRS, SDD, TSD, RTM, ADR/RFC logs, recon findings, backlog | edited continuously in place | `docs/specs/<feature>/`, `docs/RTM.md`, `docs/adr/` |
| **Cyclic** | sprint plan, retro — a fresh set **each sprint** | new instance per sprint | `docs/sprints/<sprint>/` |
| **Snapshot** | frozen baselines | immutable, per sprint / release | `.spindleloom/baselines/<tag>` |

- **Recon findings** live with the feature they de-risk — `docs/specs/<feature>/recon.md` — and are cited by the PBIs/specs they inform.
- **Recurring sprint docs** get their own cyclic home so they never mix with durable knowledge; at sprint close they freeze to a baseline.
- The **durable** part of planning (roadmap, velocity/capacity baseline) stays in the durable plane so each new sprint reads from a stable source.

## 5. Naming & traceability

- **Req-IDs:** `<DOC>-<AREA>-<NUM>` (e.g. `FRD-AUTH-012`, `SR-PERF-004`, `PBI-CHECKOUT-007`). **Immutable once assigned.**
- **One living RTM per initiative**, threading business goal → story → requirement → design → test — proving coverage and showing blast radius. **One initiative per repo root** (a repo hosting multiple initiatives is out of scope for Standard v1).
- **ADRs use one global numeric sequence** going forward. Because IDs are immutable, a pre-existing collision discovered during conversion is resolved by **recorded supersession** (the superseded ADR records the survivor) — **never by silently renumbering** an already-assigned ID.

## 6. Metadata (so docs are machine-readable)

Every durable / living document carries a metadata header so the registry can catalog it — `Owner`, `Status`, `Version`, `Last updated`. The canonical form is a Field/Value table just under the H1; the bold-list form (`- **Status:** Accepted`) and YAML frontmatter are also parsed. Transient / operational docs (PR notes, standups) are exempt — keep them lean (anti documentation-fatigue).

Worked example (canonical Field/Value form):

```markdown
# PRD: <Feature>

| Field | Value |
|---|---|
| Owner | <role / name> |
| Status | Draft · Reviewed · Approved · Baselined · Superseded |
| Version | <v1.2> |
| Last updated | <YYYY-MM-DD> |
```

## 7. Backlog — system of record

When a work tracker (Azure Boards / Jira) is connected, **the tracker is the system of record** for PBIs / backlog / bugs — status, workflow, and capacity live on the item. `backlog.md` is the **source / staging artifact** the team authors and syncs to the tracker; it is the system of record only until a tracker is wired. Never maintain the same item's status in two places.

## 8. The sanctioned exception

The only legitimate way to deviate from the canonical paths is `.spindleloom/config.json`. Every knob defaults to the canonical tree, so an **absent config means "the standard."**

```json
{
  "standard_version": "1.0",
  "profile": "mid",
  "docs_root": "docs",
  "product_dir": "product",
  "specs_dir": "specs",
  "adr_dir": "adr",
  "rfc_dir": "rfc",
  "sprints_dir": "sprints",
  "baselines_dir": "baselines",
  "rtm_file": "RTM.md"
}
```

A deviation is **declared here, reviewed, and version-pinned** — never improvised per-folder. `standard_version` records the edition the project conforms to; `profile` selects which documents the project populates (§2).

## 9. Concurrency & ownership — multiple teammates, one repo

The resolution model is **branch = local, `main` = global, PR merge = promotion**: a role's artifact is theirs alone on their branch; it becomes something downstream roles may depend on only when the PR merges — and the merge is where the CI gate (`templates/ci/sloom-gate.yml`, written by scaffold) catches collisions *before* they land in shared state. No locks, no central allocator.

Every piece of shared mutable state has one owner, one namespace key, and one enforcing gate:

| Resource | Owner role | Namespace key | Merge strategy | Enforcing gate |
|---|---|---|---|---|
| Req-ID / PBI-ID | whoever authors the requirement | `<DOC>-<AREA>-<NUM>` | git text merge | **DUP-REQID** check (`validate_reqs` / `sloom check`) |
| `docs/RTM.md` | the feature's spec owner | one per initiative | git text merge — append rows, don't reflow the table | `build_rtm --check` |
| `verifications/<PBI>.md` | change-verifier | PBI-ID | disjoint by construction | `validate_gates` |
| `signoffs/[<release-id>/]<gate>.md` | the 6 gate owners | release-id + gate | disjoint once namespaced | `validate_gates --release [--release-id]` |
| `approvals/<feature>/<phase>.md` | the phase's approver (matrix below) | feature + phase | disjoint by construction | `validate_gates --accepted` + `sloom run advance` |
| `runs/<run-id>.json` | run-orchestrator | run-id | one file per run | structural (never shared) |
| `context-log.jsonl` | every agent via `save_context` | append-only | git text merge (append-at-EOF) | `sloom context . --import` after pull |
| `context.db`, `chroma/` | local machine | — | **never committed** — rebuilt from the log | gitignored by scaffold |
| `artifacts.json` / `ARTIFACTS.md` | generated | — | regenerate before commit, never hand-edit | `registry --check` |
| PBI claiming | the assignee | tracker `AssignedTo` | tracker is system of record (§7) | tracker's own locking |
| PBI-ID ↔ tracker-ID map (RTM Azure column) | backlog-manager — sole pusher, **from merged `main` only** | PBI-ID | write back + commit immediately after push | idempotent push (skips mapped) + `emit_backlog check` |

**The phase acceptance graph.** Agents (and teammates) parallelize freely *within* a phase; crossing a boundary requires the accountable role's acceptance token — `"can I start?" is a file check, not a meeting`. `discovery → requirements → design → planning → build → test → review → release → operate`, with `process` cross-cutting (gates nothing). Build→release boundaries are already mechanical (verifications + sign-offs); the four upstream boundaries take an acceptance token, written via `sloom approve <phase> --feature <slug> --role <role> --by "<name>"`:

| Phase boundary | Output accepted | Default approver (override: config `"approvals"`) |
|---|---|---|
| discovery → requirements | doc-strategy tier decision, MRD | sponsor / product owner |
| requirements → design | BRD/PRD/FRD/SRS/URS set (per tier) | product owner |
| design → planning | SDD/TSD, API contract, data model, ADRs | architect / tech lead |
| planning → build | backlog, estimates, sprint plan | product owner + team lead |
| build → test → review → release | verifications + sign-off tokens | *(already mechanical)* |
| operate | runbooks / SLOs in place | SRE (advisory) |

Local token files are canonical (git-tracked, PR-reviewable, offline); `sloom approve --notify-tracker` optionally mirrors an acceptance as a **comment** on the mapped work items — comment only, because item *state* stays owned by the tracker's own workflow (§7). Because these gates are files, an autonomous loop and a human teammate hit the **same** gates — this is what makes distributed runs and loop engineering safe: `sloom run status|advance <run-id>` lets a teammate check/advance a run without an LLM, and it refuses the same things the orchestrator refuses. Acceptance is enforced at **run time** — `sloom run advance` and the orchestrator refuse a boundary-crossing step whose token isn't `ACCEPTED`, and anyone can check with `validate_gates.py --accepted <phase> --feature <slug>`. The default `sloom check` battery does **not** run `--accepted`, so the CI gate (`sloom-gate.yml`) catches collisions/traceability/unevidenced gates but not phase acceptance — a green PR is not by itself proof a phase was accepted. Teams that want merge-time enforcement add the optional `--accepted` step shown in `templates/ci/sloom-gate.yml`. 

**Open flags & re-dispatch.** When a role finds an upstream gap it cannot fix itself (a missing story, an unratified fact, a spec↔code mismatch), it leaves a machine-readable `FLAG(<owner-agent>): <what>` marker in its artifact — not only prose. `sloom flags <root>` lists every open flag grouped by owner: the re-work queue the run-orchestrator (or a human) drains by re-dispatching that agent, and `sloom flags --strict` gates on it. This closes the run2 gap where flags accumulated as annotations with no loop-back.

## 10. Adoption

- **Greenfield** — `python scaffold.py <repo> --profile <p>` (or `/spec-new`) lays down the tree.
- **Brownfield** — `python scaffold.py <repo> migrate` **converts** an existing repo to the standard: it relocates artifacts into the canonical tree and rewrites cross-links deterministically (dry-run by default). **Do not hand-move files** — the converter is the supported path; hand-moving is exactly what causes layout thrash.

## 11. Conformance

A repo is conformant when it matches the standard for its declared `profile` / `standard_version`. Enforced by:

- **`validate_reqs.py`** — Req-ID format, RTM coverage, ADR-reference integrity, **duplicate-ID and multiple-ADR-directory detection**, and a **layout / version conformance check**;
- **`build_artifact_registry.py --check`** — fails CI on any conformance violation.

Conformance is also queryable live via the `sloom` MCP server.

## 12. The golden rule — one system of record per kind

**One system of record per kind of thing. Never duplicate; link by RTM ID.** If you're updating the same fact in two places, the architecture is wrong.

| Artifact kind | System of record | Why |
|---|---|---|
| Durable docs (MRD, BRD, PRD, SRS, SDD, TSD, URS) | **repo `docs/`** (or a wiki) | searchable, reviewed in PRs, AI-readable |
| ADRs, RFCs, per-feature specs | **repo** (`docs/adr/`, `docs/rfc/`, `docs/specs/`) | versioned with the code they govern |
| PBIs / backlog / bugs | **work tracker** (Azure Boards / Jira) when connected; else `backlog.md` | status/workflow/capacity live on the item; `backlog.md` is the staging artifact synced to it (§7) |
| Solution-recon findings | **repo** (`docs/specs/<feature>/recon.md`) | ground-truth that de-risks a feature; lives with it |
| Sprint plans / retros | **repo** (`docs/sprints/<sprint>/`) | per-sprint (cyclic); frozen to a baseline at close |
| Code, tests, pipelines | **repo** | obvious |
| Generated catalog, config, baselines | **`.spindleloom/`** | tool machinery, derived — never hand-edited |

### Directionality & drift (tracker-backed kinds)

For kinds whose system of record is the **work tracker** (PBIs / backlog / bugs), the rule also has a **direction** — otherwise the repo doc and the tracker silently become two sources of truth:

- The repo doc (`backlog.md`) is a **one-way generation source** — it seeds the tracker once; thereafter the **tracker is authoritative** for status and acceptance criteria. Don't re-maintain those in the doc (that *is* the duplication the golden rule forbids).
- **Write tracker IDs back into `RTM.md`** (the Azure column) so traceability spans the boundary: source → PBI → work-item ID. An empty Azure column is a drift gap, not a finished load.
- **Tasks live only in the tracker** (below-story decomposition); the docs stop at PBI.
- On disagreement, the **tracker wins** — fix drift by updating the RTM / a doc note, never by syncing the same fact in two places.

The `backlog-manager`'s **Tracker sync contract** gives the full field map (which doc field maps to which work-item field — the seam where "everything dumped into Description" defects start).

## 13. Versioning, baselines & lifecycle

Documents are living, but changes are deliberate:

- **Status** moves Draft → Reviewed → Approved → Baselined → Superseded (in the metadata header).
- **Baseline** at decision points (sprint close / phase gate): `python build_artifact_registry.py <repo> --baseline <tag>` freezes every artifact's id/status/version/updated to `.spindleloom/baselines/<tag>.json`. Tag with the sprint name to baseline **per sprint** — diff baselines to see what moved between sprints or releases.
- **Version explicitly** (v1.0, v1.1) and keep a change log of what changed and why. IDs never change.
- Regulated contexts (FDA 21 CFR 820.30) add a formal change board; the URS and downstream fall under it.

## 14. How to find anything (retrieval)

Four complementary paths — you should never have to *know where a doc lives*:

1. **By traceability** — follow an `<DOC>-<AREA>-<NUM>` ID through `RTM.md` (up to its source, down to its tests). `/spec-check`.
2. **By catalog** — `.spindleloom/ARTIFACTS.md` (or `artifacts.json`): every artifact with its id, kind, path, owner, status, version, last-updated. Generated by `build_artifact_registry.py`.
3. **Live, from any tool** — the `sloom` MCP server (short for Spindleloom): `find_artifact("PRD")`, `list_artifacts(status="draft")`, `trace_requirement("FRD-TRK-001")`, `rtm_coverage()`.
4. **By navigation** — the project wiki (`wiki-curator`) and the `personas/` field handbook for role-by-role entry points.

## 15. The tools (all stdlib-only except the MCP server)

| Tool | Role |
|---|---|
| `hooks/scaffold.py` | lay down the `docs/` + `.spindleloom/` layout (tier-aware, idempotent) |
| `hooks/validate_reqs.py` | RTM coverage / Req-ID / ADR-ref gate (CI + hook) |
| `hooks/build_artifact_registry.py` | generate the catalog; `--baseline <tag>` freezes a snapshot |
| `hooks/emit_backlog.py` | backlog.md → work-tracker work items (the sync contract of §12, automated): parse · field-map (AC → its own field) · dry-run plan · ID write-back; pluggable tracker adapter |
| `hooks/mcp_server.py` | live traceability + artifact queries over MCP (launched via `uv run`) |
| `hooks/rtm_core.py` | the shared stdlib parser behind all of the above |

See `BEST-PRACTICES.md` for the requirement-quality standard and feedback loops, and `hooks/HOOKS.md` for wiring these into CI.

---

# Part II — Story Craft

> *The card is not the story — write the conversation it starts.* The Spindleloom reference for agile story craft, grounded in primary sources (Cohn, Wake, Lawrence & Green / Humanizing Work, Agile Alliance, Scrum.org). `backlog-manager`, `frd-writer`, `test-plan-writer`, and the DoR/DoD + epic templates all reference this — don't restate it per item.

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Active reference |
| Last updated | 2026-06-21 |

## 1. The Connextra format (default, not dogma)

**"As a `<role>`, I want `<capability>`, so that `<benefit>`."** Originated with Rachel Davies at Connextra; popularized by Mike Cohn. The deeper definition (Ron Jeffries) is the **three Cs — Card, Conversation, Confirmation**: the template names the parts of the *card*; the three Cs say what a story *is*.

- **The "so that" clause** — understanding WHY guides HOW. Strongly recommended, not mandatory (Cohn writes it ~97% of the time). Drop it only when it genuinely adds nothing (e.g. a basic login).
- **No developer-only stories** — every story delivers value a customer can prioritize. *"All connections go through a pool"* → rewrite as *"Up to fifty users can use the app with a five-user DB license."*

## 2. INVEST — the quality gate (Bill Wake, 2003)

Run every story through this **before it enters a sprint**:

- **I**ndependent — minimize cross-story dependencies (they choke sprint planning).
- **N**egotiable — the card is a placeholder for a conversation, not a contract. If it can't change, it's a spec.
- **V**aluable — visible, prioritizable value; not engineer-only.
- **E**stimable — understood well enough to size; if not, converse or timebox a spike.
- **S**mall — 6–10 similar stories fit a sprint (see §5).
- **T**estable — if you can't write the acceptance test, it isn't ready.

## 3. Acceptance criteria

AC are the agreed pass/fail conditions for **one specific story**. They are **co-authored, never solo** — they come from a **Three Amigos** session that converges on concrete examples *before* the story enters a sprint:

- **Business:** "What problem are we solving?"
- **Development:** "How might we build it?"
- **Testing:** "What could go wrong?"

**AC ≠ DoD.** AC is the exit gate from the **story** (story-specific pass/fail). The **Definition of Done** is the exit gate from the **sprint** (team-wide, applied to every Increment). Don't conflate them.

Two forms — choose per story:

- **Gherkin / Given–When–Then** — for behaviour with user-visible examples (flows, state changes, happy *and* unhappy paths). One scenario per case.
  ```
  Scenario: Failed login locks account
  Given a user with 4 failed attempts
  When they submit wrong credentials again
  Then the account is locked
  And a reset email is sent within 30 s
  ```
- **Rule-based checklist** — for independent business rules/constraints with no single flow to narrate.
  ```
  ☐ Password must be ≥ 12 characters
  ☐ Account locks after 5 failed attempts
  ☐ Reset link expires after 15 minutes
  ☐ Rate limit: 10 attempts / IP / hour
  ```

> **Red flag:** AC that describe *implementation* ("the system shall use Redis") instead of *observable outcomes*.

## 4. Splitting — always vertical

Slice through **all layers** so each slice delivers visible value. **Horizontal splits (a "UI story" + a "DB story") are the single most common anti-pattern** — they may satisfy *Small* but fail *Independent* and *Valuable* (the DB layer alone has no customer value). Horizontal is acceptable only for a pure spike.

> **Spindleloom brownfield exception:** when a UI needs an endpoint/data that **doesn't exist yet** (platform extension), a backend enabler PBI *is* a legitimate split — `*-BE` blocks `*-FE`, schedule BE first. See `backlog-manager` + the DoR backend-readiness gate.

**The 9 patterns (Humanizing Work — Lawrence & Green):**

1. **Workflow steps** — thin path through the whole flow; if still big, slice the complex step first.
2. **Operations / CRUD** — "manage/maintain" hides Create·Read·Update·Delete; each its own story.
3. **Business-rule variations** — each decision path (tiers, tax rules, permissions) its own story.
4. **Variations in data** — split by data shape/type (one file format vs another).
5. **Data-entry methods** — bulk import / manual form / API upload as separate stories.
6. **Simple / complex** — ship the 80% simple case first; tackle the edge case separately.
7. **Major effort** — no obvious pattern; ship the highest-value thin slice, defer the rest.
8. **Defer performance** — split behaviour from speed/scale; optimize in a separate story.
9. **Break out a spike** — too uncertain to split/estimate; **timebox** an investigation, real story follows.

**SPIDR (Cohn)** — Spike · Paths · Interfaces · Data · Rules — a *parallel* catalog over the same ground (not derived from the 9; treat as independent).

**Two kinds of epic (Cohn):** **Compound** → split by CRUD verb or data boundary. **Complex / uncertain** → spike first, then write the real stories.

## 5. Right-sizing — the 6–10 rule

By the time a story reaches the **top** of the backlog, **6–10 similar stories should fit one sprint**. It scales with team size / sprint length (others cite 5–15 — a rule of thumb, not an SLA). Split **just-in-time** (1–2 sprints before the top), not months ahead — early splitting is false precision on work that will change. **Right-sizing is the prerequisite for *any* estimation technique** (points, t-shirt, #NoEstimates), not a substitute for it.

## 6. Hierarchy (tool-agnostic)

`Initiative → Theme → `**`Epic`**` → `**`Story`**` → Task`. The two stable anchors are **epic** (too big for a sprint; a placeholder, progressively decomposed) and **story** (fits a sprint, delivers visible value, has AC). Above epic = portfolio planning; below story = task decomposition (sub-day technical units, **no standalone user value**). "Feature" / "Initiative" are vendor conventions (SAFe / Jira / Azure Boards) — don't let tool vocabulary dictate architecture.

## 7. Red-flag anti-patterns — reject on sight

- Story won't fit a sprint alone → it's an epic; split it **before** it enters the backlog.
- Split by architectural layer (UI / DB) → horizontal; wrong for customer-facing work.
- Missing "so that" with no reason → you can't prioritize it against anything.
- Valued only by developers ("use a connection pool") → rewrite for visible customer benefit.
- AC describe implementation ("use Redis") → describe observable outcomes.
- Gold-plating beyond the AC → stop; negotiate scope or write a new story.
- A story you can't write a test for → fails *Testable*; don't pull it in.
- Card treated as a fixed contract → it's a placeholder; details are negotiated during development.

## Templates

In `templates/`: the user-story row (`backlog-template.md`), **`epic-template.md`**, **`task-template.md`** (lean — tasks are tracker-only, no AC of their own), the AC forms (§3), the splitting cheat sheet (§4), `definition-of-ready-done-template.md`, and the red-flag list (§7).

## Sources (primary; adversarially verified)

- Mike Cohn — *User Stories Applied* (2004) · "Why the Three-Part Template Works So Well" (Mountain Goat Software)
- Bill Wake — *INVEST in Good Stories and SMART Tasks* (xp123.com, 2003)
- Richard Lawrence & Peter Green — *The Humanizing Work Guide to Splitting User Stories*
- Agile Alliance — *Three Amigos* glossary
- Scrum.org — *Definition of Done vs Definition of Ready* (DoR was removed from the 2020 Scrum Guide — use as a team aid, not a mandated gate)

---

# Part III — Team Roles, Epic Decomposition & Azure DevOps Fit

*Three things for a team adopting this toolkit: how a concrete 10-person team maps onto the fleet (sec 1 -- now mostly superseded by the persona handbook), the architect's epic-decomposition sequence from PRD feature to build-ready PBIs (sec 2 -- the unique content here), and how the artifacts map onto Azure DevOps as the system of record (sec 3).*

---

## 1. Team of 10 — who runs what

> **The per-role operating detail now lives in the [Persona Field Handbook](personas/index.html)** -- 15 role playbooks, each with the agents that role drives, copy-ready prompts, the gates it owns, KPIs and hand-offs. This section keeps only what the handbook does not: the concrete 10-person mapping and its one structural gap.

Team: **1 Principal Director, 1 Project Manager, 1 Architect, 2 Leads, 5 Software Developers.**

One important note up front: there is **no dedicated Product Owner / Product Manager** in this team. Someone must own the PRD, backlog priority, and acceptance -- by default the **Project Manager wears the PO hat**, with the **Principal Director** setting business priorities. Flag this as the single biggest role gap to resolve before kickoff.

Map the 9 onto personas: Principal Director -> *Sponsor*; Project Manager -> *Product Owner* + *Delivery Lead*; Architect -> *Architect*; Leads -> *Developer* (reviewer half) + parts of *QA*; Developers -> *Developer*. Unstaffed personas (UX, Security, SRE, Docs, AI/ML, Compliance) are hats the same 9 wear when the work demands it -- the agents carry the method so the hat is cheap to put on.

### How the 9 complete a project end-to-end
1. **Inception** — Principal Director + PM run `mrd-writer`/`brd-writer`; PM runs `doc-strategy-advisor` to pick the doc set for a 10-person (Mid-tier) team: **PRD + FRD-in-tickets + SDD**, with TSD for the build.
2. **Definition** — PM (PO hat) writes the PRD; Architect + Leads produce SRS/SDD; Architect logs ADRs and sets the constitution/tech-radar.
3. **Breakdown** — PM/Leads run `backlog-manager` (PRD/FRD → epics → PBIs); whole team runs `estimation-facilitator` (Planning Poker).
4. **Delivery loop** — `sprint-planner` each sprint (goal + capacity-fit backlog); devs build; daily standup; Architect/Leads review (`code-reviewer`); `retrospective-facilitator` at sprint end; repeat.
5. **Governance/Release** — PM runs `raid-keeper` + `status-reporter`; Leads run `test-plan-writer`/`qa-tester`; `release-manager` handles go/no-go with the Director.

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
| Spike | **Task** (what `emit_backlog.py` maps it to today) | For estimation "?" items; tag it `spike` by hand if you want the distinction |

### Field & feature mapping
- **Story points** (estimation-facilitator) → the **Story Points** (or Effort) field. Velocity, burndown, and CFD are then **built-in Azure Analytics charts** — this directly covers the DORA/flow-metrics need (see also `engineering-metrics-template`).
- **Sprint plan** (sprint-planner) → an Azure **Iteration**; the sprint goal goes in the iteration description; **Capacity** planning is a native Boards feature.
- **Definition of Ready / Done** → Board column policies / a shared Wiki page; gate columns enforce DoR.
- **Priority / MoSCoW** → backlog **order** (stack rank) + the Priority field or a `MoSCoW` tag.
- **RTM / traceability** → Azure **work-item links**: parent-child (Epic→Story→Task) plus **"Tested By"** links to **Test Plans** test cases, and links from commits/PRs (Repos) to work items. This realizes the RTM natively.
- **Retro action items** (retrospective-facilitator) → work items tagged `retro-action`, assigned and tracked in the next iteration.
- **RAID / risk** (raid-keeper) → a custom **Risk/Issue** work-item type or a Wiki RAID page; Decisions → link to ADRs in Repos.

### Where the documents live
Layout is owned by **Part I** above -- this section only adds the Azure angle:
- **Docs (BRD/PRD/FRD/SRS/SDD/TSD/URS)** stay in **Repos** per the standard tree (`docs/`); mirror or link them from the Wiki, each **linked from the Epic/Feature** it governs. The repo file is the source of truth.
- **ADRs / RFCs** → `docs/adr/NNNN-*.md` and `docs/rfc/NNNN-*.md` in **Repos**, reviewed in PRs (matches the docs-as-code stance).
- **Backlog** → the tracker owns PBI **status** once connected (Part I sec 7); `docs/backlog.md` is the staging artifact you author, then push with `sloom backlog` -- don't hand-maintain both.

### Recommended flow on Azure
1. Generate docs with the agents → store in Repos (+ Wiki links).
2. `backlog-manager` output → push to Boards with **`sloom backlog`** (`hooks/emit_backlog.py` → `hooks/azure_boards_adapter.py`): creates Epics/Stories/Tasks/Bugs via JSON-Patch, puts acceptance criteria in the native **Acceptance Criteria** field, sets Priority/StoryPoints/Tags, links Epic parents (`--link-epics`), and writes the created IDs back into the RTM. (`hooks/jira_adapter.py` is the same flow for Jira; CSV import is the fallback when you have no PAT.)
3. `estimation-facilitator` → fill Story Points; `sprint-planner` → assign to an Iteration with capacity (iteration/capacity assignment is manual -- the adapter deliberately doesn't own it).
4. Devs work the board; link commits/PRs to stories; Test Plans hold test cases (`test-plan-writer` feeds these).
5. Analytics dashboards give velocity/burndown/CFD/DORA — covering most of the metrics/reporting need natively.

### Fit verdict
**Strong fit.** Azure Boards natively absorbs the backlog, estimation, sprint, metrics, and traceability concepts — and its built-in analytics covers much of the metrics/reporting need. The agents become the **authoring/standardization layer** (generate well-formed docs, INVEST stories, sprint goals, retro structure) that feeds Azure, while Azure is the **system of record** for execution. The one thing Azure won't do for you is *write good content* — which is exactly what these agents are for.
