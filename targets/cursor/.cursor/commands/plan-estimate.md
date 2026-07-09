---
description: Size a backlog with story points (Planning Poker or solo mode) — reference story, modified Fibonacci, split/spike flags, velocity & capacity math.
argument-hint: [path-to-backlog.md]
---

Run **estimation-facilitator** on the backlog at **$1** (default: the `backlog.md` in context). See `agents/estimation-facilitator.md`.

1. Establish/confirm the **reference story** (the team's "1" or "2"); estimate everything relative to it on modified Fibonacci.
2. Solo mode: points + one-line rationale + confidence per story. With a team: run Planning Poker (private pick → simultaneous reveal → high/low explain → re-vote).
3. Flag ≥13 and "?" items back to `backlog-manager` to split or spike — never force a number.
4. Re-estimation is **mandatory** for any item `solution-recon` re-scoped or a blocker split — stale points corrupt capacity math.
5. Compute velocity from history (or forecast conservatively with none) and hand capacity to `sprint-planner`.
