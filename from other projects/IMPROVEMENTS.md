# Toolkit Improvements — Wheelwright PM-Agents (pilot-driven backlog)

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Living |
| Last updated | 2026-06-20 |
| Sources | [`PILOT-READOUT.md`](PILOT-READOUT.md) (Run 1, 2026-06-15→16) · Run 2 (2026-06-20) · Run 3 (2026-06-20, IA episode) |

> A living, prioritized backlog of concrete improvement candidates for the fleet + tooling, captured from
> real pilot runs on the **IDP-Accelerator** repo. Every item = *component · gap · fix*, grounded in something
> we actually hit. Run 1 = a 4-item build/test pilot; Run 2 = a PM-agent re-prioritization + an end-to-end
> push to Azure Boards + a canonical information-architecture migration.

## Prioritized backlog

| ID | Area | Gap → Fix | Priority | Source |
|----|------|-----------|----------|--------|
| **IMP-001** | scaffold / IA | `scaffold.py` only *creates* (idempotent), no story for an existing repo with content. We hand-migrated (`git mv` + `sed` link surgery). → add a **`migrate`/`adopt` mode** that relocates existing artifacts into the canonical tree and rewrites cross-links. | **High** | Run 2 |
| **IMP-002** | registry | `build_artifact_registry.py` silently emitted **duplicate IDs** (two `ADR-0004`/`ADR-0005`: our `docs/adr/` vs the repo's existing `docs/12-decisions/`). → **detect + warn/error on duplicate Req-IDs and multiple ADR directories** (`--check` should fail). | **High** | Run 2 |
| **IMP-003** | ADR convention | ADRs are numbered **initiative-locally** (`adr-0001…`) so they collide across initiatives/repos. → global or **initiative-prefixed IDs** (`ADR-AEP-001`); `scaffold` should **detect + reuse an existing ADR dir** rather than create `docs/adr/`. | Med | Run 2 |
| **IMP-004** | doc agents | Output lacks the IA **metadata header**, so the catalog came back with owner/status/version = `—` for most rows. → every doc-producing agent emits the Field/Value metadata block the IA requires. | **High** | Run 2 |
| **IMP-005** | IA | `solution-recon` findings ("solution-recon-findings") have **no canonical home** (neither durable doc nor PBI); we parked them ad hoc. → name where recon findings live in `INFORMATION-ARCHITECTURE.md`. | Med | Run 2 |
| **IMP-006** | IA / RTM | **Multiple-RTM** story undefined — `aep_decouple/RTM.md` + `docs/RTM.md` both catalog as id `RTM` (collision). → per-initiative RTM guidance + a root index. | Med | Run 2 |
| **IMP-007** | Azure | **No backlog→Boards automation.** `TEAM-ROLES-AND-AZURE-DEVOPS.md` describes the mapping but ships nothing; we created 60+ items by hand via MCP + a manual CSV. → a **`backlog.md → Boards` push/sync tool** (+ reverse `Boards → catalog` status sync). | **High** | Run 2 |
| **IMP-008** | Azure | Iteration creation **silently failed** (classification-node permission the MCP lacked); fell back to `sprint-N` tags. → document required **PAT scopes + the iteration-creation caveat**. | Med | Run 2 |
| **IMP-009** | backlog-manager | No **re-prioritize/re-order sub-workflow** — it's framed for *create-from-PRD*; re-ordering an existing backlog + cutting one dependency edge meant adapting the CREATE flow. → add a distinct RE-PRIORITIZE mode. | **High** | Run 2 |
| **IMP-010** | sprint-planner | **Single-sprint** template with no slot for **conditional/gated commitments** or a **must-land-by** field — multi-sprint output + the runtime/decision gates needed hand-rolling; the "leave slack" rule collided with a hard sale-gate. → multi-sprint mode + conditional state + must-land-by. | **High** | Run 2 |
| **IMP-011** | delivery agents | **Readiness is binary** (Ready/blocked) but we hit three distinct kinds: **blocked-on-runtime**, **blocked-on-decision**, **blocked-on-external-release**. → a richer readiness taxonomy shared by backlog-manager + sprint-planner. | Med | Run 2 |
| **IMP-012** | sprint-planner / estimation | **No velocity persistence** — capacity was hand-fed ("~36 pts") with no source; `estimation-facilitator` computes velocity but nothing stores it. → a velocity/baseline store the planner reads. | Med | Run 2 |
| **IMP-013** | feedback loops | Agents *should* "flag discoveries upstream" but the mechanism is **manual** (recon → we hand-edited the briefs + wrote ADR-0005). → a structured **discoveries/feedback log** artifact. | Med | Run 1+2 |
| **IMP-014** | pbi-next / backlog-manager | **No pre-pickup existence check** — Run 1 nearly rebuilt an already-shipped feature (spec said "deferred", code was done). → wire `solution-recon`'s existence check into the DoR / `pbi-next` ("does the artifact/code already exist?"). | **High** | Run 1 |
| **IMP-015** | pilot / CI | **Environment-readiness is unmodeled** and bit Run 1 twice (non-collecting test suite; unconfigured Vitest). → a **Wk-0 baseline gate** (build + test suites collect & pass, lint runs) before the funnel starts. | **High** | Run 1 |
| **IMP-016** | process | Full ceremony (plan-first, security gate) is **overhead on test-authoring/verify** items. → apply the **lean-10**; reserve the full gate for **build-from-scratch** work. | Med | Run 1 |
| **IMP-017** | adoption | Agents ran **"inline"** (a subagent reading each `.md` spec) rather than installed. → a one-command install into `.claude/agents/` (the `targets/claude-code` build) in the pilot guide. | Low | Run 2 |
| **IMP-018** | standard | **No declared stance** — the IA doc reads as a *default*, not an enforced standard, so a brownfield repo waffles between "adopt canonical" and "keep existing" (Run 3 reversed the same files 3×). → ship an authoritative **`STANDARD.md`**: the one project-agnostic layout adopters target; existing repos **convert to it**. | **High** | Run 3 |
| **IMP-019** | config / scaffold | Layout is **hardcoded** in `scaffold.py` (`docs/specs`, `docs/adr`); no per-project knobs. → `.shipwright/config.json` declares `docs_root`/`adr_dir`/`specs_dir`/`sprints_subdir`; scaffold + agents **honor it**; default = the standard (the escape hatch, not the norm). | **High** | Run 2+3 |
| **IMP-020** | IA doc | The durable/living/snapshot **3-plane model** + lean `sprints/` subfolder + **baseline-per-sprint** isn't documented, so teams reinvent "global vs sprint docs." → document it in `INFORMATION-ARCHITECTURE.md`. | Med | Run 3 |

## Top 3 by leverage
1. **IMP-001 — brownfield migrator.** Proven by Run 3: without a deterministic converter, every adoption hand-thrashes the layout (we reversed the same files 3×). The IA assumes a fresh scaffold; real repos already have `docs/` + an ADR log.
2. **IMP-018 — `STANDARD.md` (pick one stance).** The waffling came from having no authoritative target. Lock *standard + converter*; stop hand-moving files until the converter exists.
3. **IMP-007 — backlog→Boards sync.** The toolkit's promise (Azure mapping) outran its tooling; the entire last mile was manual.

## What worked (keep — don't "improve" away)
- **Plan-first on build-from-scratch** and the **security gate** caught real defects (Run 1).
- **Enforced traceability** (RTM + `validate_reqs.py`) is the rare, real asset; the catalog/baseline machinery caught the ADR collision the moment it ran (Run 2).
- The **delivery chain** (backlog-manager → sprint-planner) mapped cleanly onto a real re-prioritization; `solution-recon`'s brownfield ground-truth directly de-risked the plan (Run 2).
- The **registry/catalog is genuinely layout-agnostic** — it scans `docs_root` and detects kind by filename token across *any* folder names (proven on `12-decisions` + `19-v2-program`), so only `scaffold.py` is layout-bound (Run 3). The **3-plane model** (durable docs / living tracker / baseline snapshots) cleanly answers "global vs sprint docs."
