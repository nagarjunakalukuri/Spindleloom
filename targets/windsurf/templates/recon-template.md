# Solution Recon — <feature / PBI ID>

| Field | Value |
|---|---|
| Feature / PBI | <id + name> |
| Date | <YYYY-MM-DD> |
| Author | `solution-recon` |
| Repo / branch | <what was read, at what revision> |
| Verdict | READY / READY-WITH-PREREQ / BLOCKED |

> Written by `solution-recon` to `docs/specs/<feature>/recon.md`. This file is the
> **build context pack**: `backend-developer` / `frontend-developer` read it first and
> re-verify its `file:line` citations before building. Cite it, don't paste it.

## 1. Claim under test

What the spec/PBI assumes, stated as a falsifiable claim.

## 2. Ground truth — what the code actually does

| Claim | Verdict | Evidence (`file:line`) |
|---|---|---|
| <the spec says X exists> | CONFIRMED / MISSING / DIFFERENT | `path/to/file.py:42` |

Every row cites a real location. "Not found" is a finding, not a blank.

## 3. The seam

Where the change lands: the module, the extension point, the sibling to mirror, and the
contract (request/response shape, event, schema) it must honor.

## 4. Task breakdown (codebase-grounded, ordered)

1. `<new / edit path>` — what changes, which contract or pattern it follows
2. …

Ordered so each step compiles and is verifiable on its own.

## 5. Scenarios and edge cases the code already handles

What exists (so nobody rebuilds it) and what genuinely does not.

## 6. Mismatches, decisions, re-estimation

| # | Spec says | Code says | Consequence | Owner |
|---|---|---|---|---|
| 1 | | | FRD change / forced decision / prereq | `frd-writer` / `architect` / `backlog-manager` |

If the build shape shifts (FE-only -> backend-first, net-new -> blocked, or a prereq
appears) the original estimate is stale — name the affected PBIs and hand to
`estimation-facilitator`.

## 7. Open flags

Upstream gaps this recon cannot fix itself, in the machine-readable form so `sloom flags`
routes them:

- `FLAG(<owner-agent>): <what is missing or contradictory>`
