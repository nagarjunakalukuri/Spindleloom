---
name: ux-design-method
description: The product-design method — flows before screens, every state designed (loading/empty/error/partial), Nielsen-heuristic self-review, design-token discipline, and a buildable handoff spec. Use when designing UX/UI for a feature, reviewing a design for completeness, or when shipped UI keeps needing "one more state". Consumed by ux-ui-designer; pairs with the frontend-developer (who implements it) and accessibility-auditor (who verifies it).
---

# UX design method — flows, states, system, handoff

## 1 · Flows before screens

Map the end-to-end user flow first: entry point → steps → success, **plus the exits**
(abandon, error, back). Most UX defects are flow gaps, not visual ones. Each flow traces
to a PRD persona + goal; a screen serving no stated goal is scope creep — cut it.

## 2 · The five-state rule

Every screen ships in five states, designed explicitly, never improvised in code:
**loading · empty · error · partial · ideal**. The ideal state is the easy 20%. For each
non-ideal state: what the user sees, what they can do next, and the copy (real words, not
lorem). A design without its empty state isn't done.

## 3 · Heuristic self-review (before handoff)

Walk the ten Nielsen heuristics as a checklist — the ones that catch the most in practice:
visibility of system status (does every action acknowledge?), user control (undo/cancel/back),
error prevention over error messages, recognition over recall (visible options, not memorized
commands), and consistency with the existing design system. Record what each pass changed;
a review that changes nothing was a rubber stamp.

## 4 · Design-token discipline

Reuse before invent: type scale, color roles (semantic, not raw hex), spacing grid, and
components come from the design system. A genuinely new pattern is **flagged and defined**
(token + usage rule), not silently one-off'd — one-offs are how systems fragment. Color
alone never carries meaning (pair with icon/text — accessibility is a design input).

## 5 · The buildable handoff

The spec is done when an engineer can build and a tester can test **without asking**:
annotated wireframes/hi-fi per state, the interaction spec (what every action does —
transitions, validation, optimistic vs blocking), keyboard/focus order, and `UX-<AREA>-<NUM>`
IDs aligned to the FRD so the RTM reads through. End with the `## Digest`.

## Anti-patterns

| Smell | Fix |
|---|---|
| Screens designed, flow implied | draw the flow first; screens fall out of it |
| "We'll design the error state later" | later = the developer invents it at 6pm |
| New button style per feature | token discipline; flag-and-define or reuse |
| Spec = a picture with no interaction notes | if the tester must ask, it isn't a spec |
