#!/usr/bin/env python3
"""
test_mcp_server.py — end-to-end smoke test for the Spindleloom MCP server.

Spawns mcp_server.py over stdio exactly as a harness would, then asserts the
expected tools/resources are registered and that representative tool calls
return data against a spec root. Exits non-zero on any failure, so it doubles
as a CI gate.

Run it (the MCP SDK is the repo's `dev` dependency, auto-installed by uv):
    uv run python hooks/test_mcp_server.py

Options:
    --spec-root PATH   project root to point the server at
                       (default: examples/healthy-meal-app)
    --server PATH      server entrypoint (default: the sibling mcp_server.py)
    --uv               launch the server via the SHIPPED launcher
                       (`uv run --with "mcp[cli]" python <server>`) instead of
                       this interpreter — validates exactly what .mcp.json runs.

Requires the MCP SDK (provided by the `dev` group; or `pip install "mcp[cli]"`).
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    import unittest
    raise unittest.SkipTest(
        'mcp SDK not installed — run via `uv run python hooks/test_mcp_server.py` '
        'or `pip install "mcp[cli]"` first.'
    )

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

EXPECTED_TOOLS = {
    "trace_requirement", "rtm_coverage", "list_requirements",
    "find_decision", "list_artifacts", "find_artifact",
    "funnel_status", "stale_artifacts", "next_req_id", "search_specs", "scaffold_project",
    "check_conformance",
}
EXPECTED_RESOURCES = {
    "rtm://current", "spindleloom://requirements", "spindleloom://artifacts",
    "spindleloom://decisions",
}


def parse_args():
    ap = argparse.ArgumentParser(description="Smoke-test the Spindleloom MCP server.")
    ap.add_argument("--spec-root", default=str(REPO / "examples" / "healthy-meal-app"))
    ap.add_argument("--server", default=str(HERE / "mcp_server.py"))
    ap.add_argument("--uv", action="store_true",
                    help="launch via the shipped `uv run --with mcp[cli]` launcher")
    return ap.parse_args()


def server_params(args):
    if args.uv:
        command, pre = "uv", ["run", "--with", "mcp[cli]", "python"]
    else:
        command, pre = sys.executable, []
    return StdioServerParameters(
        command=command,
        args=[*pre, args.server],
        env={**os.environ, "SPINDLELOOM_SPEC_ROOT": args.spec_root},
    )


async def run(args):
    failures = []

    def check(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        if not cond:
            failures.append(msg)

    async with stdio_client(server_params(args)) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"SERVER: {init.serverInfo.name} {init.serverInfo.version}")
            print(f"SPEC_ROOT: {args.spec_root}\n")

            tools = {t.name for t in (await session.list_tools()).tools}
            check(EXPECTED_TOOLS <= tools,
                  f"tools registered ({len(tools)}): missing {EXPECTED_TOOLS - tools or 'none'}")

            resources = {str(r.uri) for r in (await session.list_resources()).resources}
            check(EXPECTED_RESOURCES <= resources,
                  f"resources registered ({len(resources)}): missing {EXPECTED_RESOURCES - resources or 'none'}")

            cov = await session.call_tool("rtm_coverage", {})
            text = cov.content[0].text if cov.content else ""
            check('"req_ids"' in text, "rtm_coverage() returns coverage counts")

            reqs = await session.call_tool("list_requirements", {})
            check(reqs.content and reqs.content[0].text.strip().startswith(("[", "{")),
                  "list_requirements() returns the requirement list")

            arts = await session.call_tool("list_artifacts", {})
            check(arts.content and arts.content[0].text.strip().startswith(("[", "{")),
                  "list_artifacts() returns the artifact catalog")

            fs = await session.call_tool("funnel_status", {})
            check(bool(fs.content) and '"altitudes"' in fs.content[0].text,
                  "funnel_status() returns the altitude breakdown")

            stale = await session.call_tool("stale_artifacts", {})
            check(bool(stale.content) and '"checked"' in stale.content[0].text,
                  "stale_artifacts() returns a staleness report")

            nid = await session.call_tool("next_req_id", {"doc": "FRD", "area": "FAV"})
            check(bool(nid.content) and '"next_id"' in nid.content[0].text,
                  "next_req_id(FRD, FAV) suggests the next id")

            srch = await session.call_tool("search_specs", {"query": "Traceability"})
            check(bool(srch.content) and '"matches"' in srch.content[0].text,
                  "search_specs() returns matches")

            scaf = await session.call_tool("scaffold_project", {})
            check(bool(scaf.content) and "SPINDLELOOM_WRITABLE" in scaf.content[0].text,
                  "scaffold_project() is read-only by default (gated on SPINDLELOOM_WRITABLE)")

            res = await session.read_resource("spindleloom://decisions")
            check(bool(res.contents) and res.contents[0].text.strip().startswith(("[", "{")),
                  "spindleloom://decisions resource returns the decisions table")

            conf = await session.call_tool("check_conformance", {})
            check(bool(conf.content) and '"conformance"' in conf.content[0].text,
                  "check_conformance() returns the conformance + audit report")

    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s) failed.")
        return 1
    print("OK — all checks passed.")
    return 0


def main():
    return asyncio.run(run(parse_args()))


if __name__ == "__main__":
    sys.exit(main())
