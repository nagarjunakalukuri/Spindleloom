#!/usr/bin/env python3
"""
install.py -- Wheelwright installer.

Copies the correct bundle for your AI coding tool into a target repo,
including the skills/ directory that manual copy steps often miss.

Usage:
    # Install for Claude Code (manual, into current repo)
    python3 hooks/install.py --target claude-code

    # Install into a specific repo
    python3 hooks/install.py --target claude-code --repo /path/to/your/project

    # Install globally (~/.claude/ -- shared across all repos)
    python3 hooks/install.py --target claude-code --global

    # Install for Cursor / GitHub Copilot / Windsurf
    python3 hooks/install.py --target cursor
    python3 hooks/install.py --target copilot
    python3 hooks/install.py --target windsurf

    # Preview what would be copied without writing
    python3 hooks/install.py --target claude-code --dry-run

    # Rebuild bundles from source first, then install
    python3 hooks/install.py --target claude-code --rebuild
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent   # hooks/
SRC  = HERE.parent                       # project root

TARGETS = ["claude-code", "cursor", "copilot", "windsurf"]


# ── helpers ──────────────────────────────────────────────────────────────────

def _copy(src: Path, dst: Path, dry: bool) -> list[str]:
    """Copy a file or directory tree into dst. Returns list of written paths."""
    copied: list[str] = []
    if src.is_file():
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied.append(str(dst))
    elif src.is_dir():
        for item in src.iterdir():
            copied.extend(_copy(item, dst / item.name, dry))
    return copied


def _header(label: str, dry: bool) -> None:
    prefix = "  [dry-run]" if dry else "  [copy]"
    print(f"\n{prefix} {label}")


# ── per-target installers ─────────────────────────────────────────────────────

def _install_claude_code(bundle: Path, repo: Path, global_install: bool, dry: bool) -> list[str]:
    claude = Path.home() / ".claude" if global_install else repo / ".claude"
    copied: list[str] = []

    _header("agents/ -> .claude/agents/", dry)
    copied.extend(_copy(bundle / "agents", claude / "agents", dry))

    _header("skills/ -> .claude/skills/", dry)
    copied.extend(_copy(SRC / "skills", claude / "skills", dry))

    _header("commands/ -> .claude/commands/", dry)
    copied.extend(_copy(SRC / "commands", claude / "commands", dry))

    if not global_install:
        _header("CLAUDE.md -> repo root", dry)
        copied.extend(_copy(bundle / "CLAUDE.md", repo / "CLAUDE.md", dry))

        _header("mcp/ -> repo root", dry)
        copied.extend(_copy(bundle / "mcp", repo / "mcp", dry))

        _header(".mcp.json -> repo root", dry)
        copied.extend(_copy(bundle / ".mcp.json", repo / ".mcp.json", dry))

    return copied


def _install_cursor(bundle: Path, repo: Path, dry: bool) -> list[str]:
    copied: list[str] = []

    _header(".cursor/ -> repo root", dry)
    copied.extend(_copy(bundle / ".cursor", repo / ".cursor", dry))

    # Cursor auto-reads .claude/skills/ — same copy as Claude Code
    _header("skills/ -> .claude/skills/  (cursor reads this)", dry)
    copied.extend(_copy(SRC / "skills", repo / ".claude" / "skills", dry))

    _header("mcp/ -> repo root", dry)
    copied.extend(_copy(bundle / "mcp", repo / "mcp", dry))

    _header(".cursor/mcp.json already set; using ${workspaceFolder}", dry)
    return copied


def _install_copilot(bundle: Path, repo: Path, dry: bool) -> list[str]:
    copied: list[str] = []

    _header(".github/ -> repo root", dry)
    copied.extend(_copy(bundle / ".github", repo / ".github", dry))

    _header(".vscode/ -> repo root", dry)
    copied.extend(_copy(bundle / ".vscode", repo / ".vscode", dry))

    # Copilot reads .claude/skills/ via the agents it loads
    _header("skills/ -> .claude/skills/  (copilot reads this)", dry)
    copied.extend(_copy(SRC / "skills", repo / ".claude" / "skills", dry))

    _header("mcp/ -> repo root", dry)
    copied.extend(_copy(bundle / "mcp", repo / "mcp", dry))

    return copied


def _install_windsurf(bundle: Path, repo: Path, dry: bool) -> list[str]:
    copied: list[str] = []

    _header(".windsurf/ -> repo root", dry)
    copied.extend(_copy(bundle / ".windsurf", repo / ".windsurf", dry))

    _header("skills/ -> .claude/skills/  (windsurf reads this)", dry)
    copied.extend(_copy(SRC / "skills", repo / ".claude" / "skills", dry))

    _header("mcp/ -> repo root", dry)
    copied.extend(_copy(bundle / "mcp", repo / "mcp", dry))

    mcp_py = repo / "mcp" / "mcp_server.py"
    print(
        "\n  NOTE (Windsurf MCP is user-global):\n"
        f"  Add the server entry below to ~/.codeium/windsurf/mcp_config.json\n"
        f"  (use the absolute path shown — ${{workspaceFolder}} is not supported there):\n\n"
        f'  {{\n'
        f'    "mcpServers": {{\n'
        f'      "wheelwright": {{\n'
        f'        "command": "uv",\n'
        f'        "args": ["run", "--with", "mcp[cli]", "python",\n'
        f'                 "{mcp_py}"],\n'
        f'        "env": {{ "WHEELWRIGHT_SPEC_ROOT": "{repo}/docs" }}\n'
        f'      }}\n'
        f'    }}\n'
        f'  }}\n'
    )
    return copied


# ── next-steps messages ───────────────────────────────────────────────────────

NEXT_STEPS = {
    "claude-code": (
        "  Open Claude Code in your project, then:\n"
        "    /agents              -- list all 52 agents\n"
        "    /help-role           -- agents grouped by your role\n"
        "    /spec-new <feature>  -- scaffold a project\n\n"
        "  To enable live RTM queries (MCP), install uv:\n"
        "    Windows:  irm https://astral.sh/uv/install.ps1 | iex\n"
        "    macOS:    curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        "  Then .mcp.json auto-discovers the server -- nothing else to run.\n\n"
        "  To enable agent context memory (semantic search):\n"
        "    pip install chromadb   # then set WHEELWRIGHT_SEMANTIC=1 in .mcp.json"
    ),
    "cursor": (
        "  Reload Cursor window (Ctrl+Shift+P -> Developer: Reload Window).\n"
        "  Agents appear as description-triggered rules in .cursor/rules/.\n"
        "  MCP: install uv, then .cursor/mcp.json auto-discovers the server."
    ),
    "copilot": (
        "  Reload VS Code window (Ctrl+Shift+P -> Developer: Reload Window).\n"
        "  Agents appear as chat modes in GitHub Copilot Chat.\n"
        "  MCP: install uv, then .vscode/mcp.json auto-discovers the server."
    ),
    "windsurf": (
        "  Reload Windsurf window.\n"
        "  Agents appear as always-on/description-triggered Cascade rules.\n"
        "  See the NOTE above to wire the MCP server (it's user-global in Windsurf)."
    ),
}


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Install Wheelwright into a repo's AI coding tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--target", required=True, choices=TARGETS,
                    help="AI coding tool: claude-code | cursor | copilot | windsurf")
    ap.add_argument("--repo", default=".",
                    help="Target repo root (default: current directory)")
    ap.add_argument("--global", dest="global_install", action="store_true",
                    help="Claude Code only: install into ~/.claude/ (all repos)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would be copied without writing anything")
    ap.add_argument("--rebuild", action="store_true",
                    help="Re-run build_harness_artifacts.py from source first")
    args = ap.parse_args()

    if args.global_install and args.target != "claude-code":
        ap.error("--global only applies to --target claude-code")

    # Rebuild bundles if requested
    if args.rebuild:
        print("Rebuilding harness bundles from source...")
        r = subprocess.run([sys.executable, str(HERE / "build_harness_artifacts.py")])
        if r.returncode != 0:
            print("Bundle rebuild failed — aborting.")
            sys.exit(1)
        print()

    repo   = Path(args.repo).resolve()
    bundle = SRC / "targets" / args.target

    if not bundle.exists():
        print(f"Bundle not found: {bundle}")
        print("Run:  python3 hooks/build_harness_artifacts.py")
        sys.exit(1)

    dest_label = "~/.claude/" if args.global_install else str(repo)
    dry_label  = " [DRY RUN]" if args.dry_run else ""
    print(f"Wheelwright installer{dry_label}")
    print(f"  source :  {SRC}")
    print(f"  target :  {args.target}")
    print(f"  dest   :  {dest_label}")

    if args.target == "claude-code":
        copied = _install_claude_code(bundle, repo, args.global_install, args.dry_run)
    elif args.target == "cursor":
        copied = _install_cursor(bundle, repo, args.dry_run)
    elif args.target == "copilot":
        copied = _install_copilot(bundle, repo, args.dry_run)
    elif args.target == "windsurf":
        copied = _install_windsurf(bundle, repo, args.dry_run)

    verb = "Would copy" if args.dry_run else "Copied"
    print(f"\n{verb} {len(copied)} files.")

    if not args.dry_run:
        print("\nNext steps:")
        print(NEXT_STEPS[args.target])


if __name__ == "__main__":
    main()
