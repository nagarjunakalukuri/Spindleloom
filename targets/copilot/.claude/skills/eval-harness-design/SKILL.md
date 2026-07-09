---
name: eval-harness-design
description: Build the eval harness for a shipped AI/LLM feature — a golden dataset, the right scorer (exact / heuristic / LLM-as-judge with a calibrated rubric), thresholds, and a regression-eval CI gate. Use when testing an AI feature, setting up LLM-as-judge, or gating a model/prompt change. Unit tests don't catch model regressions; this does. Consumed by ai-eval, ai-orchestrator, pipeline-engineer, and change-verifier.
---

# Eval-harness design — gate AI features on evals, not unit tests

A model-backed feature can pass every unit test and still regress (worse answers, new hallucinations). Evals are its test suite. Build one like this:

## Golden dataset
- Cases that represent **real usage** + the **failure modes you care about** (not just easy ones). Include adversarial / edge / out-of-scope inputs.
- Each case: input, expected output *or* a checkable property, and the requirement/PBI it ties to.
- **Grow it from escapes:** every production miss becomes a new golden case (the dataset compounds).
- Version it; freeze a baseline so you can diff scores across model/prompt changes.

## Pick the scorer by what "good" means
- **Exact / structural** — deterministic outputs (JSON shape, a classification label, a number). Cheapest; use when you can.
- **Heuristic** — regex / contains / ROUGE-style overlap for semi-structured text.
- **LLM-as-judge** — open-ended quality (helpfulness, groundedness, tone). Use only when the above can't, and **calibrate it**: a written rubric with a scale, a few human-labeled anchors, and a check that the judge agrees with humans before you trust it. Pin the judge model/prompt; a drifting judge invalidates the trend.

## Thresholds & the CI gate
- Set a pass bar per metric (e.g. groundedness ≥ 0.95 on the core set) and a **no-regression** rule vs. the frozen baseline.
- Wire it as a CI gate (with `pipeline-engineer`): a model/prompt change that drops a metric below bar fails the build, same as a red test.
- Separate **core** (must-pass, blocks merge) from **exploratory** (tracked, doesn't block).

## Cover the failure modes, not just accuracy
Hallucination / fabrication, prompt-injection & jailbreak, PII leakage, refusal of valid requests, latency & cost per call. A high accuracy score with an open injection hole is not "good enough."

## Review smells
- Only happy-path cases → add adversarial/edge.
- An uncalibrated LLM-judge → the score is noise; anchor it to human labels.
- No baseline → you can measure a run but not a *regression*.
- The judge uses the same model as the feature → bias; use a different one.
