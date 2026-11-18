#!/usr/bin/env bash
# Builds the fixture project for the `flaky-cache-expiry-test` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/__init__.py <<'__FIXTURE_EOF__'

__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/cache.py <<'__FIXTURE_EOF__'
"""A small cache whose entries expire."""
import time


class TTLCache:
    def __init__(self, ttl: float):
        self.ttl = ttl
        self._items: dict[str, tuple[object, float]] = {}

    def set(self, key: str, value: object) -> None:
        self._items[key] = (value, time.monotonic() + self.ttl)

    def get(self, key: str):
        item = self._items.get(key)
        if item is None:
            return None
        value, expires = item
        if time.monotonic() >= expires:
            del self._items[key]
            return None
        return value
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_cache.py <<'__FIXTURE_EOF__'
import time

from shop.cache import TTLCache


def test_value_is_returned_before_expiry():
    cache = TTLCache(ttl=0.05)
    cache.set("a", 1)
    time.sleep(0.04)
    assert cache.get("a") == 1


def test_value_expires():
    cache = TTLCache(ttl=0.05)
    cache.set("a", 1)
    time.sleep(0.06)
    assert cache.get("a") is None
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
