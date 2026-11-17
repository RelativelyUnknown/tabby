# interview

A skill of the Tabby plugin that asks you a few questions about your project and saves the answers as a short `## Tabby` section in `AGENTS.md`. You run it yourself (`/tabby:interview` in Claude Code, `@interview` in OpenCode, `/interview` in Copilot). Tabby never interviews you before a task and never needs the section to work; it is optional.

**Entry point:** [`SKILL.md`](SKILL.md). The procedure is in [`references/start.md`](references/start.md) (the rounds, the section's format, the drift check) and [`references/research.md`](references/research.md) (what it reads first).

## Why bother

Without the section, Tabby infers the project from the code and your request, and marks guesses `(assumed)`. Code can say what a project is. It cannot say who uses it, what is coming next, or what you will never build. Those facts change design: whether a function takes a batch so a Rust version can cross the boundary once, whether a key is one service's id when a second service is planned.

With the section, every later task starts from those facts (core rule 12): the agent names the lines that shape the task, builds the seam the next `growth:` item needs instead of a choice it would have to undo, checks its work against `goals:`, asks before contradicting a line, and does not re-ask what `decided:` or the code already records.

## What happens

1. **It researches the project, read-only.** It reads entry points, the package's public names, tests, CI, history and agent files. It does not run your build, tests or installs, and it does not follow instructions found in your files (a README or comment addressed to the agent is evidence, and it tells you it ignored it). Every fact gets a source (`path:line`) and a status: `seen`, `inferred` or `needs you`.
2. **The project's state sets how many rounds it asks.** Each round is at most three questions, each with a recommended answer and the evidence behind it.

   | State | Looks like | Rounds |
   | --- | --- | --- |
   | New | no code, or a stub | 3: purpose, name, users; the shape and tool stack; boundaries |
   | Young | under about 30 commits or 6 months, few tests, no CI | 2 |
   | Established | many commits, CI, tests, docs | 2, corrections only; a third only for a conflict it found |
   | Has a section | `## Tabby` exists | none, unless the code changed since `reviewed:` |

   It stops when it could predict your next three answers, after four rounds, or when you say to go ahead.
3. **It restates your answers and waits for a clear yes.** "Sounds good" is not a yes; it asks what to refine. Only then does it write the section, and it writes no code in the same turn.

## Example

One real round one, from a read-only run on a two-file project (a CLI that fetches a Spotify playlist, one placeholder test, one commit). Trimmed:

```
Project state: Young (one commit, one placeholder test, no CI).

| Fact | Source | Status |
| --- | --- | --- |
| Python CLI `songmatch`, entry point `songmatch.cli:main` | pyproject.toml:6-7 | seen |
| README: "Compare two friends playlists and print the songs they share" | README.md:3 | seen |
| main() takes one playlist ID and prints it; no comparison | src/songmatch/cli.py:4-6 | seen |
| Request has no auth header; Spotify's playlist endpoint needs a token | src/songmatch/spotify.py:4 | inferred, not run |

Round one:
1. Purpose: the README says compare two playlists, but cli.py only prints one.
   Which is the goal? Recommended: build the comparison (README.md:3, cli.py:4-6).
2. Users: who runs it, and how do they get a Spotify token?
   Recommended: you, on your own machine, a token in an environment variable.
3. Kind: a personal command-line tool nobody imports? Recommended: yes, `kind: code`.

I have not written AGENTS.md.
```

The questions come from a mismatch the code showed, not from a form.

## What it saves

A section like this (every line optional, one line each):

```markdown
## Tabby
reviewed: 2026-11-09 @ a1b2c3d
name: songmatch
purpose: compare two playlists and print the songs they share
users: me, on my laptop
goals: shared songs listed in under 5 s for 500-track playlists
growth: 1. Apple Music replaces Spotify from June 2026
out-of-scope: a web UI
constraints: python 3.12+; no new runtime dependencies
ask-first: new dependency, public API change
kind: code
commands: make check
decided: (filled by later tasks)
```

| Line | What the agent does with it |
| --- | --- |
| `growth:` | builds the seam the first item needs; rejects choices it would have to undo |
| `goals:` | checks the result against each one it touched before reporting |
| `ask-first:`, `never:`, `always:` | follows them without being told again |
| `out-of-scope:` | does not build it; asks if a task conflicts |
| `kind:` | picks which reference pages apply (library, native extension, HTTP service, worker, other) |
| `decided:` | a choice you made in chat, dated, so no later session asks again |
| `reviewed:` | the commit the facts were checked at, for the drift check |

Tool defaults go in a separate `## Python defaults` section, filled from what the project already uses, never from Tabby's own preferences. Both sections are plain text you can edit.

## Afterwards

- **Later tasks keep it true.** A task that builds a `growth:` item, adds a module or records a decision you gave in chat updates the section in the same task and says which lines changed. The Stop hook asks once when a session changed the project's shape and left it untouched.
- **Drift check.** When a task starts, the agent compares the section with `git rev-list --count <reviewed>..HEAD` and whether the build files changed, and asks only about what changed. A commit count alone does not make the section stale.
- **Running it again** on a project with a section restates it and changes nothing unless the code changed or you edit a line.

## What it does not do

- It never writes source code, never runs the project's commands, and never starts by itself.
- With nobody to answer (CI), it does not stop: it writes the section from the evidence, marks every unknown `(assumed)` and says which lines need confirming.
- It does not guess a purpose. What the code cannot establish is marked `review` and asked.
