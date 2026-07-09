---
name: context-engineering
description: Assemble the right, minimal context for an agent's task — a budget-first reading order (recall → digests → traced sections → full read last), the context-pack manifest (`hooks/build_context_pack.py`), source-cited working notes, and stale-context handling. Use at the start of any task that consumes upstream artifacts, when a context window is filling with full-document reads, or when dispatching another agent. Consumed by run-orchestrator, solution-recon, backend-developer, and frontend-developer; pairs with agent-handoff-context (the save/recall half).
---

# Context engineering — feed the task, not the archive

An agent's quality degrades in both directions: too little context invents facts; too much
buries the three lines that matter under 40k tokens of prose. The method: **budget first,
then fill by priority — cheapest, highest-signal sources first — and stop when the task
is grounded**, not when the folder is exhausted.

## The reading order (cheapest signal first)

1. **Recall before reading.** `recall_context(query, task_id)` — one call returns prior
   agents' compressed notes. Treat `stale: true` entries as *leads to re-verify*, never
   as facts. Also recall `task_id="project-ops"` for the environment incantations.
2. **Digests and headers.** Each doc's Field/Value header (Owner/Status/Version/Updated)
   and its `## Digest` section (≤5 bullets, where present) tell you whether the full doc
   is worth your budget. Status `Draft` reads differently from `Approved`.
3. **Traced sections only.** Use the RTM (or `trace_requirement`) to find the exact IDs
   your task touches, then read *those sections* of the upstream docs — not the documents
   end-to-end. `search_specs` beats a full read for a single fact.
4. **Full reads last**, and only for the artifacts your contract `inputs:` names. If you
   are reading a document your contract doesn't route to you, either the contract is
   wrong (flag it) or you are drifting.

## The context pack (mechanical assembly)

`python hooks/build_context_pack.py <project-root> <agent> [--feature <slug>] [--task-id <slug>]`
assembles the manifest for one agent+task: the contract's inputs resolved to real paths
(with Status/Updated stamps), the feature's RTM slice, saved context entries (stale-flagged),
open `ASSUMPTION-n` tags in scope, and a size estimate against the budget. Dispatchers
(run-orchestrator, or a human) hand the pack to the agent instead of "read the docs folder".

## Budgets

| Situation | Budget discipline |
|---|---|
| Ceremony agents (estimate, plan, retro) | contract inputs only — the backlog/estimates ARE the compression |
| Builders | the recon pack + traced spec sections; full FRD/SRS only for the touched IDs |
| Writers | full upstream doc(s) they refine + digests of everything else |
| Reviewers/checkers | the diff/change + the AC + the standard — not the whole funnel |

The pack builder prints the assembled size; when it exceeds the budget it says what to
demote from full-read to digest/query. Over budget is a signal to compress upstream
(a missing digest, an unsplit doc), not to skim silently.

## Writing FOR downstream context (the producer's half)

- End every CREATE with a **`## Digest`** — ≤5 bullets: what this doc decides, the IDs it
  mints, what downstream must not miss. It is an abstract (pointers), not a copy.
- `save_context` your working notes with `source=` set, so recall can stale-flag them.
- Cite IDs, not prose ("per SR-PERF-001", not "per the performance requirement") — IDs are
  greppable, traceable, and cheap to verify.

## Anti-patterns

| Smell | Fix |
|---|---|
| "I read every file in docs/ to be safe" | Budget first; the contract + RTM slice define scope |
| Re-deriving the test incantation | `recall_context(task_id="project-ops")` |
| Trusting a recalled note over the artifact | `stale: true` → re-verify against the source |
| A shared log everyone appends to as transport | save/recall with task_id — scoped, queryable, gated |
| Pasting whole documents into a dispatch prompt | hand the context-pack manifest instead |
