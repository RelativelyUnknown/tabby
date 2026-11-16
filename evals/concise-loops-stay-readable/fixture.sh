#!/usr/bin/env bash
# Builds the fixture project for the `concise-loops-stay-readable` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

mkdir -p "$(dirname pyproject.toml)"
cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv]
package = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p "$(dirname src/shop/__init__.py)"
cat > src/shop/__init__.py <<'__FIXTURE_EOF__'
__FIXTURE_EOF__
mkdir -p "$(dirname src/shop/orders.py)"
cat > src/shop/orders.py <<'__FIXTURE_EOF__'
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
    customer: str
    total_cents: int
    paid: bool
__FIXTURE_EOF__
mkdir -p "$(dirname tests/test_orders.py)"
cat > tests/test_orders.py <<'__FIXTURE_EOF__'
from shop.orders import Order


def test_order_is_frozen():
    order = Order(1, "ada", 500, True)
    assert order.total_cents == 500
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
