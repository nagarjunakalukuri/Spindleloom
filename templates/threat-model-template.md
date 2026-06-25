# Threat Model & Security Review — <Feature / System>

| Field | Value |
|---|---|
| Reviewer | <AppSec / security engineer> |
| Related | <SDD / SRS security NFRs> |
| Status | Draft / Reviewed |
| Last updated | <date> |

> Threat-model at design time, then gate at PR/CI. STRIDE per component; threats become testable `SEC-<AREA>-<NUM>` requirements traced to the RTM. Complements the automated SAST/dep/secret scanners run by `ci-cd-pipeline`.

## System overview & trust boundaries
<assets worth protecting; entry points; trust boundaries (client ↔ gateway ↔ services ↔ data/3rd-party)>

## STRIDE analysis
| Component / data flow | Threat (STRIDE) | Likelihood × Impact | Mitigation | Requirement |
|---|---|---|---|---|
| <component> | S/T/R/I/D/E: <threat> | M × H | <control> | SEC-<AREA>-001 |

## Security requirements (testable)
| SEC ID | Requirement ("the system shall…") | Verification |
|---|---|---|
| SEC-<AREA>-001 | The system shall enforce authz server-side on <op> | test / review |

## AppSec checklist
- [ ] Authn + authz server-side on every sensitive operation (no client-trust)
- [ ] Input validated/encoded at boundaries (injection, XSS)
- [ ] Secrets out of code; rotated; least-privilege tokens/roles
- [ ] Sensitive data encrypted in transit & at rest; PII handled per policy
- [ ] Dependencies scanned; no known criticals shipped
- [ ] Required CI security gates (SAST/DAST/dep/secret scan) enabled

## Findings & verdict
| Severity | Finding | Fix |
|---|---|---|
| 🔴/🟡/🟢 | <…> | <…> |

**Verdict:** Approve / Approve-with-fixes / Block — <one line>
