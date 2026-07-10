# Claude Prompt Library — with the fleet upgrade map

| Field | Value |
|---|---|
| Owner | Toolkit maintainer |
| Status | Reference |
| Sources | viral "power prompt" posts + the official Claude Code prompt library + platform model docs |

The prompts people share work because they smuggle a role, a method and an output contract into one message. **This fleet ships those as named specialists** -- with typed inputs, quality gates and a traceability thread the one-shot prompt can never have. Use the map below: if you were about to paste a power prompt, invoke its specialist instead. The rest of the file keeps the originals verbatim -- they are still useful outside a Spindleloom repo, and Parts 2-3 (the official library and model-specific tips) are good craft anywhere.

## The upgrade map — the prompt you saw, and the specialist that does it better

| # | The viral prompt | The fleet upgrade | Why the specialist wins |
|---|---|---|---|
| 1 | Full Startup Engineering Team | `/spec-new` then `/run` -- `run-orchestrator` drives the whole chain | one prompt asks for everything at once; the chain produces each artifact with contracts, gates and one RTM |
| 2 | Codebase Audit | `solution-recon` (`/build-recon`) | findings land as a recon doc the PBIs cite, not a chat answer that scrolls away |
| 3 | Production-Level Debugging | `debugger` | one-hypothesis-at-a-time discipline, fix the shared cause, regression test required |
| 4 | Performance Optimization Engineer | `performance-engineer` | profiles against the SRS budgets (SR-PERF ids), not vibes |
| 5 | Clean Architecture Refactor | `architect` + `tech-debt-keeper` + `code-reviewer` | debt is registered and ranked; refactors are reviewed against the coding standard |
| 6 | Startup Backend Architect | `sdd-writer` + `api-designer` + `data-modeler` | the contracts land as OpenAPI/ERD that frontend, backend and tests build against |
| 7 | Senior Frontend Engineer | `frontend-developer` + `ux-ui-designer` + `accessibility-auditor` | every state designed, a11y audited to WCAG AA -- verified, not promised |
| 8 | AI Technical Lead Mode | `architect` + `rfc-facilitator` | the challenge happens as an RFC and lands as an ADR, not in chat memory |
| 9 | Production Security Audit | `security-reviewer` | STRIDE at design time plus a release-blocking sign-off token |
| 10 | Senior DevOps + Deployment Engineer | `pipeline-engineer` + `sre` + `release-manager` | pipeline + SLOs + an evidence-based go/no-go, not a checklist in prose |

Per-role copy-ready prompts for THIS fleet live in the [Persona Field Handbook](personas/index.html) -- 54 prompts, filterable by role/phase, each grounded in an agent contract.

---

## PART 1: Role-Based Power Prompts (from social media)

These prompts frame Claude as a specific senior engineering role to get expert-level output.

---

### 1. Full Startup Engineering Team

> "Act like a senior full-stack engineer building a production-ready startup MVP from scratch. First design the complete system architecture, then build the most minimal but scalable version possible.
>
> Include:
> - System architecture
> - File structure
> - Database schema
> - API endpoints
> - UI architecture
> - Production-ready code
>
> Build it like a real startup that could scale to millions of users."

---

### 2. Codebase Audit

> "Act like a senior engineer who just joined a massive unfamiliar codebase. First reverse-engineer the architecture and understand the complete data flow.
>
> Then identify:
> - Bad architecture decisions
> - Duplicate logic
> - Performance bottlenecks
> - Scalability risks
> - Maintainability issues
>
> Finally provide:
> - A clean architecture breakdown
> - Critical problem areas
> - Refactoring strategies
> - Improved production-grade code
>
> Do not change functionality. Only upgrade the code quality, scalability, and maintainability."

---

### 3. Production-Level Debugging

> "Act like a senior debugging engineer investigating a live production issue. Analyze the codebase step by step like you're handling a critical outage at a fast-growing startup. Your job:
>
> - Understand what the code actually does
> - Trace the real root cause
> - Explain why the failure happens
> - Identify hidden edge cases
> - Propose the most robust fix possible
>
> Finally provide:
> - Code functionality breakdown
> - Root cause analysis
> - Failure explanation
> - Edge case analysis
> - Fixed production-ready code
>
> Do not guess. Think deeply before making changes."

---

### 4. Performance Optimization Engineer

> "Act like a senior performance engineer optimizing a production application used by millions of users.
>
> Your goals:
> - Maximum speed
> - Lower memory usage
> - Better scalability
> - Faster rendering
> - Cleaner execution
>
> Carefully identify:
> - Performance bottlenecks
> - Inefficient logic
> - Unnecessary rendering
> - Expensive operations
> - Memory leaks
>
> Then provide:
> - Performance issue breakdown
> - Optimization strategies
> - Improved production-ready code
> - Scalability recommendations
>
> Optimize the code like you're preparing it for massive traffic."

---

### 5. Clean Architecture Refactor

> "Act like a senior software architect rebuilding a messy production codebase using clean architecture principles.
>
> Your mission:
> - Separate concerns properly
> - Increase modularity
> - Reduce tight coupling
> - Improve scalability
> - Make the codebase easier to maintain long term
>
> Do NOT change the product behavior. Only improve the architecture and code quality.
>
> Finally provide:
> - New folder structure
> - Clean architecture breakdown
> - Refactored production-grade code
> - Explanation of architectural improvements
>
> Refactor it like a real senior engineer preparing the codebase to scale."

---

### 6. Startup Backend Architect

> "Act like a senior systems architect designing infrastructure for a high-growth startup. First design a scalable production-grade system architecture. Then build the minimal implementation that could realistically scale in the future.
>
> Include:
> - System architecture
> - Component structure
> - Data flow
> - API design
> - Database schema
> - Caching strategy
> - Production-ready implementation code
>
> Optimize for scalability, maintainability, and real-world production usage."

---

### 7. Senior Frontend Engineer

> "Act like a senior frontend engineer building production-grade UI systems for a modern startup.
>
> Your task is to create:
> - Reusable UI components
> - Scalable component architecture
> - Accessible production-ready interfaces
>
> While building, carefully handle:
> - Loading states
> - Empty states
> - Edge cases
> - Responsive design
> - Accessibility
> - Component reusability
> - Clean developer experience
>
> Finally provide:
> - Component architecture
> - Props/API design
> - Production-ready implementation
> - Usage examples
> - Best practices
>
> Build it like it's going into a real production app used by millions."

---

### 8. AI Technical Lead Mode

> "Act like a senior technical lead managing a real engineering team.
>
> Before writing code:
> - Ask clarifying questions
> - Challenge bad decisions
> - Identify scaling risks
> - Suggest better approaches
> - Prioritize simplicity
>
> Think long-term like someone responsible for maintaining this product for 5+ years.
>
> Then provide:
> - Technical decisions
> - Tradeoff analysis
> - Recommended architecture
> - Implementation plan
> - Production-ready solution
>
> This makes Claude stop behaving like a code generator... and start thinking like an actual tech lead."

---

### 9. Production Security Audit

> "Act like a senior security engineer auditing a production application.
>
> Carefully inspect the system for:
> - Security vulnerabilities
> - Authentication flaws
> - API weaknesses
> - Injection risks
> - Sensitive data exposure
> - Infrastructure risks
>
> Then provide:
> - Vulnerability report
> - Severity levels
> - Attack scenarios
> - Secure implementation fixes
> - Production-grade recommendations"

---

### 10. Senior DevOps + Deployment Engineer

> "Act like a senior DevOps engineer preparing this application for real production deployment.
>
> Your job:
> - Design deployment architecture
> - Configure CI/CD
> - Setup monitoring/logging
> - Improve reliability
> - Reduce downtime risks
> - Optimize scaling
>
> Provide:
> - Infrastructure architecture
> - Deployment workflow
> - CI/CD pipeline
> - Docker/Kubernetes setup
> - Monitoring strategy
> - Production deployment checklist"

---

## PART 2: Official Claude Code Prompt Library (from code.claude.com)

Organized by phase of software development. Fill in `{slots}` with your own context.

---

### DISCOVER

| Goal | Prompt |
|------|--------|
| Get oriented | `give me an overview of this codebase: architecture, key directories, and how the pieces connect` |
| Explain code | `explain what {path} does and how data flows through it. write it up as {format}` |
| Find behavior | `where do we {behavior}?` |
| Check dependencies | `what would break if I deleted {target}?` |
| Trace history | `look through the commit history of {path} and summarize how it evolved and why` |
| Scope a change | `which files would I need to touch to {change}?` |
| Product question | `I am a {role}. walk me through what happens when a user {action}, from the UI down to the result` |

---

### DESIGN

| Goal | Prompt |
|------|--------|
| Plan before coding | `plan how to refactor the {target} to {goal}. list the files you would change, but don't edit anything yet` |
| Draft a spec | `I want to build {feature}. interview me about implementation, UX, edge cases, and tradeoffs until we have covered everything, then write the spec to SPEC.md` |
| Turn meeting into tickets | `read {input} and write up the action items, then create a {tracker} ticket for each with acceptance criteria` |
| Map edge cases | `list the error states, empty states, and edge cases for {feature} that the design needs to cover` |
| Build prototype from mockup | `here is a mockup. build a working prototype I can click through, matching the layout and states shown` |
| Implement from screenshot | `implement this design, then take a screenshot of the result, compare it to the original, and fix any differences` |

---

### BUILD

| Goal | Prompt |
|------|--------|
| Follow existing pattern | `look at how {example} is implemented to understand the pattern, then build {new} the same way` |
| Add a feature | `add a {endpoint} endpoint that returns {payload}` |
| Generate docs | `find {scope} without {format} comments and add them, matching the style already used in the file` |
| Work an issue end to end | `read issue #{issue}, implement the fix, and run the tests` |
| Update copy | `find every place we say "{copy}" or a close variant, show me each one in context, then update them all to "{new}". leave tests and the changelog alone` |
| Draft from examples | `read the {examples} in {folder} to learn the structure and voice, then draft a new one for {topic}` |

---

### TEST

| Goal | Prompt |
|------|--------|
| Write + run + fix | `write tests for {path}, run them, and fix any failures` |
| TDD | `write tests for {feature} first, then implement it until they pass` |
| Fill coverage gaps | `read {report} and add tests for the lowest-covered files until each is above {target}%` |

---

### REFACTOR

| Goal | Prompt |
|------|--------|
| Migrate a pattern | `migrate everything from {from} to {to}: identify every place that needs to change, then make the changes` |
| Port to another language | `port {source} to {target}, keeping the same {keep}` |
| Optimize to a target | `optimize {target} to bring {metric} from {current} down to under {goal}` |
| Fix a visual bug | `the {element} extends {amount} beyond the {container} on {viewport}. fix it.` |

---

### REVIEW

| Goal | Prompt |
|------|--------|
| Pre-commit review | `review my uncommitted changes and flag anything that looks risky before I commit` |
| Review a PR | `review PR #{pr} and summarize what changed, then list any concerns` |
| Review infra changes | `here is my Terraform plan output. what is this going to do, and is anything here going to cause problems?` |
| Security review | `use a subagent to review {path} for security issues and report what it finds` |
| Content review | `review {file} for {concerns} and list anything I should fix before it goes to {reviewer}` |

---

### STEER (course correct Claude)

| Goal | Prompt |
|------|--------|
| Course correct | `that is not right: {feedback}. try a different approach` |
| Narrow scope | `that is too much. keep only the changes to {scope} and undo your other edits` |
| Turn correction into a rule | `you keep {mistake}. add a rule to CLAUDE.md so this stops happening` |

---

### GIT & SHIP

| Goal | Prompt |
|------|--------|
| Resolve merge conflicts | `resolve the merge conflicts in this branch and explain what you kept from each side` |
| Commit message | `commit these changes with a message that summarizes what I did` |
| Open a PR | `find the {tracker} ticket about {topic} and open a PR that implements it` |
| Draft release notes | `compare {from} to {to} and draft release notes grouped by feature, fix, and breaking change` |
| Write CI workflow | `write a GitHub Actions workflow that {steps} on every push to {branch}` |

---

### DEBUG & OPERATE

| Goal | Prompt |
|------|--------|
| Fix a failing test | `the {test} test is failing, find out why and fix it` |
| Investigate error | `users are seeing {symptom} on {where}. investigate and tell me what is going on` |
| Fix a build error | `here is a build error. fix the root cause and verify the build succeeds` |
| Production incident | `{symptom}. check the logs, recent deploys, and config changes, then tell me the most likely cause` |
| Diagnose from screenshot | `here is a screenshot of {console}. walk me through why {resource} is failing and give me the exact commands to fix it` |
| Query logs | `show me all {events} for {scope} over {timeframe}. write the query, run it, and tell me what stands out` |

---

### DATA & AUTOMATE

| Goal | Prompt |
|------|--------|
| Analyze a file | `read {file}, summarize the key patterns, and write the results to {output}` |
| Generate ad variations | `read {file}, find the underperforming {items}, and generate {n} new variations that stay under {limit} characters` |
| Create a reusable skill | `create a /{name} skill for this project that {steps}` |
| Add a hook | `write a hook that {action} after every {event}` |
| Connect via MCP | `set up the {server} MCP server so you can read my {data} directly` |
| Capture session memory | `summarize what we did this session and suggest what to add to CLAUDE.md` |

---

## PART 3: Model-Specific Prompting (from platform.claude.com docs)

Prompting patterns that differ per model. Applies mainly to API/agent builders, but the copy-paste snippets work in any Claude interface.

---

### Claude Fable 5 (frontier model, multi-day autonomous runs)

**Big idea:** Instruction-following is strong enough that one brief instruction replaces long enumerated lists. Prompts/skills written for older models are often *too prescriptive* and can degrade output — try removing old instructions.

**Copy-paste snippets:**

Prevent overplanning:
> "When you have enough information to act, act. Do not re-derive facts already established, re-litigate decisions the user already made, or narrate options you will not pursue. If weighing a choice, give a recommendation, not an exhaustive survey."

Prevent scope creep / unrequested refactoring:
> "Don't add features, refactor, or introduce abstractions beyond what the task requires. Don't design for hypothetical future requirements: do the simplest thing that works well. Only validate at system boundaries (user input, external APIs)."

Concise output:
> "Lead with the outcome. Your first sentence should answer 'what happened' — the TLDR. Supporting detail comes after. Be selective about what you include; don't compress writing into fragments or arrow chains."

Honest progress reports (nearly eliminates fabricated status updates):
> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. If tests fail, say so with the output."

Stay in scope:
> "When the user is describing a problem or thinking out loud rather than requesting a change, the deliverable is your assessment. Report findings and stop. Don't apply a fix until they ask."

Autonomous pipelines (prevent early stopping):
> "You are operating autonomously. For reversible actions that follow from the original request, proceed without asking. Before ending your turn, check your last paragraph — if it's a plan, question, or promise about undone work, do that work now with tool calls."

Memory across runs:
> "Store one lesson per file with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they mattered. Update existing notes rather than duplicating; delete notes that turn out wrong."

Give the reason, not only the request:
> "I'm working on [the larger task] for [who it's for]. They need [what the output enables]. With that in mind: [request]."

Other tips:
- Start at the *top* of your difficulty range — testing only simple tasks undersells it
- Fresh-context verifier subagents outperform self-critique for checking work
- Use `high` effort as default, `xhigh` for capability-critical work
- Don't instruct it to echo its reasoning in responses (triggers refusals)

---

### Claude Opus 4.8

- **Effort is the main lever.** `xhigh` for coding/agents; minimum `high` for intelligence-sensitive work; `max` can overthink. Set large output budgets (64k+) at high effort.
- **Very literal instruction following.** It won't silently generalize. State scope explicitly: "Apply this to every section, not just the first one."
- **Response length auto-calibrates** to task complexity. To force concision: "Provide concise, focused responses. Skip non-essential context." Positive examples work better than "don't" lists.
- **Code review gotcha:** "Only report high-severity issues" makes it silently drop real bugs. Instead:
  > "Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance at this stage. Your goal is coverage. Include confidence level and estimated severity for each finding."
- **Design default:** persistent cream backgrounds + serif type + terracotta accents. Generic "don't use cream" just swaps to another fixed palette. Either give a concrete visual spec, or:
  > "Before building, propose 4 distinct visual directions tailored to this brief (each as: bg hex / accent hex / typeface — one-line rationale). Ask the user to pick one, then implement only that direction."
- **Anti-AI-slop snippet:**
  > "NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients), predictable layouts, and cookie-cutter design. Use unique fonts, cohesive themes, and micro-interactions."
- **Interactive coding:** specify the task, intent, and constraints fully in the *first* message — drip-feeding requirements across turns reduces efficiency and performance.
- Spawns fewer subagents by default; instruct explicitly when to fan out.

---

### Claude Sonnet 5

Mostly shares Opus 4.8 patterns (literal instructions, calibrated verbosity, code-review coverage prompt, design-variety approaches). Key differences:

- **Adaptive thinking on by default** — requests without a `thinking` field now think. Disable with `thinking: {type: "disabled"}`.
- **No sampling params:** `temperature`/`top_p`/`top_k` return a 400 error. Use prompt instructions for variety instead.
- **New tokenizer:** ~30% more tokens for the same text — raise `max_tokens` limits tuned for Sonnet 4.6.
- **Effort mapping when migrating:** Sonnet 5 at `medium` ≈ Sonnet 4.6 at `high`; Sonnet 5 at `high` ≈ Sonnet 4.6 at `max`.
- More agentic by default — reaches for tools and self-verification loops readily. With thinking disabled, tool use drops; add an explicit nudge if needed.

---

## Key Principles (What Makes These Prompts Work)

1. **Assign a role** — "Act like a senior X" unlocks expert-level reasoning and output quality
2. **Describe the outcome, not the steps** — Let Claude figure out how to get there
3. **Give it a way to verify its own work** — Ask it to run, test, compare, or screenshot
4. **Point at a reference** — Name an existing file or pattern to match
5. **State a measurable target** — Give a metric and threshold so "done" is unambiguous
6. **Paste the actual artifact** — Logs, errors, screenshots are better than descriptions
7. **Say how you want the answer** — Name the format, length, or audience upfront
8. **Turn corrections into rules** — Add persistent instructions to CLAUDE.md

---

*Sources: power.ai / itsaiaiguide (Instagram), code.claude.com/docs/en/prompt-library, platform.claude.com model prompting guides (Fable 5, Opus 4.8, Sonnet 5)*
