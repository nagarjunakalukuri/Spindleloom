#!/usr/bin/env python3
"""sloom — the one front door to the toolkit's CLIs.

Fifteen scripts, one entry. `sloom check` detects what kind of repo it's in and runs
the right gate battery; every other subcommand forwards to its tool unchanged, so the
individual contracts (and muscle memory) still work.

    sloom check [<root>]        repo-aware gate battery (see below)
    sloom reqs      <args…>     validate_reqs      (traceability + quality lint)
    sloom rtm       <args…>     build_rtm          (seed / --check)
    sloom gates     <args…>     validate_gates     (verifications / --release / --context)
    sloom pack      <args…>     build_context_pack (per-agent context manifest)
    sloom registry  <args…>     build_artifact_registry (catalog / --baseline / --check)
    sloom scaffold  <args…>     scaffold           (greenfield / migrate)
    sloom backlog   <args…>     emit_backlog       (docs -> tracker)
    sloom graph                 validate_graph     (fleet self-check)
    sloom targets   <args…>     build_harness_artifacts (bundles / --check)
    sloom index                 regenerate INDEX + HELP + handoffs

`sloom check` batteries:
  toolkit repo  (agents/ + hooks/validate_graph.py present)
      -> validate_graph · build_handoffs --check · build_harness_artifacts --check
  adopter repo  (anything else)
      -> validate_reqs · build_rtm --check · registry --check (when a catalog exists)
         · validate_gates (artifact audit)
Exit = 0 only if every gate in the battery passed. Stdlib-only.
"""
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

HERE = Path(__file__).resolve().parent

TOOLS = {
    "reqs": "validate_reqs.py",
    "rtm": "build_rtm.py",
    "gates": "validate_gates.py",
    "pack": "build_context_pack.py",
    "registry": "build_artifact_registry.py",
    "scaffold": "scaffold.py",
    "backlog": "emit_backlog.py",
    "graph": "validate_graph.py",
    "targets": "build_harness_artifacts.py",
}


def run(script, args):
    return subprocess.call([sys.executable, str(HERE / script), *args])


def check(root):
    root = Path(root)
    if (root / "agents").is_dir() and (root / "hooks" / "validate_graph.py").is_file():
        print("sloom check: toolkit repo detected — fleet battery\n")
        battery = [("validate_graph.py", []),
                   ("build_handoffs.py", ["--check"]),
                   ("build_harness_artifacts.py", ["--check"]),
                   ("validate_targets.py", [])]
    else:
        print(f"sloom check: adopter repo — spec battery on {root}\n")
        battery = [("validate_reqs.py", [str(root)]),
                   ("build_rtm.py", [str(root), "--check"])]
        try:
            sys.path.insert(0, str(HERE))
            import rtm_core
            if (Path(rtm_core.tool_dir(root)) / "artifacts.json").exists():
                battery.append(("build_artifact_registry.py", [str(root), "--check"]))
        except ImportError:
            pass
        battery.append(("validate_gates.py", [str(root)]))

    failed = []
    for script, args in battery:
        print(f"── {script} {' '.join(args)}".rstrip())
        if run(script, args) != 0:
            failed.append(script)
        print()
    if failed:
        print(f"sloom check: FAIL — {len(failed)} gate(s) red: {', '.join(failed)}")
        return 1
    print(f"sloom check: OK — all {len(battery)} gates green.")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("help", "--help", "-h"):
        print(__doc__)
        return 0 if len(argv) >= 2 else 2
    cmd, rest = argv[1], argv[2:]
    if cmd == "check":
        return check(rest[0] if rest else ".")
    if cmd == "index":
        rc = 0
        for s in ("build_agent_index.py", "build_help.py", "build_handoffs.py"):
            rc = run(s, []) or rc
        return rc
    if cmd in TOOLS:
        return run(TOOLS[cmd], rest)
    print(f"sloom: unknown command '{cmd}' — run `sloom help`")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
