#!/usr/bin/env bash
# Builds the fixture project for the `dry-run-flag-stays-small` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

mkdir -p "$(dirname pyproject.toml)"
cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cleaner"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv]
package = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p "$(dirname src/cleaner/__init__.py)"
cat > src/cleaner/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/cleaner/cli.py)"
cat > src/cleaner/cli.py <<'__FIXTURE_EOF__'
import argparse
import pathlib
import sys


def delete_old(paths: list[pathlib.Path]) -> int:
    count = 0
    for path in paths:
        path.unlink()
        count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cleaner")
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    args = parser.parse_args(argv)
    count = delete_old(args.paths)
    print(f"deleted {count} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
__FIXTURE_EOF__
mkdir -p "$(dirname tests/test_cli.py)"
cat > tests/test_cli.py <<'__FIXTURE_EOF__'
from cleaner.cli import main


def test_deletes(tmp_path):
    f = tmp_path / "a.log"
    f.write_text("x")
    assert main([str(f)]) == 0
    assert not f.exists()
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
