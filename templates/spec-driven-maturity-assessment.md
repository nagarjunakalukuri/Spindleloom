# Spec Driven Development — Maturity Assessment

| Field | Value |
|---|---|
| Team / Project | <name> |
| Assessor | <name> |
| Date | <date> |
| Current rung | <1 Spec-first / 2 Spec-anchored / 3 Spec-as-source> |

## The ladder

| Rung | Name | In one line |
|---|---|---|
| 1 | Spec-first | Loose instructions in CLAUDE.md / AGENTS.md / .cursorrules. |
| 2 | Spec-anchored | A living, versioned spec updated before code and reviewed in PRs. |
| 3 | Spec-as-source | The spec is the source of truth; code is a generated artifact. |

Higher is not automatically better — pick the rung that matches your codebase size, change velocity, and process tolerance.

## Scorecard

Rate each signal: ❌ none · 🟡 partial · ✅ solid.

| # | Signal | Score | Evidence / notes |
|---|---|---|---|
| 1 | A spec exists (beyond ad-hoc comments) | | |
| 2 | The spec is structured (intent, behavior, constraints) not just loose rules | | |
| 3 | The spec is updated *before* code changes | | |
| 4 | The spec is versioned and reviewed in PRs | | |
| 5 | Specs capture *why* (decisions + rationale), not only *what* | | |
| 6 | The AI tool is explicitly pointed at the spec as ground truth | | |
| 7 | Drift (code diverging from intent) is actively detected | | |
| 8 | Non-goals / out-of-scope are written down | | |
| 9 | Code can be checked against — or regenerated from — the spec | | |

## Interpretation

- Mostly ❌ on 1–2 → **Rung 1 (Spec-first).**
- ✅ on 1–6, some 🟡 on 7 → **Rung 2 (Spec-anchored).**
- ✅ on 7–9 with reliable regeneration → **Rung 3 (Spec-as-source).**

## Top level-up actions

| # | Action | Owner | Target date |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## Notes / risks

<Specification drift seen recently, technical-debt hotspots, where AI output diverged from intent.>
