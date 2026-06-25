#!/usr/bin/env python3
"""
validate_reqs.py — spec traceability & requirement-ID validator.

Generic, dependency-free (Python 3 stdlib only). Validates a spec folder against
the conventions in project_guides/BEST-PRACTICES.md:

  1. Req-IDs follow  <DOC>-<AREA>-<NUM>   (e.g. FRD-AUTH-012, SR-PERF-004)
  2. No duplicate Req-IDs across the set
  3. RTM coverage: every FRD-* / SR-* requirement ID appears in RTM.md
  4. No broken references: an ID cited in RTM.md that is defined nowhere
  5. PBI orphans: a PBI defined in a backlog doc but not traced in RTM.md (scope creep)
  6. ADR reference integrity: every ADR-NNNN cited has a defining adr-NNNN-*.md file

The parsing/audit logic lives in `rtm_core.py` (shared with the MCP server); this
file is the CLI/CI/hook front-end that formats the audit and sets the exit code.

Usage:
    python validate_reqs.py <spec-folder>        # audit a folder
    python validate_reqs.py <file1.md> <file2.md> # audit specific files (their folder's RTM is used)

Exit code 0 = clean, 1 = problems found. Safe to use as a CI gate or a
Claude Code hook (see HOOKS.md). It only reads files; it never writes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402


def find_spec_root(args):
    """Resolve a folder from the args (folder, or the parent of given files)."""
    if not args:
        return Path(".")
    p = Path(args[0])
    return p if p.is_dir() else p.parent


def main(argv):
    project_root = find_spec_root(argv[1:])
    root = rtm_core.resolve_docs_root(project_root)
    if not rtm_core.markdown_files(root):
        print(f"validate_reqs: no .md files in {root}")
        return 0

    rep = rtm_core.audit(root)
    conf = rtm_core.conformance(project_root)
    problems = [p["message"] for p in rep["problems"]] + conf["problems"]
    test_cov_line = rep["test_coverage_line"]
    advisories = rep["advisories"] + conf["advisories"]
    n_ids, n_files = rep["counts"]["req_ids"], rep["counts"]["files"]

    if problems:
        print(f"validate_reqs: {len(problems)} issue(s) in {root}/")
        for p in problems:
            print("  - " + p)
        if test_cov_line:
            print(f"  {test_cov_line}")
        for a in advisories:
            print("  · " + a)  # advisory — does not affect exit code
        print(f"\n  ({n_ids} unique Req-IDs scanned across {n_files} files)")
        return 1

    print(f"validate_reqs: OK — {n_ids} Req-IDs, traceability intact in {root}/")
    if test_cov_line:
        print(f"  {test_cov_line}")
        for a in advisories:
            print("  · " + a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
