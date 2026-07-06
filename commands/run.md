---
description: Drive a multi-agent run end-to-end against a goal — set up the run-state + stop contract, then propose and (on confirmation) dispatch the next runnable agent through the fleet.
argument-hint: [objective | "continue"]
---

Drive a fleet run for **$1** using the `run-orchestrator` agent.

1. If **$1** is `continue` (or blank with an existing run), read `.shipwright/run-state.json` (+ `RUN.md`) and resume. Otherwise start a new run: instantiate `templates/run-state-template.md`, capture the **four-part stop contract** (end state · evidence · constraints · budget), and pick the entry point from the objective — greenfield → `doc-strategy-advisor`; brownfield change → `solution-recon`; a single ticket → `/pbi-next`; production incident → `incident-responder`; AI-guardrail setup → `ai-orchestrator`.
2. Compute the **runnable** agent(s) from the contract graph (`agents/INDEX.md` + each agent's `upstream`/`downstream`/`gate`): an agent runs when **all its required upstreams are `done` and its gate (DoR/DoD) has passed**; convergent agents (e.g. `backlog-manager`) wait for their join; independent branches may run in parallel.
3. **Propose** the next agent(s) + the context to hand them, and **wait for confirmation** before dispatching (autonomy rung 1–2; never auto-dispatch to protected paths). In the build phase use `/pbi-next` type-routing (Story → developer, Bug → `debugger`, Spike → `solution-recon`, Decision → `architect`); a build step is not `done` until `change-verifier` returns PASS.
4. **Record** progress in the run-state (status, produced-artifact pointers, decision log) and repeat until the **stop contract is met**, the **budget is spent**, or the run is **blocked** (surface what's missing).

Do not produce the artifacts yourself — dispatch the specialists. Keep the run-state the single source of truth and reset context between steps. See `agents/run-orchestrator.md` and the `agentic-loop-design` skill.
