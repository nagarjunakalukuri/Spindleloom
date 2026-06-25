# Product Backlog — <Project>

| Field | Value |
|---|---|
| Product Owner | <name> |
| Status | Living |
| Last refined | <YYYY-MM-DD> |
| Source | <PRD/FRD links> |

## Epics

| Epic | Goal | Source (PRD/FRD) |
|---|---|---|
| <EPIC> | <goal> | <PRD #> |

## Backlog (ordered)

| Rank | PBI ID | Type | Story / item | Acceptance criteria | Priority | Est. | Deps | Source | Ready? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PBI-<EPIC>-001 | Story | As a <persona>, I want <goal> so that <benefit> | Given <context>, when <action>, then <result> | Must | <pts> | — | <FRD ID> | ✅ |
| 2 | PBI-<EPIC>-002 | Story | | | Should | | | | ❌ |

> Types: Story/Code · Bug · Spike · **Decision** (→ architect→adr-writer) · **Docs** · Task. Priority: MoSCoW (Must/Should/Could/Won't). Ready? = meets Definition of Ready. Route by Type — see backlog-manager "PBI types & routing".
>
> **Field map → work item** (per `backlog-manager` *Tracker sync contract*): Story/item → **Description** · Acceptance criteria → the **Acceptance Criteria field** (never Description) · Priority → Priority · Est. → Story Points · Type → Work Item Type · parent epic → Parent · Sprint → Iteration (or a `sprint-N` tag). **Tasks live on the board only** — shape in `task-template.md`.

## Notes

<Splits made, parent epics, open questions for refinement.>
