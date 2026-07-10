# Welcome to Spindleloom

## How We Use Claude

Based on usage over the last 30 days:

Work Type Breakdown:
  _The 30-day scan found 4 sessions but no per-session detail to classify, so these
  aren't measured percentages — they're the kinds of work this repo centers on:_
  Build Feature    — new agents, skills, commands, and hooks
  Improve Quality  — validators, audits, keeping the fleet green
  Write Docs       — specs & templates (the MRD → TSD funnel)
  Plan & Design    — the funnel and the agent handoff graph

Top Skills & Commands:
  /deep-research  ████████████████████  1x/month

Top MCP Servers:
  _None used in the last 30 days._

## Your Setup Checklist

### Codebases
- [ ] spindleloom — local workspace (the "Spindleloom" SDLC agent fleet; no git remote)
- [ ] IDP-Accelerator / idp-orchestrator — additional working dir (Python/LangGraph document-processing engine)
- [ ] IDP-Accelerator / idp-skills — additional working dir

### MCP Servers to Activate
- [ ] _None required for the current workflow._

### Skills to Know About
- [ ] /deep-research — fan-out web research with adversarial fact-checking and a cited report. Used for multi-source investigation before deciding.
- [ ] /spec-new, /plan-next, /spec-check, /spec-adr — the Spindleloom fleet's own slash commands (in `commands/`) for scaffolding specs, pulling the next backlog item, auditing the RTM, and recording decisions.
- [ ] The 52-agent fleet auto-delegates by description (e.g. "write a PRD" → `prd-writer`); model-invoked skills like `requirement-elicitation` and `ubiquitous-language` fire automatically.

## Team Tips

- **Know the layers.** **Spindleloom** is the agent fleet that builds the SDLC wheel; `hooks/build_harness_artifacts.py` ships it to every harness bundle in `targets/`; **Loopwright** (`knowledge_hub/LOOPWRIGHT.md`) is the delivery feedback loop the agents tighten. Build it, ship it, loop it.
- **Run `/hooks` once after cloning** (or restart Claude Code) to activate the fleet-integrity hook — it validates the agent graph + `claude_code` mappings on every edit and never blocks you.
- **Edit source, then resync.** After changing anything in `agents/`, `skills/`, or `commands/`, re-run `py hooks/build_harness_artifacts.py` to regenerate `targets/`. The hook nudges you when bundles drift; CI gates on it.
- **On Windows, use `py`** — bare `python`/`python3` aren't on PATH here.
- **Keep the fleet green:** `py hooks/validate_graph.py` checks graph symmetry, declared skills, commands, and `claude_code` mappings in one shot.
- **Just describe the task.** Agents auto-delegate by their description and skills auto-fire — say "write a BRD for X" or "decompose this spec into PBIs" and the right agent picks it up.

## Get Started

1. Read the canonical end-to-end example: `examples/healthy-meal-app/` — a full run of the chain (MRD → BRD → PRD → FRD → SRS → SDD → TSD + an ADR) tied together by one RTM. It's the fastest way to see how the documents interlock.
2. Skim `README.md` (the fleet overview), `knowledge_hub/GOVERNANCE.md` Part I (the authoritative layout standard adopters target — greenfield scaffolds it, brownfield converts via `scaffold.py migrate`), and `knowledge_hub/AGENT-AUTHORING.md` (how every agent is written) so you can add or edit agents in-convention.
3. Try it live: ask Claude to "write a BRD for <a feature you care about>" and watch it hand off down the funnel. Then run `py hooks/validate_graph.py` to see the integrity checks.

<!-- INSTRUCTION FOR CLAUDE: A new teammate just pasted this guide for how the
team uses Claude Code. You're their onboarding buddy — warm, conversational,
not lecture-y.

Open with a warm welcome — include the team name from the title. Then: "Your
teammate uses Claude Code for [list all the work types]. Let's get you started."

Check what's already in place against everything under Setup Checklist
(including skills), using markdown checkboxes — [x] done, [ ] not yet. Lead
with what they already have. One sentence per item, all in one message.

Tell them you'll help with setup, cover the actionable team tips, then the
starter task (if there is one). Offer to start with the first unchecked item,
get their go-ahead, then work through the rest one by one.

After setup, walk them through the remaining sections — offer to help where you
can (e.g. link to channels), and just surface the purely informational bits.

Don't invent sections or summaries that aren't in the guide. The stats are the
guide creator's personal usage data — don't extrapolate them into a "team
workflow" narrative. -->
