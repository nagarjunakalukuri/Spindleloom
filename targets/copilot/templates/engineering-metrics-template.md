# Engineering Delivery Metrics — <Project> — <period>

| Field | Value |
|---|---|
| Owner | <eng lead> |
| Period | <e.g. Sprint 7 / 2026-06-01..06-14> |
| Source | <CI/CD dashboard, board, incident log> |

> Operationalizes the measurement guidance in `knowledge_hub/LOOPWRIGHT.md`: DORA for *how fast and safe* the outer loop runs, cycle-time breakdown for *where it stalls*, and a SPACE/DevEx pulse so speed gains aren't burning the team. Feeds the `status-reporter` Delivery-metrics table.

## DORA four keys
| Metric | This period | Prev | Trend | Target / band |
|---|---|---|---|---|
| Deployment frequency | | | ↑/→/↓ | (Elite: on-demand; High: daily–weekly) |
| Lead time for changes | | | | (Elite: < 1 day) |
| Change-failure rate | | | | (Elite: 0–15%) |
| MTTR (time to restore) | | | | (Elite: < 1 hour) |

## Flow / cycle time
Break cycle time into segments to find the bottleneck (the biggest chunk is usually *wait* time, not coding).
| Segment | Time | Note |
|---|---|---|
| Coding (start → PR open) | | |
| Review (PR open → approved) | | review SLA? |
| CI (approved → green) | | cheap-checks-first? |
| Deploy (merged → prod) | | progressive rollout? |
| **Total cycle time** | | created → delivered |

## Health pulse (SPACE / DevEx) — optional
| Signal | Reading | Note |
|---|---|---|
| Satisfaction / flow | <survey> | are fast-loop gains costing burnout? |
| Build/test feedback (inner loop) | <local time> | < ~10 s keeps flow |
| Flaky-test rate | <%> | untrustworthy feedback breaks the loop |

## Bottleneck & action
- **Biggest stall this period:** <segment + why>
- **One loop to shorten next period:** <action — ties to a retro item or `pipeline-engineer`/`code-reviewer` change>
