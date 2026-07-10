# MedRemind — the fleet-eval reference run

| Field | Value |
|---|---|
| What | The canonical **behavioral E2E evaluation** of the fleet's 10-agent spec+plan spine (protocol: `knowledge_hub/FLEET-EVAL.md`); latest run 4, graded **A** |
| Feature | Prescription refill reminders + pharmacist approval for a pharmacy chain — deliberately "a little complex": two personas, a regulated (HIPAA) branch, hard NFRs, a third-party integration, a capacity-vs-mandate conflict |
| Method | Ten agents chained in isolation, each receiving ONLY the artifacts the contract graph routes to it; every agent filed an honest handoff report; a fresh AI subagent (same model family, not a human/third-party) scored every handoff |
| Grade history | Run 1: **C+** (2 BROKEN handoffs — SDD designed blind to the SRS; URS orphaned from the BRD; no RTM ever materialized). Contract fixes landed. Run 2 (this folder): **B+** — 0 BROKEN, all four fixes verified, the DoR gate blocked 10 unratified-assumption items |

## How this differs from `healthy-meal-app/`

`healthy-meal-app/` shows what a **finished, polished** document set looks like.
This example shows what the fleet **actually produces under experimental conditions** —
including its honest imperfections, which are the point:

- `handoff-log.md` — each agent's own account of what it received vs needed vs invented.
- `verdict.md` — the judge's per-handoff scoring, fix verdicts, and new findings.
- **22 tagged `ASSUMPTION-n` entries** with owners, carried through the chain; 10 of 26
  backlog items correctly blocked on ratification by the Definition of Ready.
- A living `RTM.md` seeded by brd-writer and appended by every writer (matrix-shaped —
  one of the two sanctioned RTM shapes).
- The QUALITY advisories `validate_reqs` prints on this folder (compound shall-clauses in
  the FRD/SRS) are **left in deliberately** — they demonstrate the requirement-quality
  lint working on real output; the writers' exit bar now prevents new ones.

Two defects the run shipped were fixed *in place* per the conventions they motivated:
the RTM's ID-range shorthand (expanded — shorthand is invisible to validators) and a
phantom ID in the verdict prose.

## Reproduce / re-run

Follow `knowledge_hub/FLEET-EVAL.md` with `brief.md` (kept byte-stable so grades compare
across runs). Validate any run with:

```
python hooks/validate_reqs.py <run-dir>       # traceability + quality lint
python hooks/build_rtm.py <run-dir> --check   # every minted ID present in the RTM
```

Run 3 (A-) and run 4 (A) landed 2026-07-10: the estimation input seam was fixed (stem-aware
contract routing) and flags are now surfaced + routed to owners (`sloom flags` + the run-ledger
re-work loop). The remaining deduction is pipeline re-entrancy — the second orchestration pass
and security-reviewer in-chain (IMP-104 in `knowledge_hub/IMPROVEMENTS.md`, reworded from run 4).
