# Release <version> — <Project>

| Field | Value |
|---|---|
| Target date | <date> |
| Approver | <Director / PM> |
| Rollout | canary / blue-green / phased |
| Status | Planned / Go / No-go / Shipped |

## Scope

<PBIs / epics included; link the sprint(s).>

## Go / No-Go checklist

- [ ] QA sign-off received (qa-tester): P0/P1 pass, no open S1/S2 unmitigated
- [ ] CI/CD pipeline green; artifact built & scanned
- [ ] DoD met for all included items
- [ ] Open risks/issues (RAID) reviewed; none blocking
- [ ] Rollback plan tested and ready
- [ ] Stakeholders informed; support/on-call ready
- [ ] Migration/data steps (if any) rehearsed

**Decision:** Go / No-go — <reasons / residual risk>

## Rollout & rollback

<stages, health checks, and the exact rollback procedure>

## Release notes

**For users:** New: … · Improved: … · Fixed: …

**Internal:** changelog, migration steps, known issues.
