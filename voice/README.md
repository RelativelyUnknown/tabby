# voice

A command of the Tabby plugin that sets how the agent words its replies. You run it yourself (`/tabby:voice terse|explain|auto` in Claude Code); the agent never changes it on its own. It affects wording only, never what the agent does.

**Entry point:** [`SKILL.md`](SKILL.md), a single file.

## What it does

Every reply leads with the result. The voice decides what follows it.

| Voice | After the result | For |
| --- | --- | --- |
| `terse` | what ran and what it showed, what is left; no teaching | someone experienced, or in a hurry |
| `explain` | a short how-it-works in plain words; each new idea named once with a one-line example from your code | someone learning, or who asks "how does that work" |
| `auto` (default) | chosen from what you say: learning cues ("new to Python", "6 months in", "idk where to start") give `explain`, anything else gives `terse` | when you have not decided |

The same change in each voice:

- terse: "Added `--month`. 15 tests pass. Not done: Dutch number format."
- explain: "Added `--month`. 15 tests pass. How it works: `argparse` reads the flag and `datetime.strptime` checks it looks like `2026-09`, so a typo gives an error instead of an empty report."

## Setting it

```
/tabby:voice explain     # saves a `voice: explain` line in AGENTS.md
/tabby:voice auto        # removes the line
/tabby:voice             # reports the current voice and changes nothing
```

The line goes in the `## Tabby` section of `AGENTS.md`, or a new `## Tabby` section holding only that line, so it works without the interview and is plain text you can edit. It applies from the next session; the agent follows the new choice from its next reply.

Three places set the voice, and the first one set wins (checked by running the session-start hook):

1. `TABBY_VOICE` in the environment
2. `{"voice": "terse"}` in `.claude/tabby.json` (Claude Code refuses writes to `.claude/`, so the command does not use it; it works if you create the file by hand)
3. `voice:` in `AGENTS.md`

With `explain` or `terse` set, the session-start hook adds one line to the agent's context: "Reply voice: explanatory. Result first, then a short how-it-works in plain words; name each new idea once." (or the terse equivalent). With `auto` it adds nothing, and the agent matches the reader by core rule 13 in [`../core/TABBY-CORE.md`](../core/TABBY-CORE.md).

## Limits

- It is a Claude Code command. In OpenCode and Copilot you can put a `voice:` line in `AGENTS.md` by hand, but the hook that turns it into an instruction is Claude Code only, so there the core rule's "match the reader" is what applies.
- It changes how the agent talks, not how much it does. A terse reply still states what ran and what is left.
