---
description: Surface the next pull-able PBI from a backlog, with its acceptance criteria and spec refs.
argument-hint: [path-to-backlog.md]
---

From the backlog at **$1** (default: the `backlog.md` / `*-backlog.md` in context), return the **next item to pick up**.

1. Parse the PBI table(s) and the suggested pull order.
2. Find the topmost PBI whose dependencies are all marked done and whose Definition of Ready is met.
3. Return it in full: ID, **Type** (Story/Code · Decision · Docs · Spike · Bug), title, story, **acceptance criteria**, the upstream FRD/SRS IDs it traces to, and its Definition of Done.
4. Read those referenced spec sections and summarize the exact behavior/constraints the implementer must satisfy (so they can start without re-reading everything).
5. If the top item is **blocked**, say what blocks it and name the next unblocked item instead.

Do not start coding — this surfaces the work and its contract. If asked to implement, **route by Type** (see backlog-manager "PBI types & routing"): Story/Code → `backend-developer`/`frontend-developer`; Decision → `architect` → `adr-writer`; Docs → `feature-docs-writer`; Spike → `solution-recon`; Bug → `debugger`. Hand off the PBI as the spec — a Decision PBI yields an ADR, not a PR.
