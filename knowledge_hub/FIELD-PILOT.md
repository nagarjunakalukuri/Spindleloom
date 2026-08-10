# Field Pilot - eight runs of the fleet inside a live enterprise codebase

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Closed record (eight runs, 2026-07-03 -> 2026-07-24); the human-team pilot in [`archive/PILOT-PLAN.md`](archive/PILOT-PLAN.md) is still unrun |
| Complements | [`FLEET-EVAL.md`](FLEET-EVAL.md) - synthetic, isolated, judge-graded. This is the opposite: real code, real stakes, no control group. |
| Subject | A regulated-industry enterprise platform, de-identified (see *The host application*) |
| Judge | None. Findings are self-reported by the operating session and evidenced by file, command, or artifact. |
| Feeds | [`IMPROVEMENTS.md`](IMPROVEMENTS.md) - the open gaps below are the toolkit's own backlog |

`FLEET-EVAL.md` proves the fleet *coordinates* on a fixed brief in a scratch directory. It
cannot show what happens when the same fleet meets a codebase with history: stale documents,
a work-item tracker that disagrees with the code, two initiatives sharing one repository,
and a team that will not stop shipping while you audit them. This record is that second
question, answered over eight runs. It is written for two readers: an adopter deciding
whether the discipline survives contact with a real repo, and a maintainer deciding what to
build next.

**Read the honesty note first.** There is no baseline, no control team, and no independent
judge. Every run was driven by an AI session operating the fleet, and that same session wrote
the findings. What this record can honestly show is *what broke, what caught it, and what
was still missing* - not a productivity number. Where a claim rests only on the operator's
own say-so, it says so.

## The host application

De-identified. Structure preserved, identity removed - no client, product, module, ticket,
branch, or person name appears anywhere in this record, and quantities are given as bands
rather than exact counts.

| Dimension | What it was |
|---|---|
| Domain | Regulated-industry operations: high-volume document ingestion, rule-based evaluation against a regulatory ruleset, human-in-the-loop review of machine judgments, and an immutable audit trail over every decision |
| Stack | Python service backend, React/TypeScript frontend, managed container hosting (replicated in production), a managed NoSQL store, an enterprise work-item tracker as the delivery system of record |
| Team | A mid-size pod - sponsor, PM (wearing the PO hat), architect, leads, developers, QA. Team composition is context from the engagement, not something these runs measured. |
| Repository | One repo, **two parallel initiatives**, a governed docs tree in the low hundreds of files carrying a comparable number of requirement IDs across ADRs, backlogs, RTMs, sprint plans and threat models |
| Verticals touched | A compliance module (the primary subject), a public-filings module, a legal module, a net-new life-sciences vertical, and a cross-cutting knowledge layer spanning all four |

Why it was a fair test: the repo was **not** scaffolded by this toolkit. It arrived with its
own ADR numbering, its own document tree, its own conventions, and a second initiative the
Standard has no vocabulary for. Every conformance finding below is a real adoption cost, not
a self-inflicted one.

## Method

Two distinct modes ran, and the difference matters when reading the findings:

1. **Runs 1-4 - the toolkit reasons, the host's own agents execute.** The fleet's discipline
   (gates, traceability, contract-shaped handoffs) was applied by an operator using the host
   repo's own agent definitions. These runs test the *method*.
2. **Runs 5-8 - the installed plugin drives and executes.** The distributed fleet
   (`sloom:*` subagents plus its MCP tools) ran recon -> design -> ADR -> backlog ->
   estimation -> build -> three review gates -> fix -> re-verify, producing **merge-ready**
   code on a local branch. No pull request was opened during the pilot; "shipped" below
   means reviewed and landed locally, never deployed.

**Fidelity caveats, stated because the runs were not uniform.** Runs 5, 6 and 8 declared a
16-dispatch budget up front and recorded every step in a run ledger; runs 5 and 6 landed
exactly on budget, and run 8 went two over, both spent closing execution-confirmed defects
and recorded before the overrun rather than after. **Run 7 did neither**: it kept no run
ledger (dispatches were tracked in the operating session's own task list), declared no
budget, and ran its three review gates with the *host repo's* reviewer agents rather than
the fleet's - so it is a weaker data point for the product than runs 5, 6 and 8, and is
reported that way below.

## Run log

| Run | Mode | What it did | The findings that mattered |
|---|---|---|---|
| **1** | method | Conformance pass on a non-conformant repo: restored the pinned config, renumbered a duplicated ADR, de-duplicated filenames, expanded shorthand ID ranges in the RTM, traced six new requirement IDs, pushed six stories to the tracker with dependency links | Conformance was reachable **without relocating the tree** - the declared-deviation path let a repo with two initiatives become conformant honestly instead of hiding the second one. Five toolkit gaps surfaced. |
| **2** | method | A security gate on a compliance-critical write path; a build plan; then a **parallel four-lens gap sweep** (recon, test-plan, tech-debt, backlog) synthesized into one register | Planning-time recon **caught two fatal defects in a linker before it was built**. Every lens then found something the others structurally could not: a **ghost work item** (a blocker two stories referenced that was never cut), a dead coverage-threshold config, an auth-bypass flag hardcoded in a production image, and a disputed UI toggle settled as a test bug. And **cross-agent disagreement was signal**: a config-inferred "CI is green" claim contradicted an empirical "the suite dies at import" finding; surfacing the conflict exposed a compound risk that averaging would have hidden. |
| **3** | method | Fixed the three act-today findings from run 2 (a deploy-on-red CI condition, the hardcoded auth-bypass, an expired-credential bug), unblocked an integration suite that had never once run, and re-closed a story marked done at 31 of 108 passing tests | Re-verification with a pasted full-suite run took that story from **31/108 to 108/108**; the root cause across nine pages was **test fixtures modeling contracts that predated the real service types**, plus tests mocking import paths that do not exist in the source. Separately, the only other logging-capture usage in the entire suite also never asserted against what it captured - **a codebase-wide class of tests that structurally could not fail**. The same "recorded state disagrees with reality" pattern then turned up in narrative docs, independent of the tracker. |
| **4** | method | Planned a cross-cutting capability from an **externally-authored storyboard** a stakeholder shared - two parallel recon passes, a compliance-tension pass, a design pass, a self-referential gap audit, and a synthesis | Recon found the proposed core abstraction existed nowhere in the codebase and **structurally duplicated a prior ADR's manifest pattern** neither author knew about. The design resolved it the load-bearing way: nest the new concept as a sub-object *inside* the existing manifest rather than ship a third competing config-object pattern. The compliance pass returned **six concrete tensions** against the platform's own audit and security standards (single-actor audit schema vs dual e-signature, append-only vs two-signature approval, signer sourcing, signature integrity, redaction-as-mutation, visual-only access control). |
| **5** | product | First end-to-end build by the installed fleet: 16 dispatches, recon -> architect -> ADR + RAID -> backlog -> estimation -> backend build -> 3 gates -> frontend build -> 3 gates, every review finding fixed and re-verified in-session | A checker **temporarily broke a guard clause to prove its covering test was not tautological**, watched it fail, and restored it - unprompted. Reviewers also *discovered* rather than merely verified: one found a real accessibility defect (focus never restored after an approve/reject) **by reading past green tests**, and grepped the whole backend to check a workaround's justification, finding the underlying problem worse than believed (three inconsistent error-envelope shapes, not one). |
| **6** | product | A second slice, same loop shape, 16 dispatches, exactly on budget | Recon **corrected the plan document's own architecture claim** before design began. The architect made a call under a real tension (storing raw text the feature needs vs a never-log-content rule), **named the objection to its own decision** rather than hiding the tradeoff, and designed a reversible mitigation. A gap documented in run 5 (parallel writers needing each other's unminted IDs) was consciously *designed around* by sequencing the two writers - the first time a catalogued gap was avoided rather than re-hit. |
| **7** | product (reduced fidelity) | A third slice, run **concurrently with run 6 in a separate session**, against the same uncommitted planning documents. No run ledger, no declared budget, host-repo reviewers on the gates. | A real write race: a cleanup agent was killed mid-edit. Nothing was lost only because the other session had left a hand-written courtesy note this session happened to read. Both sessions also independently reached the same "next free ID" and **minted the same work-item ID twice**; recovery was to renumber *and* record the collision in the document so the numbering gap stays explained. Two independently orchestrated runs **cannot currently detect each other**. |
| **8** | product | The deferred slice from run 6, 18 dispatches (2 over cap, both for execution-confirmed defects) | Checkers stopped trusting the maker's *own* mutation-proof: one independently reverted the fix itself, confirmed the exact original crash reproduced, restored it byte-identically, and re-confirmed green. Architect grounding reached into **infrastructure-as-code** (replica count) to settle a design decision application code could not answer. Verifying one view surfaced **the same latent crash pattern in two already-shipped views** - a defect class, not a defect. |

## What held up

Recorded deliberately, because a gap catalog alone reads as a failure log:

- **Adversarial verification is real.** Across four build runs, checkers rebuilt acceptance
  matrices from source rather than trusting summaries, re-diffed a deliberately duplicated
  code path line-by-line for security divergence, and twice proved a test's discriminating
  power by breaking the code under it. In run 8 they went further and treated the maker's own
  mutation-proof as a claim requiring independent re-verification.
- **Checkers found new defects, not just confirmation.** The highest-value review findings
  were things nobody had asked about: an accessibility defect behind green tests, an
  error-envelope inconsistency three times worse than believed, and a latent crash class
  present in two already-shipped components.
- **Agents audited the operator.** A backlog agent overturned the operating session's own
  prior status claims - twice, with evidence. Independent verification worked *on the person
  running the pilot*, which is the sharpest available test of the builder-is-not-verifier rule.
- **Recon before design paid for itself repeatedly.** Four runs had their own plan corrected
  before code: two fatal linker defects caught at planning time, a wrong extension point, a
  wrong service to mirror, and a proposed abstraction that duplicated an existing one.
- **Refusal was used correctly.** Agents declined to force a story to Ready over a real unowned
  dependency, declined to invent a filename that did not exist yet, declined a false-precision
  estimate, and declined to force-reuse a component that did not fit - each time stating why.
- **Registers were extended, not duplicated.** Both keeper agents checked for a pre-existing
  register before creating one, and verified the claims they were handed with fresh searches
  rather than transcribing them.
- **The loop shape survived losing its tooling.** With the CLI absent (gap 16), a hand-rolled
  propose -> confirm -> dispatch loop still kept the human at the right altitude: architecture
  calls and scope changes got an explicit decision, routine dispatches did not.
- **Context handoff worked when it was used.** Run 2 persisted a synthesized finding register
  for downstream agents - the one positive data point for the mechanism gap 20 criticizes.

## The gap catalog

Twenty-one numbered gaps, generalized. Gap 10 was retracted by its own author. Gaps 11 and 12
were catalogued in the host repo's evolution log rather than here, to avoid the exact
"same claim in two places" drift the pilot kept finding; they are summarized but not re-derived.

**Status** is against the current release of this toolkit, verified by reading the code - not
by assuming the name of a feature implies its behavior. **One gap is closed** (16, fixed in
response to this record); ten are partially addressed, seven remain open, and two were never
re-assessed.

### Group A - intake and discovery (upstream of recon)

| # | Gap | Status | Where it stands |
|---|---|---|---|
| 1 | The audit sees only one initiative; a second one sharing the repo is silently unaudited | **OPEN** | `rtm_core.resolve_docs_root()` still resolves exactly one root, and `markdown_files()` now *excludes* any subtree owning its own RTM - which stops false orphans but means the second initiative is not audited at all. A fixture with a second scope containing an uncovered requirement and a broken citation still exits 0. |
| 13 | No intake gate for externally-authored artifacts entering the decision pipeline | **OPEN** | A stakeholder's link plus an HTML file got a full multi-agent recon and design pass before it had any repo-tracked identity. Nothing requires a minimal source/date/author/premise record before recon spend, and nothing lets a later run detect "we already ground-truthed this." |
| 14 | No cross-initiative collision check for *proposals* | **OPEN** | Every existing collision check matches identical IDs of already-minted artifacts. Nothing compares two not-yet-built proposals for a duplicated abstraction - the run-4 case, where two config-object patterns designed months apart by different authors would have shipped as competitors. |
| 15 | Backlog and estimation cannot distinguish a greenfield vertical from a thin extension | **OPEN** | The backlog row schema has no scope dimension; its Type column carries routing categories, not effort class. A net-new vertical and a small extension land on the board looking identically sized. |
| 11 | Verification stamps carry no time-to-live | *not re-assessed* | A green conformance stamp stays quotable indefinitely, however much code has landed since. |
| 12 | Context handoffs compress away the scope of what was scanned | *not re-assessed* | A handoff records the findings but not the sweep's boundaries, so a downstream agent cannot tell what was *not* looked at. |
| 10 | *(retracted by its author)* | - | An absence-claim that turned out to be wrong; kept in the numbering for honesty. |

### Group B - reconciliation (recorded state vs reality)

| # | Gap | Status | Where it stands |
|---|---|---|---|
| 7 | Nothing reconciles recorded state against reality - the pilot's dominant failure mode, hit in both directions, on the tracker **and** in narrative docs | **PARTIAL** | A drift check now diffs backlog items against the RTM's own tracker-mapping column and reports unpushed/orphaned - entirely offline. Neither adapter can read work-item state back (one can read the instance's field *schema*, never an item's status), the reverse sync is still an open register item, and no mechanism at all covers the doc-vs-code variant. |
| 8 | A "done" claim need not be evidence-typed | **PARTIAL** | A structured verification artifact is now mandatory and a gate fails a PASS with no coverage matrix or a non-green row. But the cells are unvalidated text - a matrix row containing the bare word "pass" satisfies it; no executed-run record, command string, or output is required. Only *release sign-offs* mechanically demand evidence. |
| 6 | Renaming an artifact silently breaks downstream lookups | **PARTIAL** | Dangling citations are now flagged for two ID classes (a cited ADR with no defining file; an RTM-cited requirement that does not exist) - exactly the run-1 scenario. There is still no rename or alias ledger, and an ordinary hand-rename leaves stale file-path links unchecked. |
| 2 | Human shorthand defeats requirement-ID validation | **PARTIAL** | A range-shorthand lint now catches the dotted and ellipsis forms, and `--strict` promotes it to a hard failure - which the spec-writer agents name as their exit bar. But no shipped mechanical gate passes `--strict` (not CI, not pre-commit, not the adopter battery), so by default it prints and passes; and it still misses the bare continuation form (`-002, -004`), hyphen and en-dash ranges, and "001 to 004". |
| 4 | The artifact-kind detector over-claims, collapsing distinct files to one ID | **PARTIAL** | The over-claim itself is unchanged, but duplicate artifact IDs are now a hard failure rather than silence: two backlogs in different feature folders fail the check by name. |
| 3 | The pinned config is project knowledge but silently deletable | **PARTIAL** | Deleting it now raises an advisory - which never affects the exit code. Worse, a missing config silently re-points the entire audit at a different tree with no message, so a deviation that was declared can be un-declared by deletion. |
| 5 | The converter refuses two initiatives without offering a path | **PARTIAL** | The refusal is now diagnosed per file (ADR-number collisions, many-to-one destination collisions, byte-compared "differs / identical" verdicts) instead of one flat rejection. There is still no reconcile or merge mode, and no RTM-merge tool exists. |

### Group C - orchestration and plumbing (the weakest layer)

| # | Gap | Status | Where it stands |
|---|---|---|---|
| 16 | **The agent definitions reference a CLI and hooks that no install path ships** | **MOSTLY CLOSED** | *What the pilot found:* the tooling existed in source, but the bundle generator hardcoded a four-file hook tuple, so `sloom.py`, `validate_gates.py` and `build_context_pack.py` shipped in **zero** of the six bundles while eight agent definitions called them - costing hand-rolled workarounds in three of four product runs. *Fixed:* the generator now **computes** the closure from the import graph (`hook_closure()` over `CLI_ENTRY_POINTS`, matching indented imports); all 13 CLI modules ship plus `templates/` (without it `sloom scaffold` silently wrote `_TODO_` stubs); tool paths in shipped prose are repointed per bundle; toolkit-only subcommands now explain themselves instead of emitting a file-not-found; `validate_targets` enforces presence + import resolution on every bundle; a smoke test scaffolds and runs the CLI from a clean copy of each. *Still open (IMP-174):* plugin prose uses repo-relative paths where a plugin installs under a plugin root, bare `sloom` has no shipped shim, and `sloom pack` can't locate agents in three harness layouts. |
| 17 | No run-state persistence primitive; the ledger is hand-maintained in two files | **PARTIAL** | The machine-readable half is now real: a locked read-modify-write with atomic replace, upstream-completion enforcement, phase-acceptance checks, and an appended decision log. The human-readable mirror is still hand-synced - the template and the orchestrator both still call for the pair, nothing derives one from the other, and nothing checks they agree. Run 5 hand-synced them at 11 step transitions, run 6 at 16. |
| 21 | Two concurrent sessions sharing uncommitted documents cannot detect each other | **PARTIAL** | Per-run mutual exclusion now exists (an exclusive lock around one run's ledger). Neither of the pilot's two asks is built: no lease naming the documents a run currently owns, and no registry a starting run can query. The governing model resolves concurrency by branch-and-merge, which is precisely what does not cover two sessions writing the same uncommitted file in one working tree. |
| 19 | Parallel writers cannot see each other's not-yet-minted IDs | **PARTIAL** | A next-free-ID helper exists and is exposed as a tool, but it is pure read-only computation - two parallel callers get the same answer and nothing records a claim, which is exactly how run 7's two sessions minted the same ID. Collisions are caught only afterwards, as a duplicate-ID failure. Run 6 showed the gap can be *designed around* by sequencing the writers. |
| 18 | Budget enforcement is arithmetic the enforcer does by hand | **OPEN** | The orchestrator's stated job includes enforcing a dispatch cap, but nothing computes spend. The run ledger has no dispatch counter and the status command prints step states only. Every run self-reported its count from memory; one had to recount mid-run. |
| 20 | Specialist agents cannot persist their own handoff context | **OPEN** | Verified across all 52 contracts: no agent's tool manifest includes an MCP tool, so only the orchestrating session can call save/recall - while the handoff skill still reads as if any agent could. Every handoff fact in the product runs was extracted from returned text and saved on the specialists' behalf. |
| 9 | Cross-agent finding dedup after a fan-out is manual | **OPEN** | The run-2 sweep produced 39 raw findings that the operator merged by hand to roughly 32. There is still no shared finding-ID convention (the fan-out lens agent mints no IDs at all) and no merge helper. |

### Two frictions that never got a number

Recorded because both had real consequences and neither fits the numbered catalog:

- **No "gated / conditional" state on a planned work item.** A story whose own recon had
  declared it blocked was still committed into a sprint at 8 points, because "don't commit
  until cleared" existed only as prose with nothing enforcing it.
- **Parallel review gates can finalize on stale peer state.** With three reviewers dispatched
  at once, one filed "no evidence of a security sign-off" as a blocking finding while that
  sign-off was landing in the same batch. It self-corrected within the turn, and parallelizing
  the gates is still right, but a shared "gates landed so far" view would remove the friction.

### What the shape of this catalog says

The pilot's own conclusion, and an independent code review agrees: **the agents are the
strongest part of the system and the scaffolding around them is the weakest.** Not one gap in
Group C is about an agent's judgment. They are all about the plumbing an orchestrator needs
and does not have - a shipped CLI, a run registry, a dispatch counter, a way for a specialist
to persist what it learned. Group A says the same thing at the other end of the pipeline: the
blind spots cluster *before* recon and *after* review, not in the middle where the reasoning
happens.

## What to build next

The pilot's own prescriptions, carried forward verbatim in intent. These are registered in
[`IMPROVEMENTS.md`](IMPROVEMENTS.md):

1. ~~**Ship the referenced tooling, or branch the docs.**~~ **Done** - the generator computes
   the CLI's import closure and every bundle ships it; `validate_targets` and a standalone
   smoke test hold it there (gap 16, IMP-160).
2. **Derive the run ledger's readable half from its machine half**, or add a save-run-state
   tool mirroring the context-save shape (gap 17).
3. **Add a dispatch/spend read** so budget enforcement stops being unaided arithmetic (gap 18).
4. **Add a reserve-next-id call** so parallel writers can cross-reference correctly on first
   write (gap 19).
5. **Expose the context tools to specialists, or state plainly that persistence is the
   orchestrator's job** - the skill currently implies the opposite (gap 20).
6. **Add a doc-ownership lease or a queryable run registry** so a starting run can discover an
   active one before writing shared state (gap 21).
7. **Require an intake stub** (source, date, author, one-line premise) as the *first* write for
   any externally-authored artifact, before recon spend (gap 13).
8. **Force a prior-art position** (reuse / extend / justify-new) whenever a proposal introduces
   a config-object, manifest, or profile abstraction (gap 14).
9. **Add a scope field** to the backlog row - net-new-vertical / extend-vertical / cross-cutting
   - so estimation can apply different scrutiny to each (gap 15).

## What an adopter should take from this

Seven practices earned their place under real pressure. None of them require a toolkit change:

1. **Verify by execution, never by reading.** A test that exists is not a criterion that is
   met. Where it matters, break the code deliberately and watch the test fail before you trust it.
2. **Treat the maker's own proof as a claim.** The strongest runs had the checker independently
   reproduce the mutation, not read about it.
3. **Read past the green tests.** Two of the pilot's best findings were defects that every test
   passed over: a test suite that captured logs and asserted nothing, and a component whose own
   accessibility claim its tests never checked.
4. **Recon before design, always - including recon of your own plan.** Four runs had a written
   plan corrected before code, each time by reading the actual source rather than the document.
5. **Fan out with genuinely different lenses, then keep the disagreements.** Where two lenses
   contradicted each other, the contradiction was the finding.
6. **Re-read a shared document immediately before editing it.** With no locking, this was the
   only defense that worked - and it is not sufficient: two sessions still minted the same ID
   independently, because re-reading protects text, not identifiers.
7. **Record a budget overrun before you spend it, and only for an execution-confirmed defect.**
   Transparent overrun beat both rigid enforcement and silent drift.

And one for maintainers of any agent fleet: **ship the tooling your agent definitions assume,
or make the definitions branch.** Gap 16 forced hand-rolled workarounds in three of the four
product runs.

## Limitations

- **No baseline, no control, no independent judge.** Nothing here supports a claim about speed,
  cost, or defect rate. The productivity question needs the human-team pilot in
  [`archive/PILOT-PLAN.md`](archive/PILOT-PLAN.md), which remains unrun.
- **The operator wrote the findings.** Mitigated in places (agents overturned the operator's own
  claims twice) but not eliminated.
- **One codebase, one domain, one team.** Regulated-industry document processing is a favorable
  case for a traceability-heavy toolkit; a fast-moving consumer product might report differently.
- **Runs 1-4 tested the method, not the product.** Only runs 5-8 exercised the distributed fleet
  as an adopter would receive it - and run 7 did so at reduced fidelity (see *Method*).
- **Nothing was released.** The runs produced merge-ready code on a local branch; no pull
  request, no deployment, no production observation.
- **The statuses above are a code read, not a re-run.** They say what the current release
  implements, not that a ninth run would find the gap gone.
