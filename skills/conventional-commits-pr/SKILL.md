---
name: conventional-commits-pr
description: Write Conventional-Commit messages and reviewer-first pull-request descriptions — `type(scope): imperative summary`, one logical change per commit, link the PBI/ADR, lead the PR with what / why / how-to-test, carry provenance, and split oversized PRs. Use when committing, opening a PR, or setting a team's commit/PR conventions. Consumed by pr-author, backend-developer, frontend-developer, and dev-onboarding.
---

# Conventional commits & reviewer-first PRs

A good PR tells a reviewer *what changed, why, and how to verify* in 30 seconds. A good commit history is a readable, machine-parseable record.

## Conventional Commits
```
type(scope): imperative summary   (PBI-CHECKOUT-007)

Why: one or two lines of intent — not what the diff already shows.
```
- **types:** `feat` · `fix` · `chore` · `refactor` · `docs` · `test` · `perf` · `build` · `ci`.
- **Imperative mood** ("add", not "added"). **One logical change per commit.** Reference the PBI.
- `feat!:` or a `BREAKING CHANGE:` footer for anything that breaks a contract.

## The PR description (reviewer-first)
Lead with what the reviewer needs, in this order:
1. **What & why** — one paragraph. The diff shows *how*; you supply the intent.
2. **How to test** — concrete steps / commands; the acceptance criteria become the checklist.
3. **Risk & scope** — blast radius, what you did *not* change, follow-ups.
4. **Provenance** — assumptions made, alternatives rejected, and anything left **unverified** (carry the `change-verifier` verdict). This is what fights comprehension debt — the next reader follows the reasoning, not just the diff.
5. **Links** — the PBI/story and any ADR.

## Right-size it
Small PRs review faster and break less. If the diff spans several concerns, **say so and recommend splitting**. A giant unexplained PR stalls in review.

## Honest, not salesy
State trade-offs, known gaps, and follow-ups plainly. A PR that oversells hides the risk the reviewer needs to see.

## Smells
- One-word or empty PR body → the reviewer reverse-engineers intent (slow, error-prone).
- Many unrelated changes in one commit/PR → unreviewable, un-revertable.
- No PBI link / no "how to test" → breaks traceability and slows review.
