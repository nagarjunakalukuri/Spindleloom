#!/usr/bin/env python3
"""test_sloom_run.py — the distributed-run CLI must enforce the graph, not just edit JSON.
status reports the runnable set; advance flips a row; advance REFUSES when a required
upstream isn't done (a teammate can't skip the graph by hand). Stdlib-only."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

LEDGER = {
    "run_id": "run-20260709-auth",
    "objective": "ship user-auth",
    "status": "active",
    "ledger": [
        {"agent": "prd-writer", "status": "done", "upstream": [], "gate": None,
         "produced": "docs/product/prd.md", "notes": ""},
        {"agent": "frd-writer", "status": "pending", "upstream": ["prd-writer"],
         "gate": None, "produced": None, "notes": ""},
        {"agent": "backlog-manager", "status": "pending", "upstream": ["frd-writer"],
         "gate": "DoR", "produced": None, "notes": ""},
    ],
    "decision_log": [],
}


def _project():
    tmp = Path(tempfile.mkdtemp(prefix="sloomrun_"))
    runs = tmp / ".spindleloom" / "runs"
    runs.mkdir(parents=True)
    (runs / "run-20260709-auth.json").write_text(
        json.dumps(LEDGER, indent=2), encoding="utf-8")
    return tmp


def _run(*args):
    return subprocess.run([sys.executable, str(HERE / "sloom.py"), "run", *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_status_reports_runnable_and_blocked():
    tmp = _project()
    try:
        r = _run("status", "run-20260709-auth", str(tmp))
        assert r.returncode == 0, r.stdout + r.stderr
        assert "runnable now: frd-writer" in r.stdout, r.stdout
        assert "blocked: backlog-manager — waiting on frd-writer" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_advance_refuses_when_upstream_not_done():
    tmp = _project()
    try:
        r = _run("advance", "run-20260709-auth", "--agent", "backlog-manager",
                 "--status", "done", str(tmp))
        assert r.returncode == 1 and "REFUSED" in r.stdout, r.stdout
        state = json.loads((tmp / ".spindleloom/runs/run-20260709-auth.json").read_text(encoding="utf-8"))
        assert state["ledger"][2]["status"] == "pending"  # unchanged on refusal
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_advance_records_step_and_unblocks_downstream():
    tmp = _project()
    try:
        r = _run("advance", "run-20260709-auth", "--agent", "frd-writer",
                 "--status", "done", "--artifact", "docs/specs/auth/frd.md", str(tmp))
        assert r.returncode == 0, r.stdout + r.stderr
        state = json.loads((tmp / ".spindleloom/runs/run-20260709-auth.json").read_text(encoding="utf-8"))
        assert state["ledger"][1]["status"] == "done"
        assert state["ledger"][1]["produced"] == "docs/specs/auth/frd.md"
        assert state["decision_log"] and "frd-writer → done" in state["decision_log"][-1]
        r2 = _run("status", "run-20260709-auth", str(tmp))
        assert "runnable now: backlog-manager" in r2.stdout, r2.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_advance_refuses_at_unaccepted_phase_boundary():
    """A step that crosses a phase boundary needs the acceptance token; approve unblocks."""
    tmp = _project()
    try:
        state = json.loads((tmp / ".spindleloom/runs/run-20260709-auth.json").read_text(encoding="utf-8"))
        state["feature"] = "user-auth"
        state["ledger"][1]["requires_acceptance"] = "requirements"
        (tmp / ".spindleloom/runs/run-20260709-auth.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8")
        r = _run("advance", "run-20260709-auth", "--agent", "frd-writer",
                 "--status", "done", str(tmp))
        assert r.returncode == 1 and "phase boundary" in r.stdout, r.stdout
        # the accountable role accepts -> the same advance now succeeds
        a = subprocess.run([sys.executable, str(HERE / "sloom.py"), "approve", "requirements",
                            "--feature", "user-auth", "--role", "product-owner",
                            "--by", "N. Kalukuri", str(tmp)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert a.returncode == 0 and "ACCEPTED recorded" in a.stdout, a.stdout
        tok = tmp / ".spindleloom/approvals/user-auth/requirements.md"
        assert tok.is_file() and "By: N. Kalukuri" in tok.read_text(encoding="utf-8")
        r2 = _run("advance", "run-20260709-auth", "--agent", "frd-writer",
                  "--status", "done", str(tmp))
        assert r2.returncode == 0, r2.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_unknown_run_lists_known_ones():
    tmp = _project()
    try:
        r = _run("status", "run-bogus", str(tmp))
        assert r.returncode != 0 and "run-20260709-auth" in (r.stdout + r.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _project_two_runnable():
    tmp = Path(tempfile.mkdtemp(prefix="sloomrun_"))
    runs = tmp / ".spindleloom" / "runs"
    runs.mkdir(parents=True)
    ledger = {"run_id": "r2", "objective": "x", "status": "active",
              "ledger": [{"agent": "a", "status": "pending", "upstream": [], "gate": None},
                         {"agent": "b", "status": "pending", "upstream": [], "gate": None}]}
    (runs / "r2.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    return tmp


def test_concurrent_advances_no_lost_update():
    """Two teammates advancing different agents at once: the cross-process lock + atomic
    write must keep BOTH updates. The pre-fix non-atomic write could clobber one."""
    tmp = _project_two_runnable()
    try:
        procs = [subprocess.Popen(
            [sys.executable, str(HERE / "sloom.py"), "run", "advance", "r2",
             "--agent", ag, "--status", st, str(tmp)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for ag, st in (("a", "done"), ("b", "running"))]
        for proc in procs:
            proc.communicate()
        state = json.loads((tmp / ".spindleloom/runs/r2.json").read_text(encoding="utf-8"))
        by = {r["agent"]: r["status"] for r in state["ledger"]}
        assert by == {"a": "done", "b": "running"}, by
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _boundary_project(verdict_feature=None):
    tmp = _project()
    run_p = tmp / ".spindleloom/runs/run-20260709-auth.json"
    state = json.loads(run_p.read_text(encoding="utf-8"))
    state["feature"] = "user-auth"
    state["ledger"][1]["requires_acceptance"] = "requirements"
    run_p.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return tmp, run_p


def test_rejected_verdict_does_not_unblock_advance():
    """A REJECTED token must NOT let a boundary step advance — only Verdict: ACCEPTED does."""
    tmp, run_p = _boundary_project()
    try:
        subprocess.run([sys.executable, str(HERE / "sloom.py"), "approve", "requirements",
                        "--feature", "user-auth", "--role", "product-owner", "--by", "Ana",
                        "--verdict", "REJECTED", str(tmp)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
        r = _run("advance", "run-20260709-auth", "--agent", "frd-writer", "--status", "done", str(tmp))
        assert r.returncode == 1 and "phase boundary" in r.stdout, r.stdout
        assert json.loads(run_p.read_text(encoding="utf-8"))["ledger"][1]["status"] == "pending"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_advance_refused_when_feature_namespace_mismatches():
    """An ACCEPTED token under a DIFFERENT feature slug must not unblock — acceptance is
    keyed by the ledger's feature namespace."""
    tmp, run_p = _boundary_project()
    try:
        subprocess.run([sys.executable, str(HERE / "sloom.py"), "approve", "requirements",
                        "--feature", "billing", "--role", "product-owner", "--by", "Ana", str(tmp)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
        r = _run("advance", "run-20260709-auth", "--agent", "frd-writer", "--status", "done", str(tmp))
        assert r.returncode == 1 and "phase boundary" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_advance_valueless_flag_errors_cleanly():
    """A trailing flag with no value must give a clean usage error (rc 2), not an IndexError."""
    tmp = _project()
    try:
        r = _run("advance", "run-20260709-auth", "--agent", "frd-writer", str(tmp), "--status")
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "Traceback" not in r.stderr, r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_status_surfaces_flag_rework_against_done_step():
    """B3: a FLAG(owner) targeting an already-done ledger step shows as re-work in status —
    the flag loop closes back to the run instead of accumulating unactioned."""
    tmp = Path(tempfile.mkdtemp(prefix="sloomrun_"))
    try:
        runs = tmp / ".spindleloom" / "runs"
        runs.mkdir(parents=True)
        (runs / "r.json").write_text(json.dumps({"run_id": "r", "status": "active", "ledger": [
            {"agent": "backlog-manager", "status": "done", "upstream": []},
            {"agent": "estimation-facilitator", "status": "pending", "upstream": ["backlog-manager"]}]}),
            encoding="utf-8")
        (tmp / "docs").mkdir()
        (tmp / "docs" / "09-estimation.md").write_text(
            "# est\nFLAG(backlog-manager): PBI-PLAT-004 has no ranked backlog row\n", encoding="utf-8")
        r = _run("status", "r", str(tmp))
        assert r.returncode == 0, r.stdout + r.stderr
        assert "re-work" in r.stdout and "backlog-manager" in r.stdout, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    failures = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        try:
            fn()
            print(f"  ok  {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {name}: {str(e)[:250]}")
    print(f"{'FAIL' if failures else 'OK'} — sloom run tests: {len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
