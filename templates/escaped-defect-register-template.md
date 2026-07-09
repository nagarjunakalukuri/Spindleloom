# Escaped-Defect Register — <Project>

| Field | Value |
|---|---|
| Owner | <QA lead / eng lead> |
| Status | Living |
| Last reviewed | <YYYY-MM-DD> |

> The test phase's self-measurement. A defect found in QA or production *escaped* every
> earlier, cheaper gate — each entry names **which gate should have caught it**, so the
> gates learn instead of the same class escaping twice. Fed by `qa-tester` (QA escapes)
> and `incident-responder` (production escapes); reviewed in the retro; trends route to
> the owning gate agent (`test-author` / `change-verifier` / `test-plan-writer` /
> `code-reviewer` / `pipeline-engineer`). Sibling of `flaky-test-register-template.md`.

## Register

| ID | Defect (link BUG-/INC-) | Found in | Should have been caught by | Why it escaped | Gate fix (owner) | Status |
|---|---|---|---|---|---|---|
| ESC-001 | <BUG-042 cart total wrong> | QA / prod | unit test (`test-author`) / verifier AC matrix (`change-verifier`) / test plan case (`test-plan-writer`) / review (`code-reviewer`) / CI gate (`pipeline-engineer`) | <missing boundary case; mock hid contract; AC never covered it> | <the new test/check added, with link> (owner) | Open / Gate fixed |

## Trend (per sprint/release)

| Period | Escapes to QA | Escapes to prod | Top escaping gate | Gate fixes landed |
|---|---|---|---|---|

## Review rules

- Every S1/S2 found in QA or production gets a row **within a day** — while the "why" is fresh.
- "Should have been caught by" names ONE primary gate; ambiguity means the gates overlap badly — note that too.
- A row closes only when the **gate fix lands** (a test, a verifier rule, a CI check), not when the defect is fixed — fixing the bug without fixing the gate guarantees a sibling escape.
- The retro reads the trend table: a gate that tops the column two periods running becomes a retro action.
