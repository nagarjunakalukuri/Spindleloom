---
description: Establish codebase ground truth for a feature/PBI before spec or build — existence checks, real contracts, sibling to mirror, ordered task breakdown.
argument-hint: [feature-or-PBI]
---

Run **solution-recon** for **$1** (a feature, PBI ID, or capability). See `agents/solution-recon.md`. Brownfield only — skip for true greenfield.

1. Existence-check what the spec/PBI assumes: endpoints, data, fields, status values — grep the code, don't trust the doc.
2. Extract the **real contract**: paths, field names, enums, status codes, the actual shapes returned.
3. Name the **sibling to mirror** (the nearest working pattern an implementer should clone-and-re-point).
4. Classify: FE-only vs backend-first vs **blocked (needs prereq PBI)** — if blocked, say exactly what's missing so `backlog-manager` can cut the enabler.
5. Produce the ordered, code-grounded task breakdown and save to `docs/specs/<feature>/recon.md` (the DoR readiness signal AND the builder's warm context).

Flag every spec↔code mismatch upstream (`frd-writer`/`sdd-writer`/`adr-writer`) rather than silently absorbing it; re-scoped items go to `estimation-facilitator` for mandatory re-estimation.
