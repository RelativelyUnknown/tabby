# Project documents: contributing, decisions, runbooks, troubleshooting


## CONTRIBUTING.md

- How to set up a dev environment in as few commands as possible (`uv sync`), and the one command that runs all checks.
- How to run a single test; where tests and docs live.
- Branch, commit and pull-request conventions, if any; what reviewers check.
- Where to ask questions, and the code of conduct link.

Keep it short; a contributor reads it once, when they decide to contribute.

## Architecture decision record

One record per decision, numbered, kept in `docs/adr/NNNN-short-title.md`. It lets a stranger understand in a year why the code is shaped this way.

Write one when a decision would be expensive to reverse: a framework or major dependency, a data model or schema, an authentication scheme, a public API shape, a storage or wire format, going native. A choice that one commit can undo needs a commit message, not a record.

The project's convention comes first. If records exist, match their directory, file format, numbering, name pattern and headings, and continue the sequence. Use the template below only when there is none; if two conventions exist, say so instead of adding a third.

```markdown
# ADR NNNN: <decision as a short phrase>

- Status: proposed | accepted | superseded by ADR NNNN
- Date: YYYY-MM-DD
- Decided by: <people or meeting>

## Context
The forces: what we need, the constraints, what changed.

## Decision
What we do, in one or two sentences, in the active voice ("We keep jobs in a Postgres table").

## Alternatives considered
- <option>: why not (say "not evaluated" if that is the truth).

## Consequences
What gets easier, what gets harder, what we now have to maintain.
```

- An accepted record is not edited. A new decision gets a new record and the old one is marked superseded.
- State the cost of the decision as plainly as the benefit.
- Record the date and the deciders as given; do not invent reasons the deciders did not give.

## Runbook

A procedure for someone woken at night who did not write the system. Every step is an action they can do without thinking.

```markdown
# Runbook: <situation>

## When to use this
The alert or symptom, by its exact name.

## Before you start
Access, tools and where to run commands.

## Steps
1. <action>
   ```bash
   <exact command>
   ```
   Expected: <what a good result looks like>.
2. <action> ... Expected: ...

## Check it worked
The command and the result that means "fixed".

## If it did not work
The next thing to try, the time limit, and who to escalate to (name, channel) with what to tell them.
```

- One action per step, with the exact command in a code block; no "check the logs" without the command.
- Every check says what a good result looks like ("Expected: 0"), so the reader can tell success from failure.
- Give a time limit for escalation, and the person or channel.
- Last line: the owner and the date the steps were last run.

## Troubleshooting: errors by exact message

For a reader who has an error in front of them. Key every row by the exact text they see, so they can search for it.

| Symptom (exact message) | Cause | Fix |
| --- | --- | --- |
| `LedgerTimeout: no response in 30s` | The API is slow | Raise `LEDGER_TIMEOUT` (default 30) |

- One row per distinct symptom. Quote the message verbatim in code font, including numbers that vary only if they matter.
- Cause in one clause, fix as an action with the exact setting or command. A long fix links to a how-to guide instead of growing the cell.
- Order rows by how often people hit them, or alphabetically for an error-code catalogue (code, meaning, fix).
- A decision that needs several questions is an FAQ tree: question, then the answer or the next question, one level per heading.
- Say what to do when none of the rows match: where to report it and what to include.
