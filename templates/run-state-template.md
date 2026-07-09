# Run State — <objective / feature>

> The `run-orchestrator`'s spine for one fleet run — the single source of truth for *where the run is*. The machine copy lives at `.spindleloom/runs/<run-id>.json`; this file is its human-readable mirror at `.spindleloom/runs/<run-id>.md`. **One file pair per run, keyed by run-id** — concurrent runs (two teammates, two features) never share a file. The orchestrator reads and updates it each step, and resets context between steps — **this file is the memory** (state lives on disk, not in the context window). Humans check/advance a run without an LLM via `sloom run status|advance <run-id>`.

| Field | Value |
|---|---|
| Run id | `run-YYYYMMDD-<slug>` |
| Objective | <one line> |
| Feature | `<slug>` — the acceptance namespace. **Must match the `--feature` slug used with `sloom approve`** so `sloom run advance` finds the token at `approvals/<feature>/<phase>.md`. Stored as the top-level `feature` key in the run JSON; omit (defaults to `project`) only for single-feature / whole-project runs. |
| Handoff context | each completed ledger step records the `save_context` entry (agent_id + task_id) it saved, or an explicit `none — nothing to hand off`; `validate_gates.py --context <task_id>` proves the stream is non-empty |
| Sign-off tokens | `.spindleloom/signoffs/{qa,security,performance,accessibility,raid,dod}.md` — or `signoffs/<release-id>/<gate>.md` when more than one release train is in flight — written by the owning gate agents; `validate_gates.py --release [--release-id <slug>]` computes the AND |
| Entry point | doc-strategy-advisor / solution-recon / pbi-next / incident-responder / ai-orchestrator |
| Autonomy rung | 0 manual · 1 triage · 2 draft · 3 verified-PR · 4 auto-merge |
| Status | active / blocked / done / stopped |

## Stop contract (all four — see the `agentic-loop-design` skill)
- **End state:** <measurable done condition — e.g. "PRD→FRD→backlog exist and trace; the tracking PBI is built and change-verifier returns PASS">
- **Evidence:** <the proof that must exist — e.g. "RTM coverage clean; verification-report PASS; CI green">
- **Constraints:** <boundaries / protected paths — e.g. "no DB migrations; don't touch auth">
- **Budget:** <hard cap — turns / tokens / $ / wall-clock>

## Agent ledger
status: `pending` · `running` · `done` · `blocked`. A step that crosses a phase boundary carries `requires_acceptance: <phase>` in the JSON — it cannot go `done`/`running` until `.spindleloom/approvals/<feature>/<phase>.md` says `Verdict: ACCEPTED` (written by the accountable role via `sloom approve`; enforced identically by `sloom run advance` and the orchestrator).

| # | Agent | Status | Gate | Produced (artifact / id) | Notes |
|---|---|---|---|---|---|
| 1 | doc-strategy-advisor | done | — | doc-strategy | tier = mid |
| 2 | prd-writer | done | — | docs/product/prd.md (PRD) | |
| 3 | frd-writer | running | — | — | |
| 4 | backlog-manager | pending | DoR | — | join: waits on FRD + SRS |
| 5 | backend-developer | pending | — | — | routed via /plan-next by PBI type |
| 6 | change-verifier | pending | DoD | — | build-phase gate before PR |

## Runnable now
<agents whose required upstreams are `done` and gate passed — what the orchestrator proposes to dispatch next>

## Blocked
<agent → what it is waiting on>

## Decision log (provenance)
- <date> — <decision · why · what was rejected> — so the next human/agent follows the reasoning, not just the diff.

## Budget
- Spent: <turns / tokens / $> · Cap: <…>
