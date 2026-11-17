#!/usr/bin/env bash
# Builds the fixture project for the `type-error-no-ignore` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

mkdir -p "$(dirname pyproject.toml)"
cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "reports"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv]
package = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mypy]
strict = true
mypy_path = "src"
__FIXTURE_EOF__
mkdir -p "$(dirname src/reports/__init__.py)"
cat > src/reports/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/reports/users.py)"
cat > src/reports/users.py <<'__FIXTURE_EOF__'
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    email: str


_USERS = {1: User(1, "a@example.com")}


def find_user(user_id: int) -> User | None:
    return _USERS.get(user_id)
__FIXTURE_EOF__
mkdir -p "$(dirname src/reports/report.py)"
cat > src/reports/report.py <<'__FIXTURE_EOF__'
from reports.users import find_user


def greeting(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:
        return "Hello, guest"
    return f"Hello, {user.email}"
__FIXTURE_EOF__
mkdir -p "$(dirname tests/test_report.py)"
cat > tests/test_report.py <<'__FIXTURE_EOF__'
from reports.report import greeting


def test_known_user():
    assert greeting(1) == "Hello, a@example.com"


def test_unknown_user():
    assert greeting(99) == "Hello, guest"
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
