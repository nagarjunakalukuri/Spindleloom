# Loopwright — the delivery-loop layer

*Loopwright is the Spindleloom fleet's loop layer — the **loop-engineering** discipline applied to this project: the feedback loops of software delivery, what they are, why they dominate productivity, how to measure and tighten them, and how the fleet's agents map onto them.*

> **The three `-wright`s.** **Spindleloom** builds the fleet (market → spec → build → ship → operate); **Shipwright** generates the per-harness bundles from that single source (`hooks/build_harness_artifacts.py` → `targets/`); **Loopwright** is this layer — the fleet running inside the delivery feedback loop, tightening each loop so feedback arrives fast and clear. *Build it, ship it, loop it.*

> **Scope note — two senses of "loop engineering".** This document is about the **human delivery loop**: a developer's inner loop (edit→build→test→debug) and the team's outer loop (PR→CI→review→deploy). The term is also used for a *different* discipline — engineering **autonomous AI-agent loops** (scheduling an agent against a goal, with stop conditions, maker/checker verification, and an autonomy ladder). In that sense, "inner loop" is one agent turn and "outer loop" is the orchestration system around it. For the **agent** loop, see `agents/ai-orchestration.md` → "Autonomous loop architecture". This file is the **human** loop.

---

## 1. What "loop engineering" actually means

Software delivery is not a line from idea to production — it's a set of **nested feedback loops**. "Loop engineering" is the deliberate practice of designing those loops so that *feedback arrives fast, clear, and early*. The core insight: **the speed and quality of feedback is the single biggest lever on both developer productivity and software quality.** A team isn't slow because people type slowly; it's slow because its loops are slow — a 25-minute CI run, a two-day PR review wait, a bug found in production instead of at the keyboard.

Every loop has the same anatomy: **act → get feedback → correct.** Loop engineering asks two questions at every stage: *How long is this loop?* and *How trustworthy is the feedback?* Shorten the time and sharpen the signal, and everything else — throughput, quality, morale — follows.

The defining law of loops is the **cost-of-delay curve**: the later a loop catches a problem, the more it costs to fix. A typo caught by your editor costs seconds; the same logic error caught in code review costs minutes; in QA, hours; in production, a postmortem and customer trust. Loop engineering is largely about **pushing detection leftward** into faster, cheaper loops.

---

## 2. The two loops: inner and outer

The canonical framing splits delivery into two loops ([Speedscale](https://docs.speedscale.com/concepts/inner-outer/), [Curiosity](https://www.curiositysoftware.ie/guide-software-delivery-inner-outer-loops)):

### Inner loop — the individual, seconds to minutes
The workflow a single developer repeats dozens of times an hour: **edit → build → run → test → debug.** It's fast, local, and private. Inner-loop activities include writing code, problem-solving, running unit tests, and debugging. This is where developers want to *live* — it's where flow state happens.

> **Goal: maximize time in the inner loop, and make each iteration as fast as possible.** Sub-10-second build/test feedback keeps a developer in flow; a 3-minute local build breaks it.

### Outer loop — the team/organization, minutes to days
Everything required to turn individual contributions into a reliable product in users' hands: **commit → PR → code review → CI → integration/e2e tests → security scans → merge → deploy → monitor.** It involves other people and shared systems, so it's slower and full of *wait time*.

> **Goal: minimize how often and how long the outer loop interrupts the developer.** Every outer-loop wait (CI queue, review delay) is a flow-breaking context switch.

| | Inner loop | Outer loop |
|---|---|---|
| Scope | One developer | Team / org / systems |
| Cadence | Seconds–minutes | Minutes–days |
| Activities | edit, build, run unit tests, debug | PR, review, CI, integration, deploy, operate |
| Optimized by | fast local tooling, hot reload, good tests | automation, small PRs, fast CI, self-service platforms |
| Failure mode | slow build kills flow | slow CI/review creates wait + context-switching |

The art is **balance**: maximize inner-loop iterations (speed + flexibility), minimize outer-loop friction (without sacrificing the quality and stability the outer loop exists to provide).

---

## 3. The DevEx lens: why loops are about humans, not just pipelines

Modern developer-experience research frames productivity around three dimensions ([DX / DevEx](https://shiftmag.dev/dora-space-gsm-or-devex-how-to-measure-developer-productivity-1304/)):

1. **Feedback loops** — the speed and quality of responses to a developer's actions. (This is loop engineering, named directly.)
2. **Cognitive load** — the mental effort a task demands. Slow or noisy loops *add* cognitive load: while you wait 20 minutes for CI, you've swapped context and must reload it.
3. **Flow state** — energized, immersed focus. Flow is fragile; a single outer-loop interruption can cost 20+ minutes to recover. Fast inner loops protect flow; friction-y outer loops destroy it.

DORA's 2025 research found the platform capability most correlated with positive developer experience is **"clear feedback on the outcome of my tasks"** — fast *and* legible feedback (good logs, diagnostics, actionable errors) lets developers self-serve instead of waiting on someone. So loop engineering is two-dimensional: **latency** (how fast) and **clarity** (how understandable). A fast loop that returns a cryptic red X is only half-engineered.

This also reframes the productivity paradox: studies have shown experienced developers can be *slower* with naive AI assistance while feeling faster — because ungoverned AI lengthens the *correction* half of the loop (reviewing, debugging, untangling drift) even as it shortens the *authoring* half. Loop engineering says: optimize the whole loop, not just the keystroke.

---

## 4. Measuring loops

You tune what you measure. The mature stack layers several frameworks ([SPACE](https://linearb.io/blog/space-framework), [DORA](https://dora.dev/capabilities/platform-engineering/), [comparison](https://www.lotharschulz.info/2025/05/04/engineering-metrics-frameworks-dora-devex-space-dx-core-4-essp-comparison/)):

- **DORA (four keys)** — the outer-loop delivery scorecard: **deployment frequency**, **lead time for changes**, **change-failure rate**, **MTTR** (time to restore). Start here; it's the baseline of how fast and safely the outer loop runs.
- **Flow metrics** — **cycle time** (work started → done, *including wait time*) and **lead time** (created → delivered). Cycle time is the best single number for "how long is our overall loop, and where does it stall?" Break it into coding / review / CI / deploy segments to find the bottleneck.
- **SPACE** — broadens beyond delivery to **S**atisfaction, **P**erformance, **A**ctivity, **C**ommunication, **E**fficiency. Prevents optimizing speed at the expense of burnout. Use DORA first, then add SPACE for team health.
- **DevEx / DX Core 4** — measures the three dimensions above (feedback loops, cognitive load, flow) directly via developer perception + system signals.

Rule of thumb: **DORA tells you the outer loop's speed and safety; cycle-time breakdown tells you *where* it stalls; SPACE/DevEx tell you whether your "improvements" are quietly burning people out.** Measure the inner loop too — local build/test time, time-to-first-feedback — even if only by periodic survey.

---

## 5. Tightening each loop

### Inner loop — make iterations near-instant
- **Fast feedback at the keyboard:** sub-second linters/formatters, type-checkers, and test runners in the editor; hot reload; incremental builds.
- **Fast, reliable unit tests:** a test suite that runs in seconds and isn't flaky. Flaky tests *destroy* the loop because the feedback is no longer trustworthy.
- **Reproducible local env + a readiness gate:** one-command setup so "works on my machine" isn't a coin flip — and `dev-onboarding` now *verifies* it (build/test/lint actually run, fast and non-flaky) before work starts, rather than only documenting it.
- **Clear errors:** actionable messages and diagnostics so the developer self-corrects without asking anyone.

### Outer loop — reduce frequency and duration of interruptions
- **Small PRs:** the highest-leverage outer-loop move. Small PRs review faster, merge faster, and break less. Big PRs stall the loop and hide defects.
- **Fast CI, cheap checks first:** order pipeline stages so format/lint/unit fail in the first minute; reserve slow e2e/security for later. (This is `ci-cd-pipeline`.)
- **Automate the gates:** lint/format/coverage/security as required CI checks, so humans review *design and intent*, not style. (`coding-standards` + `ci-cd-pipeline` + `code-reviewer`.)
- **Cut wait time:** review SLAs, async review norms, and a clear "stuck → ask" rule so PRs don't sit. Wait time is usually the biggest chunk of cycle time.
- **Progressive delivery:** canary/blue-green deploys with auto-rollback shrink the deploy loop and its blast radius. (`release-manager`, `ci-cd-pipeline`.)
- **Platform engineering / self-service:** by 2025, ~90% of orgs run an internal developer platform. The point is to let developers self-serve infra/deploys (a fast loop) instead of filing tickets and waiting (a slow loop).

### The unifying move: shift detection left
Each loop should catch the class of problem it's cheapest to catch: types/format → editor; logic → unit tests; integration → CI; intent/design → review; value → QA/UAT; resilience → staging/canary. A bug that escapes to a slower loop is a signal to add a check to a faster one (e.g., a production incident should usually spawn a new test).

---

## 6. How this project's agents map onto the loops

This toolkit is **Loopwright** — loop engineering as a set of agents — each one tightens a specific loop by making the feedback faster or clearer.

```
OUTER-OUTER (product/planning loop) ── slowest, most expensive to get wrong
  mrd → brd → prd → frd → srs → sdd → tsd          (spec the right thing)
  backlog-manager → estimation → sprint-planner     (plan the loop)
  status-reporter · raid-log · retrospective         (track & learn)
        │
        ▼
OUTER (integration/delivery loop) ── minutes to days
  code-reviewer → ci-cd-pipeline → qa-tester → release-manager → incident-postmortem
        │
        ▼
INNER (developer loop) ── seconds to minutes
  dev-onboarding sets up + GATES the loop (one-command env; build/test/lint verified fast & non-flaky);
  coding-standards sets the bar; then the cycle:
  backend/frontend-developer EDIT → build → test-author's fast tests RUN → debugger / flaky-test-detective on red
  (debugger + flaky-test-detective serve both loops — cheapest here, at the keyboard)
```

| Loop | Agents that tighten it | How |
|---|---|---|
| **Inner** | `dev-onboarding` (setup + **readiness gate**), `coding-standards`, `backend-developer`/`frontend-developer`, `test-author`, `debugger`, `flaky-test-detective` | One-command env + a *verified* fast/non-flaky loop (the gate) + a clear bar; then edit→build→test→debug at the keyboard. `debugger` and `flaky-test-detective` are **dual-loop** — invoked here first (cheapest), and from CI/QA when something escapes. |
| **Outer (integrate)** | `code-reviewer`, `ci-cd-pipeline`, `qa-tester` | Severity-grouped reviews + automated gates + reproducible bug reports = faster, clearer feedback on a change |
| **Outer (ship/operate)** | `release-manager`, `incident-postmortem` | Evidence-based go/no-go + blameless postmortems = safe fast deploys and learning that closes the loop |
| **Planning loop** | `backlog-manager`, `estimation-facilitator`, `sprint-planner`, `retrospective-facilitator` | Ready, estimated, goal-aligned work = the team iterates on the *right* things; retro tunes the loop itself |
| **Governance** | `raid-log`, `status-reporter` | Fast, honest feedback to stakeholders shortens the *decision* loop |

Two project features are pure loop engineering:
- **The RTM + Req-ID thread** makes the *correction* loop fast: when something changes, traceability shows the blast radius instantly instead of a manual hunt.
- **The validation gates** (DoR → review → CI → DoD → QA sign-off → go/no-go) are deliberately ordered so each catches problems at the cheapest loop — exactly the "shift-left" principle.

---

## 7. Anti-patterns — how loops break

- **The 25-minute CI run:** the outer loop is so slow developers batch work and context-switch; cycle time balloons. Fix: parallelize, cache, cheap-checks-first.
- **Flaky tests:** feedback becomes untrustworthy, so people ignore red — the loop still runs but no longer *means* anything. Fix: quarantine and fix flakes ruthlessly.
- **Giant PRs:** review takes days, defects hide, merge conflicts pile up. Fix: small, single-concern PRs (`code-reviewer` flags oversize).
- **Bug found in prod that a unit test could've caught:** detection happened in the most expensive loop. Fix: postmortem action → add the test (`incident-postmortem` → backlog).
- **Ticket-driven infra:** every environment/deploy is a wait-on-another-team loop. Fix: self-service platform.
- **Reviewing style by hand:** humans spending the review loop on formatting tools should enforce. Fix: automate in CI (`coding-standards` + `ci-cd-pipeline`).
- **"Watermelon" status:** the stakeholder feedback loop returns "green" while reality is red, so course-correction comes too late. Fix: honest RAG grounded in metrics (`status-reporter`).

---

## 8. Tune-your-loops checklist (for the 9-person team on Azure DevOps)

**Inner loop**
- [ ] One-command local setup; build/test feedback < ~10s (CONTRIBUTING via `dev-onboarding`)
- [ ] Linter/formatter/type-checker in the editor; zero hand-reviewing of style
- [ ] Unit suite fast and non-flaky

**Outer loop**
- [ ] PRs small and single-concern; review SLA agreed (`code-reviewer`)
- [ ] CI: cheap checks first, required to merge; runs in a few minutes (`ci-cd-pipeline`, Azure Pipelines + branch policies)
- [ ] Automated deploy to staging + progressive prod rollout with rollback (`release-manager`)
- [ ] QA handoff + bug reports reproducible; sign-off feeds go/no-go (`qa-tester`)

**Measure**
- [ ] DORA four keys on the Azure dashboard (deploy freq, lead time, change-fail, MTTR)
- [ ] Cycle time broken into coding / review / CI / deploy to find the stall
- [ ] A periodic DevEx/SPACE pulse so speed gains aren't burning the team

**Close the loops**
- [ ] Every production incident spawns a test or guardrail (`incident-postmortem` → backlog)
- [ ] Recurring review nits get automated (`coding-standards`)
- [ ] Retro picks one loop to shorten each sprint (`retrospective-facilitator`)

---

## 9. The one-paragraph takeaway
Software speed is loop speed. There are two loops — the **inner loop** (a developer editing, building, testing, debugging in seconds) and the **outer loop** (the team integrating, reviewing, shipping, operating over minutes to days). Productivity comes from **maximizing time in a fast inner loop and minimizing outer-loop interruptions**, while keeping feedback not just *fast* but *clear*. Measure it with DORA + cycle time, watch the humans with SPACE/DevEx, and relentlessly **shift detection left** so each problem is caught in the cheapest possible loop. This project's agents are, end to end, an implementation of that idea: each one shortens or sharpens a specific feedback loop.

## Sources
- [Inner vs Outer Loop — Speedscale](https://docs.speedscale.com/concepts/inner-outer/)
- [A Guide to Software Delivery's Inner & Outer Loops — Curiosity](https://www.curiositysoftware.ie/guide-software-delivery-inner-outer-loops)
- [Inner vs Outer Loop: developer productivity — Medium/Kashif Mohammed](https://kashif-mohammed.medium.com/inner-vs-outer-loop-the-secret-to-developer-productivity-f1944af563da)
- [Reducing toil in inner & outer loops — DEV](https://dev.to/payel_bhattacharya_71206f/understanding-and-reducing-toil-in-the-inner-and-outer-loops-of-software-development-2m55)
- [DORA / SPACE / DevEx comparison — shiftmag](https://shiftmag.dev/dora-space-gsm-or-devex-how-to-measure-developer-productivity-1304/)
- [SPACE framework — LinearB](https://linearb.io/blog/space-framework)
- [DORA: platform engineering capability](https://dora.dev/capabilities/platform-engineering/)
- [Engineering metrics frameworks compared — Lothar Schulz](https://www.lotharschulz.info/2025/05/04/engineering-metrics-frameworks-dora-devex-space-dx-core-4-essp-comparison/)
