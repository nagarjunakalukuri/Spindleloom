# The Spindleloom Standard

| Field | Value |
|---|---|
| Standard version | 1.0 |
| Status | Active |
| Owner | Spindleloom (toolkit maintainer) |
| Last updated | 2026-06-20 |
| Detailed reference | [`INFORMATION-ARCHITECTURE.md`](INFORMATION-ARCHITECTURE.md) |

> **This is the standard, not a default.** Spindleloom defines **one** project-agnostic way to lay out, name, and version SDLC artifacts. Every project that adopts Spindleloom targets this shape: greenfield projects **scaffold** it; existing projects **convert** to it (`scaffold.py migrate`). The layout is not a menu — where a project genuinely cannot use a canonical path, it declares the deviation in `.shipwright/config.json` (the sanctioned exception, §8), never by improvising a new tree. Nothing here is specific to any product, domain, or tool.
>
> **This repository is exempt.** Spindleloom's own source repo *ships* the standard — it is the toolkit distribution, not a consuming project. The standard governs the repos that **adopt** Spindleloom.

## 1. Two layers of knowledge

Knowledge is owned by exactly one party — never both, never duplicated.

| Layer | What | Lives in | Edited by |
|---|---|---|---|
| **Toolkit knowledge** (global) | The standard, conventions, requirement-quality rules, ceremony, and the agents / skills / commands / templates themselves | The Spindleloom **bundle / plugin** (referenced, updated centrally) | The toolkit maintainer — **never** the adopting team |
| **Project knowledge** | The artifacts a team produces — product docs, specs, RTM, ADRs, backlog, sprint docs | The **adopter's repo** (`docs/` + `.shipwright/`) + the work tracker | The adopting team |

**The rule that keeps them clean:** the toolkit ships the *how*; the project holds the *what*. Toolkit knowledge is **never copied into a project's `docs/`** — it is referenced through the installed bundle and updates centrally. A project never stores its own artifacts inside the toolkit.

## 2. Invariant vs. variable

The standard is a set of **invariant rules** plus one chosen **profile** that varies only *which documents are populated* — never the tree shape or the names.

**Invariant — every profile, always:**
- the `docs/` (visible deliverables) + `.shipwright/` (hidden machinery) split;
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
└── .shipwright/                  # HIDDEN — tool machinery (project knowledge, generated)
    ├── config.json               #   profile, standard_version, and any sanctioned path deviations
    ├── artifacts.json            #   generated catalog (the registry)
    ├── ARTIFACTS.md              #   human-readable catalog
    ├── velocity.json             #   durable capacity baseline the planner reads (see §4)
    └── baselines/<tag>.json      #   SNAPSHOT plane — frozen per sprint / release
```

## 4. The four cadence planes

Project knowledge is organized by how often it changes, so recurring work never pollutes durable knowledge.

| Plane | What | Cadence | Home |
|---|---|---|---|
| **Durable** | constitution, MRD, BRD, PRD, roadmap, velocity baseline | set once, rarely changes | `docs/product/` (+ `.shipwright/velocity.json`) |
| **Living** | FRD, SRS, SDD, TSD, RTM, ADR/RFC logs, recon findings, backlog | edited continuously in place | `docs/specs/<feature>/`, `docs/RTM.md`, `docs/adr/` |
| **Cyclic** | sprint plan, retro — a fresh set **each sprint** | new instance per sprint | `docs/sprints/<sprint>/` |
| **Snapshot** | frozen baselines | immutable, per sprint / release | `.shipwright/baselines/<tag>` |

- **Recon findings** live with the feature they de-risk — `docs/specs/<feature>/recon.md` — and are cited by the PBIs/specs they inform.
- **Recurring sprint docs** get their own cyclic home so they never mix with durable knowledge; at sprint close they freeze to a baseline.
- The **durable** part of planning (roadmap, velocity/capacity baseline) stays in the durable plane so each new sprint reads from a stable source.

## 5. Naming & traceability

- **Req-IDs:** `<DOC>-<AREA>-<NUM>` (e.g. `FRD-AUTH-012`, `SR-PERF-004`, `PBI-CHECKOUT-007`). **Immutable once assigned.**
- **One living RTM per initiative**, threading business goal → story → requirement → design → test — proving coverage and showing blast radius. **One initiative per repo root** (a repo hosting multiple initiatives is out of scope for Standard v1).
- **ADRs use one global numeric sequence** going forward. Because IDs are immutable, a pre-existing collision discovered during conversion is resolved by **recorded supersession** (the superseded ADR records the survivor) — **never by silently renumbering** an already-assigned ID.

## 6. Metadata (so docs are machine-readable)

Every durable / living document carries a metadata header so the registry can catalog it — `Owner`, `Status`, `Version`, `Last updated`. The canonical form is a Field/Value table just under the H1; the bold-list form (`- **Status:** Accepted`) and YAML frontmatter are also parsed. Transient / operational docs (PR notes, standups) are exempt — keep them lean (anti documentation-fatigue).

## 7. Backlog — system of record

When a work tracker (Azure Boards / Jira) is connected, **the tracker is the system of record** for PBIs / backlog / bugs — status, workflow, and capacity live on the item. `backlog.md` is the **source / staging artifact** the team authors and syncs to the tracker; it is the system of record only until a tracker is wired. Never maintain the same item's status in two places.

## 8. The sanctioned exception

The only legitimate way to deviate from the canonical paths is `.shipwright/config.json`. Every knob defaults to the canonical tree, so an **absent config means "the standard."**

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

## 9. Adoption

- **Greenfield** — `python scaffold.py <repo> --profile <p>` (or `/spec-new`) lays down the tree.
- **Brownfield** — `python scaffold.py <repo> migrate` **converts** an existing repo to the standard: it relocates artifacts into the canonical tree and rewrites cross-links deterministically (dry-run by default). **Do not hand-move files** — the converter is the supported path; hand-moving is exactly what causes layout thrash.

## 10. Conformance

A repo is conformant when it matches the standard for its declared `profile` / `standard_version`. Enforced by:

- **`validate_reqs.py`** — Req-ID format, RTM coverage, ADR-reference integrity, **duplicate-ID and multiple-ADR-directory detection**, and a **layout / version conformance check**;
- **`build_artifact_registry.py --check`** — fails CI on any conformance violation.

Conformance is also queryable live via the `spindleloom` MCP server.

## 11. This document vs. INFORMATION-ARCHITECTURE.md

`STANDARD.md` is **the mandate** — what is required, and why. [`INFORMATION-ARCHITECTURE.md`](INFORMATION-ARCHITECTURE.md) is **the detailed reference** — how the tree, metadata, retrieval, and baselines work in practice. When the two appear to differ, **`STANDARD.md` governs**.
