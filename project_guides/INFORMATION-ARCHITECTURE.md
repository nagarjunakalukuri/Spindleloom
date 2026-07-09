# Information Architecture — where artifacts live, how they're organized, found, and versioned

The **detailed reference** for the layout mandated by [`STANDARD.md`](STANDARD.md): where each thing is stored, how the tree is laid out, how you retrieve anything, and how versions/baselines work. `STANDARD.md` is the mandate (what's required, and why); this is the how. Consolidates what was spread across `BEST-PRACTICES.md` and `TEAM-ROLES-AND-AZURE-DEVOPS.md`. Read this once; the tooling enforces it. When the two appear to differ, `STANDARD.md` governs.

## The golden rule

**One system of record per kind of thing. Never duplicate; link by RTM ID.** If you're updating the same fact in two places, the architecture is wrong.

| Artifact kind | System of record | Why |
|---|---|---|
| Durable docs (MRD, BRD, PRD, SRS, SDD, TSD, URS) | **repo `docs/`** (or a wiki) | searchable, reviewed in PRs, AI-readable |
| ADRs, RFCs, per-feature specs | **repo** (`docs/adr/`, `docs/rfc/`, `docs/specs/`) | versioned with the code they govern |
| PBIs / backlog / bugs | **work tracker** (Azure Boards / Jira) when connected; else `backlog.md` | status/workflow/capacity live on the item; `backlog.md` is the staging artifact synced to it (STANDARD.md §7) |
| Solution-recon findings | **repo** (`docs/specs/<feature>/recon.md`) | ground-truth that de-risks a feature; lives with it |
| Sprint plans / retros | **repo** (`docs/sprints/<sprint>/`) | per-sprint (cyclic); frozen to a baseline at close |
| Code, tests, pipelines | **repo** | obvious |
| Generated catalog, config, baselines | **`.spindleloom/`** | tool machinery, derived — never hand-edited |

### Directionality & drift (tracker-backed kinds)

The golden rule names *where* each kind lives; for kinds whose system of record is the **work tracker** (PBIs / backlog / bugs), it also has a **direction** — otherwise the repo doc and the tracker silently become two sources of truth:

- The repo doc (`backlog.md`) is a **one-way generation source** — it seeds the tracker once; thereafter the **tracker is authoritative** for status and acceptance criteria. Don't re-maintain those in the doc (that *is* the duplication the golden rule forbids).
- **Write tracker IDs back into `RTM.md`** (the Azure column) so traceability spans the boundary: source → PBI → work-item ID. An empty Azure column is a drift gap, not a finished load.
- **Tasks live only in the tracker** (below-story decomposition); the docs stop at PBI.
- On disagreement, the **tracker wins** — fix drift by updating the RTM / a doc note, never by syncing the same fact in two places.

The `backlog-manager`'s **Tracker sync contract** gives the full field map (which doc field maps to which work-item field — the seam where "everything dumped into Description" defects start).

## Brand the machinery, name the deliverables for what they are

The durable docs are your product's knowledge — they outlive any tool, so they live in a **visible, content-named** tree (`docs/`), never a tool-branded or hidden folder. The tool's own state is disposable, so it lives in a **hidden, branded** folder (`.spindleloom/`) — the analog of `.git/` or Spec Kit's `.specify/`.

```
repo/
├── docs/                       # VISIBLE — the deliverables (human-read, PR-reviewed, wiki-publishable)
│   ├── constitution.md         #   durable law (enterprise profile)
│   ├── product/                #   DURABLE — the funnel, cross-feature
│   │   └── mrd.md  brd.md  prd.md
│   ├── specs/<feature>/         #   LIVING — per-feature work
│   │   └── frd.md  srs.md  sdd.md  tsd.md  recon.md
│   ├── sprints/<sprint>/        #   CYCLIC — one fresh set per sprint
│   │   └── plan.md  retro.md
│   ├── adr/  rfc/               #   LIVING — append-only decision logs (NNNN-*.md)
│   └── RTM.md                   #   the traceability backbone (one per initiative root)
└── .spindleloom/                # HIDDEN — tool machinery (the .git / .specify analog)
    ├── config.json             #   profile, standard_version + sanctioned path knobs (STANDARD.md §8)
    ├── artifacts.json          #   generated catalog (the registry)
    ├── ARTIFACTS.md            #   human-readable catalog
    ├── velocity.json           #   durable capacity baseline the sprint-planner reads
    └── baselines/<tag>.json    #   SNAPSHOT — frozen version/status snapshots
```

Scaffold it: `python scaffold.py <repo> --profile mid --feature <name>` (or `/spec-new`); convert an existing repo with `python scaffold.py <repo> migrate`. The layout is config-driven — every path knob defaults to the Standard tree and is overridable in `.spindleloom/config.json`; everything (scaffold, validator, registry, MCP) resolves through it. See [`STANDARD.md`](STANDARD.md) §8.

## How it's organized — the profiles

The tree shape above is fixed (the Standard); a project's **profile** selects only *which documents are populated* (see [`STANDARD.md`](STANDARD.md) §2):

- **`lean` (flat)** — `prd.md` + `RTM.md`; fastest, smallest. Suits solo / early work.
- **`mid` (default)** — `prd` + per-feature `frd`, `sdd`. Suits most teams.
- **`enterprise`** — full funnel `mrd brd prd` + per-feature `srs sdd` + `constitution`. Suits altitude discipline and larger/regulated programs.

The funnel (MRD→PRD) is durable and cross-feature (`docs/product/`); per-feature work stays **together** in `docs/specs/<feature>/`; one `RTM.md` per initiative is the record. Reserve kind-folders only for the append-only logs (`adr/`, `rfc/`). Don't scatter one feature across `mrd/`, `prd/`, `srs/` folders.

## The four cadence planes

Project knowledge is organized by **how often it changes**, so recurring work never pollutes durable knowledge:

| Plane | What | Cadence | Home |
|---|---|---|---|
| **Durable** | constitution, MRD, BRD, PRD, roadmap, velocity baseline | set once, rarely changes | `docs/product/` (+ `.spindleloom/velocity.json`) |
| **Living** | FRD, SRS, SDD, TSD, RTM, ADR/RFC logs, recon, backlog | edited continuously in place | `docs/specs/<feature>/`, `docs/RTM.md`, `docs/adr/` |
| **Cyclic** | sprint plan, retro — a fresh set each sprint | new instance per sprint | `docs/sprints/<sprint>/` |
| **Snapshot** | frozen baselines | immutable, per sprint / release | `.spindleloom/baselines/<tag>` |

- **Solution-recon findings** live with the feature they de-risk — `docs/specs/<feature>/recon.md` — cited by the PBIs/specs they inform (not a floating doc, not a PBI).
- **Recurring sprint docs** get their own cyclic home; at sprint close they freeze to a baseline (below), so the global tree stays clean.
- The **durable** slice of planning (roadmap, the velocity/capacity baseline the sprint-planner reads from `.spindleloom/velocity.json`) stays in the durable plane so each sprint starts from a stable source.

## Naming & traceability

- **Req-IDs:** `<DOC>-<AREA>-<NUM>` (e.g. `FRD-AUTH-012`, `SR-PERF-004`, `PBI-CHECKOUT-007`). Immutable once assigned.
- **One living RTM** threads business goal → story → requirement → design → test. Link both directions so you can prove coverage and see blast radius. `validate_reqs.py` fails CI if a requirement isn't traced.

## Metadata convention (so docs are machine-readable)

Every **durable document** carries a metadata header so the registry can catalog it. Canonical form — a Field/Value table just under the H1:

```markdown
# PRD: <Feature>

| Field | Value |
|---|---|
| Owner | <role / name> |
| Status | Draft · Reviewed · Approved · Baselined · Superseded |
| Version | <v1.2> |
| Last updated | <YYYY-MM-DD> |
```

The registry also reads the **bold-list** form ADRs use (`- **Status:** Accepted`) and YAML **frontmatter** — pick whichever fits the doc; all three are parsed. Transient/operational docs (PR, retro, estimation) don't need it — keep them lean (anti documentation-fatigue).

## Versioning, baselines & lifecycle

Documents are living, but changes are deliberate:

- **Status** moves Draft → Reviewed → Approved → Baselined → Superseded (in the metadata header).
- **Baseline** at decision points (sprint close / phase gate): `python build_artifact_registry.py <repo> --baseline <tag>` freezes every artifact's id/status/version/updated to `.spindleloom/baselines/<tag>.json`. Tag with the sprint name to baseline **per sprint** — diff baselines to see what moved between sprints or releases.
- **Version explicitly** (v1.0, v1.1) and keep a change log of what changed and why. IDs never change.
- Regulated contexts (FDA 21 CFR 820.30) add a formal change board; the URS and downstream fall under it.

## How to find anything (retrieval)

Four complementary paths — you should never have to *know where a doc lives*:

1. **By traceability** — follow an `<DOC>-<AREA>-<NUM>` ID through `RTM.md` (up to its source, down to its tests). `/spec-check`.
2. **By catalog** — `.spindleloom/ARTIFACTS.md` (or `artifacts.json`): every artifact with its id, kind, path, owner, status, version, last-updated. Generated by `build_artifact_registry.py`.
3. **Live, from any tool** — the `sloom` MCP server (short for Spindleloom): `find_artifact("PRD")`, `list_artifacts(status="draft")`, `trace_requirement("FRD-TRK-001")`, `rtm_coverage()`.
4. **By navigation** — the project wiki (`wiki-curator`) and `how-to-use.html` for role-by-role entry points.

## The tools (all stdlib-only except the MCP server)

| Tool | Role |
|---|---|
| `hooks/scaffold.py` | lay down the `docs/` + `.spindleloom/` layout (tier-aware, idempotent) |
| `hooks/validate_reqs.py` | RTM coverage / Req-ID / ADR-ref gate (CI + hook) |
| `hooks/build_artifact_registry.py` | generate the catalog; `--baseline <tag>` freezes a snapshot |
| `hooks/emit_backlog.py` | backlog.md → work-tracker work items (the sync contract, automated): parse · field-map (AC → its own field) · dry-run plan · ID write-back; pluggable tracker adapter |
| `hooks/mcp_server.py` | live traceability + artifact queries over MCP (launched via `uv run`) |
| `hooks/rtm_core.py` | the shared stdlib parser behind all of the above |

See `BEST-PRACTICES.md` for the requirement-quality standard and feedback loops, and `hooks/HOOKS.md` for wiring these into CI.
