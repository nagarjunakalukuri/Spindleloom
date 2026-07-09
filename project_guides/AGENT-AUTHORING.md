# Agent Authoring Conventions

How every agent in this project is written, so the fleet stays consistent as it grows. Distilled from Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) and tailored to document-writing agents. Read this before adding or editing an agent.

## Prompting principles we follow

1. **Clear role + context with the *why*.** Open with a one-line role ("You are a senior business analyst…") and explain *why* the document matters. Models generalize better from motivation than from rules alone. (Best practices: *Give Claude a role*, *Add context*.)
2. **Sequential, numbered workflow.** Steps where order/completeness matters go in numbered lists (our `When asked to CREATE/REVIEW/UPDATE` sections). (*Be clear and direct*.)
3. **Calm instructions — no overtriggering.** Do **not** use shouty imperatives like "CRITICAL", "you MUST", "ALWAYS", "NEVER" to force behavior. Modern Claude models (Opus 4.5+) *overtrigger* on aggressive language. Use normal phrasing: "Use X when…", "Prefer…". (*Tool usage*, *Overthinking*.)
4. **Ground, don't fabricate.** Agents read the upstream document(s) before drafting, verify facts (WebSearch for market data, current standards, library versions), cite sources with dates, and explicitly flag any value they assumed rather than confirmed. Never invent figures or requirements. (*Minimizing hallucinations*.)
5. **Right-sized output — fight documentation fatigue.** Produce the leanest document that does the job for the team's tier; don't pad. No feature/section beyond what the task needs. This mirrors the doc's anti-overengineering guidance and our own "documentation fatigue" theme. (*Overeagerness*.)
6. **Examples teach format.** Where an exemplar helps, point to or wrap a concrete example in `<example>` tags so the model distinguishes it from instructions. The `examples/healthy-meal-app/` set is the project's canonical end-to-end exemplar — reference it rather than re-inventing samples. (*Use examples effectively*.)
7. **Tri-mode + handoffs.** Every document agent supports create / review / update, names the agent it hands off to, and flags discoveries back upstream (feedback loops in `BEST-PRACTICES.md`).

## Frontmatter conventions

```yaml
---
name: <kebab-case; `-writer` for document agents, a role/action name for others (e.g. doc-strategy-advisor, backlog-manager, estimation-facilitator, sprint-planner, retrospective-facilitator, spec-steward)>
description: One sentence on purpose + explicit trigger phrases the user might say + any aliases (e.g. FSD→frd/sdd, TRD→srs) + where it sits in the funnel.
tools: Read, Write, Edit, Glob, Grep[, WebSearch, WebFetch]   # add web tools only if the agent verifies external facts
model: inherit
examples:                       # 1-2 copy-paste prompts a user would TYPE to invoke this agent
  - "Break docs/prd.md into INVEST user stories with acceptance criteria, ordered by MoSCoW."
  - "Split PBI-CHECKOUT-007 into 2-4 stories that still trace to FRD-ORD-001."
---
```

- **description does the triggering** — list the real phrases a user would type, plus aliases, plus run-order ("Run after the PRD"). This is what routes work to the right agent.
- **examples** are the copy-paste prompts surfaced by `/help-role`, `agents/HELP.md`, and the generated `AGENTS.md`. Keep them specific to *this* agent (not swappable), in natural user phrasing (what a person types, not a description), calm (no shouty caps), and one tight sentence each. Quote each entry; YAML-escape literal quotes. `validate_graph.py` fails if an agent has none. Generate at scale with the `author-agent-examples` workflow → `hooks/add_examples.py`.
- **tools:** document agents need Read/Write/Edit/Glob/Grep; add WebSearch/WebFetch only for agents that verify external facts (mrd, srs, sdd, tsd, urs). Router/log and delivery/facilitator agents (doc-strategy-advisor, adr-writer, backlog-manager, estimation-facilitator, sprint-planner, retrospective-facilitator) omit web tools.

### Machine-readable contract (the handoff graph)

The framework's value is an unbroken handoff chain feeding one RTM — but that chain lives only in prose across the agent files, so a new team has to reverse-engineer it. Every agent therefore also declares a **contract block** in frontmatter so the funnel is discoverable and tool-parseable (auto-build the graph, validate coverage, drop into any `.claude/`):

```yaml
phase: planning                       # discovery|requirements|design|planning|build|test|review|release|operate|process
loop: planning                        # which delivery loop it tightens: inner|outer-integrate|outer-ship|planning|governance (LOOPWRIGHT.md §6)
agentic_role: facilitator             # role in the agentic loop: maker|checker|facilitator|keeper|orchestrator|advisor
inputs: [PRD, FRD]                    # upstream artifacts this agent reads
outputs: backlog                      # the artifact it produces/maintains
id_prefix: PBI                        # ID convention it owns (omit if it produces no IDs)
rtm_column: "Product story → Backlog item (PBI)"   # the RTM column it populates ('—' if none)
upstream: [prd-writer, frd-writer]    # agents it receives handoffs from
downstream: [estimation-facilitator, sprint-planner]   # agents it hands off to
gate: definition-of-ready-done-template.md   # entry/exit criteria it enforces (omit if none)
skills: [backlog-decomposition]       # skills it relies on (so they self-arm)
claude_code: { command: /plan-next, subagent_type: backlog-manager }   # portability mapping
```

- **Additive and convention-only** — no behavior change; it makes the handoff/traceability data that was prose into something a hook, an index generator, or `/agents` can read.
- **`loop` + `agentic_role`** classify the agent along the two loop dimensions: which *delivery* loop it tightens (`LOOPWRIGHT.md` §6 — `inner` = the developer's edit/build/test cycle, `outer-integrate` = PR→CI→QA, `outer-ship` = release→operate, `planning` = the spec/agile planning loop, `governance` = cross-cutting registers and orchestration) and which *agentic* role it plays in a maker/checker loop (`maker` produces an artifact, `checker` returns a verdict without patching the work under review, `facilitator` runs a ceremony/process, `keeper` maintains a living register, `orchestrator` dispatches other agents, `advisor` analyzes and recommends). `validate_graph.py` enforces both fields exist with valid values; the run-orchestrator and generators may route or group by them.
- Build/design agents that produce ad-hoc notes still get an `id_prefix` (e.g. `API-`, `DM-`, `FE-`, `BE-`) so the RTM chain doesn't dead-end at the design/build layer.
- Top-of-funnel and log agents set `upstream: []` / `rtm_column: "—"` as appropriate — empty is a valid, explicit answer.
- **The Digest convention.** Every document agent ends its CREATE output with a `## Digest` — ≤5 bullets: what the doc decides, the IDs it mints, what downstream must not miss. It's an abstract (pointers), not a copy; `build_context_pack.py` surfaces it so downstream agents can triage before full-reading (see the `context-engineering` skill).
- **Context layers — one home per kind of context.** Three stores exist while a run executes; the same fact in two of them is a defect (the golden rule applied to context): **facts/decisions of record** → the docs tree + RTM/ADRs (durable, reviewed); **compressed working notes** — decisions-in-flight with reasons, output paths, blockers, inherited constraints, resolved incantations → the `sloom` context memory (`save_context`/`recall_context`; the committed, git-mergeable `.spindleloom/context-log.jsonl` is the cross-machine source of truth, `.spindleloom/context.db` its local gitignored index — teammates run `sloom context . --import` after a pull), ≤5 bullets per entry, scoped by `task_id`; **orchestration state** — stop contract, ledger, gates → `.spindleloom/runs/<run-id>.json` (one file per run, so concurrent runs by different teammates never clobber each other). Ad-hoc handoff files (a shared log everyone appends to) are the anti-pattern: lossy, unscoped, and invisible to `validate_gates --context`.
- **Edge semantics.** `upstream`/`downstream` model **artifact handoffs and routing** in the forward direction only. Two flows are deliberately *not* graph edges: (a) **feedback flag-backs** — the prose "Feedback loop" sections route push-backs (e.g. sdd-writer's reality-check to prd/srs-writer) out-of-band, so a run driver must read them from the body, not the graph; (b) **the recon context pack** — developers receive FRD/SRS/SDD content via `solution-recon-findings` (the warm build context), not via direct edges from each writer. Advisor/router agents' downstream edges mean "routes to", not "hands an artifact to".

## Agent classes

- **Document agents** (`*-writer`): produce a versioned document; body = role → principles → create/review/update → embedded template → who participates → common pitfalls → feedback loop (if it has meaningful upstream feedback) → style rules. Always ship a matching `templates/` file.
- **Facilitator/delivery agents** (backlog-manager, estimation-facilitator, sprint-planner, retrospective-facilitator): run a recurring agile activity and maintain living state (backlog, estimates, sprint plan, retro log). Same body shape, but the "template" is the artifact they maintain, and they chain to each other rather than feeding the document funnel.
- **Router/practice agents** (doc-strategy-advisor, spec-steward): advise or assess rather than produce a fixed artifact; a template is optional.
- **model:** `inherit` unless a task needs a specific model.

## Shared standards every agent points to

- Requirement quality (29148/INCOSE checklist, "the system shall…", one obligation per statement) → `BEST-PRACTICES.md`.
- Req-ID convention `<DOC>-<AREA>-<NUM>` and the RTM traceability backbone → `BEST-PRACTICES.md`.
- Feedback loops, change control, team-size tiers, frameworks (arc42, C4, Diátaxis, Docs-as-Code) → `BEST-PRACTICES.md`.

## Checklist for adding a new agent

1. Confirm it fills a real gap, not an alias of an existing doc (check the alias map in `doc-strategy-advisor.md`).
2. Write frontmatter per the conventions above (triggers, aliases, tools, run-order) **plus the machine-readable contract block** (phase, inputs/outputs, id_prefix, rtm_column, upstream/downstream, gate, skills, claude_code) **plus 1-2 `examples:` prompts** (`validate_graph.py` enforces their presence).
3. Body: role + why → core principles → create/review/update workflow → embedded template → who participates → common pitfalls → feedback loop (include only where the agent has meaningful upstream feedback — top-of-funnel and log agents may omit it) → style rules.
   - **Gate/verification agents** (review, test, security, accessibility, CI, AI-orchestration) should also carry a short **Anti-rationalization** table — the excuses used to skip the gate paired with the rebuttal — placed just before "Common pitfalls". It keeps a gate from being waved through, especially by an AI agent talking itself out of the check. Keep it calm and tailored (3–5 rows), not generic.
4. Use the shared Req-ID convention and reference the quality checklist; don't redefine them.
5. Add a matching `templates/<doc>-template.md`.
6. Register it: `README.md` (agent table + templates list), `doc-strategy-advisor.md` (funnel/tiers/ownership), and `BEST-PRACTICES.md` if it changes the funnel.
7. Add it to the `examples/healthy-meal-app/` run if it belongs in the mainline chain.
8. Run a consistency check: no aggressive caps, no fabricated samples, references resolve.
