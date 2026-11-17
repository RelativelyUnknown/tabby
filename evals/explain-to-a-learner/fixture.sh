#!/usr/bin/env bash
# Builds the fixture project for the `explain-to-a-learner` case in the empty workspace.
set -euo pipefail
cat > greet.py <<'__FIXTURE_EOF__'
import sys


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "world"
    print(f"Hello, {name}!")


if __name__ == "__main__":
    main()
__FIXTURE_EOF__
git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
