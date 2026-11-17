# hooks

The quality gate of the Tabby plugin for Claude Code: three small scripts that run on their own and check what the agent did. They are on by default. `/tabby:hooks` shows or changes whether they run. OpenCode and Copilot have no plugin hooks; see "Other tools" below.

**Entry point:** [`SKILL.md`](SKILL.md). The hooks are declared in [`hooks.json`](hooks.json) and all run [`../scripts/gate.py`](../scripts/gate.py), which uses only the standard library.

## Why

Rules in a prompt get skipped under pressure. The agent edits a test to get green or adds `# type: ignore`, and the summary says "done". The gate checks the diff itself, after the fact, and sends the problem back to the agent once.

## The three hooks

| Hook | When | What it does |
| --- | --- | --- |
| SessionStart | a session starts | Puts the core rules ([`../core/TABBY-CORE.md`](../core/TABBY-CORE.md)), what `detect.py` found about the project and your `## Tabby` and `## Python defaults` sections into the agent's context. Records a baseline of existing violations and already-changed files, so only this session's work is judged. |
| PostToolUse (Edit, Write) | after each edit of a `.py` file | Runs the project's own `ruff format` and `ruff check --fix` on that file, only when the project configures ruff. Problems go back to the agent. |
| Stop | the agent finishes a turn | Checks the diff for shortcuts, runs the project's check command once, and asks once for a review or a memory update when the change calls for it. |

The Stop hook checks only lines the session added (or, in test files, removed):

- a `# type: ignore` or `# noqa` with no reason after ` -- `
- `Any` or `cast(` in non-test code
- `pytest.mark.skip` or `xfail` with no `reason=`
- a bare `except:` or `except Exception: pass`
- in a test file: fewer assertions than before, or a deleted test

It then runs `make check`, `test`, `ci` or `verify` (or the `just` equivalent) if the project has one. Once per session it also asks for the read-only `tabby-reviewer` subagent when the change is large (over 80 changed lines or more than 3 Python files made in this session), and for an update to the `## Tabby` section when the session changed the project's shape (a build file, a new module, native sources) and left it untouched.

## Example

The agent loosens a test and silences a checker. The Stop hook, run against that diff:

```
Tabby gate: the diff added shortcuts. Fix each, then finish with your full summary of the change as the final message (what changed, what you ran and the result), not only the fix-up.
- src/calc.py: suppression added (return a + b  # type: ignore); fix the cause, or explain after ` -- `
- tests/test_calc.py: 1 assertion(s) removed from an existing test; do not weaken tests to get green
```

The hook exits with code 2, which sends the message to the agent. The agent fixes the cause and writes its summary.

## Modes

| Mode | What runs |
| --- | --- |
| `full` (default) | everything above |
| `lite` | the core rules and project memory at session start, the diff check, and the request to update `## Tabby`. No ruff on edits, no check command, no reviewer request. For a project where those would be noise. |
| `off` | nothing runs, and the core rules are not injected |

## Changing it

| To | Do |
| --- | --- |
| turn the gate off | `/tabby:hooks off` (writes `{"mode": "off"}` to `.claude/tabby.json`), or `TABBY_GATE=off` in the environment |
| turn it back on | `/tabby:hooks on` |
| use `lite` | `{"mode": "lite"}` in `.claude/tabby.json`, or `TABBY_MODE=lite`. There is no `/tabby:hooks lite`. |
| keep the gate but skip the reviewer request | `{"review": false}`, or change `review_lines` and `review_files` |
| see what is set | `/tabby:hooks` with no word; it changes nothing |

The environment wins over the file, and a change takes effect on the next session. Claude Code refuses writes to `.claude/`, so if the agent cannot create the file, create it yourself.

## Guarantees

- It never loops: a stop already continued by this hook passes.
- Any internal error exits 0, so a bug in the gate never blocks work.
- It reads the repo and runs only the project's own tools. It never installs anything and never edits a test.

## Other tools

OpenCode and Copilot do not run these hooks. Paste [`../core/TABBY-CORE.md`](../core/TABBY-CORE.md) into `AGENTS.md` (OpenCode) or `.github/copilot-instructions.md` (Copilot), or let `python3 tools/install.py <target> --core FILE` do it. The diff check works anywhere:

```
git diff -U0 origin/main | python3 scripts/guard.py    # one line per violation, exit 1 if any
```

## Limits

- It checks the diff's shape, not whether a change is right. A weakened assertion that keeps the same count passes.
- The project's check command is only found as `make` or `just` targets named `check`, `test`, `ci` or `verify`; other setups are not run.
- Tests: `python3 -m unittest tests.test_gate tests.test_guard` from the repository root.
