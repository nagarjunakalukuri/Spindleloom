# Sign-off -- <gate>

<!--
  A release sign-off token. One per release gate; the go/no-go is the AND over all of them.
  Home: .spindleloom/signoffs/[<release-id>/]<gate>.md   (release-id namespaces concurrent trains)
  Gates (the default release battery): qa, security, performance, accessibility, raid, dod
  Written by the accountable role -- by hand from this template, or with:
      sloom signoff <gate> --verdict GO --by "<name>" --evidence <path-or-note> [--release-id <id>]
  Enforced by: validate_gates.py --release [--release-id <id>]   (and sloom check in an adopter repo)
  A GO with no Evidence line is treated as a forged gate and fails the release.
-->

| Field | Value |
|---|---|
| Gate | <qa / security / performance / accessibility / raid / dod> |
| Release | <release-id, or omit for a single-train repo> |

Verdict: GO
By: <name / role>
Date: <YYYY-MM-DD>
Evidence: <link or path to the test report / scan / benchmark / audit that backs this GO>
Notes: <residual risk, waivers, or conditions -- optional>
