# AI Eval Plan — <AI feature>

| Field | Value |
|---|---|
| Owner | <ML/AI engineer / SDET> |
| Related | <PRD / FRD / ai-orchestration-policy> |
| Status | Draft / Active |
| Last updated | <date> |

> Evals = dataset + scorer + threshold, run as a CI gate. Grow the golden set from real failures; cover AI-specific failure modes. Version dataset + prompt + model + score together. Use `EVAL-<AREA>-<NUM>` IDs.

## What we're evaluating
| EVAL ID | Behavior / capability | Why it matters (PRD link) |
|---|---|---|
| EVAL-<AREA>-001 | <e.g. answer groundedness> | <user value / risk> |

## Golden dataset
- Source: <real cases / curated> · size: <N> · tags: happy path / edge / known-failure
- Coverage notes & gaps: <…>

## Scorers
| Behavior | Scorer | Threshold |
|---|---|---|
| structured output | exact / schema check | 100% valid |
| open-ended quality | LLM-as-judge (rubric below) | ≥ <X>/5 |
| groundedness (RAG) | faithfulness metric | ≥ <X> |
| safety (injection / PII / refusal) | rule + judge | 0 leaks; correct refusals |

**LLM-judge rubric:** <criteria> · **Calibration:** judge vs human agreement on <N> labeled cases = <%>.

## Failure modes guarded
- [ ] Hallucination / groundedness  - [ ] Prompt injection / jailbreak
- [ ] PII leakage                   - [ ] Refusal correctness  - [ ] Output-format validity

## CI regression gate
- Runs on: prompt / model / retrieval change · Pass bar: <e.g. ≥95% core set, no safety regression> · Blocks merge: yes/no
- Versioning: dataset `<v>`, prompt `<v>`, model `<id>` recorded with each run.
