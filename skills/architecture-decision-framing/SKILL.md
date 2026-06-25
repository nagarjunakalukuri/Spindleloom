---
name: architecture-decision-framing
description: Turn one forced, hard-to-reverse technical choice into an evidence-grounded recommendation — frame the real options (including do-nothing), weigh them on cost / risk / reversibility / blast-radius / precedent-fit, recommend one, and state the strongest objection to it. Use when weighing extend-vs-rebuild, sync-vs-async, build-vs-buy, a data store, or an auth model. Output maps 1:1 to an ADR. Consumed by architect, adr-writer, rfc, sdd-writer, and tsd-writer.
---

# Framing an architecture decision — recommend, don't survey

A list of options with no call is a non-answer. The job is to make *one* forced choice decidable.

## Scope it
- **One decision per analysis.** If you're weighing several, write several. The output maps 1:1 to an ADR.
- **Architecturally significant only** — costly-to-reverse or structure-shaping (topology, sync vs async, extend-vs-new-component, data store, auth model, build-vs-buy, a major dependency). Routine choices get a code comment, not an analysis.

## Ground every claim in reality
Pull the facts from the code (or `solution-recon`): what exists, the established pattern, the real blast radius. An option's "con" must cite where it bites (`file:line`). Unverified → say "unverified", don't assert.

## Frame the real options
- Always include **do-nothing / status-quo** as a baseline.
- 2–4 genuine options — not one real choice plus strawmen.
- For each: how it works in one line, what it costs to build, and what it costs *later* (operate, change, reverse).

## Weigh on the axes that actually decide it
Cost-to-build · **reversibility** · blast-radius · risk · precedent-fit (does it mirror an existing sibling?) · operability. **Name the axis that dominates** and why — most decisions turn on one or two, not all.

## Recommend + the strongest objection
End with **one** recommendation stated plainly, the trigger that would change it, and the **strongest honest objection** to your own pick (so the reviewer/ADR sees the trade-off, not a sales pitch).

## Hand-off
The analysis feeds `adr-writer` (records the decision + rationale, immutably) and, when it needs socializing first, `rfc` (opens it for comment). You analyze and recommend; the ADR is the record.

## Smells
- Options that are all-strawmen-but-one → not a real comparison.
- No reversibility axis → the most important question for a hard-to-undo choice is unasked.
- A recommendation with no stated objection → likely motivated reasoning.
