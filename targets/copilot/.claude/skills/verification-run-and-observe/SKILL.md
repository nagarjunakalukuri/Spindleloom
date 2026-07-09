---
name: verification-run-and-observe
description: Prove a change works by running it and observing real behavior — not by asserting it does. Build, run the changed tests and the linter, exercise the changed path (start the app / hit the endpoint / render the screen), read the actual output, and iterate to green before handing off. Use whenever you write or fix code or tests. Pairs with the test-design skill and the debugger agent.
---

# Verification — run it, observe it, iterate to green

In an AI-driven loop, **verification is the bottleneck, not authoring.** Writing code is cheap; the expensive failure is handing off code that was never run. This skill is the "observe" half of plan → edit → **run → observe** → fix. The rule: *the running program is the source of truth, never your reading of the source.*

## Resolve the toolchain/runner first
Before any command, resolve how *this* project runs — don't assume a bare `python`/`node`/`go` is on PATH (virtual environments and version managers aren't auto-activated, least of all on Windows). If a project `CLAUDE.md` or `dev-onboarding` documents the incantation, follow it exactly; otherwise detect it, **resolve once, and reuse the resolved command for the whole run** — never re-detect per command.

*Worked example (Python):* try `uv run python --version` — if the project uses `uv`, use `uv run python` / `uv run pytest` for **all** invocations; else call `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Unix/Mac) directly, and set `PYTHONPATH` per `pyproject.toml` if imports fail. Store it in a variable (`PYTHON=...`) and substitute throughout.

## The loop
1. **Build / compile.** If it doesn't build, nothing else matters — fix that first.
2. **Run the changed tests** — the narrow set first, then the package suite (per `dev-onboarding`'s per-package collect rule). Read the actual output, not the exit code alone.
3. **Run the linter / type-checker.** Green tests with red lint or type errors is not done.
4. **Exercise the changed path for real** — the step most often skipped:
   - *backend:* start the service (or a test harness) and hit the endpoint; check the status code, the body, and a log line.
   - *frontend:* render the changed screen and confirm each state (loading / empty / error / success) actually appears — not just that the component compiles.
   - *data / migration:* run the migration up **and** down on a scratch DB.
5. **Observe vs. expected.** For each acceptance criterion, state what you ran and what you saw. "A test exists" ≠ "the criterion is met."

## Iterate to green (bounded)
If any of build / tests / lint / smoke is red: read the actual error, form **one** hypothesis, fix, re-run. Repeat — but **bound it** (≈3 attempts); if a fix makes something *else* red, revert to the last green state and retry rather than stacking fixes. If it's still red, stop and hand to `debugger` with the repro and what you've already tried. Never make it pass by cheating — skipping the test, commenting it out, loosening the assertion, or catching-and-swallowing the error.

## Trust the run, not the read (anti-rationalization)
| Excuse | Reality |
|---|---|
| "It's a tiny change, it obviously works." | Tiny changes break builds constantly. Running costs seconds; a red main costs the team hours. |
| "The tests pass, so it works." | Passing tests prove the tested paths — not that the feature renders or the endpoint responds. Run the path. |
| "CI will catch it." | CI is a backstop, not your inner loop. Shifting the failure right wastes a whole cycle; catch it locally. |
| "I read the code, it's correct." | The compiler and the runtime disagree with confident readings every day. Observe, don't assume. |
| "It's red but unrelated to my change." | Either it's related (find out) or the baseline was already broken (flag it) — never hand off red as "not mine." |

## Before you hand off
Don't pass work downstream until: it **builds**, the **changed tests pass**, **lint/types are green**, and the **changed path was executed and observed** to meet its acceptance criteria. If you genuinely couldn't run something (no environment, missing secret, network blocked), say so explicitly and name what's unverified — an un-run change is an unverified change, and the next agent must know. Record *why* the change holds — what you ran, key assumptions, and anything you couldn't verify — so the next agent (and the `change-verifier`) follows the reasoning, not just the diff.
