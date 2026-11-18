#!/usr/bin/env bash
# Builds the fixture project for the `tidy-unused-dependencies` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "app"
version = "0.3.0"
requires-python = ">=3.12"
dependencies = ["requests", "pillow", "pyyaml", "rich", "uvicorn"]

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
cat > Dockerfile <<'__FIXTURE_EOF__'
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
__FIXTURE_EOF__
mkdir -p src/app
cat > src/app/__init__.py <<'__FIXTURE_EOF__'

__FIXTURE_EOF__
mkdir -p src/app
cat > src/app/main.py <<'__FIXTURE_EOF__'
from app.net import fetch_json


async def app(scope, receive, send):
    ...
__FIXTURE_EOF__
mkdir -p src/app
cat > src/app/net.py <<'__FIXTURE_EOF__'
import requests


def fetch_json(url: str) -> dict:
    return requests.get(url, timeout=10).json()
__FIXTURE_EOF__
mkdir -p src/app
cat > src/app/thumb.py <<'__FIXTURE_EOF__'
from PIL import Image


def thumbnail(path: str) -> Image.Image:
    img = Image.open(path)
    img.thumbnail((128, 128))
    return img
__FIXTURE_EOF__
mkdir -p src/app
cat > src/app/config.py <<'__FIXTURE_EOF__'
import yaml


def load(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_smoke.py <<'__FIXTURE_EOF__'
def test_imports():
    import app.main  # noqa: F401
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
