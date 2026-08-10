# Performance Audit — <Feature / Path>

| Field | Value |
|---|---|
| Owner | <performance engineer> |
| Related | <SRS perf NFRs / SDD> |
| Status | Draft / Optimized |
| Last updated | <date> |

> Measure first, optimize the profiled bottleneck against a budget, verify under load — behavior-preserving. Use `PERF-<AREA>-<NUM>` IDs.

## Budgets (from the SRS)
| Path | Metric | Budget | Source NFR |
|---|---|---|---|
| <e.g. menu load> | P95 latency | < 1.0 s | SR-PERF-… |
| <filter re-render> | time | < 200 ms | SR-… |
| <bundle> | gzipped size | < 200 KB | SR-… |

## Baseline (measured, before)
| Path | Metric | Now | Over budget? | How measured |
|---|---|---|---|---|

## Bottlenecks (ranked by share of total cost)
| PERF ID | Bottleneck | Where | % of cost | Type (CPU / query / memory / network / render) |
|---|---|---|---|---|
| PERF-<AREA>-001 | e.g. N+1 query | OrderService | 60% | query |

## Optimizations
| PERF ID | Change | Expected impact | Actual (re-measured) | Behavior preserved? |
|---|---|---|---|---|
| PERF-<AREA>-001 | batch query + index | −60% latency | <result> | tests green ✓ |

## Caching (if added)
- What: <…> · TTL/invalidation: <…> · staleness accepted: <…>

## Load-test verification
- Tool / scenario: <…> · target concurrency: <N> · result vs budget: <pass/fail>

## Frontend (Core Web Vitals, if applicable)
| Metric | Now | Target | After |
|---|---|---|---|
| LCP | | < 2.5 s | |
| INP | | < 200 ms | |
| CLS | | < 0.1 | |

## Verdict & recommendations
- Meets budgets? <yes/no, per path> · residual + next steps · perf-regression gate to add (CI).
