---
name: code-minimalism
description: Write and review for the least code that fully does the job — reuse before rewrite, stdlib/native before dependency, delete before add. Use when writing, refactoring, or reviewing code, choosing a library, or when a change feels over-engineered (speculative abstraction, boilerplate, a dependency for a few lines, a hand-rolled thing the platform already ships). Lazy about the solution, never about understanding the problem or about validation, error handling, security, and accessibility.
---

# Code minimalism — the least code that fully does the job

The cheapest code to read, test, and operate is the code that was never written. Minimal is not golfed and not flimsy: it is *only what the task needs*, with every safety check intact. Be lazy about the solution, never about the reading.

## The ladder — stop at the first rung that holds

Run this **after** you understand the change — read the code it touches and trace the real flow first. A small diff in the wrong place is a second bug, not a lazy win.

1. **Does this need to exist at all?** Speculative need → skip it, say so in one line (YAGNI).
2. **Already in this codebase?** A helper, util, type, or pattern that lives here → reuse it. Re-implementing what's a few files over is the most common waste.
3. **Standard library does it?** Use it.
4. **Native platform feature covers it?** `<input type="date">` over a picker lib, a DB constraint over app code, CSS over JS.
5. **An already-installed dependency solves it?** Use it. Don't add a new dependency for what a few lines cover.
6. **Can it be one line?** Make it one line.
7. **Only then:** write the minimum that works.

Two rungs both work → take the higher one and move on. When two options are the same size, pick the one that's correct on edge cases — minimal means less code, not the weaker algorithm.

## Reviewing for over-build

When the task is "what can we cut?", report one line per finding — location, what to cut, what replaces it — and end with `net: -<N> lines possible` (or `Lean already. Ship.`). Tags:

- `delete:` dead code, unused flexibility, speculative feature → replaced by nothing.
- `stdlib:` hand-rolled thing the standard library ships → name the function.
- `native:` dependency or code doing what the platform already does → name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, a layer with one caller.
- `shrink:` same behavior, fewer lines → show the shorter form.

This is a complexity lens only — route correctness, security, and performance findings to a normal review pass, and never flag a change's one required check as bloat.

## Mark deliberate simplifications

When you take a shortcut on purpose, leave a one-line marker so the next reader sees intent, not ignorance. If the shortcut has a known ceiling, name the ceiling **and** the upgrade path:

```
# minimal: global lock here; switch to per-account locks if throughput matters
```

## Never lazy about

Understanding the problem (read it fully, trace the real flow before picking a rung); input validation at trust boundaries; error handling that prevents data loss; security; accessibility; hardware calibration a spec-ideal model can't see; anything the user explicitly asked for. A lazy diff without its check is unfinished — non-trivial logic leaves one runnable check behind (the smallest thing that fails if the logic breaks). If the user wants the full version, build it — don't re-argue.

## Output discipline

Code (or findings) first, then at most a few lines: what you skipped and when to add it. If the explanation runs longer than the code, cut the explanation — a paragraph defending a simplification is complexity smuggled back in as prose. Explanation the user asked for (a report, a walkthrough) is not debt; give it in full.
