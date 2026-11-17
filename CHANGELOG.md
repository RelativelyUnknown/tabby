# Changelog

## 0.3.0

- The interview's answers steer the coding agent (new core rule 12): it names the `## Tabby` lines that shape a task, builds the seam the next `growth:` item needs and rejects choices one would have to undo, checks its work against `goals:`, and does not re-ask what `decided:`, the code or the git history records. "Keep replies short" is now rule 13.
- Project memory is written back: a task that builds a `growth:` item, adds a module or is given a decision in chat updates the section in the same task (`growth.md`, `memory-check.md`). The Stop hook asks once when a session changed the project's shape (build files, new modules, native sources) and left `AGENTS.md` untouched; this request also runs in `lite` mode.
- In Claude Code the SessionStart hook prints the `## Tabby` and `## Python defaults` sections, so sessions decide from them without a `CLAUDE.md` import.
- The interview saves `name:` (a project without one was named after the plugin) and an empty `decided:` line; an item goes in `growth:` or `out-of-scope:`, never both; the restate checks the lines against each other.
- The "run the interview skill" line is offered only when there is no `## Tabby` section.
- A requirement the user changes may update the existing test that pins the old behaviour (core rule 2); the requested behaviour is never left unbuilt to keep an old test or message intact.
- The reviewer request counts only files changed in this session, so a turn that changed nothing gets none; it and the memory request come in one message. The reviewer also checks the change against the `## Tabby` section.
- Native ports keep the Python reference in the package as the importable fallback, and a growth seam for native code takes a batch.
- The debt ledger is `/tabby:tabby-debt` in Claude Code (the docs said `/tabby:debt`, which does not exist). Deliberate limits now get a `# shortcut:` comment when they are written (core rule 7), and an empty ledger leads to a list of unmarked limits to mark.
- The frontend and diagram skills say how to tell whether Playwright is there (run `ui-check` or the renderer; Python's `import playwright` says nothing), and an unmeasured page change is not done.
- `check.py` measures text at the size it is shown in a README or docs column (at most 1040 px wide), so a long, wide diagram fails as too small to read; the quickstart says to group into zones and stack rows.
- The interview suggests project names from the user's words, never from Tabby's.

## 0.2.0

- Replies match the reader (core rule 12): result first, plus a short how-it-works for a user who says they are learning, no lessons for an experienced one. `/tabby:voice terse|explain|auto` (or `TABBY_VOICE`, `{"voice": ...}` in `.claude/tabby.json`) sets it by hand.
- Personal or financial data files go in `.gitignore` before the first commit, and nothing is staged unasked; the reviewer request lists new files with `git ls-files --others` so it never needs `git add -N`.
- Diagram and animation quickstarts for a read-only sandbox keep every file inside the project (spec on stdin).
- Always-on core rules (`core/TABBY-CORE.md`), injected at session start in Claude Code; `tools/install.py --core FILE` appends them to AGENTS.md for other tools.
- Quality-gate hooks, on by default (`hooks/hooks.json`, `scripts/gate.py`, `scripts/guard.py`): ruff on edited files, a diff check for suppressions, skipped or weakened tests and swallowed errors, and the project's check command once at the end. Off with `TABBY_GATE=off` or `.claude/tabby.json`.
- Skill descriptions no longer say "MUST be your first tool call"; `interview` is user-invoked only; the optional reminder hook is removed.
- `tabby` reads reference pages when the task touches an area, not all before the first edit; new `code/shortcut-examples.md` with before and after pairs.
- `detect.py` reports house rules (ruff families, type-checker and pytest strictness, python floor, `src/` layout) and existing helper modules.
- Five new headroom eval cases, four with hidden tests; `summarise.py` separates ceiling cases and prints a bootstrap interval and the regression list; `quality.py` counts tests weakened; `judge.py` scores testable structure; `make_arms.py` builds ablation arms.

- `tabby-reviewer` subagent (`agents/tabby-reviewer.md`): a read-only review in a fresh context, Standards and Spec reported apart. The Stop hook asks for it once when a change is large (over 80 lines or 3 Python files).
- Security audit reports can be written as JSON (`security-audit/findings.schema.json`) and checked with `tabby-review/scripts/validate_findings.py`.
- `tabby-debt` skill (user-invoked, `/tabby:debt`): `scripts/shortcuts.py` lists every `# shortcut: <limit>, <trigger>` comment as a ledger and flags the ones with no trigger; `--check` exits 1 for CI.
- Intensity modes for the hooks: `full`, `lite` (core rules and diff check only) and `off`, set with `TABBY_MODE` or `.claude/tabby.json`.
- `detect.py` notices a monorepo, lists the nested Python projects and nested AGENTS.md files; the `tabby` skill says the nearest AGENTS.md wins and a package section holds only what differs.
- `tools/install.py` writes the read-only `tabby-reviewer` agent for the claude, opencode and github targets (`--no-agent` skips it). The OpenCode and Copilot file formats follow their public docs and have not been run.

## 0.1.0

First release.
