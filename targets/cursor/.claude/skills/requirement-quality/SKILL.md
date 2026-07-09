---
name: requirement-quality
description: Check that requirements are well-formed against the ISO/IEC/IEEE 29148 + INCOSE standard. Use when writing or reviewing any BRD/PRD/FRD/SRS/URS requirement, or when a requirement feels vague, untestable, or "does two things". Returns per-requirement pass/fail with the specific defect and a rewrite.
---

# Requirement quality check (ISO/IEC/IEEE 29148 + INCOSE)

Apply this whenever authoring or reviewing requirements. It is the industry gold standard for well-formed requirements (see `project_guides/BEST-PRACTICES.md`).

## Per-requirement checklist
For each requirement, verify all eight:

- **Necessary** — serves a stated goal/problem. If not → cut it.
- **Unambiguous** — exactly one reading.
- **Singular** — one obligation. The word "and"/"or" → split into two requirements.
- **Feasible** — achievable within constraints.
- **Verifiable** — provable by a test or inspection. If you can't name the test, it's not verifiable.
- **Traceable** — links to an upstream source and a downstream design/test.
- **Correct** — reflects the real need.
- **Consistent** — doesn't contradict another requirement.

## Per-set checks (the set as a whole, not any single requirement)
- **Complete** — no gaps; every stated need has a requirement.
- **Consistent** — no two requirements conflict across the set.
- **Feasible** — achievable *together* within budget/time (vs each requirement's standalone feasibility above).

## Writing rules (enforce on rewrite)
1. Active voice, **"the system shall …"** for functional/system requirements.
2. One obligation per statement — "and"/"or" is a smell.
3. **Ban vague adjectives** (fast, user-friendly, intuitive, robust, seamless). Replace with a measurable target.
   - ✗ "Search should be fast."
   - ✓ "For `/v1/search`, P95 latency < 200 ms at < 10 RPS/tenant; error rate < 0.1% over 24 h."
4. Normative text governs; diagrams/wireframes are informative only.

## Mechanized gate (run it, don't just eyeball it)
Part of this checklist is automated — make it a pre-handoff gate, not a post-hoc report:
`sloom reqs <docs-root> --strict` (hooks/validate_reqs.py) fails on compound-shall and
vague-adjective smells on requirement-defining lines, and on machine-broken `<ID>..<N>`
range shorthand that orphans every ID between the endpoints. It also runs continuously
(advisory) via the `on_md_edit` hook. Run `--strict` before every handoff and clear the
findings on your own IDs. If a compound/vague phrasing is genuinely deliberate (one subject,
two audiences), don't just argue it in prose — the gate ignores prose; add a machine-checkable
sign-off marker `<!-- quality-ok: <Req-ID> <one-line reason> -->` and the lint accepts that ID.
It is the exit bar; don't ship lint debt downstream.

## How to apply
1. Extract each requirement (one row/bullet).
2. Run the 8-point checklist; mark the first failing criterion.
3. For any fail, output: `<Req-ID> — FAIL <criterion>: <why>` and a compliant rewrite.
4. After all items, run the per-set checks and report completeness/consistency/feasibility.

## Output format
```
SR-PERF-002 — FAIL Verifiable: "should be responsive" has no measurable target.
  Rewrite: "The system shall render the dashboard first meaningful paint in < 2 s (P95) at ≤ 12 tenants."
FRD-AUTH-007 — FAIL Singular: validates token AND logs the attempt (two obligations).
  Rewrite: split into FRD-AUTH-007 (validate) and FRD-AUTH-008 (log).
Set: complete ✓ · consistent ✓ · feasible — flag SR-SCALE-001 vs budget.
```
