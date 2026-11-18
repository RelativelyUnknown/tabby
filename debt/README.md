# debt

A skill of the Tabby plugin that keeps a ledger of the shortcuts you chose on purpose. You run it yourself (`/tabby:debt` in Claude Code, `/debt` in the other tools); the agent never starts it on its own.

**Entry point:** [`SKILL.md`](SKILL.md). The work is done by [`scripts/shortcuts.py`](scripts/shortcuts.py), which uses only the standard library.

## The problem it solves

Every real project leaves things simple on purpose: a linear scan because there are 200 rows today, UTC only because every user is in Europe, a whole file read into memory because uploads are small. That is fine. The cost comes later, when nobody remembers the limit or what would make it matter, and the shortcut becomes a surprise in production.

Tabby's rule is that a deliberate limit is written down where it lives, in one comment:

```python
# shortcut: <the limit>, <when to upgrade>
rows = [r for r in rows if r["id"] == key]  # shortcut: linear scan, move to an index past 10k rows
```

The agent adds these comments as it works (core rule 7 in [`../core/TABBY-CORE.md`](../core/TABBY-CORE.md)), and the reviewer checks that each one names both parts ([`../review/changes/self-review.md`](../review/changes/self-review.md)). `debt` is the other half: it collects every marker into one table, so the list is read in one sitting instead of rediscovered by accident.

## What it does

1. Runs `scripts/shortcuts.py`, which reads the files and prints a table of every `# shortcut:` comment (also `//` and `--` comment styles): file and line, the limit, the trigger, and a flag.
2. Flags a comment that has a limit but no trigger. Without a trigger nothing will ever prompt a revisit; this is the one defect the ledger exists to catch.
3. For each flagged row, proposes a one-line rewrite that names both parts, and applies it only if you agree.
4. Checks rows whose trigger may already have fired (the row count, the request rate, the supported Python version) against the current number, and says which have. It fixes nothing unasked.
5. If the ledger is empty or thin, looks for limits that were never marked (`MAX_` constants, hard-coded limits in validation, slow fallbacks, skipped cases named in the README) and proposes a comment for each.

## Example

Three markers in a small project:

```
| File | Limit | Trigger to revisit | Flag |
| --- | --- | --- | --- |
| src/search.py:2 | linear scan | move to an index past 10k rows | - |
| src/upload.py:1 | whole file read into memory | - | no trigger |
| src/upload.py:3 | UTC only | add a per-user zone when a customer outside Europe signs up | - |

3 shortcut(s); 1 flagged.
```

The flagged row is the useful one: "whole file read into memory" says what is simple but not when it stops being acceptable. A rewrite such as `# shortcut: whole file read into memory, stream it past 50 MB uploads` fixes it.

## In CI

```
python3 debt/scripts/shortcuts.py . --check    # exit 1 when any marker is flagged
python3 debt/scripts/shortcuts.py . --json     # the rows as JSON
```

`--check` fails only for a marker with no limit or no trigger; a project with no markers passes. It does not fail because shortcuts exist.

## What it does not do

- It reads the comment's shape, not its meaning. A trigger is whatever follows the last comma (or a word such as `when`, `once`, `past`, `until`), so `# shortcut: single worker, because of the GIL` counts as having a trigger even though "because of the GIL" is a reason, not an event. The review step is for that.
- In a git repository it reads tracked files only (`git ls-files`). A new file shows up after `git add`; outside git it walks the folder and skips `.git`, `.venv`, `node_modules`, `build` and `dist`.
- It reads source and config files (`.py`, `.pyi`, `.rs`, `.c`, `.h`, `.cpp`, `.zig`, `.js`, `.ts`, `.sql`, `.toml`, `.yaml`, `.sh`, `.cfg` and a few more), not Markdown.
- It never edits a file without your yes, never runs the project's code, and never starts by itself.

## Tests

`python3 -m unittest tests.test_shortcuts` from the repository root.
