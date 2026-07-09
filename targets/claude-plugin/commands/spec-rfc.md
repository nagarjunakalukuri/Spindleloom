---
description: Propose a significant technical change for comment before building it — the forward-looking RFC / design-review process.
argument-hint: [create|review|close] [topic]
---

Run the **RFC (Request for Comments)** process for **$2** (topic). Mode: **$1** (default: `create`). An RFC is the proposal/debate that happens *before* building; once accepted, the decision is recorded as an ADR and the SDD is updated. See `agents/rfc-facilitator.md`.

## create
1. Confirm the change is RFC-worthy (significant + affects others). If it's routine, suggest a PR note; if the decision is already made, route to `/spec-adr`.
2. Find the next number: scan `docs/rfc/` for the highest `NNNN` and increment (zero-padded).
3. Draft from `templates/rfc-template.md` — fill Summary, Problem & context (cite SRS/SDD), Proposal, real Alternatives (incl. "do nothing"), Impact, Open questions. Set deciders and a "Comments by" close date; status `Draft`.
4. Save as `docs/rfc/NNNN-kebab-case-title.md`.

## review
Facilitate: check it's a single significant change with honest alternatives, concrete impact/migration, a recommendation, a decider, and a close date. Summarize the open questions reviewers should weigh in on. Read-only.

## close
Set the final status (Accepted / Rejected / Deferred), record the decision and key dissent, then **hand off**: open an ADR via `adr-writer` (`/spec-adr`) to record the decision immutably, and flag the SDD section (`sdd-writer`) that must change. The ADR — not the RFC — is the durable record.
