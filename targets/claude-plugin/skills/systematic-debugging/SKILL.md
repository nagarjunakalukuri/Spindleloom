---
name: systematic-debugging
description: Root-cause a failure with a repeatable method instead of flailing — reproduce it reliably, read the actual error, bisect to the smallest failing case, form one hypothesis at a time, fix the cause (not the symptom), and lock it with a regression test. Use on a failing test, a stack trace, a log, or a production incident. Consumed by debugger, backend-developer, frontend-developer, flaky-test-detective, and incident-responder.
---

# Systematic debugging — method over flailing

Debugging is the biggest time sink in a developer's day, and random changes make it worse. Work the method:

## 1. Reproduce first
A bug you can't reproduce, you can't fix or confirm fixed. Find the smallest, most reliable trigger. If it only happens sometimes, make the conditions explicit (state, timing, data, concurrency) until it's deterministic.

## 2. Read the actual error
Read the **whole** stack trace / log, top frame to root cause — not just the last line. The answer is usually written down; confident guessing skips it.

## 3. Bisect / isolate
Shrink the failing surface: comment out, `git bisect`, binary-search the input, disable half the config. Get to the **smallest case that still fails** — that *is* the location.

## 4. One hypothesis at a time
State a single falsifiable hypothesis ("the cache returns a stale value after update"), make **one** change to test it, observe. Changing five things at once means you can't tell which mattered — and often adds new bugs.

## 5. Fix the cause, not the symptom
A `try/catch` that hides the error, a retry that masks a race, a null-check that silences a deeper invariant violation — these are symptom patches. Fix where it actually goes wrong. If the real fix is too big now, say so and file it; don't paper over it.

## 6. Lock it with a regression test
Add a test that **fails before the fix and passes after** (red→green) — that proves you fixed the real thing and stops it returning. Hand it to `test-author` if it belongs in the suite.

## 7. Capture the lesson
Recurring root causes are signal: feed them to `coding-standards-writer`, the backlog, or a postmortem so the *class* of bug gets prevented, not just this instance.

## Smells
- "I changed some things and it works now" → you don't know what fixed it; it'll be back.
- A fix with no failing-first regression test → unproven.
- Catching-and-swallowing the error to make the red go away → you hid the bug, you didn't fix it.
