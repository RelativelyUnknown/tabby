#!/usr/bin/env bash
# Builds the fixture project for the `numpydoc-docstrings` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[project]
name = "stats"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.ruff.lint]
select = ["D"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"
__FIXTURE_EOF__
cat > stats.py <<'__FIXTURE_EOF__'
# stats.py
def zscore(values: list[float]) -> list[float]:
    m = sum(values) / len(values)
    sd = (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5
    if sd == 0:
        raise ValueError('values have zero variance')
    return [(v - m) / sd for v in values]
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
