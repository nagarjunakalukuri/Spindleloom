#!/usr/bin/env python3
"""
azure_boards_adapter.py — Spindleloom: the live Azure Boards push() for emit_backlog.py (IMP-007).

emit_backlog.py field-maps backlog.md -> tracker-agnostic work-item payloads and leaves the
network push to "YOUR adapter". This IS that adapter for Azure DevOps Boards — the last mile,
made real. Pair them:

    backlog.md --emit_backlog.plan--> work-item payloads --push (here)--> {PBI-ID: work-item-id}
                                                                     --emit_backlog.writeback--> RTM

Stdlib only (urllib) — no azure SDK. Network writes happen ONLY with --apply and full creds.

Config (env):
    AZURE_DEVOPS_ORG_URL   e.g. https://dev.azure.com/your-org   (or AZURE_DEVOPS_ORG=your-org)
    AZURE_DEVOPS_PROJECT   the project name
    AZURE_DEVOPS_PAT       a Personal Access Token with **Work Items (Read, write, & manage)** scope (IMP-008)

Usage:
    python hooks/azure_boards_adapter.py <backlog.md>                        # dry-run: what it WOULD create
    python hooks/azure_boards_adapter.py <backlog.md> --apply                # create work items (needs creds)
    python hooks/azure_boards_adapter.py <backlog.md> --apply --link-epics --rtm docs/RTM.md

Caveats (IMP-008):
  - Iteration / Area paths are NOT created here — pre-create them or assign in Boards.
  - StoryPoints is set only for User Story / Bug (Task uses Remaining Work; left unset).
  - Headless/agent runs that --apply perform NETWORK WRITES — pre-approve the command in the runner.
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_backlog  # noqa: E402  (reuse parse / plan / writeback)

API = "7.1"


def build_patch(wi, parent_url=None):
    """Tracker-agnostic work-item payload -> Azure JSON-Patch document. Pure & offline-testable.
    Acceptance criteria land in their OWN field (never folded into Description); story points only
    for non-Task; the source ref + PBI id become tags so the item is findable by its source."""
    ops = []

    def add(path, value):
        if value is not None and value != "":
            ops.append({"op": "add", "path": path, "value": value})

    add("/fields/System.Title", wi["title"])
    add("/fields/System.Description", wi.get("description"))
    add("/fields/Microsoft.VSTS.Common.AcceptanceCriteria", wi.get("acceptance_criteria"))
    add("/fields/Microsoft.VSTS.Common.Priority", wi.get("priority"))
    if wi["work_item_type"] != "Task":
        add("/fields/Microsoft.VSTS.Scheduling.StoryPoints", wi.get("story_points"))
    tags = list(wi.get("tags") or [])
    if wi.get("source_ref"):
        tags.append(wi["source_ref"])
    tags.append(wi["pbi_id"])  # findable by its source PBI id
    deduped = list(dict.fromkeys(t for t in tags if t))
    if deduped:
        add("/fields/System.Tags", "; ".join(deduped))
    if parent_url:
        ops.append({"op": "add", "path": "/relations/-",
                    "value": {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": parent_url}})
    return ops


def _cfg():
    org_url = os.environ.get("AZURE_DEVOPS_ORG_URL")
    if not org_url and os.environ.get("AZURE_DEVOPS_ORG"):
        org_url = "https://dev.azure.com/" + os.environ["AZURE_DEVOPS_ORG"]
    return org_url, os.environ.get("AZURE_DEVOPS_PROJECT"), os.environ.get("AZURE_DEVOPS_PAT")


def _post(url, body, pat):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json-patch+json",
                 "Authorization": "Basic " + base64.b64encode((":" + pat).encode()).decode()})
    with urllib.request.urlopen(req) as r:  # noqa: S310 (https only, user-supplied org)
        return json.loads(r.read().decode("utf-8"))


def _create(org_url, project, pat, wi_type, patch):
    url = (f"{org_url}/{urllib.parse.quote(project)}/_apis/wit/workitems/"
           f"{urllib.parse.quote('$' + wi_type)}?api-version={API}")
    return _post(url, patch, pat)


def push(plan, dry_run=True, link_epics=False):
    """Create one Azure Boards work item per plan['work_items']; return {PBI-ID: work-item-id}.
    dry_run (default) makes NO network calls — it prints the per-item plan and returns {}."""
    org_url, project, pat = _cfg()
    live = (not dry_run) and all((org_url, project, pat))
    if (not dry_run) and (not live):
        print("!! refusing to --apply: set AZURE_DEVOPS_ORG_URL (or ORG), AZURE_DEVOPS_PROJECT, "
              "AZURE_DEVOPS_PAT (Work Items read+write scope)", file=sys.stderr)
        return {}
    id_map, epics = {}, {}
    for wi in plan["work_items"]:
        parent_url = None
        if link_epics and wi.get("parent_epic"):
            slug = wi["parent_epic"]
            if slug not in epics and live:
                ep = _create(org_url, project, pat, "Epic", build_patch(
                    {"title": f"Epic: {slug}", "work_item_type": "Epic",
                     "tags": [slug.lower()], "pbi_id": f"EPIC-{slug}"}))
                epics[slug] = ep["url"]
            parent_url = epics.get(slug)
        patch = build_patch(wi, parent_url)
        if live:
            res = _create(org_url, project, pat, wi["work_item_type"], patch)
            id_map[wi["pbi_id"]] = str(res["id"])
            print(f"  created #{res['id']}  {wi['pbi_id']}  ({wi['work_item_type']})")
        else:
            print(f"  [dry-run] would create {wi['work_item_type']:10} {wi['pbi_id']}  ({len(patch)} fields)")
    return id_map


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__.strip().split("\n\n")[0])
        print("\nusage: azure_boards_adapter.py <backlog.md> [--apply] [--link-epics] [--rtm <file>]")
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
        rtm.write_text(emit_backlog.writeback(rtm.read_text(encoding="utf-8"), id_map), encoding="utf-8")
        print(f"writeback: recorded {len(id_map)} id(s) in {rtm}")
    elif id_map:
        print(json.dumps(id_map, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
