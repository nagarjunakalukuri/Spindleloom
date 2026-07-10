---
description: Show how to use a Spindleloom agent — its responsibility, when to run it, and copy-paste example prompts. Triggers on "how do I use <agent>", "help for <role>", "what does <agent> do", "show example prompts for <agent>".
argument-hint: [agent-name]
---

Help the user put a role to work. The argument is **$1** (an agent name, e.g. `backlog-manager`, or a phrase like "the architect's agents").

1. Read `agents/HELP.md` (the generated help index: each agent's **Owns** / **Run when** / **Try** prompts, grouped by lifecycle phase).
2. If **$1** names or closely matches one agent, show that entry: its responsibility, when to run it, and its example prompts — and name the agents immediately upstream/downstream so the user knows what feeds it and what it hands to.
3. If **$1** is blank or names a role/phase (e.g. "QA", "design", "the architect"), list the matching agents with their one-line **Owns** and the single best example prompt for each, then offer to expand one.
4. If nothing matches, suggest the closest agent names and point to `agents/HELP.md` and `spindleloom_website/personas/` (the role-by-role field handbook).

Keep it tight and copy-paste-ready — the point is the user can grab a prompt and run it. Don't paraphrase the agent's whole body.
