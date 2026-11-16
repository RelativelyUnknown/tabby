# Testing Tabby

How to check that Tabby works and how to measure what it changes. The unit tests are fast and free; the evals run real `claude` sessions and cost money (about 1.3 cents per run on Haiku 5.5).

## Unit tests

```
python3 -m unittest discover tests
python3 tools/linkcheck.py
python3 tools/descriptions.py
```

They cover the hook gate (`scripts/gate.py`), the diff check (`scripts/guard.py`), `detect.py`, the installer, the shortcut ledger and the security findings validator. They need only the standard library.

## Evals

### Check the environment before you trust a score

`claude plugin eval` runs the agent's Bash inside a bubblewrap sandbox (`bubblewrap` and `socat` must be installed). In that sandbox the network to PyPI is blocked, the home directory is read-only (so `uv run` cannot create its cache) and the Python on `PATH` is whatever is installed system-wide. If `pytest` and the packages the fixtures import (pydantic, fastapi, httpx, pandas and so on) are not installed there, the agent cannot run the tests in either arm, and every score measures that handicap, not Tabby. A first run in an unprepared container looked normal and was not. Before a full run, install the test dependencies into the system Python, run one case with `--keep-temp --runs 1`, and open the trace: look for a real `N passed` line from pytest and for the absence of `No module named pytest`, `Read-only file system` on the project's own commands, and `403 user denied` from pip. The "Read-only file system" line about a `cwd-` file in the temp folder is harness bookkeeping and harmless.

### Reading the results

`python3 tools/eval/summarise.py DIR` splits the cases. Those where the agent without Tabby already scores 0.95 or more are reported as no-regression checks. The headline delta uses the rest, with a 95% bootstrap interval and the list of cases where Tabby is worse by 0.10 or more. Five cases added in 0.2.0 target known failure modes: `type-error-no-ignore`, `reuse-existing-slugify`, `vague-request-asks-first`, `pydantic-v2-model` and `dry-run-flag-stays-small`.

### Ablation: which part gives which gain

Run `python3 tools/eval/make_arms.py arms/` and run the same cases against each arm with `run.py --plugin arms/<arm> --plugin-dir .`, then compare with `summarise.py --compare`. The arms are `full`, `no-gate` (core rules, no hooks that check), `gate-only`, `skills-only` and `core-only`. Not yet verified: that `claude plugin eval` runs a plugin's hooks. Check first with one cheap case (`--cases type-error-no-ignore --runs 1`) on `full` and on `skills-only`; if the two behave the same, the harness is not running hooks and the gate results mean nothing. Hidden tests, suppressions added, tests weakened and diff size come from `tools/eval/quality.py` (five cases added in 0.2.0 have hidden tests); blind pairwise judging of the diffs comes from `tools/eval/judge.py`, which now also scores `testable_structure`. Report the two separately: quality has parts a metric cannot see.

The cases are listed in the [README](README.md#what-each-case-tests). Case folders are in [`evals/`](evals/), the runner and summaries in [`tools/eval/`](tools/eval/).
