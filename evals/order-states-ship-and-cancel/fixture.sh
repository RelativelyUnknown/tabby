#!/usr/bin/env bash
# Builds the fixture project for the `order-states-ship-and-cancel` case in the empty workspace.
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
cat > src/shop/orders.py <<'__FIXTURE_EOF__'
"""Orders."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    id: int
    status: str = "pending"  # pending, shipped or cancelled
    shipped_at: datetime | None = None
    cancelled_reason: str | None = None
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_orders.py <<'__FIXTURE_EOF__'
from shop.orders import Order


def test_new_order_is_pending():
    assert Order(1).status == "pending"
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
