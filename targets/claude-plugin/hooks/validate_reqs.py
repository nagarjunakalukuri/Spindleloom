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

It also runs the 29148/INCOSE requirement-quality lint (the `requirement-quality`
skill's mechanizable rules): vague-adjective ban-list and non-singular "shall …
and/or …" smells on requirement-defining lines. Advisory by default; `--strict`
promotes quality findings to failures.

Usage:
    python validate_reqs.py <spec-folder>            # audit a folder
    python validate_reqs.py <spec-folder> --strict   # quality lint also fails the run
    python validate_reqs.py <file1.md> <file2.md>    # audit specific files (their folder's RTM is used)

Exit code 0 = clean, 1 = problems found. Safe to use as a CI gate or a
Claude Code hook (see HOOKS.md). It only reads files; it never writes.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402

# The requirement-quality skill's ban-list, mechanized (word-boundary, case-insensitive).
VAGUE = re.compile(r"\b(fast|user-friendly|intuitive|robust|seamless|easy|easily|quick|quickly)\b", re.I)
SHALL_COMPOUND = re.compile(r"\bshall\b[^.|]*\b(and|or)\b", re.I)


def quality_lint(root):
    """Lint requirement-DEFINING lines: vague adjectives and compound shall-clauses.
    Returns advisory strings; the caller decides whether they fail the run."""
    findings = []
    files = rtm_core.markdown_files(root)
    all_ids = rtm_core.collect_ids(files, root)
    defined_in = rtm_core.definition_files(all_ids)
    seen = set()
    for rid, fs in sorted(defined_in.items()):
        if rid.split("-", 1)[0] not in rtm_core.COVERED_DOCS or not fs:
            continue
        for rel in fs:
            p = root / rel
            if not p.exists() or p.name == rtm_core.RTM_NAME:
                continue
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if rid not in line:
                    continue
                m = VAGUE.search(line)
                if m and (rid, "vague") not in seen:
                    seen.add((rid, "vague"))
                    findings.append(f"QUALITY    {rid} ({rel}): vague adjective '{m.group(1)}' — replace with a measurable target")
                if SHALL_COMPOUND.search(line) and (rid, "compound") not in seen:
                    seen.add((rid, "compound"))
                    findings.append(f"QUALITY    {rid} ({rel}): 'shall … and/or …' — may bundle two obligations; split if so")
                break  # lint the first (defining) line per file only
    return findings


def find_spec_root(args):
    """Resolve a folder from the args (folder, or the parent of given files)."""
    if not args:
        return Path(".")
    p = Path(args[0])
    return p if p.is_dir() else p.parent


def main(argv):
    strict = "--strict" in argv
    args = [a for a in argv[1:] if a != "--strict"]
    project_root = find_spec_root(args)
    root = rtm_core.resolve_docs_root(project_root)
    if not rtm_core.markdown_files(root):
        print(f"validate_reqs: no .md files in {root}")
        return 0

    rep = rtm_core.audit(root)
    conf = rtm_core.conformance(project_root)
    problems = [p["message"] for p in rep["problems"]] + conf["problems"]
    test_cov_line = rep["test_coverage_line"]
    advisories = rep["advisories"] + conf["advisories"]
    quality = quality_lint(root)
    if strict:
        problems += quality
    else:
        advisories += quality
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
        print("  · " + a)  # advisory — does not affect exit code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
