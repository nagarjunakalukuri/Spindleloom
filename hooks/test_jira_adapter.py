#!/usr/bin/env python3
"""Tests for jira_adapter.build_payload() — pure, offline, no network."""
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jira_adapter as ja


class TestBuildPayload(unittest.TestCase):

    def setUp(self):
        # Clear any env overrides that might leak between tests.
        for key in ("JIRA_SP_FIELD", "JIRA_AC_FIELD", "JIRA_EPIC_LINK_FIELD",
                    "JIRA_TYPE_MAP", "JIRA_PROJECT_KEY"):
            os.environ.pop(key, None)
        os.environ["JIRA_PROJECT_KEY"] = "PROJ"

    def _story(self, **overrides):
        base = {
            "title": "User can reset password",
            "work_item_type": "User Story",
            "description": "As a user I want to reset my password.",
            "acceptance_criteria": "Given I am logged out, when I click reset, then I receive an email.",
            "story_points": 3,
            "priority": "2",
            "tags": ["auth"],
            "source_ref": "PRD-001",
            "pbi_id": "PBI-042",
        }
        base.update(overrides)
        return base

    def test_basic_story_fields(self):
        payload = ja.build_payload(self._story())
        f = payload["fields"]
        self.assertEqual(f["project"]["key"], "PROJ")
        self.assertEqual(f["summary"], "User can reset password")
        self.assertEqual(f["issuetype"]["name"], "Story")
        self.assertEqual(f["priority"]["name"], "High")   # priority "2" → High
        self.assertIn("PBI-042", f["labels"])
        self.assertIn("PRD-001", f["labels"])
        self.assertIn("auth", f["labels"])

    def test_ac_appended_to_description_by_default(self):
        """When JIRA_AC_FIELD is not set, AC must be appended to description, not a separate field."""
        payload = ja.build_payload(self._story())
        f = payload["fields"]
        # Description should contain AC text
        desc_text = f["description"]["content"][0]["content"][0]["text"]
        self.assertIn("Acceptance Criteria", desc_text)
        self.assertIn("reset", desc_text)
        # No custom AC field should be set
        self.assertNotIn("customfield_10040", f)

    def test_ac_in_own_field_when_configured(self):
        """When JIRA_AC_FIELD is set, AC goes there and description stays clean."""
        os.environ["JIRA_AC_FIELD"] = "customfield_10040"
        payload = ja.build_payload(self._story())
        f = payload["fields"]
        # Custom AC field should contain the criteria
        self.assertIn("customfield_10040", f)
        ac_text = f["customfield_10040"]["content"][0]["content"][0]["text"]
        self.assertIn("reset", ac_text)
        # Description should NOT contain "Acceptance Criteria" header
        desc_text = f["description"]["content"][0]["content"][0]["text"]
        self.assertNotIn("Acceptance Criteria:", desc_text)

    def test_task_has_no_story_points(self):
        """Tasks should not receive a story_points field (they use time tracking)."""
        wi = self._story(work_item_type="Task", story_points=5)
        payload = ja.build_payload(wi)
        f = payload["fields"]
        self.assertEqual(f["issuetype"]["name"], "Task")
        self.assertNotIn("story_points", f)
        self.assertNotIn("customfield_10016", f)

    def test_story_points_on_story(self):
        payload = ja.build_payload(self._story(story_points=8))
        sp_field = os.environ.get("JIRA_SP_FIELD", "story_points")
        self.assertEqual(payload["fields"][sp_field], 8.0)

    def test_parent_key_sets_parent_field(self):
        """Next-gen projects: parent_key should set fields.parent.key."""
        payload = ja.build_payload(self._story(), parent_key="PROJ-10")
        self.assertEqual(payload["fields"]["parent"]["key"], "PROJ-10")

    def test_epic_link_field_when_configured(self):
        """Classic projects: parent_key should set the configured epic link field."""
        os.environ["JIRA_EPIC_LINK_FIELD"] = "customfield_10014"
        payload = ja.build_payload(self._story(), parent_key="PROJ-5")
        f = payload["fields"]
        self.assertEqual(f["customfield_10014"], "PROJ-5")
        self.assertNotIn("parent", f)

    def test_dry_run_makes_no_network_calls(self):
        """push() in dry_run mode must not raise even without any creds."""
        plan = {
            "count": 1,
            "warnings": [],
            "work_items": [self._story()],
        }
        result = ja.push(plan, dry_run=True)
        self.assertEqual(result, {})

    def test_labels_no_spaces(self):
        """Jira labels cannot contain spaces — should be replaced with underscores."""
        wi = self._story(tags=["auth flow", "reset password"])
        payload = ja.build_payload(wi)
        for lbl in payload["fields"]["labels"]:
            self.assertNotIn(" ", lbl, f"label '{lbl}' contains a space")

    def test_adf_structure(self):
        """_to_adf should produce a valid minimal ADF document."""
        adf = ja._to_adf("hello world")
        self.assertEqual(adf["type"], "doc")
        self.assertEqual(adf["version"], 1)
        text = adf["content"][0]["content"][0]["text"]
        self.assertEqual(text, "hello world")

    def test_adf_none_on_empty(self):
        self.assertIsNone(ja._to_adf(""))
        self.assertIsNone(ja._to_adf(None))

    def test_comment_payload_is_adf(self):
        """add_comment's payload (offline): API v3 comments must be ADF, not a plain string."""
        payload = ja.build_comment("Phase 'design' ACCEPTED by N.K.")
        self.assertEqual(payload["body"]["type"], "doc")
        self.assertEqual(payload["body"]["version"], 1)
        self.assertEqual(payload["body"]["content"][0]["content"][0]["text"],
                         "Phase 'design' ACCEPTED by N.K.")

    def test_add_comment_no_creds_no_network(self):
        import os
        saved = {k: os.environ.pop(k, None)
                 for k in ("JIRA_BASE_URL", "JIRA_USER_EMAIL", "JIRA_API_TOKEN")}
        try:
            self.assertFalse(ja.add_comment("PROJ-1", "x"))  # returns False, never dials out
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


def test_push_records_partial_id_map_when_a_create_fails():
    """#4 regression: if _post fails mid-loop, items already created must still land in
    the caller's id_map -- otherwise a retry duplicates the tracker work items."""
    import emit_backlog
    backlog = """## Backlog (ordered)
| Rank | PBI ID | Type | Story / item | Acceptance criteria | Priority | Est. | Deps | Source | Ready? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PBI-A-001 | Story | first | ac | Must | 1 | - | S | yes |
| 2 | PBI-A-002 | Story | second | ac | Must | 1 | - | S | yes |
"""
    plan = emit_backlog.plan(backlog)
    calls = {"n": 0}
    def fake_post(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"key": "PROJ-1"}
        raise RuntimeError("429 rate limited")
    saved_post, saved_cfg = ja._post, ja._cfg
    ja._post = fake_post
    ja._cfg = lambda: ("https://x.atlassian.net", "PROJ", "e@x", "tok")
    id_map = {}
    try:
        try:
            ja.push(plan, dry_run=False, id_map=id_map)
        except RuntimeError:
            pass
    finally:
        ja._post, ja._cfg = saved_post, saved_cfg
    assert id_map == {"PBI-A-001": "PROJ-1"}, id_map


if __name__ == "__main__":
    unittest.main()
