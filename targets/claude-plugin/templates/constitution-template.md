# Project Constitution — <Project Name>

| Field | Value |
|---|---|
| Owner | <eng lead / architect> |
| Version | v1.0 |
| Status | Draft / Active / Superseded |
| Last updated | <YYYY-MM-DD> |

> The durable, AI-read-first source of project law. Every contributor — human or AI agent — reads this before changing anything. It holds *standing principles*, not feature details; per-feature behavior lives in the funnel docs (PRD/FRD/SRS). Promote scattered guardrails here; **link** to `coding-standards` and the `ai-orchestration-policy` rather than copying them. The constitution is the rung-1→rung-2 anchor in the `spec-driven-dev` maturity ladder.

## Purpose & intent
<What this system is for and the outcomes it must achieve. The "why" that should outlive any individual feature.>

## Non-negotiable principles
Numbered, each a *testable* rule (apply the "the system shall" discipline from the `requirement-quality` standard — no vague adjectives). These are what an AI agent must never violate.

1. <e.g. All external errors use the shape `{code, message}` with codes from the registry.>
2. <e.g. No PII in logs or analytics events.>
3. <e.g. Every write path is idempotent.>

## Architectural boundaries
<Key components and the rules about how they may interact (which layers may call which). Links to the SDD for detail.>

## Conventions
<Code style, naming, error handling, testing bar.> See `coding-standards` for the enforceable detail — do not duplicate it here.

## AI-agent operating rules
<What AI coding agents may do autonomously vs. what needs human-in-the-loop, by risk.> See the `ai-orchestration-policy` for the full delegation matrix.

1. Read the relevant `/specs/<feature>` (or FRD/SRS) before changing code.
2. If intent is unclear or a spec is stale, update the spec first and flag it — don't guess.
3. Keep every change traceable to a principle here or a requirement upstream.

## Non-goals
- <What this project deliberately does not do — guards against scope creep and "helpful" agents adding unwanted behavior.>

## Amendment process
The constitution is versioned and PR-reviewed like code. Changing a **principle** (not a typo) bumps the version and requires an ADR (`adr-writer`) recording the why and the rejected alternatives. Supersede, don't silently rewrite — per the change-control & baseline model in `project_guides/BEST-PRACTICES.md`.
