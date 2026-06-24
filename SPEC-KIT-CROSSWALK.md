# GitHub Spec Kit ↔ this toolkit — crosswalk & interop

*How [GitHub Spec Kit](https://github.com/github/spec-kit) relates to this toolkit, a command-by-command map, and three ways to adopt one, the other, or both.*

---

## TL;DR

**Spec Kit is the container; this toolkit is the content.** Spec Kit is a `uv`/`pipx`-installable CLI (`specify init`) that scaffolds files and installs `/speckit.*` slash commands into 30+ AI agents (Claude Code included). Its methodology is deliberately thin and feature-loop-shaped. This toolkit is a curated library of agents, templates, and skills with deep methodology (ISO/IEC/IEEE 29148 + INCOSE requirements, arc42/C4 design, RTM traceability, regulated/GAMP). **They compose**: Spec Kit's plumbing + this toolkit's depth.

## Command crosswalk

| Spec Kit command | What it does | Equivalent here |
|---|---|---|
| `/speckit.constitution` | Project governing principles | `/constitution` command + `templates/constitution-template.md` |
| `/speckit.specify` | Requirements & user stories | The funnel: `mrd-writer` → `brd-writer` → `prd-writer` → `frd-writer` |
| `/speckit.clarify` | Resolve ambiguous requirements | `requirement-quality` skill (29148/INCOSE per-requirement gate) |
| `/speckit.plan` | Technical plan + tech stack | `srs-writer` → `sdd-writer` (arc42/C4) → `tsd-writer`; decisions logged by `adr-writer` |
| `/speckit.tasks` | Ordered task breakdown | `backlog-manager` + `backlog-decomposition` skill |
| `/speckit.taskstoissues` | Tasks → GitHub issues | — (out of scope; pair with `gh`/your tracker) |
| `/speckit.implement` | Execute tasks → code | Inner-loop agents (`test-author`, `code-reviewer`, …) governed by `ai-orchestration` |
| `/speckit.analyze` | Cross-artifact consistency | `/spec-analyze` command + `cross-artifact-analysis` skill |
| `/speckit.checklist` | Quality validation checklists | `definition-of-ready-done` + `requirement-quality` + `test-plan` |
| *(traceability — not a Spec Kit command)* | — | `/rtm-check` + `traceability-rtm` skill + `RTM.md` |

## The structural difference that matters

Spec Kit organizes by **feature**: `specs/[feature-id]/{spec.md, plan.md, tasks.md, data-model.md, contracts/, quickstart.md}`. This toolkit organizes by **document type**: the MRD→TSD funnel, tied together by a shared `RTM.md`.

- **Per-feature (Spec Kit)** suits agile/incremental work — each feature is a self-contained folder you scaffold and implement.
- **Per-document (this toolkit)** suits regulated/waterfall/larger programs — traceability and altitude discipline across the whole product.

They aren't exclusive. A **hybrid** layout: per-feature folders for the spec/plan/tasks, each linking up to the shared funnel docs (PRD/SRS) and a single `RTM.md` that threads Req-IDs across both. Use feature folders for *the work*, the funnel + RTM for *the system of record*.

## What each does better (honest)

| Spec Kit | This toolkit |
|---|---|
| One-command install & scaffolding (`specify init`) | Deep requirement rigor (29148/INCOSE, "system shall") |
| Fan-out across 30+ agents; presets/extensions | RTM traceability — find blast radius, prove nothing dropped |
| Tight feature spec→code loop | Full SDLC: delivery, governance, inner-loop, regulated/GAMP |
| Slash-command + skills mode out of the box | Cross-artifact semantic analysis (`/spec-analyze`), ADR discipline |

Don't chase `/speckit.implement`-style full automation — this toolkit's `ai-orchestration` + human-in-the-loop gates are the more responsible design for anything past a prototype.

## Three adoption paths

1. **Coming from Spec Kit** — keep `specify init` for install/scaffolding and the `/speckit.*` commands; replace Spec Kit's thin templates with these via its **preset** mechanism (`.specify/templates/overrides/` or an installed preset). You get Spec Kit's plumbing with this toolkit's depth.
2. **Greenfield / no Spec Kit** — use this toolkit directly: copy `agents/` into `.claude/agents/`, run the `/constitution` → funnel → `/spec-analyze` → backlog flow. Ignore the CLI.
3. **Hybrid** — Spec Kit for scaffolding and slash-command install across agents; this toolkit for artifact depth, traceability, and governance.

## Roadmap option (not built)

Package this toolkit as a **Spec Kit preset** so `specify preset add` installs the templates and command overrides in one step. That would make the toolkit a true drop-in depth upgrade for the Spec Kit ecosystem. Tracked as a future item — see `AI-2026-TRENDS-AND-COVERAGE.md` for the broader direction.
