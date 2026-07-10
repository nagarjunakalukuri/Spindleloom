# Task — <PBI-ID> T<n>: <verb> <object>

> A **Task** is sub-day implementation under a PBI — **no standalone user value and no acceptance criteria of its own**; it rolls up to the parent story's AC. Tasks are **created and owned on the work tracker, not mirrored in `backlog.md`** (`knowledge_hub/GOVERNANCE.md` Part II §6 · `backlog-manager` *Tracker sync contract*). Keep this lean — a Task is a checklist item, not a document.

| Field | → Work item |
|---|---|
| Title | `<PBI-ID> T<n> — <verb> <object>` (e.g. `PBI-AEP-208 T2 — Parser gia_parser.py`) |
| Parent | the PBI (hierarchy link) |
| Description | one line — what changes + the seam/file it touches |
| Estimate | remaining hours (optional) |

**Done** = the slice is merged and the parent story's AC is that much closer; the **story's** DoD governs acceptance, not the task.
