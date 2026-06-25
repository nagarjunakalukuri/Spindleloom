# Analytics & Instrumentation Spec — <Feature>

| Field | Value |
|---|---|
| Owner | <product analyst / PM> |
| Related | <PRD success metrics / FRD> |
| Status | Draft / Active |
| Last updated | <date> |

> Makes the PRD's success metrics measurable. Every event ties to a metric or a decision. Event schema is a versioned contract; keep PII out. Use `PA-<AREA>-<NUM>` IDs.

## Success metrics (from PRD)
| PA ID | Metric | Definition (numerator / denominator / window / population) | PRD target |
|---|---|---|---|
| PA-<AREA>-001 | orders/active user/week | orders ÷ active users, 7-day, active = ≥1 session | ≥ 3 |

## Tracking plan (events)
| Event | When it fires | Key properties | Feeds metric |
|---|---|---|---|
| `order_placed` | on 201 from order API | orderId, value, items | PA-…-001 |

## Funnels
```
<step> → <step> → <step>   (drop-off measured at each)
```

## Experiments (A/B)
| Hypothesis | Variant | Primary metric | Guardrail metrics | Sample/power | Stop rule |
|---|---|---|---|---|---|
| <change> raises <metric> | A / B | PA-… | latency, error rate | n, 80% power | <decision> |

## Dashboards & privacy
- Dashboards: <links/owners>
- Privacy: events carry no PII beyond <consented fields>; per the constitution's PII rule and compliance constraints.

## Loop back
<hit/miss vs PRD target → prd-writer revision or backlog follow-up>
