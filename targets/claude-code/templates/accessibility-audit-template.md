# Accessibility Audit — <Feature / Release>

| Field | Value |
|---|---|
| Auditor | <name> |
| Standard | WCAG 2.1 AA |
| Related | <UX design / FRD / build> |
| Status | Draft / Signed off |
| Last updated | <date> |

> Independent verification + sign-off gate. Findings cite the specific WCAG success criterion (POUR). Manual checks (keyboard, screen reader, contrast, reflow) — not an automated scan alone. Use `A11Y-<AREA>-<NUM>` IDs.

## Scope tested
<screens / flows / components; assistive tech & tools used (e.g. NVDA, VoiceOver, axe)>

## Findings
| A11Y ID | Screen / element | WCAG criterion | Severity | Issue | Fix |
|---|---|---|---|---|---|
| A11Y-<AREA>-001 | <…> | 2.1.1 Keyboard | 🔴 Blocker | <keyboard trap> | <fix> |
| A11Y-<AREA>-002 | <…> | 1.4.3 Contrast | 🟡 | <ratio 3.1:1> | <raise to ≥4.5:1> |

Severity: 🔴 blocks a task · 🟡 degrades · 🟢 minor.

## Manual check summary (POUR)
- **Perceivable:** contrast, text alternatives, captions, reflow at 200%
- **Operable:** keyboard path, focus order/visible, no traps, target size
- **Understandable:** labels, error identification/suggestion, consistent nav
- **Robust:** valid roles/names/states (ARIA), works with screen readers

## Conformance verdict & sign-off
- **Level:** meets / partially meets **WCAG 2.1 AA**
- **Residual gaps:** <open non-blockers + plan>
- **Sign-off:** Go / No-go for release — <auditor, date>
