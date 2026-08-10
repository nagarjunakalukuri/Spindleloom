#!/usr/bin/env python3
"""on_md_edit.py — the plugin's PostToolUse hook: validate spec edits, visibly.

Fires after Write/Edit. Exits 0 fast unless the edited file is a markdown document
(machinery dotdirs excluded); for spec edits it runs the traceability gate
(validate_reqs, incl. the requirement-quality lint) and the RTM presence check
(build_rtm --check) against the project root, and SURFACES any problems on stderr
with exit 2 — Claude Code feeds that back to the model, so drift is corrected in
the same turn instead of discovered at commit time. Advisory, not blocking:
PostToolUse cannot undo the edit; it makes the model fix it.

Reads the hook payload from stdin (tool_input.file_path). Stdlib-only.
"""
import json
import os
import subprocess
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    fp = (payload.get("tool_input") or {}).get("file_path", "")
    if not fp or not fp.endswith(".md"):
        return 0
    parts = Path(fp).parts
    if any(p.startswith(".") for p in parts) or "templates" in parts:
        return 0  # machinery / template edits are not spec content

    root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    problems = []
    for script, args in (("validate_reqs.py", [root]),
                         ("build_rtm.py", [root, "--check"])):
        p = HERE / script
        if not p.is_file():
            continue
        r = subprocess.run([sys.executable, str(p), *args],
                           capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            problems.append(f"[{script}]\n{(r.stdout + r.stderr).strip()}")

    if problems:
        print("spec gate (sloom): the last .md edit leaves the project failing "
              "these checks — fix before moving on:\n" + "\n\n".join(problems),
              file=sys.stderr)
        return 2  # PostToolUse: stderr is fed back to the model (advisory, visible)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a hook must never hard-crash the editing loop
        print(f"spec gate (sloom): hook error (non-fatal): {e}", file=sys.stderr)
        sys.exit(0)
