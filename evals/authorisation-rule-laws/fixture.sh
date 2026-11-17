#!/usr/bin/env bash
# Builds the fixture project for the `authorisation-rule-laws` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "docshare"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest", "hypothesis"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p src/docshare tests
touch src/docshare/__init__.py
cat > src/docshare/rules.py <<'__FIXTURE_EOF__'
"""Who may do what to a shared document. Pure rules: no I/O."""


def can_edit(role: str, is_owner: bool) -> bool:
    """Admins edit any document; editors edit the ones they own."""
    return role == "admin" or (role == "editor" and is_owner)
__FIXTURE_EOF__
cat > tests/test_rules.py <<'__FIXTURE_EOF__'
from docshare.rules import can_edit


def test_admin_can_edit():
    assert can_edit("admin", False)
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
