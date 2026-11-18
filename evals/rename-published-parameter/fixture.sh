#!/usr/bin/env bash
# Builds the fixture project for the `rename-published-parameter` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fetchlib"
version = "1.4.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
cat > CHANGELOG.md <<'__FIXTURE_EOF__'
# Changelog

## 1.4.0

- Added `retries` to `fetch()`.
__FIXTURE_EOF__
cat > README.md <<'__FIXTURE_EOF__'
# fetchlib

```python
from fetchlib import fetch

fetch("https://example.com", timeout=5)
```
__FIXTURE_EOF__
mkdir -p src/fetchlib
cat > src/fetchlib/__init__.py <<'__FIXTURE_EOF__'
from fetchlib.client import fetch

__all__ = ["fetch"]
__FIXTURE_EOF__
mkdir -p src/fetchlib
cat > src/fetchlib/client.py <<'__FIXTURE_EOF__'
def fetch(url: str, timeout: float = 10, retries: int = 3) -> dict:
    """Fetch a URL. Returns the settings used (the transport is stubbed in this fixture)."""
    return {"url": url, "timeout": timeout, "retries": retries}
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_client.py <<'__FIXTURE_EOF__'
from fetchlib import fetch


def test_fetch_uses_timeout():
    assert fetch("https://example.com", timeout=5)["timeout"] == 5
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
