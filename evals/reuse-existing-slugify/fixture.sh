#!/usr/bin/env bash
# Builds the fixture project for the `reuse-existing-slugify` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

mkdir -p "$(dirname pyproject.toml)"
cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "blog"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv]
package = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p "$(dirname src/blog/__init__.py)"
cat > src/blog/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/blog/core/__init__.py)"
cat > src/blog/core/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/blog/core/text.py)"
cat > src/blog/core/text.py <<'__FIXTURE_EOF__'
import re
import unicodedata


def slugify(title: str) -> str:
    """Lowercase ASCII slug: accents folded, runs of other characters become one hyphen."""
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")
__FIXTURE_EOF__
mkdir -p "$(dirname src/blog/posts.py)"
cat > src/blog/posts.py <<'__FIXTURE_EOF__'
from blog.core.text import slugify


def post_path(title: str) -> str:
    return f"/posts/{slugify(title)}"
__FIXTURE_EOF__
mkdir -p "$(dirname tests/test_posts.py)"
cat > tests/test_posts.py <<'__FIXTURE_EOF__'
from blog.posts import post_path


def test_post_path():
    assert post_path("Hello, World") == "/posts/hello-world"
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
