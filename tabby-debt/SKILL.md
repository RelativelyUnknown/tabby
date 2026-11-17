---
name: tabby-debt
description: "Use only when the user asks for it: /tabby:tabby-debt (Claude Code), /tabby-debt elsewhere, 'list our shortcuts', 'show the technical debt ledger'. Lists the deliberate `# shortcut:` comments in a repository with their limits and triggers, and flags the ones that name no trigger. Never run it on your own."
disable-model-invocation: true
license: MIT
---

# Shortcut ledger

A shortcut is a deliberate simplification with a known limit, written as `# shortcut: <the limit>, <when to upgrade>` (for example `# shortcut: linear scan, move to an index past 10k rows`). This skill collects them into one list so they get revisited.

1. Run `python3 scripts/shortcuts.py <project>` from this skill's folder (the harness names the folder when it loads the skill; use its full path). It reads files only and prints a table: file and line, the limit, the trigger, and a flag. In a git repository it sees tracked files only, so `git add` a new file first; the flag checks the comment's shape, not whether the trigger is a real event ("because of the GIL" passes), so read the trigger column yourself.
2. Show the table. For each flagged row (no trigger, or no limit), propose a one-line rewrite that names both; apply it only if the user agrees.
3. For rows whose trigger may already have fired, check the current number against it (row count, request rate, supported Python version) and say which have. Do not fix them unasked.
4. `--check` makes the script exit 1 when anything is flagged, for use in CI; `--json` prints the rows as JSON.
5. If the ledger is empty or thin, look for deliberate limits that were never marked: size caps (`MAX_` constants, hard-coded limits in validation), slow fallbacks, skipped cases named in the README or AGENTS.md. List each with the line and a proposed `# shortcut:` comment; add them only if the user agrees.
