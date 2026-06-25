#!/usr/bin/env python3
"""
jira_adapter.py — Wheelwright: the live Jira push() for emit_backlog.py.

emit_backlog.py field-maps backlog.md → tracker-agnostic work-item payloads and leaves the
network push to "YOUR adapter". This IS that adapter for Jira Cloud (REST API v3) — the last
mile, made real. Pair them:

    backlog.md --emit_backlog.plan--> work-item payloads --push (here)--> {PBI-ID: issue-key}
                                                                     --emit_backlog.writeback--> RTM

Stdlib only (urllib + json) — no jira-python SDK. Network writes happen ONLY with --apply
and full creds.

Config (env):
    JIRA_BASE_URL      e.g. https://your-org.atlassian.net
    JIRA_PROJECT_KEY   the project key, e.g. PROJ
    JIRA_USER_EMAIL    email of the service account
    JIRA_API_TOKEN     an Atlassian API token (https://id.atlassian.com/manage-profile/security/api-tokens)
                       — NOT your password; needs Create/Edit Issues scope on the project

    Optional field customisation (Jira field IDs vary per instance — check via /rest/api/3/field):
    JIRA_SP_FIELD      Story Points field id  (default: story_points)
    JIRA_AC_FIELD      Acceptance Criteria field id  (default: None → appended to description)
    JIRA_EPIC_LINK_FIELD  Epic Link field id for classic projects (default: None → use parent)

Usage:
    python hooks/jira_adapter.py <backlog.md>                        # dry-run: what it WOULD create
    python hooks/jira_adapter.py <backlog.md> --apply                # create issues (needs creds)
    python hooks/jira_adapter.py <backlog.md> --apply --link-epics --rtm docs/RTM.md
    python hooks/jira_adapter.py --list-fields                       # print all field ids for your instance

Caveats:
  - Iteration / Sprint fields are NOT set here — assign in Jira or extend FIELD_MAP.
  - Story Points is set only for Story / Bug (Task uses time tracking; left unset).
  - Acceptance Criteria is stored in JIRA_AC_FIELD if set, otherwise appended to description.
  - Headless/agent runs that --apply perform NETWORK WRITES — pre-approve the command in the runner.
  - Jira Cloud only. Jira Server/Data Center uses a different auth scheme.
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_backlog  # noqa: E402  (reuse parse / plan / writeback)

API = "rest/api/3"

# Work-item-type → Jira issue type name mapping.
# Extend or override via JIRA_TYPE_MAP env var (JSON dict string).
DEFAULT_TYPE_MAP = {
    "User Story": "Story",
    "Story":      "Story",
    "Bug":        "Bug",
    "Task":       "Task",
    "Epic":       "Epic",
    "Feature":    "Epic",
}

# Priority → Jira priority name.
DEFAULT_PRIORITY_MAP = {
    "1": "Highest",
    "2": "High",
    "3": "Medium",
    "4": "Low",
    "5": "Lowest",
}


def _to_adf(text):
    """Convert a plain-text string to a minimal Atlassian Document Format (ADF) paragraph.
    ADF is required for Jira Cloud description/comment fields in API v3."""
    if not text:
        return None
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


def build_payload(wi, parent_key=None):
    """Tracker-agnostic work-item dict → Jira issue create payload. Pure & offline-testable.

    Acceptance criteria land in their OWN field when JIRA_AC_FIELD is set (never folded into
    Description by default — mirrors the Azure adapter contract). Story Points only for
    Story/Bug; Tasks use time tracking.
    """
    type_map = json.loads(os.environ.get("JIRA_TYPE_MAP", "{}")) or DEFAULT_TYPE_MAP
    issue_type = type_map.get(wi.get("work_item_type", "Story"), "Story")

    sp_field    = os.environ.get("JIRA_SP_FIELD", "story_points")
    ac_field    = os.environ.get("JIRA_AC_FIELD")          # None → append to description
    el_field    = os.environ.get("JIRA_EPIC_LINK_FIELD")   # classic epic link field id

    proj_key = os.environ.get("JIRA_PROJECT_KEY", "")
    fields = {
        "project":   {"key": proj_key},
        "summary":   wi["title"],
        "issuetype": {"name": issue_type},
    }

    # Description (ADF)
    desc_parts = [wi.get("description") or ""]
    if not ac_field and wi.get("acceptance_criteria"):
        desc_parts.append("\n\nAcceptance Criteria:\n" + wi["acceptance_criteria"])
    combined = "\n".join(p for p in desc_parts if p).strip()
    if combined:
        fields["description"] = _to_adf(combined)

    # Acceptance Criteria in its own field (when configured)
    if ac_field and wi.get("acceptance_criteria"):
        fields[ac_field] = _to_adf(wi["acceptance_criteria"])

    # Story Points (Story + Bug only)
    if issue_type in ("Story", "Bug") and wi.get("story_points") is not None:
        try:
            fields[sp_field] = float(wi["story_points"])
        except (TypeError, ValueError):
            pass

    # Priority
    raw_priority = str(wi.get("priority", ""))
    pri_name = DEFAULT_PRIORITY_MAP.get(raw_priority)
    if pri_name:
        fields["priority"] = {"name": pri_name}

    # Labels (tags + source ref + PBI id — same approach as Azure adapter)
    tags = list(wi.get("tags") or [])
    if wi.get("source_ref"):
        tags.append(wi["source_ref"])
    tags.append(wi["pbi_id"])
    labels = list(dict.fromkeys(t for t in tags if t))
    if labels:
        # Jira labels cannot contain spaces
        fields["labels"] = [lbl.replace(" ", "_") for lbl in labels]

    # Epic link (classic projects use a custom field; next-gen uses parent)
    if parent_key:
        if el_field:
            fields[el_field] = parent_key          # classic: "Epic Link" custom field
        else:
            fields["parent"] = {"key": parent_key} # next-gen / team-managed

    return {"fields": fields}


def _cfg():
    return (
        os.environ.get("JIRA_BASE_URL", "").rstrip("/"),
        os.environ.get("JIRA_PROJECT_KEY"),
        os.environ.get("JIRA_USER_EMAIL"),
        os.environ.get("JIRA_API_TOKEN"),
    )


def _auth_header(email, token):
    return "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()


def _post(base_url, path, body, email, token):
    url = f"{base_url}/{API}/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={
            "Content-Type":  "application/json",
            "Accept":        "application/json",
            "Authorization": _auth_header(email, token),
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Jira API {exc.code} on {url}: {body_text}") from exc


def list_fields(base_url, email, token):
    """Print all field id/name pairs for this Jira instance — helps find SP and AC field ids."""
    url = f"{base_url}/{API}/field"
    req = urllib.request.Request(
        url, method="GET",
        headers={"Accept": "application/json", "Authorization": _auth_header(email, token)},
    )
    with urllib.request.urlopen(req) as r:
        fields = json.loads(r.read().decode("utf-8"))
    for f in sorted(fields, key=lambda x: x.get("name", "")):
        print(f"  {f['id']:40}  {f['name']}")


def push(plan, dry_run=True, link_epics=False):
    """Create one Jira issue per plan['work_items']; return {PBI-ID: issue-key}.
    dry_run (default) makes NO network calls — it prints the per-item plan and returns {}."""
    base_url, project, email, token = _cfg()
    live = (not dry_run) and all((base_url, project, email, token))
    if (not dry_run) and (not live):
        print(
            "!! refusing to --apply: set JIRA_BASE_URL, JIRA_PROJECT_KEY, "
            "JIRA_USER_EMAIL, JIRA_API_TOKEN",
            file=sys.stderr,
        )
        return {}

    id_map, epics = {}, {}
    for wi in plan["work_items"]:
        parent_key = None
        if link_epics and wi.get("parent_epic"):
            slug = wi["parent_epic"]
            if slug not in epics and live:
                ep_payload = build_payload({
                    "title": f"Epic: {slug}",
                    "work_item_type": "Epic",
                    "tags": [slug.lower()],
                    "pbi_id": f"EPIC-{slug}",
                })
                ep = _post(base_url, "issue", ep_payload, email, token)
                epics[slug] = ep["key"]
                print(f"  created epic  {ep['key']}  EPIC-{slug}")
            parent_key = epics.get(slug)

        payload = build_payload(wi, parent_key)
        if live:
            res = _post(base_url, "issue", payload, email, token)
            id_map[wi["pbi_id"]] = res["key"]
            print(f"  created  {res['key']}  {wi['pbi_id']}  ({wi['work_item_type']})")
        else:
            n_fields = len(payload.get("fields", {}))
            print(f"  [dry-run] would create {wi['work_item_type']:10} {wi['pbi_id']}  ({n_fields} fields)")
    return id_map


def main(argv):
    # --list-fields mode: print field ids so the user can set JIRA_SP_FIELD / JIRA_AC_FIELD
    if "--list-fields" in argv:
        base_url, _, email, token = _cfg()
        if not all((base_url, email, token)):
            print("set JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN to list fields",
                  file=sys.stderr)
            return 2
        list_fields(base_url, email, token)
        return 0

    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__.strip().split("\n\n")[0])
        print("\nusage: jira_adapter.py <backlog.md> [--apply] [--link-epics] [--rtm <file>]")
        print("       jira_adapter.py --list-fields")
        return 2

    p = emit_backlog.plan(Path(args[0]).read_text(encoding="utf-8"))
    print(f"{p['count']} work item(s) planned; {len(p['warnings'])} warning(s).")
    for w in p["warnings"]:
        print("  warn:", w)

    dry = "--apply" not in flags
    id_map = push(p, dry_run=dry, link_epics="--link-epics" in flags)

    if dry:
        print("Dry-run — no network calls. Re-run with --apply (and creds) to create + write back.")
        return 0

    if id_map and "--rtm" in argv:
        rtm = Path(argv[argv.index("--rtm") + 1])
        rtm.write_text(emit_backlog.writeback(rtm.read_text(encoding="utf-8"), id_map),
                       encoding="utf-8")
        print(f"writeback: recorded {len(id_map)} key(s) in {rtm}")
    elif id_map:
        print(json.dumps(id_map, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
