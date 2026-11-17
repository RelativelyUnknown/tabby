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

The same agent with and without Tabby on Claude Haiku 5.5 (`claude plugin eval`, regex and model-judged graders, 3 runs per case, 17 November 2026). The final 0.2.0 run covers all 112 cases; plugin-fired indicators are excluded from the scores.

| Run | Without Tabby | With Tabby | Delta | Better / worse / same (changes of 0.10 or more) |
| --- | --- | --- | --- | --- |
| 0.2.0, final (112 cases) | 0.812 | 0.902 | +0.090 | 34 / 6 / 72 |
| 0.2.0, first full run (106 cases) | 0.804 | 0.875 | +0.071 | 31 / 13 / 62 |
| 0.1.0 (`main`), 98 common cases, older graders | 0.793 | 0.834 | +0.041 (+0.001 to +0.083) | 25 / 15 / 58 |

On the 74 cases where the agent without Tabby scores under 0.95, 0.2.0's mean gain is +0.141 (95% interval +0.093 to +0.194). With Tabby a run takes 25% more turns and costs 59% more (the core rules, the gate, the reviewer subagent and the larger context). The row for 0.1.0 was scored by the graders as they were then, and 0.2.0's by the repaired ones, so the gap between those rows is an upper bound. Between the two 0.2.0 runs, the plugin changed to fix what the worst cases showed (a read-only-sandbox flow that sent diagram specs outside the project, a missing fixture, a brittle grader, and a few core rules), and six cases were added; the cases were chosen after seeing the first run, so part of the gain is regression to the mean.

Six cases are worse by 0.10 or more with Tabby. I read the traces of each. `animation-self-contained-html` (-0.52): in a read-only sandbox the builder prints a 22 KB page that the model must copy by hand, and some runs give up. `port-hot-path-to-rust`: runs with Tabby add one rounding test where runs without add parity tests against the original Python; no plugin cause found. `pick-a-set-representation`, `fake-needs-contract-test`, `add-owned-resource-endpoint` and `reuse-existing-slugify` each lost a few checks in one of three runs, which is within run-to-run noise.

The traces also showed one plugin fault: 14 of 336 runs with Tabby left throwaway files in the project (none without), because a core rule invited scratch files. The rule now says not to create them for checks that run inline, to keep any unavoidable one in a single `.scratch/` folder and delete it, and the Stop hook asks once to remove leftovers. In a re-run of five of the affected cases the runs that wrote `.scratch/` all deleted it; their scores did not move beyond noise, and the full suite was not re-run after this fix.

32 of 724 graders never pass in any run, and 68% always pass, so they cannot separate the arms. Differences under about 0.05 are noise at 3 runs per case.

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
