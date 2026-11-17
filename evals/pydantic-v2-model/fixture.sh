#!/usr/bin/env bash
# Builds the fixture project for the `pydantic-v2-model` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

mkdir -p "$(dirname pyproject.toml)"
cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "orders"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.7"]

[tool.uv]
package = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p "$(dirname src/orders/__init__.py)"
cat > src/orders/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/orders/models.py)"
cat > src/orders/models.py <<'__FIXTURE_EOF__'
from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    model_config = ConfigDict(frozen=True)

    sku: str
    qty: int
__FIXTURE_EOF__
mkdir -p "$(dirname tests/test_models.py)"
cat > tests/test_models.py <<'__FIXTURE_EOF__'
from orders.models import Item


def test_item():
    assert Item(sku="a", qty=1).model_dump() == {"sku": "a", "qty": 1}
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
