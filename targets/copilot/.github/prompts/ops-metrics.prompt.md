---
description: Produce the engineering-metrics snapshot — DORA four keys + cycle-time breakdown + escaped-defect trend — from CI/board data, feeding the status report.
argument-hint: [period]
---

Run **pipeline-engineer** in metrics mode for period **$1** (default: current sprint). Fill `templates/engineering-metrics-template.md`. This document previously had two consumers (`status-reporter`, retros) and no producer — the pipeline owner produces it because the pipeline holds the data.

1. **DORA four keys** from CI/deploy history: deployment frequency, lead time for changes, change-failure rate, MTTR. Cite the source (pipeline runs, board queries) per number — no hand-waved figures.
2. **Cycle-time breakdown** from the board: coding / review-wait / CI / deploy segments — name the stall.
3. **Quality trend**: escaped-defect counts from the escaped-defect register, flake rate from the flaky-test register.
4. Save as the period's engineering-metrics doc; hand to `status-reporter` (its Delivery-metrics table reads this instead of re-deriving) and surface one "loop to shorten next period" for the retro.

Numbers you cannot source are marked `n/a — needs <source>`, never estimated: a made-up DORA table is worse than none.
