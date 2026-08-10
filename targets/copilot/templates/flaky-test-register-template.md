# Flaky-Test Register

| Field | Value |
|---|---|
| Owner | <QA / SDET> |
| Last reviewed | <date> |

## Quarantined / suspect tests

| Test | First seen | Suspected cause | Status | Owner | Due |
|---|---|---|---|---|---|
| login_e2e | <date> | race on async redirect | quarantined | @dev | <date> |

> Causes: timing/race · test order / shared state · real clock · network/external · non-deterministic data · resource leak.

## Health

- **Flake rate:** <X% of runs> (trend ↑ / → / ↓)
- **Quarantine debt:** <count parked beyond target>

> Before labelling "flaky", rule out a real intermittent product bug → hand to `debugger`.
