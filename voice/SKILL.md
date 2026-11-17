---
name: voice
description: "Use only when the user asks for it: /tabby:voice, 'explain more', 'be terse', 'talk to me like a beginner'. Sets how Tabby words its replies in this project: terse (technical, no lessons), explain (result first, then how it works) or auto (default). Never change it on your own."
disable-model-invocation: true
license: MIT
---

# Reply voice

Tabby's replies always lead with the result. The voice decides what follows.

| Voice | Reads like | Use when |
| --- | --- | --- |
| `terse` | What changed, what ran and what it showed, what is left. No teaching, no background. | The user is experienced or wants speed. |
| `explain` | The same result first, then a short how-it-works in plain words. Each new idea is named once, with a one-line example from this code. | The user is learning, or asks "how does that work". |
| `auto` (default) | Chosen from what the user says: learning cues ("new to Python", "6 months in", "idk where to start") give `explain`; anything else gives `terse`. | Nothing was set. |

Example, same change in each voice:

- terse: "Added `--month`. 15 tests pass. Not done: Dutch number format."
- explain: "Added `--month`. 15 tests pass. How it works: `argparse` reads the flag and `datetime.strptime` checks it looks like `2026-09`, so a typo gives an error instead of an empty report."

## `/tabby:voice terse|explain|auto`

Save the choice as a `voice: <choice>` line in AGENTS.md: inside the `## Tabby` section if there is one, otherwise create a `## Tabby` section holding only that line. `auto` removes the line. Claude Code refuses writes to `.claude/`, so do not use `.claude/tabby.json` (it still works if the user has made it by hand, and `TABBY_VOICE` in the environment overrides both). Say it applies from the next session, and follow the choice from your next reply on. With no argument, report the current voice.
