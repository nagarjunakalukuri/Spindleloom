---
name: requirement-elicitation
description: Interview the user one question at a time to stress-test a plan, design, or set of requirements before it is written down — surfacing gaps, contradictions, and unstated assumptions. Use before drafting or approving a BRD/PRD/FRD/SDD, when a requirement feels vague or the intent is ambiguous, or on a "interview me about this / stress-test these requirements / pressure-test the plan" request. Returns resolved decisions, open questions, and flagged assumptions ready to drop into the document and the RTM. Pairs with the brd/prd/frd-writer and rfc agents.
---

# Requirement elicitation — relentless interview before the doc

The cheapest place to fix a requirement is before it is written. This skill is the interview that extracts and stress-tests intent up front, so the document agent drafts from a shared understanding instead of guessing — and the gaps surface as flagged assumptions now, not as rework three altitudes down the funnel.

It is the elicitation front-end to `requirement-quality`: elicit first to extract and sharpen, then validate the written requirement against the 29148 checklist.

## Principles

- **One question at a time.** Wait for the answer before asking the next. A batch of questions is bewildering and gets shallow answers; a single sharp question gets a real one. (This is the deep stress-test mode — distinct from a writer agent's quick "fill the gaps" clarification batch.)
- **Walk the decision tree.** Take each branch of the plan in turn and resolve dependencies between decisions one by one — an early answer often closes or reframes a later question.
- **Recommend an answer.** For each question, offer your recommended answer and the reasoning, so the user reacts to a concrete proposal rather than a blank prompt. Disagreement is faster than invention.
- **Investigate, don't speculate.** If a question has a factual answer in the upstream document, the codebase, or the RTM, go read it instead of asking. Reserve questions for what only the human knows — intent, priority, and trade-offs.
- **Relentless, not exhaustive.** Keep going until the design holds together, then stop. The goal is a shared understanding solid enough to draft from, not every conceivable question.

## Procedure

1. Read what already exists — the upstream artifact (MRD/BRD/PRD/…), any notes, the relevant code, and the RTM. Enter the interview already knowing the answerable facts.
2. Map the open decisions into a tree: the few load-bearing choices first, their dependents below.
3. Ask one question, with your recommended answer. Wait. Incorporate the response, then re-derive which question matters next — the tree shifts as answers land.
4. When a choice is hard to reverse, surprising, and the result of a real trade-off, record it as an ADR (`/adr-new`, `adr-writer`) — see `ubiquitous-language`. Capture new or sharpened terms in the project glossary as they settle.
5. Stop when the remaining questions no longer change the shape of the thing. Hand the resolved set to the writer agent for drafting.

## Output

A short brief the document agent (or the user) drafts from:

```
Resolved decisions:
  - <decision> → <choice> (why) [ADR-NNNN if recorded]
Open questions:
  - <question still owned by a human> (owner)
Assumptions to flag:
  - <assumed, not confirmed — to verify or mark in the doc>
```

Each resolved decision is a requirement-in-waiting; each open question is a row for the RAID log or the doc's "Open questions" table; each assumption is something the writer agent must flag rather than silently bake in.

## Tie-in
Sits in front of the requirements funnel: the brd/prd/frd-writer agents elicit intent, then draft and run `requirement-quality` on the result. `ubiquitous-language` runs alongside to capture the vocabulary the interview surfaces. Unresolved items flow to the `raid-log`; load-bearing decisions become ADRs via `adr-writer`.
