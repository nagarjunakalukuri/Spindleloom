# Hooks — automated PM gates

Hooks turn the conventions in `project_guides/BEST-PRACTICES.md` from "things we agree to do" into "things the harness enforces." They're generic — any team can wire them in.

## What's here

| Hook | What it does | When to run |
|------|--------------|-------------|
| `validate_reqs.py` <!-- now incl. quality lint --> | Validates Req-ID format (`<DOC>-<AREA>-<NUM>`), flags duplicate IDs, and proves traceability — **(1)** RTM coverage (every FRD/SR requirement is traced), **(2)** no broken refs in the RTM, **(3)** no orphan PBIs (a backlog PBI not traced in the RTM = scope creep), **(4)** ADR reference integrity (every `ADR-NNNN` cited has a defining `adr-NNNN-*.md`). Test coverage is reported as non-fatal advisories. Read-only, stdlib-only, exit 1 on problems. | On spec edits (Claude Code hook), and as a CI/pre-PR gate. |
| `build_agent_index.py` | Generates `agents/INDEX.md` — a lifecycle-phase index of the fleet — from each agent's `phase:` / contract-block frontmatter, so you navigate agents by *when you run them* and the handoff graph stays in sync with the files. Read-only except for writing `INDEX.md`. | After adding or editing an agent's contract block. |
| `scaffold.py` | Lays down the canonical project layout (`docs/` deliverables + `.spindleloom/` machinery) per `project_guides/INFORMATION-ARCHITECTURE.md` — tier-aware (lean/mid/enterprise), seeds `RTM.md` + `.spindleloom/config.json`, copies template stubs. Idempotent (never overwrites). The deterministic half of `/spec-new`. | Once per new project/feature. |
| `add_examples.py` | Injects an `examples:` block (1-2 copy-paste prompts) into each agent's frontmatter from a JSON file — the output of the `author-agent-examples` workflow. Additive + idempotent; nothing else changes. | One-off / after (re)authoring example prompts. |
| `build_help.py` | Generates `agents/HELP.md` — per agent: **Owns** (from `description`), **Run when** (from `phase` + handoffs), **Try** (the `examples:` prompts), grouped by phase. The source for `/help-role` and the "how do I use this role" surface. | After editing an agent's description/contract/examples. |
| `build_handoffs.py` | Injects/refreshes a one-line **Handoff** blockquote at the top of every agent body — *Before:* read `<inputs>` (from `<upstream>`); *After:* produce `<output>` → hand to `<downstream>` — generated from the contract block so the model (not just the index) sees each agent's before/next steps. Idempotent; `--check` mode exits 1 if any agent is stale (no writes). | After any contract-block (upstream/downstream/inputs/outputs) change. |
| `validate_graph.py` | **Self-check for the fleet** — the toolkit eating its own docs-as-code. Runs **12 checks**: (1) contract-graph *symmetry*, (2) no *dangling* agent refs, (3) no *missing skills*, (4) `INDEX.md` *freshness*, (5) handoff line present, (6) `examples:` prompts present, (7) `claude_code:` mapping integrity (subagent + command resolve), (8) command well-formedness (description present), (9) armed skills are model-invocable, (10) no orphan agents outside the entry-point allowlist, (11) `loop:`/`agentic_role:` classification present with valid values, (12) `project_guides/spindleloom-agent-fleet.html` node/edge data in sync with the contract graph (the `t:'i'` wiki overlay is exempt). Prints live agent/template/skill/command counts as advisories. Read-only, stdlib-only, exit 1 on problems. | After adding/editing/removing/renaming an agent, and as a CI/pre-PR gate. |
| `rtm_core.py` | **Shared traceability + artifact core** (stdlib-only, read-only). Resolves the docs location (`resolve_docs_root` — `.spindleloom/config.json` `docs_root`, default `docs/`, fallback flat), then parses it (recursively, excluding dotdirs) into the requirement graph (Req-IDs, RTM matrix + decisions, ADR refs) *and* the artifact catalog (kind from path incl. parent folder, owner/status/version/last-updated from doc headers). Exposes `audit()`, `trace()`, `list_requirements()`, `find_decision()`, `parse_rtm()`, `artifacts()`, `find_artifact()`, `resolve_docs_root()`. Imported by the validator, the registry generator, and the MCP server — one parser, no drift. | Library; not run directly. |
| `validate_targets.py` | **Per-harness conformance** (stdlib-only) — validates the generated bundles against each TOOL's format rules, the class the drift gate can't see: Windsurf's 12k rule-truncation cap (generator auto-condenses; this proves it), frontmatter requirements per surface, per-bundle required counts (agents/commands/skills), MCP configs parse with the `sloom` server, and **bundled-hook import resolution** (a hook importing a local module that didn't ship = the shipped-broken-hook class, caught mechanically). Advisory when HARNESS-MATRIX's verified date is >90 days old. Tested by `test_validate_targets.py`. | After regenerating bundles; in `sloom check` and CI. |
| `sloom.py` | **The front door** — one CLI over every tool: `sloom check` auto-detects repo type (toolkit → fleet battery: graph + handoffs + bundle drift; adopter → spec battery: reqs + rtm + registry + gates) and aggregates the exit code; `sloom reqs|rtm|gates|pack|registry|scaffold|backlog|graph|targets|index` forward unchanged to the underlying tools. Tested by `test_sloom.py`. | The one command to teach: `python hooks/sloom.py check`. |
| `build_context_pack.py` | **Context engineering, mechanized** (stdlib-only) — assembles the minimal context manifest for one agent+task: contract `inputs:` resolved to registry-stamped paths (+ each doc's `## Digest`), the feature's RTM slice, saved handoff-context entries (stale-flagged), open `ASSUMPTION-n` tags in scope, and a size-vs-budget verdict with demotion advice. Dispatchers hand the pack to the agent instead of "read the docs folder". `--write` persists to `<tool-dir>/context-packs/`. Tested by `test_build_context_pack.py`. | When dispatching an agent (run-orchestrator step, or by hand before a task). |
| `validate_gates.py` | **Execution-quality gate validator** (stdlib-only) — computes the gates that were previously prose: (a) `change-verifier` PASS artifacts (`.spindleloom/verifications/<PBI>.md`) must exist per `--require <PBI>`, carry a `Verdict:`, and never contradict their own AC coverage matrix; (b) `--release` computes the go/no-go **AND** from the sign-off tokens (`.spindleloom/signoffs/{qa,security,performance,accessibility,raid,dod}.md` — each needs `Verdict: GO` + `Evidence:`), naming every missing/unevidenced gate; (c) advisory: an SDD left un-Approved while a backlog exists. Tested by `test_validate_gates.py` (5 cases incl. trip tests). | Pre-PR (`--require`), at go/no-go (`--release`), and in CI. |
| `build_rtm.py` | **Deterministic RTM seeder** (stdlib-only) — scans the docs root for every `<DOC>-<AREA>-<NUM>` Req-ID and creates/refreshes `RTM.md`: one row per ID (id, kind, defining file, empty Downstream/Test/Status cells to fill). Append-only and idempotent — existing rows are never modified. `--check` exits 1 if any on-disk ID is missing from the RTM. Backs the "brd-writer materializes the RTM" convention with tooling, so a run that mints IDs can't fail `validate_reqs` NO-RTM. | After adding documents/IDs; `--check` alongside `validate_reqs`. |
| `build_artifact_registry.py` | **Artifact catalog generator** (stdlib-only) — the *retrieval* layer the RTM doesn't cover. Takes a **project root**, resolves `docs_root`, discovers every artifact, and writes the catalog into **`.spindleloom/`** (machinery, out of the human docs tree): `.spindleloom/artifacts.json` + `ARTIFACTS.md` (id, kind, title, path, owner, status, version, last-updated, Req-IDs defined). `--init` bootstraps `.spindleloom/config.json`; `--baseline <tag>` freezes a version/status snapshot to `.spindleloom/baselines/<tag>.json`; `--check` exits 1 if stale. Answers "what artifacts exist, where, owned by whom, in what state?" | Against a project root; after spec changes; `--check` in CI. |
| `emit_backlog.py` | Turns `backlog.md` into work-tracker work items — the docs→tracker sync contract, automated: parse → field-map (AC → its own field, never Description) → dry-run plan → write tracker IDs back into the RTM. The live Azure Boards/Jira call lives in a pluggable `push()` adapter (host/PAT). **Headless/agent runs that `--apply` (or call the adapter) perform network writes — pre-approve them in the runner's permission layer (allowlist the command / grant write scope), or the writes get blocked/denied inconsistently; interactive runs prompt, agents don't.** Stdlib-only; offline steps testable. | After grooming `backlog.md`; to seed/sync the tracker. |
| `sdd-cache-pre.sh` | **SSRF-safe SDD URL cache (pre)** — before fetching a remote spec document, validates the URL (blocks non-http/https + RFC-1918/loopback/link-local), checks the TTL cache (`~/.cache/spindleloom/sdd/` or `$SDD_CACHE_DIR`), and prints the cached body + exits 0 on a fresh hit so the caller skips the network fetch. Exits 1 on miss/expired (caller should fetch then call the post-hook). Expires stale entries (configurable via `SDD_CACHE_MAX_AGE`, default 7 days). Bash + stdlib-only; no curl calls of its own. | Called by Claude Code `WebFetch` pre-hooks or CI pipelines that fetch external SDD/spec URLs. |
| `sdd-cache-post.sh` | **SSRF-safe SDD URL cache (post)** — after a successful fetch, validates the URL, verifies `CACHE_DIR` is not a symlink (path-traversal guard), reads the fetched content from stdin, refuses to cache empty responses, and writes the body + metadata atomically. Mirrors the SSRF guard from the pre-hook. Bash + stdlib-only. | Called immediately after a successful `curl` / `WebFetch` to persist the response; pair with `sdd-cache-pre.sh`. |
| `jira_adapter.py` | **The live Jira `push()`** for `emit_backlog` — turns planned work items into real Jira issues via the Cloud REST API v3 (JSON body; AC → `JIRA_AC_FIELD` when set, otherwise appended to description; story points only for Story/Bug; next-gen `parent` link or classic `JIRA_EPIC_LINK_FIELD`; labels sanitised — no spaces). Stdlib-only (`urllib`); **dry-run by default — network writes only with `--apply` + creds** (`JIRA_BASE_URL`, `JIRA_PROJECT_KEY`, `JIRA_USER_EMAIL`, `JIRA_API_TOKEN`). Run `--list-fields` to discover your instance's custom field ids for SP and AC. Offline field-mapping and ADF generation covered by `test_jira_adapter.py`. | After `emit_backlog` planning; to create/sync Jira issues. |
| `azure_boards_adapter.py` | **The live Azure Boards `push()`** for `emit_backlog` (IMP-007) — turns the planned work items into real Boards work items via the REST API (JSON-Patch; AC → `Microsoft.VSTS.Common.AcceptanceCriteria`; StoryPoints for Story/Bug only; optional epic parent-linking via `--link-epics`), then writes the new ids back into the RTM. Stdlib-only (`urllib`); **dry-run by default — network writes only with `--apply` + a PAT** (Work Items read+write scope, IMP-008). Iteration/Area paths are not auto-created (assign in Boards). Offline field-mapping covered by `test_azure_boards_adapter.py`. | After `emit_backlog` planning; to create/sync Azure Boards items. |
| `mcp_server.py` | **Spindleloom MCP server** (FastMCP) — exposes **19 tools**: 12 traceability/catalog/conformance tools (`trace_requirement`, `rtm_coverage`, `list_requirements`, `find_decision`, `list_artifacts`, `find_artifact`, `funnel_status`, `stale_artifacts`, `next_req_id`, `search_specs`, `check_conformance`, `scaffold_project` — the last gated behind `SPINDLELOOM_WRITABLE=1`) + 7 agent-context-memory tools (`save_context`, `recall_context`, `list_contexts`, `get_context`, `delete_context`, `delete_context_entry`, `sync_contexts`; SQLite in `.spindleloom/context.db`, optional ChromaDB semantic search behind `SPINDLELOOM_SEMANTIC=1`), plus **4 resources** (`rtm://current`, `spindleloom://requirements`, `spindleloom://artifacts`, `spindleloom://decisions`) — so any MCP-aware harness (Claude Code, Cursor, Copilot, Windsurf) queries specs live instead of reading static markdown. Reads `$SPINDLELOOM_SPEC_ROOT`. The **one** component with a required dependency (`mcp[cli]`; `chromadb` is optional), isolated here — `rtm_core`, the validator, and the registry generator stay stdlib-only. | Launched by a harness via the generated `.mcp.json`. |
| `build_harness_artifacts.py` | **The harness generator** — one source → harness-native bundles, across every customization surface a tool exposes (agents, skills, instructions, hooks, commands, plugin, **MCP**), not just agents. Bundles `mcp/` (the server) and emits each tool's native `.mcp.json` (Claude `mcpServers` / VS Code `servers`). Emits 6 targets under `targets/<harness>/`: **`claude-plugin`** (the headline — a complete installable Claude Code plugin: `.claude-plugin/plugin.json` + `marketplace.json` bundling agents + commands + skills + hooks + templates + conventions skill + the MCP server + scaffold), `claude-code` (loose subagents), `cursor` (`.mdc` rules + always-on conventions + `.cursor/mcp.json`), `copilot` (chat modes + `copilot-instructions.md` + `.vscode/mcp.json`), `windsurf` (`model_decision` rules + always-on conventions; MCP via user-global config), and `agents-md` (cross-tool `AGENTS.md` router). See `project_guides/HARNESS-MATRIX.md` for the full 7-surface × tool matrix. Replaces the manual copy-table in `INSTALL.md`. `--only <harnesses>` selects targets, `--out <dir>` changes the output root, `--check` exits 1 if any bundle is stale (drift gate). Read-only except under the output root; stdlib-only. | After any source (agent/skill/command/hook/convention) change; `--check` in CI. |

Run them manually any time:
```
python spindleloom/hooks/validate_reqs.py <spec-folder>   # spec/RTM traceability
python spindleloom/hooks/build_handoffs.py                # refresh agent handoff lines
python spindleloom/hooks/build_agent_index.py             # refresh agents/INDEX.md
python spindleloom/hooks/validate_graph.py                # agent-fleet integrity
python spindleloom/hooks/build_harness_artifacts.py       # generate targets/<harness>/ bundles
# (use python3 or `py -3` if `python` isn't on PATH)
```

The two `build_*` generators derive from the contract block (single source of truth); `validate_graph.py` then checks the results are consistent — so the fleet's sequence knowledge stays correct without hand-editing. Re-run the generators after any agent change; wire `validate_graph.py` (and `build_handoffs.py --check`) into CI.

`validate_graph.py` is what stops the kind of drift this fleet is prone to: an agent added without reciprocating its handoff edges, a renamed agent leaving a dangling reference, an `INDEX.md` left stale, or a `claude_code:` mapping pointing at a command/subagent that no longer exists (the layer that makes the fleet work inside Claude Code). Run it (and `build_agent_index.py`) after any agent change; wire it into CI so the graph can't merge broken.

## Wire it as a Claude Code hook (per-developer or per-repo)

Add to `.claude/settings.json` (project) or `~/.claude/settings.json` (global). This runs the validator after any spec doc is written/edited and surfaces problems back to the session as feedback:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python spindleloom/hooks/validate_reqs.py \"$CLAUDE_PROJECT_DIR\"/$(dirname \"${CLAUDE_TOOL_INPUT_file_path#$CLAUDE_PROJECT_DIR/}\") 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Notes:
- Replace `python` with `python3` or `py -3` to match the platform (Windows often needs `py -3`).
- The `|| true` keeps the hook advisory (warn, don't block the edit). Drop it to make a failing validation block.
- Scope it tighter by matching only your spec folder if you don't want it firing on code edits.

The hook above is the **consumer** gate (it validates spec docs an installed team writes). When you're **authoring the fleet itself**, wire the integrity validator the same way so a broken `claude_code:` mapping, command, or skill is caught the instant you save — and, in the same hook, get nudged when your source edits have left the generated `targets/` bundles stale:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "shell": "bash",
            "command": "out=$(py \"$CLAUDE_PROJECT_DIR/hooks/validate_graph.py\" 2>&1); ec=$?; if [ $ec -ne 0 ]; then echo \"$out\" >&2; exit 2; fi; if ! py \"$CLAUDE_PROJECT_DIR/hooks/build_harness_artifacts.py\" --check >/dev/null 2>&1; then printf '{\"systemMessage\":\"Spindleloom harness bundles are stale vs source — run: py hooks/build_harness_artifacts.py to resync targets/.\"}'; fi",
            "timeout": 30,
            "statusMessage": "Validating fleet integrity…"
          }
        ]
      }
    ]
  }
}
```

Notes:
- Put this in **`.claude/settings.local.json`** (personal, gitignored), not the committed `settings.json` — the `py` launcher is Windows-specific (swap to `python3` on macOS/Linux), so a committed copy would silently no-op for teammates on other platforms. The team-wide guarantee is the CI gate below; this is just live feedback while you author. A teammate opts in by dropping the snippet into their own `settings.local.json` with their platform's launcher.
- **Two tiers, two severities.** A broken graph is a real problem to fix now, so `validate_graph.py` failing exits `2` and surfaces the findings to the session (after the edit lands — it never blocks the write). Bundle drift is a *do-it-before-you-finish* reminder, not a per-edit failure, so it emits a non-blocking `systemMessage` nudge instead (no `exit 2`, so the agent doesn't treat the edit as failed). Both go quiet once you fix the graph / re-run the generator.
- If `.claude/` didn't exist when the session started, run `/hooks` once (or restart) so Claude Code picks the hook up.

## Wire it as a CI / pre-PR gate (recommended for shared repos)

This is the higher-leverage placement — it makes traceability a merge requirement (BEST-PRACTICES "Definition of Ready" / change-control). Example GitHub Actions step:

```yaml
- name: Validate spec traceability
  run: |
    for d in $(git diff --name-only origin/main... | grep -E '/RTM\.md$' | xargs -n1 dirname | sort -u); do
      python spindleloom/hooks/validate_reqs.py "$d"
    done
```

Or simply run it against each spec folder that changed in the PR. A non-zero exit fails the check.

For the agent fleet itself, add `validate_graph.py` as a gate so a broken contract graph can't merge:

```yaml
- name: Validate agent-fleet integrity
  run: |
    python spindleloom/hooks/build_agent_index.py   # keep INDEX current
    python spindleloom/hooks/validate_graph.py       # symmetry, dangling refs, skills, INDEX, claude_code mappings, commands
    python spindleloom/hooks/build_harness_artifacts.py --check   # per-tool bundles not stale vs source
```

## Wire the SDD cache hooks (WebFetch SSRF guard)

`sdd-cache-pre.sh` and `sdd-cache-post.sh` implement a TTL cache for remote spec-document fetches with SSRF prevention. Wire them as `PreToolUse`/`PostToolUse` hooks on `WebFetch` so every remote SDD/spec URL is validated and cached automatically.

Add to `.claude/settings.local.json` (personal, gitignored — path separator is platform-specific):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "WebFetch",
        "hooks": [
          {
            "type": "command",
            "shell": "bash",
            "command": "url=\"$CLAUDE_TOOL_INPUT_url\"; hit=$(bash \"$CLAUDE_PROJECT_DIR/hooks/sdd-cache-pre.sh\" \"$url\" 2>/dev/null); rc=$?; if [ $rc -eq 0 ]; then printf '{\"decision\":\"block\",\"reason\":\"sdd-cache hit\",\"systemMessage\":\"%s\"}' \"$hit\"; elif [ $rc -eq 2 ]; then printf '{\"decision\":\"block\",\"reason\":\"SSRF guard: URL rejected by sdd-cache-pre.sh\"}'; fi",
            "timeout": 10,
            "statusMessage": "Checking SDD URL cache…"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "WebFetch",
        "hooks": [
          {
            "type": "command",
            "shell": "bash",
            "command": "url=\"$CLAUDE_TOOL_INPUT_url\"; result=\"$CLAUDE_TOOL_RESULT\"; printf '%s' \"$result\" | bash \"$CLAUDE_PROJECT_DIR/hooks/sdd-cache-post.sh\" \"$url\" 2>/dev/null || true",
            "timeout": 10,
            "statusMessage": "Caching fetched SDD…"
          }
        ]
      }
    ]
  }
}
```

Notes:
- **Pre-hook exit codes:** `0` = cache hit (block the fetch, serve the cached body); `1` = miss (allow the fetch to proceed); `2` = SSRF guard triggered (block the fetch, surface the rejection). Claude Code's `decision: "block"` stops the tool call and returns `systemMessage` to the session instead.
- **Post-hook:** reads the fetched content from the tool result env var and writes it to the cache. The `|| true` keeps it advisory — a failed cache write doesn't break the session.
- **TTL:** 7 days by default. Override: `"env": {"SDD_CACHE_MAX_AGE": "86400"}` (1 day) in the hook config.
- **Cache location:** `~/.cache/spindleloom/sdd/` by default. Override: `"env": {"SDD_CACHE_DIR": "/your/path"}`.
- On **Windows**, set `"shell": "bash"` and ensure Git Bash is on `PATH`, or use WSL. The `py` launcher is not needed here (pure bash).
- Scope to spec-document URLs only by adding a URL pattern check at the top of each hook if you don't want all WebFetch calls cached.

## Extending

The validator is intentionally small and readable. PBI-orphan and ADR-reference checks are now built in (see the table above); fork it to add further team-specific rules (e.g. "every PBI must cite a depends-on", "no requirement older than N days without a Status", "every story has an estimate"). To extend coverage to more doc types, the cleanest hook is each agent's contract block — `id_prefix` / `rtm_column` declare what an agent produces, so the validator can be generalized to read those rather than the hardcoded `{FRD,SR,SRS}` set. Keep it stdlib-only so any team can run it with no install.
