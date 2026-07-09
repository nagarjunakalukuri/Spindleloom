---
name: ubiquitous-language
description: Establish and maintain one ubiquitous language for the project — a living glossary of canonical terms — and record the decisions that shape it as ADRs. Use when terms are overloaded or used inconsistently across documents, when a new concept needs a precise name before it spreads, or when a hard-to-reverse choice needs capturing. Returns glossary updates and, where warranted, an ADR. Pairs with the adr-writer and spec-steward agents; the proactive counterpart to cross-artifact-analysis's terminology-drift check.
---

# Ubiquitous language — one vocabulary, recorded decisions

Terminology drift is a latent bug: when the PRD says "member", the FRD says "user", and the schema says "account", a real defect is already encoded. `cross-artifact-analysis` catches that drift after it has spread across documents; this skill prevents it by maintaining one canonical vocabulary as the work happens — and by recording the decisions that shaped it so they are not re-litigated later.

Active discipline, not passive documentation: challenge imprecise terms, test them against concrete scenarios, and capture the resolution immediately.

## The glossary
- One canonical term per concept, defined in plain language, kept in a single living glossary for the project (or one glossary per bounded context for larger systems, with a top-level map pointing to each). Place it per `project_guides/INFORMATION-ARCHITECTURE.md`.
- **Glossary-only.** It holds terms and their meanings — no requirements, design, or implementation detail. Those live in the funnel docs; decisions live in ADRs.
- Create it lazily — when the first term is worth pinning, not before.

## Active practices
- **Challenge conflicts.** When the user's word clashes with the glossary, flag it on the spot rather than letting two names for one thing propagate.
- **Prefer the precise term.** Replace an overloaded word ("process", "handle") with the canonical one, and flow the change down to the docs that used the old word.
- **Test with scenarios.** Probe a concept's boundary with a concrete edge case — the boundary is where two terms turn out to be one, or one turns out to be two.
- **Verify against the source.** When stated behavior and the code (or upstream doc) disagree, surface the contradiction; the glossary records the resolved truth, not the wish.
- **Feeds the funnel.** A sharp glossary is what makes a requirement *Unambiguous* (`requirement-quality`) and keeps IDs and terms consistent across the RTM.

## When to record an ADR
Capture a decision as an ADR (`/spec-adr`, `adr-writer`) only when all three hold:
1. **Hard to reverse** — real cost to change later.
2. **Surprising without context** — a future reader would question the choice.
3. **Genuine trade-off** — real alternatives existed.

A naming choice that meets all three (e.g. modeling "order" and "fulfillment" as separate concepts) is worth an ADR; a routine term definition is not — it just goes in the glossary.

## Tie-in
The proactive half of the terminology pair with `cross-artifact-analysis` (which audits drift after the fact). ADRs route through the existing `adr-writer` / `/spec-adr` machinery and the RAID log's decisions index; `spec-steward` keeps the glossary authoritative so AI tools read one vocabulary. `requirement-elicitation` surfaces the terms this skill pins down.
