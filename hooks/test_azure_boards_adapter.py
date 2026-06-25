#!/usr/bin/env python3
"""Offline tests for azure_boards_adapter.build_patch + dry-run (no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import azure_boards_adapter as a  # noqa: E402


def test_build_patch_basic():
    wi = {"pbi_id": "PBI-CHECKOUT-007", "work_item_type": "User Story",
          "title": "PBI-CHECKOUT-007 — pay with a saved card", "description": "As a user, I pay with a saved card.",
          "acceptance_criteria": "Given a saved card, when I pay, then I get a confirmation.",
          "priority": 1, "story_points": 5.0, "parent_epic": "CHECKOUT",
          "source_ref": "FRD-CHK-001", "tags": ["checkout"]}
    paths = {o["path"]: o["value"] for o in a.build_patch(wi)}
    assert paths["/fields/System.Title"].startswith("PBI-CHECKOUT-007")
    assert paths["/fields/Microsoft.VSTS.Common.AcceptanceCriteria"].startswith("Given a saved card")
    assert paths["/fields/Microsoft.VSTS.Common.Priority"] == 1
    assert paths["/fields/Microsoft.VSTS.Scheduling.StoryPoints"] == 5.0
    # the sync-contract invariant: AC is NEVER folded into the description
    assert "Given a saved card" not in paths["/fields/System.Description"]
    # findable by source ref AND its PBI id
    assert "FRD-CHK-001" in paths["/fields/System.Tags"]
    assert "PBI-CHECKOUT-007" in paths["/fields/System.Tags"]


def test_task_has_no_story_points():
    wi = {"pbi_id": "PBI-X-1", "work_item_type": "Task", "title": "t", "description": "d",
          "acceptance_criteria": "", "priority": None, "story_points": 3.0,
          "parent_epic": "X", "source_ref": "", "tags": []}
    paths = {o["path"] for o in a.build_patch(wi)}
    assert "/fields/Microsoft.VSTS.Scheduling.StoryPoints" not in paths


def test_parent_relation_when_linked():
    wi = {"pbi_id": "PBI-X-1", "work_item_type": "User Story", "title": "t", "description": "d",
          "acceptance_criteria": "a", "priority": 2, "story_points": 1.0,
          "parent_epic": "X", "source_ref": "", "tags": []}
    ops = a.build_patch(wi, parent_url="https://dev.azure.com/o/_apis/wit/workItems/42")
    rel = [o for o in ops if o["path"] == "/relations/-"]
    assert rel and rel[0]["value"]["rel"] == "System.LinkTypes.Hierarchy-Reverse"


def test_dry_run_makes_no_network_calls():
    plan = {"count": 1, "warnings": [], "work_items": [
        {"pbi_id": "PBI-X-1", "work_item_type": "Task", "title": "t", "description": "d",
         "acceptance_criteria": "", "priority": None, "story_points": None,
         "parent_epic": "X", "source_ref": "", "tags": []}]}
    assert a.push(plan, dry_run=True) == {}


if __name__ == "__main__":
    test_build_patch_basic()
    test_task_has_no_story_points()
    test_parent_relation_when_linked()
    test_dry_run_makes_no_network_calls()
    print("ok — 4 tests passed")
