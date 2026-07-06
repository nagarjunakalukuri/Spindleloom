# UX Design — <Feature>

| Field | Value |
|---|---|
| Designer | <name> |
| Related | <PRD stories / FRD IDs> |
| Status | Draft / In review / Approved |
| Last updated | <date> |

> The pre-code product design (UX **and** UI) `frontend-developer` implements: flows, screens, states, interactions, and the visual/design-system layer, traced to PRD/FRD. Use `UX-<AREA>-<NUM>` IDs aligned to the FRD AREA codes. Accessibility is designed in here (WCAG 2.1 AA intent), not deferred to QA.

## Users & jobs
| Persona (from PRD) | Job to be done | Success looks like |
|---|---|---|

## User flow(s)
For each flow: entry → steps → success, plus error/empty/edge states.
```
<entry> → <step> → <step> → <success>
   ↳ error: <state>   ↳ empty: <state>   ↳ edge: <state>
```

## Screens / wireframes
| UX ID | Screen | Purpose | Key components | Traces (PRD/FRD) |
|---|---|---|---|---|
| UX-<AREA>-001 | <screen> | <user goal> | <components / content> | PRD #, FRD-… |

<low-fidelity wireframe sketch or description per screen>

## Screen states (per screen)
- **Loading:** … · **Empty:** … · **Error:** … · **Success/Partial:** …

## Visual / UI design (hi-fi)
- **Hi-fi screens:** <links/sketches of the visual mockups for key screens, all states>
- **Visual hierarchy:** <what draws the eye first; primary vs secondary actions>
- **Type / color / spacing:** <type scale, color roles (semantic, not raw hex), spacing/grid>
- **Iconography & imagery:** <set, usage rules>

## Design system
| Token / component | Reused or new? | Notes |
|---|---|---|
| <e.g. Button/primary> | reused | |
| <new pattern> | new — defined here | spec for `frontend-developer` to implement |

## Interaction spec
<what happens on each action: transitions, validation, micro-copy intent, optimistic vs blocking>

## Accessibility intent (WCAG 2.1 AA)
- Keyboard path & focus order · contrast · input labels & errors · motion/animation considerations

## Open questions
- <gaps surfaced during design → route to prd/frd-writer>
