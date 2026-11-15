# Changelog

## 0.2.0

- Always-on core rules (`core/TABBY-CORE.md`), injected at session start in Claude Code; `tools/install.py --core FILE` appends them to AGENTS.md for other tools.
- Quality-gate hooks, on by default (`hooks/hooks.json`, `scripts/gate.py`, `scripts/guard.py`): ruff on edited files, a diff check for suppressions, skipped or weakened tests and swallowed errors, and the project's check command once at the end. Off with `TABBY_GATE=off` or `.claude/tabby.json`.
- Skill descriptions no longer say "MUST be your first tool call"; `interview` is user-invoked only; the optional reminder hook is removed.
- `tabby` reads reference pages when the task touches an area, not all before the first edit; new `code/shortcut-examples.md` with before and after pairs.
- `detect.py` reports house rules (ruff families, type-checker and pytest strictness, python floor, `src/` layout) and existing helper modules.
- Five new headroom eval cases, four with hidden tests; `summarise.py` separates ceiling cases and prints a bootstrap interval and the regression list; `quality.py` counts tests weakened; `judge.py` scores testable structure; `make_arms.py` builds ablation arms.

## 0.1.0

First release.
