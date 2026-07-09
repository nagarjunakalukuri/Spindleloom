---
name: agentic-loop-design
description: Design an autonomous or assistive agent loop that converges instead of drifting — reason→act→observe, a separate maker/checker split, verifiable stop conditions (end-state · evidence · constraints · budget), state-on-disk, and the autonomy ladder. Use when building or reviewing a scheduled/looping agent, a maker/checker harness, or any "run an agent against a goal" system. Consumed by ai-orchestrator (policy), ai-eval (the signal it climbs on), change-verifier, pipeline-engineer, and run-orchestrator.
---

# Agentic loop design — make the loop converge, not drift

An agent loop that runs unattended will run until it drifts, over-builds, or burns budget — unless you design the convergence in. The discipline:

## Stack the loop layers (each wraps the one below)
1. **Agent loop** — reason → act → **observe** → repeat. It must run code and see the result, not just suggest.
2. **Verification loop** — a *separate* checker grades the output against a rubric and sends it back when short (maker/checker, below).
3. **Event-driven loop** — runs on a schedule / webhook / message, not by hand.
4. **Hill-climbing loop** — production + eval results feed an analysis pass that improves the *harness itself* (prompts, skills, stop conditions). The highest-leverage layer; needs a human reviewing the harness changes it proposes.

## Verifiable stop conditions (the contract — all four, or it drifts)
- **End state** — a specific, measurable condition ("coverage for `src/billing` ≥ 90%").
- **Evidence** — concrete proof the agent must produce ("`npm test` exits 0; coverage report confirms").
- **Constraints** — explicit boundaries ("do not touch public APIs or migrations").
- **Budget** — a hard cap on turns/tokens/cost ("stop after 25 turns or $5"). The backstop when the end state proves unreachable.

## Maker/checker — never let the writer grade its own work
Split into a **maker** (drafts) and a separate **checker** (verifies against spec/tests) — ideally a different/smaller model, since the model that wrote the bug is the worst one to spot it. The checker enforces the stop condition's evidence. (In this fleet that's the `change-verifier` agent.)

## State lives on disk, not in context
The agent forgets between runs — durable state goes in a `TODO/STATUS/PLAN` spine (or issues/board), and context resets between iterations to avoid window degradation. Static conventions belong in **skills**; *changing* state belongs in **memory**.

## Keep it bounded and cheap
- Triage is one cheap pass; reserve the maker+checker (and stronger models) for items the state marks actionable.
- Cap iterations per item (~3), then escalate to a human rather than spiral.
- Gate spawning on actionable state — don't spawn implementer+verifier every tick.

## Autonomy ladder (climb one rung at a time)
0 Manual → 1 Triage (surface findings) → 2 Draft (open branches) → 3 Verified-PR (checker gates before the human) → 4 Auto-merge (low-risk categories only). Each rung adds exactly one power; keep oversight proportional to risk. Never jump to auto-merge on protected paths.

## Loop risks (sharpen as the loop improves, never ease)
- **Weak verification** → strengthen the checker and the evidence, not just the maker.
- **Comprehension debt** → budget time to *read* loop output, and keep provenance (why a change was made, what was rejected).
- **Cognitive surrender** → the loop is for recurring, verifiable work; keep direct control where your judgment is the value.
