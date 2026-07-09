#!/usr/bin/env python3
"""
scaffold.py — lay down the canonical Spindleloom project layout.

Creates the visible, content-named docs tree (the deliverables) + the hidden
`.spindleloom/` machinery, per the information-architecture decision: brand the
machinery, name the deliverables for what they are.

    docs/
      constitution.md                  (enterprise profile)
      product/   mrd.md brd.md prd.md   (DURABLE — the funnel)
      specs/<feature>/  frd srs sdd tsd recon   (LIVING — per-feature work)
      sprints/<sprint>/  plan.md retro.md        (CYCLIC — one set per sprint)
      adr/  rfc/                        (LIVING — append-only logs)
      RTM.md                            (the traceability backbone)
    .spindleloom/
      config.json                       (standard_version, profile, sanctioned path deviations)
      baselines/<tag>.json              (SNAPSHOT — frozen per sprint/release)

Profile-aware (lean | mid | enterprise) — scaffolds the document set the profile calls for.
Layout is config-driven (see rtm_core.layout): an absent .spindleloom/config.json yields the
canonical Standard tree. Stubs come from the bundled templates/. Idempotent: existing files
are never overwritten. Dependency-free (stdlib only). See project_guides/STANDARD.md for the rules.

Usage:
    python scaffold.py <project-root> [--profile mid] [--feature <name>] [--templates <dir>]
    python scaffold.py <project-root> migrate [--feature <name>] [--apply] [--force]
    (--tier is accepted as a back-compat alias for --profile)

`migrate` converts an EXISTING repo to the Standard: it relocates detected artifacts into
the canonical tree and rewrites cross-links. Dry-run by default (prints the plan); add
--apply to write. It refuses to apply on a non-git repo (no rollback; override with
--force) or while ADR collisions exist (resolve those by recorded supersession first —
the Standard never silently renumbers an assigned id).
"""
import json
import os
import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rtm_core  # noqa: E402

# profile -> {durable funnel docs in <product_dir>/, per-feature docs in <specs_dir>/<feature>/}
PROFILES = {
    "lean":       {"product": ["prd"],                "feature": []},
    "mid":        {"product": ["prd"],                "feature": ["frd", "sdd"]},
    "enterprise": {"product": ["mrd", "brd", "prd"],  "feature": ["srs", "sdd"]},
}
TIERS = PROFILES  # back-compat alias

RTM_HEADER = """# RTM — Requirements Traceability Matrix

> The single chain tying business intent down to tests (see `project_guides/BEST-PRACTICES.md`).
> Proves nothing was dropped and shows the blast radius of any change. One per initiative, living.

| Business goal (BRD) | Product story (PRD) | Functional req (FRD) | Software req (SRS) | Design (SDD) | Build / test (TSD) |
|---|---|---|---|---|---|
| _seed from the BRD/PRD_ | | | | | |

## Decisions
| ID | Decision | Where |
|---|---|---|
| _link ADRs here_ | | |
"""


def write_if_absent(path, content, created):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path)


def scaffold(root, profile=None, feature="feature-1", templates=None, tier=None):
    """Lay down the canonical Standard layout under `root` (idempotent — never overwrites
    an existing file). Honors any sanctioned path deviations in .spindleloom/config.json;
    an absent config yields the canonical tree. `profile` (lean | mid | enterprise; `tier`
    is a back-compat alias) selects which documents are populated, defaulting to the
    project's configured profile or 'mid'. Returns the created file paths as strings.
    Raises ValueError on an unknown profile. Shared by the CLI below and the MCP server."""
    root = Path(root)
    lay = rtm_core.layout(root)
    profile = profile or tier or lay["profile"]
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; choose {list(PROFILES)}")
    templates = Path(templates) if templates else Path(__file__).resolve().parent.parent / "templates"

    docs = root / lay["docs_root"]
    created = []
    # skeleton dirs (config-driven; includes the cyclic sprints/ plane)
    for d in (lay["product_dir"], f"{lay['specs_dir']}/{feature}", lay["adr_dir"], lay["rfc_dir"], lay["sprints_dir"]):
        (docs / d).mkdir(parents=True, exist_ok=True)

    # .spindleloom machinery + config (records the conformance-relevant fields)
    write_if_absent(root / ".spindleloom" / "config.json",
                    json.dumps({"standard_version": rtm_core.STANDARD_VERSION,
                                "profile": profile, "docs_root": lay["docs_root"]}, indent=2) + "\n",
                    created)

    # RTM backbone
    write_if_absent(docs / lay["rtm_file"], RTM_HEADER, created)

    # constitution for enterprise (durable law)
    spec = PROFILES[profile]
    if profile == "enterprise":
        spec = {**spec, "product": ["constitution"] + spec["product"]}

    def stub(doc):
        t = templates / f"{doc}-template.md"
        return t.read_text(encoding="utf-8", errors="ignore") if t.is_file() else f"# {doc.upper()}\n\n_TODO_\n"

    for doc in spec["product"]:
        write_if_absent(docs / lay["product_dir"] / f"{doc}.md", stub(doc), created)
    for doc in spec["feature"]:
        write_if_absent(docs / lay["specs_dir"] / feature / f"{doc}.md", stub(doc), created)

    # docs index
    funnel = " → ".join(spec["product"]) or "(none)"
    feat = ", ".join(spec["feature"]) or "(in tickets)"
    write_if_absent(docs / "README.md",
                    f"# Docs\n\n> Scaffolded by `scaffold.py` (profile: {profile}). "
                    f"Visible deliverables; machinery lives in `.spindleloom/`. See `project_guides/STANDARD.md`.\n\n"
                    f"- **{lay['product_dir']}/** — durable funnel: {funnel}\n"
                    f"- **{lay['specs_dir']}/{feature}/** — per-feature (living): {feat}\n"
                    f"- **{lay['sprints_dir']}/<sprint>/** — per-sprint plan + retro (cyclic)\n"
                    f"- **{lay['adr_dir']}/**, **{lay['rfc_dir']}/** — append-only decision logs\n"
                    f"- **{lay['rtm_file']}** — traceability backbone (`<DOC>-<AREA>-<NUM>` ids)\n\n"
                    f"Fill each via its agent; keep the RTM in sync. See `project_guides/INFORMATION-ARCHITECTURE.md`.\n",
                    created)
    return [str(p) for p in created]


# ---------------------------------------------------------------- brownfield converter (migrate)

_MD_LINK = re.compile(r"(\]\()([^)\s]+)(\))")  # ](target) — bare links (no title)

# kinds that have a canonical home in the Standard tree (others are left in place)
_PRODUCT_KINDS = {"mrd", "brd", "prd", "urs", "constitution"}
_FEATURE_KINDS = {"frd", "srs", "sdd", "tsd"}


def _classify_target(relposix, kind, lay, feature):
    """Where a detected artifact belongs in the Standard tree (repo-relative posix), or
    None to leave it in place. Filenames are preserved — only the folder is normalized.
    A spec/recon file already under specs/ is left where it is — its plane is already
    correct and we don't churn an existing feature name."""
    docs = lay["docs_root"]
    name = relposix.rsplit("/", 1)[-1]
    specs_prefix = f"{docs}/{lay['specs_dir']}/"
    if kind in _PRODUCT_KINDS:
        return f"{docs}/{lay['product_dir']}/{name}"
    if kind in _FEATURE_KINDS or kind == "recon":
        return None if relposix.startswith(specs_prefix) else f"{docs}/{lay['specs_dir']}/{feature}/{name}"
    if kind == "sprint-plan":  # cyclic plane (§4) — relocate out of wherever it sits into sprints/
        return f"{docs}/{lay['sprints_dir']}/{name}"
    if kind == "adr":
        return f"{docs}/{lay['adr_dir']}/{name}"
    if kind == "rfc":
        return f"{docs}/{lay['rfc_dir']}/{name}"
    if kind == "rtm":
        return f"{docs}/{lay['rtm_file']}"
    return None


def _migrate_kind(relposix):
    """detect_kind augmented with migrate-only kinds: `recon` (solution-recon findings) has a
    Standard home (§4 — with its feature) but is intentionally not a global catalog kind, so it
    is resolved here in the converter rather than widening rtm_core.detect_kind."""
    k = rtm_core.detect_kind(relposix)
    if k:
        return k
    stem = relposix.rsplit("/", 1)[-1]
    stem = stem[:-3].lower() if stem.lower().endswith(".md") else stem.lower()
    if stem == "recon" or stem.endswith(("-recon", "_recon")):
        return "recon"
    return None


def _resolve_link(src_relposix, link):
    """Resolve a markdown link relative to its source file into a repo-relative posix
    path (anchors/queries/externals dropped), or None if not a local file link."""
    t = link.split("#", 1)[0].split("?", 1)[0]
    if not t or t.startswith(("http://", "https://", "mailto:", "/")):
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(src_relposix), t))


def _rewrite_links(text, src_old, src_new, moved):
    """Rewrite markdown links in a file (moving src_old -> src_new) that point at any
    moved file, recomputed relative to the file's NEW location. `moved` maps old->new."""
    def repl(m):
        raw, frag = m.group(2), ""
        if "#" in raw:
            raw, f = raw.split("#", 1)
            frag = "#" + f
        resolved = _resolve_link(src_old, raw)
        if resolved in moved:
            newrel = posixpath.relpath(moved[resolved], posixpath.dirname(src_new))
            return m.group(1) + newrel + frag + m.group(3)
        return m.group(0)
    return _MD_LINK.sub(repl, text)


_NOISE_DIRS = {"node_modules", "__pycache__", "venv", "dist", "build", "site-packages", "vendor"}
# A directory carrying any of these is a Spindleloom distribution (toolkit knowledge) or a
# generated harness bundle — never a consuming project's content, so it is pruned wholesale.
_DIST_MARKERS = ("project_guides/STANDARD.md", "build_harness_artifacts.py", "marketplace.json", ".claude-plugin")
# Toolkit content folders: their files are toolkit knowledge, not a project's artifacts.
_TOOLKIT_DIRS = {"agents", "skills", "commands", "templates", "hooks"}


def _is_distribution_dir(d):
    """True if directory `d` is (or contains the marker of) a Spindleloom distribution."""
    return any((Path(d) / m).exists() for m in _DIST_MARKERS)


def _looks_toolkit(relposix):
    """A path that is Spindleloom's own source rather than a project artifact: under a
    toolkit content folder, or an agent/template filename pattern (`*-writer`, `*-template`)."""
    parts = relposix.split("/")
    if any(p in _TOOLKIT_DIRS for p in parts[:-1]):
        return True
    stem = parts[-1][:-3].lower() if parts[-1].lower().endswith(".md") else parts[-1].lower()
    return stem.endswith(("-writer", "-template"))


def _scan_migratable(root):
    """The .md files under root eligible for migration — pruning dotdirs, noise dirs,
    Spindleloom distribution subtrees (self-exemption), and the toolkit's own source files.
    So the converter never plans to relocate toolkit knowledge into a project's docs/."""
    root = Path(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        dirnames[:] = [n for n in dirnames
                       if not n.startswith(".")
                       and n not in _NOISE_DIRS
                       and not _is_distribution_dir(d / n)]
        for fn in filenames:
            if not fn.lower().endswith(".md"):
                continue
            rel = (d / fn).relative_to(root).as_posix()
            if fn[:-3].lower() in rtm_core._SKIP_STEMS or _looks_toolkit(rel):
                continue
            out.append(d / fn)
    return sorted(out)


def migrate(root, feature="feature-1", apply=False, force=False):
    """Convert an existing repo to the Standard layout: relocate detected artifacts into
    the canonical tree (per config) and rewrite cross-links. Dry-run by default; pass
    apply=True to write. Self-exempts Spindleloom distributions + toolkit source, guards
    against many-to-one destination collisions, refuses on a non-git repo (unless force)
    or while ADR/destination collisions exist, and pins the Standard in config on apply."""
    root = Path(root)
    if _is_distribution_dir(root):
        return {"root": str(root), "apply": apply, "exempt": True, "moves": [], "moved_count": 0,
                "note": "this directory is a Spindleloom distribution (toolkit knowledge), exempt per "
                        "project_guides/STANDARD.md — nothing to convert. Point migrate at a CONSUMING project."}
    lay = rtm_core.layout(root)
    docs_root = rtm_core.resolve_docs_root(root)
    is_git = (root / ".git").exists()

    rep = rtm_core.audit(docs_root)
    blockers = [p["message"] for p in rep["problems"] if p["code"] in ("DUP-ADR", "MULTI-ADR-DIR")]

    moves, leave, adr_nums = {}, [], {}
    for f in _scan_migratable(root):
        rel = f.relative_to(root).as_posix()
        kind = _migrate_kind(rel)
        if kind == "adr":
            n = rtm_core.adr_file_num(rel)
            if n is not None:
                adr_nums.setdefault(n, []).append(rel)
        target = _classify_target(rel, kind, lay, feature) if kind else None
        if target is None:
            leave.append({"path": rel, "kind": kind})
        elif target != rel:
            moves[rel] = target

    # never auto-resolve an ADR-number collision — flag it, leave it (Standard §5)
    colliding = {rel for fs in adr_nums.values() if len(fs) > 1 for rel in fs}
    for rel in list(moves):
        if rel in colliding:
            del moves[rel]

    # many-to-one destination guard: distinct sources resolving to one path would clobber
    rev = {}
    for s, dd in moves.items():
        rev.setdefault(dd, []).append(s)
    dest_collisions = {dd: sorted(ss) for dd, ss in sorted(rev.items()) if len(ss) > 1}
    for ss in dest_collisions.values():
        for s in ss:
            moves.pop(s, None)

    # destination-exists guard: a planned dest already on disk (and not itself being vacated)
    # would clobber a pre-existing file (e.g. a second RTM onto the canonical one). Never move
    # it — flag for human resolution (Standard §5: one RTM per initiative; never clobber).
    dest_exists = []
    for s in sorted(moves):
        dd = moves[s]
        if dd in moves or not (root / dd).exists():
            continue
        try:
            differs = (root / s).read_bytes() != (root / dd).read_bytes()
        except OSError:
            differs = True
        dest_exists.append({"from": s, "to": dd, "differs": differs})
        del moves[s]

    plan = {
        "root": str(root), "apply": apply, "is_git": is_git,
        "moves": [{"from": a, "to": b} for a, b in sorted(moves.items())],
        "leave_in_place": leave,
        "adr_collisions": sorted(colliding),
        "dest_collisions": dest_collisions,
        "dest_exists": dest_exists,
        "blockers": blockers,
        "moved_count": len(moves),
    }

    if not apply:
        plan["note"] = "dry-run — re-run with --apply to write"
        return plan
    if blockers or colliding or dest_collisions or dest_exists:
        plan["error"] = ("refusing to apply: resolve ADR collisions (by recorded supersession), "
                         "many-to-one destination collisions, and destinations that already exist "
                         "first — the converter never clobbers")
        return plan
    if not is_git and not force:
        plan["error"] = "refusing to apply on a non-git repo (no rollback); pass --force to override"
        return plan

    moved = dict(moves)
    for old, new in moves.items():
        dst = root / new
        dst.parent.mkdir(parents=True, exist_ok=True)
        (root / old).rename(dst)
    inv = {n: o for o, n in moves.items()}
    for f in _scan_migratable(root):
        rel_new = f.relative_to(root).as_posix()
        rel_old = inv.get(rel_new, rel_new)
        txt = f.read_text(encoding="utf-8", errors="ignore")
        new_txt = _rewrite_links(txt, rel_old, rel_new, moved)
        if new_txt != txt:
            f.write_text(new_txt, encoding="utf-8")

    # pin the Standard in config (convert == conform); merge, don't clobber existing knobs
    cfg = rtm_core.load_config(root)
    cfg.setdefault("standard_version", rtm_core.STANDARD_VERSION)
    cfg.setdefault("profile", lay["profile"])
    cfg.setdefault("docs_root", lay["docs_root"])
    # rename the legacy tool dir first (pre-0.3 repos used .shipwright/)
    legacy = root / rtm_core.LEGACY_TOOL_DIR
    canonical = root / rtm_core.TOOL_DIR
    if legacy.is_dir() and not canonical.exists():
        legacy.rename(canonical)
    cfgp = canonical / "config.json"
    cfgp.parent.mkdir(parents=True, exist_ok=True)
    cfgp.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    plan["applied"] = True
    return plan


# ---------------------------------------------------------------- CLI

_BOOL_FLAGS = {"apply", "force"}


def _parse_flags(argv):
    pos, flags, i = [], {}, 1
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            key = a[2:]
            if key in _BOOL_FLAGS:
                flags[key] = True
            else:
                flags[key] = argv[i + 1] if i + 1 < len(argv) else ""
                i += 1
        else:
            pos.append(a)
        i += 1
    return pos, flags


def _print_migrate(plan):
    if plan.get("exempt"):
        print(f"migrate: {plan['root']}\n  EXEMPT: {plan['note']}")
        return
    print(f"migrate [{'APPLY' if plan['apply'] else 'DRY-RUN'}] {plan['root']} (git={plan['is_git']})")
    if plan.get("error"):
        print(f"  ERROR: {plan['error']}")
    for b in plan["blockers"]:
        print("  blocker:", b)
    if plan["adr_collisions"]:
        print(f"  ADR collisions (resolve by supersession, not moved): {', '.join(plan['adr_collisions'])}")
    if plan.get("dest_collisions"):
        print("  destination collisions (>=2 sources -> one path; not moved):")
        for dd, ss in plan["dest_collisions"].items():
            print(f"    {dd}  <-  {', '.join(ss)}")
    if plan.get("dest_exists"):
        print("  destination already exists (would clobber; not moved):")
        for de in plan["dest_exists"]:
            tag = "differing content — needs merge" if de["differs"] else "identical — delete the source"
            print(f"    {de['to']}  <-  {de['from']}  ({tag})")
    print(f"  moves ({plan['moved_count']}):")
    for m in plan["moves"]:
        print(f"    {m['from']}  ->  {m['to']}")
    if plan["leave_in_place"]:
        print("  left in place (no Standard home / unclassifiable):")
        for lv in plan["leave_in_place"]:
            print(f"    {lv['path']}  ({lv['kind'] or 'unclassified'})")
    if plan.get("applied"):
        print("  applied: files relocated and cross-links rewritten.")
    elif not plan.get("error"):
        print(f"  {plan.get('note', '')}")


def main(argv):
    pos, flags = _parse_flags(argv)
    root = Path(pos[0]) if pos else Path(".")
    feature = flags.get("feature", "feature-1")

    if len(pos) >= 2 and pos[1] == "migrate":
        plan = migrate(root, feature=feature, apply=bool(flags.get("apply")), force=bool(flags.get("force")))
        _print_migrate(plan)
        return 1 if plan.get("error") else 0

    try:
        created = scaffold(root, profile=flags.get("profile") or flags.get("tier"),
                           feature=feature, templates=flags.get("templates"))
    except ValueError as e:
        print(f"scaffold: {e}")
        return 2

    if created:
        print(f"scaffold: created {len(created)} file(s) under {root}/ (feature {feature}):")
        for p in created:
            print("  +", p)
    else:
        print(f"scaffold: nothing to do — {root}/ already laid out (idempotent).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
