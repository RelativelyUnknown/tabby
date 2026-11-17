---
name: hooks
description: "Use only when the user asks for it: /tabby:hooks, 'turn the Tabby gate on or off'. Reports or changes whether the Tabby quality gate hooks run in this project. Never change it on your own."
disable-model-invocation: true
license: MIT
---

# Tabby hooks (on by default in Claude Code)

The plugin ships three hooks in [hooks.json](hooks.json), all run by `scripts/gate.py`:

- **SessionStart** injects the core rules ([core/TABBY-CORE.md](../core/TABBY-CORE.md)) and the facts `detect.py` finds, so the rules are active on every session without a skill load.
- **PostToolUse** (Edit, Write) runs the project's own `ruff format` and `ruff check --fix` on the edited `.py` file, only when the project configures ruff. Problems go back to the model.
- **Stop** checks the diff made during the session for shortcuts (`scripts/guard.py`): added `# type: ignore` or `# noqa`, `Any`, `cast(`, skips without a reason, bare `except`, deleted tests, fewer assertions. It then runs the project's `make check|test|ci|verify` (or `just`) once if one exists. A failure goes back to the model once; it never loops. When the change is large (over 80 changed lines or more than 3 Python files), it asks once for the `tabby-reviewer` subagent ([agents/tabby-reviewer.md](../agents/tabby-reviewer.md)) to read the diff in a fresh context, on two separate axes: the repository's standards and the request.

The hooks read the repo and run only the project's own tools. They never install anything and never edit a test.

`.claude/tabby.json` also takes `{"voice": "terse"|"explain"}` (see `/tabby:voice`, which saves a `voice:` line in AGENTS.md), `{"review": false}` (no reviewer request), `review_lines` and `review_files` (thresholds).

## Modes

- **full** (default): everything above.
- **lite**: the core rules at session start and the diff check at the end only. No ruff on edits, no check command, no reviewer request. For a project where those would be noise.
- **off**: nothing runs, and the core rules are not injected.

Set `{"mode": "lite"}` in `.claude/tabby.json`, or `TABBY_MODE=lite` in the environment (the environment wins).

## `/tabby:hooks off`

Create `.claude/tabby.json` with `{"mode": "off"}` (merge if it exists; `{"gate": false}` means the same), or tell the user to set `TABBY_GATE=off` in the environment. Say that it takes effect on the next session.

## `/tabby:hooks on`

Remove the `gate` and `mode` keys from `.claude/tabby.json` (delete the file if it becomes empty) and unset `TABBY_GATE` and `TABBY_MODE`.

## `/tabby:hooks` with no word

Say whether `.claude/tabby.json` or `TABBY_GATE` turns the gate off, and what `on` and `off` do. Change nothing.

## Other harnesses

OpenCode and Copilot have no plugin hooks here. Paste the text of [core/TABBY-CORE.md](../core/TABBY-CORE.md) into `AGENTS.md` (OpenCode) or `.github/copilot-instructions.md` (Copilot), and run `scripts/guard.py` from pre-commit or CI: `git diff -U0 origin/main | python3 scripts/guard.py`.
