# Story Craft — Epics, Stories, Acceptance Criteria & Tasks

> *The card is not the story — write the conversation it starts.* The Wheelwright reference for agile story craft, grounded in primary sources (Cohn, Wake, Lawrence & Green / Humanizing Work, Agile Alliance, Scrum.org). `backlog-manager`, `frd-writer`, `test-plan-writer`, and the DoR/DoD + epic templates all reference this — don't restate it per item.

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Active reference |
| Last updated | 2026-06-21 |

## 1. The Connextra format (default, not dogma)

**"As a `<role>`, I want `<capability>`, so that `<benefit>`."** Originated with Rachel Davies at Connextra; popularized by Mike Cohn. The deeper definition (Ron Jeffries) is the **three Cs — Card, Conversation, Confirmation**: the template names the parts of the *card*; the three Cs say what a story *is*.

- **The "so that" clause** — understanding WHY guides HOW. Strongly recommended, not mandatory (Cohn writes it ~97% of the time). Drop it only when it genuinely adds nothing (e.g. a basic login).
- **No developer-only stories** — every story delivers value a customer can prioritize. *"All connections go through a pool"* → rewrite as *"Up to fifty users can use the app with a five-user DB license."*

## 2. INVEST — the quality gate (Bill Wake, 2003)

Run every story through this **before it enters a sprint**:

- **I**ndependent — minimize cross-story dependencies (they choke sprint planning).
- **N**egotiable — the card is a placeholder for a conversation, not a contract. If it can't change, it's a spec.
- **V**aluable — visible, prioritizable value; not engineer-only.
- **E**stimable — understood well enough to size; if not, converse or timebox a spike.
- **S**mall — 6–10 similar stories fit a sprint (see §5).
- **T**estable — if you can't write the acceptance test, it isn't ready.

## 3. Acceptance criteria

AC are the agreed pass/fail conditions for **one specific story**. They are **co-authored, never solo** — they come from a **Three Amigos** session that converges on concrete examples *before* the story enters a sprint:

- **Business:** "What problem are we solving?"
- **Development:** "How might we build it?"
- **Testing:** "What could go wrong?"

**AC ≠ DoD.** AC is the exit gate from the **story** (story-specific pass/fail). The **Definition of Done** is the exit gate from the **sprint** (team-wide, applied to every Increment). Don't conflate them.

Two forms — choose per story:

- **Gherkin / Given–When–Then** — for behaviour with user-visible examples (flows, state changes, happy *and* unhappy paths). One scenario per case.
  ```
  Scenario: Failed login locks account
  Given a user with 4 failed attempts
  When they submit wrong credentials again
  Then the account is locked
  And a reset email is sent within 30 s
  ```
- **Rule-based checklist** — for independent business rules/constraints with no single flow to narrate.
  ```
  ☐ Password must be ≥ 12 characters
  ☐ Account locks after 5 failed attempts
  ☐ Reset link expires after 15 minutes
  ☐ Rate limit: 10 attempts / IP / hour
  ```

> **Red flag:** AC that describe *implementation* ("the system shall use Redis") instead of *observable outcomes*.

## 4. Splitting — always vertical

Slice through **all layers** so each slice delivers visible value. **Horizontal splits (a "UI story" + a "DB story") are the single most common anti-pattern** — they may satisfy *Small* but fail *Independent* and *Valuable* (the DB layer alone has no customer value). Horizontal is acceptable only for a pure spike.

> **Wheelwright brownfield exception:** when a UI needs an endpoint/data that **doesn't exist yet** (platform extension), a backend enabler PBI *is* a legitimate split — `*-BE` blocks `*-FE`, schedule BE first. See `backlog-manager` + the DoR backend-readiness gate.

**The 9 patterns (Humanizing Work — Lawrence & Green):**

1. **Workflow steps** — thin path through the whole flow; if still big, slice the complex step first.
2. **Operations / CRUD** — "manage/maintain" hides Create·Read·Update·Delete; each its own story.
3. **Business-rule variations** — each decision path (tiers, tax rules, permissions) its own story.
4. **Variations in data** — split by data shape/type (one file format vs another).
5. **Data-entry methods** — bulk import / manual form / API upload as separate stories.
6. **Simple / complex** — ship the 80% simple case first; tackle the edge case separately.
7. **Major effort** — no obvious pattern; ship the highest-value thin slice, defer the rest.
8. **Defer performance** — split behaviour from speed/scale; optimize in a separate story.
9. **Break out a spike** — too uncertain to split/estimate; **timebox** an investigation, real story follows.

**SPIDR (Cohn)** — Spike · Paths · Interfaces · Data · Rules — a *parallel* catalog over the same ground (not derived from the 9; treat as independent).

**Two kinds of epic (Cohn):** **Compound** → split by CRUD verb or data boundary. **Complex / uncertain** → spike first, then write the real stories.

## 5. Right-sizing — the 6–10 rule

By the time a story reaches the **top** of the backlog, **6–10 similar stories should fit one sprint**. It scales with team size / sprint length (others cite 5–15 — a rule of thumb, not an SLA). Split **just-in-time** (1–2 sprints before the top), not months ahead — early splitting is false precision on work that will change. **Right-sizing is the prerequisite for *any* estimation technique** (points, t-shirt, #NoEstimates), not a substitute for it.

## 6. Hierarchy (tool-agnostic)

`Initiative → Theme → `**`Epic`**` → `**`Story`**` → Task`. The two stable anchors are **epic** (too big for a sprint; a placeholder, progressively decomposed) and **story** (fits a sprint, delivers visible value, has AC). Above epic = portfolio planning; below story = task decomposition (sub-day technical units, **no standalone user value**). "Feature" / "Initiative" are vendor conventions (SAFe / Jira / Azure Boards) — don't let tool vocabulary dictate architecture.

## 7. Red-flag anti-patterns — reject on sight

- Story won't fit a sprint alone → it's an epic; split it **before** it enters the backlog.
- Split by architectural layer (UI / DB) → horizontal; wrong for customer-facing work.
- Missing "so that" with no reason → you can't prioritize it against anything.
- Valued only by developers ("use a connection pool") → rewrite for visible customer benefit.
- AC describe implementation ("use Redis") → describe observable outcomes.
- Gold-plating beyond the AC → stop; negotiate scope or write a new story.
- A story you can't write a test for → fails *Testable*; don't pull it in.
- Card treated as a fixed contract → it's a placeholder; details are negotiated during development.

## Templates

In `templates/`: the user-story row (`backlog-template.md`), **`epic-template.md`**, **`task-template.md`** (lean — tasks are tracker-only, no AC of their own), the AC forms (§3), the splitting cheat sheet (§4), `definition-of-ready-done-template.md`, and the red-flag list (§7).

## Sources (primary; adversarially verified)

- Mike Cohn — *User Stories Applied* (2004) · "Why the Three-Part Template Works So Well" (Mountain Goat Software)
- Bill Wake — *INVEST in Good Stories and SMART Tasks* (xp123.com, 2003)
- Richard Lawrence & Peter Green — *The Humanizing Work Guide to Splitting User Stories*
- Agile Alliance — *Three Amigos* glossary
- Scrum.org — *Definition of Done vs Definition of Ready* (DoR was removed from the 2020 Scrum Guide — use as a team aid, not a mandated gate)
