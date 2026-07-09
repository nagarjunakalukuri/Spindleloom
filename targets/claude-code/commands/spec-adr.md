---
description: Record a new Architecture Decision Record using the next sequential number.
argument-hint: <short decision title>
---

Create a new ADR for the decision: **$ARGUMENTS**.

1. Confirm it's architecturally significant (costly to reverse or shapes structure). If it's a routine implementation choice, say so and suggest a code comment / PR note instead — don't create an ADR.
2. Scan the ADR location (`adr/`, `docs/adr/`, or the spec folder) for the highest existing `NNNN` and increment (zero-padded).
3. Gather: the forces/problem that triggered it, the constraints, and the options on the table — ask only for what's missing.
4. Write it with the `adr-writer` Nygard template: Status (default Proposed unless confirmed Accepted), Context, Decision ("We will …"), Alternatives considered (with why-not), Consequences (including the negative ones).
5. Save as `adr-NNNN-kebab-title.md` and add a row to the RTM/decision index.

One decision per file, ~one page. Never edit an accepted ADR's body later — supersede it with a new one.
