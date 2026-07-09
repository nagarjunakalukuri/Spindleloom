---
name: brownfield-recon
description: Establish ground truth from an existing codebase before writing, accepting, or building a spec/PBI — existence-check the endpoints/data it assumes, extract the REAL contract (paths, field names, enum/status values) from the code, find the sibling to mirror, classify FE-only vs backend-first, and produce an ordered, code-grounded task breakdown. Use before building on an existing system. Consumed by solution-recon, backend-developer, frontend-developer, and estimation-facilitator.
---

# Brownfield recon — derive from the code, not from the doc

Documents derive from other documents and drift; the repo is what actually runs. On existing systems the decisive question is almost always *"does the thing this work assumes actually exist, and in what shape?"* A 15-minute recon prevents dead/stub UI, wrong data assumptions, and mid-sprint surprises.

## The method
1. **State the claim** the spec/PBI makes ("aggregates `reconciliation_result`", "calls `/aep/rag/*`").
2. **Existence check** — grep/read for the endpoint, service, model, and data it assumes. Record **present / absent / partial**. (Also catches "already built" — don't spec what exists.)
3. **Extract the real contract** — the *actual* method/path, request/response keys, and **enum/status values** as they are in code, not the doc's paraphrase. (The spec said `pass/fail`; the code said `matched|mismatch|missing|partial|pending`. The code wins.)
4. **Find the sibling to mirror** — most new work on a platform clones an existing pattern; name the concrete files to copy from.
5. **Enumerate real scenarios** — edge cases, error paths, and states come from reading the implementation + its tests, not from imagining them.
6. **Classify the build shape** — **FE-only** (data already exists/exposed) vs **backend-first** (split a blocking BE task and schedule it first) vs net-new. This drives the task split and the estimate.

## Treat citations as pointers, not gospel
Recon is a pre-build snapshot. Before building, re-verify a cited `file:line` still matches — an earlier change in a sibling group can move what a later recon pointed at.

## Feed back, don't absorb
When recon contradicts the spec, route the correction upstream (to the frd/prd author) and, if it forces a decision, to `architecture-decision-framing` / `adr-writer`. Don't silently paper over a spec↔code mismatch — surfacing it early is the whole point. A surprise found here re-triggers estimation.

## Smells
- A UI story specced against an endpoint nobody confirmed exists → dead/stub UI.
- The spec's field names/enums used verbatim without checking the code → runtime mismatches.
- Building cold with no named sibling when one exists → re-inventing the platform's pattern.
