---
name: agent-handoff-context
description: Token-efficient context handoff between agents using the MCP memory tools (save_context / recall_context / list_contexts). Compresses decisions, outputs, blockers, and constraints into <=5 bullets that downstream agents retrieve in one tool call -- no re-reading of full documents. Use at the START of any task with prior upstream agents, and at the END before handing off downstream.
---

# Agent handoff context -- compress and persist what the next agent needs

## Why

Reading upstream docs end-to-end wastes tokens when only 3--5 facts govern the next step.
Saving those facts to the MCP memory layer lets downstream agents recall them in one tool call
at near-zero token cost.

Rule: **recall before reading, save before handing off.**

---

## Pattern: START of task (recall first)

Before opening any upstream document, check what prior agents already decided:

```
list_contexts(task_id="<feature-slug>")
```
Scan who ran and what they saved. Then retrieve the relevant facts:

```
recall_context(query="<your keywords>", task_id="<feature-slug>", limit=5)
```

Use the recalled facts to decide which upstream docs (if any) you still need to read in full.
A recalled "• Decision: JWT RS256 -- SSO req" means you don't re-read the entire SRS to find
the auth constraint -- it's already extracted.

If `recall_context` returns nothing, proceed with full document reads as normal and save context
when you finish.

---

## Pattern: END of task (save before handoff)

After producing your output, save a compressed summary in <=5 bullet points using this schema:

| Slot | What goes here | Example |
|---|---|---|
| **Decision** | Choice made + one-line reason | `Decision: JWT RS256, 15 min expiry -- SSO req SRS-SEC-002` |
| **Output** | What you produced + where it lives | `Output: src/auth/token_service.py -- POST /token, POST /refresh` |
| **Blocker** | Unresolved item downstream must know | `Blocker: refresh-token rotation not spec'd -- change-verifier should flag` |
| **Constraint** | SRS/SDD constraint you respected (saves next agent re-deriving it) | `Constraint: SRS-SEC-003 max 200ms met -- measured p99 = 140ms` |
| **Open** | What the next agent must decide or verify | `Open: security-reviewer to check token storage on mobile clients` |

```
save_context(
    agent_id="backend-developer",
    task_id="user-auth",
    facts=(
        "• Decision: JWT RS256, 15 min expiry -- SSO req SRS-SEC-002\n"
        "• Output: src/auth/token_service.py -- POST /token, POST /refresh\n"
        "• Blocker: refresh-token rotation not yet spec'd\n"
        "• Constraint: SRS-SEC-003 max 200ms met -- p99 = 140ms\n"
        "• Open: change-verifier should run the SEC suite before PR"
    ),
    tags="auth,security,jwt,backend"
)
```

---

## Token budget

| Unit | Limit |
|---|---|
| Each bullet | <=100 chars |
| Full facts field | <=500 chars total |
| recall_context results | max 5 returned (enough to ground any agent) |

Violating the budget defeats the purpose -- keep facts terse and precise.

---

## Do you even need this? (when to skip)

The harness already maintains context *within one conversation window* — saving and
recalling inside a single-agent, single-session task is pure overhead; skip it. The store
exists for the boundaries that window cannot cross: **subagent isolation** (every fleet
agent starts with an empty window — it has seen nothing of the conversation), **session
end** (resume tomorrow), **compaction** (long sessions summarize lossily and you don't
choose what survives; a saved entry is deliberate compression), **tool switches**
(Cursor shares nothing with Claude Code; the MCP store is common), and **teammates**
(their context starts at zero). Rule of thumb: one agent + one sitting = conversation is
enough; anything chained, resumed, or shared = save before handoff.

## Which context goes where (the boundary rule)
Facts of record (requirements, decisions, designs) live in the **docs tree** — never re-state them here; cite the path. This store holds only **compressed working notes**: decisions-in-flight + reason, output paths, blockers, inherited constraints, open questions. Orchestration state (stop contract, ledger) lives in `.spindleloom/run-state.json`. The same fact in two stores is a defect. When your facts summarize one artifact, pass `source="<its path>"` — recall then flags the entry **stale** if the registry shows the artifact changed after you saved, so outdated summaries are visible instead of authoritative.

## task_id convention

Use a stable slug for the feature or sprint:
- Feature: `user-auth`, `payment-checkout`, `admin-dashboard`
- Sprint: `sprint-3`, `sprint-4-hotfix`
- Run: `run-20260625` (when driven by run-orchestrator)

The same slug must be used by all agents in that work stream so `recall_context` scopes correctly.

---

## run-orchestrator usage

The run-orchestrator saves the run spine at each dispatch step:

```
save_context(
    agent_id="run-orchestrator",
    task_id="<run-id>",
    facts=(
        "• Dispatched: backend-developer -- user-auth token service\n"
        "• Stop contract: all AC in FRD-AUTH-001..005 passing\n"
        "• Gate: change-verifier must pass before pr-author\n"
        "• Budget: 3 agents remaining of 7 planned\n"
        "• Next: change-verifier"
    ),
    tags="run-state,orchestration"
)
```

And recalls it at each resume to know where the run left off -- making runs resumable across
sessions without re-reading the contract graph.

---

## Writing good recall queries

SQLite mode scores by keyword overlap — every word in your query is checked against the
`facts` and `tags` fields. Rules:

1. **Use full words, not abbreviations** — `acceptance criteria` not `AC`, `kubernetes` not `K8s`.
   Facts are saved with full words; abbreviated queries miss them.
2. **Include the Req-ID when you know it** — `FRD-TRK-001` is a strong discriminator.
3. **Name the upstream agent when known** — `srs-writer security PCI constraints` scores higher
   than `security constraints` alone.
4. **Use 3–6 keywords** — fewer than 3 may be too broad; more than 8 dilutes the score.
5. **Semantic mode** — write a natural phrase rather than keywords:
   `what auth constraints did the security reviewer flag` beats `security review auth constraints`.

---

## Interpreting recall scores

**SQLite mode** — `score` = matched keywords / total query keywords (0–1):

| Score | Meaning | Action |
|---|---|---|
| >= 0.6 | Strong match | Use as ground truth |
| 0.3–0.59 | Partial match | Skim facts, verify key claims |
| < 0.3 | Weak hit | Treat as hint only; read source doc |

**ChromaDB semantic mode** — cosine similarity (-1 to 1, typically 0–1 in practice):

| Score | Meaning | Action |
|---|---|---|
| >= 0.30 | Reliable match | Use as ground truth |
| 0.15–0.29 | Context hint | Verify with source doc |
| < 0.15 | Likely noise | Ignore |

---

## Cross-task search

Omit `task_id` to search across all saved context — useful when reusing decisions from a
previous sprint or feature:

```
recall_context(query="JWT refresh token auth pattern", limit=5)
```

Use cases:
- "What auth approach did we use on the user-auth feature?"
- "Has anyone already documented the Kafka idempotency approach?"
- "What tech-radar decisions exist for Node.js?"

Cross-task recall still ranks by keyword relevance, so the best match across all tasks
surfaces first regardless of which sprint or feature it came from.

---

## Context lifecycle -- when to clean up

Context accumulates across sprints. Call `delete_context` at:

- **Sprint boundary** — after retro is complete and facts are encoded in the backlog:
  `delete_context(task_id="sprint-3")`
- **Feature close** — after the feature ships and retrospective notes are final.
- **Superseded decision** — when an agent re-runs and produces different facts, the new
  `save_context` creates a fresh snapshot (both coexist, newest first). Delete the stale one:
  `delete_context(task_id="payment-checkout", agent_id="architect")`
- **one bad or superseded note** among good ones — find its id via `list_contexts`, then:
  `delete_context_entry(entry_id=42)`

Use `list_contexts(task_id=...)` to audit what's still live before deleting.

---

## What NOT to save

- Do NOT save raw document sections -- save the extracted decision, not the paragraph it came from.
- Do NOT save things already in the RTM -- use `trace_requirement` instead.
- Do NOT save implementation details the next agent will read from code directly.
