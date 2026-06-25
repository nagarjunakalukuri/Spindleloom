# Technical-Debt Register — <project>

| Field | Value |
|---|---|
| Owner | <role / name> |
| Status | Living |
| Last updated | <YYYY-MM-DD> |


- **Owner:** <architect / eng lead>
- **Last groomed:** <YYYY-MM-DD>

> A living, *owned* list of what's rotting and why — so debt is **negotiable with the PM**, not anecdotal. Prioritize by **impact × interest** (how fast it worsens) against **effort**. Decided items get promoted to the backlog; accepting debt is a valid, recorded decision. Fed by postmortems, retros, and code reviews.

## Register
| ID | Description | Location | Type | Impact | Interest (worsening) | Effort | Owner | Decision | Backlog link |
|---|---|---|---|---|---|---|---|---|---|
| DEBT-001 | <what & why it's debt> | <service/file/module> | design / code / test / infra / doc | <cost now> | <quantified rate, e.g. +20 ms/release> | S / M / L | <name> | pay now / schedule / accept / monitor | PBI-… |

## Decision key
- **pay now** — promote to current backlog as a PBI.
- **schedule** — promote to a future sprint/epic.
- **accept** — interest is low enough to live with; recorded so it isn't re-raised.
- **monitor** — re-score interest at next grooming; promote if it worsens.

## PM-negotiation view (sorted by impact × interest vs effort)
<Top items the architect/lead takes to the PM to negotiate paydown capacity. For multiple teams, group by owning team/service to show where rot concentrates.>

## Sources this period
<Where new items came from — postmortems, retros, code reviews — so the feedback loop is visible.>
