---
description: Assess a spec set — which docs exist, coverage gaps, and drift from the code/intent.
argument-hint: [path-to-spec-folder]
---

Assess the health of the spec set at **$1** (default: the spec folder in context).

Report, concisely:
1. **Funnel coverage** — which of MRD/BRD/PRD/FRD/SRS/SDD/TSD/backlog/RTM exist; which expected-for-this-tier docs are missing.
2. **Traceability gaps** — read the RTM and the spec docs; list any FRD/SRS Req-ID that has no downstream design or PBI (uncovered scope), and any PBI with no upstream trace (scope creep). Run the `traceability-rtm` skill if available.
3. **Requirement quality** — sample the requirements and flag any that fail the ISO 29148/INCOSE checklist (vague adjectives, multiple obligations, untestable). Run the `requirement-quality` skill if available.
4. **Drift** — compare the spec's stated behavior/intent against the current code where determinable; flag where code diverges from spec or the spec is stale (cite files). Do not assume code is correct — the spec is the reference.
5. **Status & ownership** — each doc's Status field and owner; flag any doc with no owner or a stale "Last updated".

Output a short table: doc · exists? · owner · status · top issue. End with the 3 highest-leverage fixes. Read-only — propose, don't edit.
