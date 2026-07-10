# Project Guides — what lives here, and who reads what

**This folder is the knowledge hub** -- the Markdown sources of truth. **The browsable website lives in [`../spindleloom_website/`](../spindleloom_website/index.html)**: every `.md` here has a generated reading twin there (`BEST-PRACTICES.md` -> `best-practices.html`, ...), derived by `hooks/build_guides_site.py` with a `--check` drift gate. Edit the MD here, never the twin.

One owner per fact. Every topic below has exactly **one** home; every other file links to it instead of restating it. If you find yourself updating the same fact in two files here, the architecture is wrong — fix the ownership, not both copies.

## Layer 1 · UNDERSTAND — "what is this project?" (readers, HTML)

| Open | It gives you |
|---|---|
| [`project-overview.html`](../spindleloom_website/project-overview.html) | **The canonical end-to-end page.** Exec summary, loop engineering, the lifecycle, roles, all 52 agents by phase, the PBI journey, information architecture, traceability, the worked run + artifact chain, the pilot ask. If a fact about the whole system needs a home, it's here. |
| [`for-everyone.html`](../spindleloom_website/for-everyone.html) | The **plain-language story** — the wheel, the eight stages, the three moves. Deliberately links out for all detail; share this one with non-technical folks. |
| [`spindleloom-agent-fleet.html`](../spindleloom_website/spindleloom-agent-fleet.html) | The **interactive fleet map** — all 52 agents and every delegation edge, filterable. |

## Layer 2 · OPERATE — "what do *I* run?" (by role, HTML)

| Open | It gives you |
|---|---|
| [`claude-prompt-library.md`](claude-prompt-library.md) | The generic Claude power-prompts people share, **each mapped to the fleet specialist that does it better**, plus the official Claude Code prompt library and model-specific prompting tips. The fleet's own 54 per-role prompts live in the personas hub's Prompt-library lens. |
| [`personas/`](../spindleloom_website/personas/index.html) | **The Persona Field Handbook** — 15 role playbooks (builder + business side). Per role: the agents you drive, copy-ready prompts, your I/O contract, the gates you own, KPIs, hand-offs, troubleshooting, glossary. *The single by-role surface* — the older `how-to-use.html` is archived; `role-playbooks.html` was removed after salvage. |

## Layer 3 · GOVERN — standards & references (maintainers + agents, MD)

> Prefer reading in a browser? [`governance-handbook.html`](../spindleloom_website/governance-handbook.html) renders `GOVERNANCE.md` as one navigable page. It is a **generated view** -- edit the MD source, never the HTML.

| Read | It owns |
|---|---|
| [`GOVERNANCE.md`](GOVERNANCE.md) | The merged governance standard. **Part I** the versioned layout mandate for adopter repos (tree, profiles, cadence planes, ID immutability, conformance, the golden rule, baselines, retrieval, the tools); **Part II** story craft (cards, INVEST, AC, splitting, sizing); **Part III** the 9-person mapping, epic decomposition, Azure DevOps fit. |
| [`BEST-PRACTICES.md`](BEST-PRACTICES.md) | The documentation funnel, feedback loops, the requirement-quality standard (29148/INCOSE), traceability backbone, gates, delivery patterns. |
| [`AGENT-AUTHORING.md`](AGENT-AUTHORING.md) | The contract-block schema + prompting conventions. Read before creating/editing any agent. |
| [`LOOPWRIGHT.md`](LOOPWRIGHT.md) | The delivery-loop layer: inner/outer loops, DevEx, measuring & tightening, agents-to-loops map. |
| [`HARNESS-MATRIX.md`](HARNESS-MATRIX.md) | The 7-surface × 4-tool matrix the harness generator targets. |
| [`FLEET-EVAL.md`](FLEET-EVAL.md) | The behavioral E2E regression protocol (golden brief + judge rubric). |
| [`IMPROVEMENTS.md`](IMPROVEMENTS.md) | The living improvement register (audit-driven backlog for the toolkit itself). |

## `archive/`

Spent or superseded documents, kept for the record: the 2026 positioning piece (`AI-2026-TRENDS-AND-COVERAGE.md` -- its gaps were all built, so it read as marketing, not a to-do list), the pilot plan + both readouts, and the pre-personas `how-to-use.html` (its worked example was folded into `project-overview.html` §12, its invoke primer into the personas hub). `role-playbooks.html` was removed outright after its artifact chain, prompt-ingredients model and MCP scenarios were folded in. Nothing in `archive/` is load-bearing; don't link to it from new work except as history.

## Related, outside this folder

- Repo root [`README.md`](../README.md) — install, quick start, the 23 slash commands.
- [`hooks/HOOKS.md`](../hooks/HOOKS.md) — every hook/script, and how to wire them.
- [`agents/INDEX.md`](../agents/INDEX.md) / [`agents/HELP.md`](../agents/HELP.md) — generated agent indexes.
- [`../spindleloom_website/brand/`](../spindleloom_website/brand/) — the Woven Loop identity study + the live run-state widget; the SVG marks stay in [`../assets/`](../assets/).
