#!/usr/bin/env python3
"""Tests for emit_backlog.py — the backlog.md -> work-tracker sync-contract emitter.

Runnable two ways (stdlib only): `python hooks/test_emit_backlog.py` or `pytest`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_backlog  # noqa: E402

SAMPLE = """# Product Backlog — Demo

## Epics
| Epic | Goal | Source (PRD/FRD) |
|---|---|---|
| CHECKOUT | Fast, secure checkout | PRD #2 |

## Backlog (ordered)
| Rank | PBI ID | Type | Story / item | Acceptance criteria | Priority | Est. | Deps | Source | Ready? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PBI-CHECKOUT-001 | Story | As a shopper, I want to pay with a saved card so that checkout is fast | Given a saved card, when I pay, then the order completes | Must | 3 | — | FRD-ORD-001 | ✅ |
| 2 | PBI-CHECKOUT-002 | Bug | Declined card shows no error to the user | Given a decline, then I see why and can retry | Should | 2 | 001 | FRD-ORD-001 | ❌ |
"""


def test_parse_finds_pbis_skips_epics_table():
    pbis = emit_backlog.parse_backlog(SAMPLE)
    assert [p["id"] for p in pbis] == ["PBI-CHECKOUT-001", "PBI-CHECKOUT-002"]
    assert pbis[0]["epic"] == "CHECKOUT"


def test_field_map_matches_sync_contract():
    items = emit_backlog.plan(SAMPLE)["work_items"]
    a, b = items
    # Type -> Work Item Type
    assert a["work_item_type"] == "User Story"
    assert b["work_item_type"] == "Bug"
    # MoSCoW -> Priority
    assert a["priority"] == 1 and b["priority"] == 2
    # Est -> Story Points (numeric)
    assert a["story_points"] == 3.0
    # epic -> Parent
    assert a["parent_epic"] == "CHECKOUT"
    # Ready?
    assert a["ready"] is True and b["ready"] is False


def test_ac_lands_in_its_OWN_field_not_description():
    """The headline contract: AC must be its own field, never folded into Description."""
    a = emit_backlog.plan(SAMPLE)["work_items"][0]
    assert a["acceptance_criteria"].startswith("Given a saved card")
    assert a["description"].startswith("As a shopper")
    # AC text must NOT be inside the description
    assert a["acceptance_criteria"] not in a["description"]
    assert "Given a saved card" not in a["description"]


def test_writeback_appends_azure_column_when_absent():
    table = ("| PBI ID | Story |\n"
             "|---|---|\n"
             "| PBI-CHECKOUT-001 | pay with saved card |\n"
             "| PBI-CHECKOUT-002 | declined card error |\n")
    out = emit_backlog.writeback(table, {"PBI-CHECKOUT-001": "12345", "PBI-CHECKOUT-002": "12346"})
    assert "Azure" in out
    assert "12345" in out and "12346" in out


def test_writeback_fills_existing_azure_column_idempotently():
    table = ("| PBI ID | Azure |\n"
             "|---|---|\n"
             "| PBI-CHECKOUT-001 | — |\n"
             "| PBI-UNMAPPED-009 | — |\n")
    out = emit_backlog.writeback(table, {"PBI-CHECKOUT-001": "12345"})
    lines = [ln for ln in out.split("\n") if "CHECKOUT-001" in ln]
    assert "12345" in lines[0]
    # an unmapped row is left untouched (still the placeholder)
    assert any("UNMAPPED-009 | —" in ln for ln in out.split("\n"))


RTM_MAPPED = ("| PBI ID | Story | Azure (work-item id) |\n"
              "|---|---|---|\n"
              "| PBI-CHECKOUT-001 | pay with saved card | 12345 |\n"
              "| PBI-CHECKOUT-002 | declined card error | — |\n")


def test_read_id_map_inverts_writeback():
    m = emit_backlog.read_id_map(RTM_MAPPED)
    assert m == {"PBI-CHECKOUT-001": "12345"}, m  # placeholder cell = unmapped


def test_filter_pushed_skips_mapped_pbis():
    """The idempotency guard: already-RTM-mapped PBIs are skipped, never re-created."""
    p = emit_backlog.plan(SAMPLE)
    filtered, skipped = emit_backlog.filter_pushed(p, RTM_MAPPED)
    assert skipped == [("PBI-CHECKOUT-001", "12345")]
    assert [wi["pbi_id"] for wi in filtered["work_items"]] == ["PBI-CHECKOUT-002"]
    assert filtered["count"] == 1
    # fully-mapped RTM -> zero creates
    both = RTM_MAPPED.replace("declined card error | — |", "declined card error | 12346 |")
    filtered2, skipped2 = emit_backlog.filter_pushed(p, both)
    assert filtered2["count"] == 0 and len(skipped2) == 2


def test_check_drift_flags_new_and_gone():
    d = emit_backlog.check_drift(SAMPLE, RTM_MAPPED)
    assert d["new_unpushed"] == ["PBI-CHECKOUT-002"]      # in backlog, unmapped
    assert d["gone_orphaned"] == [] and d["ok"]
    # a mapped PBI that vanished from the backlog is GONE (orphaned tracker item)
    gone_rtm = RTM_MAPPED.replace("PBI-CHECKOUT-001", "PBI-RETIRED-001")
    d2 = emit_backlog.check_drift(SAMPLE, gone_rtm)
    assert d2["gone_orphaned"] == ["PBI-RETIRED-001"] and not d2["ok"]


def test_writeback_fills_tracker_named_column_not_appends_azure():
    # A team may name the mapping column for its own tracker; writeback FILLS it rather
    # than appending a second 'Azure' column (tracker-aware; read/fill side is permissive).
    table = """| PBI ID | Jira |
|---|---|
| PBI-CHECKOUT-001 | - |
"""
    out = emit_backlog.writeback(table, {"PBI-CHECKOUT-001": "PROJ-9"})
    assert "PROJ-9" in out
    assert "Azure" not in out           # reused the existing column, appended nothing
    assert out.count("Jira") == 1


def test_read_id_map_reads_tracker_named_column():
    rtm = """| PBI ID | Story | Jira |
|---|---|---|
| PBI-CHECKOUT-001 | pay | PROJ-9 |
"""
    assert emit_backlog.read_id_map(rtm) == {"PBI-CHECKOUT-001": "PROJ-9"}


def test_atomic_write_replaces_and_cleans_temp():
    import tempfile
    d = Path(tempfile.mkdtemp())
    target = d / "RTM.md"
    target.write_text("old", encoding="utf-8")
    emit_backlog.atomic_write(target, "new content")
    assert target.read_text(encoding="utf-8") == "new content"
    assert not (d / "RTM.md.tmp").exists()   # temp file consumed by os.replace


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"{len(fns)} passed")


if __name__ == "__main__":
    _run()
