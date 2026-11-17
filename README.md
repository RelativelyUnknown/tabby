<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/cat-head-dark.png">
    <img src="assets/cat-head-light.png" width="150" alt="The Tabby logo: a painted tabby cat's head, orange in light mode and grey in dark mode.">
  </picture>
</p>

# Tabby

Tabby is a set of six agent skills for Python projects, and for the Rust, C, C++ and Zig code behind a Python API. It works in OpenCode, GitHub Copilot and Claude Code. It makes the agent find the cause before the fix, reuse before it writes, keep the diff small, and never edit a test to get green.

![6 skills](https://img.shields.io/badge/skills-6-2a8f89?style=flat-square)
![OpenCode, Copilot, Claude Code](https://img.shields.io/badge/works%20in-OpenCode%20%7C%20Copilot%20%7C%20Claude%20Code-2a8f89?style=flat-square)
![MIT licence](https://img.shields.io/badge/license-MIT-2a8f89?style=flat-square)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/cat-sleeping-dark.png">
    <img src="assets/cat-sleeping-light.png" width="560" alt="A tabby cat asleep in a curl, painted in brushstrokes: orange in light mode and grey in dark mode.">
  </picture>
</p>

## Install

Tabby is plain `SKILL.md` folders in the open [Agent Skills](https://agentskills.io/specification) format, so one copy of each folder works in all three tools. Pick your tool:

**Claude Code.** Run these as two separate prompts:

```
/plugin marketplace add RelativelyUnknown/my-skills
```

```
/plugin install tabby@tabby
```

On Claude Code 2.1.275 or later, one command does both: `/plugin install tabby --marketplace RelativelyUnknown/my-skills`.

**OpenCode and GitHub Copilot.** Clone the repository and copy the skills into your project:

```
git clone https://github.com/RelativelyUnknown/my-skills
cd your-project
python3 ../my-skills/tools/install.py agents
```

`agents` installs to `.agents/skills/`, which both tools read. Add `--user` to install for every project (`~/.agents/skills/`). Other targets: `github` (`.github/skills/`, Copilot), `opencode` (`.opencode/skills/`), `claude` (`.claude/skills/`, read by all three). The installer never deletes anything and skips folders that already exist unless you pass `--force`.

Install Tabby only from `RelativelyUnknown/my-skills` on GitHub.

| | Claude Code | OpenCode | GitHub Copilot |
| --- | --- | --- | --- |
| Skills load when the request matches | yes | yes | yes |
| Run the interview | `/tabby:interview` | `@interview` | `/interview` |
| Set the reply voice | `/tabby:voice terse\|explain\|auto` | | |
| Project memory file | `CLAUDE.md` containing `@AGENTS.md` | `AGENTS.md` | `AGENTS.md` or `.github/copilot-instructions.md` |
| Core rules and quality gate | plugin hooks, on by default (`hooks/`) | paste [`core/TABBY-CORE.md`](core/TABBY-CORE.md) into `AGENTS.md` | paste [`core/TABBY-CORE.md`](core/TABBY-CORE.md) into `.github/copilot-instructions.md` |
| Read-only reviewer subagent | `agents/tabby-reviewer.md`, asked for after a large change | `install.py opencode` writes `.opencode/agents/` (not run here) | `install.py github` writes `.github/agents/*.agent.md` (not run here) |
| Paste the core rules for you | n/a | `install.py opencode --core AGENTS.md` | `install.py github --core .github/copilot-instructions.md` |

## Example

Give the agent this bug report:

```
Bug report: `apply_discount(19.99, 15)` returns 16.9915 but the docstring says results are rounded to cents, half up. Fix it.
```

With Tabby, the agent writes a test that asserts 16.99, runs it and sees it fail, fixes the rounding, runs the whole suite, and leaves the existing tests alone. The eval case `evals/bug-fix-starts-red` checks each of those steps. To run it (needs the `claude` CLI; it costs a few cents):

```
python3 tools/eval/run.py --out results --cases bug-fix-starts-red --plugin . --plugin-dir . --model claude-haiku-5-5 --runs 3
python3 tools/eval/summarise.py results
```

## The six skills

The harness keeps the six descriptions in context (about 2,400 characters, roughly 600 tokens). When a task matches one, it loads that skill's body and only the files the body names for that task. The skills point at each other by relative path, so keep the folders side by side.

| Skill | The agent loads it when you | What it adds |
| --- | --- | --- |
| [`tabby`](tabby/) | write, fix, test, speed up, package or release Python, or the Rust, C, C++ or Zig behind it | Rules the agent never skips, and files on errors, typing, dependencies and uv, CI, performance, libraries, services, design, and native layouts, PyO3, the C API and wheels |
| [`tabby-review`](tabby-review/) | ask for a review of a diff or pull request, a repository audit or a security audit | Self-review, a security audit that separates confirmed bugs from look-alikes, and a checklist for the Python and native boundary |
| [`tabby-docs`](tabby-docs/) | write a README, docstrings, a tutorial, a changelog, an ADR or a runbook | One page type per reader need, and a check of the docs against the code |
| [`tabby-diagrams`](tabby-diagrams/) | ask for a diagram, an architecture picture or an animation | A builder that turns a small spec into an SVG or an HTML animation, and checkers for crowded labels, contrast and loop jumps |
| [`tabby-frontend`](tabby-frontend/) | build a page, dashboard, data app or docs site | A method, design tokens, a list of things it refuses to ship, and `ui-check` for contrast, focus, motion and layout |
| [`tabby-debt`](tabby-debt/) | `/tabby:debt` | A ledger of the `# shortcut: <limit>, <trigger>` comments in the repository, with the ones that name no trigger flagged |
| [`interview`](interview/) | run `/tabby:interview` | Researches the repository read-only, asks at most three questions a round, and saves a `## Tabby` section to `AGENTS.md` |

The core rules in [`core/TABBY-CORE.md`](core/TABBY-CORE.md) are always on. In Claude Code, hooks in [`hooks/`](hooks/) inject them at session start, run the project's ruff on edited files, and at the end of a turn check the diff for shortcuts (added suppressions, skipped or weakened tests, bare `except`) and run the project's check command once. Modes: `full`, `lite` (core rules and the diff check only) and `off`, set with `TABBY_MODE` or `{"mode": "lite"}` in `.claude/tabby.json`. Large changes also get one request for the read-only `tabby-reviewer` subagent. In the other tools the core lives in the instructions file (see the table above).

## The rules it holds

- Done means the real problem is solved and verified by running the code. Passing tests are evidence, not the goal.
- It never edits, deletes, skips or loosens an existing test to get green.
- It finds the cause before the fix. No special-casing inputs, no sleeps or retries to hide a symptom.
- It does not silence tools (`# type: ignore`, `# noqa`, `Any`, looser config).
- It keeps the diff small. It adds no dependency, changes no public API and makes no commit or push unless you ask.
- It uses your project's own tools, and reuses in this order: your project, the standard library, the community's standard library, then code you write yourself.

## Project memory

Tabby does the task first and never interviews you before it. Project memory lives in `AGENTS.md` for every tool. It infers the project from the repository and your request, and marks guesses `(assumed)`. `/tabby:interview` saves what the project is for and where it is going to a `## Tabby` section in `AGENTS.md`; later tasks read that section and ask before contradicting it. Tool and style defaults live in a `## Python defaults` section. Both are plain text you can edit.

## Measured effect

The same agent with and without Tabby on Claude Haiku 5.5 (`claude plugin eval`, regex and model-judged graders, 3 runs per case, 16 November 2026). The final 0.2.0 run covers all 106 cases with the repaired graders; plugin-fired indicators are excluded from the scores.

| Run | Without Tabby | With Tabby | Delta | Better / worse / same |
| --- | --- | --- | --- | --- |
| 0.2.0, final (106 cases) | 0.804 | 0.875 | +0.071 | 31 / 13 / 62 |
| 0.1.0 (`main`), 98 common cases, older graders | 0.793 | 0.834 | +0.041 (+0.001 to +0.083) | 25 / 15 / 58 |

On the 65 cases where the agent without Tabby scores under 0.95, 0.2.0's mean gain is +0.135 (95% interval +0.066 to +0.204). On the 100 cases that `main` also ran, 0.2.0 with Tabby scores 0.870 against 0.831 for 0.1.0 with Tabby, but 0.1.0's runs were scored by the graders as they were then, and 0.2.0's by the repaired ones, so read that +0.039 as an upper bound. Turns rise 26% and cost 58% per run with Tabby (the core rules, the gate and the reviewer subagent). Thirteen cases are worse by 0.10 or more; the largest are `diagram-state-machine`, `animation-self-contained-html`, `numpydoc-docstrings` (no fixture) and `optional-parquet-dependency`. 32 of 700 graders never pass in any run, and 64% always pass, so they cannot separate the arms. Differences under about 0.05 are noise at 3 runs per case.

After that run I read the traces of the seven worst cases, fixed what they showed (a read-only-sandbox flow that sent diagram specs outside the project, a missing fixture, one brittle grader, and three core rules) and re-ran only those seven. With Tabby they went from 0.00-0.85 to 0.50-1.00 and are now at or above the without-Tabby arm in each (for example `diagram-state-machine` 0.00 to 1.00, `optional-parquet-dependency` 0.58 to 1.00, `numpydoc-docstrings` 0.22 to 0.78). The without-Tabby arm stayed within 0.1 on five of the seven (`numpydoc-docstrings` has a new fixture, and `optional-parquet-dependency` fell 0.88 to 0.64). The cases were picked because they scored worst, so part of the gain is regression to the mean; the suite-wide numbers above are not re-run.

What the first 0.2.0 build got wrong, found by reading traces:

- **The skills stopped loading.** Calmer descriptions plus a core that said "read a skill page only when the task touches that area" cut skill loading from 185 of 252 runs to 13. Descriptions and core now say to load the skill at the start; it loads in 194 of 252 runs.
- **The reviewer request swallowed the summary.** After the reviewer subagent replied, the final message held only its verdict, so graders that read the trace saw no summary of the change. The request and the core now ask for a full summary.
- **Some graders never matched.** Graders that read files by glob path never found a file, so four cases scored low in every arm. They now read the trace. Run `summarise.py` and look at its grader-health line to find graders that never pass.
- **Runs without the with/without ablation score every grader.** That includes the plugin-fired indicator and the "with-only" graders, which the paired runs leave out. Re-score such runs against the paired runs' graders before comparing (see TESTING.md).

On the cases with hidden tests, runs with Tabby had fewer ruff errors (0.27 against 0.70 per run), smaller diffs (49 against 59 added lines) and no weakened tests. The score does not capture that. One model, one suite, 3 runs.

### Re-measuring

How to re-run the evals, read the summary (headroom cases, bootstrap interval, regression list) and run the ablation arms is in [TESTING.md](TESTING.md). **Check the eval environment first:** the sandbox needs pytest and the fixtures' packages installed, or every score measures that handicap.

### What each case tests

All 105 cases, grouped by what they check, with the request, the pass condition and the graders for each, are in the [case catalogue in TESTING.md](TESTING.md#case-catalogue).

## Links

- [`evals/`](evals/): the eval cases, trigger sets and seeded-audit fixtures
- [`tools/eval/`](tools/eval/): the runner, summaries, trace reader, quality, smell and judge tools
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md): ideas adapted from other projects, with sources and licences
- [Issues](https://github.com/RelativelyUnknown/my-skills/issues)

## License

MIT. Fonts, icons and adapted material are credited in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
