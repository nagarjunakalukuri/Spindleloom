# Documentation Strategy — MedRemind (RxKart refill reminder & approval module)

*Author: `doc-strategy-advisor` · phase: discovery · 2026-07-09 · run3*
*Source of truth for scope: `brief.md` (living-spec was not routed — see FLAG).*

> **Purpose.** Recommend the *smallest* documentation set that still prevents chaos for
> this feature, name one owner per document, define where each artifact lives (system of
> record), and route each kept document to the specialist agent that writes it. This is a
> governance artifact — it produces **no Req-IDs** (rtm_column `—`); it tells the fleet
> *which* docs to produce and *who* owns them.

---

## 1 · Context (as read from `brief.md`)

| Factor | Value | Doc-strategy consequence |
|---|---|---|
| Team size | 7 (1 PM/acting-PO, 1 architect, 4 devs, 1 QA) | **Tier 1 — Lean (1–15)**, single squad |
| Squads | 1 | No architect *broadcast* layer (tech radar / RFC council) — overhead at 1 squad |
| Industry | Pharmacy chain, dispensing controlled substances | **Regulated → URS mandatory** regardless of size |
| Data | PHI in notifications; HIPAA applies | **Threat model + security review mandatory** (internet-facing + PHI) |
| Surfaces | Existing mobile app (250k MAU) + pharmacist web portal | Patient-facing UI → UX/UI design + **a11y gate**; internet-facing → security |
| Hard NFRs | ≤5 min delivery; queue <2s @ 500 concurrent; 99.9% uptime (store hours) | Constraints must be **traceable for audit → keep a lean SRS** + SRE/perf engagements |
| Tools | Azure DevOps (Boards) | PBIs live in **Azure Boards**, not per-PBI markdown |
| Cadence | 2-week sprints; first shippable slice in **3 sprints** | Delivery chain must be running from sprint 0 |

**Profile chosen: "Lean + Compliance."** Start from the Tier-1 collapse, then re-elevate
only the artifacts that HIPAA + controlled-substance auditability *force* back into
existence. We do **not** adopt the full enterprise stack — the team is too small to
sustain it, and documentation fatigue is the failure mode we are guarding against.

---

## 2 · The doc set — keep / merge / drop

Every kept doc carries a one-line justification, an owner, and the agent that writes it.

### KEEP (11 living artifacts)

| # | Document | Why it survives the cut | Owner (role) | Writer agent |
|---|---|---|---|---|
| DS-01 | **BRD** (lean, ≤2 pp) | Business why + ROI (41%→60%) + compliance mandate as a *business* constraint auditors trace to | PM / PO | `brd-writer` |
| DS-02 | **PRD** | User-facing features: reminders, one-tap refill, pharmacist queue, generic-substitution accept flow | PM / PO | `prd-writer` |
| DS-03 | **URS** | **Mandatory (regulated).** Intended use, pharmacist operator tasks, patient-safety & controlled-substance handling | QA lead (validation) | `urs-writer` |
| DS-04 | **FRD** (mostly in tickets) | Functional logic lives in Azure Boards *except* the two high-risk flows kept as explicit FRD sections (below) | PM / BA | `frd-writer` |
| DS-05 | **SRS** (lean) | Client stated hard NFRs + HIPAA/PHI + Schedule II–V rules — the *constraints/rules* layer auditors demand, traced in the RTM | Architect | `srs-writer` |
| DS-06 | **SDD/TSD** (RFC-style) | One tech-design doc: architecture + Twilio (SMS) & Firebase (push) integration + identity-verification design | Architect | `sdd-writer` (+ `tsd-writer` for the notification pipeline) |
| DS-07 | **ADR log** (append-only) | Standing decisions — PHI-minimization mechanism in SMS, Schedule II–V identity-verification approach — reviewed in PRs | Architect | `adr-writer` |
| DS-08 | **Threat model + security review** | **Mandatory.** Internet-facing + PHI + controlled substances: STRIDE, patient-vs-pharmacist authz, PHI-in-transit | Security engineer (borrowed — see gap) | `security-reviewer` |
| DS-09 | **Test plan** (traced to reqs) | Compliance + the RTM backbone make requirement→test traceability non-negotiable | QA | `test-plan-writer` |
| DS-10 | **RAID log** | Live risks (HIPAA breach, mis-dispense, Twilio deliverability), assumptions, issues, decisions | PM | `raid-keeper` |
| DS-11 | **RTM** | The traceability spine BRD→URS→PRD→FRD→SRS→SDD→test — the audit artifact for a regulated build | Architect (custodian); each writer appends | seeded by `brd-writer` |

**Two FRD sections that stay explicit (not just ticket ACs)** — they are the highest-risk
logic in the feature and auditors will read them directly:
1. **Controlled-substance exclusion** (Schedule II–V): no auto-reminder, no one-tap refill,
   extra identity verification, pharmacist-initiated contact.
2. **Generic-substitution acceptance**: patient must accept before dispensing.

### MERGE
- **FSD** (if anyone requests one) → split across `frd-writer` + `sdd-writer`; do **not** create a new format.
- **Bulk FRD** → embedded as acceptance criteria in Azure Boards work items (only the two flows above stay as prose).

### DROP
- **MRD** — RxKart has an existing 250k-MAU product and known market; no market-discovery gap. Business context lives in the BRD. (`mrd-writer` not engaged.)
- **Standalone FRD document** — folded into tickets per above.
- **Full architect direction layer** (constitution / tech radar / RFC council / tech-debt register) — a single squad under one architect does not need the *broadcast* machinery; the tech radar earns its place only at Tier 2+ (multiple squads making overlapping choices). The ADR log (DS-07) covers "decide + light RFC" at this size.
- **`ai-eval`** — the feature ships no AI/LLM capability; not needed.

---

## 3 · System-of-record model (one home per kind of thing)

| Artifact kind | Lives in | Rule |
|---|---|---|
| Specs (BRD/PRD/URS/FRD/SRS/SDD/TSD), ADRs, threat model, RTM, test plan | **Git repo** `docs/` tree (per `project_guides/STANDARD.md`) | Living Markdown, versioned, PR-reviewed. **Ban PDFs.** |
| PBIs / epics / stories / tasks | **Azure Boards** | Single source of truth for work. **Do not** mirror as per-PBI markdown — it drifts. `backlog-manager` seeds the board from PRD/FRD. |
| Project wiki (home/index, nav, links to each record) | Wiki (built by `wiki-curator`) | This agent decides *which* docs and *where*; `wiki-curator` *builds and keeps* the wiki, linking every system of record above. |
| Live risks/assumptions/issues/decisions | RAID log (repo) | `raid-keeper` maintains continuously. |

---

## 4 · Ownership & scope matrix (mapped to the real 7-person team)

| Document group | Owner (this team) | Primary consumers |
|---|---|---|
| BRD, PRD | PM / PO (1) | Architect, devs, QA, RxKart stakeholders |
| Backlog priority, RAID, status | PM / PO (1) | Whole team, leadership |
| URS, test plan, DoR/DoD gate | QA lead (1) — acts as validation lead | Devs, auditors, PM |
| SRS, SDD/TSD, ADR log, RTM custody | Architect (1) | Devs, QA, security |
| FRD detail-in-tickets, code, PRs, coding standards | Devs (4) | QA, PM |
| Threat model + security review | **borrowed security engineer** (no headcount) | Devs, `code-reviewer`, CI |
| UX/UI design | **borrowed / part-time designer** (no headcount) | Frontend devs, PM, QA |
| SLOs, runbooks, on-call | Architect proxying **SRE** (no headcount) | Devs, release |
| A11y audit gate | **borrowed accessibility auditor** (pre-GA) | UX, frontend, release |

**Staffing gap (material):** the roster has no dedicated designer, security engineer, SRE,
or BA — yet HIPAA + patient-facing UI make the security review and a11y audit
*mandatory gates*, not optional. Recommendation: **borrow or contract** these for gated
engagements rather than skipping them. Tracked as ASSUMPTION-2 and a RAID risk for `raid-keeper`.

---

## 5 · Craft & delivery agents to engage (by what's being built)

**Engineering inner loop (active build team):** `dev-onboarding`, `coding-standards-writer`,
`code-reviewer`, `pipeline-engineer`, `qa-tester`. Stack-depth for mobile+portal:
`frontend-developer`, `backend-developer`, `api-designer`, `data-modeler`.

**Engineering-craft actors (added by need):**
- `ux-ui-designer` — patient reminder/refill screens + pharmacist queue UI (pre-code). **Add.**
- `security-reviewer` — **Add (mandatory):** internet-facing + PHI + controlled substances.
- `sre` — **Add:** 99.9% uptime target + the ≤5-min reminder-delivery SLO need SLOs/observability/runbooks.
- `accessibility-auditor` — **Add as a pre-GA gate:** patient-facing healthcare UI carries ADA exposure. Not per-sprint.
- `performance-engineer` — **Add as a focused engagement:** the "<2s @ 500 concurrent" queue and ≤5-min delivery budgets need one profiling owner; not a standing seat on a 7-person team.
- `product-analytics` — **Add once live:** instrument the 41%→60% on-time-refill metric + refill funnel + reminder-channel A/B. Defer until after the 3-sprint slice ships.
- `ai-eval` — **Not needed.**

**Delivery chain (runs every sprint):**
`backlog-manager` (PRD/FRD → Azure Boards backlog) → `estimation-facilitator` (points) →
`sprint-planner` (goal + committed backlog) → build → `retrospective-facilitator` (improve).
Given the 3-sprint MVP pressure, stand this chain up from sprint 0 and slice vertically
(reminder → one-tap refill → pharmacist queue) so each sprint ships something demonstrable.

**Definition of Ready (adopt now):** no work item enters a sprint until its acceptance
criteria are peer-reviewed **and** — for any item touching PHI or Schedule II–V flows — it
carries a linked security/compliance note. This is the guardrail that keeps a small,
time-pressured team from shipping a compliance defect.

---

## 6 · Routing summary (what to run next)

`spec-steward` (living-spec) → **this doc-strategy** → `brd-writer` → `urs-writer` →
`prd-writer` → `frd-writer` → `srs-writer` → `sdd-writer`/`tsd-writer` → `adr-writer`
(as decisions arise) → `security-reviewer` + `ux-ui-designer` (parallel) →
`backlog-manager` → `estimation-facilitator` → `sprint-planner` → build inner-loop →
`test-plan-writer` + `qa-tester` → `sre` + `performance-engineer` + `accessibility-auditor`
(pre-GA gates) → `wiki-curator` (assemble wiki) → `product-analytics` (post-launch).
`raid-keeper` and `status-reporter` run continuously.

---

## 7 · Assumptions (unratified — carry, do not treat as decided)

- **ASSUMPTION-1** *(owner: `spec-steward`)* — The **living-spec was not routed to this agent**
  (absent on disk). Scope here is inferred solely from `brief.md`. The living-spec must
  ratify: exact regulatory jurisdiction (US states / DEA scope for Schedule II–V) and whether
  the module is US-only. See FLAG.
- **ASSUMPTION-2** *(owner: PM)* — Roster is fixed at 7 with **no designer / security / SRE / BA
  headcount**; this strategy assumes those craft roles are **borrowed or contracted** for
  gated engagements (security review, a11y audit, SRE setup). If they cannot be sourced, the
  mandatory HIPAA/a11y gates become a schedule risk.
- **ASSUMPTION-3** *(owner: architect)* — "Regulated" = **HIPAA + DEA controlled-substance
  handling**, **not** FDA 21 CFR Part 11 / GxP computerized-system validation (this is a
  pharmacy *service*, not a medical device). If Part 11 / CSV applies, the URS becomes a
  formal validated-system deliverable and a validation plan is required — re-scope the doc set.
- **ASSUMPTION-4** *(owner: PM)* — The existing mobile app and portal already provide
  patient/pharmacist authentication; the new Schedule II–V identity-verification step
  **builds on the existing IdP** rather than introducing a new one.

---

## 8 · FLAG (discovery back upstream)

```
FLAG(spec-steward): living-spec — my sole contract input — is not present at
examples/medremind-fleet-eval/run3/ (context pack §1 confirms "not found on disk").
Proceeded from brief.md under ASSUMPTION-1. Please produce/route living-spec so downstream
writers inherit a ratified scope (jurisdiction, US-only, Part 11/GxP applicability) rather
than inheriting my brief-derived assumptions.
```

---

## 9 · RTM impact

This agent's `rtm_column` is `—`: it authors **no requirements** and therefore adds **no
requirement rows** to the RTM. It has **seeded the empty RTM scaffold** (`RTM.md`) with the
standard funnel columns so `brd-writer` can fill the first rows without re-deciding the
schema. The governance decision IDs above (`DS-01`…`DS-11`) identify *documents to produce*,
not traceable requirements, and intentionally do not appear as RTM requirement rows.
