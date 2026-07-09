---
description: Independently verify a change against its acceptance criteria by RUNNING it — build, tests, lint, exercise each criterion; PASS/FAIL verdict with evidence.
argument-hint: [pbi-or-change]
---

Run **change-verifier** on **$1** (a PBI, branch, or described change). See `agents/change-verifier.md`. Maker ≠ checker: verify work you did not write; never patch it (red goes to `debugger`).

1. **Impacted-test discovery first**: grep every changed symbol across ALL test dirs; the blast radius defines the suite list, not the changed files alone.
2. Build; run the impacted suites + lint. Record exact commands and the **suite-level summary line** — per-file "implemented" notes are not evidence.
3. Exercise each acceptance criterion **by execution** (run the path, hit the endpoint, render the screen) and fill the AC coverage matrix — no uncovered or red AC in a PASS.
4. Name anything you **could not verify** (unreachable suite, missing env) explicitly.
5. Verdict: PASS → `pr-author`/`code-reviewer`; FAIL → `debugger` with the failing evidence.
