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
- **Stop** checks the diff made during the session for shortcuts (`scripts/guard.py`): added `# type: ignore` or `# noqa`, `Any`, `cast(`, skips without a reason, bare `except`, deleted tests, fewer assertions. It then runs the project's `make check|test|ci|verify` (or `just`) once if one exists. A failure goes back to the model once; it never loops.

The hooks read the repo and run only the project's own tools. They never install anything and never edit a test.

## `/tabby:hooks off`

Create `.claude/tabby.json` with `{"gate": false}` (merge if it exists), or tell the user to set `TABBY_GATE=off` in the environment. Say that it takes effect on the next session.

## `/tabby:hooks on`

Remove the `gate` key from `.claude/tabby.json` (delete the file if it becomes empty) and unset `TABBY_GATE`.

## `/tabby:hooks` with no word

Say whether `.claude/tabby.json` or `TABBY_GATE` turns the gate off, and what `on` and `off` do. Change nothing.

## Other harnesses

OpenCode and Copilot have no plugin hooks here. Paste the text of [core/TABBY-CORE.md](../core/TABBY-CORE.md) into `AGENTS.md` (OpenCode) or `.github/copilot-instructions.md` (Copilot), and run `scripts/guard.py` from pre-commit or CI: `git diff -U0 origin/main | python3 scripts/guard.py`.
