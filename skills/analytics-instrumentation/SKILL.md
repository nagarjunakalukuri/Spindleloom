---
name: analytics-instrumentation
description: Instrument product metrics so PRD success claims become measurable — an event taxonomy that survives renames, funnel design, guardrail metrics, PII-safe payloads, and A/B tests sized honestly. Use when specifying events for a feature, checking whether a shipped feature moved its metric, or designing an experiment. Consumed by product-analytics; closes the PRD's build→measure loop and feeds follow-up PBIs via backlog-manager.
---

# Analytics instrumentation — measure what the PRD promised

## Start from the metric, not the event

The PRD names a success metric ("on-time refill 41%→60%"). Work backwards: what user
actions compose it, what's the denominator, over what window? An event spec that doesn't
ladder up to a PRD metric is logging, not instrumentation.

## Event taxonomy that survives

- **`object_action` naming** (`refill_requested`, `reminder_sent`), past tense, snake_case —
  never UI-coupled names (`blue_button_clicked` dies at the next redesign).
- **Properties over event proliferation**: one `refill_requested` with `channel: push|sms`
  beats two events; you can slice properties, you can't merge events retroactively.
- Every event carries the **standard envelope**: user/session ids (pseudonymous), timestamp,
  app version, and the feature-flag/experiment cohort — cohort at event time, not joined later.
- **Version the spec**: events are a contract (`PA-<AREA>-<NUM>` IDs in the RTM); changing a
  property's meaning is a breaking change with a migration note, same as an API.

## Funnels and guardrails

- Define the funnel steps *before* launch (reminder_sent → opened → refill_requested →
  approved → dispensed) with expected drop-off; the first week's job is validating the
  instrumentation, not celebrating the number.
- Pair every success metric with a **guardrail** (opt-outs, support tickets, latency) —
  a metric that can only be read as good is a vanity metric.

## PII safety

No PHI/PII in event payloads — ids are pseudonymous, free-text fields are banned from
events (that's where emails leak), and the property list is reviewed like code. The
security-reviewer's data-handling rules apply to telemetry too.

## Experiments, honestly

- One primary metric per test, sized *before* launch (minimum detectable effect vs traffic —
  underpowered tests produce confident noise); guardrails monitored alongside.
- Cohort assignment is sticky and logged on every event; peeking rules agreed upfront.
- A missed PRD metric is a **finding, not a failure to hide**: route it to backlog-manager
  as a follow-up PBI (the analytics→backlog edge exists for exactly this).

## Anti-patterns

| Smell | Fix |
|---|---|
| Events named after UI widgets | object_action; the UI will change, the behavior won't |
| Metric defined after launch | pre-registered metric + denominator + window |
| Success metric with no guardrail | pair it, or you'll ship regressions proudly |
| "We'll join cohorts later" | cohort on the event, at event time |
