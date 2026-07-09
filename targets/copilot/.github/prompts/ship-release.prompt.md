---
description: Plan and gate a release — evidence-based go/no-go from QA sign-off, CI status, and open risks; rollout plan and release notes.
argument-hint: [plan|go-no-go|notes]
---

Run **release-manager**. Mode: **$1** (default: `go-no-go`). See `agents/release-manager.md`.

## plan
Scope the release (what ships, what doesn't), the rollout strategy (staged/canary + rollback trigger), owners, and the date; save the release plan.

## go-no-go
First run `python hooks/validate_gates.py . --release` — it computes the sign-off AND from `.spindleloom/signoffs/*.md` and names every missing/unevidenced gate; exit 1 is an automatic **no-go**. Then walk the gate with **evidence, not vibes**: QA sign-off (suite-level results + open S1/S2), CI green on the release candidate, review/security verdicts in, accessibility/performance sign-offs where applicable, open RAID risks accepted by name. Any unevidenced gate = **no-go with the missing item named** — an unevidenced sign-off is a forged gate.

## notes
Write the release notes from shipped PBIs (user-visible language, traced IDs), and hand post-release watch items to `sre`/`incident-responder`.
