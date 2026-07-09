#!/usr/bin/env python3
"""validate_gates.py — mechanical enforcement for the execution-quality gates.

The fleet's structural gates (graph, Req-IDs, drift) are validator-enforced, but the
gates that require EVIDENCE OF EXECUTION were prose the model was trusted to follow:
the DoD's "independently checked — change-verifier returned PASS", and the release
go/no-go's "unevidenced gate = no-go". This hook computes them.

Conventions it checks (all under the project's .spindleloom/ machinery dir):

  .spindleloom/verifications/<PBI-ID>.md   — one per verified change, written by
      change-verifier: must contain `Verdict: PASS|FAIL` and an AC coverage matrix
      (a table with a per-criterion status column). A PASS with any AC row not
      marked covered/green is a CONTRADICTION and fails.

  .spindleloom/signoffs/<gate>.md          — one per release gate, written by the
      owning agent (qa, security, performance, accessibility, raid, dod):
      must contain `Verdict: GO|PASS` plus an Evidence line.

Modes:
    python hooks/validate_gates.py <root>                      # audit all artifacts
    python hooks/validate_gates.py <root> --context <task_id>  # fail if no handoff context saved
    python hooks/validate_gates.py <root> --require PBI-X-001  # fail if PBI unverified
    python hooks/validate_gates.py <root> --release            # compute the go/no-go AND
    python hooks/validate_gates.py <root> --release --gates qa,security,raid
                                                               # override the default gate set
Exit 0 = gates hold, 1 = a gate fails or is unevidenced. Stdlib-only, read-only.
"""
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

DEFAULT_RELEASE_GATES = ["qa", "security", "performance", "accessibility", "raid", "dod"]
AC_OK = re.compile(r"(?i)\b(pass|passed|green|covered|met|ok|✅)\b|✅")
AC_ROW = re.compile(r"(?m)^\|\s*(AC[-\s]?\d+|Given\b)", re.I)


def read_verdict(text):
    m = re.search(r"(?im)^\**\s*verdict\s*\**\s*[:|]\s*\**\s*(PASS|FAIL|GO|NO-GO)\b", text)
    if m:
        return m.group(1).upper()
    m = re.search(r"(?im)^\|\s*Verdict\s*\|\s*(PASS|FAIL|GO|NO-GO)\b", text)
    return m.group(1).upper() if m else None


def ac_matrix_problems(text):
    """Rows of the AC coverage matrix that are not green. Returns (rows_found, bad_rows)."""
    rows, bad = 0, []
    for line in text.splitlines():
        if not AC_ROW.match(line):
            continue
        rows += 1
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not any(AC_OK.search(c) for c in cells[1:]):
            bad.append(cells[0][:60])
    return rows, bad


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    require = None
    release = "--release" in argv
    gates = DEFAULT_RELEASE_GATES
    if "--require" in argv:
        require = argv[argv.index("--require") + 1]
    if "--gates" in argv:
        gates = [g.strip() for g in argv[argv.index("--gates") + 1].split(",") if g.strip()]
    ctx_task = argv[argv.index("--context") + 1] if "--context" in argv else None

    ship = root / ".spindleloom"
    if not ship.is_dir() and (root / ".shipwright").is_dir():
        ship = root / ".shipwright"  # pre-0.3 tool dir; scaffold.py migrate renames it
    problems = []

    # ---- verification artifacts (the DoD maker/checker gate) ----
    vdir = ship / "verifications"
    verified = {}
    for p in sorted(vdir.glob("*.md")) if vdir.is_dir() else []:
        text = p.read_text(encoding="utf-8", errors="ignore")
        verdict = read_verdict(text)
        rows, bad = ac_matrix_problems(text)
        if verdict is None:
            problems.append(f"verification {p.name}: no `Verdict:` line — not evidence")
        elif verdict == "PASS":
            if rows == 0:
                problems.append(f"verification {p.name}: PASS with no AC coverage matrix — a PASS must show what it covered")
            elif bad:
                problems.append(f"verification {p.name}: PASS contradicts its own matrix — uncovered/red AC: {', '.join(bad[:4])}")
        verified[p.stem] = verdict
    if require:
        v = verified.get(require)
        if v is None:
            problems.append(f"required: no verification artifact for {require} "
                            f"(.spindleloom/verifications/{require}.md) — the change-verifier gate was skipped")
        elif v != "PASS":
            problems.append(f"required: {require} verification verdict is {v}, not PASS")

    # ---- release sign-off tokens (the computed go/no-go AND) ----
    if release:
        sdir = ship / "signoffs"
        for g in gates:
            p = sdir / f"{g}.md"
            if not p.is_file():
                problems.append(f"release gate '{g}': no sign-off token (.spindleloom/signoffs/{g}.md) — unevidenced = no-go")
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            verdict = read_verdict(text)
            if verdict not in ("GO", "PASS"):
                problems.append(f"release gate '{g}': verdict is {verdict or 'missing'} — no-go")
            elif not re.search(r"(?im)^\**\s*evidence\s*\**\s*[:|]", text):
                problems.append(f"release gate '{g}': GO with no Evidence line — an unevidenced sign-off is a forged gate")

    # ---- handoff-context gate: agents must save before handing off ----
    ctx_count = None
    if ctx_task:
        db = ship / "context.db"
        if not db.is_file():
            problems.append(f"context: no {db.name} in the tool dir — no agent has saved handoff "
                            f"context for this project (see the agent-handoff-context skill)")
        else:
            try:
                con = sqlite3.connect(db)
                ctx_count = con.execute(
                    "SELECT COUNT(*) FROM agent_context WHERE task_id=?", (ctx_task,)
                ).fetchone()[0]
                con.close()
            except sqlite3.Error as e:
                problems.append(f"context: cannot read {db.name}: {e}")
            if ctx_count == 0:
                problems.append(f"context: zero saved entries for task_id '{ctx_task}' — the run "
                                f"passed work between agents without persisting handoff context")

    # ---- advisory: an approved SDD should precede decomposition ----
    advisories = []
    backlogs = list(root.rglob("*backlog*.md"))
    backlogs = [b for b in backlogs if ".spindleloom" not in b.parts and ".spindleloom" not in b.parts and "templates" not in b.parts]
    if backlogs:
        for sdd in root.rglob("sdd*.md"):
            if ".spindleloom" in sdd.parts or ".spindleloom" in sdd.parts or "templates" in sdd.parts:
                continue
            head = sdd.read_text(encoding="utf-8", errors="ignore")[:1500]
            m = re.search(r"(?im)^\|\s*Status\s*\|\s*([^|]+?)\s*\|", head)
            if m and "approved" not in m.group(1).lower() and "baselined" not in m.group(1).lower():
                advisories.append(f"advisory: backlog exists but {sdd.name} Status is "
                                  f"'{m.group(1).strip()}' — decomposition ran ahead of design sign-off")

    n_ver = len(verified)
    if problems:
        print(f"validate_gates: FAIL — {len(problems)} gate problem(s) ({n_ver} verification artifact(s) scanned):")
        for e in problems:
            print("  -", e)
        for a in advisories:
            print("  ·", a)
        return 1
    ok_bits = [f"{n_ver} verification artifact(s) clean"]
    if release:
        ok_bits.append(f"all {len(gates)} release gates evidenced GO")
    if require:
        ok_bits.append(f"{require} verified PASS")
    if ctx_task and ctx_count:
        ok_bits.append(f"{ctx_count} handoff-context entr{'y' if ctx_count == 1 else 'ies'} for '{ctx_task}'")
    print(f"validate_gates: OK — {'; '.join(ok_bits)}")
    for a in advisories:
        print("  ·", a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
