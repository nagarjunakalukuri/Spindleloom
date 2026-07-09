#!/usr/bin/env python3
"""sloom — the one front door to the toolkit's CLIs.

One front door to the toolkit's CLIs. `sloom check` detects what kind of repo it's in and runs
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
    sloom context   <args…>     sync_context_log   (--import after pull / --export backfill)
    sloom graph                 validate_graph     (fleet self-check)
    sloom targets   <args…>     build_harness_artifacts (bundles / --check)
    sloom index                 regenerate INDEX + HELP + handoffs
    sloom run status  <run-id> [<root>]                  the distributed-run ledger:
    sloom run advance <run-id> --agent <name> --status done
                      [--artifact <path>] [--note <txt>] [<root>]
                                what's runnable/blocked; flip a step (refuses while a
                                required upstream isn't done or a crossed phase boundary
                                lacks its acceptance — humans advance a run without an
                                LLM, but can't skip the graph)
    sloom approve <phase> [--feature <slug>] --role <role> --by "<name>"
                  [--verdict ACCEPTED] [--covers <paths>] [--notify-tracker] [<root>]
                                record a phase-boundary acceptance token
                                (.spindleloom/approvals/<feature>/<phase>.md);
                                --notify-tracker mirrors it as a work-item comment

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
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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
    "context": "sync_context_log.py",
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
            # md<->tracker drift, once a backlog exists and the RTM carries a mapping column
            docs = Path(rtm_core.resolve_docs_root(root))
            backlogs = sorted(p for p in docs.rglob("*backlog*.md")
                              if not any(part.startswith(".") for part in p.relative_to(docs).parts))
            rtm = docs / "RTM.md"
            if backlogs and rtm.is_file() and \
                    "azure" in rtm.read_text(encoding="utf-8", errors="ignore").lower():
                battery.append(("emit_backlog.py", ["check", str(backlogs[0]), "--rtm", str(rtm)]))
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


# ---------------------------------------------------------------- distributed runs
# The ledger shape run-orchestrator writes to .spindleloom/runs/<run-id>.json:
#   {"run_id": ..., "objective": ..., "status": "active", "feature": "<slug|project>",
#    "ledger": [{"agent": "frd-writer", "status": "pending|running|done|blocked",
#                "upstream": ["prd-writer"], "gate": "DoR"|null,
#                "produced": null|"path", "notes": ""}, ...],
#    "decision_log": ["<iso-date> — <what/why>", ...]}
# This CLI lets a TEAMMATE check/advance the run without an LLM — the graph rules
# (an agent runs only when its upstreams are done) are enforced, not advisory. The
# top-level "feature" key is the acceptance namespace: a step with requires_acceptance
# is gated on .spindleloom/approvals/<feature>/<phase>.md, so it MUST match the --feature
# slug passed to `sloom approve` (defaults to "project" when unset).

def _load_run(run_id, root):
    p = Path(root) / ".spindleloom" / "runs" / f"{run_id}.json"
    if not p.is_file():
        runs = sorted(x.stem for x in (Path(root) / ".spindleloom" / "runs").glob("*.json")) \
            if (Path(root) / ".spindleloom" / "runs").is_dir() else []
        hint = f" — known runs: {', '.join(runs)}" if runs else " — no runs started yet"
        raise SystemExit(f"sloom run: no ledger at {p}{hint}")
    import json
    return p, json.loads(p.read_text(encoding="utf-8"))


def _with_run_lock(p, fn):
    """Serialize a read-modify-write of the run ledger across teammates. An O_EXCL lock
    file is an atomic cross-platform mutex; the actual write uses os.replace (atomic), so a
    concurrent `sloom run advance` can never clobber a step another teammate just recorded."""
    import os
    import time
    lock = p.with_name(p.name + ".lock")
    for _ in range(100):
        try:
            os.close(os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            time.sleep(0.05)
    else:
        raise SystemExit(f"sloom run: {lock.name} held too long — another writer is busy; retry")
    try:
        return fn()
    finally:
        try:
            os.unlink(lock)
        except OSError:
            pass


def _done_agents(state):
    return {row["agent"] for row in state.get("ledger", []) if row.get("status") == "done"}


def _missing_upstreams(row, state):
    return [u for u in row.get("upstream", []) if u not in _done_agents(state)]


def run_cmd(rest):
    if not rest or rest[0] not in ("status", "advance"):
        print("usage: sloom run status <run-id> [<root>]\n"
              "       sloom run advance <run-id> --agent <name> --status <done|running|blocked>\n"
              "                         [--artifact <path>] [--note <text>] [<root>]")
        return 2
    sub = rest[0]
    VALUE_FLAGS = {"--agent", "--status", "--artifact", "--note"}
    args, i = [], 1
    while i < len(rest):  # positionals only — value-flags consume their value, booleans don't
        t = rest[i]
        if t.startswith("--"):
            i += 2 if (t in VALUE_FLAGS and i + 1 < len(rest)) else 1
        else:
            args.append(t)
            i += 1
    if not args:
        print("sloom run: missing <run-id>")
        return 2
    run_id, root = args[0], (args[1] if len(args) > 1 else ".")

    def opt(name, default=None):
        if name in rest:
            j = rest.index(name)
            return rest[j + 1] if j + 1 < len(rest) else default
        return default

    p, state = _load_run(run_id, root)

    if sub == "status":
        print(f"run {state.get('run_id', run_id)} — {state.get('status', '?')} — "
              f"{state.get('objective', '')}".rstrip(" —"))
        runnable, blocked = [], []
        for row in state.get("ledger", []):
            st = row.get("status", "pending")
            mark = {"done": "✓", "running": "▶"}.get(st, "·")
            missing = _missing_upstreams(row, state)
            print(f"  {mark} {row['agent']:28} {st:8} "
                  f"{('gate: ' + row['gate']) if row.get('gate') else '':14} "
                  f"{row.get('produced') or ''}".rstrip())
            if st == "pending":
                (blocked if missing else runnable).append((row["agent"], missing))
        print("runnable now: " + (", ".join(a for a, _ in runnable) or "(none)"))
        for a, missing in blocked:
            print(f"blocked: {a} — waiting on {', '.join(missing)}")
        # B3: close the flag loop — a FLAG(owner) against an already-done step is unclosed
        # re-work; surface it so the run loops back instead of shipping the gap.
        flagged = _scan_flags(root)
        done_agents = {r["agent"] for r in state.get("ledger", []) if r.get("status") == "done"}
        rework = sorted(a for a in flagged if a in done_agents)
        if rework:
            print("re-work (flagged done steps — re-dispatch these):")
            for a in rework:
                print(f"  ! {a} — {len(flagged[a])} open flag(s) against a done step (see: sloom flags)")
        return 0

    # advance — the whole read-modify-write runs under a cross-process lock, so a
    # concurrent teammate's `advance` cannot clobber a step just recorded (lost update).
    agent, new_status = opt("--agent"), opt("--status")
    if not agent or new_status not in ("done", "running", "blocked", "pending"):
        print("sloom run advance: need --agent <name> and --status <done|running|blocked|pending>")
        return 2

    def _advance_locked():
        _, state = _load_run(run_id, root)  # re-read fresh inside the lock, not the pre-lock copy
        row = next((r for r in state.get("ledger", []) if r.get("agent") == agent), None)
        if row is None:
            print(f"sloom run: agent '{agent}' is not in this run's ledger")
            return 2
        if new_status in ("done", "running"):
            missing = _missing_upstreams(row, state)
            if missing:
                print(f"sloom run: REFUSED — {agent} requires upstream(s) not yet done: "
                      f"{', '.join(missing)}. The graph is the gate; finish those first.")
                return 1
            # a step crossing a phase boundary needs that boundary's acceptance token —
            # the same gate validate_gates --accepted checks and run-orchestrator enforces
            need_phase = row.get("requires_acceptance")
            if need_phase:
                feature = state.get("feature", "project")
                tok = Path(root) / ".spindleloom" / "approvals" / feature / f"{need_phase}.md"
                ok = tok.is_file() and __import__("re").search(
                    r"(?im)^\**\s*verdict\s*\**\s*[:|]\s*\**\s*ACCEPTED\b",
                    tok.read_text(encoding="utf-8", errors="ignore"))
                if not ok:
                    print(f"sloom run: REFUSED — {agent} crosses the '{need_phase}' phase "
                          f"boundary but no ACCEPTED token exists at "
                          f".spindleloom/approvals/{feature}/{need_phase}.md. The accountable "
                          f"role accepts first: sloom approve {need_phase} --feature {feature} "
                          f"--role <role> --by \"<name>\"")
                    return 1
        row["status"] = new_status
        if opt("--artifact"):
            row["produced"] = opt("--artifact")
        if opt("--note"):
            row["notes"] = opt("--note")
        from datetime import date
        state.setdefault("decision_log", []).append(
            f"{date.today().isoformat()} — {agent} → {new_status}"
            + (f" ({opt('--artifact')})" if opt("--artifact") else "")
            + (f" — {opt('--note')}" if opt("--note") else ""))
        import json
        sys.path.insert(0, str(HERE))
        import emit_backlog
        emit_backlog.atomic_write(p, json.dumps(state, indent=2, ensure_ascii=False) + "\n")
        print(f"sloom run: {agent} → {new_status} recorded in {p.name}")
        return 0

    return _with_run_lock(p, _advance_locked)


# ---------------------------------------------------------------- phase acceptance
# The four upstream phases (discovery, requirements, design, planning) have no execution
# evidence — their gate is a named human's acceptance. `sloom approve` writes the token
# the enforcement side (validate_gates --accepted, sloom run advance, run-orchestrator)
# checks. Local token = canonical; --notify-tracker mirrors it as a COMMENT on the mapped
# work items (state stays owned by the tracker's own workflow).

PHASES = ("discovery", "requirements", "design", "planning",
          "build", "test", "review", "release", "operate")


def approve_cmd(rest):
    VALUE_FLAGS = {"--feature", "--role", "--by", "--verdict", "--covers", "--notes"}
    args, i = [], 0
    while i < len(rest):
        t = rest[i]
        if t.startswith("--"):
            i += 2 if (t in VALUE_FLAGS and i + 1 < len(rest)) else 1
        else:
            args.append(t)
            i += 1
    if not args or args[0] not in PHASES:
        print(f"usage: sloom approve <phase> [--feature <slug>] --role <role> --by \"<name>\"\n"
              f"                     [--verdict ACCEPTED|REJECTED|CHANGES-REQUESTED]\n"
              f"                     [--covers <paths>] [--notes <text>] [--notify-tracker] [<root>]\n"
              f"       phases: {', '.join(PHASES)}")
        return 2
    phase_name, root = args[0], (args[1] if len(args) > 1 else ".")

    def opt(name, default=None):
        if name in rest:
            j = rest.index(name)
            return rest[j + 1] if j + 1 < len(rest) else default
        return default

    feature = opt("--feature", "project")
    role, by = opt("--role"), opt("--by")
    verdict = (opt("--verdict", "ACCEPTED") or "ACCEPTED").upper()
    if not role or not by:
        print("sloom approve: --role and --by are required — acceptance is a named human's act")
        return 2
    from datetime import date
    tok = Path(root) / ".spindleloom" / "approvals" / feature / f"{phase_name}.md"
    tok.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Acceptance — {phase_name} ({feature})", "",
             f"Verdict: {verdict}", f"By: {by}", f"Role: {role}",
             f"Date: {date.today().isoformat()}"]
    if opt("--covers"):
        lines.append(f"Covers: {opt('--covers')}")
    if opt("--notes"):
        lines.append(f"Notes: {opt('--notes')}")
    tok.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sloom approve: {verdict} recorded at {tok}")

    if "--notify-tracker" in rest:
        return _notify_tracker(root, feature, phase_name, verdict, by, role)
    return 0


def _notify_tracker(root, feature, phase_name, verdict, by, role):
    """Mirror the acceptance as a comment on the feature's mapped work items."""
    import os
    sys.path.insert(0, str(HERE))
    import emit_backlog
    import rtm_core
    rtm = Path(rtm_core.resolve_docs_root(root)) / "RTM.md"
    id_map = emit_backlog.read_id_map(rtm.read_text(encoding="utf-8", errors="ignore")) \
        if rtm.is_file() else {}
    slug = "".join(c for c in feature.lower() if c.isalnum())

    def _for_feature(pid):
        # Match the feature against the PBI's own area segment (PBI-<AREA>-<NUM>), both
        # directions, so 'user-auth' matches area 'AUTH'. NEVER fall back to every item —
        # a slug that matches nothing must comment on nothing, not fan out repo-wide.
        parts = pid.upper().split("-")
        area = parts[1].lower() if len(parts) >= 3 else "".join(c for c in pid.lower() if c.isalnum())
        return bool(slug) and (slug in area or area in slug)

    targets = {pid: wid for pid, wid in id_map.items() if _for_feature(pid)}
    if not targets:
        print(f"  · --notify-tracker: no RTM work items match feature '{feature}' — comment "
              f"skipped (nothing fanned out to unrelated items); comment manually if needed")
        return 0
    if os.environ.get("AZURE_DEVOPS_PAT"):
        import azure_boards_adapter as adapter
    elif os.environ.get("JIRA_API_TOKEN"):
        import jira_adapter as adapter
    else:
        print("  · --notify-tracker: no tracker creds in the env (AZURE_DEVOPS_PAT / "
              "JIRA_API_TOKEN) — token written locally; comment skipped")
        return 0
    text = (f"Phase '{phase_name}' {verdict} for '{feature}' by {by} ({role}) — recorded at "
            f".spindleloom/approvals/{feature}/{phase_name}.md")
    # Local idempotency: a sidecar lists work items already commented for this phase, so a
    # re-run (or a retry after a tracker hiccup) never double-posts — no tracker GET needed.
    notified_p = Path(root) / ".spindleloom" / "approvals" / feature / f"{phase_name}.notified"
    already = set(notified_p.read_text(encoding="utf-8").split()) if notified_p.is_file() else set()
    posted = []
    for pid, wid in sorted(targets.items()):
        if wid in already:
            print(f"  · comment already posted for {pid} → {wid} — skipping (idempotent)")
            continue
        try:
            sent = adapter.add_comment(wid, text)
            if sent:
                posted.append(wid)
            print(f"  · comment {'posted to' if sent else 'skipped (creds incomplete) for'} "
                  f"{pid} → {wid}")
        except Exception as e:  # a tracker hiccup must not undo the local (canonical) token
            print(f"  · comment FAILED for {pid} → {wid}: {e}")
    if posted:
        with notified_p.open("a", encoding="utf-8") as f:
            f.write(chr(10).join(posted) + chr(10))
    return 0


def _scan_flags(root):
    """Grep the docs tree for FLAG(<owner-agent>): <what> markers -> {owner: [(text, rel, line)]}.
    Shared by `sloom flags` and the run-ledger re-work loop (B3)."""
    import re as _re
    sys.path.insert(0, str(HERE))
    import rtm_core
    docs = Path(rtm_core.resolve_docs_root(root))
    pat = _re.compile(r"FLAG\(([a-z0-9-]+)\):\s*(.+?)\s*$")
    by_agent = {}
    for pth in rtm_core.markdown_files(docs):
        try:
            rel = pth.relative_to(docs).as_posix()
        except ValueError:
            rel = pth.name
        for i, line in enumerate(pth.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            m = pat.search(line)
            if m:
                by_agent.setdefault(m.group(1), []).append((m.group(2).strip(), rel, i))
    return by_agent


def flags_cmd(rest):
    """Open-flags register — list unresolved FLAG(<agent>): markers as a re-dispatch queue.
    A writer that finds an upstream gap it cannot fix itself leaves `FLAG(<owner-agent>): <what>`
    in its artifact; this surfaces them grouped by owner so a run (or a human) can send that
    agent back to work, closing the run2 "flags accumulate, nothing loops back" gap. Report by
    default; `--strict` exits nonzero when any flag is open (usable as a merge/run gate)."""
    args = [a for a in rest if not a.startswith("--")]
    root = Path(args[0]) if args else Path(".")
    by_agent = _scan_flags(root)
    total = sum(len(v) for v in by_agent.values())
    if not total:
        print("sloom flags: no open FLAG(<agent>): markers — nothing queued for re-dispatch")
        return 0
    print(f"sloom flags: {total} open flag(s) across {len(by_agent)} owner(s) — re-work queue:")
    for agent in sorted(by_agent):
        print(f"  -> {agent}")
        for txt, rel, ln in by_agent[agent]:
            print(f"       {rel}:{ln}  {txt}")
    return 1 if "--strict" in rest else 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("help", "--help", "-h"):
        print(__doc__)
        return 0 if len(argv) >= 2 else 2
    cmd, rest = argv[1], argv[2:]
    if cmd == "check":
        return check(rest[0] if rest else ".")
    if cmd == "run":
        return run_cmd(rest)
    if cmd == "approve":
        return approve_cmd(rest)
    if cmd == "flags":
        return flags_cmd(rest)
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
